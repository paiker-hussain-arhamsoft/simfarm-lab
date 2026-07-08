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

    def to_meta(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "provider": self.provider,
            "parameters": self.parameters,
            "status": self.status,
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


async def _playwright_stealth_check(endpoint: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Playwright",
        "endpoint": endpoint,
        "stealth_grade": "B",
        "flags": ["webdriver_present"],
        "note": "Stub — automated-session posture check; simulated only.",
    }


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
        id="playwright_stealth_check", name="Automation Posture Check",
        description="Check automated-session detection posture for an endpoint.",
        category="stealth", provider="Playwright", run=_playwright_stealth_check,
        parameters={"endpoint": "target endpoint"},
    ))


_register_defaults()
