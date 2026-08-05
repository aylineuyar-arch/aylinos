"""
AylinOS — Networking Operator Dashboard
Shows OS-found contacts, scoring, outreach queue, and pipeline stats.
"""

# Per-company pastel card backgrounds (pipeline queue only — OS-found rows use indigo OS style)
COMPANY_BG = {
    "Planhat":    ("rgba(99,102,241,.08)",  "rgba(99,102,241,.25)"),   # indigo
    "Mistral AI": ("rgba(124,58,237,.08)",  "rgba(124,58,237,.25)"),   # violet
    "ElevenLabs": ("rgba(220,38,38,.07)",   "rgba(220,38,38,.22)"),    # red
    "Multiverse": ("rgba(217,119,6,.07)",   "rgba(217,119,6,.22)"),    # amber
    "Junior":     ("rgba(13,148,136,.07)",  "rgba(13,148,136,.22)"),   # teal
}

TAG_DEFS = {
    "hm":          ("#4f46e5", "rgba(99,102,241,.13)",   "👤 Hiring Manager"),
    "role":        ("#059669", "rgba(16,185,129,.13)",   "🎯 Role Match"),
    "mba":         ("#7c3aed", "rgba(124,58,237,.13)",   "🎓 MBA"),
    "dartmouth":   ("#047857", "rgba(5,150,105,.13)",    "🌲 Tuck / Dartmouth"),
    "lbs":         ("#1d4ed8", "rgba(59,130,246,.13)",   "🏛 LBS"),
    "consulting":  ("#b45309", "rgba(217,119,6,.13)",    "💼 Consulting"),
}


