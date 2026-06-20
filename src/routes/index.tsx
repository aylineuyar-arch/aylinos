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

// Type out a list of phrases as a live placeholder
function useTypingPlaceholder(phrases: string[], { typeMs = 55, holdMs = 1600, eraseMs = 28 } = {}) {
  const [text, setText] = useState("");
  useEffect(() => {
    let phraseIdx = 0;
    let charIdx = 0;
    let mode: "type" | "hold" | "erase" = "type";
    let timer: ReturnType<typeof setTimeout>;
    const tick = () => {
      const phrase = phrases[phraseIdx];
      if (mode === "type") {
        charIdx++;
        setText(phrase.slice(0, charIdx));
        if (charIdx >= phrase.length) { mode = "hold"; timer = setTimeout(tick, holdMs); return; }
        timer = setTimeout(tick, typeMs);
      } else if (mode === "hold") {
        mode = "erase"; timer = setTimeout(tick, eraseMs);
      } else {
        charIdx--;
        setText(phrase.slice(0, Math.max(0, charIdx)));
        if (charIdx <= 0) { mode = "type"; phraseIdx = (phraseIdx + 1) % phrases.length; timer = setTimeout(tick, 280); return; }
        timer = setTimeout(tick, eraseMs);
      }
    };
    timer = setTimeout(tick, 600);
    return () => clearTimeout(timer);
  }, [phrases, typeMs, holdMs, eraseMs]);
  return text;
}



