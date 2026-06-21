"""
AylinOS — API Server
---------------------
FastAPI backend serving the dashboard and agent endpoints.

Endpoints:
  GET  /                      → dashboard HTML
  GET  /api/jobs              → all jobs with status
  GET  /api/metrics           → pipeline conversion metrics
  POST /api/jobs/refresh      → run discovery agent (human-in-the-loop trigger)
  POST /api/jobs/{id}/status  → update application status
  GET  /api/jobs/{id}/prep    → get interview prep (generates if missing)
  POST /api/research          → run company research agent

Human-in-the-loop: /api/jobs/refresh requires explicit POST — agent never
auto-applies or auto-submits. All status changes are user-initiated.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
from agents import discovery, interview_prep, research
from agents.advisor import run as run_advisor
from agents.router import stream_query
from api.dashboard_html import render_dashboard, render_analytics
from api.home import render_home
from api.advisor_html import render_advisor
from api.evals_html import render_evals

app = FastAPI(title="AylinOS", version="1.0.0")


@app.on_event("startup")
def seed_on_startup():
    """Seed jobs from CSV on startup if DB is empty — survives Render redeploys."""
    import csv, os
    from datetime import datetime
    conn = db.get_conn()
    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    if count > 0:
        conn.close()
        return
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "jobs_seed.csv")
    if not os.path.exists(csv_path):
        conn.close()
        return
    now = datetime.utcnow().isoformat()
    seeded = 0
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO jobs
                    (id, title, company, location, url, source, company_type,
                     fit_score, apply_flag, posted_date, fetched_at, raw_json)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (row["id"], row["title"], row["company"], row["location"],
                      row["url"], row["source"], row["company_type"],
                      float(row["fit_score"]) if row["fit_score"] else None,
                      int(row["apply_flag"] or 0), row["posted_date"], now, "{}"))
                conn.execute("""
                    INSERT OR IGNORE INTO applications (job_id, status, applied_at, notes, updated_at)
                    VALUES (?,?,?,?,?)
                """, (row["id"], row["status"] or "no_reply",
                      row["applied_at"] or None, row["notes"] or "", now))
                seeded += 1
            except Exception:
                pass
    conn.commit()
    conn.close()
    print(f"[startup] Seeded {seeded} jobs from CSV")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Home Screen ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home():
    from evals.run import get_latest_eval_results
    metrics = db.get_metrics()
    api_metrics = db.get_api_call_metrics()
    eval_metrics = get_latest_eval_results()
    return render_home(metrics, api_metrics, eval_metrics)


# ── OS Query Stream ────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str

@app.post("/api/stream")
def os_stream(body: QueryRequest):
    """
    Core OS endpoint. Takes natural language query, routes to right agent,
    streams response as SSE. Powers the home screen search bar.
    """
    return StreamingResponse(
        stream_query(body.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


# ── Job Search ─────────────────────────────────────────────────────────────────

@app.get("/job-search", response_class=HTMLResponse)
def dashboard():
    jobs = db.get_all_jobs()
    metrics = db.get_metrics()
    return render_dashboard(jobs, metrics)


@app.get("/analytics", response_class=HTMLResponse)
def analytics():
    metrics = db.get_metrics()
    funnel = db.get_stage_dropoff()
    by_type = db.get_funnel_by_company_type()
    weekly = db.get_weekly_volume()
    return render_analytics(metrics, funnel, by_type, weekly)


@app.get("/api/analytics")
def api_analytics():
    return {
        "metrics": db.get_metrics(),
        "funnel": db.get_stage_dropoff(),
        "by_company_type": db.get_funnel_by_company_type(),
        "weekly_volume": db.get_weekly_volume(),
    }


# ── Jobs ───────────────────────────────────────────────────────────────────────

@app.get("/api/jobs")
def get_jobs(status: str = None):
    return db.get_all_jobs(status_filter=status)


@app.get("/api/metrics")
def get_metrics():
    return db.get_metrics()


class RefreshRequest(BaseModel):
    confirmed: bool = False


class JobSeedPayload(BaseModel):
    id: str
    title: str = ""
    company: str = ""
    location: str = ""
    url: str = ""
    source: str = "seed"
    company_type: str = ""
    fit_score: float = None
    apply_flag: int = 0
    posted_date: str = ""
    status: str = "no_reply"
    applied_at: str = ""
    notes: str = ""

@app.post("/api/jobs/seed")
def seed_job(body: JobSeedPayload):
    """Seed a single job row from local DB into Render DB."""
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    conn = db.get_conn()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO jobs
            (id, title, company, location, url, source, company_type,
             fit_score, apply_flag, posted_date, fetched_at, raw_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (body.id, body.title, body.company, body.location, body.url,
              body.source, body.company_type, body.fit_score, body.apply_flag,
              body.posted_date, now, "{}"))
        # Insert application status row
        conn.execute("""
            INSERT OR IGNORE INTO applications (job_id, status, applied_at, notes, updated_at)
            VALUES (?,?,?,?,?)
        """, (body.id, body.status, body.applied_at or None, body.notes, now))
        conn.commit()
        return {"status": "ok", "id": body.id}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        conn.close()


@app.post("/api/jobs/refresh")
def refresh_jobs(body: RefreshRequest):
    """
    Human-in-the-loop: user must explicitly confirm before running discovery.
    This prevents the agent from running autonomously on a schedule.
    """
    if not body.confirmed:
        return {
            "status": "pending",
            "message": "Send confirmed=true to trigger discovery agent. This will fetch and score new jobs (~3-5 min)."
        }
    jobs = discovery.run(save_to_db=True)
    return {"status": "complete", "jobs_found": len(jobs)}


class StatusUpdate(BaseModel):
    status: str  # discovered | applied | rejected | interviewing | offer | withdrawn
    notes: str = ""


VALID_STATUSES = {"discovered", "applied", "rejected", "interviewing", "offer", "withdrawn"}


@app.post("/api/jobs/{job_id}/status")
def update_status(job_id: str, body: StatusUpdate):
    if body.status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Must be one of: {VALID_STATUSES}")
    db.update_status(job_id, body.status, body.notes)
    return {"status": "updated", "job_id": job_id, "new_status": body.status}


# ── Interview Prep ─────────────────────────────────────────────────────────────

@app.get("/api/jobs/{job_id}/prep")
def get_prep(job_id: str, refresh: bool = False):
    try:
        return interview_prep.run(job_id, force_refresh=refresh)
    except ValueError as e:
        raise HTTPException(404, str(e))


# ── Audio Practice ─────────────────────────────────────────────────────────────

@app.get("/api/jobs/{job_id}/audio")
def get_audio(job_id: str):
    """
    Stream the ElevenLabs-generated STAR story audio for a job.
    Generates on-demand if not cached. Returns 404 if ElevenLabs not configured.
    """
    import os
    audio_path = f"/tmp/aylinos_prep_{job_id}.mp3"
    if not os.path.exists(audio_path):
        # Try generating it now
        try:
            prep = interview_prep.run(job_id)
            audio_path = prep.get("audio_path", "")
        except Exception as e:
            raise HTTPException(500, str(e))
    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(404, "Audio not available — set ELEVENLABS_API_KEY to enable")
    return FileResponse(audio_path, media_type="audio/mpeg", filename=f"prep_{job_id}.mp3")


# ── Company Research ───────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    company: str
    force_refresh: bool = False


@app.post("/api/research")
def run_research(body: ResearchRequest):
    result = research.run(body.company, force_refresh=body.force_refresh)
    return result


# ── Career Intelligence Advisor ────────────────────────────────────────────────

@app.get("/advisor", response_class=HTMLResponse)
def advisor_page():
    return render_advisor()


@app.post("/api/advisor")
def advisor(body: ResearchRequest):
    result = run_advisor(body.company, force_refresh=body.force_refresh)
    return result


# ── App Pages ──────────────────────────────────────────────────────────────

@app.get("/cs-triage", response_class=HTMLResponse)
def cs_triage():
    return render_app_page(
        title="CS Triage",
        icon="🎫",
        color="#10b981",
        desc="Inbound support tickets categorized and routed in under 1 second using Claude Haiku.",
        tech=["Claude Haiku", "Streamlit", "FastAPI"],
        details=[
            ("Model", "Claude Haiku 3.5"),
            ("Categories", "Billing · Technical · Account · General"),
            ("Latency", "&lt;1s per classification"),
            ("Interface", "Streamlit web app"),
        ],
        repo_note="Run via: <code>streamlit run ai-cs-triage/app.py</code>",
        back_url="/"
    )


@app.get("/networking", response_class=HTMLResponse)
def networking():
    from api.networking_html import render_networking
    os_contacts = db.get_companies_with_contacts()
    # Pull live from Airtable if keys are set
    airtable_contacts = []
    try:
        import os as _os
        from pyairtable import Api
        at_key = _os.environ.get("AIRTABLE_API_KEY", "")
        at_base = _os.environ.get("AIRTABLE_BASE_ID", "")
        if at_key and at_base:
            api = Api(at_key)
            table = api.table(at_base, "JPM Contacts")
            for rec in table.all():
                f = rec["fields"]
                airtable_contacts.append({
                    "company":       f.get("Division / Team", "JPMorgan"),
                    "contact_name":  f.get("Name", ""),
                    "contact_title": f.get("Title", ""),
                    "contact_angle": f.get("Notes", "") or f.get("Intel — Role", ""),
                    "fit_score":     None,
                    "strategy":      f.get("Warm Path", ""),
                    "status":        f.get("Outreach Status", "queued").lower().replace(" ", "-"),
                    "source":        "Airtable",
                })
    except Exception as e:
        print(f"[Airtable] fetch failed: {e}")
    return render_networking(os_contacts, airtable_contacts)


@app.get("/outreach", response_class=HTMLResponse)
def outreach():
    return render_app_page(
        title="Finance Outreach",
        icon="📧",
        color="#8b5cf6",
        desc="Targeted outreach to finance sector AI roles. JPMorgan-focused. Fit scoring + Claude-drafted emails.",
        tech=["Claude", "Airtable", "Playwright"],
        details=[
            ("Primary Target", "JPMorgan Chase"),
            ("CRM", "Airtable"),
            ("Fit Ranking", "AI-scored by role match"),
            ("Drafts", "Personalized per contact"),
        ],
        repo_note="Run via: <code>python3 finance-ai-role-outreach/outreach.py</code>",
        back_url="/"
    )


@app.get("/research", response_class=HTMLResponse)
def research_page():
    return render_app_page(
        title="Company Research",
        icon="🔬",
        color="#ec4899",
        desc="Live company intelligence via Tavily web search + Claude Opus synthesis. Structured briefs saved to Google Drive.",
        tech=["Tavily", "Claude Opus", "Google Drive"],
        details=[
            ("Data Source", "Tavily live web search"),
            ("Synthesis", "Claude Opus 4.6"),
            ("Storage", "SQLite + Google Drive"),
            ("Output", "JSON brief: investors, leadership, AI angle, hiring culture"),
        ],
        repo_note='POST <code>/api/research</code> with <code>{"company": "Anthropic"}</code>',
        back_url="/"
    )


def render_app_page(title, icon, color, desc, tech, details, repo_note, back_url):
    tech_tags = "".join(
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:3px 9px;border-radius:4px;background:rgba(255,255,255,0.05);color:rgba(232,232,237,0.4);border:1px solid rgba(255,255,255,0.07)">{t}</span>'
        for t in tech
    )
    detail_rows = "".join(
        f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05)">'
        f'<td style="padding:12px 0;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(232,232,237,0.3);text-transform:uppercase;letter-spacing:0.06em;width:140px">{k}</td>'
        f'<td style="padding:12px 0;font-size:13px;color:rgba(232,232,237,0.7)">{v}</td></tr>'
        for k, v in details
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title} — AylinOS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  font-family:'Inter',system-ui,sans-serif;
  background:#0c0c10;
  min-height:100vh;
  color:#e8e8ed;
  padding:40px;
  -webkit-font-smoothing:antialiased;
}}
.back{{
  font-family:'JetBrains Mono',monospace;
  font-size:11px;color:rgba(232,232,237,0.32);
  text-decoration:none;display:inline-flex;
  align-items:center;gap:6px;margin-bottom:40px;
  transition:color 150ms;
}}
.back:hover{{color:rgba(232,232,237,0.7)}}
.card{{
  background:#111116;border:1px solid rgba(255,255,255,0.07);
  border-radius:12px;padding:36px;max-width:600px;
  border-left:2px solid {color};
}}
.card-icon{{font-size:22px;margin-bottom:20px;color:{color}}}
h1{{font-size:24px;font-weight:600;letter-spacing:-0.02em;margin-bottom:10px}}
.desc{{font-size:14px;color:rgba(232,232,237,0.55);line-height:1.65;margin-bottom:24px;max-width:52ch}}
.tags{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:28px}}
table{{width:100%;border-collapse:collapse;border-top:1px solid rgba(255,255,255,0.07)}}
.note{{
  margin-top:24px;
  padding:12px 16px;
  background:rgba(255,255,255,0.03);
  border-radius:8px;
  font-family:'JetBrains Mono',monospace;
  font-size:11px;
  color:rgba(232,232,237,0.32);
  border:1px solid rgba(255,255,255,0.06);
}}
code{{background:rgba(255,255,255,0.07);padding:1px 5px;border-radius:3px;font-family:'JetBrains Mono',monospace}}
</style>
</head>
<body>
<a href="{back_url}" class="back">← AylinOS</a>
<div class="card">
  <div class="card-icon">{icon}</div>
  <h1>{title}</h1>
  <p class="desc">{desc}</p>
  <div class="tags">{tech_tags}</div>
  <table>{detail_rows}</table>
  <div class="note">{repo_note}</div>
</div>
</body>
</html>"""


