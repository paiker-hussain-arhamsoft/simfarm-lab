import { useState, useRef, useEffect, useCallback } from "react";
import {
  Users,
  GitBranch,
  LayoutGrid,
  Globe,
  SendHorizonal,
  Loader2,
  RotateCcw,
  ShieldCheck,
  Brain,
  Telescope,
  Clapperboard,
  MonitorPlay,
  Terminal,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  ArrowRight,
  Network,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId = "persona_architect" | "orchestration_engineer" | "social_media_strategist" | "automation_director";

type AgentMeta = {
  id: AgentId;
  role: string;
  tool: string;
  color: string;
  bg: string;
  border: string;
  desc: string;
  icon: React.ElementType;
};

const AGENTS: AgentMeta[] = [
  {
    id: "persona_architect",
    role: "Persona Architect",
    tool: "ElizaOS",
    color: "#10b981",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    desc: "7-layer character architecture, persona fleet design, memory config, character JSON",
    icon: Users,
  },
  {
    id: "orchestration_engineer",
    role: "Orchestration Engineer",
    tool: "Botpress · LangGraph",
    color: "#6366f1",
    bg: "bg-indigo-500/10",
    border: "border-indigo-500/30",
    desc: "Graph topology, state schema, memory graph, perspective engine, goal stacks",
    icon: GitBranch,
  },
  {
    id: "social_media_strategist",
    role: "Social Media Strategist",
    tool: "Socioboard · Multi-account",
    color: "#f59e0b",
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    desc: "Account architecture, content calendar, engagement protocol, analytics dashboard",
    icon: LayoutGrid,
  },
  {
    id: "automation_director",
    role: "Automation Director",
    tool: "Playwright · Puppeteer · Selenium",
    color: "#ec4899",
    bg: "bg-pink-500/10",
    border: "border-pink-500/30",
    desc: "Stealth config, fingerprint evasion, proxy rotation, session orchestration, full brief",
    icon: Globe,
  },
];

const PERSONA_COUNTS = [
  "10 personas", "50 personas", "100 personas", "500 personas",
  "1,000 personas", "10,000 personas", "30,000+ personas",
];

const PLATFORMS = [
  "Twitter/X", "Facebook", "Instagram", "LinkedIn",
  "Telegram", "Reddit", "YouTube", "Multi-platform",
];

const ORCHESTRATION_ENGINES = [
  { id: "langgraph", label: "LangGraph", note: "Graph-based, stateful, cyclic agent loops" },
  { id: "botpress", label: "Botpress", note: "Enterprise NLU, flow-based, human-in-the-loop" },
  { id: "both", label: "LangGraph + Botpress", note: "LangGraph backend, Botpress for escalation" },
];

const AUTOMATION_TOOLS = [
  { id: "playwright", label: "Playwright", badge: "Apache-2", note: "Built-in stealth, multi-browser, auto-wait" },
  { id: "puppeteer", label: "Puppeteer", badge: "Apache-2", note: "Chrome CDP, puppeteer-extra-stealth plugin" },
  { id: "selenium", label: "Selenium Grid", badge: "Apache-2", note: "Distributed, language-agnostic, enterprise scale" },
];

const MEMORY_DEPTHS = [
  "Minimal (conversation only)",
  "Standard (short + long-term)",
  "Full (episodic + semantic)",
  "Deep (cross-persona shared memory)",
];

const GEOGRAPHIC_SPREADS = [
  "Single city", "Single country", "Multi-regional",
  "Multi-national", "Global (6 continents)",
];

const PIPELINE_STEPS = [
  { label: "Persona Design", icon: Users, color: "#10b981" },
  { label: "Orchestration", icon: GitBranch, color: "#6366f1" },
  { label: "Social Media", icon: LayoutGrid, color: "#f59e0b" },
  { label: "Automation", icon: Globe, color: "#ec4899" },
];

const EXAMPLE_OBJECTIVES = [
  "Research: map narrative diffusion patterns across 100 synthetic personas for academic study",
  "Red team: test platform moderation resilience against coordinated inauthentic behavior",
  "Simulation: model how regional linguistic personas shape political discourse online",
  "Education: demonstrate social engineering attack surface for cybersecurity curriculum",
];

type AgentTurn = {
  agentId: AgentId;
  role: string;
  tool: string;
  color: string;
  content: string;
  done: boolean;
};

type RunState = "idle" | "running" | "done" | "error";

function AgentCard({ agent, active, done }: { agent: AgentMeta; active: boolean; done: boolean }) {
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
      <p className="text-xs text-muted-foreground/70 mb-1.5">{agent.desc}</p>
      <span className="text-xs font-mono" style={{ color: agent.color }}>
        {agent.tool}
      </span>
    </div>
  );
}

