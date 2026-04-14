import { useState, useRef, useEffect, useCallback } from "react";
import {
  Brain,
  SendHorizonal,
  Loader2,
  ChevronRight,
  RotateCcw,
  ShieldCheck,
  User,
  Cpu,
  FlaskConical,
  Lightbulb,
  Layers,
  Zap,
  StopCircle,
  Copy,
  Check,
} from "lucide-react";
import { useSessionId } from "@/hooks/useSessionId";
import { useLocation } from "wouter";

type AgentId = "director" | "researcher" | "critic" | "synthesizer";

type AgentMeta = {
  id: AgentId;
  role: string;
  color: string;
  bg: string;
  border: string;
  desc: string;
  icon: React.ElementType;
};

const AGENTS: AgentMeta[] = [
  {
    id: "director",
    role: "Director",
    color: "#60a5fa",
    bg: "bg-blue-500/10",
    border: "border-blue-500/30",
    desc: "Decomposes tasks and orchestrates the agent pipeline",
    icon: Cpu,
  },
  {
    id: "researcher",
    role: "Researcher",
    color: "#34d399",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    desc: "Provides deep analysis, context and factual grounding",
    icon: FlaskConical,
  },
  {
    id: "critic",
    role: "Critic",
    color: "#f59e0b",
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    desc: "Stress-tests assumptions and sharpens the solution",
    icon: Lightbulb,
  },
  {
    id: "synthesizer",
    role: "Synthesizer",
    color: "#a78bfa",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
    desc: "Integrates all contributions into a final polished answer",
    icon: Layers,
  },
];

type AgentTurn = {
  agentId: AgentId;
  role: string;
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
      className={`rounded-xl border p-4 transition-all duration-300 ${
        active
          ? `${agent.bg} ${agent.border} shadow-lg`
          : done
          ? "bg-muted/20 border-border/60 opacity-70"
          : "bg-muted/10 border-border/40"
      }`}
    >
      <div className="flex items-center gap-2.5 mb-1.5">
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
          style={{ backgroundColor: `${agent.color}20`, border: `1px solid ${agent.color}40` }}
        >
          <Icon className="w-3.5 h-3.5" style={{ color: agent.color }} />
        </div>
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-xs font-semibold text-foreground truncate">
            {agent.role}
          </span>
          {active && (
            <span className="flex items-center gap-1 text-xs font-medium" style={{ color: agent.color }}>
              <Loader2 className="w-3 h-3 animate-spin" />
              Running
            </span>
          )}
          {done && !active && (
            <Check className="w-3 h-3 text-emerald-400 shrink-0" />
          )}
        </div>
      </div>
      <p className="text-xs text-muted-foreground leading-relaxed">{agent.desc}</p>
    </div>
  );
}

