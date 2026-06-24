"""
AylinOS — Evals Dashboard HTML
--------------------------------
Renders the /evals page showing prompt v1 vs v2 comparison.
Demonstrates: real eval methodology, precision/recall, cost tracking.
"""

from api.dashboard_html import SHARED_STYLES


def _traces_rows(traces: list) -> str:
    if not traces:
        return '<div style="color:var(--muted);font-size:12px;padding:16px 0">No traces yet — queries will appear here after Render deploys.</div>'
    cluster_colors = {"career": "#818cf8", "gtm": "#34d399", "support": "#4ade80", "compliance": "#fb923c", "general": "#94a3b8"}
    rows = []
    for t in traces:
        import json as _json
        agents_list = _json.loads(t.get("agents", "[]")) if isinstance(t.get("agents"), str) else t.get("agents", [])
        agents_str = " · ".join(agents_list)
        color = cluster_colors.get(t.get("cluster", "general"), "#94a3b8")
        ts = (t.get("traced_at") or "")[:16].replace("T", " ")
        q = (t.get("query") or "")[:60]
        latency = t.get("latency_ms", 0)
        rows.append(
            f'<div style="display:flex;gap:16px;align-items:baseline;padding:8px 0;border-bottom:1px solid var(--border);font-size:12px">'
            f'<span style="color:var(--muted);font-family:\'JetBrains Mono\',monospace;white-space:nowrap;min-width:120px">{ts}</span>'
            f'<span style="flex:1;color:var(--text)">{q}</span>'
            f'<span style="color:{color};font-family:\'JetBrains Mono\',monospace;white-space:nowrap">{agents_str}</span>'
            f'<span style="color:var(--muted);font-family:\'JetBrains Mono\',monospace;white-space:nowrap">{latency}ms</span>'
            f'</div>'
        )
    return "".join(rows)


def render_evals(eval_data: dict, api_metrics: dict, traces=None) -> str:
    if not eval_data:
        return _render_no_data(api_metrics, traces)

    v1 = eval_data.get("v1", {})
    v2 = eval_data.get("v2", {})

    v1m = v1.get("metrics", {}) if v1 else {}
    v2m = v2.get("metrics", {}) if v2 else {}

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Evals — AylinOS</title>
{SHARED_STYLES}
<style>
.page-header {{
    display:flex;align-items:center;justify-content:space-between;
    margin-bottom:32px;
}}
.page-title {{ font-size:18px;font-weight:600;letter-spacing:-0.02em; }}
.page-sub {{
    font-family:'JetBrains Mono',monospace;
    font-size:11px;color:var(--muted);margin-top:4px;
}}
.back {{
    font-family:'JetBrains Mono',monospace;font-size:11px;
    color:var(--muted);text-decoration:none;
    display:inline-flex;align-items:center;gap:6px;
}}
.back:hover {{ color:var(--text); }}

.section-label {{
    font-family:'JetBrains Mono',monospace;
    font-size:10px;color:var(--muted);
    text-transform:uppercase;letter-spacing:0.08em;
    margin-bottom:16px;margin-top:32px;
}}

/* Metric comparison cards */
.compare-grid {{
    display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:8px;
}}
.metric-card {{
    background:var(--surface);border:1px solid var(--border);
    border-radius:8px;padding:20px;
}}
.metric-card.v1 {{ border-top:2px solid rgba(251,146,60,0.6); }}
.metric-card.v2 {{ border-top:2px solid rgba(129,140,248,0.6); }}
.metric-version {{
    font-family:'JetBrains Mono',monospace;
    font-size:10px;color:var(--muted);margin-bottom:14px;
    text-transform:uppercase;letter-spacing:0.08em;
}}
.metric-main {{ font-size:28px;font-weight:600;letter-spacing:-0.03em; }}
.metric-main.v1 {{ color:rgba(251,146,60,0.85); }}
.metric-main.v2 {{ color:rgba(129,140,248,0.9); }}
.metric-label {{ font-size:12px;color:var(--muted);margin-top:2px; }}
.metric-row {{
    display:flex;gap:16px;margin-top:16px;padding-top:16px;
    border-top:1px solid var(--border);
}}
.metric-mini {{ flex:1; }}
.metric-mini-val {{ font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:500; }}
.metric-mini-label {{ font-size:10px;color:var(--muted);margin-top:2px; }}

