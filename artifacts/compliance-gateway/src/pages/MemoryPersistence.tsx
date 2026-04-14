import { useState, useRef, useEffect, useCallback } from "react";
import {
  Database,
  Brain,
  Server,
  BarChart2,
  SendHorizonal,
  Loader2,
  RotateCcw,
  ShieldCheck,
  Telescope,
  Clapperboard,
  MonitorPlay,
  Terminal,
  Network,
  Radio,
  Globe,
  PhoneCall,
  Rss,
  EyeOff,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  ArrowRight,
  Layers,
  HardDrive,
  Cpu,
  GitBranch,
  Clock,
  Search,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId =
  | "mem0_architect"
  | "zeta_engineer"
  | "kafka_cassandra_architect"
  | "operations_director";

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
    id: "mem0_architect",
    role: "Mem0 Memory Architect",
    tool: "Mem0 · Open-source AI Agent Memory",
    color: "#6366f1",
    bg: "bg-indigo-500/10",
    border: "border-indigo-500/30",
    desc: "Qdrant vector store, Neo4j graph, fact extraction pipeline, persona memory isolation, multi-agent sharing, async write queue",
    icon: Brain,
  },
  {
    id: "zeta_engineer",
    role: "Zeta Memory Engineer",
    tool: "Zeta · Structured Distributed Memory",
    color: "#0ea5e9",
    bg: "bg-sky-500/10",
    border: "border-sky-500/30",
    desc: "PostgreSQL+pgvector schema, hot/warm/cold tiers, Redis cache, event sourcing, version vectors, conflict resolution",
    icon: GitBranch,
  },
  {
    id: "kafka_cassandra_architect",
    role: "Data Lake Architect",
    tool: "Apache Kafka · Cassandra · 120M+ Records",
    color: "#f59e0b",
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    desc: "120M+ voter records, Kafka topic design, Cassandra data model, Spark bulk load, Trino analytics, data governance + PII encryption",
    icon: HardDrive,
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#f43f5e",
    bg: "bg-rose-500/10",
    border: "border-rose-500/30",
    desc: "Master Docker Compose, memory routing tree, full OEADS integration flow, storage estimates, cost model, failure modes",
    icon: BarChart2,
  },
];

type SelectorOption = { id: string; label: string; note: string };

const PERSONA_COUNTS: SelectorOption[] = [
  { id: "small", label: "100–1K personas", note: "Dev/test scale — single-node deployments" },
  { id: "medium", label: "10K–100K personas", note: "Campaign scale — clustered deployments" },
  { id: "large", label: "1M+ personas", note: "National scale — full distributed stack" },
  { id: "voter", label: "120M+ voter records", note: "Full US voter file — Cassandra optimized" },
];

const DATA_VOLUMES: SelectorOption[] = [
  { id: "light", label: "< 1GB structured data", note: "Single PostgreSQL instance sufficient" },
  { id: "medium", label: "1–100GB", note: "PostgreSQL + Redis + Qdrant stack" },
  { id: "heavy", label: "100GB–10TB", note: "Cassandra cluster + Kafka pipeline" },
  { id: "massive", label: "10TB+ (120M+ records)", note: "Full Kafka + Cassandra + Spark lake" },
];

const MEMORY_SCOPES: SelectorOption[] = [
  { id: "session", label: "Session only", note: "Per-run context, no long-term persistence" },
  { id: "user", label: "Per-persona long-term", note: "Persistent across all sessions per persona" },
  { id: "agent", label: "Shared agent knowledge", note: "Collective knowledge per agent type" },
  { id: "full", label: "Full hierarchical", note: "Session + persona + agent + campaign levels" },
];

const RETENTION_POLICIES = [
  "7 days (ephemeral campaign)",
  "90 days (short cycle)",
  "2 years (engagement history)",
  "Indefinite (voter records)",
  "Custom TTL by memory type",
];

const QUERY_PATTERNS = [
  "Semantic search (Mem0/Qdrant)",
  "Structured lookup (Zeta/PostgreSQL)",
  "Time-series (Cassandra engagement_history)",
  "Hybrid: semantic + structured filters",
  "Bulk analytics (Spark + Trino)",
  "All patterns (full stack)",
];

const INTEGRATION_TARGETS = [
  "Standalone memory service",
  "Memory + Persona stack (TIER 3)",
  "Memory + SIM Farm (TIER 4)",
  "Memory + Stealth layer (TIER 4)",
  "Full OEADS integration",
];

const PIPELINE_STEPS = [
  { label: "Mem0", icon: Brain, color: "#6366f1" },
  { label: "Zeta", icon: GitBranch, color: "#0ea5e9" },
  { label: "Kafka + Cassandra", icon: HardDrive, color: "#f59e0b" },
  { label: "Operations", icon: BarChart2, color: "#f43f5e" },
];

