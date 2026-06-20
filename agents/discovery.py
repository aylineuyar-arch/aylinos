"""
AylinOS — Discovery Agent
--------------------------
Fetches and scores jobs from JSearch + ATS sources.
Logic ported from: ../claudecode/jobs.py (fetch_jsearch_jobs, fetch_ats_jobs, score_job)
Difference: saves results to SQLite via db.schema instead of returning a flat list.
"""

import os
import json
import time
import requests
import anthropic
from datetime import datetime, timezone, timedelta

from db import upsert_job

CUTOFF = datetime.now(timezone.utc) - timedelta(days=30)

PROFILE = """
Tuck MBA (Dartmouth), graduating June 2026.
Ex-Deloitte Tech Strategy Senior Consultant (4 years).
PM Strategy & Ops intern at Skild AI ($14B valuation, NVIDIA/Sequoia-backed).
BS Electrical Engineering. Strong at GTM, cross-functional ops, AI/ML startups, OKRs, enterprise programs.
NOT targeting: pure consulting, government, traditional finance, engineering roles.
Target roles: AI Strategist, AI Deployment, Solutions Strategist, Founder's Associate,
              Chief of Staff, AI Outcomes Manager, Strategy & Operations.
Target locations: NYC, London (open to SF).
Requires UK visa sponsorship or US authorization.
"""

SEARCHES = [
    ("AI strategist",                        "New York City, NY"),
    ("AI deployment strategist",             "New York City, NY"),
    ("strategy operations manager tech",     "New York City, NY"),
    ("chief of staff tech startup",          "New York City, NY"),
    ("AI outcomes manager",                  "New York City, NY"),
    ("solutions strategist AI",              "New York City, NY"),
    ("AI strategist",                        "London, UK"),
    ("chief of staff tech",                  "London, UK"),
    ("strategy operations manager tech",     "San Francisco, CA"),
    ("forward deployed AI",                  "New York City, NY"),
]

TARGET_COMPANIES = [
    # AI Labs
    "openai", "anthropic", "mistral", "cohere", "scale ai", "hugging face",
    "perplexity", "glean", "elevenlabs", "harvey", "cognition", "condukt",
    "cogna", "tenex", "12 labs", "synthesia",
    # Fintech
    "ramp", "brex", "plaid", "chime", "carta", "mercury", "deel",
    "gusto", "klarna", "affirm", "stripe",
    # SaaS
    "rippling", "notion", "figma", "airtable", "miro", "retool",
    "lattice", "intercom", "linear",
    # Data / Infra
    "databricks", "confluent", "dbt labs", "fivetran",
    # Health Tech
    "hinge health", "lyra health", "spring health", "modern health",
    # London / Europe
    "monzo", "revolut", "wise", "checkout.com", "wayve", "starling bank",
    "deliveroo", "multiverse",
    # VC
    "a16z", "sequoia", "general catalyst", "lightspeed", "index ventures",
]

EXCLUDE_TITLES = [
    "engineer", "engineering", "software", "frontend", "backend",
    "developer", "devops", "designer", "recruiter", "accountant",
    "legal", "counsel", "administrative", "coordinator",
    "account executive", "sales representative", "sales development",
    "customer success", "customer support", "support specialist",
]

EXCLUDE_SENIORITY = [
    "vice president", "vp ", " vp", "svp", "evp", "managing director",
    "head of", "chief ", "c-suite", "partner", "principal",
    "senior director", "group director", "director of", "global director",
    "staff ", "distinguished ", "fellow",
]


def _is_relevant(title: str) -> bool:
    t = title.lower()
    return not any(e in t for e in EXCLUDE_TITLES + EXCLUDE_SENIORITY)


def _classify(name: str) -> str:
    n = name.lower()
    top_ai = ["anthropic", "openai", "deepmind", "google deepmind"]
    if any(x in n for x in top_ai):
        return "top-ai-lab"
    ai_keywords = ["ai", "ml", "mistral", "cohere", "scale", "cognition",
                   "harvey", "condukt", "cogna", "tenex", "glean", "perplexity"]
    if any(x in n for x in ai_keywords):
        return "competitive-tech"
    big = ["google", "meta", "microsoft", "amazon", "apple", "salesforce", "oracle"]
    if any(x in n for x in big):
        return "big-tech"
    vc = ["ventures", "capital", "partners", "a16z", "sequoia", "lightspeed",
          "general catalyst", "index", "accel", "balderton"]
    if any(x in n for x in vc):
        return "vc-firm"
    startup_signals = ["health", "fintech", "ramp", "brex", "plaid", "rippling",
                       "notion", "figma", "airtable", "stripe", "databricks"]
    if any(x in n for x in startup_signals):
        return "high-growth-startup"
    enterprise = ["ibm", "accenture", "deloitte", "pwc", "kpmg", "ey ", "mckinsey",
                  "bcg", "bain", "jpmorgan", "goldman", "morgan stanley"]
    if any(x in n for x in enterprise):
        return "enterprise"
    return "mid-tech"


