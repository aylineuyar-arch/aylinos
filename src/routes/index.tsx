import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";

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
  svg: ReactNode;
};

const APPS: App[] = [
  {
    id: "job-search",
    name: "Job Search",
    tag: "358 tracked",
    gradient: "linear-gradient(145deg,#1e1b4b,#312e81)",
    accent: "#818cf8",
    svg: (
      <svg viewBox="0 0 80 56" width="44" height="32">
        <line x1="16" y1="18" x2="32" y2="18" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="48" y1="18" x2="62" y2="18" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="40" y1="26" x2="40" y2="38" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="62" y1="26" x2="62" y2="38" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <circle cx="8" cy="18" r="7" fill="#60a5fa" opacity=".9" />
        <circle cx="40" cy="18" r="7" fill="#818cf8" className="llm-pulse" />
        <circle cx="68" cy="18" r="7" fill="#34d399" opacity=".9" />
        <circle cx="40" cy="46" r="7" fill="#fb923c" opacity=".9" />
        <circle cx="68" cy="46" r="7" fill="#f472b6" opacity=".9" />
      </svg>
    ),
  },
  {
    id: "restaurant",
    name: "Fork Yeah!",
    tag: "8-node graph",
    gradient: "linear-gradient(145deg,#052e16,#065f46)",
    accent: "#34d399",
    svg: (
      <svg viewBox="0 0 80 56" width="44" height="32">
        <line x1="8" y1="28" x2="22" y2="18" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="8" y1="28" x2="22" y2="38" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="30" y1="18" x2="44" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="30" y1="38" x2="44" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="52" y1="28" x2="65" y2="18" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="52" y1="28" x2="65" y2="38" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <circle cx="8" cy="28" r="7" fill="#60a5fa" opacity=".9" />
        <circle cx="26" cy="18" r="6" fill="#60a5fa" opacity=".75" />
        <circle cx="26" cy="38" r="6" fill="#34d399" opacity=".75" />
        <circle cx="48" cy="28" r="7" fill="#818cf8" className="llm-pulse" />
        <circle cx="70" cy="18" r="6" fill="#fb923c" opacity=".9" />
        <circle cx="70" cy="38" r="6" fill="#facc15" opacity=".9" />
      </svg>
    ),
  },
  {
    id: "cs-triage",
    name: "CS Triage",
    tag: "Sub-1s route",
    gradient: "linear-gradient(145deg,#052e16,#166534)",
    accent: "#4ade80",
    svg: (
      <svg viewBox="0 0 80 56" width="44" height="32">
        <line x1="15" y1="28" x2="32" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="46" y1="22" x2="58" y2="12" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="46" y1="26" x2="58" y2="22" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="46" y1="30" x2="58" y2="34" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="46" y1="34" x2="58" y2="44" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <circle cx="8" cy="28" r="7" fill="#60a5fa" opacity=".9" />
        <circle cx="39" cy="28" r="7" fill="#818cf8" className="llm-pulse" />
        <circle cx="64" cy="11" r="5" fill="#fb923c" opacity=".85" />
        <circle cx="64" cy="23" r="5" fill="#34d399" opacity=".85" />
        <circle cx="64" cy="35" r="5" fill="#f472b6" opacity=".85" />
        <circle cx="64" cy="45" r="5" fill="#facc15" opacity=".85" />
      </svg>
    ),
  },
  {
    id: "networking",
    name: "Networking",
    tag: "130 targets",
    gradient: "linear-gradient(145deg,#0c1a3a,#1e3a8a)",
    accent: "#60a5fa",
    svg: (
      <svg viewBox="0 0 80 56" width="44" height="32">
        <line x1="15" y1="28" x2="27" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="41" y1="28" x2="53" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="60" y1="28" x2="72" y2="20" stroke="rgba(255,255,255,.18)" strokeWidth="1" />
        <line x1="60" y1="28" x2="72" y2="36" stroke="rgba(255,255,255,.18)" strokeWidth="1" />
        <circle cx="8" cy="28" r="7" fill="#60a5fa" opacity=".9" />
        <circle cx="34" cy="28" r="7" fill="#818cf8" className="llm-pulse" />
        <circle cx="60" cy="28" r="7" fill="#fb923c" opacity=".9" />
        <circle cx="74" cy="20" r="5" fill="#f472b6" opacity=".85" />
        <circle cx="74" cy="36" r="5" fill="#34d399" opacity=".85" />
      </svg>
    ),
  },
  {
    id: "outreach",
    name: "Outreach",
    tag: "Human-gated",
    gradient: "linear-gradient(145deg,#2e1065,#5b21b6)",
    accent: "#a78bfa",
    svg: (
      <svg viewBox="0 0 80 56" width="44" height="32">
        <line x1="15" y1="28" x2="27" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="41" y1="28" x2="53" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="67" y1="28" x2="75" y2="20" stroke="rgba(255,255,255,.18)" strokeWidth="1" strokeDasharray="2,2" />
        <line x1="67" y1="28" x2="75" y2="36" stroke="rgba(255,255,255,.18)" strokeWidth="1" strokeDasharray="2,2" />
        <circle cx="8" cy="28" r="7" fill="#60a5fa" opacity=".9" />
        <circle cx="34" cy="28" r="7" fill="#818cf8" className="llm-pulse" />
        <circle cx="60" cy="28" r="7" fill="#fb923c" opacity=".9" />
        <circle cx="76" cy="20" r="4" fill="#f472b6" opacity=".85" />
        <circle cx="76" cy="36" r="4" fill="#facc15" opacity=".85" />
      </svg>
    ),
  },
  {
    id: "evals",
    name: "Evals",
    tag: "v1 → v2",
    gradient: "linear-gradient(145deg,#1a0530,#3b0764)",
    accent: "#c084fc",
    svg: (
      <svg viewBox="0 0 80 56" width="44" height="32">
        <line x1="8" y1="18" x2="22" y2="18" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="8" y1="38" x2="22" y2="38" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="36" y1="18" x2="48" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="36" y1="38" x2="48" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="56" y1="28" x2="70" y2="18" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="56" y1="28" x2="70" y2="38" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <circle cx="8" cy="18" r="6" fill="#818cf8" opacity=".75" />
        <circle cx="8" cy="38" r="6" fill="#818cf8" opacity=".9" className="llm-pulse" />
        <circle cx="29" cy="18" r="6" fill="#60a5fa" opacity=".8" />
        <circle cx="29" cy="38" r="6" fill="#60a5fa" opacity=".8" />
        <circle cx="52" cy="28" r="7" fill="#34d399" opacity=".9" />
        <circle cx="74" cy="18" r="5" fill="#f472b6" opacity=".9" />
        <circle cx="74" cy="38" r="5" fill="#fb923c" opacity=".9" />
      </svg>
    ),
  },
  {
    id: "research",
    name: "Research",
    tag: "Fan-in brief",
    gradient: "linear-gradient(145deg,#500724,#9d174d)",
    accent: "#f472b6",
    svg: (
      <svg viewBox="0 0 80 56" width="44" height="32">
        <line x1="13" y1="12" x2="33" y2="26" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="13" y1="28" x2="33" y2="28" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="13" y1="44" x2="33" y2="30" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="47" y1="28" x2="59" y2="18" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <line x1="47" y1="28" x2="59" y2="38" stroke="rgba(255,255,255,.22)" strokeWidth="1.2" />
        <circle cx="8" cy="12" r="5" fill="#60a5fa" opacity=".75" />
        <circle cx="8" cy="28" r="5" fill="#60a5fa" opacity=".85" />
        <circle cx="8" cy="44" r="5" fill="#60a5fa" opacity=".75" />
        <circle cx="40" cy="28" r="7" fill="#818cf8" className="llm-pulse" />
        <circle cx="64" cy="18" r="6" fill="#fb923c" opacity=".9" />
        <circle cx="64" cy="38" r="6" fill="#34d399" opacity=".9" />
      </svg>
    ),
  },
];

