"""Executable tool registry for the Strategic Brain.

This is the extensibility layer that makes the Strategic Brain *architecturally
capable* of the full topology: analysis, media generation, infrastructure
routing, and persona control. Each tool is a real, callable function wired into
both AutoGen and LangGraph. Implementations are currently **stubs** that return
``{"simulated": True, ...}`` — they will be replaced with real integrations
tier-by-tier (LlamaIndex, Wan2.1, Chatterbox, Scrapoxy, ElizaOS, Playwright).

The important part is the *contract*: agents can discover, call, and get
structured results from tools today, and the self-refining loop can react to
tool failures. Swapping a stub for a real implementation requires no change to
the orchestrators.
"""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


class ToolError(Exception):
    """Raised by a tool when it cannot complete (drives the self-refining loop)."""


@dataclass
class ToolSpec:
    id: str
    name: str
    description: str
    category: str  # analysis | media | infrastructure | persona | stealth | orchestration
    provider: str  # real integration this stub stands in for
    run: Callable[..., Awaitable[dict]]
    parameters: dict[str, str] = field(default_factory=dict)
    status: str = "stub"  # stub | live
    requires_internet: bool = False  # offline-first: online tools opt in explicitly

    def to_meta(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "provider": self.provider,
            "parameters": self.parameters,
            "status": self.status,
            "requires_internet": self.requires_internet,
        }


_REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    _REGISTRY[spec.id] = spec


def get_tool(tool_id: str) -> ToolSpec | None:
    return _REGISTRY.get(tool_id)


def all_tools() -> list[ToolSpec]:
    return list(_REGISTRY.values())


def tools_by_category(category: str) -> list[ToolSpec]:
    return [t for t in _REGISTRY.values() if t.category == category]


async def call_tool(tool_id: str, **kwargs: Any) -> dict:
    """Invoke a registered tool by id. Raises ToolError if not found."""
    spec = _REGISTRY.get(tool_id)
    if spec is None:
        raise ToolError(f"Unknown tool: {tool_id}")
    return await spec.run(**kwargs)


# ── Stub implementations ────────────────────────────────────────────
# Each returns a structured, clearly-simulated result. Real integrations
# swap these out per-tier without touching orchestrators.


async def _index_dataset(source: str = "crm", query: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "LlamaIndex",
        "source": source,
        "records_indexed": 12483,
        "top_matches": [f"record::{source}::{i}" for i in range(3)],
        "note": "Stub — wire to LlamaIndex/vector store in the intelligence tier.",
    }


async def _narrative_saturation_score(target: str = "", region: str = "PK", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "sentiment-engine",
        "target": target,
        "region": region,
        "saturation_score": 0.62,
        "sentiment": {"positive": 0.31, "neutral": 0.44, "negative": 0.25},
        "note": "Stub — replace with real sentiment/narrative analysis.",
    }


async def _generate_media_package(kind: str = "video", script: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Wan2.1 + Chatterbox",
        "kind": kind,
        "artifacts": ["/artifacts/media/clip_stub.mp4", "/artifacts/media/voice_stub.wav"],
        "note": "Stub — wire to media-generation tier (defensive/training use only).",
    }


async def _rotate_proxy(pool: str = "residential", reason: str = "", **_: Any) -> dict:
    # Demonstrates a tool that can 'fail' to exercise the self-refining loop.
    if pool == "blocked":
        raise ToolError("Proxy pool 'blocked' is exhausted; caller should alter the pool.")
    return {
        "simulated": True,
        "provider": "Scrapoxy",
        "pool": pool,
        "new_vector": "10.x.x.x (simulated)",
        "reason": reason,
        "note": "Stub — infrastructure routing hook; simulated only.",
    }


async def _adjust_load_balancer(strategy: str = "round_robin", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "infra-control",
        "strategy": strategy,
        "note": "Stub — cloud load-balancer control hook; simulated only.",
    }


async def _update_persona(persona_id: str = "default", traits: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "ElizaOS",
        "persona_id": persona_id,
        "applied_traits": traits,
        "note": "Stub — persona/character profile control hook.",
    }


async def _behavior_forecast(region: str = "", segments: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "LightGBM",
        "region": region,
        "model": "gradient_boosted_trees",
        "feature_importance": [
            {"feature": "economic_grievance", "weight": 0.28},
            {"feature": "incumbent_fatigue", "weight": 0.21},
            {"feature": "biradari_affiliation", "weight": 0.17},
            {"feature": "youth_turnout", "weight": 0.14},
            {"feature": "development_spend", "weight": 0.11},
        ],
        "segments": {"committed": 0.34, "persuadable": 0.29, "disengaged": 0.22, "swing": 0.15},
        "projected_turnout": 0.52,
        "note": "Stub — wire to a trained LightGBM model in the intelligence tier.",
    }


