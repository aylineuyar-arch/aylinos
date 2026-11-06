"""
AylinOS — Discovery Agent
--------------------------
Fetches and scores jobs from JSearch + ATS sources.
Logic ported from: ../claudecode/jobs.py (fetch_jsearch_jobs, fetch_ats_jobs, score_job)
Difference: saves results to SQLite via db.schema instead of returning a flat list.
"""

import os
import re
import json
import time
import requests
import anthropic
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from pathlib import Path

from db import upsert_job

_ACTIVITY_LOG = Path(__file__).resolve().parent.parent / "data" / "claude_activity.log"


_ERROR_LOG = Path(__file__).resolve().parent.parent / "data" / "discovery_errors.log"


def _ping(msg: str):
    """Write a timestamped activity line to claude_activity.log and print it."""
    ts = datetime.now().strftime("%H:%M")
    line = f"[{ts}] discovery: {msg}"
    print(line)
    try:
        _ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_ACTIVITY_LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _error(msg: str):
    """Write errors to discovery_errors.log and also surface in the console activity log."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] ERROR: {msg}"
    print(line)
    try:
        _ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_ERROR_LOG, "a") as f:
            f.write(line + "\n")
        with open(_ACTIVITY_LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

CUTOFF = datetime.now(timezone.utc) - timedelta(days=10)

PROFILE = """
Tuck MBA (Dartmouth), graduating June 2026.
Ex-Deloitte Tech Strategy Senior Consultant (4 years).
PM Strategy & Ops intern at Skild AI ($14B valuation, NVIDIA/Sequoia-backed).
BS Electrical Engineering. Strong at GTM, cross-functional ops, AI/ML startups, OKRs, enterprise programs.
NOT targeting: pure consulting, government, traditional finance, engineering roles.
Target roles (HIGH FIT — score 80+): Engagement Manager, AI Deployment Strategist, AI Deployment,
              Engagement Manager AI, Forward Deployed Engineer, Implementation Manager,
              Solutions Consultant AI, Customer Deployment, AI Outcomes Manager.
Target roles (GOOD FIT — score 70-79): Solutions Strategist, Founder's Associate,
              Chief of Staff, Strategy & Operations, Business Value Consultant.
