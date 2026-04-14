import { useState, useRef, useEffect, useCallback } from "react";
import {
  PhoneCall,
  Cpu,
  Layers,
  MapPin,
  BarChart2,
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
  Radio,
  Globe,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  ArrowRight,
  Mic,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId =
  | "hardware_architect"
  | "callflow_engineer"
  | "rural_strategist"
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
    id: "hardware_architect",
    role: "IVR Hardware Architect",
    tool: "RASP-IVR · Raspberry Pi · GSM Modem",
    color: "#f97316",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    desc: "BOM, wiring, RASP-IVR install, AT commands, solar power, multi-modem setup, enclosure, remote management",
    icon: Cpu,
  },
  {
    id: "callflow_engineer",
    role: "Call Flow Engineer",
    tool: "Verboice · TTS · ASR · VBVoice",
    color: "#8b5cf6",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
    desc: "Call flow diagram, Verboice Docker setup, flow JSON, TTS/ASR config, multi-language design, data collection schema",
    icon: Layers,
  },
  {
    id: "rural_strategist",
    role: "Rural Penetration Strategist",
    tool: "Field Deployment · Localization · Community",
    color: "#10b981",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    desc: "Region analysis, number strategy, language rollout, audio content guide, community distribution, metrics framework",
    icon: MapPin,
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#f43f5e",
    bg: "bg-rose-500/10",
    border: "border-rose-500/30",
    desc: "Platform decision matrix, Docker Compose, call flow scripts, timeline, cost model, OEADS integration",
    icon: BarChart2,
  },
];

type PlatformOption = { id: string; label: string; note: string };

const PLATFORMS: PlatformOption[] = [
  { id: "rasp_verboice", label: "RASP-IVR + Verboice", note: "Field hardware + open-source IVR — recommended for rural" },
  { id: "rasp_only", label: "RASP-IVR standalone", note: "Minimal Python-based stack, offline-first" },
  { id: "verboice", label: "Verboice (server-based)", note: "Red Cross / ILO standard, Visual Call Flow Designer" },
  { id: "vbvoice", label: "VBVoice by Pronexus", note: "Windows/.NET free toolkit, enterprise environments" },
  { id: "full", label: "Full stack (all three)", note: "Compare all platforms for research benchmarking" },
];

const LANGUAGES = [
  "English only",
  "English + Urdu",
  "English + Bengali",
  "English + Swahili",
  "English + Kinyarwanda",
  "English + Hausa",
  "English + Sinhala + Tamil",
  "Multi-dialect (custom)",
];

const DEPLOYMENT_REGIONS = [
  "South Asia (Pakistan / Bangladesh / India)",
  "East Africa (Rwanda / Tanzania / Kenya)",
  "West Africa (Nigeria / Ghana)",
  "South Asia + East Africa (multi-site)",
  "Southeast Asia (Cambodia / Myanmar)",
  "Sri Lanka",
  "Custom / undisclosed",
];

const CONNECTIVITY_LEVELS = [
  { id: "gsm_only", label: "2G GSM voice only", note: "No data, no internet — IVR on voice channel" },
  { id: "gsm_gprs", label: "2G GSM + GPRS", note: "Voice + occasional data sync for logs" },
  { id: "3g", label: "3G / HSPA", note: "Voice + reliable data for Verboice server sync" },
  { id: "mixed", label: "Mixed (urban 3G, rural GSM)", note: "Hybrid: server in city, RASP-IVR in field" },
];

const CALL_VOLUMES = [
  "< 50 calls/day (pilot)",
  "100–500 calls/day",
  "500–2,000 calls/day",
  "2,000–10,000 calls/day",
  "10,000+ calls/day (national)",
];

const INTEGRATION_TARGETS = [
  "Standalone IVR",
  "IVR + SIM Farm (TIER 4)",
  "IVR + Persona orchestration (TIER 3)",
  "IVR + Full OEADS pipeline",
];

const EXAMPLE_CASES = [
  "Community health survey: IVR collects maternal health data from rural village women via missed-call callback",
  "Agricultural extension: RASP-IVR deploys crop disease alerts to 10,000 farmers in Pakistan's Punjab province",
  "Red Cross emergency: Verboice delivers displacement reporting IVR to conflict-affected population in East Africa",
  "Academic study: Compare IVR completion rates across literacy levels and languages in Bangladesh",
];

