"""
AylinOS — Networking Operator Dashboard
Shows OS-found contacts, scoring, outreach queue, and pipeline stats.
"""


def render_networking(contacts: list, airtable_contacts: list = None) -> str:
    airtable_contacts = airtable_contacts or []
    # Seed demo targets if no OS-found contacts yet
    demo_targets = [
        {"company": "Ramp", "contact_name": "Geoff Charles", "contact_title": "VP Product", "fit_score": 88,
         "strategy": "APPLY NOW", "contact_angle": "Lead with Jolt AI acquisition and what it signals about their AI roadmap", "status": "queued"},
        {"company": "Hebbia", "contact_name": "Alex Gould", "contact_title": "Head of GTM", "fit_score": 85,
         "strategy": "NETWORK FIRST", "contact_angle": "Reference the AI Strategist role and your Skild AI GTM experience for novel AI categories", "status": "drafted"},
        {"company": "Scale AI", "contact_name": "Tom Rogan", "contact_title": "Chief of Staff", "fit_score": 82,
         "strategy": "APPLY NOW", "contact_angle": "Deloitte enterprise background + Skild AI maps directly to Scale's enterprise GTM push", "status": "sent"},
        {"company": "Anthropic", "contact_name": "Hiring Team", "contact_title": "Strategy & Ops", "fit_score": 79,
         "strategy": "NETWORK FIRST", "contact_angle": "Reference published safety research and connect through Tuck alumni network", "status": "queued"},
        {"company": "Glean", "contact_name": "Ali Morshed", "contact_title": "Head of Strategy", "fit_score": 76,
         "strategy": "NETWORK FIRST", "contact_angle": "Enterprise AI deployment angle — Deloitte clients are Glean's exact buyer profile", "status": "queued"},
        {"company": "Cursor", "contact_name": "Michael Truell", "contact_title": "CEO", "fit_score": 74,
         "strategy": "RESEARCH MORE", "contact_angle": "GTM motion for developer tools — reference bottoms-up growth question", "status": "researching"},
    ]

    # Merge: OS-found first, then Airtable, then demo seeds
    all_targets = []
    os_companies = {c["company"] for c in contacts}
    at_companies = {c["company"] for c in airtable_contacts}

    for c in contacts:
        all_targets.append({**c, "status": "os-found", "source": "AylinOS"})
    for c in airtable_contacts:
        all_targets.append({**c})
    for t in demo_targets:
        if t["company"] not in os_companies and t["company"] not in at_companies:
            all_targets.append({**t, "source": "seed"})

    def status_badge(status):
        colors = {
            "os-found":        ("#818cf8", "rgba(129,140,248,0.12)", "⚡ OS Found"),
            "sent":            ("#34d399", "rgba(52,211,153,0.12)",  "✓ Sent"),
            "message-sent":    ("#34d399", "rgba(52,211,153,0.12)",  "✓ Sent"),
            "responded":       ("#34d399", "rgba(52,211,153,0.12)",  "✓ Responded"),
            "call-scheduled":  ("#34d399", "rgba(52,211,153,0.12)",  "✓ Call Scheduled"),
            "drafted":         ("#fbbf24", "rgba(251,191,36,0.12)",  "✎ Drafted"),
            "connected":       ("#fbbf24", "rgba(251,191,36,0.12)",  "✓ Connected"),
            "queued":          ("#60a5fa", "rgba(96,165,250,0.12)",  "◎ Queued"),
            "not-started":     ("#60a5fa", "rgba(96,165,250,0.12)",  "◎ Queued"),
            "connection-sent": ("#60a5fa", "rgba(96,165,250,0.12)",  "↑ Sent Request"),
            "researching":     ("#f472b6", "rgba(244,114,182,0.12)", "⟳ Researching"),
        }
        color, bg, label = colors.get(status, ("#9ca3af", "rgba(156,163,175,0.1)", status))
        return f'<span class="badge" style="color:{color};background:{bg}">{label}</span>'

    def strat_color(s):
        if "APPLY NOW" in s: return "#34d399"
        if "NETWORK" in s: return "#60a5fa"
        if "RESEARCH" in s: return "#f472b6"
        return "#9ca3af"

    def target_row(t):
        sc = strat_color(t.get("strategy", ""))
        return f"""<div class="target-row {'os-row' if t.get('source')=='AylinOS' else ''}">
  <div class="target-main">
    <div class="target-top">
      <span class="company">{t['company']}</span>
      {status_badge(t.get('status','queued'))}
      {"<span class='os-tag'>⚡ via AylinOS</span>" if t.get('source')=='AylinOS' else ''}
    </div>
    <div class="contact-line">
      <span class="cname">{t.get('contact_name','—')}</span>
      <span class="ctitle">{t.get('contact_title','')}</span>
    </div>
    <div class="angle">{t.get('contact_angle','')[:140]}</div>
    <div class="strat" style="color:{sc}">{t.get('strategy','')}</div>
  </div>
  <div class="score-col">
    <span class="score" style="color:{sc}">{t.get('fit_score') or '—'}</span>
    <span class="score-label">fit</span>
  </div>
</div>"""

    rows = "".join(target_row(t) for t in all_targets)
    sent  = sum(1 for t in all_targets if t.get("status") == "sent")
    drafted = sum(1 for t in all_targets if t.get("status") == "drafted")
    queued  = sum(1 for t in all_targets if t.get("status") == "queued")
    os_found = sum(1 for t in all_targets if t.get("source") == "AylinOS")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AylinOS · Networking</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#f8f7f4;--surface:#ffffff;--border:rgba(0,0,0,.08);
  --border2:rgba(0,0,0,.14);--ink:#111116;--ink-2:#4a5568;--ink-3:#94a3b8;
  --accent:#6366f1;--mono:'JetBrains Mono',monospace;
}}
body{{background:var(--bg);color:var(--ink);font-family:Inter,-apple-system,sans-serif;min-height:100vh}}
.topbar{{display:flex;align-items:center;justify-content:space-between;padding:14px 32px;border-bottom:1px solid var(--border);}}
.logo{{font-size:13px;font-weight:600;color:var(--ink);text-decoration:none;}}
.logo span{{color:var(--accent)}}
nav a{{font-size:12px;color:var(--ink-3);text-decoration:none;margin-left:20px;font-family:var(--mono)}}
nav a:hover{{color:var(--ink)}}
.stats{{display:flex;gap:1px;border-bottom:1px solid var(--border);background:var(--border)}}
.stat{{background:var(--surface);flex:1;padding:20px 24px;}}
.topbar{{background:var(--surface);border-bottom:1px solid var(--border);}}

