import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import iconJobSearch from "@/assets/icon-job-search.png";
import iconRestaurant from "@/assets/icon-restaurant.png";
import iconCsTriage from "@/assets/icon-cs-triage.png";
import iconNetworking from "@/assets/icon-networking.png";
import iconOutreach from "@/assets/icon-outreach.png";
import iconEvals from "@/assets/icon-evals.png";
import iconResearch from "@/assets/icon-research.png";

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
  icon: string;
};

const APPS: App[] = [
  { id: "job-search", name: "Job Search", tag: "358 tracked",  gradient: "linear-gradient(145deg,#e0e7ff,#c7d2fe)", accent: "#6366f1", icon: iconJobSearch },
  { id: "restaurant", name: "Fork Yeah!", tag: "8-node graph", gradient: "linear-gradient(145deg,#d1fae5,#a7f3d0)", accent: "#059669", icon: iconRestaurant },
  { id: "cs-triage",  name: "CS Triage",  tag: "Sub-1s route", gradient: "linear-gradient(145deg,#dcfce7,#bbf7d0)", accent: "#16a34a", icon: iconCsTriage },
  { id: "networking", name: "Networking", tag: "130 targets",  gradient: "linear-gradient(145deg,#dbeafe,#bfdbfe)", accent: "#2563eb", icon: iconNetworking },
  { id: "outreach",   name: "Outreach",   tag: "Human-gated",  gradient: "linear-gradient(145deg,#ede9fe,#ddd6fe)", accent: "#7c3aed", icon: iconOutreach },
  { id: "evals",      name: "Evals",      tag: "v1 → v2",      gradient: "linear-gradient(145deg,#f3e8ff,#e9d5ff)", accent: "#9333ea", icon: iconEvals },
  { id: "research",   name: "Research",   tag: "Fan-in brief", gradient: "linear-gradient(145deg,#fce7f3,#fbcfe8)", accent: "#db2777", icon: iconResearch },
];

