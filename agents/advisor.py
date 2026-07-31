"""
AylinOS — Career Intelligence Advisor Agent
---------------------------------------------
Given a company name, returns a personalized career intelligence report
for Aylin Uyar: fit score, strategy, AI angle, role fit, outreach target.

Used by: POST /api/advisor
"""

import json
import time
from datetime import datetime
import anthropic
from db import get_conn, log_api_call

try:
    from integrations.tavily import research_company as tavily_research
    TAVILY_ENABLED = True
except Exception:
    TAVILY_ENABLED = False

# In-memory cache (survives server lifetime, resets on restart)
_cache: dict = {}

AYLIN_PROFILE = """
CANDIDATE: Aylin Uyar
- Education: Tuck MBA 2026 (Dartmouth), BS Electrical Engineering
- Work History:
    * Deloitte — Tech Strategy Senior Consultant, 4 years. Led digital transformation
      and AI strategy engagements for enterprise clients across ops, finance, and supply chain.
    * Skild AI ($14B valuation, NVIDIA/Sequoia-backed) — PM Intern. Owned GTM strategy
      for humanoid robotics AI platform. Built enterprise adoption playbook from scratch.
- Target roles: AI Strategist, AI Deployment Lead, Chief of Staff, Strategy & Operations,
  GTM Strategy — at AI-native or AI-first companies.
- NOT targeting: pure consulting, software engineering, VP+ executive roles, traditional finance.
- Target locations: NYC (primary), London (open, needs UK visa sponsorship), open to SF.
- Strengths: translating AI capabilities into enterprise adoption, operator GTM motion,
  structured problem-solving, cross-functional leadership, stakeholder management.
- Differentiator: rare combo of enterprise consulting rigor (Deloitte) + frontier AI startup
  exposure (Skild AI) + elite MBA (Tuck).
"""


def _ensure_advisor_column():
    """Add advisor_json column to company_research if it doesn't exist."""
    try:
        with get_conn() as conn:
            conn.execute("ALTER TABLE company_research ADD COLUMN advisor_json TEXT")
            conn.commit()
    except Exception:
        pass  # Column already exists


_ensure_advisor_column()


def get_cached_advisor(company: str):
    key = company.lower().strip()
    if key in _cache:
        return _cache[key]
    try:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT advisor_json FROM company_research WHERE company=? AND advisor_json IS NOT NULL ORDER BY id DESC LIMIT 1",
                (company,)
            ).fetchone()
            if row and row[0]:
                data = json.loads(row[0])
                _cache[key] = data
                return data
    except Exception:
        pass
    return None


def save_advisor_cache(company: str, data: dict):
    _cache[company.lower().strip()] = data
    try:
        with get_conn() as conn:
            updated = conn.execute(
                "UPDATE company_research SET advisor_json=? WHERE company=? AND id=(SELECT MAX(id) FROM company_research WHERE company=?)",
                (json.dumps(data), company, company)
            ).rowcount
            if not updated:
                conn.execute(
                    "INSERT INTO company_research (company, brief, investors, leadership, sponsorship, researched_at, advisor_json) VALUES (?, '', '', '', '', ?, ?)",
                    (company, datetime.utcnow().isoformat(), json.dumps(data))
                )
            conn.commit()
    except Exception as e:
        print(f"[Advisor] Cache save failed: {e}")


def run(company: str, force_refresh: bool = False) -> dict:
    """
    Generate career intelligence report for Aylin re: a given company.
    Caches to DB and memory. Returns structured JSON dict.
    """
    if not force_refresh:
        cached = get_cached_advisor(company)
        if cached:
            print(f"[Advisor] Using cached report for {company}")
            return cached

    client = anthropic.Anthropic()

    # Pull live web intelligence
    live_intel = ""
    if TAVILY_ENABLED:
        print(f"[Advisor] Fetching live web intel for {company}...")
        try:
            live_intel = tavily_research(company)
        except Exception as e:
            print(f"[Advisor] Tavily failed: {e}")

    live_section = (
        f"\n\nLIVE WEB INTELLIGENCE (prioritize this over training data):\n{live_intel}"
        if live_intel
        else "\n\n(No live web data available — use your training knowledge.)"
    )

    prompt = f"""You are a career intelligence analyst helping a top MBA candidate navigate their job search.

{AYLIN_PROFILE}
{live_section}

COMPANY TO ANALYZE: {company}

Generate a personalized career intelligence report. Be specific, direct, and actionable — not generic.
Think like a sharp executive recruiter who knows both sides deeply.

Return ONLY valid JSON (no markdown, no code fences) with EXACTLY this structure:
{{
  "company": "{company}",
  "fit_score": <integer 0-100>,
  "strategy": "<one of: apply_now | network_first | research_more | skip>",
  "strategy_reason": "<1-2 sentences: why this strategy, with specific intel about this company>",
  "ai_angle": "<what this company is actually doing with AI in production — be specific, not vague>",
  "role_fit": "<why Aylin specifically — reference her actual background, not generic MBA praise>",
  "outreach_target": "<specific title or person to reach out to, e.g. Chief of Staff, Head of Strategy & Ops>",
  "outreach_hook": "<1 sentence personalized hook that connects Aylin's experience to their specific challenge>",
  "open_roles": ["<role title 1>", "<role title 2>"],
  "verdict": "<1-2 sentence bold bottom line — is this worth Aylin's time and how should she approach it>"
}}

Fit score rubric:
- 80-100: Strong match, Aylin's exact profile, act fast
- 60-79: Good match with caveats, worth pursuing
- 40-59: Partial match, needs more research or networking first
- 0-39: Poor fit for Aylin's goals/background, skip or deprioritize

For open_roles: list 2-3 roles that likely exist or will open at this company that fit Aylin's profile.
If no info available, infer from company stage and type.

Be honest. If the company is a bad fit, say so and explain why. If London sponsorship is relevant, note it."""

    t0 = time.time()
    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}]
    )
    latency_ms = int((time.time() - t0) * 1000)

    # Log API call — cost approx for claude-opus-4-6: $15/$75 per 1M tokens
    try:
        cost = (resp.usage.input_tokens * 15 + resp.usage.output_tokens * 75) / 1_000_000
        log_api_call(
            agent="advisor",
            purpose=f"career_intelligence:{company}",
            model="claude-opus-4-6",
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
        )
    except Exception as e:
        print(f"[Advisor] log_api_call failed: {e}")

    raw = resp.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw.strip())
    data["company"] = company  # ensure company field is set

    save_advisor_cache(company, data)
    print(f"[Advisor] Generated report for {company} (fit={data.get('fit_score')})")

    return data


if __name__ == "__main__":
    import sys
    company = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Ramp"
    result = run(company)
    print(json.dumps(result, indent=2))
