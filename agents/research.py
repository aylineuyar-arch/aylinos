"""
AylinOS — Company Research Agent
----------------------------------
Generates structured research brief for any company.
Saves to DB for use by interview prep and scoring agents.

Architecture pattern from: ../claudecode/restaurant-agent/nodes.py (enrich node)
"""

from typing import Optional
import anthropic
from db import save_company_research, get_conn

try:
    from integrations.drive import save_company_research as _drive_save_research
    DRIVE_ENABLED = True
except Exception:
    DRIVE_ENABLED = False

try:
    from integrations.tavily import research_company as tavily_research
    TAVILY_ENABLED = True
except Exception:
    TAVILY_ENABLED = False


def get_cached_research(company: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM company_research WHERE company=? ORDER BY id DESC LIMIT 1",
            (company,)
        ).fetchone()
        return dict(row) if row else None


def run(company: str, force_refresh: bool = False) -> dict:
    """
    Research a company. Returns structured brief.
    Caches to DB — won't re-run unless force_refresh=True.
    """
    if not force_refresh:
        cached = get_cached_research(company)
        if cached:
            print(f"[Research] Using cached research for {company}")
            return cached

    client = anthropic.Anthropic()

    # Pull live web intelligence first
    live_intel = ""
    if TAVILY_ENABLED:
        print(f"[Research] Fetching live web intel for {company}...")
        live_intel = tavily_research(company)

    live_section = f"\n\nLIVE WEB INTELLIGENCE (use this to override stale training data):\n{live_intel}" if live_intel else ""

    prompt = f"""You are a strategic research analyst. Generate a structured research brief for:

COMPANY: {company}{live_section}

Return ONLY valid JSON (no markdown) with this structure:
{{
  "brief": "2-3 sentence description: what they do, business model, stage",
  "investors": "key investors and funding rounds if known",
  "leadership": "CEO name and relevant leadership if known",
  "sponsorship": "US visa sponsorship status if known, otherwise 'Unknown — verify on job posting'",
  "ai_angle": "how AI is central to their product or operations",
  "hiring_culture": "what they look for in operators and strategists based on public info",
  "recent_news": "most recent notable news or milestone if known"
}}

Be factual. Write 'Unknown' for fields you are not confident about."""

    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    import json
    data = json.loads(raw.strip())

    save_company_research(
        company=company,
        brief=data.get("brief", ""),
        investors=data.get("investors", ""),
        leadership=data.get("leadership", ""),
        sponsorship=data.get("sponsorship", ""),
    )
    print(f"[Research] Saved research for {company}")

    if DRIVE_ENABLED:
        _drive_save_research(company=company, research=data)

    return data


if __name__ == "__main__":
    import sys
    company = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Mistral AI"
    result = run(company)
    import json
    print(json.dumps(result, indent=2))
