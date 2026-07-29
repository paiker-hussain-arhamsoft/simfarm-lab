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

import asyncio
import os
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any
from backend import safety
from backend.tools import simfarm_sim


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
    result = await spec.run(**kwargs)
    return safety.enforce_result(tool_id, result)


# ── Stub implementations ────────────────────────────────────────────
# Each returns a structured, clearly-simulated result. Real integrations
# swap these out per-tier without touching orchestrators.


async def _index_dataset(source: str = "crm", query: str = "", **kwargs: Any) -> dict:
    """Index and retrieve synthetic records using a real LlamaIndex vector store.

    Uses a local Ollama embedding model, so it works offline once the Ollama
    model is present. Falls back to a deterministic stub if LlamaIndex is not
    installed or Ollama is unreachable.
    """
    try:
        import asyncio
        from llama_index.core import Document, VectorStoreIndex
        from llama_index.embeddings.ollama import OllamaEmbedding
        from backend.pipeline.llm_config import get_ollama_host, get_ollama_model
    except Exception as exc:
        return {
            "simulated": True,
            "requires_internet": False,
            "provider": "LlamaIndex",
            "source": source,
            "records_indexed": 12483,
            "top_matches": [f"record::{source}::{i}" for i in range(3)],
            "note": f"LlamaIndex fallback — {type(exc).__name__}: {exc}",
        }

    host = get_ollama_host()
    model = get_ollama_model()
    limit = max(1, int(kwargs.get("limit", 3)))
    window = max(limit * 3, 10)

    # Build a small synthetic document set for the requested source
    docs = []
    for i in range(window):
        text = (
            f"{source.upper()} record {i}. "
            f"Synthetic record from the {source} dataset. "
            f"Relevant to query: {query or 'general indexing'}."
        )
        docs.append(Document(text=text, metadata={"source": source, "record_id": i}))

    def _build() -> VectorStoreIndex:
        # Ollama embedding works offline; run the sync LlamaIndex call in a thread
        embed_model = OllamaEmbedding(
            model_name=model,
            base_url=host,
            embed_batch_size=10,
            request_timeout=120.0,
        )
        return VectorStoreIndex.from_documents(docs, embed_model=embed_model)

    try:
        index = await asyncio.to_thread(_build)
        retriever = index.as_retriever(similarity_top_k=limit)
        if query:
            nodes = await asyncio.to_thread(retriever.retrieve, query)
        else:
            # No query: return the first few indexed documents
            stored = list(index.docstore.docs.values())
            nodes = stored[:limit]
            if limit > len(nodes):
                nodes = nodes + stored[: limit - len(nodes)]

        top_matches = [
            f"record::{source}::{n.metadata.get('record_id', n.id_)}"
            for n in nodes
        ]
        return {
            "simulated": True,
            "requires_internet": False,
            "provider": "LlamaIndex",
            "engine": "VectorStoreIndex",
            "embedding_model": model,
            "embedding_base": host,
            "source": source,
            "query": query,
            "records_indexed": len(docs),
            "top_matches": top_matches,
            "note": "Indexed with LlamaIndex using a local Ollama embedding model.",
        }
    except Exception as exc:
        return {
            "simulated": True,
            "requires_internet": False,
            "provider": "LlamaIndex",
            "source": source,
            "records_indexed": 0,
            "top_matches": [],
            "note": f"LlamaIndex integration error ({type(exc).__name__}); no matches returned.",
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
        "requires_internet": False,
        "provider": "Scrapoxy",
        "pool": pool,
        "new_vector": "10.x.x.x (simulated)",
        "reason": reason,
        "note": "Stub — infrastructure routing hook; simulated only.",
    }

# ── TIER 4 · IVR and proxy-rotation local simulation tools ─────────
_TELECOM_NOTE = ("Simulated only; real telecom execution requires specific "
                 "communications-secretariat orders and is not performed.")
_PROXY_NOTE = ("Simulated only; real proxy/cloud execution requires specific "
               "communications-secretariat orders and is not performed.")

async def _ivr_hardware_setup(hardware_kit="", scenario="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "Raspberry Pi · GSM · RASP-IVR",
            "hardware_kit": hardware_kit, "topology": {"controller": "virtual-rpi", "gsm_channels": "modeled", "physical": False},
            "detection_telemetry": ["channel occupancy", "retry bursts", "clock skew"], "note": _TELECOM_NOTE}
async def _call_flow_design(scenario="", objective="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "Verboice",
            "menu_tree": {"root": "welcome (modeled)", "branches": ["information", "help", "end"], "dtmf": "modeled"},
            "scenario": scenario, "objective": objective, "real_calls": False, "note": _TELECOM_NOTE}
async def _dtmf_handler(scenario="", objective="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "VBVoice",
            "dtmf_policy": {"digits": "synthetic fixtures only", "timeouts": "modeled", "secrets": False},
            "detection_signals": ["repeated invalid digits", "automation timing"], "note": _TELECOM_NOTE}
async def _rural_reach_model(reach_model="", scenario="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "rural-reach (modeled)",
            "reach_model": reach_model, "coverage": "modeled regional envelope", "latency_ms": 420,
            "accessibility": "feature-phone compatible (concept)", "real_network": False, "note": _TELECOM_NOTE}
async def _call_route_plan(scenario="", objective="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "call-routing (modeled)",
            "routes": ["lab-entry", "sim-help", "sim-exit"], "queue": "modeled", "real_routing": False, "note": _TELECOM_NOTE}
async def _ivr_cost_model(scenario="", objective="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "cost-model (modeled)",
            "per_call_cost": "modeled currency units", "components": ["duration", "queue", "translation"],
            "real_billing": False, "note": _TELECOM_NOTE}
async def _scrapoxy_deploy(provider="", scenario="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "Scrapoxy · Docker",
            "deployment": {"containers": 0, "network": "lab-model", "executed": False}, "provider_model": provider, "note": _PROXY_NOTE}
