"""TIER 1 — Strategic Brain: Multi-Agent AI Orchestration Platform."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.agents import ALL_AGENTS
from backend.agents.workers import ALL_WORKERS
from backend.exercises.scenarios import get_all_scenarios, get_scenario, get_scenarios_by_difficulty
from backend.tools import registry
from backend.pipeline.orchestrator import (
    cancel_pipeline,
    get_config,
    is_llm_configured,
    memory,
    route_pipeline,
)
from backend.tools.analysis import get_all_tools, get_tools_for_agent

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
