"""
AylinOS — Outcome & Feedback Updater
--------------------------------------
Updates application statuses and adds interview feedback notes.
Run after import_applications.py.

  cd aylinos && python3 scripts/update_outcomes.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.schema import get_conn, init_db
from datetime import datetime

# ---------------------------------------------------------------------------
# Format: (company, role_fragment, new_status, round_eliminated, notes)
#
# role_fragment: partial match — used to find the right row when a company
#                has multiple applications
#
# status options:
#   rejected_interview  — eliminated during interview process
#   rejected_early      — eliminated via email / no recruiter engagement
#   withdrawn           — self-removed
#   no_reply            — no response
# ---------------------------------------------------------------------------

OUTCOMES = [
    (
        "BT Group",
        "Portfolio Strategic",
        "rejected_interview",
        "Round 3 — case study",
        "Bypassed recruiter and team screen via networking. Lost on case: financial uplift was missing. Timing also flagged as too early.",
    ),
    (
        "Flamapp.ai",
        "Chief of Staff",
        "rejected_early",
        "Post-application",
        "Needed immediate hire. Timing mismatch, not a fit or skill issue.",
    ),
    (
        "Handshake",
        "Strategic Project Lead",
        "rejected_interview",
        "Round 1 — recruiter screen",
        "Story was not set yet. Stumbled in the interview. Own assessment: narrative wasn't ready at that point.",
    ),
    (
        "Poseidon",
        "Strategic Initiatives",
        "rejected_interview",
        "Round 2 — team (ghosted, then informed 3 weeks later)",
        "Went with candidate more closely aligned to their needs. Ghosted after round 2 — recruiter only followed up 3 weeks later.",
    ),
    (
        "Hebbia",
        "Solution Engineer",
        "rejected_interview",
        "Round 1 — hiring manager",
        "Came in via referral. Eliminated by hiring manager. Likely factors: sales-heavy role mismatch, visa friction.",
    ),
    (
        "TransformWorks",
        "Chief of Staff",
        "rejected_interview",
        "Round 1 — recruiter",
        "Recruiter screen passed but team did not select profile to move forward.",
    ),
    (
        "HockeyStack",
        "Strategy and Operations",
        "rejected_interview",
        "Round 1 — recruiter",
        "Recruiter screen passed but team did not select profile to move forward.",
    ),
    (
        "Vertice",
        "GTM Strategy",
        "rejected_interview",
        "Round 1 — recruiter",
        "Team did not select profile. Described as a very close decision.",
    ),
    (
        "Vendelux",
        "Strategic Business",
        "rejected_interview",
        "Round 1 — recruiter",
        "Team did not select profile. Described as a very close decision.",
    ),
    (
        "Forter",
        "Strategy Ops Associate",
        "rejected_interview",
        "Round 1 — recruiter",
        "Team did not select profile. Described as a very close decision.",
    ),
    (
        "Relay",
        "Strategy & Ops Manager",
        "rejected_interview",
        "Round 2 — hiring manager",
        "Very rude and combative interview process. Eliminated after HM round.",
    ),
    (
        "JPMorgan",
        "Digital Strategy",
        "rejected_interview",
        "Round 3 — case",
        "Very disorganized process. Scheduling worked against candidate, had to follow up too many times. Eliminated after case round 3.",
    ),
    (
        "August",
        "Strategy & Operation",
        "rejected_interview",
        "Round 2 — case (ghosted)",
        "Ghosted after case round 2. Had to follow up herself to schedule own interviews. New grads running the hiring process.",
    ),
    (
        "Hebbia",
        "AI Strategist",
        "rejected_interview",
        "Round 2 — team member",
        "Eliminated after round 2 team member interview.",
    ),
    (
        "Cartesia",
        "GTM Strategist",
        "withdrawn",
        "Self-removed",
        "Self-removed after assessment. Not a good fit.",
    ),
    (
        "Bending Spoons",
        "Office of the CEO",
        "rejected_interview",
        "Round 1 — automated logic test",
        "Eliminated on automated skill/logic test in round 1.",
    ),
    (
        "Scale AI",
        "Strategic Project Lead, Gen AI",
        "rejected_interview",
        "Round 2 — live SQL case",
        "Eliminated on live SQL case round 2.",
    ),
    (
        "Tenex",
        "AI Strategist",
        "rejected_interview",
        "Round 2 — team member",
        "Close call, tough decision. Eliminated after round 2 team member interview.",
    ),
]


def run():
    init_db()
    now = datetime.utcnow().isoformat()
    updated = 0

    with get_conn() as conn:
        for company, role_fragment, status, round_info, notes in OUTCOMES:
            # Find matching job(s)
            rows = conn.execute("""
                SELECT id, title FROM jobs
                WHERE company = ? AND title LIKE ?
            """, (company, f"%{role_fragment}%")).fetchall()

            if not rows:
                # Fallback: match on company only if role fragment fails
                rows = conn.execute(
                    "SELECT id, title FROM jobs WHERE company = ?", (company,)
                ).fetchall()

            if not rows:
                print(f"  [!] Not found: {company} / {role_fragment}")
                continue

            for row in rows:
                job_id = row["id"]

                # Update application status
                conn.execute("""
                    INSERT INTO applications (job_id, status, notes, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (job_id, status, f"{round_info} — {notes}", now))

                # Add outcome event with full feedback
                conn.execute("""
                    INSERT INTO outcomes (job_id, event_type, event_date, notes)
                    VALUES (?, ?, ?, ?)
                """, (job_id, status, now, f"{round_info} | {notes}"))

                print(f"  ✓ {company} ({row['title'][:40]}) → {status}")
                updated += 1

    print(f"\n[Update] {updated} records updated.")


if __name__ == "__main__":
    run()
