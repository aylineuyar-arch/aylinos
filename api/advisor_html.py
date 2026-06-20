"""
AylinOS — Career Intelligence Advisor Page
-------------------------------------------
Renders the /advisor page: a shareable, no-auth intelligence brief tool.
"""


def render_advisor() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Career Intelligence — AylinOS</title>
<meta name="description" content="Personalized career intelligence for Aylin Uyar. Enter any company to get fit score, strategy, AI angle, and outreach advice."/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:'Inter',system-ui,sans-serif;
  background:#0c0c10;
  min-height:100vh;
  color:#e8e8ed;
  -webkit-font-smoothing:antialiased;
}
a{color:inherit;text-decoration:none}

/* Layout */
.page{max-width:720px;margin:0 auto;padding:40px 24px 80px}

/* Back link */
.back{
  font-family:'JetBrains Mono',monospace;
  font-size:11px;color:rgba(232,232,237,0.32);
  display:inline-flex;align-items:center;gap:6px;
  margin-bottom:48px;transition:color 150ms;
}
.back:hover{color:rgba(232,232,237,0.7)}

/* Header */
.header{margin-bottom:32px}
.header h1{
  font-size:28px;font-weight:600;
  letter-spacing:-0.03em;
  color:#e8e8ed;
  margin-bottom:8px;
}
.header p{
  font-size:13px;color:rgba(232,232,237,0.45);
  line-height:1.65;max-width:54ch;
}

/* Profile strip */
.profile-strip{
  display:flex;flex-wrap:wrap;gap:8px;
  margin-bottom:36px;
  padding:14px 18px;
  background:#111116;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:10px;
  align-items:center;
}
.profile-stat{
  font-family:'JetBrains Mono',monospace;
  font-size:11px;
  color:rgba(232,232,237,0.5);
  letter-spacing:0.02em;
}
.profile-dot{
  color:rgba(255,255,255,0.15);
  font-size:10px;
}

/* Input section */
.input-row{
  display:flex;gap:10px;
  margin-bottom:36px;
}
.company-input{
  flex:1;
  background:#111116;
  border:1px solid rgba(255,255,255,0.1);
  border-radius:8px;
  padding:13px 16px;
  font-family:'Inter',sans-serif;
  font-size:14px;
  color:#e8e8ed;
  outline:none;
  transition:border-color 150ms;
}
.company-input::placeholder{color:rgba(232,232,237,0.25)}
.company-input:focus{border-color:rgba(255,255,255,0.25)}
.analyze-btn{
  background:#e8e8ed;
  color:#0c0c10;
  border:none;
  border-radius:8px;
  padding:13px 22px;
  font-family:'Inter',sans-serif;
  font-size:13px;
  font-weight:600;
  cursor:pointer;
  white-space:nowrap;
  transition:opacity 150ms;
}
.analyze-btn:hover{opacity:0.88}
.analyze-btn:disabled{opacity:0.4;cursor:not-allowed}

/* Loading state */
.loading{
  display:none;
  padding:28px 0;
  text-align:center;
}
.loading.active{display:block}
.loading-steps{
  font-family:'JetBrains Mono',monospace;
  font-size:12px;
  color:rgba(232,232,237,0.4);
  display:flex;flex-direction:column;align-items:center;gap:10px;
}
.loading-step{
  opacity:0;transition:opacity 400ms;
  display:flex;align-items:center;gap:8px;
}
.loading-step.visible{opacity:1}
.spinner{
  width:14px;height:14px;
  border:1.5px solid rgba(232,232,237,0.15);
  border-top-color:rgba(232,232,237,0.6);
  border-radius:50%;
  animation:spin 0.8s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}

/* Error */
.error-msg{
  display:none;
  padding:14px 18px;
  background:rgba(239,68,68,0.08);
  border:1px solid rgba(239,68,68,0.2);
  border-radius:8px;
  font-size:13px;
  color:rgba(239,68,68,0.85);
  margin-bottom:24px;
}
.error-msg.active{display:block}

/* Results */
.results{display:none}
.results.active{display:block}

/* Company title in results */
.results-header{
  display:flex;align-items:baseline;gap:16px;
  margin-bottom:28px;
  padding-bottom:20px;
  border-bottom:1px solid rgba(255,255,255,0.07);
}
.results-company{
  font-size:20px;font-weight:600;letter-spacing:-0.02em;
  color:#e8e8ed;
}
.results-label{
  font-family:'JetBrains Mono',monospace;
  font-size:10px;
  color:rgba(232,232,237,0.28);
  text-transform:uppercase;
  letter-spacing:0.08em;
}

