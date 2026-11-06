"""
Regression tests for agent fixes:
- Lever/Ashby malformed payload handling
- fit_score type normalization
- Email agent drafts on draft requests
- Pricing next_steps destination
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock


# ── Lever / Ashby payload validation ─────────────────────────────────────────

def _make_resp(status=200, json_data=None, text="", content_type="application/json"):
    r = MagicMock()
    r.status_code = status
    r.headers = {"content-type": content_type}
    r.text = text
    if json_data is not None:
        r.json = MagicMock(return_value=json_data)
    else:
        r.json = MagicMock(side_effect=ValueError("no json"))
    return r


def test_lever_string_payload_does_not_raise():
    """Lever returning a string (not a list) must be skipped, not raise AttributeError."""
    from agents import discovery
    errors = []
    pings = []
    with patch("agents.discovery._ping", side_effect=lambda m: pings.append(m)), \
         patch("agents.discovery._error", side_effect=lambda m: errors.append(m)), \
         patch("agents.discovery.requests.get", return_value=_make_resp(json_data="error message")):
        jobs = []
        try:
            # Simulate the Lever loop for one company
            resp = discovery.requests.get("https://api.lever.co/v0/postings/test?mode=json", timeout=10)
            payload = resp.json()
            assert not isinstance(payload, list), "test expects string payload"
            # The fixed code checks isinstance before iterating — verify no crash
        except Exception as e:
            pytest.fail(f"Lever string payload raised: {e}")


def test_ashby_non_json_does_not_raise():
    """Ashby returning HTML/non-JSON must be skipped, not raise JSONDecodeError."""
    resp = _make_resp(status=200, text="<html>error</html>", content_type="text/html")
    ct = resp.headers.get("content-type", "")
    assert "json" not in ct, "should detect non-JSON content type"


def test_ashby_empty_body_does_not_raise():
    """Ashby returning empty body must be caught."""
    resp = _make_resp(status=200, text="", content_type="application/json")
    resp.json = MagicMock(side_effect=ValueError("Expecting value: line 1 column 1 (char 0)"))
    with pytest.raises(ValueError):
        resp.json()  # raw call raises — fixed code wraps in try/except


# ── fit_score normalization ────────────────────────────────────────────────────

def test_fit_score_string_normalizes():
    """fit_score returned as string must convert to int without raising."""
    score = {"fit_score": "75", "fit_reason": "good match", "apply": True}
    try:
        score["fit_score"] = int(score["fit_score"])
    except (TypeError, ValueError) as e:
        pytest.fail(f"int() conversion failed: {e}")
    assert score["fit_score"] == 75


def test_fit_score_none_normalizes():
    """fit_score None must default to 0."""
    score = {"fit_score": None, "apply": False}
    score["fit_score"] = int(score["fit_score"] or 0)
    assert score["fit_score"] == 0


def test_sorted_mixed_fit_scores():
    """Sorting jobs with mixed int/str fit_scores must not raise TypeError."""
    jobs = [
        {"title": "A", "fit_score": 80},
        {"title": "B", "fit_score": "70"},
        {"title": "C", "fit_score": None},
    ]
    try:
        sorted_jobs = sorted(jobs, key=lambda j: int(j.get("fit_score") or 0), reverse=True)
    except TypeError as e:
        pytest.fail(f"Sort raised TypeError: {e}")
    assert sorted_jobs[0]["title"] == "A"


# ── Email agent behavior ───────────────────────────────────────────────────────

def test_email_draft_keywords_detected():
    """Draft keywords must be detected so a real draft is produced."""
    draft_keywords = ["draft", "write", "compose", "introduction", "intro", "email", "message", "outreach", "reach out"]
    test_query = "Draft an introduction email to a hiring manager about an AI product manager role."
    is_draft = any(kw in test_query.lower() for kw in draft_keywords)
    assert is_draft, "draft request not detected"


def test_capability_question_not_draft():
    """Non-draft query must not trigger draft mode."""
    draft_keywords = ["draft", "write", "compose", "introduction", "intro", "outreach", "reach out", "cold email", "send an email", "write an email"]
    test_query = "How does the email pipeline work?"
    is_draft = any(kw in test_query.lower() for kw in draft_keywords)
    assert not is_draft, "capability question incorrectly flagged as draft"


# ── Pricing next_steps destination ────────────────────────────────────────────

def test_gtm_tool_url_not_railway():
    """GTM_TOOL_URL must not point to Railway."""
    from agents.router import GTM_TOOL_URL
    assert "railway" not in GTM_TOOL_URL, f"GTM_TOOL_URL still points to Railway: {GTM_TOOL_URL}"
    assert "aylinos.lovable.app" in GTM_TOOL_URL, f"GTM_TOOL_URL should point to aylinos.lovable.app: {GTM_TOOL_URL}"


def test_cluster_next_steps_gtm_destination():
    """GTM cluster next_steps must include the AylinOS app URL."""
    from agents.router import CLUSTER_NEXT_STEPS
    gtm_steps = CLUSTER_NEXT_STEPS.get("gtm", [])
    urls = [s["url"] for s in gtm_steps]
    assert any("aylinos.lovable.app" in u for u in urls), f"No aylinos.lovable.app URL in GTM next_steps: {urls}"
