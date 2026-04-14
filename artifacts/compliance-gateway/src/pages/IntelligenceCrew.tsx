import { useState, useRef, useEffect, useCallback } from "react";
import {
  Database,
  Languages,
  TrendingUp,
  Telescope,
  SendHorizonal,
  Loader2,
  RotateCcw,
  ShieldCheck,
  Brain,
  StopCircle,
  Copy,
  Check,
  ChevronDown,
  Map,
  Zap,
  BarChart3,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

type AgentId = "data_indexer" | "dialect_specialist" | "behavior_forecaster" | "intelligence_lead";

type AgentMeta = {
  id: AgentId;
  role: string;
  framework: string;
  color: string;
  bg: string;
  border: string;
  desc: string;
  icon: React.ElementType;
};

const AGENTS: AgentMeta[] = [
  {
    id: "data_indexer",
    role: "Data Indexer",
    framework: "LlamaIndex",
    color: "#38bdf8",
    bg: "bg-sky-500/10",
    border: "border-sky-500/30",
    desc: "Retrieves electoral and demographic data via vector indexing",
    icon: Database,
  },
  {
    id: "dialect_specialist",
    role: "Dialect Specialist",
    framework: "Meta-Llama-3.1-8B",
    color: "#4ade80",
    bg: "bg-green-500/10",
    border: "border-green-500/30",
    desc: "Analyzes Punjabi Shahmukhi & Saraiki cultural signals",
    icon: Languages,
  },
  {
    id: "behavior_forecaster",
    role: "Behavior Forecaster",
    framework: "LightGBM",
    color: "#fb923c",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    desc: "Predicts voter segments using gradient-boosted forecasting",
    icon: TrendingUp,
  },
  {
    id: "intelligence_lead",
    role: "Intelligence Lead",
    framework: "Synthesis",
    color: "#c084fc",
    bg: "bg-purple-500/10",
    border: "border-purple-500/30",
    desc: "Synthesizes all intelligence into an operational brief",
    icon: Telescope,
  },
];

const REGIONS = [
  "Lahore Central",
  "Multan",
  "Bahawalpur",
  "Rahim Yar Khan",
  "DG Khan",
  "Faisalabad North",
  "Gujranwala",
  "Sialkot",
  "Rawalpindi",
  "Muzaffargarh",
  "Khanewal",
  "Lodhran",
  "Vehari",
  "Jhang",
  "Sargodha",
  "Mianwali",
  "Custom Region",
];

const LANGUAGES = [
  { code: "en", label: "English", native: "English" },
  { code: "pa", label: "Punjabi (Shahmukhi)", native: "پنجابی (شاہ مکھی)" },
  { code: "skr", label: "Saraiki", native: "سرائیکی" },
  { code: "ur", label: "Urdu", native: "اردو" },
];

const EXAMPLE_QUERIES = [
  "Analyze voter sentiment and turnout likelihood for the upcoming by-election",
  "Identify top swing voter segments and their key concerns in this constituency",
  "Forecast rural vs urban voter behavior split and key mobilization factors",
  "Assess impact of economic grievances on traditional party loyalty in the region",
];

const SEGMENT_COLORS = ["#60a5fa", "#4ade80", "#fb923c", "#f87171"];

type AgentTurn = {
  agentId: AgentId;
  role: string;
  framework: string;
  color: string;
  content: string;
  done: boolean;
};

type RunState = "idle" | "running" | "done" | "error";

function AgentCard({
  agent,
  active,
  done,
}: {
  agent: AgentMeta;
  active: boolean;
  done: boolean;
}) {
  const Icon = agent.icon;
  return (
    <div
      className={`rounded-xl border p-3.5 transition-all duration-300 ${
        active
          ? `${agent.bg} ${agent.border} shadow-lg`
          : done
          ? "bg-muted/20 border-border/60 opacity-60"
          : "bg-muted/10 border-border/40"
      }`}
    >
      <div className="flex items-center gap-2.5 mb-1">
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
          style={{ backgroundColor: `${agent.color}20`, border: `1px solid ${agent.color}40` }}
        >
          <Icon className="w-3.5 h-3.5" style={{ color: agent.color }} />
        </div>
        <div className="flex items-center gap-1.5 flex-1 min-w-0">
          <span className="text-xs font-semibold text-foreground truncate">{agent.role}</span>
          {active && <Loader2 className="w-3 h-3 animate-spin shrink-0" style={{ color: agent.color }} />}
          {done && !active && <Check className="w-3 h-3 text-emerald-400 shrink-0" />}
        </div>
      </div>
      <p className="text-xs text-muted-foreground/70 mb-1">{agent.desc}</p>
      <span
        className="text-xs font-mono px-1.5 py-0.5 rounded border"
        style={{ color: agent.color, backgroundColor: `${agent.color}10`, borderColor: `${agent.color}30` }}
      >
        {agent.framework}
      </span>
    </div>
  );
}

function AgentMessage({ turn }: { turn: AgentTurn }) {
  const agent = AGENTS.find((a) => a.id === turn.agentId);
  const Icon = agent?.icon ?? Database;
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(turn.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="group">
      <div className="flex items-center gap-2 mb-2">
        <div
          className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
          style={{ backgroundColor: `${turn.color}20`, border: `1px solid ${turn.color}40` }}
        >
          <Icon className="w-3 h-3" style={{ color: turn.color }} />
        </div>
        <span className="text-xs font-semibold" style={{ color: turn.color }}>{turn.role}</span>
        <span className="text-xs text-muted-foreground/60 font-mono">· {turn.framework}</span>
        {!turn.done && <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />}
        {turn.done && (
          <button onClick={copy} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-muted/40">
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-muted-foreground" />}
          </button>
        )}
      </div>
      <div
        className="ml-8 text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap rounded-xl p-4 border"
        style={{ backgroundColor: `${turn.color}08`, borderColor: `${turn.color}20` }}
        dir={turn.agentId === "dialect_specialist" ? "auto" : "ltr"}
      >
        {turn.content}
        {!turn.done && (
          <span className="inline-block w-1.5 h-4 ml-0.5 rounded-sm animate-pulse" style={{ backgroundColor: turn.color }} />
        )}
      </div>
    </div>
  );
}

function VoterSegmentChart({ content }: { content: string }) {
  const segments = [
    { name: "Committed", value: 0, color: "#60a5fa" },
    { name: "Persuadable", value: 0, color: "#4ade80" },
    { name: "Swing", value: 0, color: "#fb923c" },
    { name: "Disengaged", value: 0, color: "#f87171" },
  ];

  const patterns = [
    { key: "Committed", regex: /Committed[:\s]+(\d+)%?/i },
    { key: "Persuadable", regex: /Persuadable[:\s]+(\d+)%?/i },
    { key: "Swing", regex: /Swing[:\s]+(\d+)%?/i },
    { key: "Disengaged", regex: /Disengaged[:\s]+(\d+)%?/i },
  ];

  let hasData = false;
  for (const { key, regex } of patterns) {
    const match = content.match(regex);
    if (match) {
      const seg = segments.find((s) => s.name === key);
      if (seg) {
        seg.value = parseInt(match[1]);
        hasData = true;
      }
    }
  }

  if (!hasData) return null;

  return (
    <div className="rounded-xl border border-border bg-card p-4 mt-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-muted-foreground" />
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Voter Segment Forecast
        </span>
      </div>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={segments} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
          <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
            formatter={(v) => [`${v}%`, ""]}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {segments.map((s, i) => (
              <Cell key={i} fill={SEGMENT_COLORS[i]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function IntelligenceCrew() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [query, setQuery] = useState("");
  const [region, setRegion] = useState(REGIONS[0]);
  const [customRegion, setCustomRegion] = useState("");
  const [language, setLanguage] = useState(LANGUAGES[0]);
  const [langOpen, setLangOpen] = useState(false);
  const [runState, setRunState] = useState<RunState>("idle");
  const [turns, setTurns] = useState<AgentTurn[]>([]);
  const [activeAgent, setActiveAgent] = useState<AgentId | null>(null);
  const [doneAgents, setDoneAgents] = useState<Set<AgentId>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [forecasterContent, setForecasterContent] = useState("");

  const abortRef = useRef<AbortController | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sessionStorage.getItem("compliance_acknowledged") !== "true") {
      setLocation("/");
    }
  }, []);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [turns]);

  const effectiveRegion = region === "Custom Region" ? customRegion || "Custom Region" : region;

  const runPipeline = useCallback(async () => {
    if (!query.trim() || runState === "running") return;

    setRunState("running");
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);
    setForecasterContent("");

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch("/api/intelligence/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query.trim(),
          region: effectiveRegion,
          language: `${language.label} (${language.native})`,
          session_id: sessionId,
        }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) throw new Error(`API error: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;
          let event: Record<string, unknown>;
          try { event = JSON.parse(raw); } catch { continue; }

          if (event.type === "agent_start") {
            const agentId = event.agent as AgentId;
            const meta = AGENTS.find((a) => a.id === agentId);
            if (!meta) continue;
            setActiveAgent(agentId);
            setTurns((prev) => [
              ...prev,
              { agentId, role: meta.role, framework: meta.framework, color: meta.color, content: "", done: false },
            ]);
          } else if (event.type === "token") {
            const agentId = event.agent as AgentId;
            const tok = event.content as string;
            setTurns((prev) =>
              prev.map((t) => t.agentId === agentId && !t.done ? { ...t, content: t.content + tok } : t)
            );
            if (agentId === "behavior_forecaster") {
              setForecasterContent((prev) => prev + tok);
            }
          } else if (event.type === "agent_done") {
            const agentId = event.agent as AgentId;
            setTurns((prev) => prev.map((t) => t.agentId === agentId ? { ...t, done: true } : t));
            setDoneAgents((prev) => new Set([...prev, agentId]));
            setActiveAgent(null);
          } else if (event.type === "done") {
            setRunState("done");
          } else if (event.type === "error") {
            setError((event.message as string) ?? "Unknown error");
            setRunState("error");
          }
        }
      }
      setRunState("done");
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setError("The pipeline was interrupted. Please try again.");
        setRunState("error");
      } else {
        setRunState("idle");
      }
    }
  }, [query, region, customRegion, language, runState, sessionId, effectiveRegion]);

  const reset = () => {
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);
    setRunState("idle");
    setForecasterContent("");
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top bar */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-green-500/10 border border-green-500/30 flex items-center justify-center">
              <Telescope className="w-4 h-4 text-green-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Intelligence Crew</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 2</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-green-400" />
              <span className="text-xs text-muted-foreground">LlamaIndex · LightGBM · Meta-Llama-3.1</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setLocation("/tool")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Brain className="w-3.5 h-3.5" />
              TIER 1
            </button>
            <button
              onClick={() => setLocation("/media-crew")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Zap className="w-3.5 h-3.5" />
              Media Crew
            </button>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden sm:inline">Compliance verified</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 flex flex-col lg:flex-row gap-6">
        {/* Left: agents + config */}
        <aside className="lg:w-80 shrink-0 flex flex-col gap-4">
          {/* Agent crew */}
          <div className="rounded-2xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 mb-4">
              <Telescope className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Intelligence Crew</span>
            </div>
            <div className="flex flex-col gap-2">
              {AGENTS.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  active={activeAgent === agent.id}
                  done={doneAgents.has(agent.id)}
                />
              ))}
            </div>
          </div>

          {/* Region selector */}
          <div className="rounded-xl border border-border bg-card p-4">
            <label className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              <Map className="w-3.5 h-3.5" />
              Constituency / Region
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              disabled={runState === "running"}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
            >
              {REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
            {region === "Custom Region" && (
              <input
                type="text"
                value={customRegion}
                onChange={(e) => setCustomRegion(e.target.value)}
                placeholder="Enter region name..."
                className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            )}
          </div>

          {/* Language selector */}
          <div className="rounded-xl border border-border bg-card p-4">
            <label className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              <Languages className="w-3.5 h-3.5" />
              Primary Language
            </label>
            <div className="relative">
              <button
                onClick={() => setLangOpen((o) => !o)}
                className="w-full flex items-center justify-between rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground hover:bg-muted/30 transition-colors"
              >
                <span>
                  {language.label}
                  <span className="ml-2 text-muted-foreground" dir="rtl">{language.native}</span>
                </span>
                <ChevronDown className="w-4 h-4 text-muted-foreground" />
              </button>
              {langOpen && (
                <div className="absolute top-full mt-1 w-full rounded-xl border border-border bg-card shadow-xl z-20 overflow-hidden">
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => { setLanguage(lang); setLangOpen(false); }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 text-sm hover:bg-muted/40 transition-colors ${
                        language.code === lang.code ? "bg-primary/10 text-primary" : "text-foreground"
                      }`}
                    >
                      <span>{lang.label}</span>
                      <span className="text-muted-foreground text-xs" dir="rtl">{lang.native}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </aside>

        {/* Main panel */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Query input */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Intelligence Query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe what voter intelligence you need for this constituency..."
              rows={3}
              disabled={runState === "running"}
              dir={["pa", "skr", "ur"].includes(language.code) ? "auto" : "ltr"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
              onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline(); }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example queries:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_QUERIES.map((q) => (
                    <button
                      key={q}
                      onClick={() => setQuery(q)}
                      className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left"
                    >
                      {q.length > 60 ? q.slice(0, 60) + "…" : q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">{effectiveRegion}</span>
                {" · "}
                <span dir="auto">{language.native}</span>
              </div>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button
                    onClick={reset}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    New Query
                  </button>
                )}
                {runState === "running" ? (
                  <button
                    onClick={() => { abortRef.current?.abort(); setRunState("idle"); setActiveAgent(null); }}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-destructive/20 border border-destructive/30 text-destructive text-sm font-semibold hover:bg-destructive/30 transition-colors"
                  >
                    <StopCircle className="w-4 h-4" />
                    Stop
                  </button>
                ) : (
                  <button
                    disabled={!query.trim() || runState === "done"}
                    onClick={runPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-green-600 text-white text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Run Intelligence
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Voter segment chart (auto-extracted) */}
          {forecasterContent && <VoterSegmentChart content={forecasterContent} />}

          {/* Agent outputs */}
          {(turns.length > 0 || error) && (
            <div
              ref={logRef}
              className="flex-1 rounded-2xl border border-border bg-card p-5 overflow-y-auto max-h-[65vh] flex flex-col gap-6"
            >
              {error && (
                <div className="rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  {error}
                </div>
              )}
              {turns.map((turn, i) => (
                <AgentMessage key={`${turn.agentId}-${i}`} turn={turn} />
              ))}
              {runState === "done" && (
                <div className="pt-2 border-t border-border text-center text-xs text-muted-foreground">
                  Intelligence brief complete — 4 specialized agents contributed
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                <Telescope className="w-8 h-8 text-green-400/60" />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">Intelligence Crew ready</p>
                <p className="text-xs text-muted-foreground max-w-xs">
                  Select a region, choose your language context, and enter an intelligence query. The crew will
                  index data, analyze dialects, forecast behavior, and deliver an operational brief.
                </p>
              </div>
              <div className="flex items-center gap-5 text-xs text-muted-foreground mt-2">
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-sky-400" />LlamaIndex</span>
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-400" />Meta-Llama</span>
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-orange-400" />LightGBM</span>
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-purple-400" />Synthesis</span>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