async def _cloud_connector(provider="", scenario="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "cloud-connectors (modeled)",
            "cloud": provider, "credentials_used": False, "deployment": "concept only", "note": _PROXY_NOTE}
async def _proxy_pool_size(pool_type="", objective="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "pool-sizing (modeled)",
            "pool_type": pool_type, "recommended_size": 24, "sizing_basis": "modeled traffic envelope", "note": _PROXY_NOTE}
async def _proxy_health_monitor(pool_type="", scenario="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "health-monitor (modeled)",
            "pool_type": pool_type, "signals": ["latency", "error ratio", "reputation fixture"], "probes_executed": False, "note": _PROXY_NOTE}
async def _proxy_integration_plan(provider="", objective="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "Playwright · Puppeteer · requests",
            "integration": "telemetry-only concept", "evasion": False, "live_requests": False, "provider_model": provider, "note": _PROXY_NOTE}
async def _proxy_cost_model(provider="", pool_type="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "cost-model (modeled)",
            "provider_model": provider, "pool_type": pool_type, "cost": "modeled units per hour", "real_billing": False, "note": _PROXY_NOTE}
async def _proxy_deployment_synth(provider="", scenario="", **_):
    return {"simulated": True, "requires_internet": False, "provider": "deployment (modeled)",
            "deployment_plan": ["validate telemetry", "stage lab fixtures", "review detections"], "executed": False, "provider_model": provider, "note": _PROXY_NOTE}

_STEALTH_NOTE = "Simulated only; real browser/WAF execution requires authorization and is not performed."
_CONTENT_NOTE = "Simulated only; real email, CMS, social, or content execution requires authorization and is not performed."
_MEMORY_NOTE = ("Simulated only; synthetic fixtures are used and no real PII or voter "
                "records are stored. Real memory/data-lake execution requires authorization "
                "and is not performed.")
async def _stealth_stub(provider, payload, **_):
    return {"simulated": safety.SIMULATED, "requires_internet": safety.REQUIRES_INTERNET, "provider": provider, "modeled": payload, "note": _STEALTH_NOTE}
async def _content_stub(provider, payload, **_):
    return {"simulated": safety.SIMULATED, "requires_internet": safety.REQUIRES_INTERNET, "provider": provider, "modeled": payload, "note": _CONTENT_NOTE}
async def _stealth_patch_model(**kw): return await _stealth_stub("playwright-extra", {"patches":["navigator","WebGL","canvas","audio","WebRTC","timezone","language","plugins","chrome-app","iframe","permissions"],"signals":["automation flags","fingerprint inconsistency"]}, **kw)
async def _canvas_spoof_model(**kw): return await _stealth_stub("canvas-spoof (modeled)", {"noise":"bounded fixture","consistency_checks":["render hash","font metrics"]}, **kw)
async def _webrtc_spoof_model(**kw): return await _stealth_stub("WebRTC-spoof (modeled)", {"leak_prevention":"fixture only","signals":["candidate exposure","ASN mismatch"]}, **kw)
async def _human_behavior_model(**kw): return await _stealth_stub("behavior-sim (modeled)", {"timing":{"typing":"lognormal","scroll":"bursty","mouse":"bounded-jitter"}}, **kw)
async def _flaresolverr_model(**kw): return await _stealth_stub("FlareSolverr · Docker", {"containers":0,"challenge_telemetry":["JS challenge","managed challenge","session age"]}, **kw)
async def _challenge_bypass_model(**kw): return await _stealth_stub("challenge-solver (modeled)", {"challenge_signals":["IUAM","managed challenge","DDoS-GUARD"]}, **kw)
async def _fingerprint_pool_model(**kw): return await _stealth_stub("Browserbase · Scrapoxy", {"pool_size":24,"diversity_metrics":["engine","viewport","locale"]}, **kw)
async def _session_isolation_model(**kw): return await _stealth_stub("session-isolation (modeled)", {"isolated":["cookie","storage","fingerprint"]}, **kw)
async def _ip_warmup_model(**kw): return await _stealth_stub("IP-warmup (modeled)", {"schedule":["observe","low-volume","normalization"],"signals":["reputation","ASN churn"]}, **kw)
async def _evasion_matrix_model(**kw): return await _stealth_stub("evasion-matrix (modeled)", {"signals":["canvas","WebGL","audio","WebRTC","timezone","language","navigator","plugins","TLS/JA3","IP reputation","behavioral timing","cookie/storage"]}, **kw)
async def _stealth_checklist_model(**kw): return await _stealth_stub("stealth-checklist (modeled)", {"checks":["consistency","challenge telemetry","rate limits","audit evidence"]}, **kw)
async def _mautic_campaign_model(**kw): return await _content_stub("Mautic · Docker", {"flow":["segment","trigger","message fixture","stop condition"],"deployed":False}, **kw)
async def _lead_scoring_model(**kw): return await _content_stub("Mautic · lead-scoring", {"weights":{"behavioral":0.6,"demographic":0.4},"live_subscribers":False}, **kw)
async def _email_auth_model(**kw): return await _content_stub("DKIM/SPF/DMARC (modeled)", {"records":["DKIM","SPF","DMARC"],"verified":False}, **kw)
async def _strapi_lifecycle_model(**kw): return await _content_stub("Strapi · AI", {"schema":"modeled content type","hooks":["draft","review","publish"],"deployed":False}, **kw)
async def _webhook_chain_model(**kw): return await _content_stub("webhook (modeled)", {"topology":["source fixture","review queue","satellite fixture"],"live":False}, **kw)
async def _postiz_scheduler_model(**kw): return await _content_stub("Postiz", {"schedule":"modeled matrix","captions":"fixture stubs","queued":False}, **kw)
async def _cross_platform_model(**kw): return await _content_stub("cross-platform (modeled)", {"repurposing":["long→short","blog→social","video→carousel"]}, **kw)
async def _content_calendar_model(**kw): return await _content_stub("calendar (modeled)", {"weeks":4,"channels":["email","social","blog","webhook"]}, **kw)
async def _content_cost_model(**kw): return await _content_stub("cost-model (modeled)", {"monthly":{"hosting":"modeled","email":"modeled","social":"modeled","cdn":"modeled"}}, **kw)
async def _memory_stub(provider, payload, **_):
    return {"simulated": safety.SIMULATED, "requires_internet": safety.REQUIRES_INTERNET, "provider": provider,
            "modeled": payload, "note": _MEMORY_NOTE}
