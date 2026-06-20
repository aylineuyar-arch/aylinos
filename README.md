# AylinOS

An AI operating system for end-to-end job search management.

Multi-agent pipeline covering discovery → research → scoring → interview prep → outcome tracking, with persistent memory and human-in-the-loop approval gates.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        AylinOS                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Discovery Agent          Research Agent                │
│  ├── JSearch API          ├── Company brief             │
│  ├── Greenhouse API       ├── Investors / leadership    │
│  ├── Lever API            └── Sponsorship status        │
│  └── Claude scoring                                     │
│          │                        │                     │
│          └──────────┬─────────────┘                     │
│                     ▼                                   │
│              SQLite (aylinos.db)                        │
│              ├── jobs                                   │
│              ├── applications  ← status tracking        │
│              ├── outcomes      ← conversion metrics     │
│              ├── interview_prep                         │
│              └── company_research                       │
│                     │                                   │
│                     ▼                                   │
│           Interview Prep Agent                          │
│           ├── Company brief (Claude Opus)               │
│           ├── STAR stories tailored to role             │
│           └── Likely interview questions                │
│                     │                                   │
│                     ▼                                   │
│              FastAPI Server                             │
│              └── Dashboard (live pipeline view)         │
└─────────────────────────────────────────────────────────┘
```

**Human-in-the-loop:** Discovery only runs on explicit user trigger. Status updates (applied / interviewing / offer / rejected) are always user-initiated. The system never auto-applies.

---

## AI Deployment Concepts Demonstrated

| Concept | Where |
|---|---|
| Agent orchestration | `agents/` — discovery, research, interview prep run as independent agents |
| Persistent memory | `db/schema.py` — SQLite stores all jobs, status history, outcomes |
| Tool calling | Discovery agent calls JSearch API, Greenhouse, Lever, Ashby |
| Human-in-the-loop | `/api/jobs/refresh` requires `confirmed=true`; status changes are user-triggered |
| Evaluations / metrics | `/api/metrics` — interview rate, offer rate, conversion by fit score band |
| Multi-model routing | Haiku for scoring (speed/cost), Opus for interview prep (quality) |

---

## Stack

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude (Haiku for scoring, Opus for prep) |
| Backend | FastAPI + Python |
| Database | SQLite (local) |
| Job Sources | JSearch API, Greenhouse, Lever, Ashby |
| Deployment | Railway |

---

## Setup

```bash
# From the root of this repo:
cd aylinos

pip install -r requirements.txt

cp .env.example .env
# Add ANTHROPIC_API_KEY and RAPIDAPI_KEY

python -m api.server
# → http://localhost:8000
```

---

## Reference Projects

Sibling workflows in this repo that AylinOS builds on:
- [`../jobs.py`](../jobs.py) — job fetching and Claude scoring logic
- [`../restaurant-agent/`](../restaurant-agent/) — LangGraph-style multi-node agent, ChromaDB memory, monitoring

---

## Modules

| File | Purpose |
|---|---|
| `agents/discovery.py` | Fetches and scores jobs from JSearch + ATS sources |
| `agents/research.py` | Generates structured company research brief |
| `agents/interview_prep.py` | Generates company brief, STAR stories, likely questions |
| `db/schema.py` | SQLite schema, upsert/query helpers, metrics |
| `api/server.py` | FastAPI server — all endpoints |
| `api/dashboard_html.py` | Live dashboard renderer with status tracking |