Target locations: NYC, London (open to SF).
Requires UK visa sponsorship or US authorization.
"""

SEARCHES = [
    # Core cluster — highest signal, deduplicated
    ("AI deployment strategist",         "New York City, NY"),
    ("AI deployment strategist",         "London, UK"),
    ("engagement manager AI",            "New York City, NY"),
    ("engagement manager AI",            "London, UK"),
    ("forward deployed engineer",        "New York City, NY"),
    ("forward deployed engineer",        "London, UK"),
    ("AI solutions consultant",          "New York City, NY"),
    ("AI solutions consultant",          "London, UK"),
    ("AI implementation manager",        "New York City, NY"),
    ("AI implementation manager",        "London, UK"),
    ("chief of staff AI startup",        "New York City, NY"),
    ("chief of staff AI startup",        "London, UK"),
    ("founder associate AI",             "New York City, NY"),
    ("founder associate AI",             "London, UK"),
    ("AI strategist",                    "New York City, NY"),
    ("AI strategist",                    "London, UK"),
    ("deployment strategist",            "New York City, NY"),
    ("deployment strategist",            "London, UK"),
]

TARGET_COMPANIES = [
    # AI Labs
    "openai", "anthropic", "mistral", "cohere", "scale ai", "hugging face",
    "perplexity", "glean", "elevenlabs", "harvey", "cognition", "condukt",
    "cogna", "tenex", "12 labs", "synthesia", "decagon", "sierra",
    "normal computing", "hebbia", "cartesia", "serval", "nooks",
    "distyl ai", "happyrobot", "solve intelligence", "reflection ai",
    "actively ai", "profound",
    # CRM / Customer Platform (Planhat competitors = same buyer)
    "planhat", "gainsight", "totango", "churnzero", "vitally", "catalyst",
    "pylon", "assembled",
    # Fintech
    "ramp", "brex", "plaid", "chime", "carta", "mercury", "deel",
    "gusto", "klarna", "affirm", "stripe", "lendable", "revolut",
    # SaaS
    "rippling", "notion", "figma", "airtable", "miro", "retool",
    "lattice", "intercom", "linear", "attio", "clay",
    "omnea", "zip", "handshake", "glimpse",
    # Data / Infra
    "databricks", "confluent", "dbt labs", "fivetran", "nscale", "celonis",
    # Health Tech
    "hinge health", "lyra health", "spring health", "modern health",
    # London / Europe
    "monzo", "revolut", "wise", "checkout.com", "wayve", "starling bank",
    "deliveroo", "multiverse", "cleo", "wolt", "bolt",
    # Enterprise
    "capco",
    # VC
    "a16z", "sequoia", "general catalyst", "lightspeed", "index ventures",
]

EXCLUDE_TITLES = [
    # Engineering
    "software engineer", "frontend engineer", "backend engineer",
    "developer", "devops", "designer",
    # Sales — hard excluded
    "account executive",
    "sales representative", "sales development representative",
    "sales manager", "enterprise sales", "inside sales",
    "business development representative", "bdr", " sdr",
    # Support / admin
    "customer support", "support specialist", "recruiter",
    "accountant", "legal", "counsel", "administrative", "coordinator",
]

# Excluded only when NOT paired with an AI/deployment/strategy signal
EXCLUDE_WITHOUT_AI = [
    "customer success",
    "engineer",
    "engineering",
    "account manager",  # ok if paired with AI signal (e.g. "Technical Account Manager, AI")
]

AI_SIGNALS = [
    "ai", "ml", "deployment", "strategist", "strategy", "operator",
    "implementation", "transformation", "enablement", "adoption",
    "intelligence", "agentic", "generative",
]

# Title must contain at least one of these to pass — purely exclusion-based filter
# was letting 140 Anthropic roles through. This cuts to roles with actual fit signal.
REQUIRE_SIGNALS = [
    "deployment", "strategist", "strategy", "engagement manager",
    "forward deployed", "solutions consultant", "solutions engineer",
    "implementation", "chief of staff", "founder", "associate",
    "ai ", " ai", "operator", "gtm", "enablement", "transformation",
    "adoption", "outcomes", "business value", "technical account",
    "program manager", "operations manager", "ops manager",
]

PER_BOARD_CAP = 10  # soft cap per board — REQUIRE_SIGNALS is the real gate

EXCLUDE_SENIORITY = [
    "vice president", "vp ", " vp", "svp", "evp", "managing director",
    "head of", "chief ", "c-suite", "partner", "principal",
    "senior director", "group director", "director of", "global director",
    "distinguished ", "fellow",
]


TARGET_LOCATIONS = [
    "new york", "nyc", ", ny", "manhattan", "new york city",
    "london", "united kingdom", ", uk", "uk -",
    "san francisco", ", ca", "bay area",
]


def _is_recent(date_str: str) -> bool:
    """Return True if date_str is within CUTOFF window, or if unparseable (keep by default)."""
    if not date_str:
        return True  # no date = assume it might be new
    try:
        # ISO 8601 — strip microseconds/Z for compat
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00").split(".")[0] + "+00:00")
        return dt >= CUTOFF
    except Exception:
        return True  # unparseable = keep


def _is_location_ok(location: str) -> bool:
    if not location:
        return True  # no location = keep (JSearch already filtered by location param)
    loc = location.lower()
    return any(t in loc for t in TARGET_LOCATIONS)


def _is_relevant(title: str) -> bool:
    t = title.lower()
    if any(e in t for e in EXCLUDE_SENIORITY):
        return False
    if any(e in t for e in EXCLUDE_TITLES):
        return False
    for soft in EXCLUDE_WITHOUT_AI:
        if soft in t and not any(s in t for s in AI_SIGNALS):
            return False
    # Must have at least one positive fit signal — prevents large boards
    # (e.g. Anthropic 140 roles) from flooding the scorer
    if not any(s in t for s in REQUIRE_SIGNALS):
        return False
    return True


def _classify(name: str) -> str:
    n = name.lower()
    top_ai = ["anthropic", "openai", "deepmind", "google deepmind", "reflection ai"]
    if any(x in n for x in top_ai):
        return "top-ai-lab"
    ai_keywords = [
        "ai", "ml", "mistral", "cohere", "scale", "cognition",
        "harvey", "condukt", "cogna", "tenex", "glean", "perplexity",
        # new AI companies
        "profound", "glimpse", "distyl", "happyrobot", "solve intelligence",
        "actively ai", "decagon", "sierra", "hebbia", "cartesia", "serval",
        "elevenlabs", "synthesia", "nooks",
    ]
    if any(x in n for x in ai_keywords):
        return "competitive-tech"
    big = ["google", "meta", "microsoft", "amazon", "apple", "salesforce", "oracle"]
    if any(x in n for x in big):
        return "big-tech"
    vc = ["ventures", "capital", "partners", "a16z", "sequoia", "lightspeed",
          "general catalyst", "index", "accel", "balderton"]
    if any(x in n for x in vc):
        return "vc-firm"
    startup_signals = [
        "health", "fintech", "ramp", "brex", "plaid", "rippling",
        "notion", "figma", "airtable", "stripe", "databricks",
        # new high-growth
        "omnea", "pylon", "celonis", "handshake", "zip", "assembled",
        "intercom", "attio", "clay", "linear", "retool", "mercury",
        "capco",
        # watchlist companies
        "planhat", "multiverse", "junior",
    ]
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
  80-100: title is in HIGH FIT list AND company is a target AI/SaaS company
  65-79: strong fit but minor gap (wrong geo, adjacent title, or tier 2 company)
  40-64: partial fit — relevant company but wrong role shape, or vice versa
  <40: poor fit — exclude
apply = true only if fit >= 65

Return ONLY JSON (no markdown):
{{"fit_score":0,"fit_reason":"one sentence","apply":false}}"""

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


