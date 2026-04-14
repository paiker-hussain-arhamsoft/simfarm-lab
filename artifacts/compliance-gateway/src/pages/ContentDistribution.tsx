import { useState, useRef, useEffect, useCallback } from "react";
import {
  Rss,
  Mail,
  Database,
  Share2,
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
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  ArrowRight,
  Layers,
  Calendar,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId =
  | "mautic_architect"
  | "strapi_engineer"
  | "postiz_manager"
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
    id: "mautic_architect",
    role: "Marketing Automation Architect",
    tool: "Mautic · Drip Campaigns · Lead Scoring",
    color: "#f97316",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    desc: "Docker deploy, email infra, drip sequence design, lead scoring, segment architecture, landing pages, tracking, API integration",
    icon: Mail,
  },
  {
    id: "strapi_engineer",
    role: "CMS Engineer",
    tool: "Strapi · AI Plugins · Auto-publishing",
    color: "#8b5cf6",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
    desc: "Content type schema, AI plugin config, lifecycle hooks, satellite site pipeline, webhook chain, media handling, scheduling",
    icon: Database,
  },
  {
    id: "postiz_manager",
    role: "Social Media Manager",
    tool: "Postiz · AI Generation · Scheduling",
    color: "#10b981",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    desc: "Platform setup, AI caption generation, content calendar, Strapi→Postiz automation, repurposing matrix, hashtag strategy, analytics",
    icon: Share2,
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#f43f5e",
    bg: "bg-rose-500/10",
    border: "border-rose-500/30",
    desc: "Master Docker Compose, full pipeline diagram, DNS setup, cost model, 4-week content calendar, monitoring, scaling playbook",
    icon: BarChart2,
  },
];

type PlatformOption = { id: string; label: string; note: string };

const NICHES: PlatformOption[] = [
  { id: "research", label: "Research / Education", note: "Academic, how-to, technical explainers" },
  { id: "finance", label: "Finance / Economics", note: "Markets, policy, personal finance" },
  { id: "tech", label: "Technology", note: "Software, AI, hardware, cybersecurity" },
  { id: "health", label: "Health / Wellness", note: "Medical research, nutrition, mental health" },
  { id: "politics", label: "Policy / Politics", note: "Analysis, opinion, public affairs" },
  { id: "custom", label: "Custom / Multi-niche", note: "Define in use case description" },
];

const CADENCES: PlatformOption[] = [
  { id: "daily", label: "Daily", note: "1 article/day + 3–5 social posts" },
  { id: "3x", label: "3× per week", note: "Balanced quality/volume" },
  { id: "weekly", label: "Weekly", note: "High-quality long-form focus" },
  { id: "aggressive", label: "Multiple per day", note: "High-volume content machine" },
];

const PLATFORMS_OPTIONS = [
  "Twitter / X",
  "Twitter + LinkedIn",
  "Twitter + LinkedIn + Facebook",
  "Instagram + TikTok",
  "Full stack (all major platforms)",
  "LinkedIn only (B2B)",
  "Reddit + Discord (community)",
];

const CONTENT_TYPES_OPTIONS = [
  "Articles + Social posts",
  "Long-form + Newsletters",
  "Short-form + Threads",
  "Video scripts + Social",
  "Full mix (articles, video, email, social)",
];

const SATELLITE_SITES_OPTIONS = [
  "1 primary site only",
  "2–5 sites",
  "5–20 sites",
  "20–100 sites",
  "100+ satellite network",
];

const AUDIENCE_OPTIONS = [
  "Researchers and practitioners",
  "General public",
  "Professionals / B2B",
  "Young adults (18–35)",
  "Decision makers / executives",
  "Global multilingual audience",
];

const EXAMPLE_CASES = [
  "Academic research: automated distribution of open-access papers to niche educational blogs and academic social accounts",
  "Policy think tank: daily briefings auto-published across 20 satellite sites with Mautic email digest for subscribers",
  "Tech media: AI-assisted article generation in Strapi, auto-scheduled to Twitter/LinkedIn via Postiz, drip for newsletter growth",
  "Health education NGO: multilingual content machine — Strapi i18n → 15 country sites → Postiz scheduling per timezone",
];

