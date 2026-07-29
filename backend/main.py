"""TIER 1 — Strategic Brain: Multi-Agent AI Orchestration Platform."""

from __future__ import annotations

import base64
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.agents import ALL_AGENTS
from backend.agents.workers import ALL_WORKERS
from backend.agents.intelligence_crew import INTELLIGENCE_CREW, LANGUAGES, REGIONS
from backend.agents.media_crew import (
    AVATAR_TOOLS,
    DURATIONS,
    MEDIA_CREW,
    TONES,
    VIDEO_TOOLS,
    VOICE_TOOLS,
)
from backend.agents.media_crew import LANGUAGES as MEDIA_LANGUAGES
from backend.agents.video_stack import (
    LIPSYNC_TOOLS,
    STYLES,
    SWAP_TOOLS,
    VIDEO_STACK,
)
from backend.agents.video_stack import DURATIONS as VIDEO_DURATIONS
from backend.agents.cyber_crew import (
    CYBER_CREW,
    DAST_TOOLS,
    ENGAGEMENTS,
    SCAN_TOOLS,
)
from backend.agents.persona_crew import (
    PERSONA_CREW,
    PLATFORMS,
    REGIONS as PERSONA_REGIONS,
    SCENARIOS as PERSONA_SCENARIOS,
)
from backend.agents.infrastructure_crew import (
    INFRASTRUCTURE_CREW, MODEM_TYPES, CARRIERS, SCENARIOS as INFRA_SCENARIOS,
)
from backend.exercises.scenarios import get_all_scenarios, get_scenario, get_scenarios_by_difficulty
from backend.tools import registry
from backend.pipeline import (
    cyber_crew,
    intelligence_crew,
    ledger_scheduler,
    legal_ledger,
    media_crew,
    persona_crew,
    infrastructure_crew,
    video_stack,
)
from backend.pipeline.compliance import ComplianceRecorder, legal_proxy_enabled
from backend.pipeline.orchestrator import (
    cancel_pipeline,
    get_config,
    is_llm_configured,
    memory,
    route_pipeline,
)
from backend.tools.analysis import get_all_tools, get_tools_for_agent

compliance_recorder = ComplianceRecorder()

app = FastAPI(
    title="TIER 1 — Strategic Brain",
    description="Multi-agent AI orchestration for cybersecurity analysis",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _start_ledger_scheduler() -> None:
    ledger_scheduler.start()


# ── Health ──────────────────────────────────────────────────────────


@app.get("/api/health")
def health():
    config = get_config()
    return {
        "status": "ok",
        "service": "tier1-strategic-brain",
        "llm_configured": config["llm_configured"],
        "stats": memory.get_stats(),
        "backends": config["backends"],
        "default_framework": config["default_framework"],
    }


# ── Config ─────────────────────────────────────────────────────────


@app.get("/api/config")
def config_endpoint():
    return get_config()


# ── Agent metadata ─────────────────────────────────────────────────


@app.get("/api/agents")
def list_agents():
    return {
        "agents": [a.to_meta() for a in ALL_AGENTS],
        "pipeline_order": [a.id for a in ALL_AGENTS],
    }


@app.get("/api/agents/{agent_id}")
def get_agent(agent_id: str):
    for a in ALL_AGENTS:
        if a.id == agent_id:
            return {
                **a.to_meta(),
                "tools_detail": get_tools_for_agent(agent_id),
            }
    raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")


# ── Tools ──────────────────────────────────────────────────────────


@app.get("/api/tools")
def list_tools():
    return {"tools": get_all_tools()}


# ── Tool registry (executable, extensible per-tier) ────────────────


@app.get("/api/registry")
def registry_endpoint():
    return {
        "tools": [t.to_meta() for t in registry.all_tools()],
        "workers": [w.to_meta() for w in ALL_WORKERS],
    }


# ── Pipeline execution ─────────────────────────────────────────────


class PipelineRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1)
    framework: str = Field(default="", description="autogen | langgraph | direct")
    backend: str = Field(default="", description="ollama | openai (auto-detect if empty)")