const PIPELINE_STEPS = [
  { label: "Hardware", icon: Cpu, color: "#f97316" },
  { label: "Call Flow", icon: Layers, color: "#8b5cf6" },
  { label: "Rural Strategy", icon: MapPin, color: "#10b981" },
  { label: "Operations", icon: BarChart2, color: "#f43f5e" },
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
  const Icon = agent?.icon ?? PhoneCall;
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

export default function IvrSystems() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [useCase, setUseCase] = useState("");
  const [platform, setPlatform] = useState(PLATFORMS[0]);
  const [targetLanguages, setTargetLanguages] = useState(LANGUAGES[0]);
  const [deploymentRegion, setDeploymentRegion] = useState(DEPLOYMENT_REGIONS[0]);
  const [connectivityLevel, setConnectivityLevel] = useState(CONNECTIVITY_LEVELS[0]);
  const [callVolume, setCallVolume] = useState(CALL_VOLUMES[1]);
  const [integrationTargets, setIntegrationTargets] = useState(INTEGRATION_TARGETS[0]);

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
      const res = await fetch("/api/ivr/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          useCase: useCase.trim(),
          platform: platform.label,
          targetLanguages,
          deploymentRegion,
          connectivityLevel: connectivityLevel.label,
          callVolume,
          integrationTargets,
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
  }, [useCase, platform, targetLanguages, deploymentRegion, connectivityLevel, callVolume, integrationTargets, runState, sessionId]);

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
            <div className="w-8 h-8 rounded-xl bg-orange-500/10 border border-orange-500/30 flex items-center justify-center">
              <PhoneCall className="w-4 h-4 text-orange-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">IVR Systems</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 4</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-orange-400" />
              <span className="text-xs text-muted-foreground">RASP-IVR · Verboice · VBVoice · Rural Penetration</span>
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
              <PhoneCall className="w-3.5 h-3.5 text-muted-foreground" />
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
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">IVR Config</p>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Mic className="w-3 h-3" />Platform
              </label>
              <OptionSelector options={PLATFORMS} selected={platform} onSelect={setPlatform} disabled={runState === "running"} accentColor="#f97316" />
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Languages</label>
              <select value={targetLanguages} onChange={(e) => setTargetLanguages(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {LANGUAGES.map((l) => <option key={l}>{l}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Deployment Region</label>
              <select value={deploymentRegion} onChange={(e) => setDeploymentRegion(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {DEPLOYMENT_REGIONS.map((r) => <option key={r}>{r}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Radio className="w-3 h-3" />Connectivity
              </label>
              <OptionSelector options={CONNECTIVITY_LEVELS} selected={connectivityLevel} onSelect={setConnectivityLevel} disabled={runState === "running"} accentColor="#10b981" />
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Call Volume</label>
              <select value={callVolume} onChange={(e) => setCallVolume(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {CALL_VOLUMES.map((v) => <option key={v}>{v}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">OEADS Integration</label>
              <select value={integrationTargets} onChange={(e) => setIntegrationTargets(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {INTEGRATION_TARGETS.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>

            <div className="rounded-lg border border-orange-500/20 bg-orange-500/5 p-3 mt-1">
              <p className="text-xs font-semibold text-orange-400 mb-1">RASP-IVR · Verboice · VBVoice</p>
              <p className="text-xs text-muted-foreground">
                Open-source IVR stack for low-connectivity populations. RASP-IVR is field-tested in Rwanda. Verboice is deployed by Red Cross and ILO. VBVoice is free for Windows/.NET.
              </p>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Research / Deployment Use Case
            </label>
            <textarea
              value={useCase}
              onChange={(e) => setUseCase(e.target.value)}
              placeholder="Describe the authorized research or humanitarian deployment use case for this IVR system..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-orange-500/40 disabled:opacity-50"
              onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline(); }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example use cases:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_CASES.map((q) => (
                    <button key={q} onClick={() => setUseCase(q)} className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left">
                      {q.length > 72 ? q.slice(0, 72) + "…" : q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground space-x-2">
                <span className="font-medium text-foreground">{platform.label}</span>
                <span>·</span>
                <span className="text-violet-400">{targetLanguages}</span>
                <span>·</span>
                <span>{deploymentRegion.split(" (")[0]}</span>
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
                    style={{ background: "linear-gradient(135deg, #f97316, #8b5cf6)", color: "white" }}
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Plan IVR
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
                  IVR deployment brief complete — hardware BOM, call flow, rural strategy, and operations runbook ready
                </div>
              )}
            </div>
          )}

          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #f9731620, #8b5cf620)", border: "1px solid #f9731630" }}>
                <PhoneCall className="w-8 h-8" style={{ color: "#f9731660" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">IVR Systems ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Describe your authorized research or humanitarian deployment use case. The pipeline produces a hardware BOM and wiring guide, call flow design with Verboice/VBVoice config, rural penetration strategy, and a complete deployment brief with Docker Compose and cost model.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "RASP-IVR", color: "#f97316" },
                  { label: "Verboice", color: "#f97316" },
                  { label: "VBVoice", color: "#8b5cf6" },
                  { label: "Rural Deployment", color: "#10b981" },
                  { label: "Multi-language", color: "#10b981" },
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
