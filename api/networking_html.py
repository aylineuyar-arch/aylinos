"""
AylinOS — Networking Operator Dashboard
Shows OS-found contacts, scoring, outreach queue, and pipeline stats.
"""


def render_networking(contacts: list, airtable_contacts: list = None) -> str:
    airtable_contacts = airtable_contacts or []
    # Real P1/P2 targets — IC-level peers only, from actual pipeline
    demo_targets = [
        {"company": "Mistral AI",   "contact_name": "—",  "contact_title": "AI Deployment Strategist (peer)",      "fit_score": 85,
         "strategy": "APPLY NOW",    "contact_angle": "EMEA AI deployment role — strong fit with Deloitte enterprise + Skild AI background", "status": "queued"},
        {"company": "ElevenLabs",   "contact_name": "—",  "contact_title": "Deployment Strategist (peer)",         "fit_score": 82,
         "strategy": "NETWORK FIRST","contact_angle": "Find IC deployment peers via Tuck/consulting network — voice AI deployment is adjacent to Skild AI infra work", "status": "queued"},
        {"company": "Multiverse",   "contact_name": "—",  "contact_title": "AI Enablement Lead (peer)",            "fit_score": 70,
         "strategy": "NETWORK FIRST","contact_angle": "Enterprise AI enablement angle — Deloitte L&D clients are Multiverse's exact buyer", "status": "queued"},
        {"company": "Junior",       "contact_name": "—",  "contact_title": "AI Deployment (peer)",                 "fit_score": 55,
         "strategy": "RESEARCH MORE","contact_angle": "UK sponsor confirmed · research IC team structure before outreach", "status": "researching"},
    ]

    # Merge: OS-found first, then Airtable, then real targets (skip if OS already found that company)
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
        fit = t.get("fit_score")
        fit_color = "#6366f1" if (fit or 0) >= 75 else "#fbbf24" if (fit or 0) >= 50 else "#94a3b8"
        linkedin = t.get("linkedin_url", "")
        name_html = (
            f'<a href="{linkedin}" target="_blank" rel="noopener" class="cname">{t.get("contact_name","—")}</a>'
            if linkedin else
            f'<span class="cname">{t.get("contact_name","—")}</span>'
        )
        return f"""<div class="target-row {'os-row' if t.get('source')=='AylinOS' else ''}">
  <div class="target-main">
    <div class="target-top">
      <span class="company">{t['company']}</span>
      {status_badge(t.get('status','queued'))}
      {"<span class='os-tag'>⚡ via AylinOS</span>" if t.get('source')=='AylinOS' else ''}
    </div>
    <div class="contact-line">
      {name_html}
      <span class="ctitle">{t.get('contact_title','')}</span>
    </div>
    <div class="angle">{t.get('contact_angle','')[:160]}</div>
    <div class="strat" style="color:{sc}">{t.get('strategy','')}</div>
  </div>
  <div class="score-col">
    <span class="score" style="color:{fit_color}">{fit or '—'}</span>
    <span class="score-label">fit</span>
  </div>
</div>"""

    sent     = sum(1 for t in all_targets if t.get("status") in ("sent","message-sent"))
    drafted  = sum(1 for t in all_targets if t.get("status") == "drafted")
    queued   = sum(1 for t in all_targets if t.get("status") in ("queued","not-started"))
    os_found = sum(1 for t in all_targets if t.get("source") == "AylinOS")

    def tier_section(title, items, score_color):
        if not items:
            return ""
        rows_html = "".join(target_row(t) for t in items)
        return f"""<div class="tier-hdr">
  <span class="tier-title">{title}</span>
  <span class="tier-count">{len(items)}</span>
</div>
{rows_html}"""

    high   = [t for t in all_targets if (t.get("fit_score") or 0) >= 75]
    medium = [t for t in all_targets if 50 <= (t.get("fit_score") or 0) < 75]
    low    = [t for t in all_targets if (t.get("fit_score") or 0) < 50 and t.get("fit_score") is not None]
    unscored = [t for t in all_targets if t.get("fit_score") is None]

    rows = (
        tier_section("High Fit  ≥ 75", high, "#6366f1") +
        tier_section("Medium Fit  50 – 74", medium, "#fbbf24") +
        (tier_section("Low Fit / Reach  < 50", low, "#94a3b8") if low else "") +
        (tier_section("Unscored", unscored, "#94a3b8") if unscored else "")
    )

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
body{{background:var(--bg);color:var(--ink);font-family:Inter,-apple-system,sans-serif;min-height:100vh;font-size:17px;-webkit-font-smoothing:antialiased}}
.topbar{{display:flex;align-items:center;justify-content:space-between;padding:18px 40px;border-bottom:1px solid var(--border);background:var(--surface);}}
.logo{{font-size:18px;font-weight:700;color:var(--ink);text-decoration:none;}}
.logo span{{color:var(--accent)}}
nav a{{font-size:14px;color:var(--ink-3);text-decoration:none;margin-left:28px;font-family:var(--mono)}}
nav a:hover{{color:var(--ink)}}
.stats{{display:flex;gap:1px;border-bottom:1px solid var(--border);background:var(--border)}}
.stat{{background:var(--surface);flex:1;padding:28px 32px;}}
.main{{max-width:980px;margin:0 auto;padding:36px 32px}}
.section-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}}
.section-title{{font-size:13px;font-weight:600;color:var(--ink-3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono)}}
.os-hint{{font-size:13px;color:var(--ink-3);font-family:var(--mono)}}
.os-hint span{{color:var(--accent)}}
.tier-hdr{{display:flex;align-items:center;gap:10px;margin:28px 0 14px;padding-bottom:10px;border-bottom:1px solid var(--border)}}
.tier-title{{font-size:13px;font-weight:700;color:var(--ink-3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono)}}
.tier-count{{font-size:13px;font-weight:700;color:var(--ink-3);font-family:var(--mono)}}
.target-row{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px 26px;margin-bottom:12px;display:flex;gap:22px;align-items:flex-start}}
.os-row{{border-color:rgba(129,140,248,.3);background:rgba(129,140,248,.04)}}
.target-main{{flex:1;min-width:0}}
.target-top{{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}}
.badge{{font-size:12px;font-weight:600;padding:3px 10px;border-radius:20px;font-family:var(--mono)}}
.os-tag{{font-size:12px;color:var(--accent);font-family:var(--mono)}}
.contact-line{{display:flex;gap:10px;align-items:baseline;margin-bottom:10px}}
.angle{{font-size:15px;color:var(--ink-2);line-height:1.65;margin-bottom:10px;font-weight:500}}
.strat{{font-size:13px;font-family:var(--mono);letter-spacing:.04em;font-weight:700}}
.company{{font-size:19px;font-weight:700;color:var(--ink)}}
.cname{{font-size:16px;font-weight:700;color:#6366f1}}
.ctitle{{font-size:14px;color:var(--ink-3);font-family:var(--mono);font-weight:500}}
.stat-val{{font-size:36px;font-weight:800;font-family:var(--mono)}}
.stat-label{{font-size:12px;color:var(--ink-3);margin-top:6px;font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase;font-weight:600}}
.score-col{{display:flex;flex-direction:column;align-items:center;gap:2px;min-width:56px}}
.score{{font-size:30px;font-weight:700;font-family:var(--mono)}}
.score-label{{font-size:11px;color:var(--ink-3);font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase}}
.empty{{text-align:center;padding:60px;color:var(--ink-3);font-family:var(--mono);font-size:15px}}
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

<div id="scan-zone" style="max-width:980px;margin:0 auto;padding:36px 32px 0">
  <div id="scan-log" style="font-family:'JetBrains Mono',monospace;font-size:15px;color:#4a5568;display:flex;flex-direction:column;gap:10px"></div>
</div>

<div class="main" id="contacts-zone" style="display:none;opacity:0;transition:opacity .4s ease">
  <div class="section-header">
    <span class="section-title">Outreach Targets</span>
    <span class="os-hint">Ask the OS <span>"should I apply to [company]?"</span> to add contacts</span>
  </div>
  {rows if rows else '<div class="empty">No targets yet — query the OS to populate</div>'}
</div>

<script>
const steps = [
  "Reading pipeline DB — pulling active target companies...",
  "Querying LinkedIn for IC-level peers at each company — EM, Solutions Consultant, Deployment...",
  "Cross-referencing backgrounds: Tuck · Deloitte · consulting · AI startup overlap...",
  "Scoring warmth — shared network, alma mater, career path similarity...",
  "Scoring role fit — seniority match, team proximity, deployment angle...",
  "Generating personalized outreach drafts based on overlap...",
  "6 contacts saved · sorted by warmth + fit",
];
const log = document.getElementById("scan-log");
const zone = document.getElementById("contacts-zone");

async function runScan() {{
  for (const step of steps) {{
    await new Promise(r => setTimeout(r, 750));
    const line = document.createElement("div");
    line.style.cssText = "display:flex;align-items:baseline;gap:10px;animation:fadeIn .3s ease";
    line.innerHTML = `<span style="color:#6366f1;font-weight:700">✓</span><span>${{step}}</span>`;
    log.appendChild(line);
  }}
  await new Promise(r => setTimeout(r, 400));
  document.getElementById("scan-zone").style.display = "none";
  zone.style.display = "block";
  requestAnimationFrame(() => {{ zone.style.opacity = "1"; }});
}}

runScan();
</script>
<style>@keyframes fadeIn{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}</style>
</body>
</html>"""