function Home() {
  const clock = useClock();
  const greeting = useGreeting();
  const rotating = useRotatingSuggestions(3, 5000);
  
  const typed = useTypingPlaceholder([
    "Ask anything, or route a task to an agent…",
    "should I apply to Ramp?",
    "book dinner in Soho tomorrow at 8",
    "draft intro to Sarah at Sequoia",
    "research Cursor's GTM motion",
    "triage today's support inbox",
  ]);
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
              <span className="sb-glyph">◇</span>Aylin<span className="sb-brand-os">OS</span>
            </span>
            <span className="sb-byline">designed &amp; shipped by Aylin</span>
            <span className="sb-divider" />
            <span className="sb-ver">v2.4.1 — "midnight oil"</span>
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
              placeholder={typed || " "}
              autoComplete="off"
              spellCheck={false}
            />

            <span className="search-cursor" aria-hidden />
            <button
              type="button"
              className={`help-toggle ${helpOpen ? "is-open" : ""}`}
              onClick={() => setHelpOpen((v) => !v)}
              aria-expanded={helpOpen}
              aria-controls="help-panel"
            >
              <span className="help-chev">{helpOpen ? "▾" : "▸"}</span>
              <span>Help me decide</span>
            </button>
          </div>

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
            </div>
          )}
        </section>

        <section id="recent-zone">
          <div className="recent-main">
            <div className="recent-grid">
              <div className="recent-card rc-searches">
                <div className="dd-label"><span>Recent searches</span></div>
                <div className="recent-row"><span className="recent-time">8m</span><span className="recent-text">"prep Hebbia interview"</span></div>
                <div className="recent-row"><span className="recent-time">1h</span><span className="recent-text">"should I apply to Ramp"</span></div>
                <div className="recent-row"><span className="recent-time">3h</span><span className="recent-text">"intro to Sarah at Sequoia"</span></div>
                <div className="recent-row"><span className="recent-time">1d</span><span className="recent-text">"Cursor GTM motion"</span></div>
              </div>
              <div className="recent-card rc-pipeline">
                <div className="dd-label">
                  <span>Running now</span>
                  <span className="dd-meta"><span className="live-dot" /> {LIVE_TICKER.length}</span>
                </div>
                {LIVE_TICKER.slice(0, 4).map((t) => (
                  <div className="recent-row" key={t.text}>
                    <span className="recent-time" style={{ color: t.dot }}>●</span>
                    <span className="recent-text">{t.text.replace(/ ·.*$/, "")}<span className="recent-sub"> · {t.text.split(" · ")[1]}</span></span>
                  </div>
                ))}
              </div>
              <div className="recent-card rc-runs">
                <div className="dd-label"><span>Recent runs</span></div>
                <div className="recent-row"><span className="recent-time">14m</span><span className="recent-text"><b>Research</b> · Cursor brief → Drive</span></div>
                <div className="recent-row"><span className="recent-time">2h</span><span className="recent-text"><b>Job Search</b> · 12 listings, 2 above bar</span></div>
                <div className="recent-row"><span className="recent-time">6h</span><span className="recent-text"><b>Outreach</b> · 3 drafts (Sequoia, Stripe, Anthropic)</span></div>
                <div className="recent-row"><span className="recent-time">1d</span><span className="recent-text"><b>CS Triage</b> · 41 tickets, 2 escalated</span></div>
              </div>
            </div>
          </div>

          <aside className="recent-rail">
            <div className="recent-card rc-inbox">
              <div className="dd-label">
                <span>New in your inbox</span>
                <span className="dd-meta">via email tracker</span>
              </div>
              <div className="signal-row">
                <div className="signal-head"><span className="signal-tag tag-job">JOB</span><span className="signal-time">2h</span></div>
                <div className="signal-title">Ramp · Staff Engineer, Platform</div>
                <div className="signal-sub">Greenhouse · matches 4/5 criteria</div>
              </div>
              <div className="signal-row">
                <div className="signal-head"><span className="signal-tag tag-reply">REPLY</span><span className="signal-time">4h</span></div>
                <div className="signal-title">Sarah (Sequoia) replied to your intro</div>
                <div className="signal-sub">"happy to grab 20 min next week"</div>
              </div>
              <div className="signal-row">
                <div className="signal-head"><span className="signal-tag tag-job">JOB</span><span className="signal-time">6h</span></div>
                <div className="signal-title">Anthropic · 4 new roles posted</div>
                <div className="signal-sub">2 match your bar · drafted notes</div>
              </div>
              <div className="signal-row">
                <div className="signal-head"><span className="signal-tag tag-booked">FORK YEA</span><span className="signal-time">7h</span></div>
                <div className="signal-title">Dinner confirmed · Friday 7:30pm</div>
                <div className="signal-sub">Via Carota · party of 2 · OpenTable</div>
              </div>
            </div>
            <div className="recent-card rc-upcoming">
              <div className="dd-label"><span>Upcoming</span><span className="dd-meta">next 7 days</span></div>
              <div className="up-row">
                <span className="up-when">Mon<br/><b>10:30</b></span>
                <div className="up-body">
                  <div className="up-title">Intro · Priya Raman</div>
                  <div className="up-sub">Head of Eng, Linder — coffee, Blue Bottle Mint Plaza</div>
                </div>
              </div>
              <div className="up-row">
                <span className="up-when">Tue<br/><b>14:00</b></span>
                <div className="up-body">
                  <div className="up-title">Interview · Staff Eng, Platform</div>
                  <div className="up-sub">Quill — sys design w/ Marcus Oduya (45m)</div>
                </div>
              </div>
              <div className="up-row">
                <span className="up-when">Thu<br/><b>09:00</b></span>
                <div className="up-body">
                  <div className="up-title">Networking · Dani Kessler</div>
                  <div className="up-sub">PM @ Northwind — Sequoia intro, 20m phone</div>
                </div>
              </div>
              <div className="up-row">
                <span className="up-when">Fri<br/><b>16:00</b></span>
                <div className="up-body">
                  <div className="up-title">Final round · Eng Manager</div>
                  <div className="up-sub">Bramble — exec chat w/ CTO + values panel</div>
                </div>
              </div>
            </div>
          </aside>

        </section>



        {/* Dock */}
        <div id="dock-row">
          <div id="dock-wrap">
            <div className="dock-label"><span>Agents</span><span className="dock-meta">{APPS.length} active · click to route</span></div>
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
        </div>


        {/* Eval footer — single line */}
        <a id="telem" href="/evals" title="Click for full eval harness — 7-day routing metrics across all agents">
          <span className="tel-key">EVALS</span>
          <span className="tel-pair"><span className="tel-k">F1</span><span className="tel-v">0.87</span><span className="tel-delta">▲0.04</span></span>
          <span className="tel-sep">·</span>
          <span className="tel-pair"><span className="tel-k">precision</span><span className="tel-v">0.91</span></span>
          <span className="tel-sep">·</span>
          <span className="tel-pair"><span className="tel-k">recall</span><span className="tel-v">0.84</span></span>
          <span className="tel-sep">·</span>
          <span className="tel-pair"><span className="tel-k">p50</span><span className="tel-v">820ms</span></span>
          <span className="tel-sep">·</span>
          <span className="tel-pair"><span className="tel-k">prompt</span><span className="tel-v accent">v2</span><span className="tel-shadow">v3 shadow 10%</span></span>
        </a>

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
  --bg:#FCF9F1;
  --bg-2:#F3F1EA;
  --ink:#2A2620;
  --ink-2:#454039;
  --ink-3:#8C8579;
  --ink-4:#A8A294;
  --b:#E5E1D5;
  --b-2:#D6D1C2;
  --surface:rgba(255,255,255,.7);
  --mono:'JetBrains Mono','SF Mono','Menlo',monospace;
  --sans:'Inter',system-ui,sans-serif;
  --accent:#EC4899;
  --accent-2:#DB2777;
}
html,body{height:100%;font-family:var(--sans);background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased}

