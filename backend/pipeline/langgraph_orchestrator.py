"""LangGraph-based multi-agent orchestration with SSE streaming."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from backend.agents import ALL_AGENTS, AgentDef
from backend.pipeline.llm_config import LLMBackend, create_langchain_llm
from backend.pipeline.memory import PipelineMemory

memory = PipelineMemory()

_active: dict[str, bool] = {}


class PipelineState(TypedDict):
    task: str
    agent_outputs: dict
    current_agent: str
    run_id: str


def cancel(run_id: str) -> bool:
    if run_id in _active:
        _active[run_id] = False
        return True
    return False


def _build_graph(llm):
    """Build the LangGraph state graph for the 4-agent pipeline."""

    def make_node(agent_def: AgentDef):
        async def node(state: PipelineState) -> dict:
            prior = [v for v in state.get("agent_outputs", {}).values()]
            user_prompt = agent_def.build_user_prompt(state["task"], prior)
            messages = [
                SystemMessage(content=agent_def.system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = await llm.ainvoke(messages)
            new_outputs = dict(state.get("agent_outputs", {}))
            new_outputs[agent_def.id] = {
                "agent": agent_def.id,
                "role": agent_def.role,
                "content": response.content,
            }
            return {
                "agent_outputs": new_outputs,
                "current_agent": agent_def.id,
            }
        return node

    graph = StateGraph(PipelineState)

    for agent_def in ALL_AGENTS:
        graph.add_node(agent_def.id, make_node(agent_def))

    # Sequential edges: director -> researcher -> critic -> synthesizer -> END
    for i in range(len(ALL_AGENTS) - 1):
        graph.add_edge(ALL_AGENTS[i].id, ALL_AGENTS[i + 1].id)
    graph.add_edge(ALL_AGENTS[-1].id, END)
    graph.set_entry_point(ALL_AGENTS[0].id)

    return graph.compile()


async def run(task: str, session_id: str, backend: LLMBackend) -> AsyncGenerator[str, None]:
    """Execute the 4-agent pipeline using LangGraph StateGraph."""
    run_id = str(uuid.uuid4())
    _active[run_id] = True

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    llm = create_langchain_llm(backend)
    model_name = backend.value
    app = _build_graph(llm)

    yield sse({
        "type": "pipeline_start",
        "run_id": run_id,
        "model": model_name,
        "framework": "langgraph",
    })

    history: list[dict] = []
    seen_agents: set[str] = set()
    initial_state: PipelineState = {
        "task": task,
        "agent_outputs": {},
        "current_agent": "",
        "run_id": run_id,
    }

    try:
        # Use astream to get node-level updates
        async for event in app.astream(initial_state, stream_mode="updates"):
            if not _active.get(run_id, False):
                yield sse({"type": "cancelled"})
                return

            # event is a dict of {node_name: state_update}
            for node_name, update in event.items():
                agent_def = next((a for a in ALL_AGENTS if a.id == node_name), None)
                if agent_def is None or node_name in seen_agents:
                    continue

                seen_agents.add(node_name)
                outputs = update.get("agent_outputs", {})
                agent_output = outputs.get(node_name, {})
                text = agent_output.get("content", "")

                yield sse({
                    "type": "agent_start",
                    "agent": agent_def.id,
                    "role": agent_def.role,
                    "color": agent_def.color,
                    "icon": agent_def.icon,
                    "description": agent_def.description,
                    "tools": agent_def.tools,
                })

                # Stream in chunks for animation
                for i in range(0, len(text), 5):
                    if not _active.get(run_id, False):
                        yield sse({"type": "cancelled"})
                        return
                    chunk = text[i:i + 5]
                    yield sse({"type": "token", "agent": agent_def.id, "content": chunk})

                history.append({
                    "agent": agent_def.id,
                    "role": agent_def.role,
                    "content": text,
                })
                yield sse({"type": "agent_done", "agent": agent_def.id})

        memory.save_run(session_id, run_id, task, history)
        yield sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield sse({"type": "error", "message": f"LangGraph error: {e}"})
    finally:
        _active.pop(run_id, None)
