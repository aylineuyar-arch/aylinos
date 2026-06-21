"""
AylinOS — Query Router + Streaming Agent
-----------------------------------------
Takes a natural language query, uses Claude to classify intent and pick
the right agent, then streams that agent's response as SSE events.

Agents:
  advisor       → "should I apply to Ramp", "is Hebbia a good fit"
  interview_prep → "prep me for my Hebbia interview", "what should I know about Scale AI"
  research       → "tell me about Anthropic", "research Cohere for me"
  cs_triage      → "triage this ticket: ...", "classify this support message"
  restaurant     → "book me dinner in Soho", "find a table for 2 tonight"
  job_search     → "show my pipeline", "how many applications", "my job stats"
  general        → everything else — Claude answers directly

SSE event format:
  data: {"type": "route", "agent": "advisor", "reason": "..."}
  data: {"type": "token", "text": "..."}
  data: {"type": "section", "label": "FIT SCORE", "value": "82"}
  data: {"type": "done"}
  data: {"type": "error", "message": "..."}
"""

import json
import os
import time
import anthropic

AYLIN_PROFILE = """
Aylin Uyar — Tuck MBA 2026 (Dartmouth), BS Electrical Engineering.
Ex-Deloitte Tech Strategy Senior Consultant (4 years).
PM intern at Skild AI ($14B, NVIDIA/Sequoia-backed) — owned GTM for humanoid robotics AI.
Targeting: AI Strategist, Chief of Staff, Strategy & Ops, GTM Strategy at AI-native companies.
Locations: NYC (primary), London (needs UK visa), open to SF.
"""

ROUTER_PROMPT = """You are the AylinOS query router. Classify the user's query into one agent.

AGENTS:
- advisor: questions about whether to apply to a company, company fit, job strategy, "should I apply to X", "is X a good fit", "where should I network"
- interview_prep: preparing for a specific interview, "prep me for X interview", "what to know before interviewing at X", "STAR stories for X"
- research: general company research without a specific job angle, "tell me about X", "research X", "what does X do"
- cs_triage: classifying or triaging a support ticket or customer complaint
- restaurant: booking or finding a restaurant, food, dinner reservations
- job_search: questions about Aylin's own job pipeline, application stats, "how many applications", "show my pipeline"
- gtm_tool: GTM strategy, pricing models, revenue forecasting, ARR, NRR, LTV, CAC, go-to-market
- email_agent: AI email pipeline, job search emails, daily digest, ATS scraping, email automation
- compliance_rag: compliance questions, financial regulations, policy documents, RAG chatbot
- general: anything else — answer directly

USER QUERY: {query}

Respond with ONLY valid JSON, no markdown:
{{"agent": "advisor", "reason": "one short phrase", "extract": "the key entity or topic"}}

extract = the company name for advisor/interview_prep/research, the ticket text for cs_triage, location/details for restaurant, empty string for others."""


def classify_query(query: str, client: anthropic.Anthropic) -> dict:
    """Use Claude Haiku to classify intent. Fast + cheap."""
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=120,
        messages=[{"role": "user", "content": ROUTER_PROMPT.format(query=query)}]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


# ── Per-agent streaming handlers ───────────────────────────────────────────────

