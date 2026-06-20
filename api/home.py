"""
AylinOS — iPad Home Screen
----------------------------
Custom icons = mini workflow architecture diagrams (node graph visual language
from portfolio). Node colors: LLM=indigo, Memory=teal, Search=blue,
Action=orange, Gate=pink. This makes every icon immediately say "AI system"
not "website app."

Key OS vs website principles applied:
- No centered page title on the desktop (title only in status bar)
- Icons sit directly on the wallpaper
- Status bar shows LIVE system health, not just app name
- Persistent chrome never changes — content loads in sheets
"""

from datetime import datetime


# Node color conventions (same as portfolio color key)
LLM    = "#818cf8"   # Reasoning / Claude
MEM    = "#34d399"   # Memory / DB / Storage
SEARCH = "#60a5fa"   # Search / APIs / External
ACTION = "#fb923c"   # Action / Output / Booking
GATE   = "#f472b6"   # Verification / Gate / Human-in-loop
NOTIFY = "#facc15"   # Notify / Email

# Each icon is an SVG mini workflow graph — nodes connected by edges
# viewBox="0 0 80 56" drawn centered in 96px icon
APPS = [
    {
        "id": "job-search",
        "name": "Job Search",
        "gradient": "linear-gradient(145deg,#1e1b4b,#312e81)",
        "accent": LLM,
        "url": "/job-search",
        "new_tab": False,
        # Mini graph: API Sources → Claude Haiku (score) → SQLite → Claude Opus (prep) → Drive
        "icon_svg": f"""
<svg viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" width="64" height="45">
  <!-- edges -->
  <line x1="16" y1="18" x2="32" y2="18" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="48" y1="18" x2="62" y2="18" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="40" y1="26" x2="40" y2="38" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="62" y1="26" x2="62" y2="38" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <!-- nodes -->
  <circle cx="8"  cy="18" r="7" fill="{SEARCH}" opacity=".9"/>
  <circle cx="40" cy="18" r="7" fill="{LLM}" class="llm-pulse"/>
  <circle cx="68" cy="18" r="7" fill="{MEM}" opacity=".9"/>
  <circle cx="40" cy="46" r="7" fill="{ACTION}" opacity=".9"/>
  <circle cx="68" cy="46" r="7" fill="{GATE}" opacity=".9"/>
  <!-- labels -->
  <text x="8"  y="35" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">APIs</text>
  <text x="40" y="10" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Claude</text>
  <text x="68" y="10" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">SQLite</text>
  <text x="40" y="56" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Prep</text>
  <text x="68" y="56" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Drive</text>
</svg>""",
        "tagline": "358 applications. Discovered, scored, and interview-prepped by Claude.",
        "what": "Pulls jobs from JSearch + Greenhouse APIs, scores each against Aylin's profile using Claude Haiku, and manages the full pipeline. Interview prep generates STAR stories and likely questions via Claude Opus, then syncs to Google Drive. ElevenLabs converts prep to audio for practice.",
        "stack": [("Search", "APIs + JSearch", SEARCH), ("LLM", "Claude Haiku + Opus", LLM), ("Memory", "SQLite + Drive", MEM), ("Audio", "ElevenLabs", ACTION)],
        "metrics": [("Applications tracked", "358"), ("Response rate", "5%"), ("Active interviews", "0")],
    },
    {
        "id": "restaurant",
        "name": "Fork Yeah!",
        "gradient": "linear-gradient(145deg,#052e16,#065f46)",
        "accent": MEM,
        "url": "http://localhost:5173",
        "new_tab": True,
        "icon_svg": f"""
<svg viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" width="64" height="45">
  <!-- LangGraph: 8-node pipeline with fan-out routing -->
  <line x1="8"  y1="28" x2="22" y2="18" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="8"  y1="28" x2="22" y2="38" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="30" y1="18" x2="44" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="30" y1="38" x2="44" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="52" y1="28" x2="65" y2="18" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="52" y1="28" x2="65" y2="38" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <circle cx="8"  cy="28" r="7" fill="{SEARCH}" opacity=".9"/>
  <circle cx="26" cy="18" r="6" fill="{SEARCH}" opacity=".75"/>
  <circle cx="26" cy="38" r="6" fill="{MEM}"    opacity=".75"/>
  <circle cx="48" cy="28" r="7" fill="{LLM}"    class="llm-pulse"/>
  <circle cx="70" cy="18" r="6" fill="{ACTION}" opacity=".9"/>
  <circle cx="70" cy="38" r="6" fill="{NOTIFY}" opacity=".9"/>
  <text x="8"  y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5">Intent</text>
  <text x="48" y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5">Claude</text>
  <text x="70" y="10" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5">Book</text>
  <text x="70" y="52" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5">Email</text>
</svg>""",
        "tagline": "Natural language → confirmed restaurant reservation with email.",
        "what": "LangGraph pipeline with 8 specialized nodes: intent parsing → venue search via Tavily → availability scrape via Playwright → ChromaDB memory lookup → preference matching → booking → confirmation email via Resend. Streams each step live via SSE so you watch the agent work in real time.",
        "stack": [("Orchestration", "LangGraph", LLM), ("Search", "Tavily", SEARCH), ("Scraping", "Playwright", SEARCH), ("Memory", "ChromaDB", MEM), ("Notify", "Resend", NOTIFY)],
        "metrics": [("Agent nodes", "8"), ("Streaming", "SSE live"), ("Memory", "ChromaDB RAG")],
    },
    {
        "id": "cs-triage",
        "name": "CS Triage",
        "gradient": "linear-gradient(145deg,#052e16,#166534)",
        "accent": "#4ade80",
        "url": "http://localhost:8501",
        "new_tab": True,
        "icon_svg": f"""
<svg viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" width="64" height="45">
  <!-- Simple: Input → Haiku → 4 routing outputs -->
  <line x1="15" y1="28" x2="32" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="46" y1="22" x2="58" y2="12" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="46" y1="26" x2="58" y2="22" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="46" y1="30" x2="58" y2="34" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="46" y1="34" x2="58" y2="44" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <circle cx="8"  cy="28" r="7" fill="{SEARCH}" opacity=".9"/>
  <circle cx="39" cy="28" r="7" fill="{LLM}"    class="llm-pulse"/>
  <circle cx="64" cy="11" r="5" fill="{ACTION}" opacity=".85"/>
  <circle cx="64" cy="23" r="5" fill="{MEM}"    opacity=".85"/>
  <circle cx="64" cy="35" r="5" fill="{GATE}"   opacity=".85"/>
  <circle cx="64" cy="45" r="5" fill="{NOTIFY}" opacity=".85"/>
  <text x="8"  y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Ticket</text>
  <text x="39" y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Haiku</text>
  <text x="76" y="13" text-anchor="start"  fill="rgba(255,255,255,.3)"  font-size="5">Billing</text>
  <text x="76" y="25" text-anchor="start"  fill="rgba(255,255,255,.3)"  font-size="5">Tech</text>
  <text x="76" y="37" text-anchor="start"  fill="rgba(255,255,255,.3)"  font-size="5">Acct</text>
  <text x="76" y="49" text-anchor="start"  fill="rgba(255,255,255,.3)"  font-size="5">Gen</text>
</svg>""",
        "tagline": "Inbound support ticket classified and routed in under 1 second.",
        "what": "Every inbound ticket hits Claude Haiku, which classifies it into one of four categories (Billing, Technical, Account, General) and routes to the right team. Demonstrates how fast and cheap Haiku is for real-time classification at scale — sub-second, cents per thousand tickets.",
        "stack": [("LLM", "Claude Haiku 3.5", LLM), ("Interface", "Streamlit", SEARCH), ("API", "FastAPI", ACTION)],
        "metrics": [("Latency", "<1s"), ("Cost", "~$0.001/ticket"), ("Categories", "4")],
    },
    {
        "id": "networking",
        "name": "Networking",
        "gradient": "linear-gradient(145deg,#0c1a3a,#1e3a8a)",
        "accent": SEARCH,
        "url": "/networking",
        "new_tab": False,
        "icon_svg": f"""
<svg viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" width="64" height="45">
  <!-- Linear 4-node pipeline with human gate -->
  <line x1="15" y1="28" x2="27" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="41" y1="28" x2="53" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="67" y1="22" x2="67" y2="38" stroke="rgba(255,255,255,.18)" stroke-width="1" stroke-dasharray="2,2"/>
  <!-- human gate branch -->
  <line x1="60" y1="28" x2="72" y2="20" stroke="rgba(255,255,255,.15)" stroke-width="1"/>
  <line x1="60" y1="28" x2="72" y2="36" stroke="rgba(255,255,255,.15)" stroke-width="1"/>
  <circle cx="8"  cy="28" r="7" fill="{SEARCH}" opacity=".9"/>
  <circle cx="34" cy="28" r="7" fill="{LLM}"    class="llm-pulse"/>
  <circle cx="60" cy="28" r="7" fill="{ACTION}" opacity=".9"/>
  <circle cx="74" cy="20" r="5" fill="{GATE}"   opacity=".85"/>
  <circle cx="74" cy="36" r="5" fill="{MEM}"    opacity=".85"/>
  <text x="8"  y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Scrape</text>
  <text x="34" y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Score</text>
  <text x="60" y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Draft</text>
  <text x="74" y="13" text-anchor="middle" fill="rgba(255,255,255,.3)"  font-size="5">Gate</text>
  <text x="74" y="49" text-anchor="middle" fill="rgba(255,255,255,.3)"  font-size="5">CRM</text>
</svg>""",
        "tagline": "130+ targets. Research, score, draft outreach — human approves before send.",
        "what": "Playwright scrapes LinkedIn contact profiles, Claude scores fit against Aylin's background and drafts a personalized outreach email. Everything queues in Airtable for human review. Nothing sends without approval — a deliberate human-in-the-loop gate that prevents the agent from acting autonomously.",
        "stack": [("Search", "Playwright + BS4", SEARCH), ("LLM", "Claude", LLM), ("Gate", "Human approval", GATE), ("CRM", "Airtable", MEM)],
        "metrics": [("Target companies", "130+"), ("Gate", "Human-in-loop"), ("CRM", "Airtable")],
    },
    {
        "id": "outreach",
        "name": "Finance Outreach",
        "gradient": "linear-gradient(145deg,#2e1065,#5b21b6)",
        "accent": GATE,
        "url": "/outreach",
        "new_tab": False,
        "icon_svg": f"""
<svg viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" width="64" height="45">
  <!-- contacts → fit score → draft → human gate → send -->
  <line x1="15" y1="28" x2="27" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="41" y1="28" x2="53" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="67" y1="28" x2="75" y2="20" stroke="rgba(255,255,255,.18)" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="67" y1="28" x2="75" y2="36" stroke="rgba(255,255,255,.18)" stroke-width="1" stroke-dasharray="2,2"/>
  <circle cx="8"  cy="28" r="7" fill="{SEARCH}" opacity=".9"/>
  <circle cx="34" cy="28" r="7" fill="{LLM}"    class="llm-pulse"/>
  <circle cx="60" cy="28" r="7" fill="{ACTION}" opacity=".9"/>
  <circle cx="76" cy="20" r="4" fill="{GATE}"   opacity=".85"/>
  <circle cx="76" cy="36" r="4" fill="{NOTIFY}" opacity=".85"/>
  <text x="8"  y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Contacts</text>
  <text x="34" y="12" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Fit Score</text>
  <text x="60" y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Draft</text>
</svg>""",
        "tagline": "Finance sector AI roles. AI-scored fit, personalized per contact.",
        "what": "Targets JPMorgan and finance-sector AI roles. Claude evaluates each contact against Aylin's profile (MBA, Deloitte, Skild AI) and generates a personalized cold email. A human approval gate in Airtable sits between draft and send — the agent never sends autonomously.",
        "stack": [("Data", "Playwright", SEARCH), ("LLM", "Claude", LLM), ("Draft", "Personalized", ACTION), ("Gate", "Human review", GATE), ("CRM", "Airtable", MEM)],
        "metrics": [("Primary target", "JPMorgan"), ("Scoring", "AI fit ranking"), ("Gate", "Human send")],
    },
    {
        "id": "evals",
        "name": "Evals",
        "gradient": "linear-gradient(145deg,#1a0530,#3b0764)",
        "accent": GATE,
        "url": "/evals",
        "new_tab": False,
        "icon_svg": f"""
<svg viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" width="64" height="45">
  <!-- v1 prompt → test cases → precision/recall delta vs v2 -->
  <line x1="8"  y1="18" x2="22" y2="18" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="8"  y1="38" x2="22" y2="38" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="36" y1="18" x2="48" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="36" y1="38" x2="48" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="56" y1="28" x2="70" y2="18" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="56" y1="28" x2="70" y2="38" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <circle cx="8"  cy="18" r="6" fill="{LLM}"    opacity=".75"/>
  <circle cx="8"  cy="38" r="6" fill="{LLM}"    opacity=".9" class="llm-pulse"/>
  <circle cx="29" cy="18" r="6" fill="{SEARCH}" opacity=".8"/>
  <circle cx="29" cy="38" r="6" fill="{SEARCH}" opacity=".8"/>
  <circle cx="52" cy="28" r="7" fill="{MEM}"    opacity=".9"/>
  <circle cx="74" cy="18" r="5" fill="{GATE}"   opacity=".9"/>
  <circle cx="74" cy="38" r="5" fill="{ACTION}" opacity=".9"/>
  <text x="8"  y="10" text-anchor="middle" fill="rgba(255,255,255,.3)"  font-size="5">v1</text>
  <text x="8"  y="52" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5">v2</text>
  <text x="29" y="10" text-anchor="middle" fill="rgba(255,255,255,.3)"  font-size="5">cases</text>
  <text x="52" y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5">eval</text>
  <text x="74" y="10" text-anchor="middle" fill="rgba(255,255,255,.3)"  font-size="5">P/R</text>
  <text x="74" y="50" text-anchor="middle" fill="rgba(255,255,255,.3)"  font-size="5">cost</text>
</svg>""",
        "tagline": "25 labeled test cases. Precision/recall delta across prompt versions.",
        "what": "Runs v1 and v2 scoring prompts against 25 labeled test cases derived from 18 real interview outcomes. Computes precision, recall, F1, and confusion matrix per prompt. Every API call is logged with model, tokens, cost, and latency — full observability. Shows exactly how the prompt improved and what it costs to run.",
        "stack": [("Test data", "18 real outcomes", MEM), ("LLM", "Claude Haiku (x50 calls)", LLM), ("Metrics", "Precision/Recall/F1", GATE), ("Cost", "Token logging", ACTION)],
        "metrics": [("Test cases", "25 labeled"), ("Ground truth", "18 interviews"), ("Metrics", "P/R/F1")],
    },
    {
        "id": "research",
        "name": "Research",
        "gradient": "linear-gradient(145deg,#500724,#9d174d)",
        "accent": GATE,
        "url": "/research",
        "new_tab": False,
        "icon_svg": f"""
<svg viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" width="64" height="45">
  <!-- Fan-in: 3 Tavily searches → Claude Opus → structured output → Drive -->
  <line x1="13" y1="12" x2="33" y2="26" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="13" y1="28" x2="33" y2="28" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="13" y1="44" x2="33" y2="30" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="47" y1="28" x2="59" y2="18" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <line x1="47" y1="28" x2="59" y2="38" stroke="rgba(255,255,255,.2)" stroke-width="1.2"/>
  <circle cx="8"  cy="12" r="5" fill="{SEARCH}" opacity=".75"/>
  <circle cx="8"  cy="28" r="5" fill="{SEARCH}" opacity=".85"/>
  <circle cx="8"  cy="44" r="5" fill="{SEARCH}" opacity=".75"/>
  <circle cx="40" cy="28" r="7" fill="{LLM}"    class="llm-pulse"/>
  <circle cx="64" cy="18" r="6" fill="{ACTION}" opacity=".9"/>
  <circle cx="64" cy="38" r="6" fill="{MEM}"    opacity=".9"/>
  <text x="40" y="43" text-anchor="middle" fill="rgba(255,255,255,.35)" font-size="5.5">Opus</text>
  <text x="4"  y="28" text-anchor="end"   fill="rgba(255,255,255,.3)"  font-size="5">Tavily</text>
  <text x="72" y="10" text-anchor="start" fill="rgba(255,255,255,.3)"  font-size="5">Brief</text>
  <text x="72" y="50" text-anchor="start" fill="rgba(255,255,255,.3)"  font-size="5">Drive</text>
</svg>""",
        "tagline": "Any company. Live web intel + Claude Opus synthesis in seconds.",
        "what": "Tavily runs 3 parallel searches (news + funding + hiring signals), feeds all results to Claude Opus which synthesizes a structured JSON brief: investors, leadership, AI angle, hiring culture, visa sponsorship. Cached to SQLite and synced to Google Drive. Try it live — type any company.",
        "stack": [("Search", "Tavily (3 queries)", SEARCH), ("LLM", "Claude Opus 4.6", LLM), ("Output", "Structured JSON", ACTION), ("Storage", "SQLite + Drive", MEM)],
        "metrics": [("Queries per run", "3 parallel"), ("Model", "Claude Opus"), ("Cache", "SQLite + Drive")],
    },
]


