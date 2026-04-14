import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type MediaAgentDef = {
  id: string;
  role: string;
  tool: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (input: MediaInput, history: AgentTurn[]) => string;
};

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

type MediaInput = {
  topic: string;
  tone: string;
  language: string;
  voiceTool: string;
  videoTool: string;
  duration: string;
  targetAudience: string;
};

const MEDIA_AGENTS: MediaAgentDef[] = [
  {
    id: "script_writer",
    role: "Script Writer",
    tool: "Duix-Avatar",
    color: "#f472b6",
    systemPrompt: `You are the Script Writer for the Duix-Avatar Media Pipeline — an advanced AI media production system.
Your role is to write a complete, camera-ready script optimized for digital human (avatar) delivery.

Your output must include:
1. AVATAR BRIEF — one paragraph describing the avatar persona (appearance, tone, delivery style)
2. FULL SCRIPT — the complete spoken script, formatted with stage directions in [brackets]
   - Include natural pauses: [pause], emphasis: [emphasize], and emotion cues: [warm], [serious], [energetic]
   - Keep sentences short for natural lip-sync cadence
   - Mark phonetically tricky words
3. TELEPROMPT VERSION — clean script without stage directions, ready for TTS
4. TIMING ESTIMATE — estimated duration based on 130 words/minute average

Write for Duix-Avatar's lip-sync engine — short, punchy sentences that sync well at 24fps.
Be compelling, natural, and adapted to the specified tone and audience.`,
    buildUserPrompt: ({ topic, tone, language, duration, targetAudience }) =>
      `Topic: "${topic}"\nTone: ${tone}\nLanguage: ${language}\nTarget duration: ${duration}\nAudience: ${targetAudience}\n\nWrite a complete avatar-ready script.`,
  },
  {
    id: "voice_architect",
    role: "Voice Architect",
    tool: "Chatterbox · Coqui · Bark",
    color: "#fb923c",
    systemPrompt: `You are the Voice Architect for the Duix-Avatar Media Pipeline, specializing in AI voice cloning and synthesis.

You have deep expertise in:
- **Chatterbox** (Resemble AI, MIT license): Zero-shot voice cloning from 5 seconds of audio. 23 languages. Outperforms ElevenLabs in blind tests (63.8% preference). Best for: natural conversational voices.
- **Coqui XTTS-v2**: Cross-lingual voice cloning, strong multilingual support, fine-tunable on regional accents. Best for: regional language delivery.
- **Bark** (Suno AI): Expressive TTS with emotional cues, laughter, breathing effects. Best for: emotionally rich delivery.

Your output must include:
1. TOOL RECOMMENDATION — which voice tool to use and why, given the script and audience
2. VOICE PROFILE — detailed voice characteristics (gender, age range, accent, pace, pitch)
3. CLONING STRATEGY — if zero-shot (Chatterbox): describe the ideal reference audio, duration, characteristics
4. LANGUAGE & ACCENT NOTES — specific regional pronunciation guidance
5. EMOTIONAL CUES — Bark-compatible emotion markers mapped to script sections: [laughter], [clears throat], [sighs]
6. ESTIMATED RENDER TIME — based on script length and chosen tool
7. FALLBACK OPTIONS — alternative tool if primary fails

Be technically precise. Reference actual tool capabilities and limitations.`,
    buildUserPrompt: ({ topic, tone, language, voiceTool, targetAudience }, history) => {
      const script = history.find((h) => h.agent === "script_writer")?.content ?? "";
      return `Topic: "${topic}"\nTone: ${tone}\nLanguage: ${language}\nPreferred voice tool: ${voiceTool}\nAudience: ${targetAudience}\n\nScript:\n${script}\n\nDesign the voice cloning and synthesis architecture.`;
    },
  },
  {
    id: "video_director",
    role: "Video Director",
    tool: "Wan2.1 · CogVideoX · Open-Sora",
    color: "#a78bfa",
    systemPrompt: `You are the Video Director for the Duix-Avatar Media Pipeline, an expert in open-source AI video generation.

You have deep expertise in:
- **Wan2.1** (Alibaba, Apache 2.0): 1.3B and 14B parameter text-to-video. 720p generation. Best performance on RTX 4090. Excellent temporal consistency.
- **CogVideoX** (Tsinghua University): Text/image/video-to-video. Runs on RTX 3060+. Good for image-driven scenes and video-to-video style transfer.
- **Open-Sora 2.0**: 11B parameter model. $200K training cost. VBench competitive with commercial models. Strong scene variety.

Your output must include:
1. TOOL RECOMMENDATION — which video model to use per scene, with hardware requirements
2. SHOT LIST — scene-by-scene breakdown with:
   - Shot type (close-up, medium, wide)
   - Prompt engineering template for the chosen model
   - B-roll recommendations for cutaway coverage
3. AVATAR INTEGRATION — how to composite Duix-Avatar into generated video (greenscreen/inpainting/PiP)
4. TECHNICAL SPECS — resolution, frame rate, estimated VRAM usage, render time
5. POST-PROCESSING — lip-sync pass timing, color grading notes
6. FALLBACK — alternative model if primary hardware is unavailable

Format prompts as JSON-ready text-to-video prompt strings.`,
    buildUserPrompt: ({ topic, tone, language, videoTool, duration }, history) => {
      const script = history.find((h) => h.agent === "script_writer")?.content ?? "";
      const voice = history.find((h) => h.agent === "voice_architect")?.content ?? "";
      return `Topic: "${topic}"\nTone: ${tone}\nLanguage: ${language}\nPreferred video model: ${videoTool}\nDuration: ${duration}\n\nScript:\n${script}\n\nVoice plan:\n${voice}\n\nDesign the full video production and shot list.`;
    },
  },
  {
    id: "production_lead",
    role: "Production Lead",
    tool: "Pipeline Synthesis",
    color: "#34d399",
    systemPrompt: `You are the Production Lead for the Duix-Avatar Media Pipeline.
Your role is to synthesize all crew inputs into a complete, executable production plan.

Your output must include:
1. EXECUTIVE SUMMARY — one paragraph overview of the production
2. PIPELINE SEQUENCE — numbered steps from raw input to final render:
   Script → Voice Clone → Avatar Render → Video Generation → Compositing → Export
3. TOOL CHAIN — exact tools in order with version recommendations
4. PRODUCTION SCHEDULE — estimated time per stage, total wall-clock time
5. HARDWARE REQUIREMENTS — minimum and recommended GPU/CPU/RAM
6. DELIVERABLES — final output formats (MP4, WebM, etc.), resolutions, file sizes
7. QUALITY CHECKLIST — pre-launch verification steps
8. DISTRIBUTION NOTES — platform-specific formatting (YouTube, WhatsApp, Instagram Reels)

Be specific, numbered, and operational. This is a production brief ready to hand to an engineering team.`,
    buildUserPrompt: ({ topic, tone, language, duration, targetAudience }, history) => {
      const parts = history.map((h) => `[${h.role}]\n${h.content}`).join("\n\n---\n\n");
      return `Production:\nTopic: "${topic}"\nTone: ${tone}\nLanguage: ${language}\nDuration: ${duration}\nAudience: ${targetAudience}\n\nCrew outputs:\n\n${parts}\n\nSynthesize into the final production plan.`;
    },
  },
];

router.post("/media/produce", async (req, res) => {
  const { topic, tone, language, voiceTool, videoTool, duration, targetAudience, session_id } = req.body ?? {};

  if (!topic || typeof topic !== "string" || topic.trim().length === 0 || topic.length > 2000) {
    res.status(400).json({ error: "Invalid request: topic is required (max 2000 chars)" });
    return;
  }
  if (!session_id || typeof session_id !== "string") {
    res.status(400).json({ error: "Invalid request: session_id is required" });
    return;
  }

  void session_id;

  const input: MediaInput = {
    topic: topic.trim(),
    tone: (tone as string) || "Professional",
    language: (language as string) || "English",
    voiceTool: (voiceTool as string) || "Chatterbox",
    videoTool: (videoTool as string) || "Wan2.1",
    duration: (duration as string) || "60 seconds",
    targetAudience: (targetAudience as string) || "General public",
  };

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);

  const history: AgentTurn[] = [];

  try {
    for (const agent of MEDIA_AGENTS) {
      send({ type: "agent_start", agent: agent.id, role: agent.role, tool: agent.tool, color: agent.color });

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
    console.error("Media crew error:", err);
    send({ type: "error", message: "Media pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
