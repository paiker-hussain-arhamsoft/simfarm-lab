import { useState, useRef, useEffect, useCallback } from "react";
import {
  EyeOff,
  Ghost,
  Shield,
  Globe2,
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
  PhoneCall,
  Rss,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  ArrowRight,
  Layers,
  Server,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId =
  | "stealth_architect"
  | "flaresolverr_engineer"
  | "browser_infra_strategist"
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
    id: "stealth_architect",
    role: "Stealth Browser Architect",
    tool: "Playwright Stealth · playwright-extra · Fingerprint Evasion",
    color: "#f97316",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    desc: "navigator.webdriver patch, canvas/audio/WebRTC spoofing, human behavior simulation, timezone-proxy consistency, fingerprint matrix",
    icon: Ghost,
  },
  {
    id: "flaresolverr_engineer",
    role: "Cloudflare Bypass Engineer",
    tool: "FlareSolverr · Puppeteer Stealth · DDoS-GUARD",
    color: "#8b5cf6",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
    desc: "FlareSolverr Docker deploy, challenge types, session management, proxy chain, horizontal scaling, Node.js + Python integration",
    icon: Shield,
  },
  {
    id: "browser_infra_strategist",
    role: "Browser Infrastructure Strategist",
    tool: "Browserbase · Scrapoxy + Playwright · Session Isolation",
    color: "#10b981",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    desc: "Browserbase vs self-hosted comparison, fingerprint pool, session pool design, ban detection, IP warm-up, distributed browser farm",
    icon: Globe2,
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#f43f5e",
    bg: "bg-rose-500/10",
    border: "border-rose-500/30",
    desc: "Master Docker Compose, evasion matrix, stealth test checklist, cost model, runbook, OEADS integration guide",
    icon: BarChart2,
  },
];

type SelectorOption = { id: string; label: string; note: string };

const TARGET_PLATFORMS: SelectorOption[] = [
  { id: "cloudflare", label: "Cloudflare-protected sites", note: "JS challenge + Managed Challenge + Turnstile" },
  { id: "ddosguard", label: "DDoS-GUARD protected", note: "Cookie challenge + behavioral analysis" },
  { id: "custom_waf", label: "Custom WAF / Bot protection", note: "Akamai, PerimeterX, DataDome, Kasada" },
  { id: "social", label: "Social media platforms", note: "Twitter, LinkedIn, Instagram — advanced fingerprinting" },
  { id: "ecommerce", label: "E-commerce / Retail", note: "Shopify, Magento — rate limit + behavior analysis" },
  { id: "general", label: "General web research", note: "Mixed protection levels, variety of WAFs" },
];

const DETECTION_LEVELS: SelectorOption[] = [
  { id: "basic", label: "Basic (navigator.webdriver only)", note: "Trivial — patched by any stealth plugin" },
  { id: "moderate", label: "Moderate (JS fingerprint + IP)", note: "Cloudflare JS challenge tier" },
  { id: "high", label: "High (JA3 + behavioral + canvas)", note: "Cloudflare Pro + behavioral analysis" },
  { id: "extreme", label: "Extreme (ML-based + multi-signal)", note: "DataDome, PerimeterX, Kasada — full stack required" },
];

const BROWSER_ENGINES = [
  "Chromium (Playwright)",
  "Chrome (Puppeteer)",
  "Firefox (Playwright)",
  "Multi-engine (Chrome + Firefox)",
];

const PROXY_STRATEGIES = [
  "Residential via Scrapoxy",
  "Datacenter + Residential mix",
  "Mobile (4G/LTE) via Scrapoxy",
  "Browserbase built-in residential",
  "Full diversity (DC + Res + Mobile)",
];

const SCALE_OPTIONS = [
  "1–5 sessions (research/dev)",
  "10–50 concurrent sessions",
  "50–200 concurrent sessions",
  "200–1000 sessions (farm)",
  "1000+ sessions (enterprise scale)",
];

const INTEGRATION_OPTIONS = [
  "Standalone stealth",
  "Stealth + Proxy Rotation (TIER 4)",
  "Stealth + Persona stack (TIER 3)",
  "Stealth + SIM Farm + Personas",
  "Full OEADS integration",
];

const PIPELINE_STEPS = [
  { label: "Playwright Stealth", icon: Ghost, color: "#f97316" },
  { label: "FlareSolverr", icon: Shield, color: "#8b5cf6" },
  { label: "Browser Infra", icon: Globe2, color: "#10b981" },
  { label: "Operations", icon: BarChart2, color: "#f43f5e" },
];