def render_home(metrics: dict = None, api_metrics: dict = None, eval_metrics: dict = None) -> str:
    m = metrics or {}
    am = api_metrics or {}
    ev = eval_metrics or {}  # latest eval run metrics
    now = datetime.now().strftime("%H:%M")

    # Eval display values
    v2m = ev.get("v2", {}).get("metrics", {}) if ev else {}
    v1m = ev.get("v1", {}).get("metrics", {}) if ev else {}
    f1_val = f"{v2m.get('f1', 0):.0%}" if v2m else "—"
    prec_val = f"{v2m.get('precision', 0):.0%}" if v2m else "—"
    rec_val = f"{v2m.get('recall', 0):.0%}" if v2m else "—"
    f1_delta = v2m.get("f1", 0) - v1m.get("f1", 0) if (v2m and v1m) else None
    delta_str = (f"+{f1_delta:.0%}" if f1_delta and f1_delta > 0 else
                 f"{f1_delta:.0%}" if f1_delta else "run evals")
    delta_color = "#34d399" if f1_delta and f1_delta > 0 else "#fb923c"
    cost_str = f"${am.get('total_cost_usd', 0):.3f}"
    calls_str = str(am.get("total_calls", 0))

    def icon_card(app):
        return f"""<div class="icon-cell" onclick="showSheet('{app['id']}')">
  <div class="app-icon" style="background:{app['gradient']}">
    {app['icon_svg']}
  </div>
  <div class="app-label">{app['name']}</div>
</div>"""

    def launch_sheet(app):
        stack_html = "".join(
            f'<div class="stk-row"><div class="stk-dot" style="background:{c}"></div>'
            f'<div class="stk-type">{t}</div><div class="stk-name">{n}</div></div>'
            for t, n, c in app["stack"]
        )
        metrics_html = "".join(
            f'<div class="met-cell"><div class="met-v">{v}</div><div class="met-k">{k}</div></div>'
            for k, v in app["metrics"]
        )
        target = "_blank"
        return f"""<div class="sheet" id="sheet-{app['id']}">
  <div class="sheet-bg" onclick="hideSheet('{app['id']}')"></div>
  <div class="sheet-card">
    <div class="sheet-pull"></div>
    <div class="sheet-top">
      <div class="sheet-iconbox" style="background:{app['gradient']}">{app['icon_svg']}</div>
      <div>
        <div class="sheet-name">{app['name']}</div>
        <div class="sheet-tag">{app['tagline']}</div>
      </div>
    </div>
    <div class="sheet-desc">{app['what']}</div>
    <div class="sheet-metrics">{metrics_html}</div>
    <div class="sheet-stack-label">Stack</div>
    <div class="sheet-stack">{stack_html}</div>
    <a href="{app['url']}" target="{target}" class="sheet-open"
       style="border-color:{app['accent']}44;color:{app['accent']};background:{app['accent']}12"
       onclick="hideSheet('{app['id']}')">
      Open Agent ↗
    </a>
  </div>
</div>"""

    icons_html  = "".join(icon_card(a) for a in APPS)
    sheets_html = "".join(launch_sheet(a) for a in APPS)
    all_ids     = "[" + ",".join(f'"{a["id"]}"' for a in APPS) + "]"

    def _dock_icon(a):
        inner = a["icon_svg"].split("<svg")[1].split(">", 1)[1].rsplit("</svg>", 1)[0]
        return (f'<div class="di" id="icon-{a["id"]}" style="background:{a["gradient"]}" '
                f'onclick="showSheet(\'{a["id"]}\')" title="{a["name"]}">'
                f'<svg viewBox="0 0 80 56" width="42" height="30">{inner}</svg></div>')

    dock_html = "".join(_dock_icon(a) for a in APPS)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AylinOS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --bg:    #080810;
  --ink:   #f0f0f5;
  --ink-2: rgba(240,240,245,.55);
  --ink-3: rgba(240,240,245,.28);
  --b:     rgba(255,255,255,.08);
  --mono:  'JetBrains Mono','Menlo',monospace;
  --sans:  'Inter',system-ui,sans-serif;
}}