/* Delta badge */
.delta-row {{ display:flex;gap:10px;margin-bottom:32px; }}
.delta-badge {{
    padding:5px 12px;border-radius:5px;
    font-family:'JetBrains Mono',monospace;font-size:11px;
    font-weight:500;
}}
.delta-pos {{ background:rgba(52,211,153,0.1);color:#34d399;border:1px solid rgba(52,211,153,0.2); }}
.delta-neg {{ background:rgba(239,68,68,0.1);color:#f87171;border:1px solid rgba(239,68,68,0.2); }}
.delta-zero {{ background:rgba(255,255,255,0.05);color:var(--muted);border:1px solid var(--border); }}

/* Confusion matrix */
.cm-grid {{
    display:grid;grid-template-columns:1fr 1fr;gap:8px;
    max-width:280px;
}}
.cm-cell {{
    border-radius:6px;padding:14px;text-align:center;
}}
.cm-tp {{ background:rgba(52,211,153,0.12);border:1px solid rgba(52,211,153,0.25); }}
.cm-tn {{ background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.15); }}
.cm-fp {{ background:rgba(239,68,68,0.10);border:1px solid rgba(239,68,68,0.2); }}
.cm-fn {{ background:rgba(251,146,60,0.10);border:1px solid rgba(251,146,60,0.2); }}
.cm-val {{ font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:600; }}
.cm-tp .cm-val {{ color:#34d399; }}
.cm-tn .cm-val {{ color:#6ee7b7; }}
.cm-fp .cm-val {{ color:#f87171; }}
.cm-fn .cm-val {{ color:#fb923c; }}
.cm-label {{ font-size:10px;color:var(--muted);margin-top:4px; }}

/* Cost table */
.cost-table {{ width:100%;border-collapse:collapse; }}
.cost-table th {{
    font-family:'JetBrains Mono',monospace;font-size:9px;
    color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;
    padding:8px 0;border-bottom:1px solid var(--border);text-align:left;
}}
.cost-table td {{
    padding:8px 0;font-size:13px;
    border-bottom:1px solid rgba(255,255,255,0.04);
}}
.cost-table .mono {{ font-family:'JetBrains Mono',monospace;font-size:12px; }}
.cost-table tr:last-child td {{ border-bottom:none; }}

/* Test case table */
.tc-table {{ width:100%;border-collapse:collapse; }}
.tc-table th {{
    font-family:'JetBrains Mono',monospace;font-size:9px;
    color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;
    padding:10px 8px;border-bottom:1px solid var(--border);text-align:left;
}}
.tc-table td {{
    padding:9px 8px;font-size:12px;
    border-bottom:1px solid rgba(255,255,255,0.04);vertical-align:middle;
}}
.tc-table tr:last-child td {{ border-bottom:none; }}
.tc-table tr:hover td {{ background:rgba(255,255,255,0.02); }}

.badge {{
    display:inline-block;padding:2px 8px;border-radius:3px;
    font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:500;
}}
.badge-high {{ background:rgba(52,211,153,0.12);color:#34d399;border:1px solid rgba(52,211,153,0.2); }}
.badge-medium {{ background:rgba(251,146,60,0.12);color:#fb923c;border:1px solid rgba(251,146,60,0.2); }}
.badge-low {{ background:rgba(239,68,68,0.10);color:#f87171;border:1px solid rgba(239,68,68,0.15); }}
.badge-correct {{ background:rgba(52,211,153,0.08);color:#34d399; }}
.badge-wrong {{ background:rgba(239,68,68,0.08);color:#f87171; }}

/* API cost section */
.api-grid {{ display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:8px; }}
.api-card {{
    background:var(--surface);border:1px solid var(--border);
    border-radius:8px;padding:16px;
}}
.api-val {{ font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:600; }}
.api-label {{ font-size:11px;color:var(--muted);margin-top:4px; }}

/* Prompt diff */
.prompt-box {{
    background:var(--surface);border:1px solid var(--border);
    border-radius:8px;padding:20px;
    font-family:'JetBrains Mono',monospace;font-size:11px;
    color:var(--text-dim);line-height:1.7;
    white-space:pre-wrap;
}}
.diff-add {{ color:#34d399; }}
.diff-remove {{ color:#f87171;text-decoration:line-through; }}

/* layout */
.grid-2 {{ display:grid;grid-template-columns:1fr 1fr;gap:24px; }}
.card {{
    background:var(--surface);border:1px solid var(--border);
    border-radius:8px;padding:24px;
}}
</style>
</head>
<body>
<div style="max-width:1100px;margin:0 auto;padding:40px 24px">

  <!-- Header -->
  <div class="page-header">
    <div>
      <a href="/" class="back">← AylinOS</a>
      <div class="page-title" style="margin-top:16px">Prompt Evals</div>
      <div class="page-sub">v1 vs v2 scoring prompt · {len_cases} labeled test cases · real outcome ground truth</div>
    </div>
    <div style="text-align:right">
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted)">run at</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:12px;margin-top:4px">{run_at}</div>
    </div>
  </div>

  <!-- Precision / Recall / F1 comparison -->
  <div class="section-label">Model Performance — Prompt v1 vs v2</div>
  <div class="compare-grid">
    {_metric_card("v1", "Original prompt (discovery.py)", v1m)}
    {_metric_card("v2", "Improved: role-type weighting + location + exclusions", v2m)}
  </div>

  <!-- Delta badges -->
  <div class="delta-row" style="margin-top:12px">
    {_delta_badge("Precision", v1m.get("precision",0), v2m.get("precision",0))}
    {_delta_badge("Recall", v1m.get("recall",0), v2m.get("recall",0))}
    {_delta_badge("F1", v1m.get("f1",0), v2m.get("f1",0))}
    {_delta_badge("Accuracy", v1m.get("accuracy",0), v2m.get("accuracy",0))}
  </div>

  <!-- Confusion matrices side by side -->
  <div class="grid-2">
    <div class="card">
      <div class="section-label" style="margin-top:0">v1 — Confusion Matrix</div>
      {_confusion_matrix(v1m)}
      <div style="margin-top:16px;font-size:11px;color:var(--muted);line-height:1.6">
        FP = wasted time applying to bad fits<br>
        FN = missed real opportunities
      </div>
    </div>
    <div class="card">
      <div class="section-label" style="margin-top:0">v2 — Confusion Matrix</div>
      {_confusion_matrix(v2m)}
      <div style="margin-top:16px;font-size:11px;color:var(--muted);line-height:1.6">
        v2 fixes: role-type signals, location penalty,<br>
        consulting exclusion, VP+ seniority filter
      </div>
    </div>
  </div>

  <!-- API Cost & Observability -->
  <div class="section-label">API Observability — All Agent Calls</div>
  <div class="api-grid">
    <div class="api-card">
      <div class="api-val">{api_metrics.get('total_calls', 0)}</div>
      <div class="api-label">total API calls</div>
    </div>
    <div class="api-card">
      <div class="api-val">${api_metrics.get('total_cost_usd', 0):.3f}</div>
      <div class="api-label">total cost</div>
    </div>
    <div class="api-card">
      <div class="api-val">{api_metrics.get('calls_today', 0)}</div>
      <div class="api-label">calls today</div>
    </div>
    <div class="api-card">
      <div class="api-val">{api_metrics.get('avg_latency_ms', 0)}ms</div>
      <div class="api-label">avg latency</div>
    </div>
  </div>

  <!-- By agent breakdown -->
  <div class="card" style="margin-bottom:24px">
    <div class="section-label" style="margin-top:0">Cost by Agent</div>
    <table class="cost-table">
      <tr>
        <th>Agent</th><th>Calls</th><th>Cost (USD)</th><th>Avg Latency</th>
      </tr>
      {_agent_rows(api_metrics.get('by_agent', []))}
    </table>
    {_model_rows(api_metrics.get('by_model', []))}
  </div>

  <!-- Test case results -->
  <div class="section-label">Test Cases — v2 Results ({len_cases} labeled examples)</div>
  <div class="card">
    <table class="tc-table">
      <tr>
        <th>ID</th><th>Label</th><th>Expected</th><th>Predicted</th>
        <th>Fit</th><th>Conv</th><th>Correct</th>
      </tr>
      {_test_case_rows(v2.get('results', []))}
    </table>
  </div>

  <!-- Prompt diff explanation -->
  <div class="section-label">What Changed v1 → v2</div>
  <div class="card">
    <div style="font-size:13px;color:var(--text-dim);line-height:1.8;margin-bottom:20px">
      Four failure modes identified from 18 real interview outcomes and 358 applications:
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      {_change_card("Role-type weighting",
        "V1 used generic fit scoring with no signal for target titles.",
        "V2 explicitly boosts AI Strategist, Chief of Staff, GTM Strategy, Strategy & Ops. Caps fit at 30 for consulting and pure sales titles.")}
      {_change_card("Location penalty",
        "V1 ignored location entirely — SF roles scored same as NYC.",
        "V2 applies -5 conversion for SF (acceptable but not preferred), -8 for other US cities.")}
      {_change_card("Consulting exclusion",
        "V1 scored Deloitte/McKinsey as 'enterprise' with no special handling.",
        "V2 caps fit at 30 for traditional consulting firms — candidate explicitly does not want to return.")}
      {_change_card("Visa friction",
        "V1 ignored visa requirements entirely.",
        "V2 applies -8 conversion to London roles at unknown startups (UK sponsorship required).")}
    </div>
  </div>

  <!-- Live Traces -->
  <div style="margin-top:40px;font-family:'JetBrains Mono',monospace;font-size:10px;
              color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px">
    Live Traces
  </div>
  <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px 20px">
    {traces_html}
  </div>

</div>
</body>
</html>""".format(
        len_cases=len(v2.get("results", [])) or 25,
        run_at=(v2 or v1 or {}).get("run_at", "not yet run")[:16].replace("T", " "),
        traces_html=_traces_rows(traces or []),
    )


def _metric_card(version: str, label: str, m: dict) -> str:
    f1 = m.get("f1", 0)
    prec = m.get("precision", 0)
    rec = m.get("recall", 0)
    acc = m.get("accuracy", 0)
    cost = m.get("total_cost_usd", 0)
    lat = m.get("avg_latency_ms", 0)
    return f"""
    <div class="metric-card {version}">
      <div class="metric-version">{version} — {label}</div>
      <div class="metric-main {version}">{f1:.1%}</div>
      <div class="metric-label">F1 Score</div>
      <div class="metric-row">
        <div class="metric-mini">
          <div class="metric-mini-val">{prec:.1%}</div>
          <div class="metric-mini-label">Precision</div>
        </div>
        <div class="metric-mini">
          <div class="metric-mini-val">{rec:.1%}</div>
          <div class="metric-mini-label">Recall</div>
        </div>
        <div class="metric-mini">
          <div class="metric-mini-val">{acc:.1%}</div>
          <div class="metric-mini-label">Accuracy</div>
        </div>
        <div class="metric-mini">
          <div class="metric-mini-val">${cost:.3f}</div>
          <div class="metric-mini-label">Cost</div>
        </div>
      </div>
    </div>"""


def _delta_badge(label: str, v1: float, v2: float) -> str:
    delta = v2 - v1
    if abs(delta) < 0.001:
        cls = "delta-zero"
        sign = "±"
    elif delta > 0:
        cls = "delta-pos"
        sign = "+"
    else:
        cls = "delta-neg"
        sign = ""
    return f'<div class="delta-badge {cls}">{label}: {sign}{delta:.1%}</div>'


def _confusion_matrix(m: dict) -> str:
    tp = m.get("tp", 0)
    fp = m.get("fp", 0)
    fn = m.get("fn", 0)
    tn = m.get("tn", 0)
    return f"""
    <div class="cm-grid">
      <div class="cm-cell cm-tp">
        <div class="cm-val">{tp}</div>
        <div class="cm-label">True Positive<br>Correctly applied</div>
      </div>
      <div class="cm-cell cm-fp">
        <div class="cm-val">{fp}</div>
        <div class="cm-label">False Positive<br>Wrong apply rec</div>
      </div>
      <div class="cm-cell cm-fn">
        <div class="cm-val">{fn}</div>
        <div class="cm-label">False Negative<br>Missed good job</div>
      </div>
      <div class="cm-cell cm-tn">
        <div class="cm-val">{tn}</div>
        <div class="cm-label">True Negative<br>Correctly skipped</div>
      </div>
    </div>"""


def _agent_rows(by_agent: list) -> str:
    if not by_agent:
        return '<tr><td colspan="4" style="color:var(--muted);font-size:12px">No calls logged yet — run agents to populate</td></tr>'
    rows = ""
    for a in by_agent:
        rows += f"""<tr>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px">{a['agent']}</td>
          <td class="mono">{a['calls']}</td>
          <td class="mono">${a['cost']:.4f}</td>
          <td class="mono">{int(a['avg_latency'])}ms</td>
        </tr>"""
    return rows


def _model_rows(by_model: list) -> str:
    if not by_model:
        return ""
    header = """<div class="section-label" style="margin-top:20px">By Model</div>
    <table class="cost-table">
      <tr><th>Model</th><th>Calls</th><th>Input tokens</th><th>Output tokens</th><th>Cost</th></tr>"""
    rows = ""
    for m in by_model:
        rows += f"""<tr>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px">{m['model']}</td>
          <td class="mono">{m['calls']}</td>
          <td class="mono">{m['input_tokens']:,}</td>
          <td class="mono">{m['output_tokens']:,}</td>
          <td class="mono">${m['cost']:.4f}</td>
        </tr>"""
    return header + rows + "</table>"


def _test_case_rows(results: list) -> str:
    if not results:
        return '<tr><td colspan="7" style="color:var(--muted);font-size:12px;padding:16px 8px">Run evals to populate — python -m evals.run</td></tr>'
    rows = ""
    for r in results:
        label = r.get("label", "")
        label_cls = {"HIGH": "badge-high", "MEDIUM": "badge-medium", "LOW": "badge-low"}.get(label, "")
        exp = "APPLY" if r["expected_apply"] else "skip"
        pred = "APPLY" if r["predicted_apply"] else "skip"
        correct = r["expected_apply"] == r["predicted_apply"]
        correct_cls = "badge-correct" if correct else "badge-wrong"
        correct_text = "✓" if correct else "✗"
        rows += f"""<tr>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted)">{r['id'][:28]}</td>
          <td><span class="badge {label_cls}">{label}</span></td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px">{exp}</td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px">{pred}</td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:12px">{r.get('fit_score',0)}</td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:12px">{r.get('conversion_score',0)}</td>
          <td><span class="badge {correct_cls}">{correct_text}</span></td>
        </tr>"""
    return rows


def _change_card(title: str, before: str, after: str) -> str:
    return f"""<div style="background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:6px;padding:16px">
      <div style="font-size:12px;font-weight:500;margin-bottom:10px">{title}</div>
      <div style="font-size:11px;color:#f87171;margin-bottom:8px">Before: {before}</div>
      <div style="font-size:11px;color:#34d399">After: {after}</div>
    </div>"""


def _render_no_data(api_metrics: dict, traces=None) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Evals — AylinOS</title>
{SHARED_STYLES}
</head>
<body>
<div style="max-width:900px;margin:0 auto;padding:40px 24px">
  <a href="/" style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);text-decoration:none">← AylinOS</a>
  <div style="margin-top:40px;font-size:18px;font-weight:600">Prompt Evals</div>
  <div style="margin-top:8px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted)">
    25 labeled test cases ready · eval run not yet executed
  </div>
  <div style="margin-top:32px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:24px">
    <div style="font-size:13px;color:var(--text-dim);line-height:1.8;margin-bottom:16px">
      Run the eval harness to populate this dashboard:
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                background:rgba(255,255,255,0.03);border:1px solid var(--border);
                border-radius:6px;padding:12px 16px;color:var(--muted)">
      cd aylinos && python -m evals.run
    </div>
    <div style="margin-top:16px;font-size:12px;color:var(--muted);line-height:1.7">
      This runs v1 and v2 scoring prompts against 25 labeled test cases derived from
      18 real interview outcomes. Outputs precision, recall, F1, confusion matrix,
      and cost per prompt version.
    </div>
  </div>

  <!-- Still show API cost even if no eval data -->
  <div style="margin-top:32px;font-family:'JetBrains Mono',monospace;font-size:10px;
              color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px">
    API Observability
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px">
      <div style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:600">{api_metrics.get('total_calls',0)}</div>
      <div style="font-size:11px;color:var(--muted);margin-top:4px">total calls</div>
    </div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px">
      <div style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:600">${api_metrics.get('total_cost_usd',0):.3f}</div>
      <div style="font-size:11px;color:var(--muted);margin-top:4px">total cost</div>
    </div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px">
      <div style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:600">{api_metrics.get('calls_today',0)}</div>
      <div style="font-size:11px;color:var(--muted);margin-top:4px">calls today</div>
    </div>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px">
      <div style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:600">{api_metrics.get('avg_latency_ms',0)}ms</div>
      <div style="font-size:11px;color:var(--muted);margin-top:4px">avg latency</div>
    </div>
  </div>

  <!-- Live Traces -->
  <div style="margin-top:40px;font-family:'JetBrains Mono',monospace;font-size:10px;
              color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px">
    Live Traces
  </div>
  <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px 20px">
    {_traces_rows(traces or [])}
  </div>
</div>
</body>
</html>"""