async def _mem0_fact_extraction_model(**kw): return await _memory_stub("Mem0", {"stages":["synthetic input","fact extraction","deduplication","confidence review"],"real_records":False}, **kw)
async def _persona_memory_isolation_model(**kw): return await _memory_stub("persona-isolation (modeled)", {"boundaries":["tenant","persona","session"],"cross_persona_access":False}, **kw)
async def _async_write_pipeline_model(**kw): return await _memory_stub("async-write (modeled)", {"queue":"synthetic event buffer","retries":3,"durability":"modeled"}, **kw)
async def _vector_graph_store_model(**kw): return await _memory_stub("Qdrant · Neo4j · Redis", {"stores":["vector fixture index","graph fixture relations","hot cache"],"live_connections":False}, **kw)
async def _pgvector_schema_model(**kw): return await _memory_stub("PostgreSQL · pgvector", {"tables":["synthetic_memories","synthetic_embeddings"],"indexes":["hnsw (modeled)"],"real_records":False}, **kw)
async def _memory_tiering_model(**kw): return await _memory_stub("memory-tiering (modeled)", {"tiers":["hot","warm","cold"],"promotion":"synthetic access score","retention":"modeled"}, **kw)
async def _event_sourcing_model(**kw): return await _memory_stub("event-sourcing (modeled)", {"events":["memory.created","memory.updated","memory.archived"],"replayable":True}, **kw)
async def _conflict_resolution_model(**kw): return await _memory_stub("conflict-resolution (modeled)", {"strategy":"version + confidence review","human_review_fixture":True}, **kw)
async def _kafka_topic_model(**kw): return await _memory_stub("Kafka (modeled)", {"topics":["synthetic.memory.events","synthetic.audit.events"],"partitions":3,"live_broker":False}, **kw)
async def _cassandra_schema_model(**kw): return await _memory_stub("Cassandra (synthetic)", {"keyspace":"synthetic_memory","tables":["memory_by_persona","events_by_day"],"synthetic_record_count":100000,"real_voter_or_pii_data":False,"capacity_estimate_only":True}, **kw)
async def _pyspark_bulk_load_model(**kw): return await _memory_stub("PySpark (modeled)", {"input":"synthetic fixtures only","records_loaded":50000,"real_data":False,"job_executed":False}, **kw)
async def _trino_analytics_model(**kw): return await _memory_stub("Trino (modeled)", {"catalog":"synthetic_lake","queries":["retention","lineage","access anomalies"],"results":"fixtures"}, **kw)
async def _pii_encryption_model(**kw): return await _memory_stub("envelope-encryption (modeled)", {"fields":["key_id","algorithm","wrapped_data_key","ciphertext"],"verified":False,"real_pii":False}, **kw)
async def _memory_routing_model(**kw): return await _memory_stub("memory-routing (modeled)", {"routes":{"hot":"Redis","warm":"pgvector","cold":"Cassandra/Trino"},"routing_executed":False}, **kw)
async def _memory_compose_model(**kw): return await _memory_stub("Docker Compose (modeled)", {"services":["memory-api","redis-fixture","pgvector-fixture","cassandra-fixture"],"started":False}, **kw)
async def _storage_estimate_model(**kw): return await _memory_stub("storage-estimate (modeled)", {"tiers":{"hot":"modeled GB","warm":"modeled GB","cold":"modeled TB"},"synthetic_capacity_only":True}, **kw)
async def _oeads_integration_model(**kw): return await _memory_stub("OEADS integration (modeled)", {"interfaces":["audit events","routing decisions","retention policy"],"live_integration":False}, **kw)


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


# ── Chatterbox TTS integration (with stub fallback) ─────────────────

_VOICE_ARTIFACT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "artifacts", "media"
)

_CHATTERBOX_SUPPORTED_LANGS = {
    "ar", "da", "de", "el", "en", "es", "fi", "fr", "he", "hi", "it",
    "ja", "ko", "ms", "nl", "no", "pl", "pt", "ru", "sv", "sw", "tr", "zh",
}

_CHATTERBOX_MODELS: dict[tuple[Any, str, tuple], Any] = {}
_CHATTERBOX_LOCK = asyncio.Lock()


def _is_chatterbox_available() -> bool:
    """Return True if the chatterbox-tts package is installed."""
    import importlib.util
    return (
        importlib.util.find_spec("chatterbox") is not None
        and importlib.util.find_spec("chatterbox.tts") is not None
        and importlib.util.find_spec("chatterbox.mtl_tts") is not None
    )


def _chatterbox_device() -> str:
    """Pick the best device Chatterbox can use."""
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


async def _load_chatterbox_model(model_cls, device: str, **kwargs) -> Any:
    """Load and cache a Chatterbox model in a worker thread."""
    key = (model_cls, device, tuple(sorted(kwargs.items())))
    if key not in _CHATTERBOX_MODELS:
        _CHATTERBOX_MODELS[key] = await asyncio.to_thread(
            model_cls.from_pretrained, device=device, **kwargs
        )
    return _CHATTERBOX_MODELS[key]


