import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type AgentDef = {
  id: string;
  role: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (task: string, history: AgentTurn[]) => string;
};

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

const AGENTS: AgentDef[] = [
  {
    id: "director",
    role: "Director",
    color: "#60a5fa",
    systemPrompt: `You are the Director agent in a multi-agent AI system (TIER 1: Strategic Brain). 
Your role is to receive the user's task and decompose it into a clear, structured plan of attack.
Be concise, decisive, and strategic. Output a brief task decomposition (3-5 key sub-tasks) and state what each downstream agent should focus on.
Do not solve the task yourself — orchestrate it. Format your response in clear sections.`,
    buildUserPrompt: (task) =>
      `Incoming task:\n"${task}"\n\nDecompose this task and direct the other agents. Be concise.`,
  },
  {
    id: "researcher",
    role: "Researcher",
    color: "#34d399",
    systemPrompt: `You are the Researcher agent in a multi-agent AI system (TIER 1: Strategic Brain).
Your role is to provide deep analysis, relevant context, supporting evidence, and factual grounding for the task.
Draw on your knowledge to inform the solution. Be thorough but structured. Use bullet points and headers where helpful.`,
    buildUserPrompt: (task, history) => {
      const directive = history.find((h) => h.agent === "director")?.content ?? "";
      return `Original task:\n"${task}"\n\nDirector's plan:\n${directive}\n\nProvide your research and analysis to support this task.`;
    },
  },
  {
    id: "critic",
    role: "Critic",
    color: "#f59e0b",
    systemPrompt: `You are the Critic agent in a multi-agent AI system (TIER 1: Strategic Brain).
Your role is to rigorously challenge, stress-test, and refine the work done by the Director and Researcher.
Identify gaps, risks, assumptions, edge cases, and potential improvements. Be constructive but direct. Your critique sharpens the final output.`,
    buildUserPrompt: (task, history) => {
      const directive = history.find((h) => h.agent === "director")?.content ?? "";
      const research = history.find((h) => h.agent === "researcher")?.content ?? "";
      return `Original task:\n"${task}"\n\nDirector's plan:\n${directive}\n\nResearcher's analysis:\n${research}\n\nChallenge this work. What's missing, risky, or could be improved?`;
    },
  },
  {
    id: "synthesizer",
    role: "Synthesizer",
    color: "#a78bfa",
    systemPrompt: `You are the Synthesizer agent in a multi-agent AI system (TIER 1: Strategic Brain).
Your role is to integrate all prior agent outputs into a single, coherent, high-quality final response.
Incorporate the Director's plan, the Researcher's findings, and the Critic's improvements. 
Produce a polished, actionable final answer to the original task. Be comprehensive yet concise.`,
    buildUserPrompt: (task, history) => {
      const parts = history.map((h) => `${h.role}:\n${h.content}`).join("\n\n---\n\n");
      return `Original task:\n"${task}"\n\nAgent contributions:\n\n${parts}\n\nSynthesize all of this into a final, polished response.`;
    },
  },
];

router.post("/agents/run", async (req, res) => {
  const { task, session_id } = req.body ?? {};
  if (!task || typeof task !== "string" || task.trim().length === 0 || task.length > 4000) {
    res.status(400).json({ error: "Invalid request: task must be a non-empty string up to 4000 characters" });
    return;
  }
  if (!session_id || typeof session_id !== "string") {
    res.status(400).json({ error: "Invalid request: session_id is required" });
    return;
  }

  void session_id;

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  const history: AgentTurn[] = [];

  try {
    for (const agent of AGENTS) {
      send({
        type: "agent_start",
        agent: agent.id,
        role: agent.role,
        color: agent.color,
      });

      const userPrompt = agent.buildUserPrompt(task, history);
      let fullContent = "";

      const stream = await openai.chat.completions.create({
        model: "gpt-5.2",
        max_completion_tokens: 8192,
        messages: [
          { role: "system", content: agent.systemPrompt },
          { role: "user", content: userPrompt },
        ],
        stream: true,
      });

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          fullContent += content;
          send({ type: "token", agent: agent.id, content });
        }
      }

      history.push({ agent: agent.id, role: agent.role, content: fullContent });
      send({ type: "agent_done", agent: agent.id });
    }

    send({ type: "done" });
  } catch (err) {
    console.error("Agent pipeline error:", err);
    send({ type: "error", message: "Agent pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