const SUGGESTIONS = [
  { q: "should I apply to Ramp", agent: "Job Search", accent: "#818cf8" },
  { q: "prep me for Hebbia interview", agent: "Job Search", accent: "#818cf8" },
  { q: "book dinner in Soho tomorrow at 8", agent: "Fork Yeah!", accent: "#34d399" },
  { q: "draft intro to Sarah at Sequoia", agent: "Outreach", accent: "#a78bfa" },
  { q: "research Cursor's GTM motion", agent: "Research", accent: "#f472b6" },
  { q: "triage today's support inbox", agent: "CS Triage", accent: "#4ade80" },
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
              <span className="sb-dot pulse" style={{ background: "#818cf8" }} />
              <span>Claude</span>
            </div>
            <div className="sb-pill">
              <span className="sb-dot pulse" style={{ background: "#60a5fa", animationDelay: ".4s" }} />
              <span>Tavily</span>
            </div>
            <div className="sb-pill">
              <span className="sb-dot pulse" style={{ background: "#34d399", animationDelay: ".8s" }} />
              <span>SQLite</span>
            </div>
            <span className="sb-divider" />
            <div className="sb-pill">
              <span className="sb-dot" style={{ background: "#34d399" }} />
              <span>
                <b>7</b> agents · <b>0</b> active
              </span>
            </div>
            <div className="sb-pill">
              <span className="sb-dot" style={{ background: "#fb923c", opacity: 0.7 }} />
              <span>
                <b>$0.00</b> today
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

        {/* Output / suggestions panel — fills the dead space intentionally */}
        <section id="output-panel">
          <div id="output-card">
            <header id="output-header">
              <span id="agent-dot" style={{ background: "#34d399" }} />
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
                    <span className="suggest-agent" style={{ color: s.accent, borderColor: `${s.accent}33`, background: `${s.accent}10` }}>
                      {s.agent}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="sec-label">Recent</div>
              <div className="recent-row">
                <span className="recent-time">14m</span>
                <span className="recent-text">
                  <b style={{ color: "#f0f0f5" }}>Research</b> · synthesized Cursor GTM brief from 3 sources → Drive
                </span>
              </div>
              <div className="recent-row">
                <span className="recent-time">2h</span>
                <span className="recent-text">
                  <b style={{ color: "#f0f0f5" }}>Job Search</b> · scored 12 new Greenhouse listings, 2 above threshold
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
              <div className="tel-val">$0.000</div>
              <div className="tel-key">API cost</div>
            </div>
            <div className="tel-cell">
              <div className="tel-val">0</div>
              <div className="tel-key">Calls</div>
            </div>
            <div className="tel-cell">
              <div className="tel-val" style={{ color: "#818cf8" }}>v2</div>
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
                  {a.svg}
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
  --bg:#070710;
  --bg-2:#0d0d18;
  --ink:#f0f0f5;
  --ink-2:rgba(240,240,245,.62);
  --ink-3:rgba(240,240,245,.32);
  --ink-4:rgba(240,240,245,.18);
  --b:rgba(255,255,255,.07);
  --b-2:rgba(255,255,255,.12);
  --mono:'JetBrains Mono','SF Mono','Menlo',monospace;
  --sans:'Inter',system-ui,sans-serif;
  --accent:#818cf8;
}
html,body{height:100%;overflow:hidden;font-family:var(--sans);background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased}

