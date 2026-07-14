"""TIER 2 — Media Crew (Duix-Avatar Pipeline) orchestrator.

Runs the 4-member Media Crew sequentially (script → voice → video → production
synthesis). Each stage invokes its registry media tools (stubs today; real
integrations swap in later) and an LLM narrates the plan. Offline-first: the
selected voice/video tool defaults to a local model; online tools raise a
ToolError unless explicitly enabled, and the crew notes the fallback.

Emits the same SSE contract as TIER 1/Intelligence Crew plus tool events.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.media_crew import MEDIA_CREW, CrewAgentDef
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

_active: dict[str, bool] = {}


def cancel(run_id: str) -> bool:
    if run_id in _active:
        _active[run_id] = False
        return True
    return False


def _tool_params(tool_id: str, inp: dict) -> dict:
    if tool_id == "render_avatar":
        return {"tool": inp.get("avatar_tool", "duix"), "script": inp.get("topic", "")}
    if tool_id == "clone_voice":
        return {"tool": inp.get("voice_tool", "chatterbox"),
                "language": inp.get("language_code", "en"), "script": inp.get("topic", "")}
    if tool_id == "generate_video":
        return {"tool": inp.get("video_tool", "wan2"),
                "script": inp.get("topic", ""), "duration": inp.get("duration", "60s")}
    return {}


async def _run_agent_tools(agent: CrewAgentDef, inp: dict) -> tuple[list[dict], list[dict]]:
    events: list[dict] = []
    results: list[dict] = []
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
            results.append({"tool": tool_id, "result": result})
        except registry.ToolError as e:
            events.append({"type": "tool_result", "worker": agent.id, "tool": tool_id,
                           "ok": False, "error": str(e)})
            # Offline-first self-heal: fall back to the local default tool.
            fallback = {"clone_voice": "chatterbox", "generate_video": "wan2"}.get(tool_id)
            if fallback:
                events.append({"type": "self_heal", "worker": agent.id,
                               "note": f"{tool_id}: online tool unavailable → falling back to offline '{fallback}'"})
                params2 = dict(params, tool=fallback)
                try:
                    result = await registry.call_tool(tool_id, **params2)
                    events.append({"type": "tool_call", "worker": agent.id, "tool": tool_id,
                                   "provider": spec.provider, "params": params2, "attempt": 2})
                    events.append({"type": "tool_result", "worker": agent.id, "tool": tool_id,
                                   "ok": True, "result": result})
                    results.append({"tool": tool_id, "result": result})
                except registry.ToolError as e2:
                    events.append({"type": "tool_result", "worker": agent.id, "tool": tool_id,
                                   "ok": False, "error": str(e2)})
                    results.append({"tool": tool_id, "error": str(e2)})
            else:
                results.append({"tool": tool_id, "error": str(e)})
    return events, results


async def run(inp: dict, session_id: str,
              backend: LLMBackend) -> AsyncGenerator[str, None]:
    run_id = str(uuid.uuid4())
    _active[run_id] = True

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    def check_cancel() -> bool:
        return not _active.get(run_id, False)

    yield sse({"type": "pipeline_start", "run_id": run_id, "model": backend.value,
               "framework": "media_crew", "language": inp.get("language", "")})

    llm = create_langchain_llm(backend)
    history: list[dict] = []

    try:
        for agent in MEDIA_CREW:
            if check_cancel():
                yield sse({"type": "cancelled"})
                return

            tool_events, tool_results = await _run_agent_tools(agent, inp)
            for ev in tool_events:
                yield sse(ev)

            yield sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                       "framework": agent.framework, "color": agent.color, "icon": agent.icon,
                       "description": agent.description, "tools": agent.tools})

            user_prompt = agent.build_user_prompt(inp, history)
            if tool_results:
                user_prompt += f"\n\nTool results (JSON):\n{json.dumps(tool_results, indent=2)}"

            messages = [
                SystemMessage(content=agent.system_prompt),
                HumanMessage(content=user_prompt),
            ]
            resp = await llm.ainvoke(messages)
            content = resp.content if hasattr(resp, "content") else str(resp)

            for i in range(0, len(content), 5):
                if check_cancel():
                    yield sse({"type": "cancelled"})
                    return
                yield sse({"type": "token", "agent": agent.id, "content": content[i:i + 5]})

            yield sse({"type": "agent_done", "agent": agent.id})
            history.append({"agent": agent.id, "role": agent.role, "content": content})

        memory.save_run(session_id, run_id, f"[media] {inp.get('topic', '')}", history)
        yield sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield sse({"type": "error", "message": f"Media Crew error: {e}"})
    finally:
        _active.pop(run_id, None)


async def route(inp: dict, session_id: str, backend: str = "") -> AsyncGenerator[str, None]:
    """Resolve the backend and run the crew, falling back to demo mode."""
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
    """Run the Media Crew with pre-recorded responses (no LLM needed)."""
    run_id = str(uuid.uuid4())

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    yield sse({"type": "pipeline_start", "run_id": run_id, "model": "demo-mode",
               "demo": True, "framework": "media_crew", "language": inp.get("language", "")})

    history: list[dict] = []
    for agent in MEDIA_CREW:
        tool_events, _ = await _run_agent_tools(agent, inp)
        for ev in tool_events:
            yield sse(ev)

        yield sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                   "framework": agent.framework, "color": agent.color, "icon": agent.icon,
                   "description": agent.description, "tools": agent.tools})

        content = DEMO_RESPONSES.get(agent.id, f"[Demo response for {agent.role}]").format(
            topic=inp.get("topic", ""), tone=inp.get("tone", ""),
            language=inp.get("language", ""), duration=inp.get("duration", ""),
            voice_tool=inp.get("voice_tool", ""), video_tool=inp.get("video_tool", ""),
        )
        for i in range(0, len(content), 4):
            yield sse({"type": "token", "agent": agent.id, "content": content[i:i + 4]})

        yield sse({"type": "agent_done", "agent": agent.id})
        history.append({"agent": agent.id, "role": agent.role, "content": content})

    memory.save_run(session_id, run_id, f"[media] {inp.get('topic', '')}", history)
    yield sse({"type": "done", "run_id": run_id, "demo": True})


DEMO_RESPONSES: dict[str, str] = {
    "script_writer": """\