@keyframes dot-pulse{0%,100%{opacity:1}50%{opacity:.35}}

#screen{
  width:100vw;min-height:100vh;display:flex;flex-direction:column;position:relative;
  background-color:var(--bg);
  background-image:
    radial-gradient(ellipse 70% 45% at 50% -5%, rgba(236,72,153,.18) 0%, transparent 60%),
    radial-gradient(ellipse 45% 35% at 8% 92%, rgba(217,119,6,.08) 0%, transparent 55%),
    radial-gradient(ellipse 40% 30% at 95% 65%, rgba(180,83,9,.07) 0%, transparent 55%),
    radial-gradient(circle at 1px 1px, rgba(69,64,57,.07) 1px, transparent 0);
  background-size:auto,auto,auto,22px 22px;
}
/* Grain overlay — adds tactile film texture */
.grain{
  position:absolute;inset:0;pointer-events:none;z-index:1;mix-blend-mode:multiply;opacity:.5;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .35 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
}
#sb,#search-zone,#recent-zone,#pipeline-band,#telem,#dock-row{position:relative;z-index:2}


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
.sb-brand{font-family:var(--mono);font-size:15px;font-weight:800;letter-spacing:-.005em;color:var(--ink);display:inline-flex;align-items:baseline;gap:1px}
.sb-brand-os{color:var(--accent);font-weight:800}
.sb-byline{font-family:var(--mono);font-size:10px;color:var(--ink-3);letter-spacing:.04em;font-style:italic}
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
  width:8px;height:8px;border-radius:50%;background:var(--accent);
  box-shadow:0 0 10px rgba(236,72,153,.6);animation:dot-pulse 1.8s ease-in-out infinite;
}
.search-cursor{
  position:absolute;left:44px;top:50%;transform:translateY(-50%);z-index:2;
  width:2px;height:20px;background:var(--accent);opacity:.85;
  animation:blink 1.05s steps(2,end) infinite;pointer-events:none;
}
#search-bar:not(:placeholder-shown) ~ .search-cursor,
.search-wrap:focus-within .search-cursor{display:none}
#search-bar{
  position:relative;z-index:1;
  width:100%;
  background:#fdf2f8;
  border:2px solid var(--accent);
  border-radius:18px;
  padding:26px 172px 26px 56px;
  font-family:var(--sans);font-size:19px;color:var(--ink);outline:none;
  letter-spacing:-.005em;
  transition:border-color 160ms, box-shadow 200ms;
  box-shadow:0 1px 0 rgba(255,255,255,.9) inset, 0 12px 32px rgba(236,72,153,.18);
}
#search-bar::placeholder{color:var(--ink-3);opacity:.9}
#search-bar:focus{
  border-color:var(--accent);
  background:#fff;
  box-shadow:0 1px 0 rgba(255,255,255,.9) inset, 0 14px 36px rgba(236,72,153,.28), 0 0 0 5px rgba(236,72,153,.2);
}



