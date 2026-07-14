"""TIER 2 — Intelligence Crew orchestrator.

Runs the 4-member Intelligence Crew sequentially (LlamaIndex retrieval →
LightGBM forecast → social/sentiment strategy → cross-channel fusion). Each
member invokes its registry tools (stubs for now) and then an LLM narrates the
findings. Emits the same SSE contract as TIER 1 plus `tool_call`/`tool_result`
so the frontend renders tool activity identically.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.intelligence_crew import INTELLIGENCE_CREW, CrewAgentDef
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
    region = inp.get("region", "")
    language = inp.get("language", "en")
    if tool_id in ("index_dataset",):
        return {"source": "electoral_roll", "query": inp.get("query", "")}
    if tool_id in ("dialect_analysis",):
        return {"region": region, "language": language}
    if tool_id in ("behavior_forecast",):
        return {"region": region, "segments": "committed,persuadable,disengaged,swing"}
    if tool_id in ("social_targeting",):
        return {"platform": "facebook", "region": region}
    if tool_id in ("narrative_saturation_score",):
        return {"target": inp.get("query", ""), "region": region}
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
            results.append({"tool": tool_id, "error": str(e)})
    return events, results


async def run(query: str, region: str, language: str, session_id: str,
              backend: LLMBackend) -> AsyncGenerator[str, None]:
    run_id = str(uuid.uuid4())
    _active[run_id] = True

    inp = {"query": query, "region": region, "language": language}

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    def check_cancel() -> bool:
        return not _active.get(run_id, False)

    yield sse({"type": "pipeline_start", "run_id": run_id, "model": backend.value,
               "framework": "intelligence_crew", "region": region, "language": language})

    llm = create_langchain_llm(backend)
    history: list[dict] = []

    try:
        for agent in INTELLIGENCE_CREW:
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

        task_label = f"[{region}] {query}"
        memory.save_run(session_id, run_id, task_label, history)
        yield sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield sse({"type": "error", "message": f"Intelligence Crew error: {e}"})
    finally:
        _active.pop(run_id, None)


async def route(query: str, region: str, language: str, session_id: str,
                backend: str = "") -> AsyncGenerator[str, None]:
    """Resolve the backend and run the crew, falling back to demo mode."""
    if backend == "openai" and is_openai_configured():
        resolved = LLMBackend.OPENAI
    elif backend == "ollama" and is_ollama_model_ready():
        resolved = LLMBackend.OLLAMA
    else:
        resolved = detect_llm_backend()

    if resolved is None:
        async for event in run_demo(query, region, language, session_id):
            yield event
        return

    async for event in run(query, region, language, session_id, resolved):
        yield event


def _demo_content(agent: CrewAgentDef, region: str, language: str, query: str) -> str:
    return DEMO_RESPONSES.get(agent.id, f"[Demo response for {agent.role}]").format(
        region=region, language=language, query=query
    )


async def run_demo(query: str, region: str, language: str,
                   session_id: str) -> AsyncGenerator[str, None]:
    """Run the Intelligence Crew with pre-recorded responses (no LLM needed)."""
    run_id = str(uuid.uuid4())
    inp = {"query": query, "region": region, "language": language}

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    yield sse({"type": "pipeline_start", "run_id": run_id, "model": "demo-mode",
               "demo": True, "framework": "intelligence_crew",
               "region": region, "language": language})

    history: list[dict] = []
    for agent in INTELLIGENCE_CREW:
        tool_events, _ = await _run_agent_tools(agent, inp)
        for ev in tool_events:
            yield sse(ev)

        yield sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                   "framework": agent.framework, "color": agent.color, "icon": agent.icon,
                   "description": agent.description, "tools": agent.tools})

        content = _demo_content(agent, region, language, query)
        for i in range(0, len(content), 4):
            yield sse({"type": "token", "agent": agent.id, "content": content[i:i + 4]})

        yield sse({"type": "agent_done", "agent": agent.id})
        history.append({"agent": agent.id, "role": agent.role, "content": content})

    memory.save_run(session_id, run_id, f"[{region}] {query}", history)
    yield sse({"type": "done", "run_id": run_id, "demo": True})


DEMO_RESPONSES: dict[str, str] = {
    "intelligence_lead": """\
## Constituency Intelligence Base — {region}

**Source: Indexed Dataset (Simulated) · LlamaIndex retrieval**

### Demographics
- Registered voters: ~412,000 (58% rural, 42% urban)
- Median age: 27; youth (18–29) share: 38%
- Dominant dialects: Punjabi (Shahmukhi), Saraiki

### Historical Voting Patterns
- Last two cycles: incumbent margin narrowing (11% → 4%)
- Turnout: 51% (2018) → 55% (2024)
- Biradari/clan affiliation remains a strong organizing factor

### Socioeconomic Indicators
- Primary grievances: inflation, load-shedding, agricultural water access
- Development spend perceived as uneven between urban core and periphery

### Open-Source Signals
- Rising local WhatsApp/Facebook group activity around cost-of-living
- Youth-led civic pages gaining reach in {region}""",

    "behavior_forecaster": """\
## LightGBM Forecast (Simulated) — {region}

### Top Feature Importances
1. economic_grievance — 0.28
2. incumbent_fatigue — 0.21
3. biradari_affiliation — 0.17
4. youth_turnout — 0.14
5. development_spend — 0.11

### Voter Segments
| Segment | Share |
|---------|-------|
| Committed | 34% |
| Persuadable | 29% |
| Disengaged | 22% |
| Swing | 15% |

### Projected Turnout
- **52%** (confidence: Medium)
- Swing + Persuadable (44%) are the decisive, model-sensitive blocks
- Youth turnout is the highest-variance driver""",

    "social_media_strategist": """\
## Channel Strategy & Sentiment — {region}

**Language context: {language}**

### Platform → Segment Mapping
- **Facebook groups / WhatsApp broadcast** → older Persuadable + rural Committed
- **TikTok / Instagram Reels** → youth Swing + Disengaged (re-engagement)

### Sentiment Posture (Simulated)
- Positive 29% · Neutral 41% · Negative 30%
- Negative sentiment concentrated on economic themes

### Messaging Themes
- Punjabi (Shahmukhi) / Saraiki-resonant framing on local development & water access
- Youth-facing, short-form content on jobs and cost-of-living
- Keep framing analytical/defensive; avoid manipulative micro-targeting""",

    "crew_synthesizer": """\
## Intelligence Brief — {region}

### 1. Executive Summary
{query} — In {region}, the contest hinges on a 44% Persuadable+Swing bloc driven mainly by economic grievance and incumbent fatigue, with youth turnout the key uncertainty.

### 2. Key Findings
- Incumbent margin has compressed sharply across the last two cycles.
- Economic grievance is the dominant predictive feature.
- Biradari affiliation still structures the Committed base.
- Youth (38% of roll) is the highest-variance segment.
- Sentiment skews neutral-to-negative on cost-of-living.

### 3. Voter Segment Breakdown
Committed 34% · Persuadable 29% · Disengaged 22% · Swing 15%

### 4. Language & Cultural Factors
Punjabi (Shahmukhi) and Saraiki framing materially affects reach; local water/development narratives resonate.

### 5. Strategic Recommendations
1. Prioritize Persuadable outreach on economic relief messaging.
2. Run youth re-engagement on short-form platforms.
3. Localize all content in Shahmukhi/Saraiki for periphery reach.

### 6. Confidence Level
**Medium** — driven by simulated data; real LlamaIndex + LightGBM integration would tighten estimates.""",
}
