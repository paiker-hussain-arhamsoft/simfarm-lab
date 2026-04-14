import { useState, useRef, useEffect, useCallback } from "react";
import {
  FileText,
  Mic2,
  Video,
  Clapperboard,
  SendHorizonal,
  Loader2,
  RotateCcw,
  ShieldCheck,
  Shield,
  Telescope,
  Brain,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  Settings2,
  Clock,
  Users,
  ArrowRight,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId = "script_writer" | "voice_architect" | "video_director" | "production_lead";

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
    id: "script_writer",
    role: "Script Writer",
    tool: "Duix-Avatar",
    color: "#f472b6",
    bg: "bg-pink-500/10",
    border: "border-pink-500/30",
    desc: "Writes camera-ready scripts with lip-sync stage directions",
    icon: FileText,
  },
  {
    id: "voice_architect",
    role: "Voice Architect",
    tool: "Chatterbox · Coqui · Bark",
    color: "#fb923c",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    desc: "Designs voice cloning strategy and synthesis pipeline",
    icon: Mic2,
  },
  {
    id: "video_director",
    role: "Video Director",
    tool: "Wan2.1 · CogVideoX · Open-Sora",
    color: "#a78bfa",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
    desc: "Shot list, model selection, avatar compositing",
    icon: Video,
  },
  {
    id: "production_lead",
    role: "Production Lead",
    tool: "Pipeline Synthesis",
    color: "#34d399",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    desc: "Final production plan: toolchain, schedule, deliverables",
    icon: Clapperboard,
  },
];

const TONES = ["Professional", "Conversational", "Persuasive", "Authoritative", "Warm", "Urgent", "Educational"];
const DURATIONS = ["30 seconds", "60 seconds", "90 seconds", "2 minutes", "3 minutes", "5 minutes"];
const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "pa", label: "Punjabi (Shahmukhi) پنجابی" },
  { code: "skr", label: "Saraiki سرائیکی" },
  { code: "ur", label: "Urdu اردو" },
  { code: "ar", label: "Arabic العربية" },
  { code: "hi", label: "Hindi हिंदी" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "zh", label: "Chinese 中文" },
];
const VOICE_TOOLS = [
  { id: "chatterbox", label: "Chatterbox", badge: "MIT", note: "Zero-shot, 23 langs, 5s reference" },
  { id: "coqui", label: "Coqui XTTS-v2", badge: "Open", note: "Cross-lingual, fine-tunable" },
  { id: "bark", label: "Bark", badge: "MIT", note: "Expressive TTS, emotional cues" },
];
const VIDEO_TOOLS = [
  { id: "wan2", label: "Wan2.1", badge: "Apache 2.0", note: "Alibaba, 14B params, 720p RTX 4090" },
  { id: "cogvideo", label: "CogVideoX", badge: "Open", note: "Tsinghua, runs RTX 3060+" },
  { id: "opensora", label: "Open-Sora 2.0", badge: "Open", note: "11B params, VBench competitive" },
];

const PIPELINE_STEPS = [
  { label: "Script", icon: FileText, color: "#f472b6" },
  { label: "Voice Clone", icon: Mic2, color: "#fb923c" },
  { label: "Avatar Render", icon: Video, color: "#a78bfa" },
  { label: "Production Brief", icon: Clapperboard, color: "#34d399" },
];

