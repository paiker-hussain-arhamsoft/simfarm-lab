import { useState, useRef, useEffect, useCallback } from "react";
import {
  Cpu,
  Radio,
  ScanLine,
  Layers,
  SendHorizonal,
  Loader2,
  RotateCcw,
  ShieldCheck,
  Brain,
  Telescope,
  Clapperboard,
  MonitorPlay,
  Terminal,
  Network,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  ArrowRight,
  Server,
  Globe,
  PhoneCall,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId = "hardware_architect" | "smsgate_engineer" | "sim_farm_strategist" | "operations_director";

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
    id: "hardware_architect",
    role: "Hardware Architect",
    tool: "GSM Modems · USB Hubs · Raspberry Pi",
    color: "#0ea5e9",
    bg: "bg-sky-500/10",
    border: "border-sky-500/30",
    desc: "BOM, physical topology, AT commands, udev rules, power cycling, signal optimization",
    icon: Cpu,
  },
  {
    id: "smsgate_engineer",
    role: "SMSgate Engineer",
    tool: "SMSgate · gammu · Python",
    color: "#8b5cf6",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
    desc: "SMSgate config, gammu setup, REST API, routing logic, systemd service, webhook",
    icon: Radio,
  },
  {
    id: "sim_farm_strategist",
    role: "SIM Farm Strategist",
    tool: "SIM Provisioning · Carrier Diversity",
    color: "#f59e0b",
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    desc: "SIM procurement, pool architecture, OTP extraction, rotation automation, cost model",
    icon: ScanLine,
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#10b981",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    desc: "Deployment sequence, verification pipeline, monitoring, runbook, scaling roadmap",
    icon: Layers,
  },
];

const MODEM_COUNTS = [
  "1 modem (prototype)", "4 modems", "8 modems", "16 modems",
  "32 modems", "64 modems", "128+ modems",
];

const CARRIER_OPTIONS = [
  "Single carrier", "Dual carrier", "Multi-carrier (3-5)",
  "MVNO pool", "Mixed MNO + MVNO", "Country-specific MNOs",
];

const GEOGRAPHIES = [
  "Single city", "Single country", "Multi-country (same region)",
  "Multi-regional", "Global", "Pakistan / South Asia", "Middle East",
];

const VERIFICATION_TARGETS = [
  "Generic OTP platforms", "Social media accounts",
  "Financial / banking apps", "Messaging apps",
  "Email providers", "Custom research target",
];

const THROUGHPUTS = [
  "10 verifications/day", "50 verifications/day",
  "100 verifications/day", "500 verifications/day",
  "1,000 verifications/day", "10,000+ verifications/day",
];

const HOST_PLATFORMS = [
  { id: "rpi4", label: "Raspberry Pi 4B", note: "4GB RAM, up to 8 modems, low cost, ARM" },
  { id: "n100", label: "Intel N100 Mini PC", note: "16GB RAM, up to 32 modems, x86" },
  { id: "nuc", label: "Intel NUC / NUC Pro", note: "32GB RAM, enterprise grade, NVMe" },
  { id: "server", label: "1U Rack Server", note: "64GB+ RAM, 100+ modems, data center" },
  { id: "vm", label: "Linux VM / VPS", note: "USB passthrough, remote modem pool" },
];

const PIPELINE_STEPS = [
  { label: "Hardware", icon: Cpu, color: "#0ea5e9" },
  { label: "SMSgate", icon: Radio, color: "#8b5cf6" },
  { label: "SIM Strategy", icon: ScanLine, color: "#f59e0b" },
  { label: "Operations", icon: Layers, color: "#10b981" },
];

