"""TIER 3 — Persona Orchestration orchestrator.

Runs the 4-member Persona crew (synthetic identity design → behavioral modeling
→ voice/dialect mapping → fleet orchestration & lifecycle). Every run is
compliance-screened and audit-logged before execution. Policy is allow-by-
default: the run proceeds and is logged; access is only limited when the safety
screen flags the request (e.g. a real deployment / evasion / fraud request).
Flagged requests are still recorded and the crew emits a compliance notice
instead of a plan.

Everything is simulated: the persona / automation tools are stubs — no real
synthetic accounts are created, nothing is deployed to live platforms, and no
stealth / fingerprint-evasion is performed.

Emits the same SSE contract as the other crews plus tool + compliance events.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.persona_crew import PERSONA_CREW, CrewAgentDef
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
    if tool_id == "persona_design":
        return {"archetype": inp.get("scenario", ""), "region": inp.get("region", "")}
    if tool_id == "behavior_model":
        return {"persona_id": "sim-persona-0001", "goal": inp.get("objective", "")}
    if tool_id == "voice_dialect_map":
        return {"language": inp.get("region", ""), "dialect": inp.get("region", "")}
    if tool_id == "fleet_orchestrate":
        return {"count": 0, "platform": inp.get("platform", "")}
    if tool_id == "browser_automation_plan":
        return {"target": inp.get("platform", ""), "tool": "playwright"}
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
                "framework": "persona_crew", "scenario": inp.get("scenario", "")})

    llm = create_langchain_llm(backend)
    history: list[dict] = []

    try:
        for agent in PERSONA_CREW:
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

        memory.save_run(session_id, run_id, f"[persona] {inp.get('objective', '')}", history)
        yield _sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield _sse({"type": "error", "message": f"Persona Orchestration error: {e}"})
    finally:
        _active.pop(run_id, None)


async def route(inp: dict, session_id: str, backend: str = "") -> AsyncGenerator[str, None]:
    """Compliance-screen and audit-log, then run the crew (allow-by-default)."""
    summary = f"[persona] {inp.get('objective', '')} | scenario={inp.get('scenario', '')}"
    result = compliance.record(
        session_id, "persona.plan", summary, inp, inp.get("authorized", False),
        authorization_ref=inp.get("authorization_ref", ""),
        approver=inp.get("approver", ""),
    )

    yield _sse({
        "type": "compliance",
        "audit_id": result.audit_id,
        "allowed": result.allowed,
        "flagged": result.flagged,
        "reasons": result.reasons,
        "verdict": result.verdict,
        "sensitivity": result.sensitivity,
        "override": result.override,
    })

    if not result.allowed:
        yield _sse({
            "type": "compliance_block",
            "audit_id": result.audit_id,
            "message": (
                "This request was flagged by the safety screen and cannot proceed as-is. "
                "It has been recorded in the audit log (id " + result.audit_id + ") for legal "
                "review. Reasons: " + "; ".join(result.reasons) + ". Persona orchestration is "
                "simulation / detection-research only — remove requests for real deployment, "
                "account fraud, or platform evasion, or (for authorized legal users) clear it "
                "via the accountable Legal-Proxy Override with a real authorization reference "
                "and approver — a claimed origin alone is not sufficient."
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
    """Run the Persona crew with pre-recorded responses (no LLM needed)."""
    run_id = str(uuid.uuid4())

    yield _sse({"type": "pipeline_start", "run_id": run_id, "model": "demo-mode",
                "demo": True, "framework": "persona_crew", "scenario": inp.get("scenario", "")})

    history: list[dict] = []
    for agent in PERSONA_CREW:
        for ev in await _run_agent_tools(agent, inp):
            yield _sse(ev)

        yield _sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                    "framework": agent.framework, "color": agent.color, "icon": agent.icon,
                    "description": agent.description, "tools": agent.tools})

        content = DEMO_RESPONSES.get(agent.id, f"[Demo response for {agent.role}]").format(
            objective=inp.get("objective", ""), scenario=inp.get("scenario", ""),
            platform=inp.get("platform", ""), region=inp.get("region", ""),
        )
        for i in range(0, len(content), 4):
            yield _sse({"type": "token", "agent": agent.id, "content": content[i:i + 4]})

        yield _sse({"type": "agent_done", "agent": agent.id})
        history.append({"agent": agent.id, "role": agent.role, "content": content})

    memory.save_run(session_id, run_id, f"[persona] {inp.get('objective', '')}", history)
    yield _sse({"type": "done", "run_id": run_id, "demo": True})


DEMO_RESPONSES: dict[str, str] = {
    "persona_architect": """\
## Design Goals & Lab Scope
Simulated {scenario} for "{objective}". All personas are synthetic and lab-only — no real accounts.

## 7 Layers (representative persona · SIMULATED)
1. Identity — "sim-persona-0001" (lab tag)
2. Backstory — modeled life history (fictional)
3. Demographics — region {region}, modeled age/occupation
4. Psychographics — values, motivations (modeled)
5. Digital Footprint — conceptual only; no real profiles created
6. Voice — dialect handle for the Voice specialist
7. Goals — scenario-scoped, lab-only

## Fleet Diversity
Vary archetypes, activity levels, and interests to model realistic distribution.

## Detection Hooks
Creation-time clustering, template reuse, and footprint gaps defenders can flag.""",

    "behavior_architect": """\
## Behavior Graph (conceptual)
States: idle → observe → engage → cool-down; triggers are scenario events (modeled).

## Cadence Model
Human-like posting/interaction distribution (modeled, never executed).

## Memory & Goals
Per-persona short/long memory and scenario goals (in-lab store only).

## Guardrails
Simulated agents never touch real platforms, never send real messages, never evade detection.

## Detection Signals
Cadence regularity, synchronized activity, and shared memory tells for blue-team detection.""",

    "voice_dialect_specialist": """\
## Dialect Profiles ({region})
Punjabi (Shahmukhi), Saraiki, Urdu, English registers modeled with code-switching notes.

## Speech-Pattern Tuning
Register, cadence, and idiom calibration at a conceptual level.

## Voice-Engine Mapping (offline-first)
Coqui XTTS-v2 / Chatterbox (offline, default); ElevenLabs only if online tools are explicitly enabled.

## Authenticity vs Detection
Note prosody artifacts and metadata a defender can use to detect synthetic voices. No audio synthesized here.""",

    "orchestration_engineer": """\
## Executive Summary
Simulated {scenario} orchestration plan for "{objective}" on {platform}. Lab-only; nothing deployed.

## Fleet Coordination (modeled)
Scheduling, deconfliction, and scale modeled — no real provisioning.

## Lifecycle
design → simulated provision → simulated monitor → retire, fully audit-logged.

## Automation Plan (conceptual)
Playwright/Puppeteer/Selenium referenced as concept only — NO stealth, NO fingerprint evasion, respect platform ToS.

## Detection & Countermeasures
Graph clustering, timing correlation, and content-similarity detection for defenders to disrupt such a fleet.

## Compliance Checklist
☑ Authorization on file ☑ Lab-only, no real deployment ☑ No account fraud / evasion ☑ Audit trail retained.""",
}
