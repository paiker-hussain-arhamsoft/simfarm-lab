"""TIER 2 — Video Stack orchestrator.

Runs the 4-member Video Stack (render strategy → script → technical direction →
production synthesis). Every run is compliance-screened and audit-logged before
execution. Policy is allow-by-default: the run proceeds and is logged; access is
only limited when the safety screen flags the request (e.g. non-consensual /
named-real-person deepfake without a consent attestation). Flagged requests are
still recorded and the crew emits a compliance notice instead of a plan.

Emits the same SSE contract as the other crews plus tool + compliance events.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.video_stack import VIDEO_STACK, CrewAgentDef
from backend.pipeline.compliance import ComplianceRecorder
from backend.pipeline.llm_config import (
    LLMBackend,
    create_langchain_llm,
    detect_llm_backend,
    is_ollama_model_ready,
    is_openai_configured,
)
from backend.pipeline.memory import PipelineMemory

from backend.tools import registry

memory = PipelineMemory()
compliance = ComplianceRecorder()

_active: dict[str, bool] = {}


def cancel(run_id: str) -> bool:
    if run_id in _active:
        _active[run_id] = False
        return True
    return False


def _tool_params(tool_id: str, inp: dict) -> dict:
    if tool_id == "face_swap":
        return {"tool": inp.get("swap_tool", "deepfacelab"),
                "source": "consented_source", "target": inp.get("topic", "")}
    if tool_id == "gfpgan_upscale":
        return {"input_path": "/artifacts/video/swap_stub.mp4", "scale": 2}
    if tool_id == "lip_sync":
        return {"tool": inp.get("lipsync_tool", "wav2lip"),
                "video": "/artifacts/video/restored_stub.mp4", "audio": "voice.wav"}
    if tool_id == "ffmpeg_pipeline":
        return {"steps": "extract,retime,scale,color,mux,encode"}
    return {}


async def _run_agent_tools(agent: CrewAgentDef, inp: dict) -> list[dict]:
    events: list[dict] = []
    for tool_id in agent.tools:
        spec = registry.get_tool(tool_id)
        if spec is None:
            continue
        params = _tool_params(tool_id, inp)
        events.append({"type": "tool_call", "worker": agent.id, "tool": tool_id,
                       "provider": spec.provider, "params": params, "attempt": 1})
        try:
            result = await registry.call_tool(tool_id, **params)
            events.append({"type": "tool_result", "worker": agent.id, "tool": tool_id,
                           "ok": True, "result": result})
        except registry.ToolError as e:
            events.append({"type": "tool_result", "worker": agent.id, "tool": tool_id,
                           "ok": False, "error": str(e)})
    return events


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def run(inp: dict, session_id: str,
              backend: LLMBackend) -> AsyncGenerator[str, None]:
    run_id = str(uuid.uuid4())
    _active[run_id] = True

    def check_cancel() -> bool:
        return not _active.get(run_id, False)

    yield _sse({"type": "pipeline_start", "run_id": run_id, "model": backend.value,
                "framework": "video_stack", "style": inp.get("style", "")})

    llm = create_langchain_llm(backend)
    history: list[dict] = []

    try:
        for agent in VIDEO_STACK:
            if check_cancel():
                yield _sse({"type": "cancelled"})
                return

            for ev in await _run_agent_tools(agent, inp):
                yield _sse(ev)

            yield _sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                        "framework": agent.framework, "color": agent.color, "icon": agent.icon,
                        "description": agent.description, "tools": agent.tools})

            user_prompt = agent.build_user_prompt(inp, history)
            messages = [
                SystemMessage(content=agent.system_prompt),
                HumanMessage(content=user_prompt),
            ]
            resp = await llm.ainvoke(messages)
            content = resp.content if hasattr(resp, "content") else str(resp)

            for i in range(0, len(content), 5):
                if check_cancel():
                    yield _sse({"type": "cancelled"})
                    return
                yield _sse({"type": "token", "agent": agent.id, "content": content[i:i + 5]})

            yield _sse({"type": "agent_done", "agent": agent.id})
            history.append({"agent": agent.id, "role": agent.role, "content": content})

        memory.save_run(session_id, run_id, f"[video] {inp.get('topic', '')}", history)
        yield _sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield _sse({"type": "error", "message": f"Video Stack error: {e}"})
    finally:
        _active.pop(run_id, None)


async def route(inp: dict, session_id: str, backend: str = "") -> AsyncGenerator[str, None]:
    """Compliance-screen and audit-log, then run the crew (allow-by-default)."""
    summary = f"[video] {inp.get('topic', '')} | style={inp.get('style', '')}"
    result = compliance.record(session_id, "video.plan", summary, inp, inp.get("consent", False))

    yield _sse({
        "type": "compliance",
        "audit_id": result.audit_id,
        "allowed": result.allowed,
        "flagged": result.flagged,
        "reasons": result.reasons,
    })

    if not result.allowed:
        # Access limited only because the activity was flagged. Still fully logged.
        yield _sse({
            "type": "compliance_block",
            "audit_id": result.audit_id,
            "message": (
                "This request was flagged by the safety screen and cannot proceed as-is. "
                "It has been recorded in the audit log (id " + result.audit_id + ") for legal "
                "review. Reasons: " + "; ".join(result.reasons) + ". To proceed, remove the "
                "flagged content or attest lawful consent for any named real person."
            ),
            "reasons": result.reasons,
        })
        yield _sse({"type": "done", "blocked": True})
        return

    if backend == "openai" and is_openai_configured():
        resolved = LLMBackend.OPENAI
    elif backend == "ollama" and is_ollama_model_ready():
        resolved = LLMBackend.OLLAMA
    else:
        resolved = detect_llm_backend()

    if resolved is None:
        async for event in run_demo(inp, session_id):
            yield event
        return

    async for event in run(inp, session_id, resolved):
        yield event


async def run_demo(inp: dict, session_id: str) -> AsyncGenerator[str, None]:
    """Run the Video Stack with pre-recorded responses (no LLM needed)."""
    run_id = str(uuid.uuid4())

    yield _sse({"type": "pipeline_start", "run_id": run_id, "model": "demo-mode",
                "demo": True, "framework": "video_stack", "style": inp.get("style", "")})

    history: list[dict] = []
    for agent in VIDEO_STACK:
        for ev in await _run_agent_tools(agent, inp):
            yield _sse(ev)

        yield _sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                    "framework": agent.framework, "color": agent.color, "icon": agent.icon,
                    "description": agent.description, "tools": agent.tools})

        content = DEMO_RESPONSES.get(agent.id, f"[Demo response for {agent.role}]").format(
            topic=inp.get("topic", ""), style=inp.get("style", ""),
            duration=inp.get("duration", ""), swap_tool=inp.get("swap_tool", ""),
        )
        for i in range(0, len(content), 4):
            yield _sse({"type": "token", "agent": agent.id, "content": content[i:i + 4]})

        yield _sse({"type": "agent_done", "agent": agent.id})
        history.append({"agent": agent.id, "role": agent.role, "content": content})

    memory.save_run(session_id, run_id, f"[video] {inp.get('topic', '')}", history)
    yield _sse({"type": "done", "run_id": run_id, "demo": True})


DEMO_RESPONSES: dict[str, str] = {
    "render_strategist": """\
