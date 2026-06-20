"""
AylinOS — Prompt Eval Harness
-------------------------------
Runs v1 and v2 scoring prompts against 25 labeled test cases.
Computes precision, recall, F1 for apply=True predictions.
Saves results to DB for dashboard display.

Usage:
  python -m evals.run           # run both prompts, print results
  python -m evals.run --v1-only # only run v1
  python -m evals.run --v2-only # only run v2

What this proves to a hiring manager:
  - You know how to build eval test sets from real outcome data
  - You can quantify prompt quality (precision/recall, not just "it works")
  - You iterate on prompts with a measurable improvement hypothesis
  - You understand the tradeoff between recall (catching good jobs) and
    precision (not wasting time on bad ones)
"""

import json
import time
import sqlite3
import anthropic
from datetime import datetime
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evals.test_cases import TEST_CASES
from db import log_api_call

# ── Candidate Profile ──────────────────────────────────────────────────────────

PROFILE = """
Tuck MBA (Dartmouth), graduating June 2026.
Ex-Deloitte Tech Strategy Senior Consultant (4 years).
PM Strategy & Ops intern at Skild AI ($14B valuation, NVIDIA/Sequoia-backed).
BS Electrical Engineering. Strong at GTM, cross-functional ops, AI/ML startups, OKRs, enterprise programs.
NOT targeting: pure consulting, government, traditional finance, engineering roles, pure sales.
Target roles: AI Strategist, AI Deployment, Solutions Strategist, Founder's Associate,
              Chief of Staff, AI Outcomes Manager, Strategy & Operations, GTM Strategy.
Target locations: NYC (primary), London (primary), SF (acceptable, not preferred).
Requires UK visa sponsorship for London roles.
"""

# ── V1 Prompt — original from discovery.py ────────────────────────────────────

V1_PROMPT_TEMPLATE = """Rate this job for an MBA candidate. Be realistic and honest.

CANDIDATE: {profile}

JOB: {title} at {company} ({company_type}) in {location}
{description}

SCORING GUIDELINES:
fit_score (0-100): how well role + company match candidate background and goals
conversion_score (0-100): realistic offer likelihood given applicant pool
  top-ai-lab: 10-25 (OpenAI/Anthropic = thousands of applicants)
  competitive-tech: 25-40 (selective, technical cultures)
  big-tech: 20-35 (mass applicant pools)
  high-growth-startup: 45-65 (smaller teams, MBA ops profile valued)
  mid-tech: 40-55 (known brand, accessible)
  vc-firm: 40-58 (tiny teams, MBA preferred for CoS/ops)
  enterprise: 10-30 (poor MBA-startup fit, slow hiring)
apply = true only if fit>=65 AND conversion>=45

Return ONLY JSON (no markdown):
{{"fit_score":0,"conversion_score":0,"fit_reason":"one sentence","conversion_reason":"one sentence","apply":false}}"""

# ── V2 Prompt — improved with failure-mode fixes ──────────────────────────────
# Fixes identified from outcome analysis:
# 1. Role-type weighting: AI Strategist / CoS / GTM / Strategy&Ops = explicit high-fit signals
# 2. Role-type exclusions: consulting titles, AE/sales, VP+ seniority = explicit low-fit
# 3. Location: NYC/London = no penalty; SF = -5 on conversion; other US = -15
# 4. Visa: London roles need sponsorship — if company unknown to sponsor, -10 conversion
# 5. Enterprise consulting (Deloitte, McKinsey) = candidate explicitly does NOT want to return