# ── Evals ──────────────────────────────────────────────────────────────────────

@app.get("/evals", response_class=HTMLResponse)
def evals_dashboard():
    from evals.run import get_latest_eval_results
    eval_data = get_latest_eval_results()
    api_metrics = db.get_api_call_metrics()
    return render_evals(eval_data, api_metrics)


@app.post("/api/evals/run")
def run_evals(background_tasks=None):
    """Trigger eval run. Takes ~2 min (25 Haiku calls x2 prompts)."""
    import threading
    from evals.run import run as run_eval_harness
    thread = threading.Thread(target=run_eval_harness, daemon=True)
    thread.start()
    return {"status": "running", "message": "Eval run started. Refresh /evals in ~2 minutes."}


@app.get("/api/evals/results")
def get_eval_results():
    from evals.run import get_latest_eval_results
    result = get_latest_eval_results()
    if not result:
        return {"status": "no_data", "message": "No eval results yet. POST /api/evals/run to generate."}
    return result


@app.get("/api/observability")
def get_observability():
    return db.get_api_call_metrics()


# ── Make.com Webhook ────────────────────────────────────────────────────────────

class WebhookRequest(BaseModel):
    source: str = "make"
    confirmed: bool = False


@app.post("/api/webhook/make")
def make_webhook(body: WebhookRequest):
    """
    Make.com automation endpoint.
    Trigger: POST {"source": "make", "confirmed": true}
    Returns a structured digest for downstream Make.com scenarios
    (Slack notification, Airtable update, Google Sheets log).

    Human-in-the-loop: confirmed=true required even from automation.
    This is deliberate — no fully autonomous job applications.
    """
    if not body.confirmed:
        return {
            "status": "pending",
            "message": "Send confirmed=true to trigger discovery. Webhook source recorded.",
            "source": body.source,
        }

    jobs = discovery.run(save_to_db=True)
    metrics = db.get_metrics()
    apply_recs = [j for j in jobs if j.get("apply")]

    return {
        "status": "complete",
        "source": body.source,
        "jobs_found": len(jobs),
        "apply_recommended": len(apply_recs),
        "top_5": [
            {
                "title": j["title"],
                "company": j["company"],
                "fit_score": j.get("fit_score"),
                "conversion_score": j.get("conversion_score"),
                "url": j.get("url", ""),
            }
            for j in sorted(apply_recs, key=lambda x: x.get("fit_score", 0), reverse=True)[:5]
        ],
        "pipeline_metrics": {
            "total_jobs": metrics["total_jobs"],
            "response_rate": metrics["response_rate"],
            "interview_rate": metrics["interview_rate"],
        },
        "dashboard_url": "https://aylinos.onrender.com/job-search",
    }


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    metrics = db.get_metrics()
    return {"status": "ok", "jobs_in_db": metrics["total_jobs"]}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api.server:app", host="0.0.0.0", port=port, reload=True)
