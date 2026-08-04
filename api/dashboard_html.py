"""
AylinOS — Dashboard HTML Renderer
Kanban pipeline + Analytics. Matches home screen design system:
dark bg, Inter + JetBrains Mono, restrained color, no glassmorphism.
"""

BADGE_LABELS = {
    "ai-startup":  "AI Startup",
    "top-ai-lab":  "Top AI Lab",
    "big-tech":    "Big Tech",
    "big-finance": "Enterprise",
    "fintech":     "Fintech",
    "vc-firm":     "VC / PE",
    "health-tech": "Health Tech",
    "startup":     "Startup",
    "recruiter":   "Recruiter",
}

# Dark-mode-compatible badge colors: (bg, text)
BADGE_COLORS = {
    "ai-startup":  ("rgba(129,140,248,0.12)", "#818cf8"),
    "top-ai-lab":  ("rgba(244,114,182,0.12)", "#f472b6"),
    "big-tech":    ("rgba(96,165,250,0.12)",  "#60a5fa"),
    "big-finance": ("rgba(52,211,153,0.12)",  "#34d399"),
    "fintech":     ("rgba(251,146,60,0.12)",  "#fb923c"),
    "vc-firm":     ("rgba(167,139,250,0.12)", "#a78bfa"),
    "health-tech": ("rgba(45,212,191,0.12)",  "#2dd4bf"),
    "startup":     ("rgba(156,163,175,0.10)", "#9ca3af"),
    "recruiter":   ("rgba(156,163,175,0.08)", "#6b7280"),
}

STATUS_LABELS = {
    "no_reply":           "No Reply",
    "interviewing":       "Active Interview",
    "rejected_interview": "Eliminated",
    "rejected_early":     "Rejected",
    "offer":              "Offer",
    "withdrawn":          "Withdrawn",
}

SHARED_STYLES = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:       #0c0c10;
  --surface:  #111116;
  --surface2: #16161d;
  --border:   rgba(255,255,255,0.07);
  --border2:  rgba(255,255,255,0.12);
  --ink:      #e8e8ed;
  --ink-2:    rgba(232,232,237,0.55);
  --ink-3:    rgba(232,232,237,0.32);
  --accent:   #818cf8;
  --mono:     'JetBrains Mono', 'Menlo', monospace;
  --sans:     'Inter', system-ui, sans-serif;
}

body {
  font-family: var(--sans);
  background: var(--bg);
  color: var(--ink);
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}

/* Top bar */
.topbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 32px;
  height: 52px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}
.logo {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 500;
  color: var(--ink);
  text-decoration: none;
}
nav { display: flex; gap: 2px; }
nav a {
  color: var(--ink-3);
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
  padding: 5px 12px;
  border-radius: 6px;
  transition: color 150ms, background 150ms;
  font-family: var(--mono);
}
nav a:hover { color: var(--ink); background: rgba(255,255,255,0.05); }
nav a.active { color: var(--ink); background: rgba(255,255,255,0.08); }

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: var(--surface2);
  border: 1px solid var(--border2);
  color: var(--ink);
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 12px;
  font-family: var(--mono);
  opacity: 0;
  transition: opacity 200ms;
  pointer-events: none;
  z-index: 2000;
}
.toast.show { opacity: 1; }
.hidden { display: none !important; }