html, body {{
  height: 100%; overflow: hidden;
  font-family: var(--sans);
  background: var(--bg);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
}}

/* LLM node pulse */
.llm-pulse {{
  animation: llm 2.8s ease-in-out infinite;
  transform-origin: center;
}}
@keyframes llm {{
  0%,100% {{ opacity:.9; r:7; }}
  50%      {{ opacity:.55; r:8.5; }}
}}

/* ── Wallpaper ─────────────────────────────── */
#screen {{
  width:100vw; height:100vh;
  display:flex; flex-direction:column;
  /* Dot-grid wallpaper — feels like a technical background, not a web hero */
  background-image:
    radial-gradient(ellipse 80% 50% at 50% 10%, rgba(79,70,229,.14) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 5%  85%, rgba(52,211,153,.07) 0%, transparent 45%),
    radial-gradient(ellipse 45% 35% at 95% 60%, rgba(244,114,182,.05) 0%, transparent 40%),
    radial-gradient(circle at 1px 1px, rgba(255,255,255,.04) 1px, transparent 0);
  background-size: auto, auto, auto, 28px 28px;
  background-color: var(--bg);
}}

/* ── Status bar ────────────────────────────── */
#sb {{
  height:32px; flex-shrink:0;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 24px;
  background:rgba(8,8,16,.7);
  backdrop-filter:blur(16px);
  border-bottom:1px solid var(--b);
}}
.sb-brand {{
  font-family:var(--mono); font-size:12px; font-weight:600;
  color:var(--ink); letter-spacing:.02em;
}}
.sb-right {{ display:flex; align-items:center; gap:18px; }}
.sb-pill {{
  display:flex; align-items:center; gap:5px;
  font-family:var(--mono); font-size:10px; color:var(--ink-3);
}}
.sb-dot {{ width:5px; height:5px; border-radius:50%; flex-shrink:0; }}
.sb-dot.pulse {{ animation:dot-pulse 2s ease-in-out infinite; }}
@keyframes dot-pulse {{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
#sb-clock {{
  font-family:var(--mono); font-size:12px; font-weight:600;
  color:var(--ink-2);
}}