/* Fit score */
.score-row{
  display:flex;align-items:center;gap:20px;
  margin-bottom:28px;
}
.score-number{
  font-size:52px;font-weight:600;letter-spacing:-0.04em;
  line-height:1;
  font-variant-numeric:tabular-nums;
}
.score-green{color:#34d399}
.score-orange{color:#fbbf24}
.score-red{color:#f87171}
.score-meta{display:flex;flex-direction:column;gap:4px}
.score-label{
  font-family:'JetBrains Mono',monospace;
  font-size:10px;
  color:rgba(232,232,237,0.28);
  text-transform:uppercase;letter-spacing:0.08em;
}
.score-desc{font-size:13px;color:rgba(232,232,237,0.55)}

/* Strategy badge */
.strategy-badge{
  display:inline-block;
  padding:5px 12px;
  border-radius:5px;
  font-family:'JetBrains Mono',monospace;
  font-size:11px;
  font-weight:500;
  text-transform:uppercase;
  letter-spacing:0.06em;
  margin-bottom:8px;
}
.badge-apply{background:rgba(52,211,153,0.12);color:#34d399;border:1px solid rgba(52,211,153,0.25)}
.badge-network{background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.2)}
.badge-research{background:rgba(96,165,250,0.1);color:#60a5fa;border:1px solid rgba(96,165,250,0.2)}
.badge-skip{background:rgba(248,113,113,0.1);color:#f87171;border:1px solid rgba(248,113,113,0.2)}

/* Intelligence sections */
.intel-section{
  margin-bottom:20px;
  padding:20px 22px;
  background:#111116;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:10px;
}
.intel-label{
  font-family:'JetBrains Mono',monospace;
  font-size:10px;
  color:rgba(232,232,237,0.28);
  text-transform:uppercase;
  letter-spacing:0.08em;
  margin-bottom:10px;
}
.intel-value{
  font-size:14px;
  color:rgba(232,232,237,0.8);
  line-height:1.65;
}

/* Outreach section */
.outreach-block{
  margin-bottom:20px;
  padding:20px 22px;
  background:#111116;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:10px;
}
.outreach-target{
  font-size:15px;font-weight:500;
  color:#e8e8ed;
  margin-bottom:10px;
}
.outreach-hook{
  font-size:13px;
  color:rgba(232,232,237,0.55);
  line-height:1.6;
  font-style:italic;
}

/* Open roles */
.roles-list{
  display:flex;flex-wrap:wrap;gap:7px;
  margin-top:10px;
}
.role-tag{
  font-family:'JetBrains Mono',monospace;
  font-size:11px;
  padding:4px 10px;
  border-radius:4px;
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.08);
  color:rgba(232,232,237,0.5);
}

/* Verdict */
.verdict-block{
  margin-bottom:0;
  padding:20px 22px;
  background:#111116;
  border:1px solid rgba(255,255,255,0.1);
  border-radius:10px;
  border-left:3px solid rgba(232,232,237,0.2);
}
.verdict-text{
  font-size:14px;font-weight:500;
  color:#e8e8ed;
  line-height:1.6;
}

/* Divider between sections */
.section-divider{height:1px;background:rgba(255,255,255,0.05);margin:8px 0}
</style>
</head>
<body>
<div class="page">

  <!-- Back -->
  <a href="/" class="back">← AylinOS</a>

  <!-- Header -->
  <div class="header">
    <h1>Career Intelligence</h1>
    <p>Enter any company to get a personalized fit analysis for Aylin Uyar — strategy, AI angle, outreach target, and verdict. Built for recruiters, collaborators, and Aylin herself.</p>
  </div>

  <!-- Profile strip -->
  <div class="profile-strip">
    <span class="profile-stat">Tuck MBA 2026</span>
    <span class="profile-dot">·</span>
    <span class="profile-stat">Deloitte → Skild AI</span>
    <span class="profile-dot">·</span>
    <span class="profile-stat">AI Strategist · GTM · Chief of Staff</span>
    <span class="profile-dot">·</span>
    <span class="profile-stat">NYC / London</span>
  </div>

  <!-- Input -->
  <div class="input-row">
    <input
      type="text"
      class="company-input"
      id="companyInput"
      placeholder="Enter a company name — Ramp, Hebbia, Anthropic..."
      autocomplete="off"
      spellcheck="false"
    />
    <button class="analyze-btn" id="analyzeBtn" onclick="analyze()">Analyze</button>
  </div>

  <!-- Loading -->
  <div class="loading" id="loadingBlock">
    <div class="loading-steps">
      <div class="loading-step" id="step1">
        <div class="spinner"></div>
        <span id="step1text">Searching company...</span>
      </div>
      <div class="loading-step" id="step2">
        <div class="spinner"></div>
        <span>Analyzing fit for Aylin...</span>
      </div>
      <div class="loading-step" id="step3">
        <div class="spinner"></div>
        <span>Generating strategy...</span>
      </div>
    </div>
  </div>

  <!-- Error -->
  <div class="error-msg" id="errorMsg"></div>

  <!-- Results -->
  <div class="results" id="results">
    <!-- Header row -->
    <div class="results-header">
      <div class="results-company" id="r-company"></div>
      <div class="results-label">intelligence brief</div>
    </div>

    <!-- Fit score -->
    <div class="score-row">
      <div class="score-number" id="r-score"></div>
      <div class="score-meta">
        <div class="score-label">Fit Score</div>
        <div class="score-desc" id="r-score-desc"></div>
      </div>
    </div>

    <!-- Strategy -->
    <div class="intel-section">
      <div class="intel-label">Strategy</div>
      <div id="r-strategy-badge" style="margin-bottom:10px"></div>
      <div class="intel-value" id="r-strategy-reason"></div>
    </div>

    <!-- AI angle -->
    <div class="intel-section">
      <div class="intel-label">AI Angle</div>
      <div class="intel-value" id="r-ai-angle"></div>
    </div>

    <!-- Role fit -->
    <div class="intel-section">
      <div class="intel-label">Role Fit for Aylin</div>
      <div class="intel-value" id="r-role-fit"></div>
    </div>

    <!-- Outreach -->
    <div class="outreach-block">
      <div class="intel-label">Outreach</div>
      <div class="outreach-target" id="r-outreach-target"></div>
      <div class="outreach-hook" id="r-outreach-hook"></div>
    </div>

    <!-- Open roles -->
    <div class="intel-section">
      <div class="intel-label">Relevant Roles to Watch</div>
      <div class="roles-list" id="r-open-roles"></div>
    </div>

    <!-- Verdict -->
    <div class="verdict-block">
      <div class="intel-label" style="margin-bottom:8px">Verdict</div>
      <div class="verdict-text" id="r-verdict"></div>
    </div>

  </div><!-- /results -->

</div><!-- /page -->

<script>
const input = document.getElementById('companyInput');
const btn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loadingBlock');
const errorMsg = document.getElementById('errorMsg');
const results = document.getElementById('results');

input.addEventListener('keydown', e => { if (e.key === 'Enter') analyze(); });

// Check URL param on load
window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const co = params.get('company');
  if (co) { input.value = co; analyze(); }
});

function setLoading(active) {
  loading.classList.toggle('active', active);
  btn.disabled = active;
  if (active) {
    results.classList.remove('active');
    errorMsg.classList.remove('active');
    ['step1','step2','step3'].forEach(s => document.getElementById(s).classList.remove('visible'));
  }
}

function showSteps(company) {
  document.getElementById('step1text').textContent = `Searching ${company}...`;
  const delays = [0, 2500, 5000];
  ['step1','step2','step3'].forEach((s, i) => {
    setTimeout(() => {
      document.getElementById(s).classList.add('visible');
    }, delays[i]);
  });
}

function scoreClass(n) {
  if (n >= 70) return 'score-green';
  if (n >= 50) return 'score-orange';
  return 'score-red';
}

function scoreDesc(n) {
  if (n >= 80) return 'Strong match — act fast';
  if (n >= 70) return 'Good match — worth pursuing';
  if (n >= 50) return 'Partial match — worth exploring';
  if (n >= 35) return 'Weak match — verify before investing time';
  return 'Poor fit — deprioritize';
}

function strategyBadge(strategy) {
  const map = {
    apply_now: ['Apply Now', 'badge-apply'],
    network_first: ['Network First', 'badge-network'],
    research_more: ['Research More', 'badge-research'],
    skip: ['Skip', 'badge-skip'],
  };
  const [label, cls] = map[strategy] || ['Unknown', 'badge-research'];
  return `<span class="strategy-badge ${cls}">${label}</span>`;
}

async function analyze() {
  const company = input.value.trim();
  if (!company) { input.focus(); return; }

  // Update URL without reload
  const url = new URL(window.location);
  url.searchParams.set('company', company);
  window.history.replaceState({}, '', url);

  setLoading(true);
  showSteps(company);

  try {
    const resp = await fetch('/api/advisor', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({company, force_refresh: false})
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Server error ${resp.status}: ${err}`);
    }

    const d = await resp.json();
    setLoading(false);
    renderResults(d);

  } catch(e) {
    setLoading(false);
    errorMsg.textContent = e.message || 'Something went wrong. Try again.';
    errorMsg.classList.add('active');
  }
}

function renderResults(d) {
  document.getElementById('r-company').textContent = d.company || '';

  const score = d.fit_score ?? 0;
  const scoreEl = document.getElementById('r-score');
  scoreEl.textContent = score;
  scoreEl.className = 'score-number ' + scoreClass(score);
  document.getElementById('r-score-desc').textContent = scoreDesc(score);

  document.getElementById('r-strategy-badge').innerHTML = strategyBadge(d.strategy);
  document.getElementById('r-strategy-reason').textContent = d.strategy_reason || '';
  document.getElementById('r-ai-angle').textContent = d.ai_angle || '';
  document.getElementById('r-role-fit').textContent = d.role_fit || '';
  document.getElementById('r-outreach-target').textContent = d.outreach_target || '';
  document.getElementById('r-outreach-hook').textContent = d.outreach_hook || '';
  document.getElementById('r-verdict').textContent = d.verdict || '';

  const rolesEl = document.getElementById('r-open-roles');
  rolesEl.innerHTML = '';
  (d.open_roles || []).forEach(role => {
    const span = document.createElement('span');
    span.className = 'role-tag';
    span.textContent = role;
    rolesEl.appendChild(span);
  });

  results.classList.add('active');
  results.scrollIntoView({behavior:'smooth', block:'start'});
}
</script>
</body>
</html>"""