function AgentMessage({
  turn,
}: {
  turn: AgentTurn;
}) {
  const agent = AGENTS.find((a) => a.id === turn.agentId);
  const Icon = agent?.icon ?? Cpu;
  const [copied, setCopied] = useState(false);

  const copyContent = () => {
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
        {!turn.done && (
          <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />
        )}
        {turn.done && (
          <button
            onClick={copyContent}
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
        className="ml-8 text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap rounded-xl p-4 border"
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

const EXAMPLE_TASKS = [
  "Analyze the ethical implications of AI-generated deepfakes in political campaigns",
  "Design a framework for detecting and watermarking AI-generated media at scale",
  "Evaluate the legal liability of platforms hosting synthetic media content",
  "Propose guidelines for responsible use of voice cloning in education",
];

export default function StrategicBrain() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [task, setTask] = useState("");
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
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [turns]);

  const runPipeline = useCallback(async () => {
    if (!task.trim() || runState === "running") return;

    setRunState("running");
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch("/api/agents/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: task.trim(), session_id: sessionId }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        throw new Error(`API error: ${res.status}`);
      }

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
              {
                agentId,
                role: meta.role,
                color: meta.color,
                content: "",
                done: false,
              },
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
            setTurns((prev) =>
              prev.map((t) =>
                t.agentId === agentId ? { ...t, done: true } : t
              )
            );
            setDoneAgents((prev) => new Set([...prev, agentId]));
            setActiveAgent(null);
          } else if (event.type === "done") {
            setRunState("done");
          } else if (event.type === "error") {
            setError(event.message as string ?? "Unknown error");
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
  }, [task, runState, sessionId]);

  const stopPipeline = () => {
    abortRef.current?.abort();
    setRunState("idle");
    setActiveAgent(null);
  };

  const reset = () => {
    setTurns([]);
    setActiveAgent(null);
    setDoneAgents(new Set());
    setError(null);
    setRunState("idle");
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top bar */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center">
              <Brain className="w-4 h-4 text-primary" />
            </div>
            <div>
              <span className="text-sm font-bold text-foreground">
                Strategic Brain
              </span>
              <span className="ml-2 text-xs text-muted-foreground font-medium uppercase tracking-wider">
                TIER 1
              </span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 ml-3 px-2 py-1 rounded-md bg-muted/30 border border-border">
              <Zap className="w-3 h-3 text-amber-400" />
              <span className="text-xs text-muted-foreground">
                AutoGen · LangGraph compatible
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden sm:inline">Compliance verified</span>
            </div>
            <button
              onClick={() => setLocation("/tier2")}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              <Layers className="w-3.5 h-3.5" />
              TIER 2
            </button>
            <a
              href="/admin"
              className="text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1.5 rounded-lg hover:bg-muted/40 transition-colors"
            >
              Admin
            </a>
          </div>
        </div>
      </header>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 flex flex-col lg:flex-row gap-6">
        {/* Left panel: agents + input */}
        <aside className="lg:w-80 shrink-0 flex flex-col gap-4">
          {/* Agent pipeline overview */}
          <div className="rounded-2xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Agent Pipeline
              </span>
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

          {/* Session info */}
          <div className="rounded-xl border border-border bg-muted/20 px-4 py-3">
            <p className="text-xs text-muted-foreground">
              <span className="font-medium text-foreground">Session</span>{" "}
              <span className="font-mono text-primary/70 break-all">
                {sessionId.slice(0, 16)}…
              </span>
            </p>
          </div>
        </aside>

        {/* Main panel: task input + output */}
        <main className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Task input */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Task Input
            </label>
            <textarea
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Describe the task or problem you want the agent team to work on..."
              rows={3}
              disabled={runState === "running"}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) runPipeline();
              }}
            />

            {/* Example tasks */}
            {runState === "idle" && !turns.length && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">
                  Example tasks:
                </p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_TASKS.map((t) => (
                    <button
                      key={t}
                      onClick={() => setTask(t)}
                      className="text-xs px-3 py-1.5 rounded-lg border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors text-left"
                    >
                      {t.length > 55 ? t.slice(0, 55) + "…" : t}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-4">
              <p className="text-xs text-muted-foreground">
                {task.length}/4000 · Cmd+Enter to run
              </p>
              <div className="flex items-center gap-2">
                {(runState === "done" || runState === "error") && (
                  <button
                    onClick={reset}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    New Task
                  </button>
                )}
                {runState === "running" ? (
                  <button
                    onClick={stopPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-destructive/20 border border-destructive/30 text-destructive text-sm font-semibold hover:bg-destructive/30 transition-colors"
                  >
                    <StopCircle className="w-4 h-4" />
                    Stop
                  </button>
                ) : (
                  <button
                    disabled={!task.trim() || runState === "done"}
                    onClick={runPipeline}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {runState === "running" ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <SendHorizonal className="w-4 h-4" />
                    )}
                    Run Agents
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Agent output log */}
          {(turns.length > 0 || error) && (
            <div
              ref={logRef}
              className="flex-1 rounded-2xl border border-border bg-card p-5 overflow-y-auto max-h-[60vh] flex flex-col gap-6"
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
                  Pipeline complete — all 4 agents contributed
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!turns.length && !error && (
            <div className="flex-1 rounded-2xl border border-dashed border-border bg-muted/10 flex flex-col items-center justify-center p-12 text-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                <Brain className="w-8 h-8 text-primary/60" />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground mb-1">
                  Ready to orchestrate
                </p>
                <p className="text-xs text-muted-foreground max-w-xs">
                  Enter a task above and the four-agent pipeline will collaborate
                  — Director, Researcher, Critic, and Synthesizer — to produce a
                  high-quality result.
                </p>
              </div>
              <div className="flex items-center gap-6 text-xs text-muted-foreground mt-2">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-blue-400" />
                  Director
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  Researcher
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  Critic
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-violet-400" />
                  Synthesizer
                </span>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