def _score_jobs_parallel(jobs: list[dict], client: anthropic.Anthropic, workers: int = 6) -> list[dict]:
    """Score a batch of jobs in parallel using a thread pool."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    scored = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_score_job, job, client): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                scores = future.result()
                # Normalize fit_score to int — Claude occasionally returns a string
                try:
                    scores["fit_score"] = float(scores["fit_score"])
                except (KeyError, TypeError, ValueError):
                    scores["fit_score"] = 0.0
                job.update(scores)
                flag = "✓" if scores.get("apply") else " "
                print(f"  {flag} {job['title']} @ {job['company']}  fit={scores['fit_score']}")
            except Exception as e:
                job.setdefault("fit_score", 0)
                print(f"  [score] error for {job.get('title','?')}: {e}")
            scored.append(job)
    return scored


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
                params={"query": f"{query} in {location}", "num_pages": "1", "date_posted": "week"},
                timeout=15
            )
            data = resp.json().get("data", [])
            for item in data:
                title = item.get("job_title", "")
                loc   = item.get("job_city", location)
                if not _is_relevant(title) or not _is_location_ok(loc):
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
                jobs.append(job)
        except Exception as e:
            _error(f"jsearch '{query}': {e}")

    _ping(f"jsearch: scoring {len(jobs)} roles in parallel...")
    return _score_jobs_parallel(jobs, client)


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
        # new additions
        "handshake", "zip", "celonis", "assembled", "pylon",
        "actively-ai", "happyrobot",
    ]
    lever_companies = [
        "mistral", "elevenlabs", "harvey", "cognition-labs", "linear",
        "mercury", "deel", "gusto", "intercom", "lattice",
        # new additions
        "omnea", "reflect", "solve-intelligence",
    ]
    ashby_companies = [
        "condukt", "cogna", "wayve", "multiverse", "synthesia",
        "decagon", "hebbia", "cartesia", "serval", "attio",
        # new additions
        "profound", "glimpse", "distyl-ai", "clay", "nooks",
    ]

    # Custom careers pages (non-standard ATS)
    custom_careers = [
        {
            "company": "Planhat",
            "url": "https://www.planhat.com/careers",
            "pattern": r'/careers/([a-f0-9-]{36})',
            "base_url": "https://www.planhat.com",
        },
    ]

    # Greenhouse
    _ping(f"greenhouse: scanning {len(greenhouse_boards)} boards...")
    gh_found = 0
    for board in greenhouse_boards:
        try:
            resp = requests.get(
                f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs",
                timeout=10
            )
            board_roles = 0
            for item in resp.json().get("jobs", []):
                if board_roles >= PER_BOARD_CAP:
                    break
                title = item.get("title", "")
                loc   = item.get("location", {}).get("name", "")
                if not _is_relevant(title) or not _is_location_ok(loc):
                    continue
                if not _is_recent(item.get("updated_at", "")):
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
                jobs.append(job)
                board_roles += 1
                gh_found += 1
            if board_roles > 0:
                _ping(f"greenhouse/{board}: {board_roles} roles")
        except Exception as e:
            _error(f"greenhouse/{board}: {e}")
    _ping(f"greenhouse done — {gh_found} roles across {len(greenhouse_boards)} boards")

    # Lever
    _ping(f"lever: scanning {len(lever_companies)} companies...")
    lv_found = 0
    for company in lever_companies:
        try:
            resp = requests.get(
                f"https://api.lever.co/v0/postings/{company}?mode=json",
                timeout=10
            )
            if resp.status_code != 200:
                _error(f"lever/{company}: HTTP {resp.status_code}")
                continue
            payload = resp.json()
            if not isinstance(payload, list):
                _error(f"lever/{company}: unexpected payload type {type(payload).__name__}")
                continue
            co_roles = 0
            for item in payload:
                if co_roles >= PER_BOARD_CAP:
                    break
                title = item.get("text", "")
                loc   = item.get("categories", {}).get("location", "")
                if not _is_relevant(title) or not _is_location_ok(loc):
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
                jobs.append(job)
                co_roles += 1
                lv_found += 1
            if co_roles > 0:
                _ping(f"lever/{company}: {co_roles} roles")
        except Exception as e:
            _error(f"lever/{company}: {e}")
    _ping(f"lever done — {lv_found} roles across {len(lever_companies)} companies")

    # Custom careers pages (Planhat etc — not on standard ATS APIs)
    for co in custom_careers:
        try:
            resp = requests.get(co["url"], timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=re.compile(co["pattern"]))
            seen_urls = set()
            for link in links:
                href = link.get("href", "")
                full_url = href if href.startswith("http") else co["base_url"] + href
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                title = link.get_text(strip=True)
                if not title or not _is_relevant(title):
                    continue
                uid = f"custom_{co['company'].lower()}_{re.search(co['pattern'], href).group(1)}"
                if uid in seen:
                    continue
                seen.add(uid)
                job = {
                    "id": uid,
                    "title": title,
                    "company": co["company"],
                    "company_type": _classify(co["company"]),
                    "location": "",
                    "url": full_url,
                    "source": "custom",
                    "description": "",
                    "posted_date": "",
                }
                jobs.append(job)
        except Exception as e:
            print(f"  [discovery] Custom careers error for {co['company']}: {e}")

    # Ashby
    _ping(f"ashby: scanning {len(ashby_companies)} companies...")
    ab_found = 0
    for company in ashby_companies:
        try:
            resp = requests.post(
                f"https://api.ashbyhq.com/posting-api/job-board/{company}",
                json={},
                timeout=10
            )
            if resp.status_code != 200:
                _error(f"ashby/{company}: HTTP {resp.status_code}")
                continue
            ct = resp.headers.get("content-type", "")
            if "json" not in ct:
                _error(f"ashby/{company}: non-JSON response ({ct})")
                continue
            try:
                data = resp.json()
            except Exception as parse_err:
                _error(f"ashby/{company}: JSON parse error: {parse_err}")
                continue
            co_roles = 0
            for item in data.get("jobs", []):
                if co_roles >= PER_BOARD_CAP:
                    break
                title = item.get("title", "")
                loc   = item.get("location", "")
                if not _is_relevant(title) or not _is_location_ok(loc):
                    continue
                if not _is_recent(item.get("publishedAt", "")):
                    continue
                uid = f"ab_{item.get('id', '')}"
                if uid in seen:
                    continue
                seen.add(uid)
                display = company.replace("-", " ").title()
                job = {
                    "id": uid,
                    "title": title,
                    "company": display,
                    "company_type": _classify(display),
                    "location": loc,
                    "url": item.get("jobUrl", ""),
                    "source": "ashby",
                    "description": item.get("descriptionPlain", "")[:500],
                    "posted_date": item.get("publishedAt", ""),
                }
                jobs.append(job)
                co_roles += 1
                ab_found += 1
            if co_roles > 0:
                _ping(f"ashby/{company}: {co_roles} roles")
        except Exception as e:
            _error(f"ashby/{company}: {e}")
    _ping(f"ashby done — {ab_found} roles across {len(ashby_companies)} companies")

    _ping(f"ats: scoring {len(jobs)} roles in parallel...")
    return _score_jobs_parallel(jobs, client)


def run(save_to_db: bool = True) -> list[dict]:
    """
    Main entry point. Fetches, scores, and optionally persists jobs.
    Returns list of scored job dicts.
    """
    client = anthropic.Anthropic()
    seen: set = set()

    _ping("started")
    _ping("step 1/3 — JSearch (LinkedIn / Indeed / Glassdoor)...")
    jobs = _fetch_jsearch(client, seen)
    _ping(f"step 1/3 done — {len(jobs)} roles from JSearch")

    _ping("step 2/3 — ATS scrape (Greenhouse / Lever / Ashby)...")
    jobs += _fetch_ats(client, seen)
    _ping(f"step 2/3 done — {len(jobs)} roles total after ATS")

    # Keep top 20 by fit score — no point saving roles you can't act on today
    jobs = sorted(jobs, key=lambda j: float(j.get("fit_score") or 0), reverse=True)[:20]
    _ping(f"step 3/3 — top {len(jobs)} roles by fit score")

    if save_to_db:
        for job in jobs:
            upsert_job(job)
        _ping(f"step 3/3 done — {len(jobs)} roles saved to SQLite")

    _ping(f"complete — {len(jobs)} roles in DB")
    return jobs


# ── ATS slug map for single-company demo mode ─────────────────────────────────
COMPANY_ATS_MAP = {
    # Greenhouse
    "ramp":        ("greenhouse", "ramp"),
    "glean":       ("greenhouse", "glean"),
    "databricks":  ("greenhouse", "databricks"),
    "notion":      ("greenhouse", "notion"),
    "anthropic":   ("greenhouse", "anthropic"),
    "openai":      ("greenhouse", "openai"),
    "gainsight":   ("greenhouse", "gainsight"),
    "perplexity":  ("greenhouse", "perplexity"),
    "scale":       ("greenhouse", "scale"),
    "brex":        ("greenhouse", "brex"),
    # Ashby
    "clay":        ("ashby", "clay"),
    "hebbia":      ("ashby", "hebbia"),
    "decagon":     ("ashby", "decagon"),
    "attio":       ("ashby", "attio"),
    "cartesia":    ("ashby", "cartesia"),
    # Lever
    "elevenlabs":  ("lever", "elevenlabs"),
    "harvey":      ("lever", "harvey"),
    "linear":      ("lever", "linear"),
    "mercury":     ("lever", "mercury"),
    # Custom
    "planhat":     ("custom", "planhat"),
}


def run_single(company: str, save_to_db: bool = True) -> list[dict]:
    """
    Demo fast path — scrape and score ONE company only.
    Completes in <90s when APIs cooperate.
    Falls back gracefully if the company isn't in the ATS map or the board returns nothing.
    """
    client = anthropic.Anthropic()
    seen: set = set()
    company_key = company.lower().strip()

    if company_key not in COMPANY_ATS_MAP:
        _ping(f"single: {company} not in ATS map — trying JSearch only")
        # Fallback: run a targeted JSearch query for this company
        jobs = []
        api_key = os.environ.get("RAPIDAPI_KEY")
        if api_key:
            headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
            for loc in ["New York City, NY", "London, UK"]:
                try:
                    resp = requests.get(
                        "https://jsearch.p.rapidapi.com/search",
                        headers=headers,
                        params={"query": f"jobs at {company} in {loc}", "num_pages": "1", "date_posted": "week"},
                        timeout=15,
                    )
                    for item in resp.json().get("data", []):
                        title = item.get("job_title", "")
                        if not _is_relevant(title):
                            continue
                        uid = item.get("job_id", f"{company}_{title}")
                        if uid in seen:
                            continue
                        seen.add(uid)
                        jobs.append({
                            "id": uid, "title": title, "company": company.title(),
                            "company_type": _classify(company), "location": item.get("job_city", loc),
                            "url": item.get("job_apply_link", ""), "source": "jsearch",
                            "description": item.get("job_description", "")[:500],
                            "posted_date": item.get("job_posted_at_datetime_utc", ""),
                        })
                except Exception as e:
                    _error(f"single jsearch {company}/{loc}: {e}")
        if not jobs:
            _ping(f"single: no roles found for {company} — honest empty")
            return []
        jobs = _score_jobs_parallel(jobs, client)
        if save_to_db:
            for job in jobs:
                upsert_job(job)
        _ping(f"single: {len(jobs)} roles for {company} saved")
        return jobs

    ats, slug = COMPANY_ATS_MAP[company_key]
    _ping(f"single: Scanning {company} — {ats.upper()} board ({slug})")
    jobs = []

    try:
        if ats == "greenhouse":
            resp = requests.get(
                f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", timeout=10
            )
            for item in resp.json().get("jobs", []):
                if len(jobs) >= PER_BOARD_CAP:
                    break
                title = item.get("title", "")
                loc = item.get("location", {}).get("name", "")
                if not _is_relevant(title) or not _is_location_ok(loc):
                    continue
                uid = f"gh_{item.get('id', '')}"
                if uid in seen:
                    continue
                seen.add(uid)
                jobs.append({
                    "id": uid, "title": title, "company": company.title(),
                    "company_type": _classify(company), "location": loc,
                    "url": item.get("absolute_url", ""), "source": "greenhouse",
                    "description": "", "posted_date": item.get("updated_at", ""),
                })

        elif ats == "ashby":
            resp = requests.post(
                f"https://api.ashbyhq.com/posting-api/job-board/{slug}", json={}, timeout=10
            )
            if resp.status_code != 200:
                _error(f"ashby/{slug}: HTTP {resp.status_code}")
                jobs = []
                resp_jobs = []
            else:
                ct = resp.headers.get("content-type", "")
                try:
                    resp_jobs = resp.json().get("jobs", []) if "json" in ct else []
                except Exception as parse_err:
                    _error(f"ashby/{slug}: JSON parse error: {parse_err}")
                    resp_jobs = []
            for item in resp_jobs:
                if len(jobs) >= PER_BOARD_CAP:
                    break
                title = item.get("title", "")
                loc = item.get("location", "")
                if not _is_relevant(title) or not _is_location_ok(loc):
                    continue
                uid = f"ab_{item.get('id', '')}"
                if uid in seen:
                    continue
                seen.add(uid)
                jobs.append({
                    "id": uid, "title": title, "company": company.title(),
                    "company_type": _classify(company), "location": loc,
                    "url": item.get("jobUrl", ""), "source": "ashby",
                    "description": item.get("descriptionPlain", "")[:500],
                    "posted_date": item.get("publishedAt", ""),
                })

        elif ats == "lever":
            resp = requests.get(
                f"https://api.lever.co/v0/postings/{slug}?mode=json", timeout=10
            )
            if resp.status_code != 200:
                _error(f"lever/{slug}: HTTP {resp.status_code}")
                resp_items = []
            else:
                payload = resp.json()
                resp_items = payload if isinstance(payload, list) else []
                if not isinstance(payload, list):
                    _error(f"lever/{slug}: unexpected payload type {type(payload).__name__}")
            for item in resp_items:
                if not isinstance(item, dict):
                    continue
                if len(jobs) >= PER_BOARD_CAP:
                    break
                title = item.get("text", "")
                loc = item.get("categories", {}).get("location", "")
                if not _is_relevant(title) or not _is_location_ok(loc):
                    continue
                uid = f"lv_{item.get('id', '')}"
                if uid in seen:
                    continue
                seen.add(uid)
                jobs.append({
                    "id": uid, "title": title, "company": company.title(),
                    "company_type": _classify(company), "location": loc,
                    "url": item.get("hostedUrl", ""), "source": "lever",
                    "description": item.get("descriptionPlain", "")[:500],
                    "posted_date": "",
                })

        elif ats == "custom" and slug == "planhat":
            resp = requests.get(
                "https://www.planhat.com/careers", timeout=15, headers={"User-Agent": "Mozilla/5.0"}
            )
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            pattern = r'/careers/([a-f0-9-]{36})'
            for link in soup.find_all("a", href=re.compile(pattern)):
                if len(jobs) >= PER_BOARD_CAP:
                    break
                href = link.get("href", "")
                title = link.get_text(strip=True)
                if not title or not _is_relevant(title):
                    continue
                uid = f"custom_planhat_{re.search(pattern, href).group(1)}"
                if uid in seen:
                    continue
                seen.add(uid)
                full_url = href if href.startswith("http") else "https://www.planhat.com" + href
                jobs.append({
                    "id": uid, "title": title, "company": "Planhat",
                    "company_type": _classify("planhat"), "location": "",
                    "url": full_url, "source": "custom", "description": "", "posted_date": "",
                })

    except Exception as e:
        _error(f"single/{company}: {e}")

    if not jobs:
        _ping(f"single: No open roles found at {company} matching your geo filters")
        return []

    _ping(f"single: Scoring {len(jobs)} roles against your profile...")
    jobs = _score_jobs_parallel(jobs, client)

    if save_to_db:
        for job in jobs:
            upsert_job(job)
        _ping(f"single: {len(jobs)} roles scored and saved to pipeline")

    return jobs


if __name__ == "__main__":
    run()
