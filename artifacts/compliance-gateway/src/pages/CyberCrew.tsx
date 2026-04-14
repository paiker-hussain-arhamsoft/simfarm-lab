import { useState, useRef, useEffect, useCallback } from "react";
import {
  Shield,
  Wifi,
  Terminal,
  FileSearch,
  SendHorizonal,
  Loader2,
  RotateCcw,
  ShieldCheck,
  Brain,
  Telescope,
  Clapperboard,
  MonitorPlay,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  ArrowRight,
  Target,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId = "red_team_strategist" | "dast_engineer" | "tls_fingerprint_engineer" | "security_director";

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
    id: "red_team_strategist",
    role: "Red Team Strategist",
    tool: "CAI by Alias Robotics",
    color: "#ef4444",
    bg: "bg-red-500/10",
    border: "border-red-500/30",
    desc: "Attack surface mapping, threat model, exploit path candidates, CAI agent loop",
    icon: Target,
  },
  {
    id: "dast_engineer",
    role: "DAST Engineer",
    tool: "CAI DAST · OWASP ZAP · Nuclei",
    color: "#f97316",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    desc: "Dynamic scanning pipeline, ZAP config, Nuclei templates, API fuzzing",
    icon: FileSearch,
  },
  {
    id: "tls_fingerprint_engineer",
    role: "TLS Fingerprint Engineer",
    tool: "Salesforce JA3 · JA3S · JARM",
    color: "#8b5cf6",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
    desc: "JA3 fingerprint analysis, browser signature rotation, cipher suite config",
    icon: Wifi,
  },
  {
    id: "security_director",
    role: "Security Director",
    tool: "Assessment Synthesis",
    color: "#06b6d4",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/30",
    desc: "Findings register, attack chain narrative, remediation roadmap, MITRE mapping",
    icon: Shield,
  },
];

const SCOPES = [
  "Web application",
  "API (REST/GraphQL)",
  "Mobile app backend",
  "Network infrastructure",
  "IoT / Embedded device",
  "ROS-based robot system",
];

const ATTACK_SURFACES = [
  "HTTP/HTTPS endpoints",
  "Authentication layer",
  "API endpoints",
  "Admin interfaces",
  "Third-party integrations",
  "WebSocket connections",
];

const PROTOCOLS = ["TLS 1.3", "TLS 1.2", "TLS 1.0/1.1", "DTLS", "mTLS"];

const BROWSER_TARGETS = [
  "Chrome 120",
  "Firefox 121",
  "Safari 17",
  "Edge 120",
  "curl 8.4",
  "Python requests 2.31",
];

const INTENSITIES = ["Passive (recon only)", "Low (safe checks)", "Moderate", "Aggressive (full active)", "Exhaustive"];

const FRAMEWORKS = [
  "OWASP / MITRE ATT&CK",
  "PTES (Pentest Execution Standard)",
  "NIST SP 800-115",
  "OWASP WSTG",
  "MITRE ATT&CK for ICS",
];

const PIPELINE_STEPS = [
  { label: "Red Team", icon: Target, color: "#ef4444" },
  { label: "DAST Scan", icon: FileSearch, color: "#f97316" },
  { label: "TLS / JA3", icon: Wifi, color: "#8b5cf6" },
  { label: "Assessment", icon: Shield, color: "#06b6d4" },
];

