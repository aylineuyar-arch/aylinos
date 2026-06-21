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
    import db as _db
    m = metrics

    # OS-found contacts (from advisor runs)
    os_contacts = _db.get_companies_with_contacts()

    interviewing = [j for j in jobs if j.get("status") == "interviewing"]
    eliminated   = [j for j in jobs if j.get("status") == "rejected_interview"]
    rejected     = [j for j in jobs if j.get("status") == "rejected_early"]
    no_reply     = [j for j in jobs if j.get("status") == "no_reply"]
    offers       = [j for j in jobs if j.get("status") == "offer"]

    def lane(title, items, accent, collapsed=False):
        count = len(items)
        cards = "".join(_mini_card(j) for j in items)
        caret = "▸" if collapsed else "▾"
        return f"""<div class="lane">
  <div class="lane-header" onclick="toggleLane(this)" style="--lane-accent:{accent}">
    <div class="lane-left">
      <span class="lane-caret">{caret}</span>
      <span class="lane-title">{title}</span>
    </div>
    <span class="lane-count" style="color:{accent}">{count}</span>
  </div>
  <div class="lane-body" {"style='display:none'" if collapsed else ""}>
    {cards if cards else '<div class="lane-empty">None yet</div>'}
  </div>
</div>"""

    def stat_cell(value, label, accent=None):
        color = accent or "var(--ink)"
        return f"""<div class="stat-cell">
  <span class="stat-value" style="color:{color}">{value}</span>
  <span class="stat-label">{label}</span>
</div>"""

    # OS contacts section — shown at top if any exist
    if os_contacts:
        contact_cards = "".join(_contact_card(c) for c in os_contacts)
        os_section = f"""<div class="lane">
  <div class="lane-header" style="--lane-accent:#818cf8">
    <div class="lane-left">
      <span class="lane-caret">▾</span>
      <span class="lane-title">⚡ AylinOS Found — Contacts Identified</span>
    </div>
    <span class="lane-count" style="color:#818cf8">{len(os_contacts)}</span>
  </div>
  <div class="lane-body">{contact_cards}</div>
</div>"""
    else:
        os_section = f"""<div class="lane">
  <div class="lane-header" style="--lane-accent:#818cf8">
    <div class="lane-left">
      <span class="lane-caret">▾</span>
      <span class="lane-title">⚡ AylinOS Found — Contacts Identified</span>
    </div>
    <span class="lane-count" style="color:#818cf8">0</span>
  </div>
  <div class="lane-body"><div class="lane-empty">Ask the OS "should I apply to [company]?" to populate contacts here</div></div>
</div>"""

    offer_lane     = lane("Offers", offers, "#34d399") if offers else ""
    interview_lane = lane("Active Interviews", interviewing, "#fbbf24")
    elim_lane      = lane("Eliminated After Interviews", eliminated, "#9ca3af", collapsed=True)
    rejected_lane  = lane("Rejected (Early / Email)", rejected, "#f87171", collapsed=True)
    noreply_lane   = lane("No Reply", no_reply, "#4b5563", collapsed=True)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AylinOS · Pipeline</title>
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
  color: var(--ink);
  line-height: 1;
}}
.stat-label {{
  font-family: var(--mono);
  font-size: 10px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}

/* Toolbar */
.toolbar {{
  padding: 20px 32px 0;
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}}
.filter-chips {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.fchip {{
  font-family: var(--mono);
  font-size: 11px;
  padding: 5px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: transparent;
  color: var(--ink-3);
  cursor: pointer;
  transition: all 150ms;
}}
.fchip:hover {{ color: var(--ink); border-color: var(--border2); }}
.fchip.active {{ color: var(--ink); border-color: rgba(129,140,248,0.5); background: rgba(129,140,248,0.08); }}
.refresh-btn {{
  font-family: var(--mono);
  font-size: 11px;
  padding: 6px 14px;
  background: rgba(129,140,248,0.1);
  color: var(--accent);
  border: 1px solid rgba(129,140,248,0.25);
  border-radius: 6px;
  cursor: pointer;
  transition: background 150ms;
  white-space: nowrap;
}}
.refresh-btn:hover {{ background: rgba(129,140,248,0.18); }}

/* Pipeline */
.pipeline {{
  padding: 20px 32px 60px;
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1px;
}}

/* Lane */
.lane {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 8px;
}}
.lane-header {{
  padding: 13px 18px;
  cursor: pointer;
  user-select: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 2px solid var(--lane-accent, var(--border2));
  transition: background 150ms;
}}
.lane-header:hover {{ background: var(--surface2); }}
.lane-left {{ display: flex; align-items: center; gap: 10px; }}
.lane-caret {{ font-size: 10px; color: var(--ink-3); width: 12px; }}
.lane-title {{ font-size: 12px; font-weight: 500; color: var(--ink-2); font-family: var(--mono); }}
.lane-count {{ font-family: var(--mono); font-size: 12px; font-weight: 500; }}
.lane-body {{ padding: 0 14px 14px; display: flex; flex-direction: column; gap: 6px; }}
.lane-empty {{ padding: 20px 0; text-align: center; color: var(--ink-3); font-size: 12px; font-family: var(--mono); }}

/* Card */
.kcard {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
  transition: border-color 150ms;
}}
.kcard:hover {{ border-color: var(--border2); }}
.contact-card {{ border-color: rgba(129,140,248,0.25); }}
.contact-row {{ display:flex; gap:8px; align-items:baseline; margin:6px 0 4px; }}
.contact-name {{ font-size:13px; font-weight:600; color:#818cf8; }}
.contact-title {{ font-size:11px; color:var(--ink-3); font-family:var(--mono); }}
.contact-angle {{ font-size:12px; color:var(--ink-2); line-height:1.5; margin-bottom:6px; }}
.contact-strat {{ font-size:10px; font-family:var(--mono); letter-spacing:.04em; }}
.kcard-top {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  gap: 8px;
}}
.kcard-company {{ font-size: 13px; font-weight: 600; color: var(--ink); }}
.kbadge {{
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}}
.kcard-title {{ font-size: 12px; color: var(--ink-3); margin-bottom: 10px; }}
.kcard-footer {{ display: flex; flex-direction: column; gap: 6px; }}
.kcard-actions {{ display: flex; gap: 6px; align-items: center; }}
.kselect {{
  font-family: var(--mono);
  font-size: 11px;
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--ink-2);
  background: var(--surface);
  cursor: pointer;
  flex: 1;
}}
.klink {{
  font-family: var(--mono);
  font-size: 11px;
  color: var(--ink-3);
  text-decoration: none;
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 5px;
  transition: color 150ms;
}}
.klink:hover {{ color: var(--ink); }}
.kcard-note {{ font-size: 11px; color: var(--ink-3); line-height: 1.5; font-family: var(--mono); }}
.kdate {{ font-family: var(--mono); font-size: 10px; color: var(--ink-3); }}
</style>
</head>
<body>