def stream_advisor(query: str, company: str, client: anthropic.Anthropic):
    """Stream career intelligence brief for a company."""
    from integrations.tavily import research_company as tavily_research, find_hiring_manager
    try:
        live_intel = tavily_research(company)
    except Exception:
        live_intel = ""
    try:
        contact_intel = find_hiring_manager(company, "VP Product GTM Strategy Operations Chief of Staff")
    except Exception:
        contact_intel = ""

    prompt = f"""You are AylinOS Career Intelligence. Generate a brief intelligence report.

{AYLIN_PROFILE}

COMPANY: {company}
LIVE INTEL: {live_intel[:1000] if live_intel else "Use your knowledge."}
CONTACT RESEARCH: {contact_intel[:600] if contact_intel else "Use your knowledge of typical leadership at this company."}
USER QUERY: {query}

Be extremely concise. Each section is 1-2 lines max — digestible, scannable. No paragraphs.

FIT SCORE:
[number 0-100 only]

STRATEGY:
[APPLY NOW / NETWORK FIRST / RESEARCH MORE / SKIP — one short phrase why, max 15 words]

AI ANGLE:
[One sentence on what they're doing with AI. Nothing more.]

ROLE FIT:
[One sentence connecting Aylin's Deloitte/Skild background to this specific company.]

OUTREACH:
[One specific named person (Title) — one-line angle for the first message.]

VERDICT:
[One punchy sentence. Bottom line only.]"""

    full_text = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            full_text += text
            yield _sse({"type": "token", "text": text})

    # Parse and save structured contact + fit data for job dashboard
    try:
        import re, db as _db
        score_m = re.search(r'FIT SCORE:\s*(\d+)', full_text)
        strat_m = re.search(r'STRATEGY:\s*(.+)', full_text)
        out_m   = re.search(r'OUTREACH:\s*(.+?)(?:\n|$)', full_text)
        fit_score = int(score_m.group(1)) if score_m else None
        strategy  = strat_m.group(1).strip() if strat_m else ""
        outreach  = out_m.group(1).strip() if out_m else ""
        contact_m = re.match(r'^([^(]+)\(([^)]+)\)\s*[—\-]\s*(.+)$', outreach)
        if contact_m:
            c_name, c_title, c_angle = [x.strip() for x in contact_m.groups()]
        else:
            c_name, c_title, c_angle = "", "", outreach
        _db.save_advisor_result(company, fit_score, strategy, c_name, c_title, c_angle)
    except Exception:
        pass

    yield _sse({"type": "done"})


def stream_interview_prep(query: str, company: str, client: anthropic.Anthropic):
    """Stream interview prep for a specific company."""
    prompt = f"""You are AylinOS Interview Prep. Generate focused interview preparation.

{AYLIN_PROFILE}

COMPANY: {company}
USER QUERY: {query}

Be concise — 1-2 lines per section, scannable, no paragraphs.

COMPANY BRIEF:
[One sentence: what they do and why it matters for this interview]

TOP STAR STORY:
[Which story to lead with + one-line framing for this company]

LIKELY Q1:
[Question — what they're testing, in 8 words or less]

LIKELY Q2:
[Question — what they're testing, in 8 words or less]

QUESTIONS TO ASK:
[Two sharp questions, one line each]"""

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})

    yield _sse({"type": "done"})


def stream_research(query: str, company: str, client: anthropic.Anthropic):
    """Stream company research brief."""
    from integrations.tavily import research_company as tavily_research
    try:
        live_intel = tavily_research(company)
    except Exception:
        live_intel = ""

    prompt = f"""You are AylinOS Research. Generate a concise company intelligence brief.

COMPANY: {company}
LIVE INTEL: {live_intel[:1200] if live_intel else "Use your knowledge."}

Be concise — 1 line per section, scannable.

WHAT THEY DO:
[One sentence: product, customer, business model]

STAGE & FUNDING:
[Series, lead investors, valuation — one line]

AI ANGLE:
[One sentence: what they're specifically doing with AI]

KEY CONTACT:
[Name (Title) — one line]

HIRING SIGNAL:
[One role they're hiring for + what it signals]"""

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})

    yield _sse({"type": "done"})


def stream_cs_triage(query: str, ticket_text: str, client: anthropic.Anthropic):
    """Stream CS ticket classification."""
    text = ticket_text or query
    prompt = f"""You are AylinOS CS Triage. Classify this support ticket instantly.

TICKET: {text}

Respond with these sections:

CATEGORY:
[Billing / Technical / Account / General]

PRIORITY:
[High / Medium / Low — with one-line reason]

SUMMARY:
[One sentence describing the issue]

RECOMMENDED ACTION:
[Exactly what the support agent should do next]

ESCALATE:
[Yes/No — and why if yes]"""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})

    yield _sse({"type": "done"})


FORK_YEAH_URL = os.environ.get("FORK_YEAH_URL", "http://localhost:5173")

# Live app URLs for portfolio projects
GTM_TOOL_URL = "https://web-production-b4e0ad.up.railway.app"
EMAIL_AGENT_URL = "https://muse-agent-transfer.lovable.app"
COMPLIANCE_RAG_URL = "https://compliance-rag-demo-mrwtbs4k7gvdvmiuck8mdn.streamlit.app"

