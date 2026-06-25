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

ROUTER_PROMPT = """You are the AylinOS query router. Select ALL relevant agents for this query (1-3 max).

AGENTS:
- advisor: "should I apply to X", "is X a good fit", career fit, job strategy
- interview_prep: "prep me for X interview", "STAR stories for X", interview coaching
- job_search: Aylin's pipeline stats, "how many applications", "show my pipeline"
- research: general company research, "tell me about X", "what does X do"
- gtm_tool: GTM strategy, pricing models, ARR, NRR, LTV, CAC, go-to-market, revenue forecasting
- email_agent: AI email pipeline, job search emails, ATS scraping, email automation
- cs_triage: support ticket classification, customer complaint triage
- restaurant: booking or finding restaurants, food, dinner reservations
- compliance_rag: compliance questions, financial regulations, policy documents
- general: anything else

ROUTING RULES:
- Career query (applying to a specific company): advisor + interview_prep are often both relevant
- Job pipeline query: job_search only
- GTM/pricing query: gtm_tool only — do NOT add research or advisor
- Compliance query: compliance_rag only
- Pricing and job search are UNRELATED — never combine them
- interview_prep is career-only, never with gtm_tool or compliance_rag
- Pick only agents that genuinely add value — minimum 1, maximum 2

USER QUERY: {query}

Respond with ONLY valid JSON, no markdown:
{{"agents": ["advisor", "interview_prep"], "reason": "career fit + interview coaching", "extract": "Decagon"}}

extract = company name for career queries, topic for GTM queries, empty string for pipeline queries."""


# Map agent internal name → display label for frontend
INTERNAL_TO_FRONTEND = {
    "advisor":        "Career Advisor",
    "interview_prep": "Interview Prep",
    "job_search":     "Job Search",
    "research":       "Research",
    "gtm_tool":       "GTM Modeler",
    "email_agent":    "Email Agent",
    "cs_triage":      "CS Triage",
    "restaurant":     "Fork Yeah!",
    "compliance_rag": "Policy Desk",
    "general":        "AylinOS",
}

# Cluster grouping — controls colors and next-step cards scoping
AGENT_CLUSTER = {
    "advisor":        "career",
    "interview_prep": "career",
    "job_search":     "career",
    "email_agent":    "career",
    "gtm_tool":       "gtm",
    "research":       "gtm",
    "cs_triage":      "support",
    "restaurant":     "support",
    "compliance_rag": "compliance",
    "general":        "general",
}

CLUSTER_COLOR = {
    "career":     "#818cf8",   # indigo
    "gtm":        "#34d399",   # emerald
    "support":    "#4ade80",   # green
    "compliance": "#fb923c",   # orange
    "general":    "#94a3b8",   # slate
}


def classify_query(query: str, client: anthropic.Anthropic) -> dict:
    """Use Claude Haiku to pick ALL relevant agents. Fast + cheap."""
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": ROUTER_PROMPT.format(query=query)}]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw.strip())
    # Backward compat: if Haiku returns single "agent", wrap it
    if "agent" in result and "agents" not in result:
        result["agents"] = [result["agent"]]
    if "agents" not in result:
        result["agents"] = ["general"]
    return result


def _build_pipeline_steps(agents: list, extract: str, query: str) -> list:
    """Generate tailored pipeline steps based on the agents selected."""
    entity = extract or "target"
    primary = agents[0] if agents else "general"

    if primary in ("advisor", "interview_prep"):
        steps = [
            f"Pulling live intel on {entity}",
            "Scoring fit against Aylin's profile",
            "Generating career strategy brief",
        ]
        if "interview_prep" in agents:
            steps.append("Building STAR stories + likely questions")
    elif primary == "job_search":
        steps = [
            "Querying job pipeline DB",
            "Computing conversion metrics",
            "Generating funnel summary",
        ]
    elif primary in ("gtm_tool", "research"):
        steps = [
            f"Researching {entity or 'market'}",
            "Modeling pricing / GTM levers",
            "Benchmarking against comparables",
        ]
        if "research" in agents:
            steps.append("Pulling live company intel")
    elif primary == "email_agent":
        steps = [
            "Scanning ATS for new postings",
            "Drafting personalized outreach",
            "Queuing for review",
        ]
    elif primary == "compliance_rag":
        steps = [
            f"Searching policy corpus for {entity or 'query'}",
            "Retrieving relevant clauses",
            "Synthesizing compliance brief",
        ]
    else:
        steps = [
            "Classifying intent",
            "Routing to best agent",
            "Generating response",
        ]
    return steps


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
Output each section header EXACTLY ONCE in this order: FIT SCORE, STRATEGY, AI ANGLE, ROLE FIT, OUTREACH, VERDICT. Never repeat a section.

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

    # Emit fit_score event so stream_query can trigger agentic chaining
    if fit_score is not None:
        yield _sse({"type": "fit_score", "score": fit_score})

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