const EXAMPLE_TARGETS = [
  "Authorized test environment: internal web app at staging.example.com",
  "Authorized API audit: REST API with JWT auth for financial services app",
  "Bug bounty scope: e-commerce platform, all subdomains in scope",
  "IoT security research: ROS-based robotic arm control interface",
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
  const Icon = agent?.icon ?? Shield;
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
                  isActive || isDone
                    ? ""
                    : "border-border/40 text-muted-foreground"
                }`}
                style={
                  isActive || isDone
                    ? {
                        borderColor: step.color,
                        color: step.color,
                        backgroundColor: `${step.color}10`,
                      }
                    : {}
                }
              >
                <Icon className="w-3 h-3" />
                {step.label}
                {isActive && (
                  <span
                    className="w-1.5 h-1.5 rounded-full animate-pulse"
                    style={{ backgroundColor: step.color }}
                  />
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

export default function CyberCrew() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [target, setTarget] = useState("");
  const [scope, setScope] = useState(SCOPES[0]);
  const [attackSurface, setAttackSurface] = useState(ATTACK_SURFACES[0]);
  const [protocol, setProtocol] = useState(PROTOCOLS[0]);
  const [browserTarget, setBrowserTarget] = useState(BROWSER_TARGETS[0]);
  const [intensity, setIntensity] = useState(INTENSITIES[2]);
  const [framework, setFramework] = useState(FRAMEWORKS[0]);

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
    if (!target.trim() || runState === "running") return;

    setRunState("running");
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch("/api/cyber/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: target.trim(),
          scope,
          attackSurface,
          protocol,
          browserTarget,
          intensity,
          framework,
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
  }, [target, scope, attackSurface, protocol, browserTarget, intensity, framework, runState, sessionId]);

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
            <div className="w-8 h-8 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center">
              <Terminal className="w-4 h-4 text-red-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Cyber Crew</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 2</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-red-400" />
              <span className="text-xs text-muted-foreground">CAI · JA3 · OWASP ZAP · Nuclei</span>
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
              onClick={() => setLocation("/tier2")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Telescope className="w-3.5 h-3.5" />
              Intelligence
            </button>
            <button
              onClick={() => setLocation("/media-crew")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Clapperboard className="w-3.5 h-3.5" />
              Media Crew
            </button>
            <button
              onClick={() => setLocation("/video-stack")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <MonitorPlay className="w-3.5 h-3.5" />
              Video Stack
            </button>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden sm:inline">Compliance verified</span>
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
              <Terminal className="w-3.5 h-3.5 text-muted-foreground" />
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
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Engagement Config</p>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Scope</label>
              <select
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {SCOPES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Attack Surface</label>
              <select
                value={attackSurface}
                onChange={(e) => setAttackSurface(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {ATTACK_SURFACES.map((a) => <option key={a}>{a}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Wifi className="w-3 h-3" />TLS Protocol
              </label>
              <select
                value={protocol}
                onChange={(e) => setProtocol(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {PROTOCOLS.map((p) => <option key={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                <Wifi className="w-3 h-3 text-violet-400" />JA3 Spoof Target
              </label>
              <select
                value={browserTarget}
                onChange={(e) => setBrowserTarget(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {BROWSER_TARGETS.map((b) => <option key={b}>{b}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Scan Intensity</label>
              <select
                value={intensity}
                onChange={(e) => setIntensity(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {INTENSITIES.map((i) => <option key={i}>{i}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Compliance Framework</label>
              <select
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                disabled={runState === "running"}
                className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
              >
                {FRAMEWORKS.map((f) => <option key={f}>{f}</option>)}
              </select>
            </div>

            {/* JA3 info card */}
            <div className="rounded-lg border border-violet-500/20 bg-violet-500/5 p-3 mt-1">
              <p className="text-xs font-semibold text-violet-400 mb-1">JA3 Fingerprinting</p>
              <p className="text-xs text-muted-foreground">
                Salesforce JA3 hashes TLS client hellos: SSLVersion · Ciphers · Extensions · Curves · Points.
                Used for evasion research and detection gap analysis.
              </p>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Target input */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Engagement Target & Authorization Statement
            </label>
            <textarea
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="Describe the authorized target and authorization context (e.g., 'Authorized internal pentest of staging.example.com — written permission from CISO on file')..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-red-500/40 disabled:opacity-50"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline();
              }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example engagements:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_TARGETS.map((q) => (
                    <button
                      key={q}
                      onClick={() => setTarget(q)}
                      className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left"
                    >
                      {q.length > 65 ? q.slice(0, 65) + "…" : q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground space-x-2">
                <span className="font-medium text-foreground">{scope}</span>
                <span>·</span>
                <span>{intensity}</span>
                <span>·</span>
                <span className="text-violet-400">{browserTarget} JA3</span>
              </div>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button
                    onClick={reset}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />New Assessment
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
                    disabled={!target.trim() || runState === "done"}
                    onClick={runPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                    style={{
                      background: "linear-gradient(135deg, #ef4444, #8b5cf6)",
                      color: "white",
                    }}
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Run Assessment
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
                  Security assessment complete — red team plan, DAST pipeline, JA3 rotation strategy, and remediation roadmap ready
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
                  background: "linear-gradient(135deg, #ef444420, #8b5cf620)",
                  border: "1px solid #ef444430",
                }}
              >
                <Terminal className="w-8 h-8" style={{ color: "#ef444460" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">Cyber Crew ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Provide your authorized engagement target and context. The crew will produce a full red-team strategy, DAST scanning pipeline, JA3 TLS fingerprint rotation plan, and security assessment with MITRE ATT&CK mapping.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "CAI by Alias Robotics", color: "#ef4444" },
                  { label: "OWASP ZAP", color: "#f97316" },
                  { label: "Nuclei", color: "#f97316" },
                  { label: "Salesforce JA3", color: "#8b5cf6" },
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