async def _generate_chatterbox_voice(script: str, language: str, reference_audio: str = "") -> str:
    """Generate a WAV with Chatterbox and return the local file path."""
    device = _chatterbox_device()
    kwargs = {}
    if reference_audio:
        kwargs["audio_prompt_path"] = reference_audio

    if language == "en":
        from chatterbox.tts import ChatterboxTTS
        model = await _load_chatterbox_model(ChatterboxTTS, device)
        wav = await asyncio.to_thread(model.generate, script, **kwargs)
    else:
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        model = await _load_chatterbox_model(ChatterboxMultilingualTTS, device, t3_model="v3")
        wav = await asyncio.to_thread(
            model.generate, script, language_id=language, **kwargs
        )

    import torch
    import torchaudio as ta

    if wav is None:
        raise ToolError("Chatterbox produced no audio")

    if wav.ndim == 1:
        wav = wav.unsqueeze(0)
    elif wav.ndim > 2:
        wav = wav.squeeze()
        if wav.ndim == 1:
            wav = wav.unsqueeze(0)

    os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
    out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}.wav")
    ta.save(out_path, wav, model.sr)
    return out_path


# ── Coqui TTS integration (with stub fallback) ───────────────────────

_COQUI_SUPPORTED_LANGS = {
    "ar", "cs", "de", "en", "es", "fr", "hi", "hu", "it", "ja", "ko",
    "nl", "pl", "pt", "ru", "tr", "zh", "zh-cn",
}

_COQUI_LANG_MAP = {
    "zh": "zh-cn",
}

_COQUI_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
_COQUI_MODEL: Any = None
_COQUI_LOCK = asyncio.Lock()


def _is_coqui_available() -> bool:
    """Return True if the coqui-tts package is installed."""
    import importlib.util
    return importlib.util.find_spec("TTS") is not None


async def _load_coqui_model() -> Any:
    """Load and cache the Coqui XTTS v2 model in a worker thread."""
    global _COQUI_MODEL
    if _COQUI_MODEL is not None:
        return _COQUI_MODEL
    async with _COQUI_LOCK:
        if _COQUI_MODEL is None:
            from TTS.api import TTS
            device = _chatterbox_device()
            _COQUI_MODEL = await asyncio.to_thread(TTS, _COQUI_MODEL_NAME)
            _COQUI_MODEL = _COQUI_MODEL.to(device)
    return _COQUI_MODEL


async def _generate_coqui_voice(script: str, language: str, reference_audio: str = "") -> str:
    """Generate a WAV with Coqui XTTS v2 and return the local file path."""
    if os.environ.get("COQUI_TOS_AGREED", "") != "1":
        raise ToolError(
            "Coqui XTTS requires accepting the CPML terms. "
            "Set COQUI_TOS_AGREED=1 to enable."
        )

    coqui_lang = _COQUI_LANG_MAP.get(language, language)
    if coqui_lang not in _COQUI_SUPPORTED_LANGS:
        raise ToolError(f"Language '{language}' is not supported by Coqui XTTS v2")

    model = await _load_coqui_model()
    os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
    out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}.wav")

    kwargs = {"text": script, "language": coqui_lang, "file_path": out_path}
    if reference_audio:
        kwargs["speaker_wav"] = reference_audio
    elif model.speakers:
        kwargs["speaker"] = model.speakers[0]
    else:
        raise ToolError("Coqui XTTS v2 has no default speaker and no reference audio was provided")

    await asyncio.to_thread(model.tts_to_file, **kwargs)
    return out_path