## Avatar Brief
A warm, credible {language} presenter delivering a {tone} {duration} piece on "{topic}".

## Full Script
[warm] Assalam-o-alaikum. [pause] Today we talk about {topic}. [emphasize] It matters to every household.
[serious] Here is what you need to know — clearly, and without noise. [pause] Let's begin.

## Teleprompt Version
Assalam-o-alaikum. Today we talk about {topic}. It matters to every household. Here is what you need to know — clearly, and without noise. Let's begin.

## Timing Estimate
~{duration} at 130 wpm.""",

    "voice_architect": """\
## Tool Recommendation
**Chatterbox (MIT, offline)** — zero-shot cloning from 5s reference; best natural {language} delivery. (ElevenLabs only if online is explicitly enabled.)

## Voice Profile
Gender: neutral-warm · Age: 30–40 · Accent: regional {language} · Pace: 130 wpm · Pitch: mid.

## Cloning Strategy
5–8s clean reference, 48kHz, no background noise.

## Emotional Cues (Bark-compatible)
[warm] intro · [clears throat] transition · [serious] key point.

## Estimated Render Time
~20s of audio in ~15s on a local GPU.

## Fallback
Coqui XTTS-v2 (offline) for stronger cross-lingual accents.""",

    "video_director": """\
## Tool Recommendation
**Wan2.1 (Apache-2.0, offline)** for 720p scenes on RTX 4090; CogVideoX for RTX 3060+ fallback. (HeyGen only if online enabled.)

## Shot List
1. Close-up — avatar intro. Prompt: "medium close-up, warm lighting, {tone} presenter".
2. Medium — supporting b-roll. Prompt: "cutaway, {topic}, documentary style".
3. Wide — closing. Prompt: "wide establishing shot, soft focus".

## Avatar Integration
Composite Duix-Avatar over generated b-roll via greenscreen/inpainting; PiP for closing.

## Technical Specs
720p · 24fps · ~16GB VRAM · ~4 min render for {duration}.

## Fallback
CogVideoX on lower VRAM; Open-Sora for scene variety.""",

    "production_lead": """\
## Executive Summary
An offline-first {duration} {tone} digital-human piece on "{topic}" in {language}.

## Pipeline Sequence
1. Script → 2. Voice Clone (Chatterbox) → 3. Avatar Render (Duix-Avatar) → 4. Video Generation (Wan2.1) → 5. Compositing → 6. Export.

## Tool Chain
Duix-Avatar (offline) · Chatterbox (offline) · Wan2.1 (offline). Online (ElevenLabs/HeyGen) optional, disabled by default.

## Production Schedule
Script 2m · Voice 1m · Avatar 3m · Video 4m · Composite 2m · Export 1m ≈ 13m wall-clock.

## Hardware Requirements
Min: RTX 3060 12GB. Rec: RTX 4090 24GB.

## Deliverables
MP4 720p (master), WebM (web), 9:16 cut for Reels/WhatsApp.

## Quality Checklist
Lip-sync alignment · audio levels · caption accuracy · brand-safe framing.

## Distribution Notes
YouTube 16:9 · Instagram/TikTok 9:16 · WhatsApp <16MB.""",
}
