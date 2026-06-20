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
    from integrations.tavily import research_company as tavily_research
    try:
        live_intel = tavily_research(company)
    except Exception:
        live_intel = ""

    prompt = f"""You are AylinOS Career Intelligence. Generate a brief intelligence report.

{AYLIN_PROFILE}

COMPANY: {company}
LIVE INTEL: {live_intel[:1200] if live_intel else "Use your knowledge."}
USER QUERY: {query}

Write a structured intelligence brief with these exact sections, in order.
For each section write the label on its own line in ALL CAPS followed by a colon, then the content.

FIT SCORE:
[just the number 0-100, nothing else]

STRATEGY:
[one of: APPLY NOW / NETWORK FIRST / RESEARCH MORE / SKIP — then one sentence why]

AI ANGLE:
[2-3 sentences on what this company is actually doing with AI in production]

ROLE FIT:
[2-3 sentences on why Aylin specifically fits — reference her Deloitte/Skild AI background]

OUTREACH:
[who to contact and exactly what angle to use in the first message]

VERDICT:
[one bold bottom-line sentence]"""

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield _sse({"type": "token", "text": text})

    yield _sse({"type": "done"})


def stream_interview_prep(query: str, company: str, client: anthropic.Anthropic):
    """Stream interview prep for a specific company."""
    prompt = f"""You are AylinOS Interview Prep. Generate focused interview preparation.

{AYLIN_PROFILE}

COMPANY: {company}
USER QUERY: {query}

Write structured prep with these exact sections:

COMPANY BRIEF:
[3-4 sentences: what they do, stage, why it matters for this interview]

TOP STAR STORY:
[Which of Aylin's stories to lead with and exactly how to frame it for this company. Be specific.]

LIKELY Q1:
[Most likely behavioral question + one line on what they're testing]

LIKELY Q2:
[Second most likely question + what they're testing]

QUESTIONS TO ASK:
[2 sharp questions Aylin should ask that show she's done her homework]"""

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

Write with these sections:

WHAT THEY DO:
[2-3 sentences: business model, product, customer]

STAGE & FUNDING:
[Series, investors, valuation if known]

AI ANGLE:
[What they're actually doing with AI — specific, not generic]

LEADERSHIP:
[CEO + 1-2 key execs relevant to AI/strategy]

HIRING SIGNALS:
[What roles they're hiring for, what it signals about priorities]"""

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


FORK_YEAH_URL = "http://localhost:5173"

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
        else:
            yield from stream_general(query, client)

    except Exception as e:
        yield _sse({"type": "error", "message": str(e)})
