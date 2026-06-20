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
    Search for hiring manager / relevant contact at a company.
    Returns structured text for Claude to parse.
    """
    results = search(
        f"{company} hiring manager {role} LinkedIn site:linkedin.com",
        max_results=3,
        search_depth="basic"
    )

    if not results:
        results = search(
            f"{company} {role} team leader head of operations",
            max_results=3,
            search_depth="basic"
        )

    if not results:
        return ""

    formatted = f"CONTACT RESEARCH — {company} / {role}\n\n"
    for r in results:
        formatted += f"{r.get('title', '')}\n{r.get('content', '')[:300]}\n\n"
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