V2_PROMPT_TEMPLATE = """Rate this job for an MBA candidate. Be precise and calibrated.

CANDIDATE: {profile}

JOB: {title} at {company} ({company_type}) in {location}
{description}

SCORING GUIDELINES:

fit_score (0-100): role-company-candidate alignment
  HIGH FIT SIGNALS (push fit toward 70-90):
    - Title contains: AI Strategist, AI Deployment, GTM Strateg*, Strategy & Ops,
      Chief of Staff, Strategic Project Lead, Solutions Strateg*, Founder's Associate,
      AI Outcomes, Office of CEO
    - Company is AI-native or AI-first product company
    - Role involves cross-functional leadership, GTM, or deployment (not coding)
    - MBA explicitly preferred or required

  LOW FIT SIGNALS (push fit toward 10-40):
    - Title contains: Engineer, Developer, Software, Account Executive, Sales Rep,
      Customer Success, Recruiter, Designer, Legal, Accountant, VP, Director of, Head of
    - Company is traditional consulting (Deloitte, McKinsey, BCG, Accenture, Bain, KPMG)
    - Company is traditional finance with no AI angle (investment banking, hedge fund)
    - Role is quota-carrying sales
    - Seniority is VP or above

conversion_score (0-100): realistic offer probability given applicant pool
  top-ai-lab: 10-20 (OpenAI/Anthropic = 10,000+ applicants per role)
  competitive-tech: 25-42 (technical culture, selective but MBA ops roles exist)
  big-tech: 20-32 (mass applicant pools, process heavy)
  high-growth-startup: 48-68 (small teams, MBA ops profile highly valued)
  mid-tech: 42-56 (accessible, known brand premium)
  vc-firm: 40-55 (tiny teams, MBA CoS/ops roles common)
  enterprise: 8-25 (slow hiring, poor MBA-startup-AI fit)

  Location adjustments to conversion:
    - NYC or London: no adjustment (primary targets)
    - San Francisco: -5 (acceptable but not preferred, higher competition)
    - Other US city: -8 (relocation friction)

  Special cases:
    - Traditional consulting firms (Deloitte etc): candidate explicitly doesn't want to return → fit cap 30
    - London roles: candidate needs UK visa sponsorship → if company is startup/unknown, -8 conversion

apply = true ONLY if fit>=65 AND conversion>=45

Return ONLY JSON (no markdown):
{{"fit_score":0,"conversion_score":0,"fit_reason":"one sentence","conversion_reason":"one sentence","apply":false}}"""


# ── Scoring ────────────────────────────────────────────────────────────────────

MODEL = "claude-haiku-4-5-20251001"

# Haiku pricing (per million tokens)
HAIKU_INPUT_COST_PER_M = 0.80
HAIKU_OUTPUT_COST_PER_M = 4.00


def _cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1_000_000 * HAIKU_INPUT_COST_PER_M +
            output_tokens / 1_000_000 * HAIKU_OUTPUT_COST_PER_M)


def score_job(job: dict, prompt_template: str, client: anthropic.Anthropic,
              version: str) -> dict:
    prompt = prompt_template.format(
        profile=PROFILE,
        title=job["title"],
        company=job["company"],
        company_type=job["company_type"],
        location=job["location"],
        description=job.get("description", "")[:400],
    )

    t0 = time.time()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    latency_ms = int((time.time() - t0) * 1000)

    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw.strip())
    result["input_tokens"] = resp.usage.input_tokens
    result["output_tokens"] = resp.usage.output_tokens
    result["latency_ms"] = latency_ms
    result["cost_usd"] = _cost(resp.usage.input_tokens, resp.usage.output_tokens)

    # Log to DB
    log_api_call(
        agent=f"evals/{version}",
        purpose=f"score_{job['company']}_{job['title'][:30]}",
        model=MODEL,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        cost_usd=result["cost_usd"],
        latency_ms=latency_ms,
    )

    return result


# ── Metrics ────────────────────────────────────────────────────────────────────