/* ── Icon grid ─────────────────────────────── */
/* Icons sit directly on the wallpaper — no container, no title text */
#grid {{
  flex:1;
  display:grid;
  grid-template-columns: repeat(3,1fr);
  align-content:center;
  justify-items:center;
  gap:24px 0;
  padding:20px 48px 0;
  max-width:720px;
  margin:0 auto;
  width:100%;
  min-height:0;
}}

.icon-cell {{
  display:flex; flex-direction:column; align-items:center;
  gap:9px; cursor:pointer; width:120px;
}}
.app-icon {{
  width:88px; height:88px; border-radius:20px;
  display:flex; align-items:center; justify-content:center;
  box-shadow:
    0 4px 24px rgba(0,0,0,.55),
    0 1px 0 rgba(255,255,255,.13) inset,
    0 -1px 0 rgba(0,0,0,.4) inset;
  transition:transform 180ms cubic-bezier(.34,1.4,.64,1), box-shadow 180ms;
  overflow:hidden;
}}
.icon-cell:hover .app-icon {{
  transform:scale(1.1);
  box-shadow:0 10px 36px rgba(0,0,0,.6), 0 1px 0 rgba(255,255,255,.16) inset;
}}
.icon-cell:active .app-icon {{
  transform:scale(.94); transition-duration:80ms;
}}
.app-label {{
  font-size:11px; font-weight:500;
  color:rgba(240,240,245,.82);
  text-align:center; letter-spacing:.01em;
  text-shadow:0 1px 4px rgba(0,0,0,.9);
}}