@media (prefers-reduced-motion: reduce) {
  *, nav a, .toast, .kcard { transition: none; }
}
</style>
"""


def _mini_card(job: dict) -> str:
    ct = job.get("company_type") or "startup"
    bg, fg = BADGE_COLORS.get(ct, ("rgba(156,163,175,0.10)", "#9ca3af"))
    label = BADGE_LABELS.get(ct, "Startup")
    status = job.get("status") or "no_reply"
    date = (job.get("posted_date") or "")[:10]
    job_id = (job.get("id") or "").replace("'", "\\'")
    title = job.get("title") or "Role not recorded"
    company = job.get("company") or ""
    notes = job.get("notes") or ""

    return f"""<div class="kcard" data-id="{job_id}" data-status="{status}" data-type="{ct}">
  <div class="kcard-top">
    <span class="kcard-company">{company}</span>
    <span class="kbadge" style="background:{bg};color:{fg}">{label}</span>
  </div>
  <div class="kcard-title">{title[:52]}{"…" if len(title) > 52 else ""}</div>
  <div class="kcard-footer">
    <div class="kcard-actions">
      <select class="kselect" onchange="updateStatus('{job_id}', this.value)">
        {''.join(f'<option value="{s}" {"selected" if s == status else ""}>{STATUS_LABELS[s]}</option>' for s in STATUS_LABELS)}
      </select>
      {f'<a href="{job.get("url","")}" target="_blank" class="klink">↗</a>' if job.get("url") else ""}
    </div>
    {f'<div class="kcard-note">{notes[:80]}</div>' if notes else ""}
    {f'<span class="kdate">{date}</span>' if date else ""}
  </div>
</div>"""


def _contact_card(c: dict) -> str:
    """Card for OS-found contacts — shown prominently."""
    strat = c.get("strategy", "")
    strat_color = "#34d399" if "APPLY NOW" in strat else "#fbbf24" if "NETWORK" in strat else "#9ca3af"
    return f"""<div class="kcard contact-card">
  <div class="kcard-top">
    <span class="kcard-company">{c['company']}</span>
    {"<span class='kbadge' style='background:rgba(52,211,153,0.12);color:#34d399'>{}</span>".format(c['fit_score']) if c.get('fit_score') else ""}
  </div>
  <div class="contact-row">
    <span class="contact-name">{c.get('contact_name','')}</span>
    <span class="contact-title">{c.get('contact_title','')}</span>
  </div>
  <div class="contact-angle">{c.get('contact_angle','')[:120]}</div>
  <div class="contact-strat" style="color:{strat_color}">{strat[:60]}</div>
</div>"""


def render_dashboard(jobs: list, metrics: dict) -> str:
    interviewing = [j for j in jobs if j.get("status") == "interviewing"]
    no_reply     = [j for j in jobs if j.get("status") == "no_reply"]
    offers       = [j for j in jobs if j.get("status") == "offer"]

    TYPE_COLORS = {
        "ai-startup":  ("#6366f1", "rgba(99,102,241,0.1)"),
        "top-ai-lab":  ("#f472b6", "rgba(244,114,182,0.1)"),
        "big-tech":    ("#60a5fa", "rgba(96,165,250,0.1)"),
        "fintech":     ("#fb923c", "rgba(251,146,60,0.1)"),
        "vc-firm":     ("#a78bfa", "rgba(167,139,250,0.1)"),
        "mid-tech":    ("#34d399", "rgba(52,211,153,0.1)"),
    }

    STATUS_COLOR = {
        "interviewing":       ("#fbbf24", "rgba(251,191,36,0.1)",  "● Active Interview"),
        "no_reply":           ("#94a3b8", "rgba(148,163,184,0.1)", "◎ Applied"),
        "offer":              ("#34d399", "rgba(52,211,153,0.1)",  "✓ Offer"),
        "rejected_interview": ("#9ca3af", "rgba(156,163,175,0.1)", "✗ Eliminated"),
        "rejected_early":     ("#f87171", "rgba(248,113,113,0.1)", "✗ Rejected"),
    }

    def job_row(j):
        ct = j.get("company_type") or "ai-startup"
        fg, bg = TYPE_COLORS.get(ct, ("#94a3b8", "rgba(148,163,184,0.1)"))
        label = BADGE_LABELS.get(ct, ct.replace("-"," ").title())
        status = j.get("status") or "no_reply"
        sc, sbg, slabel = STATUS_COLOR.get(status, ("#94a3b8", "rgba(148,163,184,0.1)", status))
        fit = j.get("fit_score")
        notes = j.get("notes") or ""
        url = j.get("url") or ""
        company = j.get("company", "")
        apply_btn = f'<a href="{url}" target="_blank" class="apply-btn">Apply →</a>' if url else ""
        notes_html = f'<div class="job-notes">{notes}</div>' if notes else ""
        fit_color = "#6366f1" if (fit or 0) >= 75 else "#fbbf24" if (fit or 0) >= 60 else "#94a3b8"
        return f"""<div class="job-row" data-type="{ct}">
  <div class="job-main">
    <div class="job-top">
      <span class="job-company">{company}</span>
      <span class="type-badge" style="color:{fg};background:{bg}">{label}</span>
      <span class="status-badge" style="color:{sc};background:{sbg}">{slabel}</span>
    </div>
    <div class="job-title">{j.get("title","")}</div>
    {notes_html}
    <div class="job-actions">
      <a href="#" class="rerun-btn" onclick="rerunAnalysis('{company}');return false;">⟳ Rerun Analysis</a>
      {apply_btn}
    </div>
  </div>
  <div class="job-right">
    {f'<span class="fit-score" style="color:{fit_color}">{fit}</span><span class="fit-label">fit</span>' if fit else '<span class="fit-score no-fit">—</span>'}
  </div>