const SUGGESTIONS = [
  { q: "should I apply to Ramp", agent: "Job Search", accent: "#6366f1" },
  { q: "prep me for Hebbia interview", agent: "Job Search", accent: "#6366f1" },
  { q: "book dinner in Soho tomorrow at 8", agent: "Fork Yeah!", accent: "#059669" },
  { q: "draft intro to Sarah at Sequoia", agent: "Outreach", accent: "#7c3aed" },
  { q: "research Cursor's GTM motion", agent: "Research", accent: "#db2777" },
  { q: "triage today's support inbox", agent: "CS Triage", accent: "#16a34a" },
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

function Home() {
  const clock = useClock();
  return (
    <>
      <style>{CSS}</style>
      <div id="screen">
        {/* Status bar */}
        <div id="sb">
          <div className="sb-left">
            <span className="sb-brand">AylinOS</span>
            <span className="sb-divider" />
            <span className="sb-ver">v2.4.1</span>
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
            <span className="prompt-eyebrow">// session 04 · ready</span>
            <h1 className="prompt-h1">
              What can I help you with, <span className="prompt-name">Aylin</span>?
            </h1>
            <p className="prompt-sub">Route a task to an agent, or ask anything. Press ⌘K to focus.</p>
          </div>

          <div className="search-wrap">
            <span className="search-caret">›</span>
            <input
              id="search-bar"
              type="text"
              placeholder="should I apply to Ramp · prep me for Hebbia interview · book dinner in Soho…"
              autoComplete="off"
              spellCheck={false}
            />
            <span className="search-cmd">⌘K</span>
          </div>
        </section>

        {/* Output / suggestions panel */}
        <section id="output-panel">
          <div id="output-card">
            <header id="output-header">
              <span id="agent-dot" style={{ background: "#10b981" }} />
              <span id="agent-name">stdin · awaiting prompt</span>
              <span className="output-meta">7 agents online · last run 14m ago</span>
            </header>
            <div id="output-body">
              <div className="sec-label">Try one of these</div>
              <ul className="suggest-list">
                {SUGGESTIONS.map((s) => (
                  <li key={s.q} className="suggest-row">
                    <span className="suggest-arrow">→</span>
                    <span className="suggest-q">{s.q}</span>
                    <span
                      className="suggest-agent"
                      style={{ color: s.accent, borderColor: `${s.accent}40`, background: `${s.accent}12` }}
                    >
                      {s.agent}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="sec-label">Recent</div>
              <div className="recent-row">
                <span className="recent-time">14m</span>
                <span className="recent-text">
                  <b>Research</b> · synthesized Cursor GTM brief from 3 sources → Drive
                </span>
              </div>
              <div className="recent-row">
                <span className="recent-time">2h</span>
                <span className="recent-text">
                  <b>Job Search</b> · scored 12 new Greenhouse listings, 2 above threshold
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Telemetry strip */}
        <div id="telem">
          <div id="telem-inner">
            <a href="/evals" className="tel-cell clickable">
              <div className="tel-val">
                — <span className="tel-badge">run evals</span>
              </div>
              <div className="tel-key">F1</div>
            </a>
            <div className="tel-cell">
              <div className="tel-val">—</div>
              <div className="tel-key">Precision</div>
            </div>
            <div className="tel-cell">
              <div className="tel-val">—</div>
              <div className="tel-key">Recall</div>
            </div>
            <div className="tel-cell">
              <div className="tel-val">0</div>
              <div className="tel-key">Calls</div>
            </div>

            <div className="tel-cell">
              <div className="tel-val" style={{ color: "#6366f1" }}>v2</div>
              <div className="tel-key">Prompt</div>
            </div>
          </div>
        </div>

        {/* Dock */}
        <div id="dock-row">
          <div id="dock">
            {APPS.map((a) => (
              <div className="di-cell" key={a.id} title={a.name}>
                <div className="di" style={{ background: a.gradient }}>
                  <img src={a.icon} alt={a.name} width={512} height={512} loading="lazy" />
                </div>
                <div className="di-label">{a.name}</div>
                <div className="di-tag">{a.tag}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

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
  width:100vw;height:100vh;display:flex;flex-direction:column;
  background-color:var(--bg);
  background-image:
    radial-gradient(ellipse 70% 45% at 50% -5%, rgba(99,102,241,.14) 0%, transparent 60%),
    radial-gradient(ellipse 45% 35% at 8% 92%, rgba(16,185,129,.08) 0%, transparent 55%),
    radial-gradient(ellipse 40% 30% at 95% 65%, rgba(244,114,182,.08) 0%, transparent 55%),
    radial-gradient(circle at 1px 1px, rgba(26,26,36,.045) 1px, transparent 0);
  background-size:auto,auto,auto,24px 24px;
}

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
  padding:48px 24px 18px;
}
.prompt-row{text-align:center;margin-bottom:22px;display:flex;flex-direction:column;align-items:center;gap:6px}
.prompt-eyebrow{font-family:var(--mono);font-size:10px;color:var(--ink-3);letter-spacing:.18em;text-transform:uppercase}
.prompt-h1{font-size:28px;font-weight:600;letter-spacing:-.025em;line-height:1.15;color:var(--ink);margin-top:2px}
.prompt-name{
  color:var(--accent);
}
.prompt-sub{font-size:13px;color:var(--ink-3);margin-top:2px}

.search-wrap{width:100%;max-width:680px;position:relative}
.search-caret{
  position:absolute;left:20px;top:50%;transform:translateY(-50%);
  font-family:var(--mono);font-size:18px;color:var(--accent);font-weight:600;
}
#search-bar{
  width:100%;
  background:rgba(255,255,255,.85);
  border:1px solid var(--b-2);
  border-radius:14px;
  padding:17px 60px 17px 44px;
  font-family:var(--sans);font-size:15px;color:var(--ink);outline:none;
  transition:border-color 160ms,box-shadow 160ms,background 160ms;
  box-shadow:0 1px 0 rgba(255,255,255,.7) inset, 0 6px 20px rgba(26,26,36,.06);
}
#search-bar::placeholder{color:var(--ink-3)}
#search-bar:focus{
  border-color:rgba(99,102,241,.5);
  box-shadow:0 0 0 4px rgba(99,102,241,.12), 0 6px 24px rgba(99,102,241,.14);
  background:#fff;
}
.search-cmd{
  position:absolute;right:14px;top:50%;transform:translateY(-50%);
  font-family:var(--mono);font-size:10.5px;font-weight:600;color:var(--ink-2);
  padding:4px 8px;border-radius:5px;
  background:rgba(255,255,255,.9);border:1px solid var(--b-2);
  pointer-events:none;letter-spacing:.04em;
}

/* Output / suggestions panel */
#output-panel{
  flex:1;min-height:0;width:100%;max-width:720px;
  margin:0 auto;padding:18px 24px 14px;
  display:flex;flex-direction:column;
}
#output-card{
  background:rgba(255,255,255,.72);
  border:1px solid var(--b);
  border-radius:14px;
  overflow:hidden;flex:1;display:flex;flex-direction:column;min-height:0;
  box-shadow:0 12px 36px rgba(26,26,36,.08), 0 1px 0 rgba(255,255,255,.8) inset;
  backdrop-filter:blur(12px);
}
#output-header{
  display:flex;align-items:center;gap:10px;
  padding:11px 16px;border-bottom:1px solid var(--b);flex-shrink:0;
  background:rgba(255,255,255,.4);
}
#agent-dot{width:6px;height:6px;border-radius:50%;animation:dot-pulse 1.6s ease-in-out infinite;box-shadow:0 0 8px currentColor}
#agent-name{font-family:var(--mono);font-size:11px;color:var(--ink-2);letter-spacing:.02em}
.output-meta{margin-left:auto;font-family:var(--mono);font-size:10px;color:var(--ink-3);letter-spacing:.02em}
#output-body{
  padding:14px 18px 16px;flex:1;overflow-y:auto;
  font-family:var(--mono);font-size:12px;color:var(--ink-2);line-height:1.7;
}
.sec-label{
  display:block;font-family:var(--mono);font-size:9.5px;color:var(--ink-3);
  text-transform:uppercase;letter-spacing:.14em;margin:14px 0 8px;
}
.sec-label:first-child{margin-top:0}