.main{{max-width:860px;margin:0 auto;padding:28px 24px}}
.section-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}}
.section-title{{font-size:11px;font-weight:500;color:var(--ink-3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono)}}
.os-hint{{font-size:11px;color:var(--ink-3);font-family:var(--mono)}}
.os-hint span{{color:var(--accent)}}
.target-row{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px;margin-bottom:8px;display:flex;gap:16px;align-items:flex-start}}
.os-row{{border-color:rgba(129,140,248,.3);background:rgba(129,140,248,.04)}}
.target-main{{flex:1;min-width:0}}
.target-top{{display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap}}

.badge{{font-size:10px;font-weight:500;padding:2px 8px;border-radius:20px;font-family:var(--mono)}}
.os-tag{{font-size:10px;color:var(--accent);font-family:var(--mono)}}
.contact-line{{display:flex;gap:8px;align-items:baseline;margin-bottom:6px}}

.angle{{font-size:12px;color:var(--ink-2);line-height:1.6;margin-bottom:6px;font-weight:500}}
.strat{{font-size:10px;font-family:var(--mono);letter-spacing:.04em;font-weight:600}}
.company{{font-size:14px;font-weight:700;color:var(--ink)}}
.cname{{font-size:13px;font-weight:700;color:#6366f1}}
.ctitle{{font-size:11px;color:var(--ink-3);font-family:var(--mono);font-weight:500}}
.stat-val{{font-size:28px;font-weight:800;font-family:var(--mono)}}
.stat-label{{font-size:11px;color:var(--ink-3);margin-top:4px;font-family:var(--mono);letter-spacing:.04em;text-transform:uppercase;font-weight:600}}
.score-col{{display:flex;flex-direction:column;align-items:center;gap:2px;min-width:40px}}
.score{{font-size:22px;font-weight:700;font-family:var(--mono)}}
.score-label{{font-size:9px;color:var(--ink-3);font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase}}
.empty{{text-align:center;padding:40px;color:var(--ink-3);font-family:var(--mono);font-size:12px}}
</style>
</head>
<body>
<div class="topbar">
  <a href="/" class="logo">Aylin<span>OS</span></a>
  <nav>
    <a href="/job-search">Pipeline</a>
    <a href="/networking" style="color:var(--ink)">Networking</a>
    <a href="/evals">Evals</a>
  </nav>
</div>

<div class="stats">
  <div class="stat">
    <div class="stat-val">{len(all_targets)}</div>
    <div class="stat-label">Targets</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#818cf8">{os_found}</div>
    <div class="stat-label">OS Found</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#34d399">{sent}</div>
    <div class="stat-label">Sent</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#fbbf24">{drafted}</div>
    <div class="stat-label">Drafted</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#60a5fa">{queued}</div>
    <div class="stat-label">Queued</div>
  </div>
</div>

<div class="main">
  <div class="section-header">
    <span class="section-title">Outreach Targets</span>
    <span class="os-hint">Ask the OS <span>"should I apply to [company]?"</span> to add contacts</span>
  </div>
  {rows if rows else '<div class="empty">No targets yet — query the OS to populate</div>'}
</div>
</body>
</html>"""