async def _dialect_analysis(region: str = "", language: str = "en", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Meta-Llama-3.1-8B",
        "region": region,
        "language": language,
        "dialects": ["Punjabi (Shahmukhi)", "Saraiki"],
        "samples": {"pa": "پنجابی ثقافتی اشارے", "skr": "سرائیکی برادری دے مسئلے"},
        "note": "Stub — wire to Meta-Llama-3.1-8B (native Punjabi/Saraiki) for real dialect analysis.",
    }


async def _social_targeting(platform: str = "facebook", region: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "social-intel",
        "platform": platform,
        "region": region,
        "reach_estimate": 184000,
        "sentiment": {"positive": 0.29, "neutral": 0.41, "negative": 0.30},
        "top_channels": ["Facebook groups", "WhatsApp broadcast", "TikTok"],
        "note": "Stub — wire to real platform-targeting / sentiment analysis.",
    }


async def _playwright_stealth_check(endpoint: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Playwright",
        "endpoint": endpoint,
        "stealth_grade": "B",
        "flags": ["webdriver_present"],
        "note": "Stub — automated-session posture check; simulated only.",
    }


# ── Media Crew stubs (offline-first; online providers opt in) ───────

_VOICE_PROVIDERS = {
    "chatterbox": {"provider": "Chatterbox", "license": "MIT", "online": False, "langs": 23},
    "coqui": {"provider": "Coqui XTTS-v2", "license": "MPL-2.0", "online": False, "langs": 17},
    "bark": {"provider": "Bark", "license": "MIT", "online": False, "langs": 13},
    "elevenlabs": {"provider": "ElevenLabs", "license": "commercial", "online": True, "langs": 29},
}

_VIDEO_PROVIDERS = {
    "wan2": {"provider": "Wan2.1", "license": "Apache-2.0", "online": False, "params": "14B"},
    "cogvideo": {"provider": "CogVideoX", "license": "open", "online": False, "params": "5B"},
    "opensora": {"provider": "Open-Sora 2.0", "license": "open", "online": False, "params": "11B"},
    "heygen": {"provider": "HeyGen", "license": "commercial", "online": True, "params": "cloud"},
}

_AVATAR_PROVIDERS = {
    "duix": {"provider": "Duix-Avatar", "license": "open", "online": False},
    "wav2lip": {"provider": "Wav2Lip", "license": "open", "online": False},
    "roop": {"provider": "Roop", "license": "open", "online": False},
}


async def _clone_voice(tool: str = "chatterbox", language: str = "en",
                       script: str = "", **_: Any) -> dict:
    p = _VOICE_PROVIDERS.get(tool, _VOICE_PROVIDERS["chatterbox"])
    if p["online"] and not _online_available():
        raise ToolError(f"{p['provider']} requires internet; fall back to an offline voice tool.")
    return {
        "simulated": True,
        "provider": p["provider"],
        "license": p["license"],
        "requires_internet": p["online"],
        "language": language,
        "reference_audio_sec": 5,
        "artifact": "/artifacts/media/voice_stub.wav",
        "note": f"Stub — wire to {p['provider']} for real voice cloning ({'online' if p['online'] else 'offline/local'}).",
    }


async def _generate_video(tool: str = "wan2", script: str = "", duration: str = "60s",
                          **_: Any) -> dict:
    p = _VIDEO_PROVIDERS.get(tool, _VIDEO_PROVIDERS["wan2"])
    if p["online"] and not _online_available():
        raise ToolError(f"{p['provider']} requires internet; fall back to an offline video model.")
    return {
        "simulated": True,
        "provider": p["provider"],
        "license": p["license"],
        "requires_internet": p["online"],
        "params": p["params"],
        "resolution": "720p",
        "duration": duration,
        "artifact": "/artifacts/media/clip_stub.mp4",
        "note": f"Stub — wire to {p['provider']} for real text-to-video ({'online' if p['online'] else 'offline/local'}).",
    }


async def _render_avatar(tool: str = "duix", photo: str = "", script: str = "",
                         **_: Any) -> dict:
    p = _AVATAR_PROVIDERS.get(tool, _AVATAR_PROVIDERS["duix"])
    return {
        "simulated": True,
        "provider": p["provider"],
        "license": p["license"],
        "requires_internet": p["online"],
        "lip_sync_fps": 24,
        "artifact": "/artifacts/media/avatar_stub.mp4",
        "note": f"Stub — wire to {p['provider']} for photo+script lip-sync (offline/local).",
    }


