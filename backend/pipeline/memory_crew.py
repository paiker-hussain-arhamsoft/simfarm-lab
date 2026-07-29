"""TIER 4 simulated memory and persistence pipeline."""
import json
import uuid
from collections.abc import AsyncGenerator
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agents.memory_crew import MEMORY_CREW, CrewAgentDef
from backend.pipeline.compliance import ComplianceRecorder
from backend.pipeline.llm_config import (
    LLMBackend, create_langchain_llm, detect_llm_backend,
    is_ollama_model_ready, is_openai_configured,
)
from backend.pipeline.memory import PipelineMemory
from backend.tools import registry

memory = PipelineMemory()
compliance = ComplianceRecorder()
_active = {}


def cancel(run_id):
    _active[run_id] = False
    return True


def _sse(data):
    return f"data: {json.dumps(data)}\n\n"


def _tool_params(tool, inp):
    return {
        "memory_backend": inp.get("memory_backend", ""),
        "storage_tier": inp.get("storage_tier", ""),
        "scenario": inp.get("scenario", ""),
        "objective": inp.get("objective", ""),
    }


async def _run_agent_tools(agent: CrewAgentDef, inp):
    out = []
    for tool_id in agent.tools:
        spec = registry.get_tool(tool_id)
        if not spec:
            continue
        params = _tool_params(tool_id, inp)
        out.append({"type": "tool_call", "worker": agent.id, "tool": tool_id,
                    "provider": spec.provider, "params": params, "attempt": 1})
        try:
            result = await registry.call_tool(tool_id, **params)
            out.append({"type": "tool_result", "worker": agent.id, "tool": tool_id,
                        "ok": True, "result": result})
        except registry.ToolError as exc:
            out.append({"type": "tool_result", "worker": agent.id, "tool": tool_id,
                        "ok": False, "error": str(exc)})
    return out


async def run(inp, session_id, backend: LLMBackend) -> AsyncGenerator[str, None]:
    run_id = str(uuid.uuid4())
    _active[run_id] = True
    yield _sse({"type": "pipeline_start", "run_id": run_id, "model": backend.value,
                "framework": "memory_crew", "scenario": inp.get("scenario", "")})
    history = []
    llm = create_langchain_llm(backend)
    try:
        for agent in MEMORY_CREW:
            if not _active.get(run_id):
                yield _sse({"type": "cancelled"})
                return
            for event in await _run_agent_tools(agent, inp):
                yield _sse(event)
            yield _sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                        "framework": agent.framework, "color": agent.color,
                        "icon": agent.icon, "description": agent.description,
                        "tools": agent.tools})
            response = await llm.ainvoke([
                SystemMessage(content=agent.system_prompt),
                HumanMessage(content=agent.build_user_prompt(inp, history)),
            ])
            content = response.content if hasattr(response, "content") else str(response)
            for i in range(0, len(content), 5):
                yield _sse({"type": "token", "agent": agent.id,
                            "content": content[i:i + 5]})
            yield _sse({"type": "agent_done", "agent": agent.id})
            history.append({"agent": agent.id, "role": agent.role, "content": content})
        memory.save_run(session_id, run_id, f"[memory] {inp.get('objective', '')}", history)
        yield _sse({"type": "done", "run_id": run_id})
    except Exception as exc:
        yield _sse({"type": "error", "message": f"Memory error: {exc}"})
    finally:
        _active.pop(run_id, None)


async def route(inp, session_id, backend=""):
    record = compliance.record(
        session_id, "memory.plan", f"[memory] {inp.get('objective', '')} | "
        f"scenario={inp.get('scenario', '')}", inp, inp.get("authorized", False),
        authorization_ref=inp.get("authorization_ref", ""),
        approver=inp.get("approver", ""),
    )
    yield _sse({"type": "compliance", "audit_id": record.audit_id,
                "allowed": record.allowed, "flagged": record.flagged,
                "reasons": record.reasons, "verdict": record.verdict,
                "sensitivity": record.sensitivity, "override": record.override})
    if not record.allowed:
        yield _sse({"type": "compliance_block", "audit_id": record.audit_id,
                    "message": "This request was flagged by the safety screen and cannot "
                    "proceed as-is. It has been recorded in the audit log (id "
                    + record.audit_id + ") for legal review.", "reasons": record.reasons})
        yield _sse({"type": "done", "blocked": True})
        return
    resolved = (
        LLMBackend.OPENAI if backend == "openai" and is_openai_configured()
        else LLMBackend.OLLAMA if backend == "ollama" and is_ollama_model_ready()
        else detect_llm_backend()
    )
    if resolved is None:
        async for event in run_demo(inp, session_id):
            yield event
    else:
        async for event in run(inp, session_id, resolved):
            yield event


async def run_demo(inp, session_id):
    run_id = str(uuid.uuid4())
    yield _sse({"type": "pipeline_start", "run_id": run_id, "model": "demo-mode",
                "demo": True, "framework": "memory_crew",
                "scenario": inp.get("scenario", "")})
    history = []
    for agent in MEMORY_CREW:
        for event in await _run_agent_tools(agent, inp):
            yield _sse(event)
        yield _sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                    "framework": agent.framework, "color": agent.color,
                    "icon": agent.icon, "description": agent.description,
                    "tools": agent.tools})
        content = (
            f"## {agent.role}\n1. Simulated {agent.framework} model for "
            f"{inp.get('scenario', '')} and \"{inp.get('objective', '')}\".\n\n"
            "## Detection & Countermeasures\nMonitor retention, access, lineage, "
            "encryption and synthetic-data boundaries; no real PII is used.\n\n"
            "## Compliance Checklist\n☑ Lab-only ☑ synthetic fixtures only "
            "☑ simulation-only ☑ audit-logged."
        )
        for i in range(0, len(content), 4):
            yield _sse({"type": "token", "agent": agent.id, "content": content[i:i + 4]})
        yield _sse({"type": "agent_done", "agent": agent.id})
        history.append({"agent": agent.id, "role": agent.role, "content": content})
    memory.save_run(session_id, run_id, f"[memory] {inp.get('objective', '')}", history)
    yield _sse({"type": "done", "run_id": run_id, "demo": True})
