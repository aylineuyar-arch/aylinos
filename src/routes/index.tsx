import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, type ComponentType } from "react";
import {
  Briefcase,
  UtensilsCrossed,
  Inbox,
  Network,
  Send,
  BarChart3,
  BookOpen,
} from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "AylinOS — Personal AI Operating System" },
      { name: "description", content: "An AI-native home screen for orchestrating personal agents." },
    ],
  }),
  component: Home,
});

type App = {
  id: string;
  name: string;
  tag: string;
  gradient: string;
  accent: string;
  Icon: ComponentType<{ size?: number; strokeWidth?: number; color?: string }>;
};

const APPS: App[] = [
  { id: "job-search", name: "Job Search", tag: "358 tracked",  gradient: "linear-gradient(155deg,#1e1b4b 0%,#4338ca 100%)", accent: "#818cf8", Icon: Briefcase },
  { id: "restaurant", name: "Fork Yeah!", tag: "8-node graph", gradient: "linear-gradient(155deg,#064e3b 0%,#047857 100%)", accent: "#34d399", Icon: UtensilsCrossed },
  { id: "cs-triage",  name: "CS Triage",  tag: "Sub-1s route", gradient: "linear-gradient(155deg,#14532d 0%,#15803d 100%)", accent: "#4ade80", Icon: Inbox },
  { id: "networking", name: "Networking", tag: "130 targets",  gradient: "linear-gradient(155deg,#0c1a3a 0%,#1e40af 100%)", accent: "#60a5fa", Icon: Network },
  { id: "outreach",   name: "Outreach",   tag: "Human-gated",  gradient: "linear-gradient(155deg,#2e1065 0%,#6d28d9 100%)", accent: "#a78bfa", Icon: Send },
  { id: "evals",      name: "Evals",      tag: "v1 → v2",      gradient: "linear-gradient(155deg,#1a0530 0%,#7e22ce 100%)", accent: "#c084fc", Icon: BarChart3 },
  { id: "research",   name: "Research",   tag: "Fan-in brief", gradient: "linear-gradient(155deg,#500724 0%,#be185d 100%)", accent: "#f472b6", Icon: BookOpen },
];



const SUGGESTIONS = [
  { q: "should I apply to Ramp", agent: "Job Search", accent: "#6366f1" },
  { q: "prep me for Hebbia interview", agent: "Job Search", accent: "#6366f1" },
  { q: "book dinner in Soho tomorrow at 8", agent: "Fork Yeah!", accent: "#059669" },
  { q: "draft intro to Sarah at Sequoia", agent: "Outreach", accent: "#7c3aed" },
  { q: "research Cursor's GTM motion", agent: "Research", accent: "#db2777" },
  { q: "triage today's support inbox", agent: "CS Triage", accent: "#16a34a" },
];

const LIVE_TICKER = [
  { dot: "#818cf8", text: "Job Search · polling Greenhouse… 14 new postings" },
  { dot: "#34d399", text: "Fork Yeah! · indexed 38 venues in SoHo for tomorrow" },
  { dot: "#f472b6", text: "Research · Tavily returned 12 sources, distilling…" },
  { dot: "#a78bfa", text: "Outreach · 3 drafts pending your approval" },
  { dot: "#60a5fa", text: "Networking · scored 22 LinkedIn profiles overnight" },
];

function useClock() {
  const [t, setT] = useState(() => {
    const d = new Date();
    return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  });
  useEffect(() => {
    const id = setInterval(() => {
      const d = new Date();
      setT(`${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`);
    }, 15_000);
    return () => clearInterval(id);
  }, []);
  return t;
}

function useGreeting() {
  const h = new Date().getHours();
  if (h < 5) return "Burning the midnight oil";
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  if (h < 22) return "Good evening";
  return "Working late";
}

function useTicker() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setI((x) => (x + 1) % LIVE_TICKER.length), 3800);
    return () => clearInterval(id);
  }, []);
  return LIVE_TICKER[i];
}