# Map each agent to its next-step apps
AGENT_NEXT_STEPS = {
    "advisor":       [{"label": "Job Search Dashboard", "url": "https://aylinos.onrender.com/job-search"}, {"label": "Networking Operator", "url": "https://aylinos.onrender.com/networking"}],
    "interview_prep":[{"label": "Job Search Dashboard", "url": "https://aylinos.onrender.com/job-search"}],
    "research":      [{"label": "Compliance RAG Chatbot", "url": COMPLIANCE_RAG_URL}, {"label": "Job Search Dashboard", "url": "https://aylinos.onrender.com/job-search"}],
    "cs_triage":     [{"label": "CS Triage Agent", "url": "https://github.com/aylineuyar-arch/ai-cs-triage"}],
    "restaurant":    [{"label": "Fork Yeah! Live Booking", "url": "https://github.com/aylineuyar-arch/restaurant-agent"}],
    "job_search":    [{"label": "Job Search Dashboard", "url": "https://aylinos.onrender.com/job-search"}, {"label": "Agentic Email Generator", "url": EMAIL_AGENT_URL}],
    "gtm_tool":      [{"label": "GTM Pricing Tool", "url": GTM_TOOL_URL}],
    "email_agent":   [{"label": "Agentic Email Generator", "url": EMAIL_AGENT_URL}],
    "compliance_rag":[{"label": "Compliance RAG Chatbot", "url": COMPLIANCE_RAG_URL}],
    "general":       [],
}

def stream_restaurant(query: str, client: anthropic.Anthropic):
    """
    Stream restaurant results. Tries to proxy through Fork Yeah! LangGraph agent
    (localhost:5173) first. Falls back to Claude-only response if not running.
    """
    import urllib.request
    import urllib.parse

    # Try Fork Yeah! agent first
    try:
        encoded = urllib.parse.quote(query)
        url = f"{FORK_YEAH_URL}/find-restaurant-stream?q={encoded}"
        req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            # Agent is running — proxy its SSE stream through
            yield _sse({"type": "token", "text": "🍴 Fork Yeah! agent connected — searching...\n\n"})
            buffer = b""
            while True:
                chunk = resp.read(256)
                if not chunk:
                    break
                buffer += chunk
                while b"\n\n" in buffer:
                    event, buffer = buffer.split(b"\n\n", 1)
                    for line in event.decode().splitlines():
                        if line.startswith("data: "):
                            raw = line[6:].strip()
                            if raw in ("[DONE]", ""):
                                continue
                            try:
                                node_data = json.loads(raw)
                                node = node_data.get("node", "")
                                text = node_data.get("text", "")
                                if node:
                                    yield _sse({"type": "token", "text": f"\n{node.upper().replace('_',' ')}:\n"})
                                if text:
                                    yield _sse({"type": "token", "text": text})
                            except Exception:
                                if raw:
                                    yield _sse({"type": "token", "text": raw})
            yield _sse({"type": "done"})
            return
    except Exception:
        pass  # Fork Yeah! not running — fall through to Claude

    # Fallback: Claude-only response
    prompt = f"""You are AylinOS Fork Yeah! restaurant assistant.

USER REQUEST: {query}

Parse the request and respond with these sections:

SEARCHING:
[Confirm what you're searching for: cuisine, location, party size, time]

TOP PICK:
[Restaurant name, neighborhood, cuisine type, price range, why it fits]

BACKUP:
[Second option with brief reason]

BOOKING:
[How to book — OpenTable link or call ahead note]

PRO TIP:
[One insider tip about the top pick or area]

Note at the end: "For live booking with Playwright + ChromaDB memory, start the Fork Yeah! agent."
"""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})

    yield _sse({"type": "done"})


def stream_job_search(query: str, client: anthropic.Anthropic):
    """Stream job pipeline stats from DB."""
    try:
        import db
        metrics = db.get_metrics()
        context = f"""
Total applications: {metrics['total_jobs']}
Response rate: {metrics['response_rate']}%
Interview rate: {metrics['interview_rate']}%
Active interviews: {metrics['interviewing']}
Offers: {metrics['offers']}
Rejected: {metrics['rejected_interview']} at interview stage
No reply: {metrics['no_reply']}
"""
    except Exception:
        context = "Pipeline data unavailable."

    prompt = f"""You are AylinOS Job Search. Answer questions about Aylin's job search pipeline.

PIPELINE DATA:
{context}

USER QUERY: {query}

{AYLIN_PROFILE}

Respond conversationally but structured. Lead with the key number they asked about,
then give 2-3 sentences of insight or recommendation. Use sections if helpful."""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})

    yield _sse({"type": "done"})