/* Shared terminal cursor + ticker primitives */
.term-cursor{
  display:inline-block;width:5px;height:10px;background:var(--accent);
  margin-left:4px;vertical-align:-1px;animation:blink 1.05s steps(2,end) infinite;
}
@keyframes blink{50%{opacity:0}}

/* Help me decide — toggle lives inside the search bar */
.help-toggle{
  position:absolute;right:8px;top:50%;transform:translateY(-50%);z-index:3;
  display:inline-flex;align-items:center;gap:6px;
  font-family:var(--mono);font-size:11px;color:var(--ink);letter-spacing:.02em;font-weight:600;
  padding:6px 10px;border-radius:7px;
  background:rgba(15,17,21,.09);border:1px solid var(--b-2);
  cursor:pointer;transition:background 140ms,border-color 140ms,color 140ms;
}
.help-toggle:hover{background:rgba(15,17,21,.14);border-color:var(--ink-3);color:var(--ink)}
.help-toggle.is-open{background:var(--ink);border-color:var(--ink);color:#fff}
.help-toggle.is-open .help-chev{color:rgba(255,255,255,.7)}
.help-chev{font-family:var(--mono);font-size:10px;color:var(--ink-3);width:8px;text-align:center}
#help-panel{
  width:100%;max-width:680px;margin:10px auto 0;
  background:rgba(255,255,255,.82);
  border:1px solid var(--b);border-radius:13px;
  box-shadow:0 10px 28px rgba(26,26,36,.07), 0 1px 0 rgba(255,255,255,.8) inset;
  backdrop-filter:blur(12px);overflow:hidden;
  animation:fadeUp .2s ease;
}
.dd-card{display:flex;flex-direction:column}
.dd-section{padding:12px 16px}
.dd-divider{height:1px;background:var(--b);margin:0}

/* Recent zone — content column + inbox-signals rail */
#recent-zone{
  width:100%;max-width:1240px;margin:14px auto 0;
  padding:0 24px;
  display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:14px;align-items:stretch;
}
.recent-main{display:flex;flex-direction:column;min-width:0}
.recent-rail{display:flex;flex-direction:column;gap:10px;min-width:0}
@media (max-width:640px){
  #recent-zone{grid-template-columns:1fr}
}
.recent-grid{
  display:flex;flex-direction:column;gap:10px;
}


.recent-card{
  padding:16px 18px;
  background:rgba(255,255,255,.6);
  border:1px solid var(--b);border-radius:12px;
  backdrop-filter:blur(10px);
  min-height:0;
}