const EXAMPLE_TOPICS = [
  "Campaign address on agricultural subsidies for rural Punjab farmers",
  "Educational video on safe digital media practices for youth",
  "Party manifesto highlights for multilingual broadcast",
  "Voter registration drive appeal in Saraiki-speaking constituencies",
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

function ToolBadge({ label, badge }: { label: string; badge: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-xs font-mono">
      {label}
      <span className="px-1 rounded text-[10px] bg-muted/60 text-muted-foreground border border-border">
        {badge}
      </span>
    </span>
  );
}

function AgentCard({ agent, active, done }: { agent: AgentMeta; active: boolean; done: boolean }) {
  const Icon = agent.icon;
  return (
    <div
      className={`rounded-xl border p-3.5 transition-all duration-300 ${
        active ? `${agent.bg} ${agent.border} shadow-lg` : done ? "bg-muted/20 border-border/60 opacity-60" : "bg-muted/10 border-border/40"
      }`}
    >
      <div className="flex items-center gap-2.5 mb-1">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0" style={{ backgroundColor: `${agent.color}20`, border: `1px solid ${agent.color}40` }}>
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
  const Icon = agent?.icon ?? FileText;
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(turn.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="group">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-6 h-6 rounded-md flex items-center justify-center shrink-0" style={{ backgroundColor: `${turn.color}20`, border: `1px solid ${turn.color}40` }}>
          <Icon className="w-3 h-3" style={{ color: turn.color }} />
        </div>
        <span className="text-xs font-semibold" style={{ color: turn.color }}>{turn.role}</span>
        <span className="text-xs text-muted-foreground/50 font-mono">· {turn.tool}</span>
        {!turn.done && <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />}
        {turn.done && (
          <button onClick={copy} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-muted/40">
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-muted-foreground" />}
          </button>
        )}
      </div>
      <div
        className="ml-8 text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap rounded-xl p-4 border font-mono text-xs"
        style={{ backgroundColor: `${turn.color}08`, borderColor: `${turn.color}20` }}
      >
        {turn.content}
        {!turn.done && (
          <span className="inline-block w-1.5 h-4 ml-0.5 rounded-sm animate-pulse" style={{ backgroundColor: turn.color }} />
        )}
      </div>
    </div>
  );
}

function PipelineFlow({ doneAgents, activeAgent }: { doneAgents: Set<AgentId>; activeAgent: AgentId | null }) {
  return (
    <div className="rounded-xl border border-border bg-card/50 p-4">
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Pipeline Flow</p>
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
                  isActive
                    ? "text-foreground border-current shadow-sm"
                    : isDone
                    ? "opacity-70"
                    : "border-border/40 text-muted-foreground"
                }`}
                style={isActive || isDone ? { borderColor: step.color, color: step.color, backgroundColor: `${step.color}10` } : {}}
              >
                <Icon className="w-3 h-3" />
                {step.label}
                {isActive && <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: step.color }} />}
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

export default function MediaCrew() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState(TONES[0]);
  const [language, setLanguage] = useState(LANGUAGES[0]);
  const [voiceTool, setVoiceTool] = useState(VOICE_TOOLS[0]);
  const [videoTool, setVideoTool] = useState(VIDEO_TOOLS[0]);
  const [duration, setDuration] = useState(DURATIONS[1]);
  const [targetAudience, setTargetAudience] = useState("General public");
  const [configOpen, setConfigOpen] = useState(true);

  const [runState, setRunState] = useState<RunState>("idle");
  const [turns, setTurns] = useState<AgentTurn[]>([]);
  const [activeAgent, setActiveAgent] = useState<AgentId | null>(null);
  const [doneAgents, setDoneAgents] = useState<Set<AgentId>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sessionStorage.getItem("compliance_acknowledged") !== "true") {
      setLocation("/");
    }
  }, []);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [turns]);

  const runPipeline = useCallback(async () => {
    if (!topic.trim() || runState === "running") return;

    setRunState("running");
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);
    setConfigOpen(false);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch("/api/media/produce", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim(),
          tone,
          language: language.label,
          voiceTool: voiceTool.label,
          videoTool: videoTool.label,
          duration,
          targetAudience,
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
              { agentId, role: meta.role, tool: meta.tool, color: meta.color, content: "", done: false },
            ]);
          } else if (event.type === "token") {
            const agentId = event.agent as AgentId;
            setTurns((prev) =>
              prev.map((t) => t.agentId === agentId && !t.done ? { ...t, content: t.content + (event.content as string) } : t)
            );
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
  }, [topic, tone, language, voiceTool, videoTool, duration, targetAudience, runState, sessionId]);

  const reset = () => {
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);
    setRunState("idle");
    setConfigOpen(true);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-pink-500/10 border border-pink-500/30 flex items-center justify-center">
              <Clapperboard className="w-4 h-4 text-pink-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Media Crew</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 2</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-pink-400" />
              <span className="text-xs text-muted-foreground">Duix-Avatar · Chatterbox · Wan2.1 · Open-Sora</span>
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
              onClick={() => setLocation("/video-stack")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-rose-500/30 bg-rose-500/5 px-2.5 py-1.5 rounded-lg hover:bg-rose-500/10 transition-colors text-rose-400/80"
            >
              <Video className="w-3.5 h-3.5" />
              Video Stack
            </button>
            <button
              onClick={() => setLocation("/cyber-crew")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-red-500/30 bg-red-500/5 px-2.5 py-1.5 rounded-lg hover:bg-red-500/10 transition-colors text-red-400/80"
            >
              <Shield className="w-3.5 h-3.5" />
              Cyber Crew
            </button>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden sm:inline">Compliance verified</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 flex flex-col lg:flex-row gap-6">
        {/* Left sidebar */}
        <aside className="lg:w-80 shrink-0 flex flex-col gap-4">
          {/* Agent cards */}
          <div className="rounded-2xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 mb-4">
              <Clapperboard className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Duix-Avatar Pipeline
              </span>
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

          {/* Production config */}
          <div className="rounded-2xl border border-border bg-card overflow-hidden">
            <button
              onClick={() => setConfigOpen((o) => !o)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/20 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Settings2 className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Production Config
                </span>
              </div>
              <ChevronRight className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${configOpen ? "rotate-90" : ""}`} />
            </button>

            {configOpen && (
              <div className="px-4 pb-4 flex flex-col gap-3 border-t border-border pt-3">
                {/* Tone */}
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">Tone</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    disabled={runState === "running"}
                    className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
                  >
                    {TONES.map((t) => <option key={t}>{t}</option>)}
                  </select>
                </div>

                {/* Language */}
                <div>
                  <label className="block text-xs text-muted-foreground mb-1 flex items-center gap-1">
                    Language
                  </label>
                  <select
                    value={language.code}
                    onChange={(e) => setLanguage(LANGUAGES.find((l) => l.code === e.target.value) ?? LANGUAGES[0])}
                    disabled={runState === "running"}
                    className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
                  >
                    {LANGUAGES.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
                  </select>
                </div>

                {/* Duration */}
                <div>
                  <label className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                    <Clock className="w-3 h-3" />
                    Duration
                  </label>
                  <select
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    disabled={runState === "running"}
                    className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50"
                  >
                    {DURATIONS.map((d) => <option key={d}>{d}</option>)}
                  </select>
                </div>

                {/* Target Audience */}
                <div>
                  <label className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                    <Users className="w-3 h-3" />
                    Target Audience
                  </label>
                  <input
                    type="text"
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    disabled={runState === "running"}
                    className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-50"
                    placeholder="e.g. Rural voters, age 30-60"
                  />
                </div>

                {/* Voice tool */}
                <div>
                  <label className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                    <Mic2 className="w-3 h-3" />
                    Voice Engine
                  </label>
                  <div className="flex flex-col gap-1">
                    {VOICE_TOOLS.map((vt) => (
                      <button
                        key={vt.id}
                        onClick={() => setVoiceTool(vt)}
                        disabled={runState === "running"}
                        className={`flex items-start gap-2 p-2 rounded-lg border text-left transition-colors disabled:opacity-50 ${
                          voiceTool.id === vt.id
                            ? "border-orange-500/50 bg-orange-500/10 text-orange-400"
                            : "border-border/50 text-muted-foreground hover:bg-muted/30"
                        }`}
                      >
                        <div className="flex-1 min-w-0">
                          <ToolBadge label={vt.label} badge={vt.badge} />
                          <p className="text-xs text-muted-foreground mt-0.5">{vt.note}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Video tool */}
                <div>
                  <label className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                    <Video className="w-3 h-3" />
                    Video Model
                  </label>
                  <div className="flex flex-col gap-1">
                    {VIDEO_TOOLS.map((vt) => (
                      <button
                        key={vt.id}
                        onClick={() => setVideoTool(vt)}
                        disabled={runState === "running"}
                        className={`flex items-start gap-2 p-2 rounded-lg border text-left transition-colors disabled:opacity-50 ${
                          videoTool.id === vt.id
                            ? "border-violet-500/50 bg-violet-500/10 text-violet-400"
                            : "border-border/50 text-muted-foreground hover:bg-muted/30"
                        }`}
                      >
                        <div className="flex-1 min-w-0">
                          <ToolBadge label={vt.label} badge={vt.badge} />
                          <p className="text-xs text-muted-foreground mt-0.5">{vt.note}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Main panel */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Topic input */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Production Brief
            </label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Describe the message, campaign, or content you want the avatar to deliver..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-pink-500/40 disabled:opacity-50"
              onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline(); }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example productions:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_TOPICS.map((q) => (
                    <button
                      key={q}
                      onClick={() => setTopic(q)}
                      className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left"
                    >
                      {q.length > 58 ? q.slice(0, 58) + "…" : q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground space-x-2">
                <span className="font-medium text-foreground">{tone}</span>
                <span>·</span>
                <span>{duration}</span>
                <span>·</span>
                <span>{language.label.split(" ")[0]}</span>
              </div>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button
                    onClick={reset}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    New Production
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
                    disabled={!topic.trim() || runState === "done"}
                    onClick={runPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                    style={{ background: "linear-gradient(135deg, #f472b6, #a78bfa)", color: "white" }}
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Produce
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Pipeline flow tracker */}
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
                  Production brief complete — script, voice, video, and pipeline plan ready
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #f472b620, #a78bfa20)", border: "1px solid #f472b630" }}>
                <Clapperboard className="w-8 h-8" style={{ color: "#f472b660" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">Duix-Avatar Pipeline ready</p>
                <p className="text-xs text-muted-foreground max-w-xs">
                  Enter your production brief, configure the tools on the left, and the crew will generate a complete script, voice cloning strategy, shot list, and production plan.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "Duix-Avatar", color: "#f472b6" },
                  { label: "Chatterbox", color: "#fb923c" },
                  { label: "Wan2.1", color: "#a78bfa" },
                  { label: "Open-Sora", color: "#34d399" },
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