@keyframes llm{0%,100%{opacity:.95;r:7}50%{opacity:.55;r:8.5}}
.llm-pulse{animation:llm 2.8s ease-in-out infinite;transform-origin:center}
@keyframes dot-pulse{0%,100%{opacity:1}50%{opacity:.35}}

#screen{
  width:100vw;height:100vh;display:flex;flex-direction:column;
  background-color:var(--bg);
  background-image:
    radial-gradient(ellipse 70% 45% at 50% -5%, rgba(99,102,241,.18) 0%, transparent 55%),
    radial-gradient(ellipse 45% 35% at 8% 92%, rgba(52,211,153,.07) 0%, transparent 50%),
    radial-gradient(ellipse 40% 30% at 95% 65%, rgba(244,114,182,.06) 0%, transparent 50%),
    radial-gradient(circle at 1px 1px, rgba(255,255,255,.035) 1px, transparent 0);
  background-size:auto,auto,auto,24px 24px;
}

/* Status bar */
#sb{
  height:34px;flex-shrink:0;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 22px;
  background:rgba(7,7,16,.72);
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
.prompt-h1{
  font-size:28px;font-weight:600;letter-spacing:-.025em;line-height:1.15;color:var(--ink);
  margin-top:2px;
}
.prompt-name{
  background:linear-gradient(135deg,#a5b4fc 0%,#818cf8 50%,#c084fc 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
}
.prompt-sub{font-size:13px;color:var(--ink-3);letter-spacing:.005em;margin-top:2px}

.search-wrap{width:100%;max-width:680px;position:relative}
.search-caret{
  position:absolute;left:20px;top:50%;transform:translateY(-50%);
  font-family:var(--mono);font-size:18px;color:var(--accent);font-weight:600;
  text-shadow:0 0 12px rgba(129,140,248,.6);
}
#search-bar{
  width:100%;
  background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.02));
  border:1px solid var(--b-2);
  border-radius:14px;
  padding:17px 60px 17px 44px;
  font-family:var(--sans);font-size:15px;font-weight:400;
  color:var(--ink);outline:none;
  transition:border-color 160ms,box-shadow 160ms,background 160ms;
  box-shadow:0 1px 0 rgba(255,255,255,.04) inset, 0 8px 24px rgba(0,0,0,.35);
}
#search-bar::placeholder{color:var(--ink-3);font-weight:400}
#search-bar:focus{
  border-color:rgba(129,140,248,.55);
  box-shadow:0 0 0 4px rgba(129,140,248,.1), 0 1px 0 rgba(255,255,255,.06) inset, 0 8px 32px rgba(99,102,241,.18);
  background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.025));
}
.search-cmd{
  position:absolute;right:14px;top:50%;transform:translateY(-50%);
  font-family:var(--mono);font-size:10.5px;font-weight:600;
  color:var(--ink-2);
  padding:4px 8px;border-radius:5px;
  background:rgba(255,255,255,.05);border:1px solid var(--b-2);
  pointer-events:none;letter-spacing:.04em;
}

