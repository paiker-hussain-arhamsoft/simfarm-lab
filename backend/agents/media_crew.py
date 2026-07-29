"""TIER 2 — Media Crew (Duix-Avatar Pipeline) agent definitions.

A digital-human media production crew adapted to the Docker/FastAPI/Ollama
architecture. Four agents run sequentially: Script Writer (Duix-Avatar) →
Voice Architect (Chatterbox/Coqui/Bark) → Video Director (Wan2.1/CogVideoX/
Open-Sora) → Production Lead (pipeline synthesis).

Offline-first: the default tool for each stage is a local/open model; online
providers (ElevenLabs, HeyGen) are optional and clearly labeled.
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


SCRIPT_WRITER = CrewAgentDef(
    id="script_writer",
    role="Script Writer",
    framework="Duix-Avatar",
    color="#f472b6",
    icon="✍️",
    description="Camera-ready script optimized for digital-human (avatar) delivery",
    system_prompt=(
        "You are the Script Writer for the Duix-Avatar Media Pipeline. Write a complete, "
        "camera-ready script optimized for digital-human (avatar) delivery. Output: "
        "1) AVATAR BRIEF (persona, tone, delivery style); 2) FULL SCRIPT with stage "
        "directions in [brackets] ([pause], [emphasize], [warm], [serious]); short "
        "sentences for natural lip-sync; 3) TELEPROMPT VERSION (clean, TTS-ready); "
        "4) TIMING ESTIMATE at ~130 wpm. Write for a 24fps lip-sync engine."
    ),
    tools=["render_avatar"],
    build_user_prompt=lambda inp, hist: (
        f"Topic: \"{inp['topic']}\"\nTone: {inp['tone']}\nLanguage: {inp['language']}\n"
        f"Target duration: {inp['duration']}\nAudience: {inp['audience']}\n\n"
        "Write a complete avatar-ready script."
    ),
)

VOICE_ARCHITECT = CrewAgentDef(
    id="voice_architect",
    role="Voice Architect",
    framework="Chatterbox · Coqui · Bark",
    color="#fb923c",
    icon="🎙️",
    description="AI voice cloning & synthesis (offline-first; ElevenLabs optional)",
    system_prompt=(
        "You are the Voice Architect for the Duix-Avatar Media Pipeline, expert in AI voice "
        "cloning. Offline-first tools: Chatterbox (MIT, zero-shot from 5s, 23 langs), "
        "Coqui XTTS-v2 (cross-lingual, fine-tunable), Bark (expressive, emotional cues). "
        "ElevenLabs is available only as an optional online fallback. Output: "
        "1) TOOL RECOMMENDATION + why; 2) VOICE PROFILE (gender, age, accent, pace, pitch); "
        "3) CLONING STRATEGY (ideal reference audio); 4) LANGUAGE & ACCENT NOTES; "
        "5) EMOTIONAL CUES (Bark markers); 6) ESTIMATED RENDER TIME; 7) FALLBACK OPTIONS. "
        "Prefer the offline tool unless the user explicitly enabled online."
    ),
    tools=["clone_voice"],
    build_user_prompt=lambda inp, hist: (
        f"Topic: \"{inp['topic']}\"\nTone: {inp['tone']}\nLanguage: {inp['language']}\n"
        f"Preferred voice tool: {inp['voice_tool']}\nAudience: {inp['audience']}\n\n"
        f"Script:\n{_prior(hist, 'script_writer')}\n\n"
        "Design the voice cloning and synthesis architecture."
    ),
)

VIDEO_DIRECTOR = CrewAgentDef(
    id="video_director",
    role="Video Director",
    framework="Wan2.1 · CogVideoX · Open-Sora",
    color="#a78bfa",
    icon="🎬",
    description="Open-source AI video generation & shot direction (HeyGen optional)",
    system_prompt=(
        "You are the Video Director for the Duix-Avatar Media Pipeline, expert in open-source "
        "AI video generation. Offline-first tools: Wan2.1 (Apache-2.0, 14B, 720p on RTX 4090), "
        "CogVideoX (runs on RTX 3060+, video-to-video), Open-Sora 2.0 (11B, VBench-competitive). "
        "HeyGen is an optional online fallback. Output: 1) TOOL RECOMMENDATION per scene + "
        "hardware; 2) SHOT LIST (shot type, prompt template, B-roll); 3) AVATAR INTEGRATION "
        "(greenscreen/inpainting/PiP for Duix-Avatar); 4) TECHNICAL SPECS (res, fps, VRAM, "
        "render time); 5) POST-PROCESSING; 6) FALLBACK. Prefer offline unless online is enabled."
    ),
    tools=["generate_video"],
    build_user_prompt=lambda inp, hist: (
        f"Topic: \"{inp['topic']}\"\nTone: {inp['tone']}\nLanguage: {inp['language']}\n"
        f"Preferred video model: {inp['video_tool']}\nDuration: {inp['duration']}\n\n"
        f"Script:\n{_prior(hist, 'script_writer')}\n\n"
        f"Voice plan:\n{_prior(hist, 'voice_architect')}\n\n"
        "Design the full video production and shot list."
    ),
)

PRODUCTION_LEAD = CrewAgentDef(
    id="production_lead",
    role="Production Lead",
    framework="Pipeline Synthesis",
    color="#34d399",
    icon="🎞️",
    description="Synthesizes crew inputs into an executable production plan",
    system_prompt=(
        "You are the Production Lead for the Duix-Avatar Media Pipeline. Synthesize all crew "
        "inputs into a complete, executable production plan. Output: 1) EXECUTIVE SUMMARY; "
        "2) PIPELINE SEQUENCE (Script → Voice Clone → Avatar Render → Video Generation → "
        "Compositing → Export); 3) TOOL CHAIN (exact tools + versions, note offline vs online); "
        "4) PRODUCTION SCHEDULE (time per stage, total); 5) HARDWARE REQUIREMENTS (min/rec GPU); "
        "6) DELIVERABLES (formats, resolutions); 7) QUALITY CHECKLIST; 8) DISTRIBUTION NOTES. "
        "Be numbered and operational."
    ),
    tools=[],
    build_user_prompt=lambda inp, hist: (
        f"Production:\nTopic: \"{inp['topic']}\"\nTone: {inp['tone']}\n"
        f"Language: {inp['language']}\nDuration: {inp['duration']}\nAudience: {inp['audience']}\n\n"
        "Crew outputs:\n\n"
        + "\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist)
        + "\n\nSynthesize into the final production plan."
    ),
)


MEDIA_CREW: list[CrewAgentDef] = [
    SCRIPT_WRITER,
    VOICE_ARCHITECT,
    VIDEO_DIRECTOR,
    PRODUCTION_LEAD,
]

CREW_BY_ID: dict[str, CrewAgentDef] = {a.id: a for a in MEDIA_CREW}


TONES: list[str] = [
    "Professional", "Conversational", "Persuasive", "Authoritative",
    "Warm", "Urgent", "Educational",
]

DURATIONS: list[str] = [
    "30 seconds", "60 seconds", "90 seconds", "2 minutes", "3 minutes", "5 minutes",
]

LANGUAGES: list[dict] = [
    {"code": "en", "label": "English", "native": "English"},
    {"code": "pa", "label": "Punjabi (Shahmukhi)", "native": "پنجابی (شاہ مکھی)"},
    {"code": "skr", "label": "Saraiki", "native": "سرائیکی"},
    {"code": "ur", "label": "Urdu", "native": "اردو"},
    {"code": "ar", "label": "Arabic", "native": "العربية"},
    {"code": "hi", "label": "Hindi", "native": "हिंदी"},
]

VOICE_TOOLS: list[dict] = [
    {"id": "chatterbox", "label": "Chatterbox", "badge": "MIT", "online": False,
     "note": "Zero-shot, 23 langs, 5s reference"},
    {"id": "coqui", "label": "Coqui XTTS-v2", "badge": "Open", "online": False,
     "note": "Cross-lingual, fine-tunable"},
    {"id": "bark", "label": "Bark", "badge": "MIT", "online": False,
     "note": "Expressive TTS, emotional cues"},
    {"id": "elevenlabs", "label": "ElevenLabs", "badge": "Online", "online": True,
     "note": "Cloud voice cloning (requires internet)"},
]

VIDEO_TOOLS: list[dict] = [
    {"id": "wan2", "label": "Wan2.1", "badge": "Apache 2.0", "online": False,
     "note": "Alibaba, 14B params, 720p RTX 4090"},
    {"id": "cogvideo", "label": "CogVideoX", "badge": "Open", "online": False,
     "note": "Tsinghua, runs RTX 3060+"},
    {"id": "opensora", "label": "Open-Sora 2.0", "badge": "Open", "online": False,
     "note": "11B params, VBench competitive"},
    {"id": "heygen", "label": "HeyGen", "badge": "Online", "online": True,
     "note": "Cloud avatar video (requires internet)"},
]

AVATAR_TOOLS: list[dict] = [
    {"id": "duix", "label": "Duix-Avatar", "badge": "Open", "online": False,
     "note": "Photo + script lip-sync"},
    {"id": "wav2lip", "label": "Wav2Lip", "badge": "Open", "online": False,
     "note": "Audio-driven lip-sync"},
    {"id": "roop", "label": "Roop", "badge": "Open", "online": False,
     "note": "Single-image face mapping"},
]