</div>"""

    # Fit tiers
    high_fit   = [j for j in no_reply if (j.get("fit_score") or 0) >= 78]
    medium_fit = [j for j in no_reply if 60 <= (j.get("fit_score") or 0) < 78]
    low_fit    = [j for j in no_reply if (j.get("fit_score") or 0) < 60]

    active_rows      = "".join(job_row(j) for j in interviewing)
    high_fit_rows    = "".join(job_row(j) for j in high_fit)
    medium_fit_rows  = "".join(job_row(j) for j in medium_fit)
    low_fit_rows     = "".join(job_row(j) for j in low_fit)
    offer_rows       = "".join(job_row(j) for j in offers)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AylinOS · Pipeline</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#f8f7f4;--surface:#ffffff;--border:rgba(0,0,0,.08);
  --border2:rgba(0,0,0,.14);--ink:#111116;--ink-2:#4a5568;--ink-3:#94a3b8;
  --accent:#6366f1;--mono:'JetBrains Mono',monospace;
}}
body{{background:var(--bg);color:var(--ink);font-family:Inter,-apple-system,sans-serif;min-height:100vh;font-size:18px;-webkit-font-smoothing:antialiased}}
.topbar{{display:flex;align-items:center;justify-content:space-between;padding:18px 40px;border-bottom:1px solid var(--border);background:var(--surface)}}
.logo{{font-size:20px;font-weight:700;color:var(--ink);text-decoration:none}}
.logo span{{color:var(--accent)}}
nav a{{font-size:15px;color:var(--ink-3);text-decoration:none;margin-left:28px;font-family:var(--mono)}}
nav a:hover,nav a.active{{color:var(--ink)}}
.stats{{display:flex;gap:1px;border-bottom:1px solid var(--border);background:var(--border)}}
.stat{{background:var(--surface);flex:1;padding:28px 32px}}
.stat-val{{font-size:42px;font-weight:800;font-family:var(--mono)}}
.stat-label{{font-size:14px;color:var(--ink-3);margin-top:6px;font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase;font-weight:600}}
.main{{max-width:960px;margin:0 auto;padding:36px 32px}}
.section-hdr{{display:flex;align-items:center;gap:10px;margin-bottom:16px;margin-top:28px}}
.section-hdr:first-child{{margin-top:0}}
.section-title{{font-size:15px;font-weight:600;color:var(--ink-3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono)}}
.section-count{{font-size:15px;font-weight:700;color:var(--ink-3);font-family:var(--mono)}}
.section-tag{{font-size:13px;font-family:var(--mono);font-weight:600;letter-spacing:.04em}}
.job-row{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px 28px;margin-bottom:12px;display:flex;align-items:center;gap:20px;transition:border-color .15s}}
.job-row:hover{{border-color:var(--border2)}}
.job-main{{flex:1;min-width:0}}
.job-top{{display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap}}
.job-company{{font-size:21px;font-weight:700;color:var(--ink)}}
.type-badge{{font-size:13px;font-weight:600;padding:4px 11px;border-radius:20px;font-family:var(--mono)}}
.status-badge{{font-size:13px;font-weight:600;padding:4px 11px;border-radius:20px;font-family:var(--mono)}}
.job-title{{font-size:16px;color:var(--ink-2);font-weight:500;line-height:1.4}}
.job-notes{{font-size:15px;color:var(--ink-3);font-family:var(--mono);margin-top:6px}}
.job-right{{display:flex;flex-direction:column;align-items:flex-end;gap:8px;flex-shrink:0}}
.fit-score{{font-size:36px;font-weight:800;font-family:var(--mono);color:var(--accent)}}
.job-actions{{display:flex;align-items:center;gap:10px;margin-top:12px}}
.rerun-btn{{font-size:13px;font-weight:600;font-family:var(--mono);color:var(--accent);text-decoration:none;padding:6px 14px;border:1px solid rgba(99,102,241,0.3);border-radius:7px;transition:background .13s}}
.rerun-btn:hover{{background:rgba(99,102,241,0.07)}}
.apply-btn{{font-size:13px;font-weight:700;font-family:var(--mono);color:#fff;background:var(--accent);padding:7px 16px;border-radius:7px;text-decoration:none;letter-spacing:.04em;white-space:nowrap}}
.apply-btn:hover{{background:#4f46e5}}
.fit-label{{font-size:13px;color:var(--ink-3);font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase;text-align:center}}
.no-fit{{color:var(--ink-3) !important}}
</style>
</head>
<body>
<div class="topbar">
  <a href="/" class="logo">Aylin<span>OS</span></a>
  <nav>
    <a href="/job-search" class="active">Pipeline</a>
    <a href="/networking">Networking</a>
    <a href="/evals">Evals</a>
  </nav>
</div>

<div class="stats">
  <div class="stat">
    <div class="stat-val">{len(jobs)}</div>
    <div class="stat-label">Applications</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#fbbf24">{len(interviewing)}</div>
    <div class="stat-label">Active Interviews</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#94a3b8">{len(no_reply)}</div>
    <div class="stat-label">Pending Reply</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#34d399">{len(offers)}</div>
    <div class="stat-label">Offers</div>
  </div>
</div>

<div class="main">
  {f'''<div class="section-hdr">
    <span class="section-title">Offers</span>
    <span class="section-count">{len(offers)}</span>
  </div>
  {offer_rows}''' if offers else ""}

  {f'''<div class="section-hdr">
    <span class="section-title">Active Interviews</span>
    <span class="section-count">{len(interviewing)}</span>
  </div>
  {active_rows}''' if interviewing else ""}

  {f'''<div class="section-hdr">
    <span class="section-title">High Fit</span>
    <span class="section-count">{len(high_fit)}</span>
    <span class="section-tag" style="color:#6366f1">≥ 78</span>
  </div>
  {high_fit_rows}''' if high_fit else ""}

  {f'''<div class="section-hdr">
    <span class="section-title">Medium Fit</span>
    <span class="section-count">{len(medium_fit)}</span>
    <span class="section-tag" style="color:#fbbf24">60 – 77</span>
  </div>
  {medium_fit_rows}''' if medium_fit else ""}

  {f'''<div class="section-hdr">
    <span class="section-title">Low Fit / Reach</span>
    <span class="section-count">{len(low_fit)}</span>
    <span class="section-tag" style="color:#94a3b8">&lt; 60</span>
  </div>
  {low_fit_rows}''' if low_fit else ""}
</div>
<script>
function rerunAnalysis(company) {{
  const frontendBase = window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : window.location.origin;
  const q = encodeURIComponent('should I apply to ' + company);
  window.open(frontendBase + '?q=' + q, '_blank');
}}
</script>
</body>
</html>"""