def _online_available() -> bool:
    """Online tools are only usable when explicitly enabled (offline-first default)."""
    return os.environ.get("ALLOW_ONLINE_TOOLS", "").lower() in ("1", "true", "yes")


def _register_defaults() -> None:
    if _REGISTRY:
        return
    register(ToolSpec(
        id="index_dataset", name="Dataset Indexer",
        description="Index and query dataset records (CRM, CDR, profiles).",
        category="analysis", provider="LlamaIndex", run=_index_dataset,
        parameters={"source": "dataset name", "query": "search query"},
    ))
    register(ToolSpec(
        id="narrative_saturation_score", name="Narrative Saturation Scorer",
        description="Compute sentiment / narrative saturation across target profiles.",
        category="analysis", provider="sentiment-engine", run=_narrative_saturation_score,
        parameters={"target": "target id", "region": "region code"},
    ))
    register(ToolSpec(
        id="generate_media_package", name="Media Package Generator",
        description="Generate localized multimedia packages (video/voice).",
        category="media", provider="Wan2.1 + Chatterbox", run=_generate_media_package,
        parameters={"kind": "video|audio|image", "script": "content script"},
    ))
    register(ToolSpec(
        id="rotate_proxy", name="Proxy Rotator",
        description="Rotate routing/proxy vectors when an endpoint is blocked.",
        category="infrastructure", provider="Scrapoxy", run=_rotate_proxy,
        parameters={"pool": "proxy pool", "reason": "why rotating"},
    ))
    register(ToolSpec(
        id="adjust_load_balancer", name="Load Balancer Controller",
        description="Adjust cloud load-balancer strategy under failure/load.",
        category="infrastructure", provider="infra-control", run=_adjust_load_balancer,
        parameters={"strategy": "balancing strategy"},
    ))
    register(ToolSpec(
        id="update_persona", name="Persona Controller",
        description="Adjust agent/character persona logic.",
        category="persona", provider="ElizaOS", run=_update_persona,
        parameters={"persona_id": "persona id", "traits": "trait adjustments"},
    ))
    register(ToolSpec(
        id="behavior_forecast", name="Voter Behavior Forecaster",
        description="Predict voter segments/turnout with a gradient-boosted model.",
        category="analysis", provider="LightGBM", run=_behavior_forecast,
        parameters={"region": "target region", "segments": "segments to score"},
    ))
    register(ToolSpec(
        id="dialect_analysis", name="Dialect & Culture Analyzer",
        description="Analyze Punjabi (Shahmukhi) / Saraiki cultural & linguistic signals.",
        category="analysis", provider="Meta-Llama-3.1-8B", run=_dialect_analysis,
        parameters={"region": "target region", "language": "language code"},
    ))
    register(ToolSpec(
        id="social_targeting", name="Social Platform Targeter",
        description="Estimate reach/sentiment and platform targeting for a region.",
        category="media", provider="social-intel", run=_social_targeting,
        parameters={"platform": "platform", "region": "target region"},
    ))
    register(ToolSpec(
        id="clone_voice", name="Voice Cloner",
        description="Zero-shot voice cloning / TTS (Chatterbox, Coqui, Bark offline; ElevenLabs online).",
        category="media", provider="Chatterbox / Coqui / Bark", run=_clone_voice,
        parameters={"tool": "chatterbox|coqui|bark|elevenlabs", "language": "lang", "script": "text"},
    ))
    register(ToolSpec(
        id="generate_video", name="Video Generator",
        description="Text-to-video generation (Wan2.1, CogVideoX, Open-Sora offline; HeyGen online).",
        category="media", provider="Wan2.1 / CogVideoX / Open-Sora", run=_generate_video,
        parameters={"tool": "wan2|cogvideo|opensora|heygen", "script": "text", "duration": "e.g. 60s"},
    ))
    register(ToolSpec(
        id="render_avatar", name="Digital Human Renderer",
        description="Photo+script lip-synced digital human (Duix-Avatar, Wav2Lip, Roop).",
        category="media", provider="Duix-Avatar / Wav2Lip / Roop", run=_render_avatar,
        parameters={"tool": "duix|wav2lip|roop", "photo": "ref photo", "script": "text"},
    ))
    register(ToolSpec(
        id="playwright_stealth_check", name="Automation Posture Check",
        description="Check automated-session detection posture for an endpoint.",
        category="stealth", provider="Playwright", run=_playwright_stealth_check,
        parameters={"endpoint": "target endpoint"},
    ))


_register_defaults()