const EXAMPLE_CASES = [
  "Security audit: test bot detection effectiveness of WAF implementation against Playwright stealth + residential proxies",
  "Academic research: study Cloudflare detection signal diversity across protected research paper repositories",
  "Red team: validate FlareSolverr + Scrapoxy pipeline for authorized penetration testing engagement",
  "Infrastructure research: benchmark Browserbase vs self-hosted Scrapoxy+Playwright for fingerprint consistency",
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
  const Icon = agent?.icon ?? EyeOff;
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

export default function StealthDetection() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [useCase, setUseCase] = useState("");
  const [targetPlatform, setTargetPlatform] = useState(TARGET_PLATFORMS[0]);
  const [detectionLevel, setDetectionLevel] = useState(DETECTION_LEVELS[2]);
  const [browserEngine, setBrowserEngine] = useState(BROWSER_ENGINES[0]);
  const [proxyStrategy, setProxyStrategy] = useState(PROXY_STRATEGIES[0]);
  const [scale, setScale] = useState(SCALE_OPTIONS[1]);
  const [integrationTargets, setIntegrationTargets] = useState(INTEGRATION_OPTIONS[0]);

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
      const res = await fetch("/api/stealth/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          useCase: useCase.trim(),
          targetPlatform: targetPlatform.label,
          detectionLevel: detectionLevel.label,
          browserEngine,
          proxyStrategy,
          scale,
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
  }, [useCase, targetPlatform, detectionLevel, browserEngine, proxyStrategy, scale, integrationTargets, runState, sessionId]);

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
              <EyeOff className="w-4 h-4 text-orange-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Stealth & Anti-Detection</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 4</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-orange-400" />
              <span className="text-xs text-muted-foreground">Playwright Stealth · FlareSolverr · Browserbase · Scrapoxy</span>
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
              <EyeOff className="w-3.5 h-3.5 text-muted-foreground" />
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
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Stealth Config</p>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Terminal className="w-3 h-3" />Target Platform
              </label>
              <OptionSelector options={TARGET_PLATFORMS} selected={targetPlatform} onSelect={setTargetPlatform} disabled={runState === "running"} accentColor="#f97316" />
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Shield className="w-3 h-3" />Detection Level
              </label>
              <OptionSelector options={DETECTION_LEVELS} selected={detectionLevel} onSelect={setDetectionLevel} disabled={runState === "running"} accentColor="#8b5cf6" />
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Browser Engine</label>
              <select value={browserEngine} onChange={(e) => setBrowserEngine(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {BROWSER_ENGINES.map((b) => <option key={b}>{b}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Globe className="w-3 h-3" />Proxy Strategy
              </label>
              <select value={proxyStrategy} onChange={(e) => setProxyStrategy(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {PROXY_STRATEGIES.map((p) => <option key={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Server className="w-3 h-3" />Scale
              </label>
              <select value={scale} onChange={(e) => setScale(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {SCALE_OPTIONS.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Layers className="w-3 h-3" />OEADS Integration
              </label>
              <select value={integrationTargets} onChange={(e) => setIntegrationTargets(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {INTEGRATION_OPTIONS.map((i) => <option key={i}>{i}</option>)}
              </select>
            </div>

            <div className="rounded-lg border border-orange-500/20 bg-orange-500/5 p-3 mt-1">
              <p className="text-xs font-semibold text-orange-400 mb-1">playwright-extra · FlareSolverr · Browserbase</p>
              <p className="text-xs text-muted-foreground">
                playwright-extra (MIT), FlareSolverr (MIT), and fingerprint-generator (Apache 2.0) are open-source. Browserbase is a managed cloud alternative. All for authorized research use only.
              </p>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Authorized Research Use Case
            </label>
            <textarea
              value={useCase}
              onChange={(e) => setUseCase(e.target.value)}
              placeholder="Describe the authorized security research or red team use case for this stealth browser infrastructure..."
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
                <span className="font-medium text-foreground">{targetPlatform.label.split(" (")[0]}</span>
                <span>·</span>
                <span className="text-violet-400">{detectionLevel.label.split(" (")[0]}</span>
                <span>·</span>
                <span>{scale}</span>
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
                    Plan Stealth Stack
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
                  Stealth deployment brief complete — fingerprint evasion, Cloudflare bypass, browser infrastructure, and operations runbook ready
                </div>
              )}
            </div>
          )}

          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #f9731620, #8b5cf620)", border: "1px solid #f9731630" }}>
                <EyeOff className="w-8 h-8" style={{ color: "#f9731660" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">Stealth & Anti-Detection ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Describe your authorized security research use case and configure the target environment. The pipeline produces a Playwright stealth fingerprint config, FlareSolverr deployment for Cloudflare bypass, managed browser infrastructure design, and a complete evasion matrix with Docker Compose.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "Playwright Stealth", color: "#f97316" },
                  { label: "FlareSolverr", color: "#8b5cf6" },
                  { label: "Fingerprint Evasion", color: "#f97316" },
                  { label: "Browserbase / Scrapoxy", color: "#10b981" },
                  { label: "Session Isolation", color: "#10b981" },
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
