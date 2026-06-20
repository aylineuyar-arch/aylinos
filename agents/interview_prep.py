"""
AylinOS — Interview Prep Agent
--------------------------------
Given a job_id, generates:
  1. Company brief (business model, investors, leadership, recent news)
  2. STAR stories tailored to the role
  3. Likely interview questions

Architecture pattern from: ../claudecode/restaurant-agent/nodes.py
Uses multi-step Claude calls with structured JSON output.
"""

import json
import anthropic
from db import get_all_jobs, get_interview_prep, save_interview_prep

# Drive sync is optional — works without credentials, just skips upload
try:
    from integrations.drive import save_prep_package as _drive_save_prep
    DRIVE_ENABLED = True
except Exception:
    DRIVE_ENABLED = False

try:
    from integrations.elevenlabs import generate_star_audio
    ELEVENLABS_ENABLED = True
except Exception:
    ELEVENLABS_ENABLED = False

PROFILE = """
Aylin Uyar — Tuck MBA 2026 (Dartmouth)
Background: Deloitte Tech Strategy Senior Consultant (4 years), PM intern at Skild AI
            ($14B valuation, NVIDIA/Sequoia-backed), BS Electrical Engineering.
Core strengths: GTM strategy, cross-functional ops, AI/ML product deployment,
                OKRs, enterprise programs, stakeholder management.

STAR Story Bank (raw material — adapt these to each role):
1. Skild AI: Designed go-to-market motion for humanoid robotics AI platform.
   Mapped enterprise customer segments, defined pricing tiers, built sales playbook.
   Outcome: Prioritized 3 verticals, reduced sales cycle estimation by 40%.

2. Deloitte — AI Transformation: Led AI readiness assessment for Fortune 500 client.
   Conducted 40+ stakeholder interviews, identified 12 automation opportunities,
   built business case for $8M AI investment.
   Outcome: Client approved full program; implementation started Q1.

3. Deloitte — Digital Program: Managed $20M digital transformation program.
   Coordinated 6 workstreams across engineering, legal, and ops.
   Outcome: Delivered on time despite 3-month scope expansion.

4. Deloitte — Change Management: Designed adoption strategy for new ERP system.
   Built training program for 2,000 employees across 8 countries.
   Outcome: 94% adoption rate in 6 months vs 60% industry benchmark.

5. AylinOS: Built AI operating system for job search (this project).
   Designed multi-agent pipeline: discovery → research → scoring → prep.
   Implemented RAG, persistent memory, human-in-the-loop approval gates.
   Outcome: Reduced application prep time by ~70%, tracking conversion metrics.
"""


def _generate_company_brief(job: dict, client: anthropic.Anthropic) -> str:
    prompt = f"""You are a research analyst preparing an interview brief.

ROLE: {job['title']} at {job['company']} ({job.get('company_type', '')})
LOCATION: {job.get('location', '')}
JOB URL: {job.get('url', '')}

Generate a concise company brief for interview preparation. Include:
1. What the company does (2-3 sentences, business model)
2. Stage / funding / investors (if known)
3. Key leadership names (CEO, relevant exec for this role)
4. Recent news or priorities (product launches, funding rounds, expansions)
5. Why someone like this candidate would be excited about this company
6. Likely company pain points this role solves

Be specific and factual. If you don't know something, say so rather than guessing.
Use what you know about {job['company']} up to your knowledge cutoff.

Format as clean prose paragraphs, not bullet points."""

    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()


def _generate_star_stories(job: dict, client: anthropic.Anthropic) -> str:
    prompt = f"""You are an interview coach preparing STAR stories.

ROLE: {job['title']} at {job['company']} ({job.get('company_type', '')})
JOB DESCRIPTION EXCERPT: {str(job.get('description', ''))[:400] or 'Not available'}

CANDIDATE PROFILE AND STORY BANK:
{PROFILE}

Select and adapt the 3 most relevant STAR stories from the candidate's story bank
for this specific role. For each story:
- Make it concrete and specific (numbers, outcomes, timeframes)
- Tailor the framing to what this company/role cares about
- Keep each story to ~150 words

Format as:
STORY 1 — [Theme]
Situation: ...
Task: ...
Action: ...
Result: ...

STORY 2 — [Theme]
...

STORY 3 — [Theme]
..."""

    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()


def _generate_questions(job: dict, client: anthropic.Anthropic) -> str:
    prompt = f"""You are an interview coach for a senior operator role.

ROLE: {job['title']} at {job['company']} ({job.get('company_type', '')})
COMPANY TYPE: {job.get('company_type', '')}

Generate 10 likely interview questions for this role, split into:

BEHAVIORAL (5 questions) — competency-based questions this company type typically asks
CASE/JUDGMENT (3 questions) — situational or strategic thinking questions
TECHNICAL/DOMAIN (2 questions) — AI deployment, strategy, or ops knowledge questions

For each question, add a one-line note on what the interviewer is actually testing.

Format:
BEHAVIORAL
1. [Question] → Testing: [what they want to see]
...

CASE / JUDGMENT
6. [Question] → Testing: [what they want to see]
...

TECHNICAL / DOMAIN
9. [Question] → Testing: [what they want to see]
..."""

    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()


def run(job_id: str, force_refresh: bool = False) -> dict:
    """
    Generate interview prep for a job_id.
    Returns dict with company_brief, star_stories, likely_questions.
    Caches to DB — won't regenerate unless force_refresh=True.
    """
    # Check cache first
    if not force_refresh:
        cached = get_interview_prep(job_id)
        if cached:
            print(f"[Interview Prep] Using cached prep for {job_id}")
            return cached

    # Get job from DB
    jobs = get_all_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        raise ValueError(f"Job {job_id} not found in database")

    client = anthropic.Anthropic()

    print(f"[Interview Prep] Generating company brief for {job['company']}...")
    brief = _generate_company_brief(job, client)

    print(f"[Interview Prep] Tailoring STAR stories...")
    stars = _generate_star_stories(job, client)

    print(f"[Interview Prep] Generating likely questions...")
    questions = _generate_questions(job, client)

    save_interview_prep(job_id, brief, stars, questions)
    print(f"[Interview Prep] Saved to database.")

    # Auto-sync to Google Drive if credentials exist
    if DRIVE_ENABLED:
        _drive_save_prep(
            company=job["company"],
            role=job["title"],
            brief=brief,
            stars=stars,
            questions=questions,
        )

    # Generate audio practice file via ElevenLabs
    audio_path = ""
    if ELEVENLABS_ENABLED:
        audio_path = generate_star_audio(job_id, stars)

    return {
        "job_id": job_id,
        "company_brief": brief,
        "star_stories": stars,
        "likely_questions": questions,
        "audio_path": audio_path,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m agents.interview_prep <job_id>")
        sys.exit(1)
    result = run(sys.argv[1])
    print("\n" + "="*60)
    print("COMPANY BRIEF")
    print("="*60)
    print(result["company_brief"])
    print("\n" + "="*60)
    print("STAR STORIES")
    print("="*60)
    print(result["star_stories"])
    print("\n" + "="*60)
    print("LIKELY QUESTIONS")
    print("="*60)
    print(result["likely_questions"])