def stream_gtm_tool(query: str, client: anthropic.Anthropic):
    """Stream GTM / pricing intelligence, with link to live tool."""
    prompt = f"""You are AylinOS GTM Intelligence, connected to a live GTM Pricing Tool.

USER QUERY: {query}

Respond with these sections:

ROUTING TO:
[GTM Pricing Tool — {GTM_TOOL_URL}]

QUICK ANSWER:
[2-3 sentences directly answering the question using GTM/pricing expertise]

KEY METRICS TO MODEL:
[3-4 bullet points of the most relevant metrics for this question: ARR, NRR, LTV:CAC, payback period, etc.]

TRY IT LIVE:
[Direct the user to open {GTM_TOOL_URL} to model this scenario interactively with real inputs and revenue forecasts]"""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})
    yield _sse({"type": "done"})


def stream_email_agent(query: str, client: anthropic.Anthropic):
    """Stream email agent intelligence, with link to live agent."""
    prompt = f"""You are AylinOS Email Intelligence, connected to a live Agentic Email Generator.

USER QUERY: {query}

Respond with these sections:

ROUTING TO:
[Agentic Email Generator — {EMAIL_AGENT_URL}]

WHAT THE AGENT DOES:
[2-3 sentences: scrapes 130+ ATS feeds daily, scores fit + conversion likelihood with Claude, emails a ranked digest at 8am ET]

FOR YOUR QUERY:
[Direct answer to what they asked about AI email pipelines or job search automation]

TRY IT LIVE:
[Direct the user to {EMAIL_AGENT_URL} to see the live agent in action]"""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})
    yield _sse({"type": "done"})


def stream_compliance_rag(query: str, client: anthropic.Anthropic):
    """Stream compliance RAG response, with link to live chatbot."""
    prompt = f"""You are AylinOS Compliance Intelligence, connected to a live Compliance RAG Chatbot.

USER QUERY: {query}

Respond with these sections:

ROUTING TO:
[Compliance RAG Chatbot — {COMPLIANCE_RAG_URL}]

QUICK ANSWER:
[2-3 sentences on the compliance/regulatory topic, drawing on financial services knowledge]

HOW THE RAG WORKS:
[One sentence: policy documents ingested into vector store, Claude answers grounded in source docs with citations]

TRY IT LIVE:
[Direct the user to {COMPLIANCE_RAG_URL} for full policy Q&A with source citations]"""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})
    yield _sse({"type": "done"})


def stream_general(query: str, client: anthropic.Anthropic):
    """General Claude response for anything that doesn't fit another agent."""
    prompt = f"""You are AylinOS, a personal AI operating system built by Aylin Uyar.

{AYLIN_PROFILE}

Answer the user's question helpfully and concisely. If it relates to Aylin's job search,
career, or the AI tools she's built, use that context.

USER: {query}"""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})

    yield _sse({"type": "done"})


# ── Main entry point ───────────────────────────────────────────────────────────

def stream_query(query: str):
    """
    Generator that yields SSE strings.
    1. Classifies query with Haiku (fast)
    2. Yields route event so frontend can update UI immediately
    3. Streams the right agent's response
    """
    client = anthropic.Anthropic()

    try:
        route = classify_query(query, client)
    except Exception as e:
        yield _sse({"type": "error", "message": f"Routing failed: {e}"})
        return

    agent = route.get("agent", "general")
    reason = route.get("reason", "")
    extract = route.get("extract", "")

    # Tell the frontend which agent activated and why
    yield _sse({"type": "route", "agent": agent, "reason": reason, "extract": extract})

    try:
        if agent == "advisor":
            company = extract or query
            yield from stream_advisor(query, company, client)
        elif agent == "interview_prep":
            company = extract or query
            yield from stream_interview_prep(query, company, client)
        elif agent == "research":
            company = extract or query
            yield from stream_research(query, company, client)
        elif agent == "cs_triage":
            yield from stream_cs_triage(query, extract, client)
        elif agent == "restaurant":
            yield from stream_restaurant(query, client)
        elif agent == "job_search":
            yield from stream_job_search(query, client)
        elif agent == "gtm_tool":
            yield from stream_gtm_tool(query, client)
        elif agent == "email_agent":
            yield from stream_email_agent(query, client)
        elif agent == "compliance_rag":
            yield from stream_compliance_rag(query, client)
        else:
            yield from stream_general(query, client)

        # Emit next steps so the frontend can render clickable app cards
        steps = AGENT_NEXT_STEPS.get(agent, [])
        if steps:
            yield _sse({"type": "next_steps", "steps": steps})

    except Exception as e:
        yield _sse({"type": "error", "message": str(e)})