/* Output / suggestions panel */
#output-panel{
  flex:1;min-height:0;width:100%;max-width:720px;
  margin:0 auto;padding:18px 24px 14px;
  display:flex;flex-direction:column;
}
#output-card{
  background:linear-gradient(180deg,rgba(17,17,24,.95),rgba(13,13,20,.95));
  border:1px solid var(--b);
  border-radius:12px;
  overflow:hidden;flex:1;display:flex;flex-direction:column;min-height:0;
  box-shadow:0 12px 40px rgba(0,0,0,.4), 0 1px 0 rgba(255,255,255,.04) inset;
}
#output-header{
  display:flex;align-items:center;gap:10px;
  padding:11px 16px;border-bottom:1px solid var(--b);flex-shrink:0;
  background:rgba(255,255,255,.015);
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
  text-transform:uppercase;letter-spacing:.14em;
  margin:14px 0 8px;
}
.sec-label:first-child{margin-top:0}

.suggest-list{list-style:none;display:flex;flex-direction:column;gap:2px}
.suggest-row{
  display:flex;align-items:center;gap:12px;
  padding:7px 10px;margin:0 -10px;border-radius:7px;
  cursor:pointer;transition:background 120ms;
}
.suggest-row:hover{background:rgba(255,255,255,.035)}
.suggest-arrow{font-family:var(--mono);font-size:11px;color:var(--ink-4);width:10px;flex-shrink:0}
.suggest-row:hover .suggest-arrow{color:var(--accent)}
.suggest-q{flex:1;font-family:var(--sans);font-size:13px;color:var(--ink);font-weight:400;letter-spacing:-.005em}
.suggest-agent{
  font-family:var(--mono);font-size:9.5px;font-weight:600;
  padding:3px 8px;border-radius:4px;border:1px solid;
  letter-spacing:.04em;text-transform:uppercase;
  flex-shrink:0;
}
.recent-row{
  display:flex;align-items:flex-start;gap:14px;
  padding:5px 0;
}
.recent-time{
  font-family:var(--mono);font-size:10px;color:var(--ink-3);
  width:34px;flex-shrink:0;padding-top:1px;letter-spacing:.02em;
}
.recent-text{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);line-height:1.55;letter-spacing:-.003em}

