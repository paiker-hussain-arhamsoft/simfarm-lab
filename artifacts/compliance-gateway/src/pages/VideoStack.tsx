import { useState, useRef, useEffect, useCallback } from "react";
import {
  Layers,
  Mic,
  Cpu,
  Film,
  SendHorizonal,
  Loader2,
  RotateCcw,
  ShieldCheck,
  Brain,
  Telescope,
  Clapperboard,
  StopCircle,
  Copy,
  Check,
  ChevronRight,
  Zap,
  MonitorPlay,
  ArrowRight,
  Shield,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId = "face_architect" | "lipsync_engineer" | "render_strategist" | "technical_director";

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
    id: "face_architect",
    role: "Face Architect",
    tool: "DeepFaceLab · FaceSwap · Deep-Live-Cam",
    color: "#f43f5e",
    bg: "bg-rose-500/10",
    border: "border-rose-500/30",
    desc: "Model selection, extraction pipeline, training config, merge settings",
    icon: Layers,
  },
  {
    id: "lipsync_engineer",
    role: "Lip Sync Engineer",
    tool: "Wav2Lip · VideoRetalking",
    color: "#f97316",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    desc: "Audio preprocessing, inference pipeline, temporal consistency",
    icon: Mic,
  },
  {
    id: "render_strategist",
    role: "Render Strategist",
    tool: "Pipeline Orchestration",
    color: "#eab308",
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/30",
    desc: "Batch processing, post-processing chain, automation scripts",
    icon: Cpu,
  },
  {
    id: "technical_director",
    role: "Technical Director",
    tool: "Production Synthesis",
    color: "#6366f1",
    bg: "bg-indigo-500/10",
    border: "border-indigo-500/30",
    desc: "Complete CLI sequence, environment setup, hardware matrix, QA",
    icon: Film,
  },
];

const FACE_SWAP_TOOLS = [
  { id: "dfl", label: "DeepFaceLab", badge: "GPL-3", note: "Industry standard, CLI batch, DF/LIAE/SAE models" },
  { id: "faceswap", label: "FaceSwap", badge: "GPL-3", note: "TensorFlow, GUI+CLI, Win/Mac/Linux" },
  { id: "deeplivecam", label: "Deep-Live-Cam", badge: "MIT", note: "Real-time, single source image, virtual cam" },
];

const LIPSYNC_TOOLS = [
  { id: "wav2lip", label: "Wav2Lip", badge: "Open", note: "GAN-based, any video, LRS2 pretrained" },
  { id: "videoretalking", label: "VideoRetalking", badge: "MIT", note: "ECCV 2022, full face enhancement + sync" },
];

const MODES = ["Offline batch", "Real-time (Deep-Live-Cam)", "Semi-automated"];
const SOURCE_MEDIA = ["Pre-recorded video", "Single photo", "Webcam feed", "Image sequence"];
const OUTPUT_FORMATS = ["MP4 H.264", "MP4 H.265", "WebM VP9", "Image sequence PNG", "ProRes 422"];
const DURATIONS = ["15 seconds", "30 seconds", "60 seconds", "2 minutes", "5 minutes", "Long-form"];

const PIPELINE_STEPS = [
  { label: "Face Swap", icon: Layers, color: "#f43f5e" },
  { label: "Lip Sync", icon: Mic, color: "#f97316" },
  { label: "Render", icon: Cpu, color: "#eab308" },
  { label: "Production Brief", icon: Film, color: "#6366f1" },
];

const EXAMPLE_CASES = [
  "Research anchor for multilingual news broadcast using consented talent",
  "Educational explainer where historical figure delivers reconstructed speech",
  "Accessibility video with lip-sync adapted for hearing-impaired viewers",
  "Political candidate avatar for regional language campaign (consented)",
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
    <div className={`rounded-xl border p-3.5 transition-all duration-300 ${active ? `${agent.bg} ${agent.border} shadow-lg` : done ? "bg-muted/20 border-border/60 opacity-60" : "bg-muted/10 border-border/40"}`}>
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
      <span className="text-xs font-mono" style={{ color: agent.color }}>{agent.tool}</span>
    </div>
  );
}

