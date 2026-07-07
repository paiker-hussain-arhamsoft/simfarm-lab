"""AutoGen-based multi-agent orchestration with SSE streaming."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat

from backend.agents import ALL_AGENTS
from backend.pipeline.llm_config import LLMBackend, create_autogen_model_client
from backend.pipeline.memory import PipelineMemory

memory = PipelineMemory()

_active: dict[str, bool] = {}


def cancel(run_id: str) -> bool:
    if run_id in _active:
        _active[run_id] = False
        return True
    return False


async def run(task: str, session_id: str, backend: LLMBackend) -> AsyncGenerator[str, None]:
    """Execute the 4-agent pipeline using AutoGen RoundRobinGroupChat."""
    run_id = str(uuid.uuid4())
    _active[run_id] = True

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    model_client = create_autogen_model_client(backend)
    model_name = backend.value

    # Create AutoGen agents from our agent definitions
    autogen_agents = []
    for agent_def in ALL_AGENTS:
        ag = AssistantAgent(
            name=agent_def.id,
            model_client=model_client,
            system_message=agent_def.system_prompt,
        )
        autogen_agents.append(ag)

    # RoundRobinGroupChat: each agent takes one turn in order
    termination = MaxMessageTermination(max_messages=len(ALL_AGENTS))
    team = RoundRobinGroupChat(autogen_agents, termination_condition=termination)

    yield sse({
        "type": "pipeline_start",
        "run_id": run_id,
        "model": model_name,
        "framework": "autogen",
    })

    history: list[dict] = []
    seen_agents: set[str] = set()

    try:
        async for event in team.run_stream(task=task):
            if not _active.get(run_id, False):
                yield sse({"type": "cancelled"})
                return

            if isinstance(event, TaskResult):
                break

            # AutoGen messages have .source (agent name) and .content
            source = getattr(event, "source", None)
            content = getattr(event, "content", None)

            if source is None or content is None:
                continue

            # Skip the initial user message
            if source == "user":
                continue

            agent_def = next((a for a in ALL_AGENTS if a.id == source), None)
            if agent_def is None or source in seen_agents:
                continue

            seen_agents.add(source)

            yield sse({
                "type": "agent_start",
                "agent": agent_def.id,
                "role": agent_def.role,
                "color": agent_def.color,
                "icon": agent_def.icon,
                "description": agent_def.description,
                "tools": agent_def.tools,
            })

            text = str(content)
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
        yield sse({"type": "error", "message": f"AutoGen error: {e}"})
    finally:
        _active.pop(run_id, None)
        await model_client.close()