@app.post("/api/pipeline/run")
async def pipeline_run(req: PipelineRequest):
    generator = route_pipeline(
        req.task,
        req.session_id,
        framework=req.framework,
        backend=req.backend,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── TIER 2 — Intelligence Crew ─────────────────────────────────────


@app.get("/api/intelligence/config")
def intelligence_config():
    return {
        "agents": [a.to_meta() for a in INTELLIGENCE_CREW],
        "regions": REGIONS,
        "languages": LANGUAGES,
        "config": get_config(),
    }


class IntelligenceRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    region: str = Field(..., min_length=1)
    language: str = Field(default="en")
    session_id: str = Field(..., min_length=1)
    backend: str = Field(default="", description="ollama | openai (auto-detect if empty)")


@app.post("/api/intelligence/plan")
async def intelligence_plan(req: IntelligenceRequest):
    generator = intelligence_crew.route(
        req.query,
        req.region,
        req.language,
        req.session_id,
        backend=req.backend,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── TIER 2 — Media Crew (Duix-Avatar Pipeline) ─────────────────────


@app.get("/api/media/config")
def media_config():
    return {
        "agents": [a.to_meta() for a in MEDIA_CREW],
        "tones": TONES,
        "durations": DURATIONS,
        "languages": MEDIA_LANGUAGES,
        "voice_tools": VOICE_TOOLS,
        "video_tools": VIDEO_TOOLS,
        "avatar_tools": AVATAR_TOOLS,
        "config": get_config(),
    }


class MediaRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=2000)
    tone: str = Field(default="Professional")
    language: str = Field(default="English")
    language_code: str = Field(default="en")
    duration: str = Field(default="60 seconds")
    audience: str = Field(default="General public")
    voice_tool: str = Field(default="chatterbox")
    video_tool: str = Field(default="wan2")
    avatar_tool: str = Field(default="duix")
    session_id: str = Field(..., min_length=1)
    backend: str = Field(default="", description="ollama | openai (auto-detect if empty)")


@app.post("/api/media/produce")
async def media_produce(req: MediaRequest):
    inp = {
        "topic": req.topic,
        "tone": req.tone,
        "language": req.language,
        "language_code": req.language_code,
        "duration": req.duration,
        "audience": req.audience,
        "voice_tool": req.voice_tool,
        "video_tool": req.video_tool,
        "avatar_tool": req.avatar_tool,
    }
    generator = media_crew.route(inp, req.session_id, backend=req.backend)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── TIER 2 — Video Stack (face-swap / lip-sync) ────────────────────


@app.get("/api/video/config")
def video_config():
    return {
        "agents": [a.to_meta() for a in VIDEO_STACK],
        "styles": STYLES,
        "durations": VIDEO_DURATIONS,
        "swap_tools": SWAP_TOOLS,
        "lipsync_tools": LIPSYNC_TOOLS,
        "legal_proxy_enabled": legal_proxy_enabled(),
        "config": get_config(),
    }


class VideoRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=2000)
    style: str = Field(default="Documentary")
    duration: str = Field(default="60 seconds")
    swap_tool: str = Field(default="deepfacelab")
    lipsync_tool: str = Field(default="wav2lip")
    consent: bool = Field(default=False, description="Lawful consent attested for any real likeness")
    authorization_ref: str = Field(
        default="", max_length=200,
        description="Legal-proxy authorization reference (case no. / signed-release ID / court order)",
    )
    approver: str = Field(
        default="", max_length=200,
        description="Identity of the approving legal-proxy reviewer",
    )
    session_id: str = Field(..., min_length=1)
    backend: str = Field(default="", description="ollama | openai (auto-detect if empty)")


@app.post("/api/video/plan")
async def video_plan(req: VideoRequest):
    inp = {
        "topic": req.topic,
        "style": req.style,
        "duration": req.duration,
        "swap_tool": req.swap_tool,
        "lipsync_tool": req.lipsync_tool,
        "consent": req.consent,
        "authorization_ref": req.authorization_ref,
        "approver": req.approver,
    }
    generator = video_stack.route(inp, req.session_id, backend=req.backend)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── TIER 2 — Cyber Crew (defensive security) ───────────────