function AgentMessage({ turn }: { turn: AgentTurn }) {
  const agent = AGENTS.find((a) => a.id === turn.agentId);
  const Icon = agent?.icon ?? Users;
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
        <span className="text-xs font-semibold" style={{ color: turn.color }}>
          {turn.role}
        </span>
        <span className="text-xs text-muted-foreground/50 font-mono">· {turn.tool}</span>
        {!turn.done && <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />}
        {turn.done && (
          <button
            onClick={copy}
            className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-muted/40"
          >
            {copied ? (
              <Check className="w-3 h-3 text-emerald-400" />
            ) : (
              <Copy className="w-3 h-3 text-muted-foreground" />
            )}
          </button>
        )}
      </div>
      <div
        className="ml-8 text-xs text-foreground/90 leading-relaxed whitespace-pre-wrap rounded-xl p-4 border font-mono"
        style={{ backgroundColor: `${turn.color}08`, borderColor: `${turn.color}20` }}
      >
        {turn.content}
        {!turn.done && (
          <span
            className="inline-block w-1.5 h-4 ml-0.5 rounded-sm animate-pulse"
            style={{ backgroundColor: turn.color }}
          />
        )}
      </div>
    </div>
  );
}

function PipelineFlow({
  doneAgents,
  activeAgent,
}: {
  doneAgents: Set<AgentId>;
  activeAgent: AgentId | null;
}) {
  return (
    <div className="rounded-xl border border-border bg-card/50 p-4">
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Pipeline</p>
      <div className="flex items-center gap-1 overflow-x-auto pb-1">
        {PIPELINE_STEPS.map((step, i) => {
          const agentId = AGENTS[i].id;
          const isActive = activeAgent === agentId;
          const isDone = doneAgents.has(agentId);
          const Icon = step.icon;
          return (
            <div key={step.label} className="flex items-center gap-1 shrink-0">
              <div
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all duration-300 ${
                  isActive || isDone ? "" : "border-border/40 text-muted-foreground"
                }`}
                style={
                  isActive || isDone
                    ? { borderColor: step.color, color: step.color, backgroundColor: `${step.color}10` }
                    : {}
                }
              >
                <Icon className="w-3 h-3" />
                {step.label}
                {isActive && (
                  <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: step.color }} />
                )}
                {isDone && <Check className="w-3 h-3" />}
              </div>
              {i < PIPELINE_STEPS.length - 1 && (
                <ArrowRight className="w-3 h-3 text-muted-foreground/30 shrink-0" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function PersonaOrchestration() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [objective, setObjective] = useState("");
  const [personaCount, setPersonaCount] = useState(PERSONA_COUNTS[2]);
  const [platform, setPlatform] = useState(PLATFORMS[0]);
  const [orchestrationEngine, setOrchestrationEngine] = useState(ORCHESTRATION_ENGINES[0]);
  const [automationTool, setAutomationTool] = useState(AUTOMATION_TOOLS[0]);
  const [memoryDepth, setMemoryDepth] = useState(MEMORY_DEPTHS[2]);
  const [geographicSpread, setGeographicSpread] = useState(GEOGRAPHIC_SPREADS[2]);

  const [runState, setRunState] = useState<RunState>("idle");
  const [turns, setTurns] = useState<AgentTurn[]>([]);
  const [activeAgent, setActiveAgent] = useState<AgentId | null>(null);
  const [doneAgents, setDoneAgents] = useState<Set<AgentId>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sessionStorage.getItem("compliance_acknowledged") !== "true") setLocation("/");
  }, []);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [turns]);

  const runPipeline = useCallback(async () => {
    if (!objective.trim() || runState === "running") return;

    setRunState("running");
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch("/api/persona/orchestrate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objective: objective.trim(),
          personaCount,
          platform,
          orchestrationEngine: orchestrationEngine.label,
          automationTool: automationTool.label,
          memoryDepth,
          geographicSpread,
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
          try {
            event = JSON.parse(raw);
          } catch {
            continue;
          }

          if (event.type === "agent_start") {
            const agentId = event.agent as AgentId;
            const meta = AGENTS.find((a) => a.id === agentId);
            if (!meta) continue;
            setActiveAgent(agentId);
            setTurns((prev) => [
              ...prev,
              { agentId, role: meta.role, tool: meta.tool, color: meta.color, content: "", done: false },
            ]);
          } else if (event.type === "token") {
            const agentId = event.agent as AgentId;
            setTurns((prev) =>
              prev.map((t) =>
                t.agentId === agentId && !t.done
                  ? { ...t, content: t.content + (event.content as string) }
                  : t
              )
            );
          } else if (event.type === "agent_done") {
            const agentId = event.agent as AgentId;
            setTurns((prev) => prev.map((t) => (t.agentId === agentId ? { ...t, done: true } : t)));
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
  }, [objective, personaCount, platform, orchestrationEngine, automationTool, memoryDepth, geographicSpread, runState, sessionId]);

  const reset = () => {
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);
    setRunState("idle");
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
              <Network className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Persona Orchestration</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 3</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-emerald-400" />
              <span className="text-xs text-muted-foreground">ElizaOS · LangGraph · Socioboard · Playwright</span>
            </div>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap justify-end">
            <button
              onClick={() => setLocation("/tool")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Brain className="w-3.5 h-3.5" />TIER 1
            </button>
            <button
              onClick={() => setLocation("/tier2")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Telescope className="w-3.5 h-3.5" />Intelligence
            </button>
            <button
              onClick={() => setLocation("/media-crew")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Clapperboard className="w-3.5 h-3.5" />Media Crew
            </button>
            <button
              onClick={() => setLocation("/video-stack")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <MonitorPlay className="w-3.5 h-3.5" />Video Stack
            </button>
            <button
              onClick={() => setLocation("/cyber-crew")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Terminal className="w-3.5 h-3.5" />Cyber Crew
            </button>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden lg:inline">Compliance verified</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <aside className="lg:w-80 shrink-0 flex flex-col gap-4">
          {/* Agent stack */}
          <div className="rounded-2xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 mb-4">
              <Network className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Agent Stack</span>
            </div>
            <div className="flex flex-col gap-2">
              {AGENTS.map((agent, i) => (
                <div key={agent.id} className="flex flex-col">
                  <AgentCard
                    agent={agent}
                    active={activeAgent === agent.id}
                    done={doneAgents.has(agent.id)}
                  />
                  {i < AGENTS.length - 1 && (
                    <div className="flex justify-center my-0.5">
                      <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/40 rotate-90" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Config */}
          <div className="rounded-2xl border border-border bg-card p-4 flex flex-col gap-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Fleet Config</p>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Persona Count</label>
              <select
                value={personaCount}
                onChange={(e) => setPersonaCount(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {PERSONA_COUNTS.map((p) => <option key={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Target Platform</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {PLATFORMS.map((p) => <option key={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <GitBranch className="w-3 h-3" />Orchestration Engine
              </label>
              <div className="flex flex-col gap-1">
                {ORCHESTRATION_ENGINES.map((e) => (
                  <button
                    key={e.id}
                    onClick={() => setOrchestrationEngine(e)}
                    disabled={runState === "running"}
                    className={`flex flex-col gap-0.5 p-2.5 rounded-lg border text-left text-xs transition-colors disabled:opacity-50 ${
                      orchestrationEngine.id === e.id
                        ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-400"
                        : "border-border/50 text-muted-foreground hover:bg-muted/30"
                    }`}
                  >
                    <span className="font-semibold">{e.label}</span>
                    <span className="text-muted-foreground text-[11px]">{e.note}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Globe className="w-3 h-3" />Automation Tool
              </label>
              <div className="flex flex-col gap-1">
                {AUTOMATION_TOOLS.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setAutomationTool(t)}
                    disabled={runState === "running"}
                    className={`flex items-start gap-2 p-2.5 rounded-lg border text-left text-xs transition-colors disabled:opacity-50 ${
                      automationTool.id === t.id
                        ? "border-pink-500/50 bg-pink-500/10 text-pink-400"
                        : "border-border/50 text-muted-foreground hover:bg-muted/30"
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <span className="font-semibold">{t.label}</span>
                        <span className="px-1 rounded text-[10px] bg-muted/60 text-muted-foreground border border-border font-mono">{t.badge}</span>
                      </div>
                      <p className="text-muted-foreground text-[11px]">{t.note}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Memory Depth</label>
              <select
                value={memoryDepth}
                onChange={(e) => setMemoryDepth(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {MEMORY_DEPTHS.map((m) => <option key={m}>{m}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Geographic Spread</label>
              <select
                value={geographicSpread}
                onChange={(e) => setGeographicSpread(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {GEOGRAPHIC_SPREADS.map((g) => <option key={g}>{g}</option>)}
              </select>
            </div>

            <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 mt-1">
              <p className="text-xs font-semibold text-emerald-400 mb-1">ElizaOS Scale</p>
              <p className="text-xs text-muted-foreground">
                ElizaOS supports 30,000+ simultaneous agents with 7-layer character architectures and plugin-based platform adapters.
              </p>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Objective input */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Research Objective
            </label>
            <textarea
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="Describe the educational or research objective for this persona orchestration exercise..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500/40 disabled:opacity-50"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline();
              }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example objectives:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_OBJECTIVES.map((q) => (
                    <button
                      key={q}
                      onClick={() => setObjective(q)}
                      className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left"
                    >
                      {q.length > 70 ? q.slice(0, 70) + "…" : q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground space-x-2">
                <span className="font-medium text-foreground">{personaCount}</span>
                <span>·</span>
                <span>{platform}</span>
                <span>·</span>
                <span className="text-emerald-400">{orchestrationEngine.label}</span>
                <span>+</span>
                <span className="text-pink-400">{automationTool.label}</span>
              </div>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button
                    onClick={reset}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />New Session
                  </button>
                )}
                {runState === "running" ? (
                  <button
                    onClick={() => {
                      abortRef.current?.abort();
                      setRunState("idle");
                      setActiveAgent(null);
                    }}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-destructive/20 border border-destructive/30 text-destructive text-sm font-semibold hover:bg-destructive/30 transition-colors"
                  >
                    <StopCircle className="w-4 h-4" />Stop
                  </button>
                ) : (
                  <button
                    disabled={!objective.trim() || runState === "done"}
                    onClick={runPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                    style={{
                      background: "linear-gradient(135deg, #10b981, #6366f1, #ec4899)",
                      color: "white",
                    }}
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Orchestrate
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Pipeline tracker */}
          {runState !== "idle" && (
            <PipelineFlow doneAgents={doneAgents} activeAgent={activeAgent} />
          )}

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
                  TIER 3 brief complete — persona fleet, orchestration graph, social media strategy, and automation pipeline ready
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div
                className="w-16 h-16 rounded-2xl flex items-center justify-center"
                style={{
                  background: "linear-gradient(135deg, #10b98120, #6366f120, #ec489920)",
                  border: "1px solid #10b98130",
                }}
              >
                <Network className="w-8 h-8" style={{ color: "#10b98160" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">TIER 3 Persona Orchestration ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Define your research objective and fleet configuration. The pipeline produces a complete 7-layer persona architecture, LangGraph orchestration design, Socioboard multi-account strategy, and Playwright automation layer.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "ElizaOS", color: "#10b981" },
                  { label: "LangGraph", color: "#6366f1" },
                  { label: "Botpress", color: "#6366f1" },
                  { label: "Socioboard", color: "#f59e0b" },
                  { label: "Playwright", color: "#ec4899" },
                ].map((t) => (
                  <span key={t.label} className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: t.color }} />
                    {t.label}
                  </span>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