def render_analytics(metrics: dict, funnel: dict, by_type: list, weekly: list) -> str:
    m = metrics
    applied      = funnel.get("applied", 1) or 1
    responded    = funnel.get("got_response", 0)
    interviewed  = funnel.get("got_interview", 0)
    offers       = funnel.get("got_offer", 0)
    pct = lambda n: f"{round(n / applied * 100, 1)}%" if applied else "0%"

    # Funnel bars
    def funnel_step(n, label, accent, p):
        width = max(4, round(float(p.rstrip('%'))))
        return f"""<div class="funnel-step">
  <div class="funnel-bar-wrap">
    <div class="funnel-bar" style="width:{width}%;background:{accent}"></div>
  </div>
  <div class="funnel-meta">
    <span class="funnel-n" style="color:{accent}">{n}</span>
    <span class="funnel-label">{label}</span>
    <span class="funnel-pct" style="color:{accent}">{p}</span>
  </div>
</div>"""

    funnel_html = "".join([
        funnel_step(applied,     "Applied",       "var(--ink-2)",  "100%"),
        funnel_step(responded,   "Got Response",  "var(--accent)", pct(responded)),
        funnel_step(interviewed, "Interviewed",   "#fbbf24",       pct(interviewed)),
        funnel_step(offers,      "Offers",        "#34d399",       pct(offers)),
    ])

    biggest = max([
        ("Application → Response",  funnel.get("drop_application_to_response", 0)),
        ("Response → Interview",    funnel.get("drop_response_to_interview", 0)),
        ("Interview → Offer",       funnel.get("drop_interview_to_offer", 0)),
    ], key=lambda x: x[1])

    # Company type table
    type_accents = {
        "top-ai-lab":  "#f472b6",
        "ai-startup":  "#818cf8",
        "big-tech":    "#60a5fa",
        "big-finance": "#34d399",
        "fintech":     "#fb923c",
        "vc-firm":     "#a78bfa",
        "health-tech": "#2dd4bf",
        "startup":     "#9ca3af",
        "recruiter":   "#6b7280",
    }
    rows = ""
    for r in sorted(by_type, key=lambda x: x.get("total", 0), reverse=True):
        ct = r.get("company_type") or "startup"
        lbl = BADGE_LABELS.get(ct, ct.replace("-", " ").title())
        tot = r.get("total", 0)
        got = r.get("got_interview", 0)
        rate = round(got / tot * 100, 1) if tot else 0
        c = type_accents.get(ct, "#9ca3af")
        rows += f"""<tr class="trow">
  <td class="td"><span class="type-label" style="color:{c}">{lbl}</span></td>
  <td class="td td-mono">{tot}</td>
  <td class="td td-mono" style="color:{c}">{got}</td>
  <td class="td">
    <div class="rate-row">
      <div class="rate-bar-bg"><div class="rate-bar" style="width:{min(rate,100)}%;background:{c}"></div></div>
      <span class="rate-pct" style="color:{c}">{rate}%</span>
    </div>
  </td>
</tr>"""

    # Weekly chart
    max_v = max((w.get("applications", 0) for w in weekly), default=1) or 1
    bars = ""
    for w in weekly[-14:]:
        n = w.get("applications", 0)
        h = max(4, int(n / max_v * 80))
        bars += f"""<div class="bar-col">
  <span class="bar-n">{n}</span>
  <div class="bar" style="height:{h}px"></div>
  <span class="bar-label">{w.get('week','')[-5:]}</span>
</div>"""

    def stat_cell(value, label, accent=None):
        color = accent or "var(--ink)"
        return f"""<div class="stat-cell">
  <span class="stat-value" style="color:{color}">{value}</span>
  <span class="stat-label">{label}</span>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AylinOS · Analytics</title>
{SHARED_STYLES}
<style>
/* Stats bar */
.stats-bar {{
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 16px 32px;
  display: flex;
  gap: 0;
}}
.stat-cell {{
  flex: 1;
  padding: 0 24px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.stat-cell:first-child {{ padding-left: 0; }}
.stat-cell:last-child {{ border-right: none; }}
.stat-value {{
  font-family: var(--mono);
  font-size: 22px;
  font-weight: 500;
  line-height: 1;
}}
.stat-label {{
  font-family: var(--mono);
  font-size: 10px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}

/* Page */
.page {{ padding: 32px; max-width: 960px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }}

/* Section cards */
.section {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}}
.section-head {{
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  font-family: var(--mono);
  font-size: 11px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}}
.section-body {{ padding: 20px; }}

/* Funnel */
.funnel {{ display: flex; flex-direction: column; gap: 10px; }}
.funnel-step {{ display: flex; flex-direction: column; gap: 6px; }}
.funnel-bar-wrap {{
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
}}
.funnel-bar {{ height: 100%; border-radius: 3px; }}
.funnel-meta {{ display: flex; align-items: center; gap: 12px; }}
.funnel-n {{ font-family: var(--mono); font-size: 18px; font-weight: 500; min-width: 48px; }}
.funnel-label {{ font-size: 13px; color: var(--ink-2); flex: 1; }}
.funnel-pct {{ font-family: var(--mono); font-size: 12px; font-weight: 500; }}
.drop-note {{
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(251,191,36,0.06);
  border: 1px solid rgba(251,191,36,0.15);
  border-radius: 8px;
  font-family: var(--mono);
  font-size: 11px;
  color: #fbbf24;
}}

/* Table */
table {{ width: 100%; border-collapse: collapse; }}
.th {{
  text-align: left;
  padding: 8px 14px;
  font-family: var(--mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--ink-3);
  border-bottom: 1px solid var(--border);
}}
.trow {{ border-bottom: 1px solid var(--border); }}
.trow:last-child {{ border-bottom: none; }}
.trow:hover td {{ background: var(--surface2); }}
.td {{ padding: 11px 14px; }}
.td-mono {{ font-family: var(--mono); font-size: 13px; color: var(--ink-2); }}
.type-label {{ font-size: 12px; font-weight: 500; }}
.rate-row {{ display: flex; align-items: center; gap: 10px; }}
.rate-bar-bg {{
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  min-width: 60px;
}}
.rate-bar {{ height: 100%; border-radius: 2px; }}
.rate-pct {{ font-family: var(--mono); font-size: 12px; font-weight: 500; min-width: 40px; text-align: right; }}

/* Weekly chart */
.chart-wrap {{
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 110px;
  padding-bottom: 24px;
}}
.bar-col {{
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  justify-content: flex-end;
}}
.bar-n {{ font-family: var(--mono); font-size: 9px; color: var(--ink-3); }}
.bar {{ width: 100%; background: rgba(129,140,248,0.5); border-radius: 3px 3px 0 0; }}
.bar-label {{ font-family: var(--mono); font-size: 9px; color: var(--ink-3); }}
</style>
</head>
<body>

<header class="topbar">
  <a href="/" class="logo">AylinOS</a>
  <nav>
    <a href="/job-search">Pipeline</a>
    <a href="/analytics" class="active">Analytics</a>
  </nav>
</header>

<div class="stats-bar">
  {stat_cell(m.get('applied', 0), 'Total Applied')}
  {stat_cell(m.get('engaged', 0), 'Got Response', 'var(--accent)')}
  {stat_cell(interviewed, 'Interviewed', '#fbbf24')}
  {stat_cell(m.get('rejected_interview', 0), 'Eliminated', '#9ca3af')}
  {stat_cell(f"{m.get('response_rate', 0)}%", 'Response Rate', 'var(--accent)')}
</div>

<div class="page">

  <div class="section">
    <div class="section-head">Conversion Funnel</div>
    <div class="section-body">
      <div class="funnel">{funnel_html}</div>
      <div class="drop-note">Biggest drop: {biggest[0]} — {biggest[1]}% lost at this stage</div>
    </div>
  </div>

  <div class="section">
    <div class="section-head">Interview Rate by Company Type</div>
    <div class="section-body" style="padding:0">
      <table>
        <thead>
          <tr>
            <th class="th">Type</th>
            <th class="th">Applied</th>
            <th class="th">Interviewed</th>
            <th class="th">Rate</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="section-head">Application Volume · Last 14 Weeks</div>
    <div class="section-body">
      <div class="chart-wrap">{bars}</div>
    </div>
  </div>

</div>
</body>
</html>"""
