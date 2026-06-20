"""
AylinOS — Persistence Layer
SQLite schema. No external setup required — file created automatically.

Referenced from: ../claudecode (job scoring patterns)
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "aylinos.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id              TEXT PRIMARY KEY,
                title           TEXT NOT NULL,
                company         TEXT NOT NULL,
                location        TEXT,
                url             TEXT,
                source          TEXT,
                company_type    TEXT,
                fit_score       INTEGER,
                conversion_score INTEGER,
                reasons         TEXT,
                apply_flag      INTEGER DEFAULT 0,
                posted_date     TEXT,
                fetched_at      TEXT NOT NULL,
                raw_json        TEXT
            );

            CREATE TABLE IF NOT EXISTS applications (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id      TEXT NOT NULL REFERENCES jobs(id),
                status      TEXT NOT NULL DEFAULT 'discovered',
                applied_at  TEXT,
                notes       TEXT,
                updated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS outcomes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id      TEXT NOT NULL REFERENCES jobs(id),
                event_type  TEXT NOT NULL,
                event_date  TEXT NOT NULL,
                notes       TEXT
            );

            CREATE TABLE IF NOT EXISTS interview_prep (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id           TEXT NOT NULL REFERENCES jobs(id),
                company_brief    TEXT,
                star_stories     TEXT,
                likely_questions TEXT,
                generated_at     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS company_research (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                company      TEXT NOT NULL,
                brief        TEXT,
                investors    TEXT,
                leadership   TEXT,
                sponsorship  TEXT,
                researched_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS api_calls (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                agent        TEXT NOT NULL,
                purpose      TEXT NOT NULL,
                model        TEXT NOT NULL,
                input_tokens  INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cost_usd     REAL DEFAULT 0,
                latency_ms   INTEGER DEFAULT 0,
                called_at    TEXT NOT NULL
            );
        """)


def upsert_job(job: dict) -> str:
    job_id = (job.get("id") or
              f"{job['company']}_{job['title']}".replace(" ", "_").lower()[:80])
    now = datetime.utcnow().isoformat()

    with get_conn() as conn:
        exists = conn.execute("SELECT id FROM jobs WHERE id=?", (job_id,)).fetchone()
        if exists:
            conn.execute("""
                UPDATE jobs SET fit_score=?, conversion_score=?, reasons=?, apply_flag=?, fetched_at=?
                WHERE id=?
            """, (job.get("fit_score"), job.get("conversion_score"),
                  job.get("reasons"), 1 if job.get("apply") else 0, now, job_id))
        else:
            conn.execute("""
                INSERT INTO jobs (id,title,company,location,url,source,company_type,
                                  fit_score,conversion_score,reasons,apply_flag,
                                  posted_date,fetched_at,raw_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (job_id, job.get("title"), job.get("company"), job.get("location"),
                  job.get("url"), job.get("source"), job.get("company_type"),
                  job.get("fit_score"), job.get("conversion_score"),
                  job.get("reasons"), 1 if job.get("apply") else 0,
                  job.get("posted_date"), now, json.dumps(job)))
            conn.execute(
                "INSERT INTO applications (job_id,status,updated_at) VALUES (?,?,?)",
                (job_id, "discovered", now)
            )
    return job_id


def update_status(job_id: str, status: str, notes: str = "") -> None:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO applications (job_id,status,applied_at,notes,updated_at)
            VALUES (?,?,?,?,?)
        """, (job_id, status, now if status == "applied" else None, notes, now))
        conn.execute("""
            INSERT INTO outcomes (job_id,event_type,event_date,notes)
            VALUES (?,?,?,?)
        """, (job_id, status, now, notes))


def get_all_jobs(status_filter: str = None) -> list:
    with get_conn() as conn:
        query = """
            SELECT j.*, a.status, a.applied_at, a.notes
            FROM jobs j
            LEFT JOIN (
                SELECT job_id, status, applied_at, notes
                FROM applications
                WHERE id IN (SELECT MAX(id) FROM applications GROUP BY job_id)
            ) a ON j.id = a.job_id
        """
        if status_filter:
            query += f" WHERE a.status = ?"
            rows = conn.execute(query, (status_filter,)).fetchall()
        else:
            rows = conn.execute(query + " ORDER BY j.fit_score DESC").fetchall()
        return [dict(r) for r in rows]


def get_metrics() -> dict:
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        apply_rec = conn.execute("SELECT COUNT(*) FROM jobs WHERE apply_flag=1").fetchone()[0]
        status_counts = {}
        for row in conn.execute("""
            SELECT a.status, COUNT(*) as n FROM applications a
            WHERE a.id IN (SELECT MAX(id) FROM applications GROUP BY job_id)
            GROUP BY a.status
        """).fetchall():
            status_counts[row["status"]] = row["n"]

        applied = total  # all imported = applied
        interviewing = status_counts.get("interviewing", 0)
        rejected_interview = status_counts.get("rejected_interview", 0)
        rejected_early = status_counts.get("rejected_early", 0)
        no_reply = status_counts.get("no_reply", 0)
        offers = status_counts.get("offer", 0)
        withdrawn = status_counts.get("withdrawn", 0)

        # Funnel: everyone who got past no_reply
        engaged = applied - no_reply
        interview_rate = round(rejected_interview / applied * 100, 1) if applied else 0
        ghosted = status_counts.get("no_reply", 0)

        return {
            "total_jobs": total,
            "apply_recommended": apply_rec,
            "applied": applied,
            "no_reply": no_reply,
            "engaged": engaged,
            "interviewing": interviewing,
            "rejected_interview": rejected_interview,
            "rejected_early": rejected_early,
            "offers": offers,
            "withdrawn": withdrawn,
            "interview_rate": interview_rate,
            "offer_rate": round(offers / applied * 100, 1) if applied else 0,
            "response_rate": round(engaged / applied * 100, 1) if applied else 0,
            "by_status": status_counts,
        }


