"""FastAPI orchestrator: prompt/style/script -> Ollama -> Wan2.1 video."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, ollama, wan2

# Make sure the artifact directory exists and is writable.
try:
    os.makedirs(config.ARTIFACT_DIR, exist_ok=True)
except OSError:
    local_dir = Path(__file__).parent / "artifacts"
    local_dir.mkdir(parents=True, exist_ok=True)
    config.ARTIFACT_DIR = str(local_dir)

app = FastAPI(title="Bee-Gravity", description="Ollama script writer -> Wan2.1 video generator.")

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.mount("/videos", StaticFiles(directory=config.ARTIFACT_DIR), name="videos")


class GenerateRequest(BaseModel):
    prompt: str = Field(default="", description="What you want to see, e.g. a bee explaining gravity")
    script: str = Field(default="", description="Optional: paste your own video prompt")
    style: str = Field(default="cartoon", description="Visual style")
    duration: str = Field(default="5s", description="Target duration, e.g. 5s or 60s")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the single-page UI."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text())


@app.get("/api/config")
async def api_config() -> dict:
    """Runtime configuration and health."""
    ollama_ready = await ollama.is_ready()
    wan2_available = wan2.is_available()
    ready = wan2_available
    warning = ""
    not_ready_reason = ""
    if not wan2_available:
        not_ready_reason = (
            "Wan2.1 is not available. Build the image with --build-arg VIDEO_STACK=wan "
            "or set WAN2_COMMAND to a working wan2-generate binary."
        )
    elif not ollama_ready:
        warning = (
            "Ollama is not reachable; prompt-to-script generation is disabled. "
            "Paste a script directly or start Ollama."
        )
    return {
        "ollama_host": config.OLLAMA_HOST,
        "ollama_model": config.OLLAMA_MODEL,
        "ollama_ready": ollama_ready,
        "wan2_command": config.WAN2_COMMAND,
        "wan2_available": wan2_available,
        "ready": ready,
        "warning": warning,
        "not_ready_reason": not_ready_reason,
        "styles": config.STYLES,
    }


@app.post("/api/generate")
async def api_generate(req: GenerateRequest) -> dict:
    """Generate a script (via Ollama if needed) and render it with Wan2.1."""
    if not req.prompt.strip() and not req.script.strip():
        raise HTTPException(status_code=400, detail="Provide a prompt or paste a script.")

    if not wan2.is_available():
        raise HTTPException(
            status_code=503,
            detail=(
                "Wan2.1 is not available. Build the image with --build-arg VIDEO_STACK=wan "
                "or set WAN2_COMMAND to a working wan2-generate binary."
            ),
        )

    script = req.script.strip()
    if not script:
        if not await ollama.is_ready():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Ollama is not reachable. Paste a script directly or start Ollama "
                    f"at {config.OLLAMA_HOST}."
                ),
            )
        try:
            script = await ollama.generate_script(req.prompt, req.style)
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"Ollama script generation failed: {exc}"
            ) from exc
        if not script:
            raise HTTPException(status_code=502, detail="Ollama returned an empty script.")

    try:
        result = await wan2.generate_video(script, req.duration, config.ARTIFACT_DIR)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Wan2.1 video generation failed: {exc}") from exc

    artifact = result["artifact"]
    filename = Path(artifact).name
    return {
        "status": "ok",
        "script": script,
        "style": req.style,
        "duration": req.duration,
        "video_url": f"/videos/{filename}",
        "artifact": artifact,
        "provider": "Wan2.1",
        "simulated": result.get("simulated", True),
    }
