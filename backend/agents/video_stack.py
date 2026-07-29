"""TIER 2 — Video Stack agent definitions.

A face-swap / lip-sync video production crew adapted to Docker/FastAPI/Ollama.
Four agents run sequentially: Render Strategist (DeepFaceLab/FaceSwap workflow)
→ Script Writer (narrative & dialogue) → Technical Director (GFPGAN upscaling,
FFmpeg pipeline) → Video Director (end-to-end production synthesis).

Offline-first and simulated: the face-swap/lip-sync tools are stubs. Every run
is compliance-screened and audit-logged; deepfaking a named real person
requires an explicit consent attestation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CrewAgentDef:
    id: str
    role: str
    framework: str
    color: str
    icon: str
    description: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict, list[dict]], str] | None = None

    def to_meta(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "framework": self.framework,
            "color": self.color,
            "icon": self.icon,
            "description": self.description,
            "tools": self.tools,
        }


def _prior(history: list[dict], agent_id: str) -> str:
    for h in history:
        if h.get("agent") == agent_id:
            return h.get("content", "")
    return ""


_COMPLIANCE_NOTE = (
    " Operate strictly within a lawful, consent-based, defensive-training context. "
    "Assume all activity is audit-logged for legal review. Flag and refuse to detail "
    "any non-consensual, deceptive, or impersonation use; recommend visible synthetic-"
    "media disclosure/watermarking."
)

RENDER_STRATEGIST = CrewAgentDef(
    id="render_strategist",
    role="Render Strategist",
    framework="DeepFaceLab · FaceSwap · Deep-Live-Cam",
    color="#38bdf8",
    icon="🧩",
    description="Face-swap workflow design and batch/real-time render strategy",
    system_prompt=(
        "You are the Render Strategist for the Video Stack. Design a face-swap production "
        "workflow using DeepFaceLab (batch, CLI automation), FaceSwap (TensorFlow, cross-"
        "platform), or Deep-Live-Cam (real-time single-image). Output: 1) TOOL CHOICE + "
        "rationale; 2) DATASET/ALIGNMENT plan (extraction, alignment, masking); 3) TRAINING "
        "vs. pretrained-model strategy + iterations; 4) HARDWARE (GPU/VRAM) + time estimate; "
        "5) QUALITY controls (color match, mask feathering). Note consent & watermarking "
        "requirements explicitly." + _COMPLIANCE_NOTE
    ),
    tools=["face_swap"],
    build_user_prompt=lambda inp, hist: (
        f"Project: \"{inp['topic']}\"\nStyle: {inp['style']}\nDuration: {inp['duration']}\n"
        f"Preferred swap tool: {inp['swap_tool']}\nConsent attested: {inp['consent']}\n\n"
        "Design the face-swap render strategy."
    ),
)

SCRIPT_WRITER = CrewAgentDef(
    id="video_script_writer",
    role="Script Writer",
    framework="Narrative & Dialogue",
    color="#f472b6",
    icon="✍️",
    description="Narrative and dialogue generation for the video piece",
    system_prompt=(
        "You are the Script Writer for the Video Stack. Write the narrative and dialogue for "
        "the video. Output: 1) LOGLINE; 2) SCENE-BY-SCENE OUTLINE; 3) FULL DIALOGUE/VO with "
        "timing cues; 4) TELEPROMPT VERSION for lip-sync. Keep sentences short for clean "
        "lip-sync cadence." + _COMPLIANCE_NOTE
    ),
    tools=[],
    build_user_prompt=lambda inp, hist: (
        f"Project: \"{inp['topic']}\"\nStyle: {inp['style']}\nDuration: {inp['duration']}\n\n"
        f"Render strategy:\n{_prior(hist, 'render_strategist')}\n\n"
        "Write the narrative and dialogue."
    ),
)

TECHNICAL_DIRECTOR = CrewAgentDef(
    id="technical_director",
    role="Technical Director",
    framework="GFPGAN · FFmpeg",
    color="#a78bfa",
    icon="⚙️",
    description="GFPGAN upscaling and the FFmpeg post-production pipeline",
    system_prompt=(
        "You are the Technical Director for the Video Stack, expert in post-production. Design "
        "the restoration + assembly pipeline: GFPGAN face restoration/upscaling, then a "
        "deterministic FFmpeg pipeline (extract, retime, scale, color, mux, encode). Output: "
        "1) UPSCALE PLAN (GFPGAN scale, artifact handling); 2) FFMPEG COMMAND SEQUENCE "
        "(concrete, ordered); 3) LIP-SYNC PASS (Wav2Lip/VideoRetalking) integration; "
        "4) ENCODING SPECS (codec, bitrate, container); 5) QA checks." + _COMPLIANCE_NOTE
    ),
    tools=["gfpgan_upscale", "lip_sync", "ffmpeg_pipeline"],
    build_user_prompt=lambda inp, hist: (
        f"Project: \"{inp['topic']}\"\nDuration: {inp['duration']}\n\n"
        f"Render strategy:\n{_prior(hist, 'render_strategist')}\n\n"
        f"Script:\n{_prior(hist, 'video_script_writer')}\n\n"
        "Design the upscaling and FFmpeg post-production pipeline."
    ),
)

VIDEO_DIRECTOR = CrewAgentDef(
    id="video_director",
    role="Video Director",
    framework="Production Synthesis",
    color="#34d399",
    icon="🎬",
    description="End-to-end production synthesis into an executable plan",
    system_prompt=(
        "You are the Video Director for the Video Stack. Synthesize all crew inputs into a "
        "complete, executable production plan. Output: 1) EXECUTIVE SUMMARY; 2) END-TO-END "
        "PIPELINE (dataset → swap → restore → lip-sync → composite → export); 3) TOOL CHAIN "
        "with versions; 4) SCHEDULE + hardware; 5) DELIVERABLES; 6) COMPLIANCE CHECKLIST "
        "(consent records, synthetic-media disclosure/watermark, audit trail). Be numbered "
        "and operational." + _COMPLIANCE_NOTE
    ),
    tools=[],
    build_user_prompt=lambda inp, hist: (
        f"Production:\nProject: \"{inp['topic']}\"\nStyle: {inp['style']}\n"
        f"Duration: {inp['duration']}\nConsent attested: {inp['consent']}\n\n"
        "Crew outputs:\n\n"
        + "\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist)
        + "\n\nSynthesize into the final production plan."
    ),
)


VIDEO_STACK: list[CrewAgentDef] = [
    RENDER_STRATEGIST,
    SCRIPT_WRITER,
    TECHNICAL_DIRECTOR,
    VIDEO_DIRECTOR,
]


STYLES: list[str] = [
    "Documentary", "News Anchor", "Explainer", "Cinematic", "Training", "Interview",
]

DURATIONS: list[str] = [
    "30 seconds", "60 seconds", "90 seconds", "2 minutes", "3 minutes", "5 minutes",
]

SWAP_TOOLS: list[dict] = [
    {"id": "deepfacelab", "label": "DeepFaceLab", "badge": "Batch", "online": False,
     "note": "Professional face-swap, CLI automation"},
    {"id": "faceswap", "label": "FaceSwap", "badge": "TensorFlow", "online": False,
     "note": "Cross-platform (Win/macOS/Linux)"},
    {"id": "deeplivecam", "label": "Deep-Live-Cam", "badge": "Real-time", "online": False,
     "note": "Real-time single-image swap"},
]

LIPSYNC_TOOLS: list[dict] = [
    {"id": "wav2lip", "label": "Wav2Lip", "badge": "Open", "online": False,
     "note": "Audio-driven lip-sync"},
    {"id": "videoretalking", "label": "VideoRetalking", "badge": "Open", "online": False,
     "note": "Expression-aware retalking"},
]
