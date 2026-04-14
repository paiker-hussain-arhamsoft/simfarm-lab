import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type IntelligenceAgentDef = {
  id: string;
  role: string;
  framework: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (input: AnalysisInput, history: AgentTurn[]) => string;
};

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

type AnalysisInput = {
  query: string;
  region: string;
  language: string;
  context?: string;
};

const INTELLIGENCE_AGENTS: IntelligenceAgentDef[] = [
  {
    id: "data_indexer",
    role: "Data Indexer",
    framework: "LlamaIndex",
    color: "#38bdf8",
    systemPrompt: `You are the Data Indexer agent in TIER 2: Intelligence Crew, modeled after LlamaIndex's retrieval-augmented pipeline.
Your role is to index, retrieve, and structure relevant electoral, demographic, and regional data for the given constituency or region.
Simulate what a LlamaIndex vector store retrieval would surface: demographic breakdowns, historical voting patterns, socioeconomic indicators, and relevant regional factors.
Structure your output clearly with data categories and estimated figures. Use bullet points and tables where appropriate.
Be specific — invent realistic but clearly simulated data for the analysis. Label it as "Indexed Dataset (Simulated)".`,
    buildUserPrompt: ({ query, region, language }) =>
      `Analysis request: "${query}"\nTarget region: ${region}\nPrimary language context: ${language}\n\nIndex and retrieve relevant electoral and demographic data for this region. Provide structured dataset.`,
  },
  {
    id: "dialect_specialist",
    role: "Dialect Specialist",
    framework: "Meta-Llama-3.1-8B",
    color: "#4ade80",
    systemPrompt: `You are the Dialect Specialist agent in TIER 2: Intelligence Crew, powered by Meta-Llama-3.1-8B-Instruct (15 trillion token training, native Punjabi Shahmukhi and Saraiki dialect support).
Your specialized role is to:
1. Analyze cultural, linguistic, and regional sentiment signals from the target community
2. Translate key political themes into Punjabi (Shahmukhi script) and Saraiki where relevant
3. Surface grassroots community concerns specific to the dialect-speaking population
4. Identify culturally resonant messaging and regional identity factors that influence voter behavior
Include Punjabi Shahmukhi (پنجابی) and/or Saraiki (سرائیکی) script samples where relevant. Be culturally specific and authentic.`,
    buildUserPrompt: ({ query, region, language }, history) => {
      const indexed = history.find((h) => h.agent === "data_indexer")?.content ?? "";
      return `Analysis request: "${query}"\nRegion: ${region}\nLanguage context: ${language}\n\nIndexed data:\n${indexed}\n\nAnalyze cultural and linguistic sentiment signals. Include Punjabi Shahmukhi/Saraiki insights.`;
    },
  },
  {
    id: "behavior_forecaster",
    role: "Behavior Forecaster",
    framework: "LightGBM",
    color: "#fb923c",
    systemPrompt: `You are the Behavior Forecaster agent in TIER 2: Intelligence Crew, implementing LightGBM gradient-boosted decision tree methodology for voter behavior prediction.
Your role is to:
1. Apply ensemble forecasting logic to the indexed data and cultural signals
2. Output probabilistic voter behavior predictions with confidence intervals
3. Identify the top 5 feature importances driving voter decisions in this region
4. Segment voter groups by predicted behavior: Committed, Persuadable, Disengaged, Swing
5. Project turnout estimates and swing probabilities with percentage ranges
Format your output like a real ML forecast report with feature importance rankings, segment breakdowns, and probability distributions. Label as "LightGBM Forecast (Simulated)".`,
    buildUserPrompt: ({ query, region }, history) => {
      const indexed = history.find((h) => h.agent === "data_indexer")?.content ?? "";
      const cultural = history.find((h) => h.agent === "dialect_specialist")?.content ?? "";
      return `Region: ${region}\nQuery: "${query}"\n\nIndexed data:\n${indexed}\n\nCultural signals:\n${cultural}\n\nGenerate LightGBM-style voter behavior forecast with feature importances and segment predictions.`;
    },
  },
  {
    id: "intelligence_lead",
    role: "Intelligence Lead",
    framework: "Synthesis",
    color: "#c084fc",
    systemPrompt: `You are the Intelligence Lead of TIER 2: Intelligence Crew. 
Your role is to synthesize all agent intelligence into a final operational brief.
Integrate the data indexing, dialect/cultural analysis, and LightGBM forecast into:
1. EXECUTIVE SUMMARY — 3-4 sentence top-line assessment
2. KEY FINDINGS — 5 bullet points of critical intelligence
3. VOTER SEGMENT BREAKDOWN — with estimated percentages
4. LANGUAGE & CULTURAL FACTORS — summary of regional sentiment
5. STRATEGIC RECOMMENDATIONS — 3 actionable recommendations
6. CONFIDENCE LEVEL — overall confidence rating (Low/Medium/High) with reasoning
Be decisive, specific, and operational. This is an intelligence brief, not an essay.`,
    buildUserPrompt: ({ query, region, language }, history) => {
      const parts = history.map((h) => `[${h.role}]\n${h.content}`).join("\n\n---\n\n");
      return `Query: "${query}"\nRegion: ${region}\nLanguage: ${language}\n\nAgent Intelligence:\n\n${parts}\n\nSynthesize into final intelligence brief.`;
    },
  },
];

router.post("/intelligence/analyze", async (req, res) => {
  const { query, region, language, context, session_id } = req.body ?? {};

  if (!query || typeof query !== "string" || query.trim().length === 0 || query.length > 3000) {
    res.status(400).json({ error: "Invalid request: query is required (max 3000 chars)" });
    return;
  }
  if (!region || typeof region !== "string") {
    res.status(400).json({ error: "Invalid request: region is required" });
    return;
  }
  if (!session_id || typeof session_id !== "string") {
    res.status(400).json({ error: "Invalid request: session_id is required" });
    return;
  }

  void session_id;

  const input: AnalysisInput = {
    query: query.trim(),
    region: region.trim(),
    language: (language as string) || "English",
    context: typeof context === "string" ? context : undefined,
  };

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  const history: AgentTurn[] = [];

  try {
    for (const agent of INTELLIGENCE_AGENTS) {
      send({
        type: "agent_start",
        agent: agent.id,
        role: agent.role,
        framework: agent.framework,
        color: agent.color,
      });

      const userPrompt = agent.buildUserPrompt(input, history);
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
    console.error("Intelligence crew error:", err);
    send({ type: "error", message: "Intelligence pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