/* ── Search zone ───────────────────────────── */
#search-zone {{
  flex-shrink:0;
  display:flex; flex-direction:column; align-items:center;
  padding:32px 24px 20px;
}}
.os-prompt {{
  font-family:var(--mono); font-size:10px;
  color:var(--ink-3); letter-spacing:.1em;
  text-transform:uppercase; margin-bottom:20px;
}}
.search-wrap {{
  width:100%; max-width:640px; position:relative;
}}
#search-bar {{
  width:100%;
  background:rgba(255,255,255,.05);
  border:1px solid rgba(255,255,255,.12);
  border-radius:12px;
  padding:15px 52px 15px 20px;
  font-family:var(--sans); font-size:15px;
  color:var(--ink); outline:none;
  transition:border-color 150ms, box-shadow 150ms;
}}
#search-bar::placeholder {{ color:var(--ink-3); }}
#search-bar:focus {{
  border-color:rgba(129,140,248,.5);
  box-shadow:0 0 0 3px rgba(129,140,248,.08);
}}
.search-cmd {{
  position:absolute; right:16px; top:50%;
  transform:translateY(-50%);
  font-family:var(--mono); font-size:11px;
  color:var(--ink-3); pointer-events:none;
}}

/* Route indicator */
#route-row {{
  display:flex; align-items:center; gap:8px;
  margin-top:10px; height:22px;
  opacity:0; transition:opacity 250ms;
}}
#route-row.visible {{ opacity:1; }}
.route-arrow {{ font-family:var(--mono); font-size:10px; color:var(--ink-3); }}
#route-badge {{
  font-family:var(--mono); font-size:10px; font-weight:500;
  padding:3px 9px; border-radius:4px;
}}
#route-reason {{ font-size:11px; color:var(--ink-3); }}