// Rotate a 3-item window through SUGGESTIONS every ~5s
function useRotatingSuggestions(windowSize = 3, intervalMs = 5000) {
  const [offset, setOffset] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setOffset((x) => (x + 1) % SUGGESTIONS.length), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return Array.from({ length: windowSize }, (_, i) => SUGGESTIONS[(offset + i) % SUGGESTIONS.length]);
}


function Home() {
  const clock = useClock();
  const greeting = useGreeting();
  const rotating = useRotatingSuggestions(3, 5000);
  const [helpOpen, setHelpOpen] = useState(false);
  
  
  
  const today = new Date().toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });
  return (
    <>
      <style>{CSS}</style>
      <div id="screen">
        <div className="grain" aria-hidden />

        {/* Status bar */}
        <div id="sb">
          <div className="sb-left">
            <span className="sb-brand">
              <span className="sb-glyph">◇</span> AylinOS
            </span>
            <span className="sb-divider" />
            <span className="sb-ver">v2.4.1 — “midnight oil”</span>
          </div>
          <div className="sb-right">
            <div className="sb-pill">
              <span className="sb-dot pulse" style={{ background: "#6366f1" }} />
              <span>Claude</span>
            </div>
            <div className="sb-pill">
              <span className="sb-dot pulse" style={{ background: "#3b82f6", animationDelay: ".4s" }} />
              <span>Tavily</span>
            </div>
            <div className="sb-pill">
              <span className="sb-dot pulse" style={{ background: "#10b981", animationDelay: ".8s" }} />
              <span>SQLite</span>
            </div>
            <span className="sb-divider" />
            <div className="sb-pill">
              <span className="sb-dot" style={{ background: "#10b981" }} />
              <span>
                <b>7</b> agents · <b>0</b> active
              </span>
            </div>
            <span id="sb-clock">{clock}</span>
          </div>
        </div>

        {/* Search zone */}
        <section id="search-zone">
          <div className="prompt-row">
            <span className="prompt-eyebrow">
              <span className="eyebrow-dot" /> {today.toUpperCase()} · session 04 · ready
            </span>
            <h1 className="prompt-h1">
              <span className="bracket">[</span>
              {greeting}, <span className="prompt-name">Aylin</span>
              <span className="bracket">]</span>
            </h1>
            <p className="prompt-sub">Route a task to an agent, or just ask.</p>

          </div>

          <div className="search-wrap">
            <span className="search-status" title="awaiting prompt">
              <span className="ss-dot" />
            </span>
            <input
              id="search-bar"
              type="text"
              placeholder="Ask anything, or route a task to an agent…"
              autoComplete="off"
              spellCheck={false}
            />
            <span className="search-cursor" aria-hidden />
            <span className="search-cmd">⌘K</span>
          </div>
        </section>

        {/* Help me decide — collapsible side panel */}
        <section id="help-zone">
          <button
            type="button"
            className={`help-toggle ${helpOpen ? "is-open" : ""}`}
            onClick={() => setHelpOpen((v) => !v)}
            aria-expanded={helpOpen}
            aria-controls="help-panel"
          >
            <span className="help-chev">{helpOpen ? "▾" : "▸"}</span>
            <span>Help me decide</span>
            <span className="help-meta">
              {helpOpen ? "hide suggestions & recent" : "suggestions & recent activity"}
            </span>
          </button>

          {helpOpen && (
            <div id="help-panel" className="dd-card">
              <div className="dd-section dd-rec">
                <div className="dd-label">
                  <span>Recommended</span>
                  <span className="dd-meta">awaiting prompt<span className="term-cursor" /></span>
                </div>
                <ul className="suggest-list">
                  {rotating.map((s) => (
                    <li key={s.q} className="suggest-row">
                      <span className="suggest-arrow">→</span>
                      <span className="suggest-q">{s.q}</span>
                      <span className="suggest-agent">{s.agent}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="dd-divider" />
              <div className="dd-section dd-recent">
                <div className="dd-label"><span>Recent</span></div>
                <div className="recent-row"><span className="recent-time">14m</span><span className="recent-text"><b>Research</b> · synthesized Cursor GTM brief → Drive</span></div>
                <div className="recent-row"><span className="recent-time">2h</span><span className="recent-text"><b>Job Search</b> · scored 12 Greenhouse listings, 2 above threshold</span></div>
                <div className="recent-row"><span className="recent-time">6h</span><span className="recent-text"><b>Outreach</b> · 3 drafts queued for review (Sarah, Ben, Maya)</span></div>
                <div className="recent-row"><span className="recent-time">1d</span><span className="recent-text"><b>Fork Yeah!</b> · booked Lodi for Sat 8pm, confirmed via email</span></div>
                <div className="recent-row"><span className="recent-time">1d</span><span className="recent-text"><b>CS Triage</b> · routed 41 tickets, 2 escalated to human</span></div>
                <div className="recent-row"><span className="recent-time">2d</span><span className="recent-text"><b>Networking</b> · scored 22 LinkedIn profiles, 4 above threshold</span></div>
              </div>
            </div>
          )}
        </section>


        {/* Active pipeline — band between dropdown and dock */}
        <div id="pipeline-band">
          <span className="pb-tag">
            <span className="pb-tag-dot" /> ACTIVE PIPELINE
          </span>
          <div className="pb-track">
            {LIVE_TICKER.map((t, i) => (
              <span className="pb-chip" key={i}>
                <span className="pb-dot" />
                {t.text}
              </span>
            ))}
          </div>
          <span className="pb-count">{LIVE_TICKER.length} running</span>
        </div>

        {/* Dock */}
        <div id="dock-row">
          <div id="dock">
            {APPS.map((a) => (
              <div className="di-cell" key={a.id} title={a.name}>
                <div className="di" style={{ background: a.gradient }}>
                  <a.Icon size={26} strokeWidth={1.75} color="#ffffff" />
                </div>
                <div className="di-label">{a.name}</div>
                <div className="di-tag">{a.tag}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Eval footer — the receipts */}
        <div id="telem">
          <div id="telem-inner">
            <a href="/evals" className="tel-cell clickable" title="Routing F1 across all 7 agents, last 7 days">
              <span className="tel-key">F1</span>
              <span className="tel-val">0.87</span>
              <span className="tel-delta up">▲ 0.04</span>
            </a>
            <div className="tel-cell" title="True positives / (true positives + false positives) on routing decisions">
              <span className="tel-key">Precision</span>
              <span className="tel-val">0.91</span>
            </div>
            <div className="tel-cell" title="True positives / (true positives + false negatives)">
              <span className="tel-key">Recall</span>
              <span className="tel-val">0.84</span>
            </div>
            <div className="tel-cell" title="LLM calls today across all agents">
              <span className="tel-key">Calls 24h</span>
              <span className="tel-val">1,247</span>
            </div>
            <div className="tel-cell" title="Median end-to-end latency">
              <span className="tel-key">p50</span>
              <span className="tel-val">820ms</span>
            </div>
            <div className="tel-cell" title="Active prompt version — shadow-testing v3 on 10% of traffic">
              <span className="tel-key">Prompt</span>
              <span className="tel-val" style={{ color: "#6366f1" }}>v2</span>
              <span className="tel-badge">v3 shadow 10%</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

/*
 * EVAL FOOTER — TAKEAWAYS PLACEHOLDER
 * ------------------------------------
 * Replace these numbers with real values from your eval harness before interviews:
 *   - F1 / Precision / Recall: routing-decision metrics across the 7 agents.
 *     Current placeholders (0.87 / 0.91 / 0.84) imply a precision-favoring router
 *     — frame in interviews as "I'd rather refuse-to-route than misroute."
 *   - Δ on F1: week-over-week change. Tie to a specific prompt or model change.
 *   - Calls 24h: real LLM call volume. If low, swap to "Calls 7d" or "Tasks 7d".
 *   - p50: median end-to-end latency. Add p95 to the tooltip when you have it.
 *   - Prompt vN + shadow %: shows you do prompt versioning and shadow rollouts.
 *
 * Talking points each cell unlocks:
 *   F1          → "How I score routing quality across heterogeneous agents."
 *   Precision   → "Cost of a wrong route is higher than a missed one — here's why."
 *   Recall      → "Where I'd push next, and the failure mode I'd accept."
 *   Calls 24h   → "Token + dollar budget per agent, and how I throttle."
 *   p50         → "What dominates latency (model, tool calls, network) + caching."
 *   Prompt v2   → "How I version prompts, A/B them, and ship safely."
 */

const CSS = `
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f4f3ee;
  --bg-2:#eceae3;
  --ink:#0f1115;
  --ink-2:rgba(15,17,21,.82);
  --ink-3:rgba(15,17,21,.62);
  --ink-4:rgba(15,17,21,.38);
  --b:rgba(15,17,21,.12);
  --b-2:rgba(15,17,21,.2);
  --surface:rgba(255,255,255,.78);
  --mono:'JetBrains Mono','SF Mono','Menlo',monospace;
  --sans:'Inter',system-ui,sans-serif;
  --accent:#4f46e5;
}
html,body{height:100%;overflow:hidden;font-family:var(--sans);background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased}

@keyframes dot-pulse{0%,100%{opacity:1}50%{opacity:.35}}

#screen{
  width:100vw;height:100vh;display:flex;flex-direction:column;position:relative;
  background-color:var(--bg);
  background-image:
    radial-gradient(ellipse 70% 45% at 50% -5%, rgba(99,102,241,.16) 0%, transparent 60%),
    radial-gradient(ellipse 45% 35% at 8% 92%, rgba(16,185,129,.1) 0%, transparent 55%),
    radial-gradient(ellipse 40% 30% at 95% 65%, rgba(244,114,182,.1) 0%, transparent 55%),
    radial-gradient(circle at 1px 1px, rgba(26,26,36,.06) 1px, transparent 0);
  background-size:auto,auto,auto,22px 22px;
}
/* Grain overlay — adds tactile film texture */
.grain{
  position:absolute;inset:0;pointer-events:none;z-index:1;mix-blend-mode:multiply;opacity:.5;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .35 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
}
#sb,#search-zone,#help-zone,#pipeline-band,#telem,#dock-row{position:relative;z-index:2}


/* Status bar */
#sb{
  height:34px;flex-shrink:0;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 22px;
  background:rgba(255,255,255,.65);
  backdrop-filter:blur(20px) saturate(1.4);
  border-bottom:1px solid var(--b);
}
.sb-left{display:flex;align-items:center;gap:12px}
.sb-brand{font-family:var(--mono);font-size:12px;font-weight:700;letter-spacing:.04em;color:var(--ink)}
.sb-ver{font-family:var(--mono);font-size:10px;color:var(--ink-3);letter-spacing:.02em}
.sb-divider{width:1px;height:14px;background:var(--b-2)}
.sb-right{display:flex;align-items:center;gap:14px}
.sb-pill{display:flex;align-items:center;gap:6px;font-family:var(--mono);font-size:10.5px;color:var(--ink-2);letter-spacing:.01em}
.sb-pill b{color:var(--ink);font-weight:600}
.sb-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0;box-shadow:0 0 6px currentColor}
.sb-dot.pulse{animation:dot-pulse 2s ease-in-out infinite}
#sb-clock{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--ink);letter-spacing:.04em;padding-left:4px}

/* Search zone */
#search-zone{
  flex-shrink:0;display:flex;flex-direction:column;align-items:center;
  padding:38px 24px 10px;
}
.prompt-row{text-align:center;margin-bottom:22px;display:flex;flex-direction:column;align-items:center;gap:6px}
.prompt-eyebrow{
  position:relative;
  display:inline-flex;align-items:center;gap:8px;
  font-family:var(--mono);font-size:10.5px;font-weight:700;color:var(--ink-2);
  letter-spacing:.2em;text-transform:uppercase;
  padding:5px 12px;border-radius:999px;
  background:rgba(255,255,255,.7);
  border:1px solid var(--b);
  backdrop-filter:blur(8px);
}
.eyebrow-dot{
  width:6px;height:6px;border-radius:50%;background:#10b981;
  box-shadow:0 0 8px #10b981;animation:dot-pulse 1.8s ease-in-out infinite;
}
.prompt-h1{
  font-size:30px;font-weight:600;letter-spacing:-.025em;line-height:1.15;
  color:var(--ink);margin-top:6px;
}
.bracket{
  font-family:var(--mono);font-weight:400;color:var(--ink-4);
  margin:0 6px;font-size:.85em;
}
.prompt-name{color:var(--accent);font-weight:700}
.prompt-sub{font-size:13px;color:var(--ink-3);margin-top:4px}
.kbd-inline{
  font-family:var(--mono);font-size:10.5px;font-weight:600;color:var(--ink);
  padding:1px 6px;border-radius:4px;
  background:rgba(255,255,255,.85);border:1px solid var(--b-2);
  box-shadow:0 1px 0 var(--b);
}

.sb-glyph{color:var(--accent);font-weight:400;margin-right:2px;display:inline-block;animation:spin 18s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}


.search-wrap{width:100%;max-width:680px;position:relative}
.search-status{
  position:absolute;left:18px;top:50%;transform:translateY(-50%);z-index:2;
  display:inline-flex;align-items:center;justify-content:center;
  width:14px;height:14px;
}
.ss-dot{
  width:7px;height:7px;border-radius:50%;background:var(--ink-3);
}
.search-cursor{
  position:absolute;left:42px;top:50%;transform:translateY(-50%);z-index:2;
  width:2px;height:18px;background:var(--ink-4);opacity:.7;
  animation:blink 1.05s steps(2,end) infinite;pointer-events:none;
}
#search-bar:not(:placeholder-shown) ~ .search-cursor,
.search-wrap:focus-within .search-cursor{display:none}
#search-bar{
  position:relative;z-index:1;
  width:100%;
  background:#ffffff;
  border:1px solid var(--b-2);
  border-radius:12px;
  padding:16px 60px 16px 52px;
  font-family:var(--sans);font-size:15px;color:var(--ink);outline:none;
  transition:border-color 160ms, box-shadow 160ms;
  box-shadow:0 1px 2px rgba(15,17,21,.04);
}
#search-bar::placeholder{color:var(--ink-3)}
#search-bar:focus{
  border-color:var(--ink);
  box-shadow:0 0 0 3px rgba(15,17,21,.08);
}
.search-cmd{
  position:absolute;right:14px;top:50%;transform:translateY(-50%);z-index:2;
  font-family:var(--mono);font-size:10.5px;font-weight:600;color:var(--ink-2);
  padding:4px 8px;border-radius:5px;
  background:rgba(255,255,255,.9);border:1px solid var(--b-2);
  pointer-events:none;letter-spacing:.04em;
}

/* Shared terminal cursor + ticker primitives */
.term-cursor{
  display:inline-block;width:5px;height:10px;background:var(--accent);
  margin-left:4px;vertical-align:-1px;animation:blink 1.05s steps(2,end) infinite;
}
@keyframes blink{50%{opacity:0}}

/* Help me decide — collapsible suggestions + recent */
#help-zone{
  flex:1;min-height:0;width:100%;max-width:720px;margin:6px auto 0;
  padding:0 24px;display:flex;flex-direction:column;align-items:flex-end;gap:8px;
}
.help-toggle{
  display:inline-flex;align-items:center;gap:8px;
  font-family:var(--mono);font-size:11px;color:var(--ink-2);
  letter-spacing:.04em;
  padding:6px 12px;border-radius:8px;
  background:rgba(255,255,255,.7);border:1px solid var(--b);
  cursor:pointer;transition:background 140ms,border-color 140ms,color 140ms;
  backdrop-filter:blur(8px);
}
.help-toggle:hover{background:rgba(255,255,255,.92);border-color:var(--b-2);color:var(--ink)}
.help-toggle.is-open{background:#fff;border-color:var(--b-2);color:var(--ink)}
.help-chev{font-family:var(--mono);font-size:10px;color:var(--ink-3);width:10px;text-align:center}
.help-meta{font-family:var(--mono);font-size:10px;color:var(--ink-3);letter-spacing:.02em;padding-left:6px;border-left:1px solid var(--b)}
#help-panel{
  width:100%;flex:1;min-height:0;display:flex;flex-direction:column;
  background:rgba(255,255,255,.82);
  border:1px solid var(--b);border-radius:13px;
  box-shadow:0 10px 28px rgba(26,26,36,.07), 0 1px 0 rgba(255,255,255,.8) inset;
  backdrop-filter:blur(12px);overflow:hidden;
  animation:fadeUp .2s ease;
}
.dd-card{display:flex;flex-direction:column}
.dd-section{padding:12px 16px}
.dd-section.dd-rec{flex-shrink:0}
.dd-section.dd-recent{flex:1;min-height:0;overflow-y:auto}
.dd-divider{height:1px;background:var(--b);margin:0}
.dd-label{
  display:flex;align-items:center;justify-content:space-between;
  font-family:var(--mono);font-size:9.5px;color:var(--ink-3);
  text-transform:uppercase;letter-spacing:.16em;margin-bottom:6px;
}
.dd-meta{display:inline-flex;align-items:center;gap:2px;color:var(--ink-3);text-transform:none;letter-spacing:.02em}
.suggest-list{list-style:none;display:flex;flex-direction:column;gap:1px;animation:fadeUp .35s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.suggest-row{
  display:flex;align-items:center;gap:12px;
  padding:7px 8px;margin:0 -8px;border-radius:6px;
  cursor:pointer;transition:background 120ms,color 120ms;
}
.suggest-row:hover{background:rgba(99,102,241,.07)}
.suggest-arrow{font-family:var(--mono);font-size:11px;color:var(--ink-4);width:10px;flex-shrink:0}
.suggest-row:hover .suggest-arrow{color:var(--accent)}
.suggest-q{flex:1;font-family:var(--sans);font-size:13px;color:var(--ink-2);letter-spacing:-.003em}
.suggest-row:hover .suggest-q{color:var(--ink)}
.suggest-agent{
  font-family:var(--mono);font-size:9px;font-weight:600;
  padding:2px 7px;border-radius:4px;
  letter-spacing:.06em;text-transform:uppercase;flex-shrink:0;
  color:var(--ink-3);background:rgba(15,17,21,.04);border:1px solid var(--b);
}
.recent-row{display:flex;align-items:flex-start;gap:12px;padding:4px 0}
.recent-time{font-family:var(--mono);font-size:10px;color:var(--ink-3);width:30px;flex-shrink:0;padding-top:1px;letter-spacing:.02em}
.recent-text{font-family:var(--sans);font-size:12px;color:var(--ink-2);line-height:1.5;letter-spacing:-.003em}
.recent-text b{color:var(--ink);font-weight:600}

/* Active pipeline — band */
#pipeline-band{
  flex-shrink:0;display:flex;align-items:center;gap:14px;
  width:100%;max-width:980px;margin:12px auto 0;padding:11px 18px;
  background:rgba(255,255,255,.55);
  border:1px solid var(--b);border-radius:11px;
  backdrop-filter:blur(10px);
  box-shadow:0 6px 18px rgba(26,26,36,.05);
}
.pb-tag{
  flex-shrink:0;display:inline-flex;align-items:center;gap:7px;
  font-family:var(--mono);font-size:10px;font-weight:700;
  letter-spacing:.2em;color:var(--ink-2);text-transform:uppercase;
}
.pb-tag-dot{
  width:7px;height:7px;border-radius:50%;background:#10b981;
  box-shadow:0 0 0 3px rgba(16,185,129,.18), 0 0 8px #10b981;
  animation:dot-pulse 1.6s ease-in-out infinite;
}
.pb-track{
  flex:1;min-width:0;display:flex;align-items:center;gap:8px;
  overflow-x:auto;scrollbar-width:none;
}
.pb-track::-webkit-scrollbar{display:none}
.pb-chip{
  flex-shrink:0;display:inline-flex;align-items:center;gap:7px;
  font-family:var(--mono);font-size:11px;color:var(--ink-2);
  padding:5px 11px;border-radius:999px;
  background:rgba(255,255,255,.8);border:1px solid var(--b);
  letter-spacing:.01em;
}
.pb-dot{
  width:5px;height:5px;border-radius:50%;flex-shrink:0;
  background:var(--ink-3);animation:dot-pulse 1.6s ease-in-out infinite;
}
.pb-count{
  flex-shrink:0;font-family:var(--mono);font-size:10px;color:var(--ink-3);
  letter-spacing:.06em;text-transform:uppercase;
}

/* Slim eval footer */
#telem{flex-shrink:0;display:flex;justify-content:center;padding:2px 24px 8px}
#telem-inner{
  display:flex;align-items:center;
  background:rgba(255,255,255,.5);
  border:1px solid var(--b);
  border-radius:7px;overflow:hidden;backdrop-filter:blur(10px);
  opacity:.85;
}
.tel-cell{
  padding:4px 12px;border-right:1px solid var(--b);
  display:inline-flex;align-items:center;gap:6px;
  text-decoration:none;transition:background 150ms;
}
.tel-cell:last-child{border-right:none}
.tel-cell.clickable{cursor:pointer}
.tel-cell.clickable:hover{background:rgba(99,102,241,.08)}
.tel-val{font-family:var(--mono);font-size:10.5px;font-weight:600;color:var(--ink);letter-spacing:.01em}
.tel-key{font-family:var(--mono);font-size:9px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.1em}
.tel-badge{
  display:inline-block;padding:1px 6px;border-radius:3px;
  font-family:var(--mono);font-size:8.5px;font-weight:600;letter-spacing:.05em;
  background:rgba(99,102,241,.1);color:var(--accent);border:1px solid rgba(99,102,241,.25);
}
.tel-delta{font-family:var(--mono);font-size:9px;font-weight:600;letter-spacing:.02em}
.tel-delta.up{color:#059669}
.tel-delta.down{color:#dc2626}

/* Dock */
#dock-row{display:flex;justify-content:center;padding:6px 16px 8px;flex-shrink:0;overflow-x:auto}
#dock{
  display:flex;align-items:flex-start;gap:6px;
  padding:14px 16px 12px;
  background:rgba(255,255,255,.7);
  backdrop-filter:blur(40px) saturate(1.6);
  border:1px solid rgba(255,255,255,.9);
  border-radius:22px;flex-shrink:0;
  box-shadow:0 16px 40px rgba(26,26,36,.12), 0 1px 0 rgba(255,255,255,.9) inset;
}
.di-cell{
  display:flex;flex-direction:column;align-items:center;gap:6px;
  width:78px;cursor:pointer;padding:2px 4px;
}
.di{
  width:54px;height:54px;border-radius:11px;
  display:flex;align-items:center;justify-content:center;overflow:hidden;
  border:1px solid rgba(255,255,255,.08);
  box-shadow:0 1px 0 rgba(255,255,255,.18) inset, 0 -1px 0 rgba(0,0,0,.25) inset, 0 6px 16px rgba(15,17,21,.22);
  transition:transform 180ms cubic-bezier(.34,1.3,.64,1), box-shadow 180ms;
}
.di svg{display:block;shape-rendering:geometricPrecision}
.di-cell:hover .di{transform:translateY(-5px);box-shadow:0 1px 0 rgba(255,255,255,.22) inset, 0 -1px 0 rgba(0,0,0,.3) inset, 0 14px 26px rgba(15,17,21,.28)}
.di-cell:active .di{transform:scale(.94);transition-duration:80ms}
.di-label{
  font-family:var(--sans);font-size:10.5px;font-weight:600;
  color:var(--ink);letter-spacing:-.005em;text-align:center;margin-top:1px;
}
.di-tag{
  font-family:var(--mono);font-size:8.5px;color:var(--ink-3);
  text-transform:uppercase;letter-spacing:.08em;text-align:center;
}

@media (prefers-reduced-motion:reduce){
  .di,.sb-dot,#agent-dot{animation:none;transition:none}
}
`;