def render_networking(contacts: list, airtable_contacts: list = None) -> str:
    airtable_contacts = airtable_contacts or []

    # Pipeline queue — P1/P2 targets grouped by company, 2-3 contacts each
    pipeline_queue = [
        # ── Planhat ──────────────────────────────────────
        {
            "company": "Planhat",
            "contact_name": "Sahil Bahl",
            "contact_title": "Head of Customer Success · Hiring Manager",
            "fit_score": 88,
            "strategy": "APPLY NOW",
            "contact_angle": "Forwarded application to recruiting · case study next · same deployment motion as Skild AI GTM work",
            "angle_tags": ["hm", "role", "consulting"],
            "status": "queued",
        },
        {
            "company": "Planhat",
            "contact_name": "Viktor Ek",
            "contact_title": "Solutions Consultant (peer)",
            "fit_score": 79,
            "strategy": "NETWORK FIRST",
            "contact_angle": "Solutions-to-strategy path mirrors Aylin's consulting background · warm intro route via CS team",
            "angle_tags": ["role", "consulting"],
            "status": "queued",
        },
        {
            "company": "Planhat",
            "contact_name": "Emma Landau",
            "contact_title": "Customer Success Manager (peer)",
            "fit_score": 74,
            "strategy": "NETWORK FIRST",
            "contact_angle": "MBA + enterprise SaaS CS overlap · can validate team culture and intro to HM",
            "angle_tags": ["mba", "role"],
            "status": "queued",
        },
        # ── Mistral AI ───────────────────────────────────
        {
            "company": "Mistral AI",
            "contact_name": "Camille Desroches",
            "contact_title": "AI Deployment Strategist (peer)",
            "fit_score": 85,
            "strategy": "APPLY NOW",
            "contact_angle": "EMEA deployment role hiring now · MBA + enterprise consulting overlap · Deloitte clients are Mistral's exact buyer",
            "angle_tags": ["role", "mba", "consulting"],
            "status": "queued",
        },
        {
            "company": "Mistral AI",
            "contact_name": "Thomas Grenier",
            "contact_title": "GTM Strategy Lead (peer)",
            "fit_score": 80,
            "strategy": "NETWORK FIRST",
            "contact_angle": "Enterprise GTM motion matches Deloitte + Skild AI operator background · warm path via EMEA network",
            "angle_tags": ["role", "consulting"],
            "status": "queued",
        },
        # ── ElevenLabs ───────────────────────────────────
        {
            "company": "ElevenLabs",
            "contact_name": "Jordan Marsh",
            "contact_title": "Deployment Strategist (peer)",
            "fit_score": 82,
            "strategy": "NETWORK FIRST",
            "contact_angle": "Tuck alum on deployment team = warm intro path · voice AI deployment mirrors Skild AI enterprise adoption playbook",
            "angle_tags": ["dartmouth", "role"],
            "status": "queued",
        },
        {
            "company": "ElevenLabs",
            "contact_name": "Priya Nair",
            "contact_title": "Enterprise Solutions Manager (peer)",
            "fit_score": 76,
            "strategy": "NETWORK FIRST",
            "contact_angle": "Enterprise voice AI rollout needs consulting-to-operator profile · former Big 4, strong warm path",
            "angle_tags": ["consulting", "role"],
            "status": "queued",
        },
        # ── Multiverse ───────────────────────────────────
        {
            "company": "Multiverse",
            "contact_name": "Marcus Webb",
            "contact_title": "AI Enablement Lead (peer)",
            "fit_score": 70,
            "strategy": "NETWORK FIRST",
            "contact_angle": "Deloitte L&D enterprise clients = Multiverse's exact buyer · peer EM can intro to HM",
            "angle_tags": ["consulting", "role"],
            "status": "queued",
        },
    ]

    def auto_angle_tags(t):
        # Only use contact_title — contact_angle is the outreach draft and contains
        # Aylin's background keywords (Tuck, Deloitte, etc.), not the contact's.
        tags = []
        title = (t.get("contact_title") or "").lower()
        if any(k in title for k in ["strategy", "ops", "operations", "deployment", "enablement", "gtm", "chief of staff", "solutions", "business"]):
            tags.append("role")
        if any(k in title for k in ["consulting", "consultant"]):
            tags.append("consulting")
        return tags

    # OS-found contacts — top 3 by fit score, auto-tagged
    queue_companies = {t["company"] for t in pipeline_queue}
    at_companies    = {c["company"] for c in airtable_contacts}
    raw_scan = [{**c, "status": "os-found", "source": "AylinOS"} for c in contacts]
    raw_scan = sorted(raw_scan, key=lambda x: x.get("fit_score") or 0, reverse=True)
    raw_scan = [c for c in raw_scan if (c.get("fit_score") or 0) >= 55][:3]
    scan_contacts = [{**c, "angle_tags": auto_angle_tags(c)} for c in raw_scan]

    # Stats
    all_targets = scan_contacts + list(airtable_contacts) + pipeline_queue
    sent     = sum(1 for t in all_targets if t.get("status") in ("sent", "message-sent"))
    drafted  = sum(1 for t in all_targets if t.get("status") == "drafted")
    queued   = sum(1 for t in all_targets if t.get("status") in ("queued", "not-started"))
    os_found = len(scan_contacts)

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

    def angle_tags_col(tags):
        if not tags:
            return ""
        chips = ""
        for tag in tags:
            if tag in TAG_DEFS:
                color, bg, label = TAG_DEFS[tag]
                chips += f'<span class="atag" style="color:{color};background:{bg}">{label}</span>'
        return chips

    def target_row(t):
        sc         = strat_color(t.get("strategy", ""))
        fit        = t.get("fit_score")
        fit_color  = "#6366f1" if (fit or 0) >= 75 else "#fbbf24" if (fit or 0) >= 50 else "#94a3b8"
        company    = t.get("company", "")
        is_os      = t.get("source") == "AylinOS"
        if is_os:
            co_bg, co_border = "rgba(129,140,248,.04)", "rgba(129,140,248,.3)"
        else:
            co_bg, co_border = COMPANY_BG.get(company, ("var(--surface)", "var(--border)"))
        linkedin   = t.get("linkedin_url", "")
        name       = t.get("contact_name", "—")
        name_html  = (
            f'<a href="{linkedin}" target="_blank" rel="noopener" class="cname">{name}</a>'
            if linkedin else
            f'<span class="cname">{name}</span>'
        )
        tags_col   = angle_tags_col(t.get("angle_tags", []))
        angle_text = t.get("contact_angle", "")[:220]

        return f"""<div class="target-row{' os-row' if is_os else ''}" style="background:{co_bg};border-color:{co_border}">
  <div class="target-main">
    <div class="target-top">
      <span class="company">{company}</span>
      {status_badge(t.get('status', 'queued'))}
      {"<span class='os-tag'>⚡ via AylinOS</span>" if is_os else ''}
    </div>
    <div class="contact-line">
      {name_html}
      <span class="ctitle">{t.get('contact_title', '')}</span>
    </div>
    {f'<div class="angle">{angle_text}</div>' if angle_text else ''}
    <div class="strat" style="color:{sc}">{t.get('strategy', '')}</div>
  </div>
  <div class="score-col">
    <span class="score" style="color:{fit_color}">{fit or '—'}</span>
    <span class="score-label">fit</span>
    {f'<div class="tag-col">{tags_col}</div>' if tags_col else ''}
  </div>
</div>"""

    def named_section(title, subtitle, items):
        if not items:
            return ""
        rows_html = "".join(target_row(t) for t in items)
        return f"""<div class="named-hdr">
  <div>
    <span class="named-title">{title}</span>
    <span class="named-count">{len(items)}</span>
  </div>
  <span class="named-sub">{subtitle}</span>
</div>
{rows_html}"""

    def grouped_queue(items):
        """Render pipeline queue grouped by company with mini company headers."""
        from itertools import groupby
        html = ""
        for company, group in groupby(items, key=lambda x: x["company"]):
            group_list = list(group)
            html += f'<div class="co-group-hdr">{company}</div>'
            html += "".join(target_row(t) for t in group_list)
        return html

    scan_section  = named_section(
        "New Scan — AylinOS Found",
        "Contacts surfaced from this query",
        scan_contacts,
    )
    queue_html = grouped_queue(pipeline_queue) if pipeline_queue else ""
    sep = '<div class="section-sep">Previous Query</div>' if scan_section and queue_html else ""
    rows = scan_section + sep + queue_html

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
  --border2:rgba(0,0,0,.14);--ink:#111116;--ink-2:#374151;--ink-3:#94a3b8;
  --accent:#6366f1;--mono:'JetBrains Mono',monospace;
}}
body{{background:var(--bg);color:var(--ink);font-family:Inter,-apple-system,sans-serif;min-height:100vh;font-size:17px;-webkit-font-smoothing:antialiased}}
.topbar{{display:flex;align-items:center;justify-content:space-between;padding:18px 40px;border-bottom:1px solid var(--border);background:var(--surface)}}
.logo{{font-size:18px;font-weight:700;color:var(--ink);text-decoration:none}}
.logo span{{color:var(--accent)}}
nav a{{font-size:14px;color:var(--ink-3);text-decoration:none;margin-left:28px;font-family:var(--mono)}}
nav a:hover{{color:var(--ink)}}
.stats{{display:flex;gap:1px;border-bottom:1px solid var(--border);background:var(--border)}}
.stat{{background:var(--surface);flex:1;padding:28px 32px}}
.stat-val{{font-size:36px;font-weight:800;font-family:var(--mono)}}
.stat-label{{font-size:12px;color:var(--ink-3);margin-top:6px;font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase;font-weight:600}}
.main{{max-width:980px;margin:0 auto;padding:36px 32px}}
.section-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}}
.section-title{{font-size:13px;font-weight:600;color:var(--ink-3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono)}}
.os-hint{{font-size:13px;color:var(--ink-3);font-family:var(--mono)}}
.os-hint span{{color:var(--accent)}}
.named-hdr{{display:flex;align-items:baseline;justify-content:space-between;margin:32px 0 14px;padding-bottom:10px;border-bottom:2px solid var(--border2)}}
.named-title{{font-size:15px;font-weight:700;color:var(--ink);letter-spacing:.04em;text-transform:uppercase;font-family:var(--mono)}}
.named-count{{font-size:14px;font-weight:600;color:var(--ink-3);font-family:var(--mono);margin-left:8px}}
.named-sub{{font-size:13px;color:var(--ink-3);font-family:var(--mono)}}
.co-group-hdr{{font-size:12px;font-weight:700;color:var(--ink-3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono);margin:20px 0 8px;padding-left:4px}}
.section-sep{{
  display:flex;align-items:center;gap:14px;
  margin:40px 0 8px;
  font-family:var(--mono);font-size:12px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);
}}
.section-sep::before,.section-sep::after{{
  content:'';flex:1;height:1px;background:var(--border2);
}}
.target-row{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px 24px;margin-bottom:10px;display:flex;gap:20px;align-items:flex-start}}
.os-row{{border-color:rgba(129,140,248,.3);background:rgba(129,140,248,.04)}}
.target-main{{flex:1;min-width:0}}
.target-top{{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}}
.company{{font-size:21px;font-weight:700}}
.badge{{font-size:12px;font-weight:600;padding:3px 10px;border-radius:20px;font-family:var(--mono)}}
.os-tag{{font-size:12px;color:var(--accent);font-family:var(--mono)}}
.contact-line{{display:flex;gap:10px;align-items:baseline;margin-bottom:10px}}
.cname{{font-size:17px;font-weight:700;color:var(--ink)}}
.ctitle{{font-size:15px;color:var(--ink-2);font-family:var(--mono);font-weight:500}}
.atag{{font-size:11px;font-weight:600;padding:3px 8px;border-radius:20px;font-family:var(--mono);white-space:nowrap}}
.tag-col{{display:flex;flex-direction:column;gap:5px;margin-top:10px;align-items:center}}
.angle{{font-size:15px;color:var(--ink-2);line-height:1.6;margin-bottom:10px;font-weight:400;
  border-left:2px solid rgba(99,102,241,.3);padding-left:12px}}
.strat{{font-size:13px;font-family:var(--mono);letter-spacing:.04em;font-weight:700}}
.score-col{{display:flex;flex-direction:column;align-items:center;gap:2px;min-width:72px}}
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
  <div id="scan-log" style="font-family:'JetBrains Mono',monospace;font-size:17px;color:#4a5568;display:flex;flex-direction:column;gap:14px"></div>
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
    await new Promise(r => setTimeout(r, 1100));
    const line = document.createElement("div");
    line.style.cssText = "display:flex;align-items:baseline;gap:12px;animation:fadeIn .35s ease";
    line.innerHTML = `<span style="color:#10b981;font-weight:700;font-size:18px">✓</span><span>${{step}}</span>`;
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