/* ── Output panel ──────────────────────────── */
#output-panel {{
  flex:1; min-height:0;
  width:100%; max-width:688px;
  margin:0 auto;
  padding:0 24px 16px;
  overflow:hidden;
  display:flex; flex-direction:column;
  opacity:0; transition:opacity 250ms;
}}
#output-panel.visible {{ opacity:1; }}
#output-card {{
  background:#111116;
  border:1px solid var(--b);
  border-radius:10px;
  overflow:hidden;
  flex:1; display:flex; flex-direction:column;
  min-height:0;
}}
#output-header {{
  display:flex; align-items:center; gap:10px;
  padding:11px 16px;
  border-bottom:1px solid var(--b);
  flex-shrink:0;
}}
#agent-dot {{ width:6px; height:6px; border-radius:50%; animation:dot-pulse 1.2s ease-in-out infinite; }}
#agent-name {{ font-family:var(--mono); font-size:11px; color:var(--ink-3); }}
#output-body {{
  padding:16px; flex:1; overflow-y:auto;
  font-family:var(--mono); font-size:12px;
  color:var(--ink-2); line-height:1.8;
  white-space:pre-wrap; word-break:break-word;
}}
/* Section labels that appear inline in the stream */
#output-body .sec-label {{
  display:block;
  font-size:9px; color:var(--ink-3);
  text-transform:uppercase; letter-spacing:.08em;
  margin-top:14px; margin-bottom:4px;
}}
#output-body .sec-label:first-child {{ margin-top:0; }}
.cursor {{
  display:inline-block; width:2px; height:13px;
  background:var(--llm); vertical-align:middle;
  margin-left:1px; animation:blink .7s step-end infinite;
}}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0}} }}

/* ── Telemetry strip ───────────────────────── */
#telem {{
  flex-shrink:0;
  display:flex; justify-content:center;
  padding:6px 24px 8px;
}}
#telem-inner {{
  display:flex; align-items:center; gap:0;
  background:rgba(255,255,255,.025);
  border:1px solid rgba(255,255,255,.06);
  border-radius:8px; overflow:hidden;
}}
.tel-cell {{
  padding:5px 14px;
  border-right:1px solid rgba(255,255,255,.05);
  text-align:center; text-decoration:none; display:block;
  transition:background 150ms; cursor:default;
}}
.tel-cell:last-child {{ border-right:none; }}
.tel-cell.clickable {{ cursor:pointer; }}
.tel-cell.clickable:hover {{ background:rgba(255,255,255,.04); }}
.tel-val {{
  font-family:var(--mono); font-size:11px; font-weight:600;
  color:var(--ink);
}}
.tel-key {{
  font-family:var(--mono); font-size:9px; color:var(--ink-3);
  text-transform:uppercase; letter-spacing:.06em; margin-top:1px;
}}
.tel-badge {{
  display:inline-block; padding:1px 5px; border-radius:3px;
  font-family:var(--mono); font-size:8px; font-weight:600; margin-left:4px;
}}

/* ── Dock ──────────────────────────────────── */
#dock-row {{
  display:flex; justify-content:center;
  padding:12px 16px 20px; flex-shrink:0;
  overflow-x:auto;
}}
#dock {{
  display:flex; align-items:center; gap:10px;
  padding:10px 14px;
  background:rgba(255,255,255,.07);
  backdrop-filter:blur(40px);
  border:1px solid rgba(255,255,255,.11);
  border-radius:22px;
  flex-shrink:0;
}}
.di {{
  width:52px; height:52px; border-radius:13px;
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; overflow:hidden;
  box-shadow:0 2px 10px rgba(0,0,0,.45),0 1px 0 rgba(255,255,255,.1) inset;
  transition:transform 200ms cubic-bezier(.34,1.4,.64,1);
}}
.di:hover {{ transform:translateY(-9px) scale(1.18); }}
.di.di-active {{ box-shadow:0 0 0 2px rgba(129,140,248,.7),0 4px 20px rgba(0,0,0,.5); transform:translateY(-5px); }}
.di:active {{ transform:scale(.9); transition-duration:80ms; }}

