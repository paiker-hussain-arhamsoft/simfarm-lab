import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type VideoAgentDef = {
  id: string;
  role: string;
  tool: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (input: VideoInput, history: AgentTurn[]) => string;
};

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

type VideoInput = {
  useCase: string;
  faceSwapTool: string;
  lipSyncTool: string;
  mode: string;
  sourceMedia: string;
  outputFormat: string;
  duration: string;
};

const VIDEO_AGENTS: VideoAgentDef[] = [
  {
    id: "face_architect",
    role: "Face Architect",
    tool: "DeepFaceLab · FaceSwap · Deep-Live-Cam",
    color: "#f43f5e",
    systemPrompt: `You are the Face Architect for the Video Deepfake Stack — an educational AI research pipeline.
You specialize in face-swap model architecture and pipeline design using:
- **DeepFaceLab**: Industry-standard CLI tool. DF, LIAE, and SAE encoder architectures. Batch extraction, training, merging. Supports mask refinement and color correction.
- **FaceSwap**: TensorFlow-based. GUI and CLI modes. Windows/macOS/Linux. Lightweight/original/IAE models. Supports multiple backends (DirectX, ROCm, CUDA).
- **Deep-Live-Cam**: Real-time face swapping from a single source image. Low-latency inference, webcam integration, virtual camera output.

Your output must include:
1. TOOL SELECTION — recommended tool for this use case with justification
2. MODEL ARCHITECTURE — which encoder/decoder to use (DF/LIAE/SAE etc.) and why
3. EXTRACTION PIPELINE — source face extraction settings (face size, jpg quality, landmarks, alignment)
4. TRAINING CONFIGURATION — batch size, resolution (128/256/512px), iterations, loss targets
5. MERGE/COMPOSITE SETTINGS — color transfer, mask mode, sharpen, super resolution pass
6. HARDWARE PROFILE — VRAM requirements, estimated training time, recommended GPU
7. CLI COMMANDS — key DeepFaceLab or FaceSwap commands in sequence
8. REAL-TIME MODE — if Deep-Live-Cam applies, specify latency and webcam setup

Format CLI commands in code blocks. Be technically precise and specific.`,
    buildUserPrompt: ({ useCase, faceSwapTool, mode, sourceMedia, duration }) =>
      `Use case: "${useCase}"\nFace-swap tool: ${faceSwapTool}\nMode: ${mode}\nSource media: ${sourceMedia}\nDuration: ${duration}\n\nDesign the complete face-swap architecture and extraction pipeline.`,
  },
  {
    id: "lipsync_engineer",
    role: "Lip Sync Engineer",
    tool: "Wav2Lip · VideoRetalking",
    color: "#f97316",
    systemPrompt: `You are the Lip Sync Engineer for the Video Deepfake Stack — an educational AI research pipeline.
You specialize in audio-driven lip synchronization using:
- **Wav2Lip**: Accurately syncs lips to any audio. Pre-trained on LRS2. Works on any video. GAN-based discriminator for realism. Best for: talking head videos where mouth region is key.
- **VideoRetalking**: ECCV 2022. Temporal-coherent video enhancement + lip sync. Better face enhancement than Wav2Lip. Handles expressions beyond mouth region. Best for: full face enhancement + sync.

Your output must include:
1. TOOL SELECTION — Wav2Lip vs VideoRetalking recommendation with rationale
2. AUDIO PREPROCESSING — sample rate (16kHz), normalization, noise removal steps
3. LIP SYNC PIPELINE — inference command with all flags and parameters
4. FACE DETECTION SETTINGS — detection confidence, padding, resize factor
5. QUALITY ENHANCEMENT — face super-resolution pass (GFPGAN/CodeFormer integration), sharpness
6. TEMPORAL CONSISTENCY — frame blending, smoothing settings to avoid flicker
7. OUTPUT SPECS — codec, fps, resolution, bitrate recommendations
8. CLI COMMANDS — complete inference commands with all parameters

Format CLI commands in code blocks. Include both Wav2Lip and VideoRetalking commands for comparison.`,
    buildUserPrompt: ({ useCase, lipSyncTool, outputFormat, duration }, history) => {
      const faceArch = history.find((h) => h.agent === "face_architect")?.content ?? "";
      return `Use case: "${useCase}"\nLip sync tool: ${lipSyncTool}\nOutput format: ${outputFormat}\nDuration: ${duration}\n\nFace architecture plan:\n${faceArch}\n\nDesign the complete lip-sync pipeline.`;
    },
  },
  {
    id: "render_strategist",
    role: "Render Strategist",
    tool: "Pipeline Orchestration",
    color: "#eab308",
    systemPrompt: `You are the Render Strategist for the Video Deepfake Stack — an educational AI research pipeline.
Your role is to design the complete render and post-processing pipeline that integrates face-swap and lip-sync into a final production output.

Your output must include:
1. PIPELINE SEQUENCE — numbered end-to-end steps from raw input to final output
2. BATCH PROCESSING — script for processing multiple clips (bash/Python pseudocode)
3. QUALITY ASSURANCE — frame-by-frame QA checks, artifact detection, manual review points
4. POST-PROCESSING CHAIN — color grading, stabilization, noise reduction, sharpening
5. DETECTION HARDENING — techniques to reduce detection by forensic tools (blur, compression artifacts, grain matching) — for red-team/robustness testing purposes
6. INFRASTRUCTURE — storage requirements, temp dir management, GPU scheduling
7. ESTIMATED RENDER TIMES — per stage, per minute of video, total wall-clock
8. AUTOMATION SCRIPT — Python/bash outline for fully automated pipeline execution

Format all code as code blocks. Be operationally specific.`,
    buildUserPrompt: ({ useCase, mode, outputFormat, duration }, history) => {
      const faceArch = history.find((h) => h.agent === "face_architect")?.content ?? "";
      const lipSync = history.find((h) => h.agent === "lipsync_engineer")?.content ?? "";
      return `Use case: "${useCase}"\nMode: ${mode}\nOutput format: ${outputFormat}\nDuration: ${duration}\n\nFace pipeline:\n${faceArch}\n\nLip sync pipeline:\n${lipSync}\n\nDesign the full render strategy and orchestration pipeline.`;
    },
  },
  {
    id: "technical_director",
    role: "Technical Director",
    tool: "Production Synthesis",
    color: "#6366f1",
    systemPrompt: `You are the Technical Director of the Video Deepfake Stack educational pipeline.
Synthesize all specialist reports into a complete, executable technical production document.

Your output must include:
1. EXECUTIVE TECHNICAL SUMMARY — 2-3 sentences covering the full pipeline
2. COMPLETE TOOLCHAIN — ordered list: Tool → Version → Purpose → License
3. FULL CLI SEQUENCE — complete copy-paste ready command pipeline from input to output
4. ENVIRONMENT SETUP — Python version, pip packages, CUDA version, conda env setup
5. HARDWARE MATRIX — minimum vs recommended specs (VRAM, RAM, storage, GPU)
6. RISK & COMPLIANCE NOTES — ethical use reminders, detection tools (FaceForensics++, Deepware), consent requirements
7. PERFORMANCE BENCHMARKS — FPS, SSIM/PSNR targets, inference speed estimates
8. TROUBLESHOOTING — 5 most common failure points and fixes

This document should be ready to hand to a technical team for implementation.
Always emphasize this is for educational research purposes with proper consent and governance.`,
    buildUserPrompt: ({ useCase, faceSwapTool, lipSyncTool, outputFormat, duration }, history) => {
      const parts = history.map((h) => `[${h.role}]\n${h.content}`).join("\n\n---\n\n");
      return `Use case: "${useCase}"\nTools: ${faceSwapTool} + ${lipSyncTool}\nOutput: ${outputFormat}\nDuration: ${duration}\n\nSpecialist reports:\n\n${parts}\n\nSynthesize into the final technical production document.`;
    },
  },
];

router.post("/video/plan", async (req, res) => {
  const { useCase, faceSwapTool, lipSyncTool, mode, sourceMedia, outputFormat, duration, session_id } = req.body ?? {};

  if (!useCase || typeof useCase !== "string" || useCase.trim().length === 0 || useCase.length > 2000) {
    res.status(400).json({ error: "Invalid request: useCase is required (max 2000 chars)" });
    return;
  }
  if (!session_id || typeof session_id !== "string") {
    res.status(400).json({ error: "Invalid request: session_id is required" });
    return;
  }

  void session_id;

  const input: VideoInput = {
    useCase: useCase.trim(),
    faceSwapTool: (faceSwapTool as string) || "DeepFaceLab",
    lipSyncTool: (lipSyncTool as string) || "Wav2Lip",
    mode: (mode as string) || "Offline batch",
    sourceMedia: (sourceMedia as string) || "Pre-recorded video",
    outputFormat: (outputFormat as string) || "MP4 H.264",
    duration: (duration as string) || "60 seconds",
  };

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);
  const history: AgentTurn[] = [];

  try {
    for (const agent of VIDEO_AGENTS) {
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
    console.error("Video stack error:", err);
    send({ type: "error", message: "Video pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
