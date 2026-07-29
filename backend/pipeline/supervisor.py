"""Supervisor orchestrator — the full 'Strategic Brain' control layer.

This is the orchestration described in the system topology note. It goes beyond
the fixed 4-agent chat and demonstrates every architectural capability the note
requires (tools are stubs for now, filled in per-tier later):

  1. Autonomous task decomposition  — Director/Supervisor splits the directive.
  2. Dynamic sub-agent spawning      — workers are spawned based on the plan
                                        (Intelligence / Media / Infrastructure / Persona).
  3. Real tool calling               — each worker invokes registry tools.
  4. Self-refining error loop        — on ToolError the Supervisor debugs, alters
                                        parameters, and re-executes (bounded retries).
  5. Multi-model                     — each role can run on a different model.
  6. Synthesis                       — a Synthesizer integrates all worker output.

SSE contract stays backward compatible (pipeline_start / agent_start / token /
agent_done / done) and adds richer events (worker_spawn / tool_call /
tool_result / self_heal) that the frontend renders when present and older
clients safely ignore.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents import DIRECTOR, SYNTHESIZER
from backend.agents.workers import WorkerDef, select_workers
from backend.pipeline.llm_config import LLMBackend, create_langchain_llm
from backend.pipeline.memory import PipelineMemory
from backend.pipeline.model_router import model_for_role
from backend.tools import registry

memory = PipelineMemory()

_active: dict[str, bool] = {}

MAX_TOOL_RETRIES = 2


def cancel(run_id: str) -> bool:
    if run_id in _active:
        _active[run_id] = False
        return True
    return False


def _make_llm(role_id: str, backend: LLMBackend):
    """Create a LangChain LLM bound to the model assigned to this role."""
    model = model_for_role(role_id, backend)
    llm = create_langchain_llm(backend)
    # ChatOllama / ChatOpenAI both accept .model; bind the per-role model.
    try:
        llm.model = model
    except Exception:
        pass
    return llm, model


async def _stream_llm(llm, system_prompt: str, user_prompt: str) -> str:
    """Invoke the LLM and return the full text."""
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    resp = await llm.ainvoke(messages)
    return resp.content if hasattr(resp, "content") else str(resp)


async def _run_worker_tools(worker: WorkerDef) -> tuple[list[dict], list[dict]]:
    """Invoke every tool in the worker's category, applying the self-refining
    loop on failure. Returns (tool_events, tool_results)."""
    events: list[dict] = []
    results: list[dict] = []

    for spec in registry.tools_by_category(worker.tool_category):
        # Choose initial params — deliberately trigger a failure for the proxy
        # rotator to demonstrate the self-heal loop.
        params: dict = {}
        if spec.id == "rotate_proxy":
            params = {"pool": "blocked", "reason": "endpoint blocked by firewall"}

        attempt = 0
        while True:
            events.append({"type": "tool_call", "worker": worker.id, "tool": spec.id,
                           "provider": spec.provider, "params": params, "attempt": attempt + 1})
            try:
                result = await registry.call_tool(spec.id, **params)
                events.append({"type": "tool_result", "worker": worker.id, "tool": spec.id,
                               "ok": True, "result": result})
                results.append({"tool": spec.id, "result": result})
                break
            except registry.ToolError as e:
                events.append({"type": "tool_result", "worker": worker.id, "tool": spec.id,
                               "ok": False, "error": str(e)})
                attempt += 1
                if attempt > MAX_TOOL_RETRIES:
                    events.append({"type": "self_heal", "worker": worker.id, "tool": spec.id,
                                   "action": "give_up", "note": "Max retries reached; skipping tool."})
                    results.append({"tool": spec.id, "error": str(e)})
                    break
                # Self-refine: alter the parameters and retry.
                new_pool = "residential" if params.get("pool") == "blocked" else "datacenter"
                events.append({"type": "self_heal", "worker": worker.id, "tool": spec.id,
                               "action": "alter_params",
                               "note": f"Tool failed; altering pool → '{new_pool}' and retrying.",
                               "params": {"pool": new_pool}})
                params = {**params, "pool": new_pool}

    return events, results


async def run(task: str, session_id: str, backend: LLMBackend) -> AsyncGenerator[str, None]:
    run_id = str(uuid.uuid4())
    _active[run_id] = True

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    def check_cancel() -> bool:
        return not _active.get(run_id, False)

    yield sse({"type": "pipeline_start", "run_id": run_id, "model": backend.value,
               "framework": "supervisor"})

    history: list[dict] = []

    async def emit_agent(agent_id, role, color, icon, description, tools, content):
        """Emit a full agent turn as SSE, chunking content into tokens."""
        yield sse({"type": "agent_start", "agent": agent_id, "role": role, "color": color,
                   "icon": icon, "description": description, "tools": tools})
        for i in range(0, len(content), 5):
            if check_cancel():
                return
            yield sse({"type": "token", "agent": agent_id, "content": content[i:i + 5]})
        yield sse({"type": "agent_done", "agent": agent_id})
        history.append({"agent": agent_id, "role": role, "content": content})

    try:
        # ── Stage 1: Supervisor / Director decomposition ──
        dir_llm, dir_model = _make_llm("director", backend)
        plan = await _stream_llm(
            dir_llm, DIRECTOR.system_prompt,
            f"Incoming directive:\n\"{task}\"\n\n"
            "Decompose it into functional workstreams. Mention which capabilities are "
            "needed (analysis/intelligence, media/content, infrastructure/routing, persona). "
            "Be concise.",
        )
        async for ev in emit_agent(DIRECTOR.id, f"{DIRECTOR.role} ({dir_model})", DIRECTOR.color,
                                    DIRECTOR.icon, DIRECTOR.description, DIRECTOR.tools, plan):
            yield ev
        if check_cancel():
            yield sse({"type": "cancelled"})
            return

        # ── Stage 2: Dynamic worker spawning ──
        workers = select_workers(plan)
        yield sse({"type": "worker_spawn", "workers": [w.to_meta() for w in workers]})

        # ── Stage 3: Each worker executes + calls tools (with self-heal) ──
        for worker in workers:
            if check_cancel():
                yield sse({"type": "cancelled"})
                return

            tool_events, tool_results = await _run_worker_tools(worker)
            for ev in tool_events:
                yield sse(ev)

            w_llm, w_model = _make_llm(worker.id, backend)
            tool_summary = json.dumps(tool_results, indent=2)
            worker_out = await _stream_llm(
                w_llm, worker.system_prompt,
                f"Directive: \"{task}\"\n\nDirector's plan:\n{plan}\n\n"
                f"Your tool results (JSON):\n{tool_summary}\n\n"
                "Given these tool results, report your findings for your workstream. Be concise.",
            )
            async for ev in emit_agent(worker.id, f"{worker.role} ({w_model})", worker.color,
                                       worker.icon, worker.description,
                                       [t["tool"] for t in tool_results], worker_out):
                yield ev

        # ── Stage 4: Synthesis ──
        syn_llm, syn_model = _make_llm("synthesizer", backend)
        prior = "\n\n".join(f"### {h['role']}\n{h['content']}" for h in history)
        synthesis = await _stream_llm(
            syn_llm, SYNTHESIZER.system_prompt,
            f"Directive: \"{task}\"\n\nAll contributions:\n{prior}\n\n"
            "Integrate everything into a single, polished strategic output.",
        )
        async for ev in emit_agent(SYNTHESIZER.id, f"{SYNTHESIZER.role} ({syn_model})",
                                   SYNTHESIZER.color, SYNTHESIZER.icon, SYNTHESIZER.description,
                                   SYNTHESIZER.tools, synthesis):
            yield ev

        memory.save_run(session_id, run_id, task, history)
        yield sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield sse({"type": "error", "message": f"Supervisor error: {e}"})
    finally:
        _active.pop(run_id, None)