.dd-label{
  display:flex;align-items:center;justify-content:space-between;
  font-family:var(--mono);font-size:11px;font-weight:600;color:var(--ink);
  text-transform:uppercase;letter-spacing:.16em;margin-bottom:10px;
}
.dd-meta{display:inline-flex;align-items:center;gap:4px;color:var(--ink-3);text-transform:none;letter-spacing:.02em;font-weight:400;font-size:10px}
.suggest-list{list-style:none;display:flex;flex-direction:column;gap:1px;animation:fadeUp .35s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.suggest-row{
  display:flex;align-items:center;gap:12px;
  padding:7px 8px;margin:0 -8px;border-radius:6px;
  cursor:pointer;transition:background 120ms,color 120ms;
}
.suggest-row:hover{background:rgba(236,72,153,.08)}
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
.recent-row{display:flex;align-items:flex-start;gap:12px;padding:5px 0}
.recent-time{font-family:var(--mono);font-size:11px;color:var(--ink-3);width:30px;flex-shrink:0;padding-top:1px;letter-spacing:.02em}
.recent-text{font-family:var(--sans);font-size:13.5px;color:var(--ink-2);line-height:1.45;letter-spacing:-.003em;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.recent-text b{color:var(--ink);font-weight:600}
.recent-sub{color:var(--ink-3)}
.live-dot{width:5px;height:5px;border-radius:50%;background:#10b981;box-shadow:0 0 6px #10b981;animation:dot-pulse 1.8s ease-in-out infinite;display:inline-block;margin-right:4px}

.today-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:2px}
.stat{display:flex;flex-direction:column;gap:2px;padding:8px 10px;background:rgba(255,255,255,.5);border:1px solid var(--b);border-radius:8px}
.stat-num{font-family:var(--mono);font-size:18px;font-weight:600;color:var(--ink);letter-spacing:-.01em}
.stat-lbl{font-family:var(--mono);font-size:9.5px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.08em}

/* Inbox signals rail */
.rc-inbox{
  background:rgba(255,255,255,.55);
  border-left:2px solid rgba(236,72,153,.35);
}

.signal-row{
  padding:11px 0;border-top:1px solid rgba(15,17,21,.06);
}
.signal-row:first-of-type{border-top:none;padding-top:4px}
.signal-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
.signal-tag{
  font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;
  padding:2px 6px;border-radius:3px;
}
/* Agent-aligned tag colors: matches dock + Running Now dots */
.tag-job{background:rgba(129,140,248,.14);color:#4338ca;border:1px solid rgba(129,140,248,.35)}
.tag-reply{background:rgba(167,139,250,.14);color:#6d28d9;border:1px solid rgba(167,139,250,.35)}
.tag-booked{background:rgba(52,211,153,.14);color:#047857;border:1px solid rgba(52,211,153,.35)}
.signal-time{font-family:var(--mono);font-size:10px;color:var(--ink-3)}
.signal-title{font-family:var(--sans);font-size:13px;color:var(--ink);font-weight:600;line-height:1.35;letter-spacing:-.005em}
.signal-sub{font-family:var(--sans);font-size:11.5px;color:var(--ink-3);margin-top:2px;line-height:1.4}

/* Upcoming — intentionally quiet */
.rc-upcoming{background:rgba(255,255,255,.4);border:1px dashed var(--b-2)}
.up-row{display:flex;gap:12px;padding:8px 0;border-top:1px solid rgba(15,17,21,.05)}
.up-row:first-of-type{border-top:none;padding-top:2px}
.up-when{
  font-family:var(--mono);font-size:9.5px;color:var(--ink-3);
  text-transform:uppercase;letter-spacing:.1em;line-height:1.35;
  width:36px;flex-shrink:0;text-align:right;padding-top:1px;
}
.up-when b{display:block;font-size:11px;color:var(--ink-2);font-weight:600;letter-spacing:.02em;margin-top:1px}
.up-body{min-width:0;flex:1}
.up-title{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);font-weight:500;line-height:1.35;letter-spacing:-.003em}
.up-sub{font-family:var(--sans);font-size:11px;color:var(--ink-4);margin-top:1px;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}





/* Eval footer — single line */
#telem{
  flex-shrink:0;display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:0 10px;
  margin:8px auto 10px;padding:0 28px;
  font-family:var(--mono);font-size:11px;color:var(--ink-2);
  text-decoration:none;transition:color 140ms;
  max-width:780px;
}
#telem:hover{color:var(--ink)}
#telem .tel-key{font-size:9.5px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-3);margin-right:4px}
.tel-pair{display:inline-flex;align-items:baseline;gap:5px}
.tel-k{color:var(--ink-3);font-size:10px;letter-spacing:.04em}
.tel-v{color:var(--ink);font-weight:600;font-size:11.5px;letter-spacing:.01em}
.tel-v.accent{color:var(--accent)}
.tel-delta{color:#059669;font-size:9.5px;font-weight:600;margin-left:2px}
.tel-sep{color:var(--ink-4);margin:0 1px}
.tel-shadow{
  margin-left:4px;padding:1px 6px;border-radius:3px;
  font-size:8.5px;font-weight:600;letter-spacing:.05em;
  background:rgba(236,72,153,.12);color:var(--accent-2);border:1px solid rgba(236,72,153,.3);
}

/* Dock */
#dock-row{display:flex;justify-content:center;padding:6px 16px 8px;flex-shrink:0;overflow-x:auto}
#dock-wrap{display:flex;flex-direction:column;align-items:stretch;gap:6px}
.dock-label{
  display:flex;align-items:baseline;justify-content:space-between;gap:12px;
  padding:0 8px;
  font-family:var(--mono);font-size:11px;font-weight:600;color:var(--ink);
  text-transform:uppercase;letter-spacing:.16em;
}
.dock-label .dock-meta{color:var(--ink-3);font-weight:400;font-size:10px;letter-spacing:.04em;text-transform:none}
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