function AgentMessage({ turn }: { turn: AgentTurn }) {
  const agent = AGENTS.find((a) => a.id === turn.agentId);
  const Icon = agent?.icon ?? Film;
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
        className="ml-8 text-xs text-foreground/90 leading-relaxed whitespace-pre-wrap rounded-xl p-4 border font-mono"
        style={{ backgroundColor: `${turn.color}08`, borderColor: `${turn.color}20` }}
      >
        {turn.content}
        {!turn.done && <span className="inline-block w-1.5 h-4 ml-0.5 rounded-sm animate-pulse" style={{ backgroundColor: turn.color }} />}
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
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all duration-300 ${isActive ? "shadow-sm" : isDone ? "opacity-70" : "border-border/40 text-muted-foreground"}`}
                style={isActive || isDone ? { borderColor: step.color, color: step.color, backgroundColor: `${step.color}10` } : {}}
              >
                <Icon className="w-3 h-3" />
                {step.label}
                {isActive && <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: step.color }} />}
                {isDone && <Check className="w-3 h-3" />}
              </div>
              {i < PIPELINE_STEPS.length - 1 && <ArrowRight className="w-3 h-3 text-muted-foreground/30 shrink-0" />}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ToolSelector<T extends { id: string; label: string; badge: string; note: string }>({
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
          className={`flex items-start gap-2 p-2.5 rounded-lg border text-left transition-colors disabled:opacity-50 ${selected.id === t.id ? "text-foreground" : "border-border/50 text-muted-foreground hover:bg-muted/30"}`}
          style={selected.id === t.id ? { borderColor: `${accentColor}50`, backgroundColor: `${accentColor}10`, color: accentColor } : {}}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="text-xs font-semibold">{t.label}</span>
              <span className="px-1 rounded text-[10px] bg-muted/60 text-muted-foreground border border-border font-mono">{t.badge}</span>
            </div>
            <p className="text-xs text-muted-foreground">{t.note}</p>
          </div>
        </button>
      ))}
    </div>
  );
}

export default function VideoStack() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [useCase, setUseCase] = useState("");
  const [faceSwapTool, setFaceSwapTool] = useState(FACE_SWAP_TOOLS[0]);
  const [lipSyncTool, setLipSyncTool] = useState(LIPSYNC_TOOLS[0]);
  const [mode, setMode] = useState(MODES[0]);
  const [sourceMedia, setSourceMedia] = useState(SOURCE_MEDIA[0]);
  const [outputFormat, setOutputFormat] = useState(OUTPUT_FORMATS[0]);
  const [duration, setDuration] = useState(DURATIONS[2]);

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
      const res = await fetch("/api/video/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          useCase: useCase.trim(),
          faceSwapTool: faceSwapTool.label,
          lipSyncTool: lipSyncTool.label,
          mode,
          sourceMedia,
          outputFormat,
          duration,
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
            setTurns((prev) => [...prev, { agentId, role: meta.role, tool: meta.tool, color: meta.color, content: "", done: false }]);
          } else if (event.type === "token") {
            const agentId = event.agent as AgentId;
            setTurns((prev) => prev.map((t) => t.agentId === agentId && !t.done ? { ...t, content: t.content + (event.content as string) } : t));
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
  }, [useCase, faceSwapTool, lipSyncTool, mode, sourceMedia, outputFormat, duration, runState, sessionId]);

  const reset = () => {
    setTurns([]); setActiveAgent(null); setDoneAgents(new Set());
    setError(null); setRunState("idle");
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center">
              <MonitorPlay className="w-4 h-4 text-rose-400" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">Video Deepfake Stack</span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">TIER 2</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-rose-400" />
              <span className="text-xs text-muted-foreground">DeepFaceLab · FaceSwap · Wav2Lip · VideoRetalking</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setLocation("/tool")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Brain className="w-3.5 h-3.5" />TIER 1
            </button>
            <button onClick={() => setLocation("/tier2")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Telescope className="w-3.5 h-3.5" />Intelligence
            </button>
            <button onClick={() => setLocation("/media-crew")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors">
              <Clapperboard className="w-3.5 h-3.5" />Media Crew
            </button>
            <button onClick={() => setLocation("/cyber-crew")} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-red-500/30 bg-red-500/5 px-2.5 py-1.5 rounded-lg hover:bg-red-500/10 transition-colors text-red-400/80">
              <Shield className="w-3.5 h-3.5" />Cyber Crew
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
              <MonitorPlay className="w-3.5 h-3.5 text-muted-foreground" />
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
          <div className="rounded-2xl border border-border bg-card p-4 flex flex-col gap-4">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Stack Config</p>

            {/* Face swap tool */}
            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-2">
                <Layers className="w-3 h-3" />Face Swap Tool
              </label>
              <ToolSelector options={FACE_SWAP_TOOLS} selected={faceSwapTool} onSelect={setFaceSwapTool} disabled={runState === "running"} accentColor="#f43f5e" />
            </div>

            {/* Lip sync tool */}
            <div>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground mb-2">
                <Mic className="w-3 h-3" />Lip Sync Tool
              </label>
              <ToolSelector options={LIPSYNC_TOOLS} selected={lipSyncTool} onSelect={setLipSyncTool} disabled={runState === "running"} accentColor="#f97316" />
            </div>

            {/* Mode */}
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Processing Mode</label>
              <select value={mode} onChange={(e) => setMode(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {MODES.map((m) => <option key={m}>{m}</option>)}
              </select>
            </div>

            {/* Source media */}
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Source Media</label>
              <select value={sourceMedia} onChange={(e) => setSourceMedia(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {SOURCE_MEDIA.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>

            {/* Output format */}
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Output Format</label>
              <select value={outputFormat} onChange={(e) => setOutputFormat(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {OUTPUT_FORMATS.map((f) => <option key={f}>{f}</option>)}
              </select>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Duration</label>
              <select value={duration} onChange={(e) => setDuration(e.target.value)} disabled={runState === "running"} className="w-full rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs text-foreground focus:outline-none disabled:opacity-50">
                {DURATIONS.map((d) => <option key={d}>{d}</option>)}
              </select>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Use case input */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Use Case Brief
            </label>
            <textarea
              value={useCase}
              onChange={(e) => setUseCase(e.target.value)}
              placeholder="Describe the educational or research use case for this video deepfake pipeline..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-rose-500/40 disabled:opacity-50"
              onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline(); }}
            />

            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Example use cases:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_CASES.map((q) => (
                    <button key={q} onClick={() => setUseCase(q)} className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left">
                      {q.length > 60 ? q.slice(0, 60) + "…" : q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground space-x-2">
                <span className="font-medium text-foreground">{faceSwapTool.label}</span>
                <span>+</span>
                <span className="font-medium text-foreground">{lipSyncTool.label}</span>
                <span>·</span>
                <span>{mode}</span>
              </div>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button onClick={reset} className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors">
                    <RotateCcw className="w-3.5 h-3.5" />New Brief
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
                    style={{ background: "linear-gradient(135deg, #f43f5e, #6366f1)", color: "white" }}
                  >
                    <SendHorizonal className="w-4 h-4" />
                    Plan Stack
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Pipeline tracker */}
          {runState !== "idle" && <PipelineFlow doneAgents={doneAgents} activeAgent={activeAgent} />}

          {/* Agent outputs */}
          {(turns.length > 0 || error) && (
            <div ref={logRef} className="flex-1 rounded-2xl border border-border bg-card p-5 overflow-y-auto max-h-[65vh] flex flex-col gap-6">
              {error && <div className="rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</div>}
              {turns.map((turn, i) => <AgentMessage key={`${turn.agentId}-${i}`} turn={turn} />)}
              {runState === "done" && (
                <div className="pt-2 border-t border-border text-center text-xs text-muted-foreground">
                  Technical production brief complete — face swap, lip sync, render, and full CLI pipeline ready
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #f43f5e20, #6366f120)", border: "1px solid #f43f5e30" }}>
                <MonitorPlay className="w-8 h-8" style={{ color: "#f43f5e60" }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">Video Deepfake Stack ready</p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Describe your educational research use case, configure the face-swap and lip-sync tools on the left, and receive a complete technical production brief with CLI commands and hardware specs.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-muted-foreground mt-1">
                {[
                  { label: "DeepFaceLab", color: "#f43f5e" },
                  { label: "FaceSwap", color: "#f43f5e" },
                  { label: "Wav2Lip", color: "#f97316" },
                  { label: "VideoRetalking", color: "#eab308" },
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