def _score_job(job: dict, client: anthropic.Anthropic) -> dict:
    prompt = f"""Rate this job for an MBA candidate. Be realistic and honest.

CANDIDATE: {PROFILE}

JOB: {job['title']} at {job['company']} ({job['company_type']}) in {job['location']}
{str(job.get('description', ''))[:400]}

SCORING GUIDELINES:
fit_score (0-100): how well role + company match candidate background and goals
conversion_score (0-100): realistic offer likelihood given applicant pool
  top-ai-lab: 10-25 (OpenAI/Anthropic = thousands of applicants)
  competitive-tech: 25-40 (selective, technical cultures)
  big-tech: 20-35 (mass applicant pools)
  high-growth-startup: 45-65 (smaller teams, MBA ops profile valued)
  mid-tech: 40-55 (known brand, accessible)
  vc-firm: 40-58 (tiny teams, MBA preferred for CoS/ops)
  enterprise: 10-30 (poor MBA-startup fit, slow hiring)
apply = true only if fit>=65 AND conversion>=45

Return ONLY JSON (no markdown):
{{"fit_score":0,"conversion_score":0,"fit_reason":"one sentence","conversion_reason":"one sentence","apply":false}}"""

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _fetch_jsearch(client: anthropic.Anthropic, seen: set) -> list[dict]:
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        print("  [discovery] RAPIDAPI_KEY not set — skipping JSearch")
        return []

    jobs = []
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}

    for query, location in SEARCHES:
        try:
            resp = requests.get(
                "https://jsearch.p.rapidapi.com/search",
                headers=headers,
                params={"query": f"{query} in {location}", "num_pages": "2", "date_posted": "month"},
                timeout=15
            )
            data = resp.json().get("data", [])
            for item in data:
                title = item.get("job_title", "")
                if not _is_relevant(title):
                    continue
                uid = item.get("job_id", f"{item.get('employer_name','')}_{title}")
                if uid in seen:
                    continue
                seen.add(uid)
                company = item.get("employer_name", "")
                job = {
                    "id": uid,
                    "title": title,
                    "company": company,
                    "company_type": _classify(company),
                    "location": item.get("job_city", location),
                    "url": item.get("job_apply_link", ""),
                    "source": "jsearch",
                    "description": item.get("job_description", "")[:500],
                    "posted_date": item.get("job_posted_at_datetime_utc", ""),
                }
                scores = _score_job(job, client)
                job.update(scores)
                jobs.append(job)
                flag = "✓" if scores["apply"] else " "
                print(f"  {flag} {title} @ {company}  fit={scores['fit_score']} conv={scores['conversion_score']}")
                time.sleep(0.3)
        except Exception as e:
            print(f"  [discovery] JSearch error for '{query}': {e}")

    return jobs


def _fetch_ats(client: anthropic.Anthropic, seen: set) -> list[dict]:
    """
    Pull from Greenhouse, Lever, Ashby for target companies.
    Pattern from: ../claudecode/jobs.py fetch_ats_jobs()
    """
    jobs = []

    greenhouse_boards = [
        "openai", "anthropic", "scale", "cohere", "ramp", "brex", "rippling",
        "notion", "figma", "airtable", "databricks", "glean", "perplexity",
        "hinge-health", "lyra-health", "spring-health", "a16z",
    ]
    lever_companies = [
        "mistral", "elevenlabs", "harvey", "cognition-labs", "linear",
        "mercury", "deel", "gusto", "intercom", "lattice",
    ]
    ashby_companies = [
        "condukt", "cogna", "wayve", "multiverse", "synthesia",
    ]

    # Greenhouse
    for board in greenhouse_boards:
        try:
            resp = requests.get(
                f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs",
                timeout=10
            )
            for item in resp.json().get("jobs", []):
                title = item.get("title", "")
                if not _is_relevant(title):
                    continue
                uid = f"gh_{item.get('id', '')}"
                if uid in seen:
                    continue
                seen.add(uid)
                company = board.replace("-", " ").title()
                job = {
                    "id": uid,
                    "title": title,
                    "company": company,
                    "company_type": _classify(company),
                    "location": item.get("location", {}).get("name", ""),
                    "url": item.get("absolute_url", ""),
                    "source": "greenhouse",
                    "description": "",
                    "posted_date": item.get("updated_at", ""),
                }
                scores = _score_job(job, client)
                job.update(scores)
                jobs.append(job)
                flag = "✓" if scores["apply"] else " "
                print(f"  {flag} {title} @ {company}  fit={scores['fit_score']} conv={scores['conversion_score']}")
                time.sleep(0.2)
        except Exception:
            pass

    # Lever
    for company in lever_companies:
        try:
            resp = requests.get(
                f"https://api.lever.co/v0/postings/{company}?mode=json",
                timeout=10
            )
            for item in resp.json():
                title = item.get("text", "")
                if not _is_relevant(title):
                    continue
                uid = f"lv_{item.get('id', '')}"
                if uid in seen:
                    continue
                seen.add(uid)
                display = company.replace("-", " ").title()
                job = {
                    "id": uid,
                    "title": title,
                    "company": display,
                    "company_type": _classify(display),
                    "location": item.get("categories", {}).get("location", ""),
                    "url": item.get("hostedUrl", ""),
                    "source": "lever",
                    "description": item.get("descriptionPlain", "")[:500],
                    "posted_date": "",
                }
                scores = _score_job(job, client)
                job.update(scores)
                jobs.append(job)
                flag = "✓" if scores["apply"] else " "
                print(f"  {flag} {title} @ {display}  fit={scores['fit_score']} conv={scores['conversion_score']}")
                time.sleep(0.2)
        except Exception:
            pass

    return jobs


def run(save_to_db: bool = True) -> list[dict]:
    """
    Main entry point. Fetches, scores, and optionally persists jobs.
    Returns list of scored job dicts.
    """
    client = anthropic.Anthropic()
    seen: set = set()

    print("\n[Discovery Agent] Fetching from JSearch (LinkedIn/Indeed/Glassdoor)...")
    jobs = _fetch_jsearch(client, seen)

    print(f"\n[Discovery Agent] Fetching from ATS (Greenhouse/Lever/Ashby)...")
    jobs += _fetch_ats(client, seen)

    print(f"\n[Discovery Agent] Found {len(jobs)} jobs total.")

    if save_to_db:
        for job in jobs:
            upsert_job(job)
        print(f"[Discovery Agent] Saved {len(jobs)} jobs to database.")

    return jobs


if __name__ == "__main__":
    run()