# Cluster-scoped next-step cards — no cross-contamination between career/GTM/etc.
CLUSTER_NEXT_STEPS = {
    "career": [
        {"label": "Networking",   "url": "https://aylinos.onrender.com/networking"},
        {"label": "Email Agent",  "url": EMAIL_AGENT_URL},
        {"label": "Interview Prep", "url": "https://aylinos.onrender.com"},
    ],
    "gtm": [
        {"label": "GTM Modeler",  "url": GTM_TOOL_URL},
        {"label": "Research",     "url": "https://aylinos.onrender.com"},
    ],
    "support": [
        {"label": "CS Triage",    "url": "https://github.com/aylineuyar-arch/ai-cs-triage"},
        {"label": "Fork Yeah!",   "url": "https://github.com/aylineuyar-arch/restaurant-agent"},
    ],
    "compliance": [
        {"label": "Policy Desk",  "url": COMPLIANCE_RAG_URL},
    ],
    "general": [],
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
    prompt = f"""You are AylinOS GTM Intelligence, a pricing and go-to-market expert.

USER QUERY: {query}

Respond with these sections ONLY — no extras, no preamble:

QUICK ANSWER:
[2-3 sentences directly answering the question using GTM/pricing expertise]

KEY METRICS TO MODEL:
[3-4 bullet points of the most relevant metrics: ARR, NRR, LTV:CAC, payback period, etc.]

HIGHLIGHT:
[The single most important insight or risk for this pricing decision]"""

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
    prompt = f"""You are AylinOS Email Intelligence, an AI job search automation expert.

USER QUERY: {query}

Respond with these sections ONLY — no extras, no preamble:

WHAT THE AGENT DOES:
[2-3 sentences: scrapes 130+ ATS feeds daily, scores fit + conversion likelihood with Claude, emails a ranked digest at 8am ET]

FOR YOUR QUERY:
[Direct answer to what they asked about AI email pipelines or job search automation]"""

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
    prompt = f"""You are AylinOS Compliance Intelligence, a financial regulations and policy expert.

USER QUERY: {query}

Respond with these sections ONLY — no extras, no preamble:

QUICK ANSWER:
[2-3 sentences on the compliance/regulatory topic, drawing on financial services knowledge]

HOW THE RAG WORKS:
[One sentence: policy documents ingested into vector store, Claude answers grounded in source docs with citations]"""

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


# ── Per-agent dispatcher ───────────────────────────────────────────────────────

def _dispatch(agent: str, query: str, extract: str, client: anthropic.Anthropic):
    """Dispatch to the correct streaming handler for a single agent."""
    if agent == "advisor":
        yield from stream_advisor(query, extract or query, client)
    elif agent == "interview_prep":
        yield from stream_interview_prep(query, extract or query, client)
    elif agent == "research":
        yield from stream_research(query, extract or query, client)
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


# ── Main entry point ───────────────────────────────────────────────────────────

def stream_query(query: str):
    """
    Generator that yields SSE strings.
    1. Haiku classifies query and selects ALL relevant agents (1-3)
    2. Yields route event so frontend can update UI immediately
    3. Fans out to each agent, with section dividers between outputs
    4. Emits pipeline_steps (tailored checklist) + next_steps cards
    """
    client = anthropic.Anthropic()
    t_start = time.time()
    agents_selected = ["general"]
    cluster = "general"
    reason = ""
    extract = ""

    try:
        route = classify_query(query, client)
    except Exception as e:
        yield _sse({"type": "error", "message": f"Routing failed: {e}"})
        return

    agents_selected = route.get("agents", ["general"])
    reason = route.get("reason", "")
    extract = route.get("extract", "")

    # Determine cluster from primary agent
    primary = agents_selected[0] if agents_selected else "general"
    cluster = AGENT_CLUSTER.get(primary, "general")
    color = CLUSTER_COLOR.get(cluster, "#94a3b8")
    pipeline_steps = _build_pipeline_steps(agents_selected, extract, query)

    # Tell the frontend the full routing decision
    yield _sse({
        "type": "route",
        "agent": primary,
        "agents": agents_selected,
        "reason": reason,
        "extract": extract,
        "cluster": cluster,
    })

    try:
        auto_chained = False
        for i, agent in enumerate(agents_selected):
            label = INTERNAL_TO_FRONTEND.get(agent, agent.replace("_", " ").title())
            # Divider between agents (not before the first)
            if i > 0:
                yield _sse({"type": "section", "label": label, "color": color})

            if agent == "advisor":
                # Intercept advisor stream to capture fit_score for agentic chaining
                fit_score_captured = None
                for sse_str in _dispatch(agent, query, extract, client):
                    if '"type": "fit_score"' in sse_str:
                        try:
                            data = json.loads(sse_str[6:].strip())
                            fit_score_captured = data.get("score")
                        except Exception:
                            pass
                    yield sse_str
                # Auto-trigger interview_prep if score >= 75 and not already queued
                if (
                    fit_score_captured is not None
                    and fit_score_captured >= 75
                    and "interview_prep" not in agents_selected
                    and not auto_chained
                ):
                    auto_chained = True
                    yield _sse({
                        "type": "section",
                        "label": f"AUTO-TRIGGERED → Interview Prep  (fit {fit_score_captured}/100)",
                        "color": color,
                        "auto": True,
                    })
                    yield from _dispatch("interview_prep", query, extract, client)
            else:
                yield from _dispatch(agent, query, extract, client)

        # Emit pipeline steps + next-step cards for the cluster
        next_step_items = CLUSTER_NEXT_STEPS.get(cluster, [])
        yield _sse({
            "type": "next_steps",
            "pipeline_steps": pipeline_steps,
            "steps": pipeline_steps,        # alias: aylinos-app bundle reads t.steps
            "items": next_step_items,
            "color": color,
        })

    except Exception as e:
        yield _sse({"type": "error", "message": str(e)})
    finally:
        # Minimal observability — never breaks the stream
        try:
            latency_ms = int((time.time() - t_start) * 1000)
            import db
            db.save_trace(query, agents_selected, cluster, reason, extract, latency_ms)
        except Exception:
            pass