const EXAMPLE_CASES = [
  "Research lab: automated phone number verification pipeline for account provisioning study",
  "Telecom security audit: test OTP delivery resilience across MVNO carrier pool",
  "Red team exercise: SIM-swap attack surface analysis for financial services client",
  "Academic study: carrier throttling patterns for bulk SMS verification requests",
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
  const Icon = agent?.icon ?? Server;
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

export default function SimFarm() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [useCase, setUseCase] = useState("");
  const [modemCount, setModemCount] = useState(MODEM_COUNTS[2]);
  const [carriers, setCarriers] = useState(CARRIER_OPTIONS[2]);
  const [geography, setGeography] = useState(GEOGRAPHIES[1]);
  const [verificationTarget, setVerificationTarget] = useState(VERIFICATION_TARGETS[0]);
  const [throughput, setThroughput] = useState(THROUGHPUTS[2]);
  const [hostPlatform, setHostPlatform] = useState(HOST_PLATFORMS[0]);

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
      const res = await fetch("/api/sim/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          useCase: useCase.trim(),
          modemCount,
          carriers,
          geography,
          verificationTarget,
          throughput,
          hostPlatform: hostPlatform.label,
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
  }, [useCase, modemCount, carriers, geography, verificationTarget, throughput, hostPlatform, runState, sessionId]);

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
            <div className="w-8 h-8 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center">
              <Radio className="w-4 h-4 text-sky-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">SIM Farm</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 4</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-sky-400" />
              <span className="text-xs text-muted-foreground">SMSgate · GSM Modems · gammu · Python</span>
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
            <button
              onClick={() => setLocation("/persona-orchestration")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Network className="w-3.5 h-3.5" />TIER 3
            </button>
            <button
              onClick={() => setLocation("/proxy-rotation")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Globe className="w-3.5 h-3.5" />Proxies
            </button>
            <button
              onClick={() => setLocation("/ivr-systems")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-orange-500/30 bg-orange-500/5 px-2.5 py-1.5 rounded-lg hover:bg-orange-500/10 transition-colors text-orange-400/80"
            >
              <PhoneCall className="w-3.5 h-3.5" />IVR
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
              <Radio className="w-3.5 h-3.5 text-muted-foreground" />
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

          {/* Config */}
          <div className="rounded-2xl border border-border bg-card p-4 flex flex-col gap-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Farm Config</p>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Modem Count</label>
              <select
                value={modemCount}
                onChange={(e) => setModemCount(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {MODEM_COUNTS.map((m) => <option key={m}>{m}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Carrier Strategy</label>
              <select
                value={carriers}
                onChange={(e) => setCarriers(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {CARRIER_OPTIONS.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Geography</label>
              <select
                value={geography}
                onChange={(e) => setGeography(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {GEOGRAPHIES.map((g) => <option key={g}>{g}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Verification Target</label>
              <select
                value={verificationTarget}
                onChange={(e) => setVerificationTarget(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {VERIFICATION_TARGETS.map((v) => <option key={v}>{v}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Daily Throughput</label>
              <select
                value={throughput}
                onChange={(e) => setThroughput(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {THROUGHPUTS.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Server className="w-3 h-3" />Host Platform
              </label>
              <div className="flex flex-col gap-1">
                {HOST_PLATFORMS.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setHostPlatform(p)}
                    disabled={runState === "running"}
                    className={`flex flex-col gap-0.5 p-2.5 rounded-lg border text-left text-xs transition-colors disabled:opacity-50 ${
                      hostPlatform.id === p.id
                        ? "border-sky-500/50 bg-sky-500/10 text-sky-400"
                        : "border-border/50 text-muted-foreground hover:bg-muted/30"
                    }`}
                  >
                    <span className="font-semibold">{p.label}</span>
                    <span className="text-muted-foreground text-[11px]">{p.note}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-sky-500/20 bg-sky-500/5 p-3 mt-1">
              <p className="text-xs font-semibold text-sky-400 mb-1">SMSgate</p>
              <p className="text-xs text-muted-foreground">
                Python-based open-source SMS gateway. Manages multiple GSM modems via AT commands. REST API for send/receive with webhook support.
              </p>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Use case input */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Research Use Case
            </label>
            <textarea
              value={useCase}
              onChange={(e) => setUseCase(e.target.value)}
              placeholder="Describe the authorized research or lab use case for this GSM modem farm and SMS gateway infrastructure..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-sky-500/40 disabled:opacity-50"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline();
              }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example use cases:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_CASES.map((q) => (
                    <button
                      key={q}
                      onClick={() => setUseCase(q)}
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
                <span className="font-medium text-foreground">{modemCount}</span>
                <span>·</span>
                <span>{carriers}</span>
                <span>·</span>
                <span className="text-sky-400">{hostPlatform.label}</span>
              </div>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button
                    onClick={reset}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />New Plan
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
                    disabled={!useCase.trim() || runState === "done"}
                    onClick={runPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                    style={{
                      background: "linear-gradient(135deg, #0ea5e9, #8b5cf6)",
                      color: "white",
                    }}
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Plan Farm
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
                  TIER 4 deployment brief complete — hardware BOM, SMSgate config, SIM strategy, and operations runbook ready
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
                  background: "linear-gradient(135deg, #0ea5e920, #8b5cf620)",
                  border: "1px solid #0ea5e930",
                }}
              >
                <Radio className="w-8 h-8" style={{ color: "#0ea5e960" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">TIER 4 SIM Farm ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Describe your authorized research use case and configure the GSM modem farm parameters. The pipeline produces a hardware BOM, complete SMSgate deployment, SIM provisioning strategy, and full operations runbook.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "SMSgate", color: "#8b5cf6" },
                  { label: "GSM Modems", color: "#0ea5e9" },
                  { label: "gammu-smsd", color: "#0ea5e9" },
                  { label: "SIM Pool", color: "#f59e0b" },
                  { label: "Python REST API", color: "#10b981" },
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
