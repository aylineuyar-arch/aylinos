"""
AylinOS — Tavily Integration
------------------------------
Live web search for company research, job market intelligence,
and hiring manager discovery.

Replaces Claude's stale training knowledge with real-time web results.
Used by: agents/research.py, agents/discovery.py
"""

import os
import requests
from datetime import datetime

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
BASE_URL = "https://api.tavily.com/search"


def search(query: str, max_results: int = 5, search_depth: str = "advanced") -> list[dict]:
    """
    Run a Tavily search. Returns list of {title, url, content, score}.
    search_depth: "basic" (faster) or "advanced" (more thorough)
    """
    if not TAVILY_API_KEY:
        print("[Tavily] No API key set — skipping live search")
        return []

    try:
        resp = requests.post(
            BASE_URL,
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": True,
                "include_raw_content": False,
            },
            timeout=15
        )
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        print(f"[Tavily] Search failed: {e}")
        return []


def research_company(company: str) -> str:
    """
    Pull live intel on a company.
    Returns a formatted string ready to pass to Claude for synthesis.
    """
    queries = [
        f"{company} AI startup latest news 2025 2026",
        f"{company} funding investors CEO leadership team",
        f"{company} product launch hiring strategy operations",
    ]

    all_results = []
    for q in queries:
        results = search(q, max_results=3, search_depth="basic")
        all_results.extend(results)

    if not all_results:
        return ""

    # Format for Claude consumption
    formatted = f"LIVE WEB RESEARCH — {company} (as of {datetime.now().strftime('%B %Y')})\n\n"
    seen_urls = set()
    for r in all_results:
        url = r.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        formatted += f"SOURCE: {r.get('title', '')}\n"
        formatted += f"URL: {url}\n"
        formatted += f"{r.get('content', '')[:400]}\n\n"

    return formatted.strip()


def find_hiring_manager(company: str, role: str) -> str:
    """
    Search LinkedIn (via Tavily) for real named contacts at a company.
    Targets the hiring manager for the role AND IC-level peers.
    Returns structured text for Claude to identify the best outreach target.
    """
    queries = [
        f"{company} VP Product OR Head of GTM OR Chief of Staff OR Head of Strategy OR Head of Customer Success site:linkedin.com",
        f"{company} Engagement Manager OR Solutions Consultant OR Deployment Specialist OR Strategy Operations site:linkedin.com",
        f"{company} leadership team product strategy operations 2025 2026",
    ]

    all_results = []
    for q in queries:
        results = search(q, max_results=3, search_depth="basic")
        all_results.extend(results)

    if not all_results:
        return ""

    formatted = f"CONTACT RESEARCH — {company}\n\n"
    seen = set()
    for r in all_results:
        url = r.get("url", "")
        if url in seen:
            continue
        seen.add(url)
        formatted += f"{r.get('title', '')}\n{r.get('content', '')[:350]}\n\n"
    return formatted.strip()


def find_open_roles(company: str) -> str:
    """
    Fetch live open roles at a company. Tries direct ATS APIs first
    (Greenhouse, Lever, Ashby), then falls back to Tavily search.
    Returns formatted role list for Claude to score.
    """
    import re as _re
    import requests as _req

    slug = company.lower().replace(" ", "-").replace(".", "")
    roles = []

    # Try Greenhouse
    try:
        r = _req.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", timeout=8)
        for item in r.json().get("jobs", []):
            roles.append({"title": item.get("title",""), "url": item.get("absolute_url",""), "location": item.get("location",{}).get("name","")})
    except Exception:
        pass

    # Try Lever
    if not roles:
        try:
            r = _req.get(f"https://api.lever.co/v0/postings/{slug}?mode=json", timeout=8)
            for item in r.json() if isinstance(r.json(), list) else []:
                roles.append({"title": item.get("text",""), "url": item.get("hostedUrl",""), "location": item.get("categories",{}).get("location","")})
        except Exception:
            pass

    # Try Ashby
    if not roles:
        try:
            r = _req.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=8)
            for item in r.json().get("jobPostings", []):
                roles.append({"title": item.get("title",""), "url": item.get("externalLink",""), "location": item.get("location","")})
        except Exception:
            pass

    # Try custom careers page scrape (BeautifulSoup)
    if not roles:
        try:
            from bs4 import BeautifulSoup
            base = f"https://www.{slug}.com"
            r = _req.get(f"{base}/careers", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all("a", href=_re.compile(r'/careers/[a-f0-9-]{20,}'))
            for link in links[:10]:
                title = link.get_text(strip=True)
                href = link.get("href","")
                full_url = href if href.startswith("http") else base + href
                if title:
                    roles.append({"title": title, "url": full_url, "location": ""})
        except Exception:
            pass

    # Fall back to Tavily search
    if not roles:
        results = search(f'"{company}" open roles jobs strategy operations AI 2026', max_results=4, search_depth="basic")
        formatted = f"OPEN ROLES — {company} (via web search)\n\n"
        for r in results:
            formatted += f"{r.get('title','')}\n{r.get('content','')[:300]}\n\n"
        return formatted.strip()

    formatted = f"OPEN ROLES — {company}\n\n"
    for role in roles[:8]:
        formatted += f"- {role['title']}{' | ' + role['location'] if role['location'] else ''} | {role['url']}\n"
    return formatted.strip()


def job_market_intel(role_type: str, location: str) -> str:
    """
    Live market intel for a role type and location.
    Used by discovery agent to understand current demand.
    """
    results = search(
        f"{role_type} jobs {location} AI startup 2026 hiring",
        max_results=4,
        search_depth="basic"
    )
    formatted = ""
    for r in results:
        formatted += f"{r.get('title','')}: {r.get('content','')[:200]}\n\n"
    return formatted.strip()