def get_funnel_by_company_type() -> list:
    """Break down interview rates by company type."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                j.company_type,
                COUNT(*) as total,
                SUM(CASE WHEN a.status IN ('interviewing','rejected_interview','offer') THEN 1 ELSE 0 END) as got_interview,
                SUM(CASE WHEN a.status = 'offer' THEN 1 ELSE 0 END) as offers
            FROM jobs j
            LEFT JOIN (
                SELECT job_id, status FROM applications
                WHERE id IN (SELECT MAX(id) FROM applications GROUP BY job_id)
            ) a ON j.id = a.job_id
            GROUP BY j.company_type
            ORDER BY total DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_weekly_volume() -> list:
    """Applications submitted per week."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                strftime('%Y-W%W', posted_date) as week,
                COUNT(*) as applications
            FROM jobs
            WHERE posted_date IS NOT NULL AND posted_date != ''
            GROUP BY week
            ORDER BY week ASC
        """).fetchall()
        return [dict(r) for r in rows]


def get_stage_dropoff() -> dict:
    """Where are applications being lost."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT a.status, COUNT(*) as n FROM applications a
            WHERE a.id IN (SELECT MAX(id) FROM applications GROUP BY job_id)
            GROUP BY a.status
        """).fetchall()
        counts = {r["status"]: r["n"] for r in rows}

        total = sum(counts.values())
        engaged = total - counts.get("no_reply", 0)
        interviewed = counts.get("rejected_interview", 0) + counts.get("interviewing", 0) + counts.get("offer", 0)
        offers = counts.get("offer", 0)

        return {
            "applied": total,
            "got_response": engaged,
            "got_interview": interviewed,
            "got_offer": offers,
            "drop_application_to_response": round((total - engaged) / total * 100, 1) if total else 0,
            "drop_response_to_interview": round((engaged - interviewed) / engaged * 100, 1) if engaged else 0,
            "drop_interview_to_offer": round((interviewed - offers) / interviewed * 100, 1) if interviewed else 0,
        }


def save_interview_prep(job_id: str, brief: str, stars: str, questions: str) -> None:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO interview_prep (job_id,company_brief,star_stories,likely_questions,generated_at)
            VALUES (?,?,?,?,?)
        """, (job_id, brief, stars, questions, now))


def get_interview_prep(job_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM interview_prep WHERE job_id=? ORDER BY id DESC LIMIT 1",
            (job_id,)
        ).fetchone()
        return dict(row) if row else None


def log_api_call(agent: str, purpose: str, model: str,
                 input_tokens: int, output_tokens: int,
                 cost_usd: float, latency_ms: int) -> None:
    """Log every Claude/Tavily API call for cost and observability tracking."""
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO api_calls (agent,purpose,model,input_tokens,output_tokens,cost_usd,latency_ms,called_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (agent, purpose, model, input_tokens, output_tokens, cost_usd, latency_ms, now))


def get_api_call_metrics() -> dict:
    """Aggregate cost and call stats for observability dashboard."""
    with get_conn() as conn:
        today = datetime.utcnow().date().isoformat()
        total = conn.execute("SELECT COUNT(*), SUM(cost_usd), SUM(latency_ms) FROM api_calls").fetchone()
        today_row = conn.execute(
            "SELECT COUNT(*), SUM(cost_usd) FROM api_calls WHERE called_at >= ?",
            (today,)
        ).fetchone()
        by_agent = conn.execute("""
            SELECT agent, COUNT(*) as calls, SUM(cost_usd) as cost, AVG(latency_ms) as avg_latency
            FROM api_calls GROUP BY agent ORDER BY cost DESC
        """).fetchall()
        by_model = conn.execute("""
            SELECT model, COUNT(*) as calls, SUM(cost_usd) as cost,
                   SUM(input_tokens) as input_tokens, SUM(output_tokens) as output_tokens
            FROM api_calls GROUP BY model ORDER BY calls DESC
        """).fetchall()
        return {
            "total_calls": total[0] or 0,
            "total_cost_usd": round(total[1] or 0, 4),
            "avg_latency_ms": round((total[2] or 0) / max(total[0] or 1, 1)),
            "calls_today": today_row[0] or 0,
            "cost_today_usd": round(today_row[1] or 0, 4),
            "by_agent": [dict(r) for r in by_agent],
            "by_model": [dict(r) for r in by_model],
        }


def save_company_research(company: str, brief: str, investors: str,
                          leadership: str, sponsorship: str) -> None:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO company_research (company,brief,investors,leadership,sponsorship,researched_at)
            VALUES (?,?,?,?,?,?)
        """, (company, brief, investors, leadership, sponsorship, now))


init_db()