@app.get("/api/cyber/config")
def cyber_config():
    return {
        "agents": [a.to_meta() for a in CYBER_CREW],
        "engagements": ENGAGEMENTS,
        "scan_tools": SCAN_TOOLS,
        "dast_tools": DAST_TOOLS,
        "legal_proxy_enabled": legal_proxy_enabled(),
        "config": get_config(),
    }


class CyberRequest(BaseModel):
    target: str = Field(..., min_length=1, max_length=2000)
    engagement: str = Field(default="External Network Pentest")
    scan_tool: str = Field(default="nmap")
    authorized: bool = Field(
        default=False, description="Written scope authorization attested for this engagement"
    )
    authorization_ref: str = Field(
        default="", max_length=200,
        description="Legal-proxy authorization reference (case no. / signed-release ID / court order)",
    )
    approver: str = Field(
        default="", max_length=200,
        description="Identity of the approving legal-proxy reviewer",
    )
    session_id: str = Field(..., min_length=1)
    backend: str = Field(default="", description="ollama | openai (auto-detect if empty)")


@app.post("/api/cyber/plan")
async def cyber_plan(req: CyberRequest):
    inp = {
        "target": req.target,
        "engagement": req.engagement,
        "scan_tool": req.scan_tool,
        "authorized": req.authorized,
        "authorization_ref": req.authorization_ref,
        "approver": req.approver,
    }
    generator = cyber_crew.route(inp, req.session_id, backend=req.backend)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── TIER 3 — Persona Orchestration (simulated) ─────────────


@app.get("/api/persona/config")
def persona_config():
    return {
        "agents": [a.to_meta() for a in PERSONA_CREW],
        "scenarios": PERSONA_SCENARIOS,
        "platforms": PLATFORMS,
        "regions": PERSONA_REGIONS,
        "legal_proxy_enabled": legal_proxy_enabled(),
        "config": get_config(),
    }


class PersonaRequest(BaseModel):
    objective: str = Field(..., min_length=1, max_length=2000)
    scenario: str = Field(default="Detection Research (blue-team)")
    platform: str = Field(default="lab-dashboard")
    region: str = Field(default="pk-urdu")
    authorized: bool = Field(
        default=False, description="Authorized research/training context attested (lab-only)"
    )
    authorization_ref: str = Field(
        default="", max_length=200,
        description="Legal-proxy authorization reference (case no. / signed authorization / order ID)",
    )
    approver: str = Field(
        default="", max_length=200,
        description="Identity of the approving legal-proxy reviewer",
    )
    session_id: str = Field(..., min_length=1)
    backend: str = Field(default="", description="ollama | openai (auto-detect if empty)")


@app.post("/api/persona/plan")
async def persona_plan(req: PersonaRequest):
    inp = {
        "objective": req.objective,
        "scenario": req.scenario,
        "platform": req.platform,
        "region": req.region,
        "authorized": req.authorized,
        "authorization_ref": req.authorization_ref,
        "approver": req.approver,
    }
    generator = persona_crew.route(inp, req.session_id, backend=req.backend)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── TIER 4 — Infrastructure (simulated) ────────────────────────────
@app.get("/api/infrastructure/config")
def infrastructure_config():
    return {
        "agents": [a.to_meta() for a in INFRASTRUCTURE_CREW],
        "scenarios": INFRA_SCENARIOS,
        "modem_types": MODEM_TYPES,
        "carriers": CARRIERS,
        "legal_proxy_enabled": legal_proxy_enabled(),
        "config": get_config(),
    }


class InfrastructureRequest(BaseModel):
    objective: str = Field(..., min_length=1, max_length=2000)
    scenario: str = ""
    modem_type: str = ""
    carrier: str = ""
    authorized: bool = False
    authorization_ref: str = ""
    approver: str = ""
    session_id: str = Field(..., min_length=1)
    backend: str = ""


@app.post("/api/infrastructure/plan")
async def infrastructure_plan(req: InfrastructureRequest):
    inp = req.model_dump()
    generator = infrastructure_crew.route(inp, req.session_id, backend=req.backend)
    return StreamingResponse(
        generator, media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive",
                 "X-Accel-Buffering": "no"},
    )


# ── Compliance & audit ──────────────────────────────────────────────