def compute_metrics(results: list[dict]) -> dict:
    """Compute precision, recall, F1 for apply=True predictions."""
    tp = sum(1 for r in results if r["predicted_apply"] and r["expected_apply"])
    fp = sum(1 for r in results if r["predicted_apply"] and not r["expected_apply"])
    fn = sum(1 for r in results if not r["predicted_apply"] and r["expected_apply"])
    tn = sum(1 for r in results if not r["predicted_apply"] and not r["expected_apply"])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "accuracy": round((tp + tn) / len(results), 3),
        "total": len(results),
        "total_cost_usd": round(sum(r["cost_usd"] for r in results), 4),
        "avg_latency_ms": round(sum(r["latency_ms"] for r in results) / len(results)),
    }


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_eval(version: str, prompt_template: str, client: anthropic.Anthropic) -> dict:
    print(f"\n[Evals] Running {version} against {len(TEST_CASES)} test cases...")
    results = []

    for tc in TEST_CASES:
        try:
            scores = score_job(tc["job"], prompt_template, client, version)
            result = {
                "id": tc["id"],
                "label": tc["label"],
                "expected_apply": tc["expected_apply"],
                "predicted_apply": scores["apply"],
                "fit_score": scores["fit_score"],
                "conversion_score": scores["conversion_score"],
                "fit_reason": scores.get("fit_reason", ""),
                "conversion_reason": scores.get("conversion_reason", ""),
                "cost_usd": scores["cost_usd"],
                "latency_ms": scores["latency_ms"],
                "version": version,
            }
            results.append(result)
            status = "✓" if result["predicted_apply"] == result["expected_apply"] else "✗"
            apply_str = "APPLY" if result["predicted_apply"] else "skip "
            exp_str = "APPLY" if result["expected_apply"] else "skip "
            print(f"  {status} [{tc['label']:6}] {apply_str} (exp:{exp_str}) "
                  f"fit={scores['fit_score']:3d} conv={scores['conversion_score']:3d} "
                  f"— {tc['id']}")
            time.sleep(0.1)
        except Exception as e:
            print(f"  [ERROR] {tc['id']}: {e}")

    metrics = compute_metrics(results)
    print(f"\n  {version} Results:")
    print(f"    Precision: {metrics['precision']:.1%}  "
          f"Recall: {metrics['recall']:.1%}  "
          f"F1: {metrics['f1']:.1%}  "
          f"Accuracy: {metrics['accuracy']:.1%}")
    print(f"    TP:{metrics['tp']} FP:{metrics['fp']} FN:{metrics['fn']} TN:{metrics['tn']}")
    print(f"    Cost: ${metrics['total_cost_usd']:.4f}  "
          f"Avg latency: {metrics['avg_latency_ms']}ms")

    return {"version": version, "metrics": metrics, "results": results}


def save_eval_results(v1: dict, v2: dict):
    """Persist eval results to SQLite for dashboard display."""
    db_path = Path(__file__).parent.parent / "aylinos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS eval_runs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            version      TEXT NOT NULL,
            run_at       TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            results_json TEXT NOT NULL
        )
    """)
    now = datetime.utcnow().isoformat()
    for ev in [v1, v2]:
        conn.execute(
            "INSERT INTO eval_runs (version,run_at,metrics_json,results_json) VALUES (?,?,?,?)",
            (ev["version"], now, json.dumps(ev["metrics"]), json.dumps(ev["results"]))
        )
    conn.commit()
    conn.close()
    print("\n[Evals] Results saved to database.")


def get_latest_eval_results() -> dict:
    """Retrieve the most recent v1 and v2 eval runs for dashboard display."""
    db_path = Path(__file__).parent.parent / "aylinos.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("SELECT 1 FROM eval_runs LIMIT 1")
    except Exception:
        return None

    results = {}
    for version in ["v1", "v2"]:
        row = conn.execute(
            "SELECT * FROM eval_runs WHERE version=? ORDER BY id DESC LIMIT 1",
            (version,)
        ).fetchone()
        if row:
            results[version] = {
                "run_at": row["run_at"],
                "metrics": json.loads(row["metrics_json"]),
                "results": json.loads(row["results_json"]),
            }
    conn.close()
    return results if results else None


def run(v1_only=False, v2_only=False):
    client = anthropic.Anthropic()
    v1_result = v2_result = None

    if not v2_only:
        v1_result = run_eval("v1", V1_PROMPT_TEMPLATE, client)
    if not v1_only:
        v2_result = run_eval("v2", V2_PROMPT_TEMPLATE, client)

    if v1_result and v2_result:
        print("\n── Delta (v2 vs v1) ──────────────────────────────────────")
        for k in ["precision", "recall", "f1", "accuracy"]:
            delta = v2_result["metrics"][k] - v1_result["metrics"][k]
            sign = "+" if delta >= 0 else ""
            print(f"  {k:12}: {sign}{delta:.1%}")
        save_eval_results(v1_result, v2_result)
    elif v1_result:
        save_eval_results(v1_result, v1_result)
    elif v2_result:
        save_eval_results(v2_result, v2_result)

    return {"v1": v1_result, "v2": v2_result}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-only", action="store_true")
    parser.add_argument("--v2-only", action="store_true")
    args = parser.parse_args()
    run(v1_only=args.v1_only, v2_only=args.v2_only)