/* ── Sheet ─────────────────────────────────── */
.sheet {{
  position:fixed; inset:0; z-index:900;
  display:none; align-items:flex-end; justify-content:center;
}}
.sheet.open {{ display:flex; }}
.sheet-bg {{
  position:absolute; inset:0;
  background:rgba(0,0,0,.65);
  backdrop-filter:blur(6px);
  animation:fi 200ms ease;
}}
.sheet-card {{
  position:relative; z-index:1;
  background:#111119;
  border:1px solid rgba(255,255,255,.12); border-bottom:none;
  border-radius:20px 20px 0 0;
  padding:10px 28px 44px;
  width:100%; max-width:580px;
  animation:su 260ms cubic-bezier(.34,1.15,.64,1);
}}
.sheet-pull {{
  width:32px; height:4px; border-radius:2px;
  background:rgba(255,255,255,.16);
  margin:0 auto 22px;
}}
.sheet-top {{
  display:flex; align-items:center; gap:14px; margin-bottom:16px;
}}
.sheet-iconbox {{
  width:52px; height:52px; border-radius:12px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 4px 16px rgba(0,0,0,.4),0 1px 0 rgba(255,255,255,.1) inset;
  overflow:hidden;
}}
.sheet-name {{
  font-size:17px; font-weight:700; letter-spacing:-.02em; margin-bottom:3px;
}}
.sheet-tag {{
  font-size:12px; color:var(--ink-2); line-height:1.5;
}}
.sheet-desc {{
  font-size:13px; color:var(--ink-2); line-height:1.75;
  margin-bottom:18px; max-width:52ch;
}}
.sheet-metrics {{
  display:flex; gap:0; margin-bottom:18px;
  background:rgba(255,255,255,.03);
  border:1px solid var(--b); border-radius:10px;
  overflow:hidden;
}}
.met-cell {{
  flex:1; padding:12px 16px; text-align:center;
  border-right:1px solid var(--b);
}}
.met-cell:last-child {{ border-right:none; }}
.met-v {{
  font-family:var(--mono); font-size:14px; font-weight:600;
  color:var(--ink); margin-bottom:3px;
}}
.met-k {{
  font-family:var(--mono); font-size:9px; color:var(--ink-3);
  text-transform:uppercase; letter-spacing:.07em;
}}
.sheet-stack-label {{
  font-family:var(--mono); font-size:9px; color:var(--ink-3);
  text-transform:uppercase; letter-spacing:.08em; margin-bottom:8px;
}}
.sheet-stack {{ display:flex; flex-direction:column; gap:6px; margin-bottom:20px; }}
.stk-row {{ display:flex; align-items:center; gap:10px; }}
.stk-dot {{ width:7px; height:7px; border-radius:50%; flex-shrink:0; }}
.stk-type {{
  font-family:var(--mono); font-size:9px; color:var(--ink-3);
  text-transform:uppercase; letter-spacing:.06em; width:72px;
}}
.stk-name {{ font-size:12px; color:var(--ink-2); }}
.sheet-open {{
  display:flex; align-items:center; justify-content:center;
  width:100%; padding:13px;
  border-radius:11px; border:1px solid;
  font-size:13px; font-weight:600;
  text-decoration:none;
  transition:filter 150ms;
}}
.sheet-open:hover {{ filter:brightness(1.2); }}

@keyframes fi {{ from{{opacity:0}} to{{opacity:1}} }}
@keyframes su {{ from{{transform:translateY(100%)}} to{{transform:translateY(0)}} }}
@media (prefers-reduced-motion:reduce) {{
  .app-icon,.di,.llm-pulse,.sb-dot,.sheet-card,.sheet-bg {{ animation:none;transition:none; }}
}}
</style>
</head>
<body>
<div id="screen">

  <div id="sb">
    <span class="sb-brand">AylinOS</span>
    <div class="sb-right">
      <div class="sb-pill">
        <div class="sb-dot pulse" style="background:{LLM}"></div>
        <span>Claude API</span>
      </div>
      <div class="sb-pill">
        <div class="sb-dot pulse" style="background:{SEARCH};animation-delay:.4s"></div>
        <span>Tavily</span>
      </div>
      <div class="sb-pill">
        <div class="sb-dot pulse" style="background:{MEM};animation-delay:.8s"></div>
        <span>SQLite</span>
      </div>
      <div class="sb-pill">
        <div class="sb-dot" style="background:#34d399"></div>
        <span>{m.get('applied', 358)} tracked &nbsp;·&nbsp; {m.get('interviewing', 0)} active &nbsp;·&nbsp; 7 agents</span>
      </div>
      <span id="sb-clock">{now}</span>
    </div>
  </div>

  <!-- Search zone -->
  <div id="search-zone">
    <div class="os-prompt">What can I help you with today?</div>
    <div class="search-wrap">
      <input
        id="search-bar"
        type="text"
        placeholder="should I apply to Ramp · prep me for Hebbia interview · book dinner in Soho..."
        autocomplete="off"
        spellcheck="false"
      />
      <span class="search-cmd">⌘K</span>
      <div id="route-row">
        <span class="route-arrow">→</span>
        <span id="route-badge"></span>
        <span id="route-reason"></span>
      </div>
    </div>
  </div>

  <!-- Streaming output panel -->
  <div id="output-panel">
    <div id="output-card">
      <div id="output-header">
        <div id="agent-dot" style="background:{LLM}"></div>
        <span id="agent-name">ready</span>
      </div>
      <div id="output-body"></div>
    </div>
  </div>

  <!-- Telemetry strip -->
  <div id="telem">
    <div id="telem-inner">
      <a href="/evals" class="tel-cell clickable">
        <div class="tel-val">{f1_val}<span class="tel-badge" style="background:{delta_color}18;color:{delta_color};border:1px solid {delta_color}33">{delta_str}</span></div>
        <div class="tel-key">F1 · evals</div>
      </a>
      <div class="tel-cell">
        <div class="tel-val">{prec_val}</div>
        <div class="tel-key">Precision</div>
      </div>
      <div class="tel-cell">
        <div class="tel-val">{rec_val}</div>
        <div class="tel-key">Recall</div>
      </div>
      <div class="tel-cell">
        <div class="tel-val">{cost_str}</div>
        <div class="tel-key">API cost</div>
      </div>
      <div class="tel-cell">
        <div class="tel-val">{calls_str}</div>
        <div class="tel-key">Calls</div>
      </div>
      <div class="tel-cell">
        <div class="tel-val" style="color:{LLM}">v2</div>
        <div class="tel-key">Prompt</div>
      </div>
    </div>
  </div>

  <!-- Icon dock -->
  <div id="dock-row">
    <div id="dock">
      {dock_html}
    </div>
  </div>

</div>

{sheets_html}

<script>
const IDS = {all_ids};