## Tool Choice
**DeepFaceLab (offline, batch)** — best quality + CLI automation for a {duration} {style} piece on "{topic}". Deep-Live-Cam only if real-time preview is needed.

## Dataset / Alignment
Consented source footage → extract frames → face alignment → mask (feathered).

## Training Strategy
Use a pretrained SAEHD model; ~30k iterations fine-tune. Note: consent records required before any real render.

## Hardware
RTX 4090 24GB · ~4–6h fine-tune (simulated).

## Quality Controls
Color transfer, mask feathering, temporal smoothing. Visible synthetic-media watermark required.""",

    "video_script_writer": """\
## Logline
A {style} {duration} piece on "{topic}".

## Scene Outline
1. Cold open. 2. Context. 3. Key message. 4. Call to action.

## Dialogue / VO
[00:00] Intro line — short, clear. [00:15] Main point. [00:40] Closing.

## Teleprompt Version
Intro line. Main point. Closing.""",

    "technical_director": """\
## Upscale Plan
GFPGAN x2 face restoration on swapped frames; deflicker pass.

## FFmpeg Command Sequence
1. `ffmpeg -i swap.mp4 -vf scale=1920:1080 scaled.mp4`
2. `ffmpeg -i scaled.mp4 -i voice.wav -c:v libx264 -c:a aac -shortest muxed.mp4`
3. Color: `-vf eq=contrast=1.05:saturation=1.1`

## Lip-Sync Pass
Wav2Lip on muxed.mp4 with voice.wav → lipsynced.mp4.

## Encoding Specs
H.264, CRF 18, MP4 (master); WebM for web.

## QA
Sync drift < 40ms, no mask seams, watermark present.""",

    "video_director": """\
## Executive Summary
Offline, consent-based {style} {duration} production on "{topic}", fully audit-logged.

## End-to-End Pipeline
Dataset → Face-Swap (DeepFaceLab) → Restore (GFPGAN) → Lip-Sync (Wav2Lip) → Composite (FFmpeg) → Export.

## Tool Chain
DeepFaceLab · GFPGAN · Wav2Lip · FFmpeg — all offline/local.

## Schedule + Hardware
Prep 1h · Train 5h · Restore 1h · Sync 30m · Composite 30m. RTX 4090 recommended.

## Deliverables
MP4 1080p master (watermarked), WebM, 9:16 cut.

## Compliance Checklist
☑ Consent records on file ☑ Synthetic-media disclosure/watermark ☑ Audit trail retained ☑ No impersonation of real persons without consent.""",
}