const EXAMPLE_CASES = [
  "Design memory layer for 50K synthetic civic research personas with per-persona long-term memory and shared agent knowledge base",
  "Build Apache Kafka + Cassandra data lake for authorized analysis of 120M US voter registration records with PII encryption",
  "Compare Mem0 vs Zeta memory architectures for 1M persona AI agent fleet requiring sub-10ms memory retrieval at scale",
  "Design full OEADS memory stack: Mem0 semantic memory + Zeta structured memory + Cassandra data lake + Kafka event pipeline",
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

function PipelineFlow({ doneAgents, activeAgent }: { doneAgents: Set<AgentId>; activeAgent: AgentId | null }) {
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

function OptionSelector<T extends { id: string; label: string; note: string }>({
  options,
  selected,
  onSelect,
  disabled,
  accentColor,
}: {
  options: T[];
  selected: T;
  onSelect: (t: T) => void;
  disabled: boolean;
  accentColor: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      {options.map((t) => (
        <button
          key={t.id}
          onClick={() => onSelect(t)}
          disabled={disabled}
          className={`flex flex-col gap-0.5 p-2.5 rounded-lg border text-left text-xs transition-colors disabled:opacity-50 ${
            selected.id === t.id ? "" : "border-border/50 text-muted-foreground hover:bg-muted/30"
          }`}
          style={
            selected.id === t.id
              ? { borderColor: `${accentColor}50`, backgroundColor: `${accentColor}10`, color: accentColor }
              : {}
          }
        >
          <span className="font-semibold">{t.label}</span>
          <span className="text-muted-foreground text-[11px]">{t.note}</span>
        </button>
      ))}
    </div>
  );
}

export default function MemoryPersistence() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [useCase, setUseCase] = useState("");
  const [agentPersonaCount, setAgentPersonaCount] = useState(PERSONA_COUNTS[1]);
  const [dataVolume, setDataVolume] = useState(DATA_VOLUMES[3]);
  const [memoryScope, setMemoryScope] = useState(MEMORY_SCOPES[3]);
  const [retentionPolicy, setRetentionPolicy] = useState(RETENTION_POLICIES[2]);
  const [queryPattern, setQueryPattern] = useState(QUERY_PATTERNS[3]);
  const [integrationTarget, setIntegrationTarget] = useState(INTEGRATION_TARGETS[4]);

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
    if (!useCase.trim() || runState === "running") return;

    setRunState("running");
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch("/api/memory/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          useCase: useCase.trim(),
          agentPersonaCount: agentPersonaCount.label,
          dataVolume: dataVolume.label,
          memoryScope: memoryScope.label,
          retentionPolicy,
          queryPattern,
          integrationTarget,
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
  }, [useCase, agentPersonaCount, dataVolume, memoryScope, retentionPolicy, queryPattern, integrationTarget, runState, sessionId]);

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
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center">
              <Database className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Memory & Persistence</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 4</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-indigo-400" />
              <span className="text-xs text-muted-foreground">Mem0 · Zeta · Kafka · Cassandra · 120M+ Records</span>
            </div>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap justify-end">
            <button onClick={() => setLocation("/tool")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Brain className="w-3.5 h-3.5" />TIER 1
            </button>
            <button onClick={() => setLocation("/tier2")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Telescope className="w-3.5 h-3.5" />Intelligence
            </button>
            <button onClick={() => setLocation("/media-crew")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Clapperboard className="w-3.5 h-3.5" />Media Crew
            </button>
            <button onClick={() => setLocation("/video-stack")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <MonitorPlay className="w-3.5 h-3.5" />Video Stack
            </button>
            <button onClick={() => setLocation("/cyber-crew")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Terminal className="w-3.5 h-3.5" />Cyber Crew
            </button>
            <button onClick={() => setLocation("/persona-orchestration")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Network className="w-3.5 h-3.5" />TIER 3
            </button>
            <button onClick={() => setLocation("/sim-farm")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Radio className="w-3.5 h-3.5" />SIM Farm
            </button>
            <button onClick={() => setLocation("/proxy-rotation")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Globe className="w-3.5 h-3.5" />Proxies
            </button>
            <button onClick={() => setLocation("/ivr-systems")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <PhoneCall className="w-3.5 h-3.5" />IVR
            </button>
            <button onClick={() => setLocation("/content-distribution")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Rss className="w-3.5 h-3.5" />Content
            </button>
            <button onClick={() => setLocation("/stealth-detection")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <EyeOff className="w-3.5 h-3.5" />Stealth
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
          <div className="rounded-2xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 mb-4">
              <Database className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Agent Stack</span>
            </div>
            <div className="flex flex-col gap-2">
              {AGENTS.map((agent, i) => (
                <div key={agent.id} className="flex flex-col">
                  <AgentCard agent={agent} active={activeAgent === agent.id} done={doneAgents.has(agent.id)} />
                  {i < AGENTS.length - 1 && (
                    <div className="flex justify-center my-0.5">
                      <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/40 rotate-90" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-4 flex flex-col gap-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Memory Config</p>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Network className="w-3 h-3" />Persona / Record Volume
              </label>
              <OptionSelector options={PERSONA_COUNTS} selected={agentPersonaCount} onSelect={setAgentPersonaCount} disabled={runState === "running"} accentColor="#6366f1" />
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <HardDrive className="w-3 h-3" />Data Volume
              </label>
              <OptionSelector options={DATA_VOLUMES} selected={dataVolume} onSelect={setDataVolume} disabled={runState === "running"} accentColor="#f59e0b" />
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Layers className="w-3 h-3" />Memory Scope
              </label>
              <OptionSelector options={MEMORY_SCOPES} selected={memoryScope} onSelect={setMemoryScope} disabled={runState === "running"} accentColor="#0ea5e9" />
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Clock className="w-3 h-3" />Retention Policy
              </label>
              <select value={retentionPolicy} onChange={(e) => setRetentionPolicy(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {RETENTION_POLICIES.map((r) => <option key={r}>{r}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Search className="w-3 h-3" />Query Pattern
              </label>
              <select value={queryPattern} onChange={(e) => setQueryPattern(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {QUERY_PATTERNS.map((q) => <option key={q}>{q}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Cpu className="w-3 h-3" />OEADS Integration
              </label>
              <select value={integrationTarget} onChange={(e) => setIntegrationTarget(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {INTEGRATION_TARGETS.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>

            <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-3 mt-1">
              <p className="text-xs font-semibold text-indigo-400 mb-1">Mem0 (Apache 2.0) · Kafka (Apache 2.0) · Cassandra (Apache 2.0)</p>
              <p className="text-xs text-muted-foreground">
                All open-source. Mem0, Kafka, and Cassandra are self-hostable with full source access. For civic data research with proper authorization and data governance controls.
              </p>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Research Use Case
            </label>
            <textarea
              value={useCase}
              onChange={(e) => setUseCase(e.target.value)}
              placeholder="Describe the authorized research use case for this memory and persistence infrastructure..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/40 disabled:opacity-50"
              onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline(); }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example use cases:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_CASES.map((q) => (
                    <button key={q} onClick={() => setUseCase(q)} className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left">
                      {q.length > 80 ? q.slice(0, 80) + "…" : q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground space-x-2">
                <span className="font-medium text-foreground">{agentPersonaCount.label}</span>
                <span>·</span>
                <span className="text-amber-400">{dataVolume.label}</span>
                <span>·</span>
                <span>{memoryScope.label}</span>
              </div>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button onClick={reset} className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors">
                    <RotateCcw className="w-3.5 h-3.5" />New Plan
                  </button>
                )}
                {runState === "running" ? (
                  <button onClick={() => { abortRef.current?.abort(); setRunState("idle"); setActiveAgent(null); }} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-destructive/20 border border-destructive/30 text-destructive text-sm font-semibold hover:bg-destructive/30 transition-colors">
                    <StopCircle className="w-4 h-4" />Stop
                  </button>
                ) : (
                  <button
                    disabled={!useCase.trim() || runState === "done"}
                    onClick={runPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                    style={{ background: "linear-gradient(135deg, #6366f1, #f59e0b)", color: "white" }}
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Plan Memory Stack
                  </button>
                )}
              </div>
            </div>
          </div>

          {runState !== "idle" && <PipelineFlow doneAgents={doneAgents} activeAgent={activeAgent} />}

          {(turns.length > 0 || error) && (
            <div ref={logRef} className="flex-1 rounded-2xl border border-border bg-card p-5 overflow-y-auto max-h-[65vh] flex flex-col gap-6">
              {error && (
                <div className="rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</div>
              )}
              {turns.map((turn, i) => <AgentMessage key={`${turn.agentId}-${i}`} turn={turn} />)}
              {runState === "done" && (
                <div className="pt-2 border-t border-border text-center text-xs text-muted-foreground">
                  Memory & persistence brief complete — Mem0, Zeta, Kafka + Cassandra data lake, and full OEADS integration guide ready
                </div>
              )}
            </div>
          )}

          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #6366f120, #f59e0b20)", border: "1px solid #6366f130" }}>
                <Database className="w-8 h-8" style={{ color: "#6366f160" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">Memory & Persistence ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Describe your authorized research use case. The pipeline produces a Mem0 semantic memory architecture, Zeta structured memory with hot/warm/cold tiers, an Apache Kafka + Cassandra data lake for 120M+ records, and a master deployment brief with Docker Compose, cost model, and full OEADS integration.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "Mem0 + Qdrant", color: "#6366f1" },
                  { label: "Zeta + pgvector", color: "#0ea5e9" },
                  { label: "Apache Kafka", color: "#f59e0b" },
                  { label: "Cassandra 120M+", color: "#f59e0b" },
                  { label: "Spark + Trino", color: "#f43f5e" },
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