@app.get("/api/compliance/audit")
def compliance_audit(session_id: str = "", limit: int = 100):
    return {
        "events": compliance_recorder.get_log(session_id or None, limit),
        "stats": compliance_recorder.get_stats(),
    }


# ── Legal-authorization ledger ──────────────────────────────────────
# The ledger supplies the authorization *references* a human legal-proxy approver
# may cite. It never auto-clears a request. Every fetch is audit-logged; SSH
# credentials are supplied at request time and never stored.


@app.get("/api/compliance/ledger/status")
def ledger_status():
    if not legal_proxy_enabled():
        raise HTTPException(status_code=403, detail="Legal-proxy role is not enabled")
    return legal_ledger.status()


class LedgerFetchRequest(BaseModel):
    source: str = Field(..., description="https | ssh | upload")
    session_id: str = Field(default="system", max_length=200)
    approver: str = Field(default="", max_length=200)
    # SSH-only, used transiently for a single fetch and never stored:
    username: str = Field(default="", max_length=200)
    password: str = Field(default="", max_length=400)
    # upload-only:
    csv: str = Field(default="", max_length=5_000_000)
    signature_b64: str = Field(
        default="", max_length=100_000,
        description="Base64 detached signature of the CSV (required when a key is set)",
    )


@app.post("/api/compliance/ledger/fetch")
def ledger_fetch(req: LedgerFetchRequest):
    if not legal_proxy_enabled():
        raise HTTPException(status_code=403, detail="Legal-proxy role is not enabled")
    try:
        if req.source == "https":
            meta = legal_ledger.fetch_https()
        elif req.source == "ssh":
            meta = legal_ledger.fetch_ssh(req.username, req.password)
        elif req.source == "upload":
            sig = base64.b64decode(req.signature_b64) if req.signature_b64 else None
            meta = legal_ledger.load_from_upload(req.csv.encode("utf-8"), sig)
        else:
            raise HTTPException(status_code=400, detail=f"unknown source '{req.source}'")
    except HTTPException:
        raise
    except Exception as exc:  # log the failed fetch, then surface a safe message
        compliance_recorder.record(
            req.session_id, "ledger.fetch",
            f"[ledger] fetch via {req.source} FAILED",
            {"source": req.source},  # note: no credentials are ever recorded
            consent_attested=True,
        )
        raise HTTPException(status_code=502, detail=f"ledger fetch failed: {exc}") from exc

    compliance_recorder.record(
        req.session_id, "ledger.fetch",
        f"[ledger] fetched {meta['count']} authorizations via {meta['source']}"
        + (f" by {req.approver}" if req.approver else ""),
        {"source": meta["source"], "count": meta["count"], "sha256": meta["sha256"][:16]},
        consent_attested=True,
    )
    return {"ok": True, "status": legal_ledger.status()}


class CancelRequest(BaseModel):
    run_id: str


@app.post("/api/pipeline/cancel")
def pipeline_cancel(req: CancelRequest):
    success = cancel_pipeline(req.run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pipeline run not found or already completed")
    return {"cancelled": True, "run_id": req.run_id}


# ── History ────────────────────────────────────────────────────────


@app.get("/api/history/{session_id}")
def get_history(session_id: str):
    runs = memory.get_runs(session_id)
    return {"session_id": session_id, "runs": runs}


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = memory.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


# ── Scenarios / Exercises ──────────────────────────────────────────


@app.get("/api/scenarios")
def list_scenarios(difficulty: str | None = None):
    if difficulty:
        return {"scenarios": get_scenarios_by_difficulty(difficulty)}
    return {"scenarios": get_all_scenarios()}


@app.get("/api/scenarios/{scenario_id}")
def scenario_detail(scenario_id: str):
    s = get_scenario(scenario_id)
    if not s:
        raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
    return s


# ── Static files (frontend) ────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.isdir(FRONTEND_DIR):
    for subdir in ("assets", "css", "js"):
        sub_path = os.path.join(FRONTEND_DIR, subdir)
        if os.path.isdir(sub_path):
            app.mount(f"/{subdir}", StaticFiles(directory=sub_path), name=subdir)

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{path:path}")
    def serve_spa(path: str):
        file_path = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