.suggest-list{list-style:none;display:flex;flex-direction:column;gap:2px}
.suggest-row{
  display:flex;align-items:center;gap:12px;
  padding:7px 10px;margin:0 -10px;border-radius:7px;
  cursor:pointer;transition:background 120ms;
}
.suggest-row:hover{background:rgba(99,102,241,.06)}
.suggest-arrow{font-family:var(--mono);font-size:11px;color:var(--ink-4);width:10px;flex-shrink:0}
.suggest-row:hover .suggest-arrow{color:var(--accent)}
.suggest-q{flex:1;font-family:var(--sans);font-size:13px;color:var(--ink);letter-spacing:-.005em}
.suggest-agent{
  font-family:var(--mono);font-size:9.5px;font-weight:600;
  padding:3px 8px;border-radius:4px;border:1px solid;
  letter-spacing:.04em;text-transform:uppercase;flex-shrink:0;
}
.recent-row{display:flex;align-items:flex-start;gap:14px;padding:5px 0}
.recent-time{font-family:var(--mono);font-size:10px;color:var(--ink-3);width:34px;flex-shrink:0;padding-top:1px;letter-spacing:.02em}
.recent-text{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);line-height:1.55;letter-spacing:-.003em}
.recent-text b{color:var(--ink);font-weight:600}

/* Telemetry strip */
#telem{flex-shrink:0;display:flex;justify-content:center;padding:4px 24px 10px}
#telem-inner{
  display:flex;align-items:stretch;
  background:rgba(255,255,255,.6);
  border:1px solid var(--b);
  border-radius:9px;overflow:hidden;backdrop-filter:blur(10px);
}
.tel-cell{
  padding:6px 16px;border-right:1px solid var(--b);
  text-align:center;text-decoration:none;display:block;transition:background 150ms;
}
.tel-cell:last-child{border-right:none}
.tel-cell.clickable{cursor:pointer}
.tel-cell.clickable:hover{background:rgba(99,102,241,.08)}
.tel-val{font-family:var(--mono);font-size:11.5px;font-weight:600;color:var(--ink);letter-spacing:.01em}
.tel-key{font-family:var(--mono);font-size:9px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.1em;margin-top:2px}
.tel-badge{
  display:inline-block;padding:1px 6px;border-radius:3px;
  font-family:var(--mono);font-size:8.5px;font-weight:600;margin-left:5px;letter-spacing:.05em;
  background:rgba(234,88,12,.1);color:#ea580c;border:1px solid rgba(234,88,12,.25);
}

/* Dock */
#dock-row{display:flex;justify-content:center;padding:8px 16px 22px;flex-shrink:0;overflow-x:auto}
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
  width:56px;height:56px;border-radius:14px;
  display:flex;align-items:center;justify-content:center;overflow:hidden;
  box-shadow:0 4px 14px rgba(26,26,36,.14), 0 1px 0 rgba(255,255,255,.8) inset;
  transition:transform 220ms cubic-bezier(.34,1.4,.64,1), box-shadow 220ms;
}
.di img{
  width:92%;height:92%;object-fit:contain;
  image-rendering:-webkit-optimize-contrast;
  image-rendering:crisp-edges;
  -webkit-backface-visibility:hidden;backface-visibility:hidden;
  transform:translateZ(0);
}
.di-cell:hover .di{transform:translateY(-6px) scale(1.08);box-shadow:0 14px 28px rgba(26,26,36,.2), 0 1px 0 rgba(255,255,255,.9) inset}
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
