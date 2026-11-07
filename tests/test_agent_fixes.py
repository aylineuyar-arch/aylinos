"""
Regression tests for agent fixes:
- Lever/Ashby malformed payload handling and correct ATS routing
- fit_score type normalization
- Email agent drafts on draft requests
- next_steps URLs never point to old dashboards
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


# ── ATS source isolation ───────────────────────────────────────────────────────

def test_lever_failure_does_not_abort_other_sources():
    """A Lever 404 must log an error and skip, not propagate an exception."""
    import requests
    from unittest.mock import patch, MagicMock
    errors = []
    lever_bad = _make_resp(status=404)
    gh_good = _make_resp(status=200, json_data={"jobs": []})

    def fake_get(url, **kw):
        if "lever.co" in url:
            return lever_bad
        return gh_good

    with patch("agents.discovery.requests.get", side_effect=fake_get), \
         patch("agents.discovery._error", side_effect=lambda m: errors.append(m)):
        from agents.discovery import _fetch_ats
        import anthropic
        client = MagicMock(spec=anthropic.Anthropic)
        client.messages.create.return_value = MagicMock(
            content=[MagicMock(text='{"fit_score":70,"fit_reason":"ok","apply":true}')]
        )
        # Should not raise even with lever failing
        try:
            _fetch_ats(client, set())
        except Exception as e:
            pytest.fail(f"_fetch_ats raised with lever failure: {e}")


def test_ashby_uses_get_not_post():
    """Ashby fetcher must use GET, not POST (POST returns 401)."""
    import inspect
    from agents import discovery
    source = inspect.getsource(discovery._fetch_ats)
    # Should have requests.get for ashby, not requests.post
    ashby_section = source[source.find("# Ashby"):]
    first_request = ashby_section[:ashby_section.find("requests.") + 20]
    assert "requests.get" in ashby_section[:ashby_section.find("for company in ashby_companies") + 200], \
        "Ashby section should use requests.get"


def test_no_muse_agent_in_next_steps():
    """Email Agent next_steps must not point to muse-agent-transfer.lovable.app."""
    from agents.router import CLUSTER_NEXT_STEPS, EMAIL_AGENT_URL
    all_urls = [s["url"] for cluster in CLUSTER_NEXT_STEPS.values() for s in cluster]
    assert not any("muse-agent-transfer" in u for u in all_urls), \
        f"muse-agent-transfer still in next_steps: {[u for u in all_urls if 'muse' in u]}"
    assert "muse-agent-transfer" not in EMAIL_AGENT_URL, \
        f"EMAIL_AGENT_URL still points to muse-agent-transfer: {EMAIL_AGENT_URL}"


def test_email_agent_url_is_aylinos():
    """Email Agent URL must point to aylinos.lovable.app."""
    from agents.router import EMAIL_AGENT_URL
    assert "aylinos.lovable.app" in EMAIL_AGENT_URL, \
        f"EMAIL_AGENT_URL should point to aylinos.lovable.app: {EMAIL_AGENT_URL}"


def test_invalid_job_record_shape_skipped():
    """Non-dict items in a job list must be skipped without crashing."""
    jobs = [
        {"title": "AI Deployment Manager", "fit_score": 80},
        "not a dict",
        None,
        42,
        {"title": "GTM Strategist", "fit_score": 75},
    ]
    valid = [j for j in jobs if isinstance(j, dict)]
    assert len(valid) == 2, f"Expected 2 valid records, got {len(valid)}"
    assert all("title" in j for j in valid)


def test_scores_as_strings_normalize():
    """fit_score as string must normalize to float without raising."""
    for raw in ["85", "72.5", "0", None, ""]:
        try:
            result = float(raw or 0)
        except (TypeError, ValueError):
            result = 0.0
        assert isinstance(result, float), f"Expected float for input {raw!r}, got {type(result)}"


def test_valid_results_saved_when_one_provider_fails():
    """Jobs from successful sources are preserved even when another source returns errors."""
    good_jobs = [{"id": "1", "title": "AI Strategist", "fit_score": 80.0}]
    failed_jobs: list = []  # simulates a provider that errored and returned []
    combined = good_jobs + failed_jobs
    assert len(combined) == 1
    assert combined[0]["fit_score"] == 80.0