/* Telemetry strip */
#telem{flex-shrink:0;display:flex;justify-content:center;padding:4px 24px 10px}
#telem-inner{
  display:flex;align-items:stretch;
  background:rgba(255,255,255,.025);
  border:1px solid rgba(255,255,255,.06);
  border-radius:9px;overflow:hidden;
  backdrop-filter:blur(10px);
}
.tel-cell{
  padding:6px 16px;border-right:1px solid rgba(255,255,255,.05);
  text-align:center;text-decoration:none;display:block;
  transition:background 150ms;
}
.tel-cell:last-child{border-right:none}
.tel-cell.clickable{cursor:pointer}
.tel-cell.clickable:hover{background:rgba(255,255,255,.04)}
.tel-val{font-family:var(--mono);font-size:11.5px;font-weight:600;color:var(--ink);letter-spacing:.01em}
.tel-key{font-family:var(--mono);font-size:9px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.1em;margin-top:2px}
.tel-badge{
  display:inline-block;padding:1px 6px;border-radius:3px;
  font-family:var(--mono);font-size:8.5px;font-weight:600;margin-left:5px;letter-spacing:.05em;
  background:rgba(251,146,60,.12);color:#fb923c;border:1px solid rgba(251,146,60,.25);
}

/* Dock */
#dock-row{display:flex;justify-content:center;padding:8px 16px 22px;flex-shrink:0;overflow-x:auto}
#dock{
  display:flex;align-items:flex-start;gap:6px;
  padding:14px 16px 12px;
  background:rgba(255,255,255,.05);
  backdrop-filter:blur(40px) saturate(1.6);
  border:1px solid rgba(255,255,255,.1);
  border-radius:22px;flex-shrink:0;
  box-shadow:0 20px 50px rgba(0,0,0,.5), 0 1px 0 rgba(255,255,255,.08) inset;
}
.di-cell{
  display:flex;flex-direction:column;align-items:center;gap:6px;
  width:78px;cursor:pointer;padding:2px 4px;
}
.di{
  width:54px;height:54px;border-radius:13px;
  display:flex;align-items:center;justify-content:center;overflow:hidden;
  box-shadow:0 4px 14px rgba(0,0,0,.5), 0 1px 0 rgba(255,255,255,.12) inset, 0 -1px 0 rgba(0,0,0,.35) inset;
  transition:transform 220ms cubic-bezier(.34,1.4,.64,1), box-shadow 220ms;
}
.di-cell:hover .di{transform:translateY(-6px) scale(1.08);box-shadow:0 14px 30px rgba(0,0,0,.6), 0 1px 0 rgba(255,255,255,.16) inset}
.di-cell:active .di{transform:scale(.94);transition-duration:80ms}
.di-label{
  font-family:var(--sans);font-size:10.5px;font-weight:500;
  color:var(--ink);letter-spacing:-.005em;text-align:center;
  text-shadow:0 1px 4px rgba(0,0,0,.7);
  margin-top:1px;
}
.di-tag{
  font-family:var(--mono);font-size:8.5px;color:var(--ink-3);
  text-transform:uppercase;letter-spacing:.08em;text-align:center;
}

@media (prefers-reduced-motion:reduce){
  .di,.llm-pulse,.sb-dot,#agent-dot{animation:none;transition:none}
}
`;