const PIPELINE_STEPS = [
  { label: "Mautic", icon: Mail, color: "#f97316" },
  { label: "Strapi", icon: Database, color: "#8b5cf6" },
  { label: "Postiz", icon: Share2, color: "#10b981" },
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
  const Icon = agent?.icon ?? Rss;
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

export default function ContentDistribution() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [useCase, setUseCase] = useState("");
  const [niche, setNiche] = useState(NICHES[0]);
  const [cadence, setCadence] = useState(CADENCES[0]);
  const [platforms, setPlatforms] = useState(PLATFORMS_OPTIONS[2]);
  const [contentTypes, setContentTypes] = useState(CONTENT_TYPES_OPTIONS[0]);
  const [satelliteSites, setSatelliteSites] = useState(SATELLITE_SITES_OPTIONS[1]);
  const [targetAudience, setTargetAudience] = useState(AUDIENCE_OPTIONS[0]);

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
      const res = await fetch("/api/content/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          useCase: useCase.trim(),
          niche: niche.label,
          targetAudience,
          publishingCadence: cadence.label,
          platforms,
          contentTypes,
          satelliteSites,
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
  }, [useCase, niche, cadence, platforms, contentTypes, satelliteSites, targetAudience, runState, sessionId]);

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
              <Rss className="w-4 h-4 text-orange-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Content Distribution</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 4</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-orange-400" />
              <span className="text-xs text-muted-foreground">Mautic · Strapi · Postiz · Blogger Machine</span>
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
              <Rss className="w-3.5 h-3.5 text-muted-foreground" />
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
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Content Config</p>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Layers className="w-3 h-3" />Niche
              </label>
              <OptionSelector options={NICHES} selected={niche} onSelect={setNiche} disabled={runState === "running"} accentColor="#f97316" />
            </div>

            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5">
                <Calendar className="w-3 h-3" />Publishing Cadence
              </label>
              <OptionSelector options={CADENCES} selected={cadence} onSelect={setCadence} disabled={runState === "running"} accentColor="#8b5cf6" />
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Platforms</label>
              <select value={platforms} onChange={(e) => setPlatforms(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {PLATFORMS_OPTIONS.map((p) => <option key={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Content Types</label>
              <select value={contentTypes} onChange={(e) => setContentTypes(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {CONTENT_TYPES_OPTIONS.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Satellite Sites</label>
              <select value={satelliteSites} onChange={(e) => setSatelliteSites(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {SATELLITE_SITES_OPTIONS.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs text-muted-foreground mb-1">Target Audience</label>
              <select value={targetAudience} onChange={(e) => setTargetAudience(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {AUDIENCE_OPTIONS.map((a) => <option key={a}>{a}</option>)}
              </select>
            </div>

            <div className="rounded-lg border border-orange-500/20 bg-orange-500/5 p-3 mt-1">
              <p className="text-xs font-semibold text-orange-400 mb-1">Mautic · Strapi · Postiz</p>
              <p className="text-xs text-muted-foreground">
                All three platforms are open-source and self-hostable. Mautic (AGPLv3) for email automation, Strapi (MIT) for headless CMS with AI plugins, Postiz (AGPLv3) for social scheduling.
              </p>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Research / Distribution Use Case
            </label>
            <textarea
              value={useCase}
              onChange={(e) => setUseCase(e.target.value)}
              placeholder="Describe the authorized research, educational, or NGO content distribution use case for this pipeline..."
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
                <span className="font-medium text-foreground">{niche.label}</span>
                <span>·</span>
                <span className="text-violet-400">{cadence.label}</span>
                <span>·</span>
                <span>{satelliteSites}</span>
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
                    Plan Pipeline
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
                  Blogger Machine deployment brief complete — Mautic automation, Strapi CMS pipeline, Postiz social scheduling, and full operations runbook ready
                </div>
              )}
            </div>
          )}

          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #f9731620, #8b5cf620)", border: "1px solid #f9731630" }}>
                <Rss className="w-8 h-8" style={{ color: "#f9731660" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">Blogger Machine ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Describe your authorized content distribution use case and configure the pipeline. The system produces a Mautic drip campaign design, Strapi CMS with AI auto-publishing, Postiz social scheduling across all platforms, and a master Docker Compose with full cost model.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "Mautic Drip Campaigns", color: "#f97316" },
                  { label: "Strapi AI Publishing", color: "#8b5cf6" },
                  { label: "Postiz Scheduling", color: "#10b981" },
                  { label: "Satellite Sites", color: "#8b5cf6" },
                  { label: "Lead Scoring", color: "#f97316" },
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