<header class="topbar">
  <a href="/" class="logo">AylinOS</a>
  <nav>
    <a href="/job-search" class="active">Pipeline</a>
    <a href="/analytics">Analytics</a>
  </nav>
</header>

<div class="stats-bar">
  {stat_cell(m.get('applied', 0), 'Total Applied')}
  {stat_cell(m.get('engaged', 0), 'Got Response', 'var(--accent)')}
  {stat_cell(len(interviewing), 'Active Interviews', '#fbbf24')}
  {stat_cell(m.get('rejected_interview', 0), 'Eliminated', '#9ca3af')}
  {stat_cell(m.get('offers', 0), 'Offers', '#34d399')}
  {stat_cell(f"{m.get('response_rate', 0)}%", 'Response Rate', 'var(--accent)')}
</div>

<div class="toolbar">
  <div class="filter-chips">
    <button class="fchip active" onclick="filterType('all',this)">All</button>
    <button class="fchip" onclick="filterType('top-ai-lab',this)">Top AI Labs</button>
    <button class="fchip" onclick="filterType('ai-startup',this)">AI Startups</button>
    <button class="fchip" onclick="filterType('big-tech',this)">Big Tech</button>
    <button class="fchip" onclick="filterType('fintech',this)">Fintech</button>
    <button class="fchip" onclick="filterType('vc-firm',this)">VC / PE</button>
  </div>
  <button class="refresh-btn" onclick="triggerRefresh()">↻ Refresh</button>
</div>

<div class="pipeline" id="pipeline">
  {os_section}
  {offer_lane}
  {interview_lane}
  {elim_lane}
  {rejected_lane}
  {noreply_lane}
</div>

<div class="toast" id="toast"></div>

<script>
function toggleLane(header) {{
  const body = header.nextElementSibling;
  const caret = header.querySelector('.lane-caret');
  const hidden = body.style.display === 'none';
  body.style.display = hidden ? '' : 'none';
  caret.textContent = hidden ? '▾' : '▸';
}}

function filterType(type, btn) {{
  document.querySelectorAll('.fchip').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.kcard').forEach(card => {{
    card.style.display = (type === 'all' || card.dataset.type === type) ? '' : 'none';
  }});
}}

async function updateStatus(jobId, status) {{
  const resp = await fetch(`/api/jobs/${{jobId}}/status`, {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ status }})
  }});
  if (resp.ok) {{
    showToast(`→ ${{status.replace(/_/g, ' ')}}`);
    setTimeout(() => location.reload(), 800);
  }}
}}

async function triggerRefresh() {{
  if (!confirm('Run discovery agent? (~3–5 min)')) return;
  showToast('Running…');
  const resp = await fetch('/api/jobs/refresh', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ confirmed: true }})
  }});
  const data = await resp.json();
  showToast(`Found ${{data.jobs_found}} jobs`);
  setTimeout(() => location.reload(), 2000);
}}

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
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
