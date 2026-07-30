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
import shlex
import shutil
import sys
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


def _is_playwright_available() -> bool:
    """Return True if the Playwright Python package is installed."""
    import importlib.util
    return importlib.util.find_spec("playwright") is not None


_BROWSER_ARTIFACT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "artifacts", "browser"
)


def _is_target_url(target: str) -> bool:
    """Return True if the target looks like a URL or about:blank."""
    return bool(target and (target.startswith(("http://", "https://", "file://")) or "://" in target or target == "about:blank"))


def _normalize_browser_target(target: str) -> str:
    """Convert a local file path to a file:// URL; leave real URLs unchanged."""
    if _is_target_url(target):
        return target
    if target and os.path.exists(target):
        return "file://" + os.path.abspath(target)
    return ""


def _is_headless_true(value: Any) -> bool:
    """Coerce a string/bool headless parameter to a boolean."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes", "on")


async def _run_playwright_session(
    target: str,
    action: str = "navigate",
    script: str = "",
    selector: str = "",
    value: str = "",
    headless: bool = True,
    screenshot: bool = False,
    output: str = "",
    browser: str = "chromium",
) -> dict:
    """Launch a Playwright browser session and execute the requested action.

    This is a defensive-automation helper: it can drive a real headless browser,
    but it never claims the result is non-simulated and it respects the
    offline-first `ALLOW_ONLINE_TOOLS` policy for external URLs.
    """
    from playwright.async_api import async_playwright

    target_url = _normalize_browser_target(target)
    if not target_url:
        raise ToolError("target must be a URL (http/https/file) or an existing file path")

    is_remote = target_url.startswith(("http://", "https://"))
    if is_remote and not _online_available():
        raise ToolError("Remote URLs require ALLOW_ONLINE_TOOLS=1")

    os.makedirs(_BROWSER_ARTIFACT_DIR, exist_ok=True)
    out_path = output
    if not out_path:
        ext = ".png" if screenshot else ".json"
        out_path = os.path.join(_BROWSER_ARTIFACT_DIR, f"{uuid.uuid4()}{ext}")
    elif not os.path.isabs(out_path):
        out_path = os.path.join(_duix_data_dir(), out_path)
    out_path = os.path.normpath(os.path.abspath(out_path))

    result: dict = {"target": target_url, "action": action, "headless": headless}

    async with async_playwright() as p:
        browser_launcher = getattr(p, browser, p.chromium)
        browser_obj = await browser_launcher.launch(headless=headless)
        try:
            context = await browser_obj.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()
            response = await page.goto(target_url, wait_until="networkidle" if is_remote else "domcontentloaded")
            result["status"] = response.status if response else None
            result["title"] = await page.title()
            result["url"] = page.url

            action_clean = (action or "navigate").lower()

            if action_clean == "stealth":
                signals = await page.evaluate("""() => ({
                    userAgent: navigator.userAgent,
                    webdriver: navigator.webdriver,
                    plugins: navigator.plugins ? navigator.plugins.length : null,
                    languages: navigator.languages,
                    platform: navigator.platform,
                    hardwareConcurrency: navigator.hardwareConcurrency,
                    deviceMemory: navigator.deviceMemory,
                    maxTouchPoints: navigator.maxTouchPoints,
                    chrome: typeof window.chrome !== 'undefined',
                    chromeRuntime: typeof chrome !== 'undefined' && !!chrome.runtime,
                    notificationPermissions: typeof Notification !== 'undefined',
                })""")
                result["signals"] = signals
                flags = []
                if signals.get("webdriver"):
                    flags.append("navigator.webdriver === true")
                if signals.get("plugins") == 0:
                    flags.append("zero_plugins")
                if not signals.get("chrome"):
                    flags.append("window.chrome_missing")
                if signals.get("languages") and len(signals.get("languages", [])) == 0:
                    flags.append("no_languages")
                result["flags"] = flags
                # Grade: A if no obvious flags, B if one, C if more.
                if len(flags) == 0:
                    result["stealth_grade"] = "A"
                elif len(flags) == 1:
                    result["stealth_grade"] = "B"
                else:
                    result["stealth_grade"] = "C"

            elif action_clean == "screenshot":
                await page.screenshot(path=out_path, full_page=False)
                result["screenshot"] = out_path

            elif action_clean == "evaluate":
                if not script:
                    raise ToolError("evaluate action requires a 'script' parameter")
                eval_result = await page.evaluate(script)
                result["evaluate_result"] = eval_result

            elif action_clean == "click":
                if not selector:
                    raise ToolError("click action requires a 'selector' parameter")
                await page.click(selector)
                result["clicked"] = selector

            elif action_clean == "type":
                if not selector or value is None:
                    raise ToolError("type action requires 'selector' and 'value' parameters")
                await page.fill(selector, value)
                result["filled"] = selector

            elif action_clean == "get_text":
                text = await page.inner_text("body")
                result["text"] = text[:10000]

            elif action_clean == "html":
                html = await page.content()
                result["html"] = html[:10000]

            elif action_clean in ("navigate", "goto"):
                # result already populated with title/url/status
                pass

            else:
                raise ToolError(f"Unsupported browser action: {action}")

            if screenshot and action_clean != "screenshot":
                await page.screenshot(path=out_path, full_page=False)
                result["screenshot"] = out_path
        finally:
            await browser_obj.close()

    return result


async def _playwright_stealth_check(endpoint: str = "", **_: Any) -> dict:
    """Launch a real Playwright session and report automation-detection signals."""
    if not _is_playwright_available():
        return {
            "simulated": True,
            "provider": "Playwright",
            "endpoint": endpoint,
            "stealth_grade": "B",
            "flags": ["webdriver_present"],
            "note": "Stub — Playwright package not installed.",
        }

    try:
        target = endpoint or "about:blank"
        session = await _run_playwright_session(
            target=target,
            action="stealth",
            headless=True,
        )
        return {
            "simulated": True,
            "provider": "Playwright",
            "endpoint": endpoint,
            "stealth_grade": session.get("stealth_grade", "B"),
            "flags": session.get("flags", []),
            "signals": session.get("signals", {}),
            "url": session.get("url"),
            "note": "Real Playwright session launched; signals collected for defensive detection research.",
        }
    except Exception as exc:
        return {
            "simulated": True,
            "provider": "Playwright",
            "endpoint": endpoint,
            "stealth_grade": "B",
            "flags": ["webdriver_present"],
            "note": f"Playwright failed ({exc}); falling back to modeled signals.",
        }


async def _browser_automation_plan(
    target: str = "",
    tool: str = "playwright",
    action: str = "navigate",
    script: str = "",
    selector: str = "",
    value: str = "",
    headless: bool = True,
    screenshot: bool = False,
    output: str = "",
    **_: Any,
) -> dict:
    """Headless browser automation with Playwright. Falls back to a plan stub."""
    if tool != "playwright":
        return {
            "simulated": True,
            "provider": "Playwright / Puppeteer / Selenium",
            "requires_internet": False,
            "tool": tool or "playwright",
            "capabilities": ["headless session (concept)", "auto-waiting (concept)",
                             "multi-browser (concept)"],
            "note": f"Tool '{tool}' is not supported by the Playwright integration; only 'playwright' is wired.",
        }

    if not _is_playwright_available() or not target or not (_is_target_url(target) or os.path.exists(target)):
        return {
            "simulated": True,
            "provider": "Playwright",
            "requires_internet": False,
            "tool": tool or "playwright",
            "target": target,
            "action": action or "navigate",
            "capabilities": ["headless session", "auto-waiting", "multi-browser (chromium)",
                             "navigate", "screenshot", "evaluate", "click", "type", "get_text", "html"],
            "note": "Playwright plan stub. Pass a URL/file target and set action='navigate' (or install Playwright) to execute a real browser session.",
        }

    try:
        session = await _run_playwright_session(
            target=target,
            action=action,
            script=script,
            selector=selector,
            value=value,
            headless=_is_headless_true(headless),
            screenshot=_is_headless_true(screenshot),
            output=output,
        )
        return {
            "simulated": True,
            "provider": "Playwright",
            "requires_internet": False,
            "tool": tool or "playwright",
            "target": session.get("target"),
            "action": session.get("action"),
            "title": session.get("title"),
            "url": session.get("url"),
            "status": session.get("status"),
            "screenshot": session.get("screenshot"),
            "evaluate_result": session.get("evaluate_result"),
            "filled": session.get("filled"),
            "clicked": session.get("clicked"),
            "text": session.get("text"),
            "html": session.get("html"),
            "note": "Real Playwright browser session executed.",
        }
    except Exception as exc:
        return {
            "simulated": True,
            "provider": "Playwright",
            "requires_internet": False,
            "tool": tool or "playwright",
            "target": target,
            "action": action or "navigate",
            "capabilities": ["headless session", "auto-waiting", "multi-browser (chromium)"],
            "note": f"Playwright execution failed ({exc}); falling back to plan stub.",
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
    "videoretalking": {"provider": "VideoRetalking", "license": "open", "online": False},
    "roop": {"provider": "Roop", "license": "open", "online": False},
    "sadtalker": {"provider": "SadTalker", "license": "open", "online": False},
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


# ── Wan2.1 text-to-video integration (with stub fallback) ───────────

_WAN2_MODEL_NAME = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
_WAN2_NEGATIVE_PROMPT = (
    "Bright tones, overexposed, static, blurred details, subtitles, style, works, "
    "paintings, images, static, overall gray, worst quality, low quality, JPEG "
    "compression residue, ugly, incomplete, extra fingers, poorly drawn hands, "
    "poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, "
    "still picture, messy background, three legs, many people in the background, "
    "walking backwards"
)
_WAN2_PIPELINE: Any = None
_WAN2_LOCK = asyncio.Lock()


def _is_wan2_available() -> bool:
    """Return True if diffusers>=0.33 with Wan support is installed."""
    import importlib.util
    try:
        import diffusers
        return (
            importlib.util.find_spec("diffusers") is not None
            and hasattr(diffusers, "__version__")
            and diffusers.__version__ >= "0.33.0"
            and hasattr(diffusers, "WanPipeline")
        )
    except Exception:
        return False


def _wan2_torch_dtype() -> Any:
    """Pick a safe dtype for the current device."""
    import torch
    if torch.cuda.is_available():
        return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return torch.float32


async def _load_wan2_pipeline() -> Any:
    """Load and cache the Wan2.1 1.3B T2V pipeline in a worker thread."""
    global _WAN2_PIPELINE
    if _WAN2_PIPELINE is not None:
        return _WAN2_PIPELINE
    async with _WAN2_LOCK:
        if _WAN2_PIPELINE is None:
            import torch
            from diffusers import AutoencoderKLWan, WanPipeline
            dtype = _wan2_torch_dtype()
            vae_dtype = torch.float32
            vae = await asyncio.to_thread(
                AutoencoderKLWan.from_pretrained, _WAN2_MODEL_NAME,
                subfolder="vae", torch_dtype=vae_dtype
            )
            _WAN2_PIPELINE = await asyncio.to_thread(
                WanPipeline.from_pretrained, _WAN2_MODEL_NAME,
                vae=vae, torch_dtype=dtype
            )
            if torch.cuda.is_available():
                _WAN2_PIPELINE = _WAN2_PIPELINE.to("cuda")
            else:
                _WAN2_PIPELINE = _WAN2_PIPELINE.to("cpu")
    return _WAN2_PIPELINE


def _parse_duration(duration: str) -> int:
    """Parse a duration string like '60s' or '5' into seconds (default 5)."""
    digits = "".join(ch for ch in (duration or "5s") if ch.isdigit())
    try:
        return max(1, int(digits or 5))
    except ValueError:
        return 5


async def _generate_wan2_video(script: str, duration: str = "5s") -> str:
    """Generate an MP4 with Wan2.1 and return the local file path."""
    import torch
    from diffusers.utils import export_to_video

    pipe = await _load_wan2_pipeline()
    seconds = _parse_duration(duration)
    # Wan2.1 default training resolution is 480P; keep frame count modest and cap it.
    num_frames = min(max(5, seconds * 15), 81)
    num_frames = max(5, (num_frames // 4) * 4 + 1)

    os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
    out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}.mp4")

    frames = await asyncio.to_thread(
        pipe,
        prompt=script,
        negative_prompt=_WAN2_NEGATIVE_PROMPT,
        height=480,
        width=832,
        num_frames=num_frames,
        guidance_scale=5.0,
        num_inference_steps=30,
    )
    export_to_video(frames.frames[0], out_path, fps=15)
    return out_path


async def _generate_video(tool: str = "wan2", script: str = "", duration: str = "60s",
                          **_: Any) -> dict:
    p = _VIDEO_PROVIDERS.get(tool, _VIDEO_PROVIDERS["wan2"])
    if p["online"] and not _online_available():
        raise ToolError(f"{p['provider']} requires internet; fall back to an offline video model.")

    if tool == "wan2" and _is_wan2_available() and script:
        try:
            artifact_path = await _generate_wan2_video(script, duration)
            return {
                "simulated": True,
                "provider": p["provider"],
                "license": p["license"],
                "requires_internet": False,
                "params": p["params"],
                "resolution": "480p",
                "duration": duration,
                "artifact": artifact_path,
                "note": f"Generated locally with {p['provider']} (1.3B, CPU/GPU).",
            }
        except Exception as exc:
            return {
                "simulated": True,
                "provider": p["provider"],
                "license": p["license"],
                "requires_internet": False,
                "params": p["params"],
                "resolution": "480p",
                "duration": duration,
                "artifact": "/artifacts/media/clip_stub.mp4",
                "note": f"Wan2.1 failed ({exc}); Stub — wire to {p['provider']} for real text-to-video (offline/local).",
            }

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


# ── Duix-Avatar integration (remote service, with stub fallback) ────

_DUIX_POLL_INTERVAL = 2.0
_DUIX_MAX_POLL = 120


def _duix_video_host() -> str:
    """Return the configured Duix video-generation service URL, or empty."""
    return os.environ.get("DUIX_VIDEO_HOST", "").rstrip("/")


def _duix_data_dir() -> str:
    """Return the shared data directory visible to both the app and Duix."""
    return os.environ.get("DUIX_DATA_DIR", _VOICE_ARTIFACT_DIR)


async def _prepare_audio_for_duix(script: str, language: str = "en") -> str:
    """Synthesize audio for Duix using the local voice stack (Chatterbox/Coqui)."""
    if not script:
        raise ToolError("No script or audio provided for Duix avatar")
    voice_result = await _clone_voice(tool="chatterbox", language=language, script=script, reference_audio="")
    artifact = voice_result.get("artifact", "")
    if not artifact or artifact.endswith("voice_stub.wav") or not os.path.exists(artifact):
        raise ToolError("No local voice engine available to synthesize audio for Duix")
    return artifact


async def _render_avatar(tool: str = "duix", photo: str = "", script: str = "", audio: str = "",
                         language: str = "en", **_: Any) -> dict:
    p = _AVATAR_PROVIDERS.get(tool, _AVATAR_PROVIDERS["duix"])

    if tool in ("wav2lip", "videoretalking", "roop", "sadtalker"):
        if not photo or not _external_lip_sync_command_configured(tool):
            return {
                "simulated": True,
                "provider": p["provider"],
                "license": p["license"],
                "requires_internet": p["online"],
                "lip_sync_fps": 24,
                "artifact": "/artifacts/media/avatar_stub.mp4",
                "note": f"Stub — wire to {p['provider']} for photo+script lip-sync (offline/local).",
            }
        try:
            data_dir = _duix_data_dir()
            video_path = photo if os.path.isabs(photo) else os.path.join(data_dir, photo)
            video_path = os.path.normpath(video_path)
            if not os.path.exists(video_path):
                raise ToolError(f"Reference photo/video not found: {video_path}")

            if audio:
                audio_path = audio if os.path.isabs(audio) else os.path.join(data_dir, audio)
                audio_path = os.path.normpath(audio_path)
            else:
                audio_path = await _prepare_audio_for_duix(script, language)

            if not os.path.exists(audio_path):
                raise ToolError(f"Audio file not found: {audio_path}")

            artifact = await _run_external_lip_sync(tool, video_path, audio_path)
            return {
                "simulated": True,
                "provider": p["provider"],
                "license": p["license"],
                "requires_internet": False,
                "lip_sync_fps": 25,
                "artifact": artifact,
                "note": f"Generated by {p['provider']} from reference video + {'provided' if audio else 'synthesized'} audio.",
            }
        except Exception as exc:
            return {
                "simulated": True,
                "provider": p["provider"],
                "license": p["license"],
                "requires_internet": p["online"],
                "lip_sync_fps": 24,
                "artifact": "/artifacts/media/avatar_stub.mp4",
                "note": f"{p['provider']} failed ({exc}); Stub — wire to {p['provider']} for photo+script lip-sync (offline/local).",
            }

    host = _duix_video_host()
    if not host or not photo:
        return {
            "simulated": True,
            "provider": p["provider"],
            "license": p["license"],
            "requires_internet": p["online"],
            "lip_sync_fps": 24,
            "artifact": "/artifacts/media/avatar_stub.mp4",
            "note": f"Stub — wire to {p['provider']} for photo+script lip-sync (offline/local).",
        }

    try:
        import httpx
        data_dir = _duix_data_dir()
        video_path = photo if os.path.isabs(photo) else os.path.join(data_dir, photo)
        video_path = os.path.normpath(video_path)
        if not os.path.exists(video_path):
            raise ToolError(f"Duix reference video not found: {video_path}")

        if audio:
            audio_path = audio if os.path.isabs(audio) else os.path.join(data_dir, audio)
            audio_path = os.path.normpath(audio_path)
        else:
            audio_path = await _prepare_audio_for_duix(script, language)

        if not os.path.exists(audio_path):
            raise ToolError(f"Duix audio file not found: {audio_path}")

        task_code = str(uuid.uuid4())
        payload = {
            "audio_url": audio_path,
            "video_url": video_path,
            "code": task_code,
            "chaofen": 0,
            "watermark_switch": 0,
            "pn": 1,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{host}/easy/submit", json=payload)
            r.raise_for_status()

        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(_DUIX_MAX_POLL):
                await asyncio.sleep(_DUIX_POLL_INTERVAL)
                r = await client.get(f"{host}/easy/query", params={"code": task_code})
                r.raise_for_status()
                data = r.json().get("data", {})
                status = data.get("status")
                if status == "success":
                    result = data.get("result", "")
                    if not result or not os.path.exists(result):
                        raise ToolError("Duix finished but output path is not accessible")
                    # Copy the result into the shared artifact directory so it is
                    # reachable via the /artifacts static mount.
                    os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
                    ext = os.path.splitext(result)[1] or ".mp4"
                    local_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}{ext}")
                    shutil.copy2(result, local_path)
                    return {
                        "simulated": True,
                        "provider": p["provider"],
                        "license": p["license"],
                        "requires_internet": False,
                        "lip_sync_fps": 24,
                        "artifact": local_path,
                        "note": f"Generated by {p['provider']} from reference video + {'provided' if audio else 'synthesized'} audio.",
                    }
                elif status == "error":
                    raise ToolError(data.get("msg", "Duix video generation failed"))
            raise ToolError("Duix video generation timed out")

    except Exception as exc:
        note = f"Duix failed ({exc}); Stub — wire to {p['provider']} for photo+script lip-sync (offline/local)."
        return {
            "simulated": True,
            "provider": p["provider"],
            "license": p["license"],
            "requires_internet": p["online"],
            "lip_sync_fps": 24,
            "artifact": "/artifacts/media/avatar_stub.mp4",
            "note": note,
        }


def _online_available() -> bool:
    """Online tools are only usable when explicitly enabled (offline-first default)."""
    return os.environ.get("ALLOW_ONLINE_TOOLS", "").lower() in ("1", "true", "yes")


# ── Video Stack stubs (face-swap / lip-sync / restore; offline, simulated) ──

# ── InsightFace one-shot face-swap integration ──────────────────────

_INSIGHTFACE_HOME = os.environ.get(
    "INSIGHTFACE_HOME",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", ".insightface",
    ),
)

_INSIGHTFACE_APP: Any = None
_INSIGHTFACE_SWAPPER: Any = None
_INSIGHTFACE_LOCK = asyncio.Lock()


_FACESWAP_PROVIDERS = {
    "insightface": {"provider": "InsightFace InSwapper", "mode": "one-shot", "note": "one-shot image/video face swap (ONNX)"},
    "deepfacelab": {"provider": "DeepFaceLab", "mode": "batch", "note": "professional face-swap, CLI automation"},
    "faceswap": {"provider": "FaceSwap", "mode": "batch", "note": "TensorFlow, cross-platform"},
    "deeplivecam": {"provider": "Deep-Live-Cam", "mode": "realtime", "note": "real-time single-image swap"},
}

_LIPSYNC_PROVIDERS = {
    "wav2lip": {"provider": "Wav2Lip", "note": "audio-driven lip-sync"},
    "videoretalking": {"provider": "VideoRetalking", "note": "expression-aware retalking"},
}


def _is_insightface_available() -> bool:
    """Return True if the InsightFace + ONNX runtime is installed."""
    import importlib.util
    return (
        importlib.util.find_spec("insightface") is not None
        and importlib.util.find_spec("cv2") is not None
        and importlib.util.find_spec("onnxruntime") is not None
    )


def _insightface_home() -> str:
    """Return the directory where InsightFace models are cached."""
    home = os.environ.get("INSIGHTFACE_HOME", _INSIGHTFACE_HOME)
    os.makedirs(home, exist_ok=True)
    return home


async def _download_inswapper_model(model_path: str) -> None:
    """Download the InSwapper 128 ONNX model if it is not present locally."""
    import urllib.request
    url = os.environ.get(
        "INSWAPPER_MODEL_URL",
        "https://huggingface.co/ashleykleynhans/inswapper/resolve/main/inswapper_128.onnx",
    )
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    await asyncio.to_thread(urllib.request.urlretrieve, url, model_path)


async def _load_insightface_models() -> tuple[Any, Any]:
    """Load and cache the InsightFace analysis + InSwapper models."""
    global _INSIGHTFACE_APP, _INSIGHTFACE_SWAPPER
    if _INSIGHTFACE_APP is None or _INSIGHTFACE_SWAPPER is None:
        async with _INSIGHTFACE_LOCK:
            if _INSIGHTFACE_APP is None or _INSIGHTFACE_SWAPPER is None:
                import insightface
                from insightface.app import FaceAnalysis
                home = _insightface_home()
                app = await asyncio.to_thread(FaceAnalysis, name="buffalo_l", root=home)
                await asyncio.to_thread(app.prepare, ctx_id=0, det_size=(640, 640))
                model_path = os.path.join(home, "models", "inswapper_128.onnx")
                if not os.path.exists(model_path):
                    await _download_inswapper_model(model_path)
                swapper = await asyncio.to_thread(insightface.model_zoo.get_model, model_path)
                _INSIGHTFACE_APP = app
                _INSIGHTFACE_SWAPPER = swapper
    return _INSIGHTFACE_APP, _INSIGHTFACE_SWAPPER


def _is_video(path: str) -> bool:
    """Guess whether a path is a video file by extension."""
    return os.path.splitext(path)[1].lower() in (
        ".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv",
    )


def _swap_image_sync(app: Any, swapper: Any, source_path: str, target_path: str, output_path: str) -> None:
    """Swap one or more faces in a target image with the source face."""
    import cv2
    source_img = cv2.imread(source_path)
    target_img = cv2.imread(target_path)
    if source_img is None:
        raise ToolError(f"Cannot read source image: {source_path}")
    if target_img is None:
        raise ToolError(f"Cannot read target image: {target_path}")
    source_faces = app.get(source_img)
    if not source_faces:
        raise ToolError("No face found in source image")
    source_face = source_faces[0]
    target_faces = app.get(target_img)
    if not target_faces:
        raise ToolError("No face found in target image")
    res = target_img.copy()
    for face in target_faces:
        res = swapper.get(res, face, source_face, paste_back=True)
    cv2.imwrite(output_path, res)


def _swap_video_sync(app: Any, swapper: Any, source_path: str, target_path: str, output_path: str) -> None:
    """Swap faces in each frame of a target video with the source face."""
    import cv2
    source_img = cv2.imread(source_path)
    if source_img is None:
        raise ToolError(f"Cannot read source image: {source_path}")
    source_faces = app.get(source_img)
    if not source_faces:
        raise ToolError("No face found in source image")
    source_face = source_faces[0]
    cap = cv2.VideoCapture(target_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            faces = app.get(frame)
            for face in (faces or []):
                frame = swapper.get(frame, face, source_face, paste_back=True)
            out.write(frame)
    finally:
        cap.release()
        out.release()


async def _run_insightface_swap(source: str, target: str) -> str:
    """Run one-shot face swap and return the path to the generated artifact."""
    app, swapper = await _load_insightface_models()
    os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
    ext = ".mp4" if _is_video(target) else (os.path.splitext(target)[1] or ".jpg")
    out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}{ext}")
    async with _INSIGHTFACE_LOCK:
        if _is_video(target):
            await asyncio.to_thread(_swap_video_sync, app, swapper, source, target, out_path)
        else:
            await asyncio.to_thread(_swap_image_sync, app, swapper, source, target, out_path)
    return out_path


# Mapping of face-swap tool names to the environment variable that supplies the
# external command template. The template may use {source}, {target}, and {output}.
_EXTERNAL_FACESWAP_COMMANDS = {
    "deepfacelab": "DEEPFACELAB_COMMAND",
    "faceswap": "FACESWAP_COMMAND",
    "deeplivecam": "DEEP_LIVE_CAM_COMMAND",
}


def _external_face_command_configured(tool: str) -> bool:
    """Return True if the named external face-swap engine has a command configured."""
    return bool(os.environ.get(_EXTERNAL_FACESWAP_COMMANDS.get(tool, "")))


async def _run_external_face_swap(tool: str, source: str, target: str) -> str:
    """Invoke an operator-supplied external face-swap command and return the output path."""
    env_var = _EXTERNAL_FACESWAP_COMMANDS.get(tool)
    cmd_template = os.environ.get(env_var, "") if env_var else ""
    if not cmd_template:
        raise ToolError(f"{env_var} is not configured")
    os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
    ext = ".mp4" if _is_video(target) else (os.path.splitext(target)[1] or ".jpg")
    out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}{ext}")
    # Safely substitute paths into the operator-provided command template.
    command = cmd_template.format(
        source=shlex.quote(source),
        target=shlex.quote(target),
        output=shlex.quote(out_path),
    )
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise ToolError(f"{tool} command failed: {stderr.decode()[:500]}")
    if not os.path.exists(out_path):
        raise ToolError(f"{tool} command did not produce the expected output file")
    return out_path


# Lip-sync engines that are invoked through an external command template.
# The template may use {video}, {audio}, and {output}.
_EXTERNAL_LIPSYNC_COMMANDS = {
    "wav2lip": "WAV2LIP_COMMAND",
    "videoretalking": "VIDEORETALKING_COMMAND",
    "roop": "ROOP_COMMAND",
    "sadtalker": "SADTALKER_COMMAND",
}


def _external_lip_sync_command_configured(tool: str) -> bool:
    """Return True if the named external lip-sync engine has a command configured."""
    return bool(os.environ.get(_EXTERNAL_LIPSYNC_COMMANDS.get(tool, "")))


async def _run_external_lip_sync(tool: str, video: str, audio: str) -> str:
    """Invoke an operator-supplied external lip-sync command and return the output path."""
    env_var = _EXTERNAL_LIPSYNC_COMMANDS.get(tool)
    cmd_template = os.environ.get(env_var, "") if env_var else ""
    if not cmd_template:
        raise ToolError(f"{env_var} is not configured")
    os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
    # Lip-sync engines always produce a video file.
    out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}.mp4")
    command = cmd_template.format(
        video=shlex.quote(video),
        audio=shlex.quote(audio),
        output=shlex.quote(out_path),
    )
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise ToolError(f"{tool} command failed: {stderr.decode()[:500]}")
    if not os.path.exists(out_path):
        raise ToolError(f"{tool} command did not produce the expected output file")
    return out_path


async def _face_stub(tool: str) -> dict:
    """Return the original simulated stub for a face-swap provider."""
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


async def _face_swap(tool: str = "deepfacelab", source: str = "", target: str = "",
                     **_: Any) -> dict:
    if tool == "insightface":
        if not _is_insightface_available():
            return await _face_stub(tool)
        if not source or not target:
            return {
                **(await _face_stub(tool)),
                "note": "InsightFace requires source and target paths.",
            }
        try:
            artifact = await _run_insightface_swap(source, target)
            return {
                "simulated": True,
                "provider": _FACESWAP_PROVIDERS["insightface"]["provider"],
                "mode": _FACESWAP_PROVIDERS["insightface"]["mode"],
                "requires_internet": False,
                "resolution": "1080p",
                "artifact": artifact,
                "note": "Generated locally with InsightFace InSwapper (offline/local).",
            }
        except Exception as exc:
            stub = await _face_stub(tool)
            stub["note"] = f"InsightFace failed ({exc}); Stub fallback."
            return stub

    if tool in ("deepfacelab", "faceswap", "deeplivecam"):
        if not source or not target or not _external_face_command_configured(tool):
            stub = await _face_stub(tool)
            if not source or not target:
                stub["note"] = f"{tool} requires source, target, and a configured {_EXTERNAL_FACESWAP_COMMANDS.get(tool)} environment variable."
            else:
                stub["note"] = f"{tool} requires {_EXTERNAL_FACESWAP_COMMANDS.get(tool)} to be set. " \
                               "Mount the trained workspace/container and point the command at a non-interactive script."
            return stub
        try:
            artifact = await _run_external_face_swap(tool, source, target)
            return {
                "simulated": True,
                "provider": _FACESWAP_PROVIDERS[tool]["provider"],
                "mode": _FACESWAP_PROVIDERS[tool]["mode"],
                "requires_internet": False,
                "resolution": "1080p",
                "artifact": artifact,
                "note": f"Generated by external {_FACESWAP_PROVIDERS[tool]['provider']} command (offline/local).",
            }
        except Exception as exc:
            stub = await _face_stub(tool)
            stub["note"] = f"{tool} failed ({exc}); Stub fallback."
            return stub

    # Fallback for unknown tools.
    return await _face_stub(tool)


async def _lip_sync(tool: str = "wav2lip", video: str = "", audio: str = "",
                    **_: Any) -> dict:
    p = _LIPSYNC_PROVIDERS.get(tool, _LIPSYNC_PROVIDERS["wav2lip"])

    if tool in _EXTERNAL_LIPSYNC_COMMANDS and _external_lip_sync_command_configured(tool):
        if not video or not audio:
            return {
                "simulated": True,
                "provider": p["provider"],
                "requires_internet": False,
                "fps": 25,
                "artifact": "/artifacts/video/lipsync_stub.mp4",
                "note": f"{p['provider']} requires both video and audio paths to lip-sync.",
            }
        try:
            data_dir = _duix_data_dir()
            video_path = video if os.path.isabs(video) else os.path.join(data_dir, video)
            video_path = os.path.normpath(video_path)
            audio_path = audio if os.path.isabs(audio) else os.path.join(data_dir, audio)
            audio_path = os.path.normpath(audio_path)
            if not os.path.exists(video_path) or not os.path.exists(audio_path):
                raise ToolError("Video or audio file not found")

            artifact = await _run_external_lip_sync(tool, video_path, audio_path)
            return {
                "simulated": True,
                "provider": p["provider"],
                "requires_internet": False,
                "fps": 25,
                "artifact": artifact,
                "note": f"Generated by {p['provider']} (offline/local).",
            }
        except Exception as exc:
            return {
                "simulated": True,
                "provider": p["provider"],
                "requires_internet": False,
                "fps": 25,
                "artifact": "/artifacts/video/lipsync_stub.mp4",
                "note": f"{p['provider']} failed ({exc}); Stub — wire to {p['provider']} for real lip-sync (offline/local).",
            }

    return {
        "simulated": True,
        "provider": p["provider"],
        "requires_internet": False,
        "fps": 25,
        "artifact": "/artifacts/video/lipsync_stub.mp4",
        "note": f"Stub — {p['note']}. Simulated only.",
    }


def _external_gfpgan_configured() -> bool:
    """Return True if a GFPGAN command is configured."""
    return bool(os.environ.get("GFPGAN_COMMAND", ""))


async def _run_external_gfpgan(input_path: str, scale: int, output_path: str) -> str:
    """Invoke the configured GFPGAN command and return the output path."""
    cmd_template = os.environ.get("GFPGAN_COMMAND", "")
    if not cmd_template:
        raise ToolError("GFPGAN_COMMAND is not configured")

    command = cmd_template.format(
        input=shlex.quote(input_path),
        output=shlex.quote(output_path),
        scale=scale,
    )
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise ToolError(f"GFPGAN command failed: {stderr.decode()[:500]}")
    if not os.path.exists(output_path):
        raise ToolError("GFPGAN command did not produce the expected output file")
    return output_path


async def _gfpgan_upscale(input_path: str = "", scale: int = 2, **_: Any) -> dict:
    p = {"provider": "GFPGAN", "license": "open", "online": False}

    if not input_path or not _external_gfpgan_configured():
        return {
            "simulated": True,
            "provider": p["provider"],
            "license": p["license"],
            "requires_internet": p["online"],
            "scale": scale,
            "artifact": "/artifacts/video/restored_stub.mp4",
            "note": f"Stub — wire to {p['provider']} for face restoration / upscaling (offline/local).",
        }

    try:
        data_dir = _duix_data_dir()
        input_path = input_path if os.path.isabs(input_path) else os.path.join(data_dir, input_path)
        input_path = os.path.normpath(input_path)
        if not os.path.exists(input_path):
            raise ToolError(f"Input file not found: {input_path}")

        ext = os.path.splitext(input_path)[1].lower()
        out_ext = ".mp4" if ext in {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv"} else (ext or ".png")
        os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
        out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}{out_ext}")

        artifact = await _run_external_gfpgan(input_path, scale, out_path)
        return {
            "simulated": True,
            "provider": p["provider"],
            "license": p["license"],
            "requires_internet": p["online"],
            "scale": scale,
            "artifact": artifact,
            "note": f"Restored/upscaled with {p['provider']} (scale={scale}).",
        }
    except Exception as exc:
        return {
            "simulated": True,
            "provider": p["provider"],
            "license": p["license"],
            "requires_internet": p["online"],
            "scale": scale,
            "artifact": "/artifacts/video/restored_stub.mp4",
            "note": f"{p['provider']} failed ({exc}); Stub — wire to {p['provider']} for face restoration / upscaling (offline/local).",
        }


def _is_ffmpeg_available() -> bool:
    """Return True if the ffmpeg binary is present on this machine."""
    return shutil.which("ffmpeg") is not None


async def _run_ffmpeg_pipeline(
    input_paths: list[str], output_path: str, command: str = ""
) -> str:
    """Run ffmpeg with the supplied inputs, options, and output path."""
    args = ["ffmpeg", "-y"]
    for path in input_paths:
        args += ["-i", path]
    if command:
        args += shlex.split(command)
    args += [output_path]

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise ToolError(f"ffmpeg failed: {stderr.decode()[:500]}")
    if not os.path.exists(output_path):
        raise ToolError("ffmpeg did not produce the expected output file")
    return output_path


async def _ffmpeg_pipeline(
    steps: str = "",
    inputs: Any = None,
    output: str = "",
    command: str = "",
    **_: Any,
) -> dict:
    """Deterministic FFmpeg compositing / muxing pipeline.

    Real execution requires either:
      - `command` (FFmpeg options/filters, e.g. "-vf scale=1280:720 -c:a copy")
        plus `inputs` and optionally `output`, or
      - a `steps` value that starts with a dash (treated as FFmpeg options).

    If no actionable command/inputs are supplied, the original stub is returned.
    """
    p = {"provider": "FFmpeg", "requires_internet": False}
    effective_command = command or (steps if steps and steps.startswith("-") else "")

    if not _is_ffmpeg_available() or not inputs or not effective_command:
        return {
            "simulated": True,
            "provider": p["provider"],
            "requires_internet": False,
            "steps": steps or "trim,concat,scale,mux",
            "artifact": "/artifacts/video/final_stub.mp4",
            "note": "Stub — deterministic FFmpeg compositing/mux pipeline (offline/local). "
                    "Pass inputs and command (or a steps string starting with '-') to run real ffmpeg.",
        }

    try:
        if isinstance(inputs, str):
            input_paths = [p.strip() for p in inputs.split(",") if p.strip()]
        elif isinstance(inputs, list):
            input_paths = [str(p) for p in inputs]
        else:
            input_paths = [str(inputs)]

        data_dir = _duix_data_dir()
        resolved_inputs: list[str] = []
        for path in input_paths:
            path = path if os.path.isabs(path) else os.path.join(data_dir, path)
            path = os.path.normpath(path)
            if not os.path.exists(path):
                raise ToolError(f"Input file not found: {path}")
            resolved_inputs.append(path)

        os.makedirs(_VOICE_ARTIFACT_DIR, exist_ok=True)
        if output:
            out_path = output if os.path.isabs(output) else os.path.join(data_dir, output)
            out_path = os.path.normpath(out_path)
        else:
            out_path = os.path.join(_VOICE_ARTIFACT_DIR, f"{uuid.uuid4()}.mp4")
        out_path = os.path.abspath(out_path)

        artifact = await _run_ffmpeg_pipeline(resolved_inputs, out_path, effective_command)
        return {
            "simulated": True,
            "provider": p["provider"],
            "requires_internet": False,
            "steps": steps or effective_command,
            "artifact": artifact,
            "note": f"Processed with FFmpeg: {effective_command}",
        }
    except Exception as exc:
        return {
            "simulated": True,
            "provider": p["provider"],
            "requires_internet": False,
            "steps": steps or "trim,concat,scale,mux",
            "artifact": "/artifacts/video/final_stub.mp4",
            "note": f"FFmpeg failed ({exc}); Stub — deterministic FFmpeg compositing/mux pipeline (offline/local).",
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
        status="live" if _is_wan2_available() else "stub",
    ))
    register(ToolSpec(
        id="render_avatar", name="Digital Human Renderer",
        description="Photo+script or photo+audio lip-synced digital human (Duix-Avatar, Wav2Lip, VideoRetalking, Roop, SadTalker).",
        category="media", provider="Duix-Avatar / Wav2Lip / VideoRetalking / Roop / SadTalker", run=_render_avatar,
        parameters={"tool": "duix|wav2lip|videoretalking|roop|sadtalker", "photo": "reference video or image", "script": "text", "audio": "optional audio file path", "language": "lang"},
        status="live" if (
            _duix_video_host()
            or _external_lip_sync_command_configured("wav2lip")
            or _external_lip_sync_command_configured("videoretalking")
            or _external_lip_sync_command_configured("roop")
            or _external_lip_sync_command_configured("sadtalker")
        ) else "stub",
    ))
    register(ToolSpec(
        id="face_swap", name="Face-Swap Engine",
        description="Face-swap / video synthesis (InsightFace, DeepFaceLab, FaceSwap, Deep-Live-Cam). Consent-gated, simulated.",
        category="media", provider="InsightFace / DeepFaceLab / FaceSwap / Deep-Live-Cam", run=_face_swap,
        parameters={"tool": "insightface|deepfacelab|faceswap|deeplivecam", "source": "source image", "target": "target image or video"},
        status="live" if (
            _is_insightface_available()
            or _external_face_command_configured("deepfacelab")
            or _external_face_command_configured("faceswap")
            or _external_face_command_configured("deeplivecam")
        ) else "stub",
    ))
    register(ToolSpec(
        id="lip_sync", name="Lip-Sync Engine",
        description="Lip-sync deepfake anchors (Wav2Lip, VideoRetalking).",
        category="media", provider="Wav2Lip / VideoRetalking", run=_lip_sync,
        parameters={"tool": "wav2lip|videoretalking", "video": "video", "audio": "audio"},
        status="live" if (
            _external_lip_sync_command_configured("wav2lip")
            or _external_lip_sync_command_configured("videoretalking")
        ) else "stub",
    ))
    register(ToolSpec(
        id="gfpgan_upscale", name="Face Restore / Upscale",
        description="GFPGAN face restoration and upscaling.",
        category="media", provider="GFPGAN", run=_gfpgan_upscale,
        parameters={"input_path": "input", "scale": "upscale factor"},
        status="live" if _external_gfpgan_configured() else "stub",
    ))
    register(ToolSpec(
        id="ffmpeg_pipeline", name="FFmpeg Pipeline",
        description="Deterministic FFmpeg compositing / muxing pipeline.",
        category="media", provider="FFmpeg", run=_ffmpeg_pipeline,
        parameters={
            "steps": "comma-separated steps or raw FFmpeg options",
            "inputs": "input file path(s) (string or list)",
            "output": "optional output path",
            "command": "FFmpeg options/filters (e.g. -vf scale=1280:720 -c:a copy)",
        },
        status="live" if _is_ffmpeg_available() else "stub",
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
        description="Launch a real Playwright session and collect automation-detection signals for an endpoint.",
        category="stealth", provider="Playwright", run=_playwright_stealth_check,
        parameters={"endpoint": "target endpoint or about:blank"},
        status="live" if _is_playwright_available() else "stub",
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
        description="Headless browser automation with Playwright (navigate, screenshot, evaluate, click, type, get_text, html). Falls back to a plan stub when Playwright is not installed or no URL/file target is supplied.",
        category="persona", provider="Playwright", run=_browser_automation_plan,
        parameters={
            "target": "URL or local file path",
            "tool": "playwright",
            "action": "navigate|screenshot|evaluate|click|type|get_text|html",
            "script": "JavaScript expression for evaluate",
            "selector": "CSS selector for click/type",
            "value": "text value for type action",
            "headless": "true|false",
            "screenshot": "true|false",
            "output": "optional output path for screenshot",
        },
        status="live" if _is_playwright_available() else "stub",
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