// ── Sheet controls ──
function showSheet(id) {{ document.getElementById('sheet-'+id).classList.add('open'); }}
function hideSheet(id) {{ document.getElementById('sheet-'+id).classList.remove('open'); }}
document.addEventListener('keydown', e => {{
  if (e.key === 'Escape') IDS.forEach(hideSheet);
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {{
    e.preventDefault();
    document.getElementById('search-bar').focus();
  }}
}});

// ── Clock ──
function tick() {{
  document.getElementById('sb-clock').textContent =
    new Date().toLocaleTimeString('en-US',{{hour:'2-digit',minute:'2-digit',hour12:false}});
}}
tick(); setInterval(tick, 1000);

// ── Agent color map ──
const AGENT_COLORS = {{
  advisor:        '{LLM}',
  interview_prep: '{LLM}',
  research:       '{GATE}',
  cs_triage:      '{MEM}',
  restaurant:     '{MEM}',
  job_search:     '{LLM}',
  general:        '{SEARCH}',
}};
const AGENT_LABELS = {{
  advisor:        'Career Advisor',
  interview_prep: 'Interview Prep',
  research:       'Research',
  cs_triage:      'CS Triage',
  restaurant:     'Fork Yeah!',
  job_search:     'Job Search',
  general:        'AylinOS',
}};
const AGENT_ICONS = {{
  advisor:        'icon-advisor',
  interview_prep: 'icon-jobs',
  research:       'icon-research',
  cs_triage:      'icon-cs-triage',
  restaurant:     'icon-restaurant',
  job_search:     'icon-jobs',
  general:        null,
}};

// ── Stream handler ──
const searchBar  = document.getElementById('search-bar');
const routeRow   = document.getElementById('route-row');
const routeBadge = document.getElementById('route-badge');
const routeReason = document.getElementById('route-reason');
const outputPanel = document.getElementById('output-panel');
const outputBody  = document.getElementById('output-body');
const agentDot    = document.getElementById('agent-dot');
const agentName   = document.getElementById('agent-name');

let activeStream = null;

searchBar.addEventListener('keydown', e => {{
  if (e.key === 'Enter') runQuery();
}});

function highlightIcon(agent) {{
  document.querySelectorAll('.di').forEach(el => el.classList.remove('di-active'));
  const iconId = AGENT_ICONS[agent];
  if (iconId) {{
    const el = document.getElementById(iconId);
    if (el) el.classList.add('di-active');
  }}
}}

// Parse streamed text into labeled sections for display
function renderToken(text) {{
  // Accumulate in a buffer, render sections as they complete
  outputBody._buf = (outputBody._buf || '') + text;

  // Re-render the whole buffer each time (simple, works for short outputs)
  const raw = outputBody._buf;
  const sectionRe = /^([A-Z][A-Z &\/]+):$/m;
  const parts = raw.split(/(^[A-Z][A-Z &\/]+:$)/m);

  let html = '';
  for (let i = 0; i < parts.length; i++) {{
    const part = parts[i];
    if (sectionRe.test(part.trim())) {{
      html += `<span class="sec-label">${{part.trim().replace(/:$/, '')}}</span>`;
    }} else {{
      html += part;
    }}
  }}
  html += '<span class="cursor"></span>';
  outputBody.innerHTML = html;
  outputBody.scrollTop = outputBody.scrollHeight;
}}

async function runQuery() {{
  const query = searchBar.value.trim();
  if (!query) return;

  // Reset UI
  outputBody._buf = '';
  outputBody.innerHTML = '';
  routeRow.classList.remove('visible');
  outputPanel.classList.remove('visible');
  document.querySelectorAll('.di').forEach(el => el.classList.remove('di-active'));
  agentName.textContent = 'routing...';
  agentDot.style.background = '{LLM}';

  // Show output panel immediately
  outputPanel.classList.add('visible');

  try {{
    const resp = await fetch('/api/stream', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{query}})
    }});

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {{
      const {{done, value}} = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, {{stream: true}});
      const lines = buffer.split('\\n');
      buffer = lines.pop(); // keep incomplete line

      for (const line of lines) {{
        if (!line.startsWith('data: ')) continue;
        const data = JSON.parse(line.slice(6));

        if (data.type === 'route') {{
          const color = AGENT_COLORS[data.agent] || '{LLM}';
          const label = AGENT_LABELS[data.agent] || data.agent;
          agentDot.style.background = color;
          agentName.textContent = label + ' · running';
          routeBadge.textContent = label;
          routeBadge.style.cssText = `background:${{color}}18;color:${{color}};border:1px solid ${{color}}33;font-family:var(--mono);font-size:10px;font-weight:500;padding:3px 9px;border-radius:4px`;
          routeReason.textContent = data.reason;
          routeRow.classList.add('visible');
          highlightIcon(data.agent);
        }}

        else if (data.type === 'token') {{
          renderToken(data.text);
        }}

        else if (data.type === 'done') {{
          agentName.textContent = AGENT_LABELS[agentName.textContent.split(' ·')[0]] || 'done';
          // Remove cursor
          const cur = outputBody.querySelector('.cursor');
          if (cur) cur.remove();
          agentName.textContent = agentName.textContent.replace(' · running', ' · done');
        }}

        else if (data.type === 'error') {{
          outputBody.innerHTML = `<span style="color:#f87171">${{data.message}}</span>`;
        }}
      }}
    }}
  }} catch(e) {{
    outputBody.innerHTML = `<span style="color:#f87171">Connection error: ${{e.message}}</span>`;
  }}
}}
</script>
</body>
</html>"""