async def _clone_voice(tool: str = "chatterbox", language: str = "en",
                       script: str = "", reference_audio: str = "", **_: Any) -> dict:
    p = _VOICE_PROVIDERS.get(tool, _VOICE_PROVIDERS["chatterbox"])
    if p["online"] and not _online_available():
        raise ToolError(f"{p['provider']} requires internet; fall back to an offline voice tool.")

    real_error: str | None = None

    if tool == "chatterbox" and _is_chatterbox_available() and language in _CHATTERBOX_SUPPORTED_LANGS and script:
        try:
            artifact_path = await _generate_chatterbox_voice(script, language, reference_audio)
            return {
                "simulated": True,
                "provider": p["provider"],
                "license": p["license"],
                "requires_internet": False,
                "language": language,
                "reference_audio_sec": 5 if reference_audio else 0,
                "artifact": artifact_path,
                "note": f"Generated locally with {p['provider']} ({'with reference clip' if reference_audio else 'default voice'}).",
            }
        except Exception as exc:
            real_error = f"Chatterbox failed: {exc}"

    elif tool == "coqui" and _is_coqui_available() and language in _COQUI_SUPPORTED_LANGS and script:
        try:
            artifact_path = await _generate_coqui_voice(script, language, reference_audio)
            return {
                "simulated": True,
                "provider": p["provider"],
                "license": p["license"],
                "requires_internet": False,
                "language": language,
                "reference_audio_sec": 5 if reference_audio else 0,
                "artifact": artifact_path,
                "note": f"Generated locally with {p['provider']} ({'with reference clip' if reference_audio else 'built-in speaker'}).",
            }
        except Exception as exc:
            real_error = f"Coqui failed: {exc}"

    note = f"Stub — wire to {p['provider']} for real voice cloning ({'online' if p['online'] else 'offline/local'})."
    if real_error:
        note = f"{real_error}; {note}"
    return {
        "simulated": True,
        "provider": p["provider"],
        "license": p["license"],
        "requires_internet": p["online"],
        "language": language,
        "reference_audio_sec": 5,
        "artifact": "/artifacts/media/voice_stub.wav",
        "note": note,
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


# ── Video Stack stubs (face-swap / lip-sync / restore; offline, simulated) ──

_FACESWAP_PROVIDERS = {
    "deepfacelab": {"provider": "DeepFaceLab", "mode": "batch", "note": "professional face-swap, CLI automation"},
    "faceswap": {"provider": "FaceSwap", "mode": "batch", "note": "TensorFlow, cross-platform"},
    "deeplivecam": {"provider": "Deep-Live-Cam", "mode": "realtime", "note": "real-time single-image swap"},
}

_LIPSYNC_PROVIDERS = {
    "wav2lip": {"provider": "Wav2Lip", "note": "audio-driven lip-sync"},
    "videoretalking": {"provider": "VideoRetalking", "note": "expression-aware retalking"},
}


async def _face_swap(tool: str = "deepfacelab", source: str = "", target: str = "",
                     **_: Any) -> dict:
    p = _FACESWAP_PROVIDERS.get(tool, _FACESWAP_PROVIDERS["deepfacelab"])
    return {
        "simulated": True,
        "provider": p["provider"],
        "mode": p["mode"],
        "requires_internet": False,
        "resolution": "1080p",
        "artifact": "/artifacts/video/swap_stub.mp4",
        "note": f"Stub — {p['note']}. Simulated only; no real face-swap is performed. "
                "Real integration is consent-gated and audit-logged.",
    }


async def _lip_sync(tool: str = "wav2lip", video: str = "", audio: str = "",
                    **_: Any) -> dict:
    p = _LIPSYNC_PROVIDERS.get(tool, _LIPSYNC_PROVIDERS["wav2lip"])
    return {
        "simulated": True,
        "provider": p["provider"],
        "requires_internet": False,
        "fps": 25,
        "artifact": "/artifacts/video/lipsync_stub.mp4",
        "note": f"Stub — {p['note']}. Simulated only.",
    }


async def _gfpgan_upscale(input_path: str = "", scale: int = 2, **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "GFPGAN",
        "requires_internet": False,
        "scale": scale,
        "artifact": "/artifacts/video/restored_stub.mp4",
        "note": "Stub — wire to GFPGAN for face restoration / upscaling (offline/local).",
    }


async def _ffmpeg_pipeline(steps: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "FFmpeg",
        "requires_internet": False,
        "steps": steps or "trim,concat,scale,mux",
        "artifact": "/artifacts/video/final_stub.mp4",
        "note": "Stub — deterministic FFmpeg compositing/mux pipeline (offline/local).",
    }


# ── Cyber Crew stubs (defensive security; simulated, offline) ───────
# These stand in for real security tooling (Nmap, OpenVAS, OWASP ZAP, JA3, CAI,
# Metasploit, OSINT). Everything is SIMULATED — no real scanning, exploitation,
# fingerprint spoofing, or reconnaissance is performed. Results are synthetic and
# framed for authorized, defensive, blue-team / lab use only.

_SCAN_PROVIDERS = {
    "nmap": {"provider": "Nmap", "kind": "port/service discovery"},
    "openvas": {"provider": "OpenVAS", "kind": "vulnerability assessment"},
}


async def _recon_scan(tool: str = "nmap", target: str = "", **_: Any) -> dict:
    p = _SCAN_PROVIDERS.get(tool, _SCAN_PROVIDERS["nmap"])
    return {
        "simulated": True,
        "provider": p["provider"],
        "kind": p["kind"],
        "requires_internet": False,
        "target": "lab-scoped target (redacted)",
        "open_ports": [{"port": 22, "svc": "ssh"}, {"port": 443, "svc": "https"}],
        "findings": [{"id": "sim-info-1", "severity": "info", "title": "TLS 1.2 offered"}],
        "note": f"Stub — {p['provider']} {p['kind']}. Simulated only; no real scan is run. "
                "Authorized/defensive lab use; assume scope authorization is required.",
    }


async def _dast_scan(tool: str = "zap", target: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "OWASP ZAP / Burp Suite",
        "requires_internet": False,
        "target": "lab-scoped web app (redacted)",
        "alerts": [
            {"risk": "medium", "name": "Missing security headers (simulated)"},
            {"risk": "low", "name": "Cookie without SameSite (simulated)"},
        ],
        "note": "Stub — dynamic application security testing. Simulated only; no real "
                "requests are sent. Authorized/defensive testing context.",
    }


async def _ja3_fingerprint(host: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Salesforce JA3",
        "requires_internet": False,
        "ja3": "769,47-53-5-10-49171-49172,0-11-10,23-24,0 (example hash)",
        "purpose": "TLS client fingerprint ANALYSIS / detection (blue-team)",
        "note": "Stub — JA3/JA3S fingerprint profiling for DETECTION and inventory. "
                "Simulated only. Does not perform fingerprint spoofing or evasion.",
    }


async def _exploit_validate(module: str = "", target: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Metasploit",
        "requires_internet": False,
        "module": module or "auxiliary/scanner (simulated)",
        "outcome": "no exploitation performed",
        "note": "Stub — controlled vulnerability VALIDATION concept only. Simulated; no "
                "payloads, no exploitation, no real target interaction. Requires written "
                "authorization and lab scope for any real use.",
    }


async def _osint_lookup(subject: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "OSINT (public sources)",
        "requires_internet": False,
        "subject": "authorized asset (redacted)",
        "exposure": ["example public DNS record", "example leaked-credential indicator"],
        "note": "Stub — passive open-source exposure mapping for owned/authorized assets. "
                "Simulated only; no live collection is performed.",
    }


async def _cai_redteam(scope: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "CAI (Alias Robotics)",
        "requires_internet": False,
        "scope": "authorized engagement scope (redacted)",
        "plan": ["surface mapping", "DAST", "manual validation", "reporting"],
        "note": "Stub — automated red-teaming / DAST orchestration concept. Simulated only; "
                "no autonomous attacks are executed. Authorized engagement required.",
    }


# ── TIER 3 · Persona Orchestration stubs (simulated, offline) ───────
# Stand-ins for ElizaOS / Botpress / LangGraph / Socioboard / Playwright. Every
# result is SIMULATED and stays inside the platform — no real synthetic accounts
# are created, no real social posting is performed, and no stealth / fingerprint-
# evasion against live platforms is done. Framed for authorized research,
# red/blue-team training, and detection of coordinated inauthentic behavior.

async def _persona_design(archetype: str = "", region: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "ElizaOS",
        "requires_internet": False,
        "persona_id": "sim-persona-0001 (in-lab only)",
        "layers": ["identity", "backstory", "demographics", "psychographics",
                   "digital-footprint", "voice", "goals"],
        "archetype": archetype or "generic-lab-persona",
        "note": "Stub — 7-layer synthetic-identity design concept. Simulated only; no real "
                "identity, account, or digital footprint is created. Authorized research/"
                "training and detection use only.",
    }


async def _behavior_model(persona_id: str = "", goal: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Botpress / LangGraph",
        "requires_internet": False,
        "persona_id": persona_id or "sim-persona-0001",
        "patterns": ["posting cadence (modeled)", "topic affinities (modeled)",
                     "interaction style (modeled)"],
        "note": "Stub — behavioral modeling / interaction scripting concept. Simulated only; "
                "no live agents are deployed and no real interactions are sent. For modeling "
                "and detection of inauthentic behavior in a lab.",
    }


async def _voice_dialect_map(language: str = "", dialect: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Coqui / Chatterbox (offline) · ElevenLabs (online, optional)",
        "requires_internet": False,
        "language": language or "ur",
        "dialect": dialect or "standard",
        "calibration": {"pitch": "modeled", "cadence": "modeled", "register": "modeled"},
        "note": "Stub — regional dialect calibration & voice-engine mapping concept. "
                "Simulated only; no audio is synthesized here. Offline engines preferred.",
    }


async def _browser_automation_plan(target: str = "", tool: str = "playwright", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "Playwright / Puppeteer / Selenium",
        "requires_internet": False,
        "tool": tool or "playwright",
        "capabilities": ["headless session (concept)", "auto-waiting (concept)",
                         "multi-browser (concept)"],
        "note": "Stub — headless-automation PLAN only. Simulated; no browser is launched, no "
                "site is visited, and NO stealth / anti-detection / fingerprint-evasion is "
                "performed. Any real automation must respect site terms and platform integrity.",
    }


async def _fleet_orchestrate(count: int = 0, platform: str = "", **_: Any) -> dict:
    return {
        "simulated": True,
        "provider": "ElizaOS / Socioboard",
        "requires_internet": False,
        "fleet_size": "modeled (not deployed)",
        "platform": platform or "lab-dashboard",
        "lifecycle": ["design", "provision (simulated)", "monitor (simulated)", "retire"],
        "note": "Stub — multi-persona fleet coordination / lifecycle concept. Simulated only; "
                "no accounts are provisioned and nothing is deployed to real platforms. "
                "Intended for scale modeling and detection research.",
    }

# ── TIER 4 · SIM farm / GSM gateway simulator adapters ─────────────
async def _modem_topology(**kwargs): return await simfarm_sim.modem_topology(**kwargs)
async def _smsgate_config(**kwargs): return await simfarm_sim.gateway_config(**kwargs)
async def _modem_control(**kwargs): return await simfarm_sim.modem_control(**kwargs)
async def _sim_provision_plan(**kwargs): return await simfarm_sim.provision_plan(**kwargs)
async def _sim_activate(**kwargs): return await simfarm_sim.sim_activate(**kwargs)
async def _carrier_access(**kwargs): return await simfarm_sim.carrier_access(**kwargs)
async def _campaign_orchestrate(**kwargs): return await simfarm_sim.campaign_orchestrate(**kwargs)
async def _sms_send(**kwargs): return await simfarm_sim.sms_send(**kwargs)
async def _celery_dispatch(**kwargs): return await simfarm_sim.celery_dispatch(**kwargs)


def _register_defaults() -> None:
    if _REGISTRY:
        return
    register(ToolSpec(
        id="index_dataset", name="Dataset Indexer",
        description="Index and query dataset records (CRM, CDR, profiles).",
        category="analysis", provider="LlamaIndex", run=_index_dataset,
        parameters={"source": "dataset name", "query": "search query"},
        status="live",
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
        parameters={"tool": "chatterbox|coqui|bark|elevenlabs", "language": "lang", "script": "text", "reference_audio": "optional path to a 5-20s reference WAV"},
        status="live" if (_is_chatterbox_available() or _is_coqui_available()) else "stub",
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
        id="face_swap", name="Face-Swap Engine",
        description="Face-swap / video synthesis (DeepFaceLab, FaceSwap, Deep-Live-Cam). Consent-gated, simulated.",
        category="media", provider="DeepFaceLab / FaceSwap / Deep-Live-Cam", run=_face_swap,
        parameters={"tool": "deepfacelab|faceswap|deeplivecam", "source": "source", "target": "target"},
    ))
    register(ToolSpec(
        id="lip_sync", name="Lip-Sync Engine",
        description="Lip-sync deepfake anchors (Wav2Lip, VideoRetalking). Simulated.",
        category="media", provider="Wav2Lip / VideoRetalking", run=_lip_sync,
        parameters={"tool": "wav2lip|videoretalking", "video": "video", "audio": "audio"},
    ))
    register(ToolSpec(
        id="gfpgan_upscale", name="Face Restore / Upscale",
        description="GFPGAN face restoration and upscaling.",
        category="media", provider="GFPGAN", run=_gfpgan_upscale,
        parameters={"input_path": "input", "scale": "upscale factor"},
    ))
    register(ToolSpec(
        id="ffmpeg_pipeline", name="FFmpeg Pipeline",
        description="Deterministic FFmpeg compositing / muxing pipeline.",
        category="media", provider="FFmpeg", run=_ffmpeg_pipeline,
        parameters={"steps": "comma-separated steps"},
    ))
    register(ToolSpec(
        id="recon_scan", name="Attack-Surface Scanner",
        description="Port/service discovery & vulnerability assessment (Nmap, OpenVAS). Simulated.",
        category="security", provider="Nmap / OpenVAS", run=_recon_scan,
        parameters={"tool": "nmap|openvas", "target": "authorized in-scope target"},
    ))
    register(ToolSpec(
        id="dast_scan", name="DAST Scanner",
        description="Dynamic application security testing (OWASP ZAP, Burp Suite). Simulated.",
        category="security", provider="OWASP ZAP / Burp Suite", run=_dast_scan,
        parameters={"tool": "zap|burp", "target": "authorized web app"},
    ))
    register(ToolSpec(
        id="ja3_fingerprint", name="TLS Fingerprint Analyzer",
        description="JA3/JA3S TLS client fingerprint analysis for detection (blue-team). Simulated.",
        category="security", provider="Salesforce JA3", run=_ja3_fingerprint,
        parameters={"host": "host to profile"},
    ))
    register(ToolSpec(
        id="exploit_validate", name="Vulnerability Validator",
        description="Controlled vulnerability validation concept (Metasploit). Simulated; no exploitation.",
        category="security", provider="Metasploit", run=_exploit_validate,
        parameters={"module": "module name", "target": "authorized target"},
    ))
    register(ToolSpec(
        id="osint_lookup", name="OSINT Exposure Mapper",
        description="Passive open-source exposure mapping for owned/authorized assets. Simulated.",
        category="security", provider="OSINT", run=_osint_lookup,
        parameters={"subject": "owned/authorized asset"},
    ))
    register(ToolSpec(
        id="cai_redteam", name="Automated Red-Team Orchestrator",
        description="Automated red-teaming / DAST orchestration concept (CAI). Simulated.",
        category="security", provider="CAI (Alias Robotics)", run=_cai_redteam,
        parameters={"scope": "authorized engagement scope"},
    ))
    register(ToolSpec(
        id="playwright_stealth_check", name="Automation Posture Check",
        description="Check automated-session detection posture for an endpoint.",
        category="stealth", provider="Playwright", run=_playwright_stealth_check,
        parameters={"endpoint": "target endpoint"},
    ))
    register(ToolSpec(
        id="persona_design", name="Synthetic Persona Designer",
        description="7-layer synthetic-identity design concept (ElizaOS). Simulated; no real identity created.",
        category="persona", provider="ElizaOS", run=_persona_design,
        parameters={"archetype": "persona archetype", "region": "target region"},
    ))
    register(ToolSpec(
        id="behavior_model", name="Behavior Modeler",
        description="Behavioral modeling / interaction scripting concept (Botpress/LangGraph). Simulated.",
        category="persona", provider="Botpress / LangGraph", run=_behavior_model,
        parameters={"persona_id": "persona id", "goal": "objective"},
    ))
    register(ToolSpec(
        id="voice_dialect_map", name="Voice & Dialect Mapper",
        description="Regional dialect calibration & voice-engine mapping (offline TTS; ElevenLabs optional). Simulated.",
        category="persona", provider="Coqui / Chatterbox / ElevenLabs", run=_voice_dialect_map,
        parameters={"language": "language code", "dialect": "regional dialect"},
    ))
    register(ToolSpec(
        id="browser_automation_plan", name="Browser Automation Planner",
        description="Headless-automation plan concept (Playwright/Puppeteer/Selenium). Simulated; no stealth/evasion.",
        category="persona", provider="Playwright / Puppeteer / Selenium", run=_browser_automation_plan,
        parameters={"target": "authorized target", "tool": "playwright|puppeteer|selenium"},
    ))
    register(ToolSpec(
        id="fleet_orchestrate", name="Persona Fleet Orchestrator",
        description="Multi-persona coordination / lifecycle concept (ElizaOS/Socioboard). Simulated; nothing deployed.",
        category="persona", provider="ElizaOS / Socioboard", run=_fleet_orchestrate,
        parameters={"count": "fleet size (modeled)", "platform": "platform"},
    ))
    tier4 = [
        ("modem_topology", "Modem Topology", "SIM800/SIM900 · Gammu", _modem_topology, {"modem_type":"modem type","ports":"port count","hub_layout":"hub layout"}),
        ("smsgate_config", "SMSGate Config", "SMSgate · Gammu", _smsgate_config, {"gateway":"gateway","pool_size":"pool size"}),
        ("modem_control", "Modem Control", "Gammu", _modem_control, {"command":"modeled command"}),
        ("sim_provision_plan", "SIM Provision Plan", "carrier-provisioning (modeled)", _sim_provision_plan, {"count":"modeled count","carriers":"carrier list"}),
        ("sim_activate", "SIM Activate", "carrier-provisioning (modeled)", _sim_activate, {"iccid":"lab ICCID"}),
        ("carrier_access", "Carrier Access", "carrier-API (modeled)", _carrier_access, {"carrier":"carrier"}),
        ("campaign_orchestrate", "Campaign Orchestrator", "Celery", _campaign_orchestrate, {"tasks":"modeled tasks","schedule":"schedule"}),
        ("sms_send", "SMS Send", "SMSgate", _sms_send, {"to":"lab sink","body":"fixture body"}),
        ("celery_dispatch", "Celery Dispatch", "Celery", _celery_dispatch, {"task":"modeled task"}),
    ]
    for ident, name, provider, fn, params in tier4:
        register(ToolSpec(id=ident, name=name,
            description="Simulated infrastructure action; real telecom execution requires communications-secretariat orders and is not performed.",
            category="infrastructure", provider=provider, run=fn, parameters=params))
    tier4_local = [
        ("ivr_hardware_setup","IVR Hardware Setup","Raspberry Pi · GSM · RASP-IVR",_ivr_hardware_setup,{"hardware_kit":"hardware kit","scenario":"scenario"}),
        ("call_flow_design","Call Flow Designer","Verboice",_call_flow_design,{"scenario":"scenario","objective":"objective"}),
        ("dtmf_handler","DTMF Handler","VBVoice",_dtmf_handler,{"scenario":"scenario","objective":"objective"}),
        ("rural_reach_model","Rural Reach Model","rural-reach (modeled)",_rural_reach_model,{"reach_model":"reach model","scenario":"scenario"}),
        ("call_route_plan","Call Route Planner","call-routing (modeled)",_call_route_plan,{"scenario":"scenario","objective":"objective"}),
        ("ivr_cost_model","IVR Cost Model","cost-model (modeled)",_ivr_cost_model,{"scenario":"scenario","objective":"objective"}),
        ("scrapoxy_deploy","Scrapoxy Deploy","Scrapoxy · Docker",_scrapoxy_deploy,{"provider":"provider","scenario":"scenario"}),
        ("cloud_connector","Cloud Connector","cloud-connectors (modeled)",_cloud_connector,{"provider":"provider","scenario":"scenario"}),
        ("proxy_pool_size","Proxy Pool Sizer","pool-sizing (modeled)",_proxy_pool_size,{"pool_type":"pool type","objective":"objective"}),
        ("proxy_health_monitor","Proxy Health Monitor","health-monitor (modeled)",_proxy_health_monitor,{"pool_type":"pool type","scenario":"scenario"}),
        ("proxy_integration_plan","Proxy Integration Planner","Playwright · Puppeteer · requests",_proxy_integration_plan,{"provider":"provider","objective":"objective"}),
        ("proxy_cost_model","Proxy Cost Model","cost-model (modeled)",_proxy_cost_model,{"provider":"provider","pool_type":"pool type"}),
        ("proxy_deployment_synth","Proxy Deployment Synthesizer","deployment (modeled)",_proxy_deployment_synth,{"provider":"provider","scenario":"scenario"}),
    ]
    for ident, name, provider, fn, params in tier4_local:
        category = "ivr" if ident.startswith(("ivr_", "call_", "dtmf_", "rural_")) else "proxy"
        register(ToolSpec(id=ident, name=name,
            description="Simulated only; real execution requires communications-secretariat orders and is not performed.",
            category=category, provider=provider, run=fn, parameters=params))
    stealth_local = [
        ("stealth_patch_model","Stealth Patch Model","playwright-extra",_stealth_patch_model),
        ("canvas_spoof_model","Canvas Spoof Model","canvas-spoof (modeled)",_canvas_spoof_model),
        ("webrtc_spoof_model","WebRTC Spoof Model","WebRTC-spoof (modeled)",_webrtc_spoof_model),
        ("human_behavior_model","Human Behavior Model","behavior-sim (modeled)",_human_behavior_model),
        ("flaresolverr_model","FlareSolverr Model","FlareSolverr · Docker",_flaresolverr_model),
        ("challenge_bypass_model","Challenge Bypass Model","challenge-solver (modeled)",_challenge_bypass_model),
        ("fingerprint_pool_model","Fingerprint Pool Model","Browserbase · Scrapoxy",_fingerprint_pool_model),
        ("session_isolation_model","Session Isolation Model","session-isolation (modeled)",_session_isolation_model),
        ("ip_warmup_model","IP Warmup Model","IP-warmup (modeled)",_ip_warmup_model),
        ("evasion_matrix_model","Evasion Matrix Model","evasion-matrix (modeled)",_evasion_matrix_model),
        ("stealth_checklist_model","Stealth Checklist Model","stealth-checklist (modeled)",_stealth_checklist_model),
    ]
    content_local = [
        ("mautic_campaign_model","Mautic Campaign Model","Mautic · Docker",_mautic_campaign_model),
        ("lead_scoring_model","Lead Scoring Model","Mautic · lead-scoring",_lead_scoring_model),
        ("email_auth_model","Email Auth Model","DKIM/SPF/DMARC (modeled)",_email_auth_model),
        ("strapi_lifecycle_model","Strapi Lifecycle Model","Strapi · AI",_strapi_lifecycle_model),
        ("webhook_chain_model","Webhook Chain Model","webhook (modeled)",_webhook_chain_model),
        ("postiz_scheduler_model","Postiz Scheduler Model","Postiz",_postiz_scheduler_model),
        ("cross_platform_model","Cross Platform Model","cross-platform (modeled)",_cross_platform_model),
        ("content_calendar_model","Content Calendar Model","calendar (modeled)",_content_calendar_model),
        ("content_cost_model","Content Cost Model","cost-model (modeled)",_content_cost_model),
    ]
    memory_local = [
        ("mem0_fact_extraction_model","Mem0 Fact Extraction Model","Mem0",_mem0_fact_extraction_model),
        ("persona_memory_isolation_model","Persona Memory Isolation Model","persona-isolation (modeled)",_persona_memory_isolation_model),
        ("async_write_pipeline_model","Async Write Pipeline Model","async-write (modeled)",_async_write_pipeline_model),
        ("vector_graph_store_model","Vector Graph Store Model","Qdrant · Neo4j · Redis",_vector_graph_store_model),
        ("pgvector_schema_model","pgvector Schema Model","PostgreSQL · pgvector",_pgvector_schema_model),
        ("memory_tiering_model","Memory Tiering Model","memory-tiering (modeled)",_memory_tiering_model),
        ("event_sourcing_model","Event Sourcing Model","event-sourcing (modeled)",_event_sourcing_model),
        ("conflict_resolution_model","Conflict Resolution Model","conflict-resolution (modeled)",_conflict_resolution_model),
        ("kafka_topic_model","Kafka Topic Model","Kafka (modeled)",_kafka_topic_model),
        ("cassandra_schema_model","Cassandra Schema Model","Cassandra (synthetic)",_cassandra_schema_model),
        ("pyspark_bulk_load_model","PySpark Bulk Load Model","PySpark (modeled)",_pyspark_bulk_load_model),
        ("trino_analytics_model","Trino Analytics Model","Trino (modeled)",_trino_analytics_model),
        ("pii_encryption_model","PII Encryption Model","envelope-encryption (modeled)",_pii_encryption_model),
        ("memory_routing_model","Memory Routing Model","memory-routing (modeled)",_memory_routing_model),
        ("memory_compose_model","Memory Compose Model","Docker Compose (modeled)",_memory_compose_model),
        ("storage_estimate_model","Storage Estimate Model","storage-estimate (modeled)",_storage_estimate_model),
        ("oeads_integration_model","OEADS Integration Model","OEADS integration (modeled)",_oeads_integration_model),
    ]
    memory_ids = {x[0] for x in memory_local}
    stealth_ids = {x[0] for x in stealth_local}
    for ident,name,provider,fn in stealth_local+content_local+memory_local:
        register(ToolSpec(id=ident,name=name,description="Simulated only; real execution requires authorization and is not performed.",
                          category="stealth" if ident in stealth_ids else "memory" if ident in memory_ids else "content",
                          provider=provider,run=fn))


_register_defaults()
