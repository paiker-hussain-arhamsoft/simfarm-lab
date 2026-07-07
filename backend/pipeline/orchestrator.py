"""Pipeline orchestrator — routes to the selected framework and LLM backend."""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import AsyncGenerator
from typing import Optional

from openai import AsyncOpenAI

from backend.agents import ALL_AGENTS, AgentDef
from backend.pipeline import autogen_orchestrator, langgraph_orchestrator
from backend.pipeline.llm_config import (
    LLMBackend,
    detect_llm_backend,
    get_available_backends,
    get_default_framework,
    get_openai_api_key,
    get_openai_base_url,
    get_openai_model,
    is_ollama_model_ready,
    is_openai_configured,
)
from backend.pipeline.memory import PipelineMemory

# Direct-mode LLM client (legacy fallback)
_client: Optional[AsyncOpenAI] = None

memory = PipelineMemory()


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=get_openai_api_key(), base_url=get_openai_base_url())
    return _client


def is_llm_configured() -> bool:
    return is_openai_configured() or is_ollama_model_ready()


def cancel_pipeline(run_id: str) -> bool:
    """Cancel a running pipeline across all frameworks."""
    if autogen_orchestrator.cancel(run_id):
        return True
    if langgraph_orchestrator.cancel(run_id):
        return True
    # Check direct-mode active set
    if run_id in _active:
        _active[run_id] = False
        return True
    return False


def get_config() -> dict:
    """Return current framework/backend configuration."""
    return {
        "default_framework": get_default_framework(),
        "frameworks": [
            {"id": "autogen", "name": "AutoGen", "description": "Microsoft multi-agent orchestration (RoundRobinGroupChat)"},
            {"id": "langgraph", "name": "LangGraph", "description": "LangChain stateful workflows (StateGraph)"},
            {"id": "direct", "name": "Direct", "description": "Simple sequential OpenAI calls (no framework)"},
        ],
        "backends": get_available_backends(),
        "llm_configured": is_llm_configured(),
    }


async def route_pipeline(
    task: str,
    session_id: str,
    framework: str = "",
    backend: str = "",
) -> AsyncGenerator[str, None]:
    """Route pipeline execution to the selected framework and backend."""
    if not framework:
        framework = get_default_framework()

    # Resolve backend
    resolved_backend = None
    if backend == "openai" and is_openai_configured():
        resolved_backend = LLMBackend.OPENAI
    elif backend == "ollama" and is_ollama_model_ready():
        resolved_backend = LLMBackend.OLLAMA
    else:
        resolved_backend = detect_llm_backend()

    # No LLM available → demo mode
    if resolved_backend is None:
        async for event in run_demo_pipeline(task, session_id):
            yield event
        return

    # Route to framework
    if framework == "autogen":
        async for event in autogen_orchestrator.run(task, session_id, resolved_backend):
            yield event
    elif framework == "langgraph":
        async for event in langgraph_orchestrator.run(task, session_id, resolved_backend):
            yield event
    else:
        # Direct mode — use the legacy sequential OpenAI pipeline
        async for event in run_direct_pipeline(task, session_id, resolved_backend):
            yield event


# ── Direct (legacy) pipeline ────────────────────────────────────────

_active: dict[str, bool] = {}


async def run_direct_pipeline(task: str, session_id: str, backend: LLMBackend) -> AsyncGenerator[str, None]:
    """Execute the 4-agent pipeline using direct sequential LLM calls."""
    run_id = str(uuid.uuid4())
    _active[run_id] = True
    history: list[dict] = []

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    # Build appropriate client
    if backend == LLMBackend.OLLAMA:
        from backend.pipeline.llm_config import get_ollama_host, get_ollama_model
        client = AsyncOpenAI(api_key="ollama", base_url=f"{get_ollama_host()}/v1")
        model = get_ollama_model()
    else:
        client = _get_client()
        model = get_openai_model()

    yield sse({"type": "pipeline_start", "run_id": run_id, "model": model, "framework": "direct"})

    try:
        for agent in ALL_AGENTS:
            if not _active.get(run_id, False):
                yield sse({"type": "cancelled"})
                return

            yield sse({
                "type": "agent_start",
                "agent": agent.id,
                "role": agent.role,
                "color": agent.color,
                "icon": agent.icon,
                "description": agent.description,
                "tools": agent.tools,
            })

            user_prompt = agent.build_user_prompt(task, history)
            full_content = ""

            try:
                stream = await client.chat.completions.create(
                    model=model,
                    max_tokens=4096,
                    messages=[
                        {"role": "system", "content": agent.system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,
                )

                async for chunk in stream:
                    if not _active.get(run_id, False):
                        yield sse({"type": "cancelled"})
                        return
                    content = chunk.choices[0].delta.content if chunk.choices else None
                    if content:
                        full_content += content
                        yield sse({"type": "token", "agent": agent.id, "content": content})

            except Exception as e:
                error_msg = str(e)
                yield sse({"type": "agent_error", "agent": agent.id, "error": error_msg})
                full_content = f"[Agent error: {error_msg}]"

            history.append({
                "agent": agent.id,
                "role": agent.role,
                "content": full_content,
            })
            yield sse({"type": "agent_done", "agent": agent.id})

        memory.save_run(session_id, run_id, task, history)
        yield sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield sse({"type": "error", "message": str(e)})
    finally:
        _active.pop(run_id, None)


# ── Demo mode ───────────────────────────────────────────────────────

DEMO_RESPONSES: dict[str, str] = {
    "director": """\
## Task Decomposition

### Sub-task 1: Threat Landscape Mapping
**Assigned to: Researcher**
Map the current threat landscape for SIM farm operations in Pakistan's telecom ecosystem. Identify key carriers (Jazz, Zong, Telenor, Ufone), regulatory bodies (PTA, DIRBS), and known fraud patterns.

### Sub-task 2: Detection Gap Analysis
**Assigned to: Researcher + Critic**
Analyze existing detection mechanisms (IMEI tracking, CDR analysis, tower distribution) and identify gaps that sophisticated operators exploit.

### Sub-task 3: HUMINT Integration Assessment
**Assigned to: Critic**
Evaluate the feasibility and ethics of integrating human intelligence gathering techniques with automated detection systems.

### Sub-task 4: Actionable Framework
**Assigned to: Synthesizer**
Produce a detection framework combining automated signals with HUMINT, including risk scoring, escalation procedures, and legal considerations.

### Constraints
- Must comply with PTA regulations and PECA 2016
- Detection methods must be defensible in legal proceedings
- System must handle 10,000+ subscriber records efficiently""",

    "researcher": """\
## Research Findings

### 1. Pakistan SIM Farm Landscape
Pakistan's telecom sector has **187M+ mobile subscribers** across 4 MNOs. SIM farming is prevalent due to:
- Cheap prepaid SIMs (PKR 100-200 per activation)
- Biometric verification gaps (NADRA/PTA system has ~3% false acceptance)
- High demand for OTP harvesting (JazzCash, Easypaisa, social media)

**Known case studies:**
- 2023 PTA crackdown: 2.8M SIMs blocked via DIRBS (Device Identification Registration & Blocking System)
- FIA Cybercrime Wing Operation "Clean Sweep": 47 SIM farms raided in Punjab
- Telenor/Jazz joint detection program flagged 12,000 anomalous subscribers using CDR clustering

### 2. Detection Techniques (MITRE ATT&CK Mapping)
| Technique | MITRE ID | Detection Method |
|-----------|----------|-----------------|
| SIM Swapping | T1078.004 | IMEI change frequency analysis |
| Bulk SMS | T1566.001 | Traffic pattern anomaly (SMS:Voice ratio > 10:1) |
| OTP Harvesting | T1111 | Temporal regularity detection (CV < 0.3) |
| Tower Concentration | T1200 | Geographic clustering analysis |

### 3. Contact-Graph Forensics
The most durable signal against "Ghost Farms" (Legendary difficulty):
- **Reciprocity score** < 0.15 flags one-way communication patterns
- **Clustering coefficient** < 0.10 flags star-shaped ego-networks
- Combined: 94.2% precision in controlled studies (Karachi telecom dataset, 2023)

### 4. Regulatory Framework
- **PECA 2016** Section 32: Unauthorized SIM activation carries 3-year imprisonment
- **PTA SIM Registration Rules 2019**: Mandatory biometric verification
- **DIRBS**: Real-time IMEI blocking capability (average response: 72 hours)""",

    "critic": """\
## Critical Analysis

### Gaps Identified

**1. Biometric Bypass Not Addressed**
The Researcher mentions 3% false acceptance rate but doesn't address the elephant in the room: most Pakistani SIM farms use **complicit retailer networks**, not biometric spoofing. Detection should focus on retailer activation patterns, not just subscriber behavior.

**2. CDR Analysis Timing Assumptions**
The CV < 0.3 threshold for temporal regularity assumes bots send at fixed intervals. Modern SIM farm software (SMSgate, gammu-based) implements **Poisson jitter** — random delays that push CV to 0.4-0.6, evading this threshold. The Legendary-level simulator correctly models this.

**3. Legal Evidence Chain Weakness**
Contact-graph analysis produces *leads*, not *evidence*. Pakistani courts require corroborating physical evidence (Section 164 CrPC). The framework needs a clear handoff protocol: automated signal → HUMINT confirmation → physical raid → chain of custody.

**4. Scale Limitations**
Processing 10,000+ subscriber contact graphs with O(n²) clustering computation is computationally expensive. Need to specify: batch processing window, sampling strategy, or approximate algorithms (e.g., MinHash for clustering estimation).

### Improvements
- Add **retailer-level analysis** as a detection layer (activation velocity per CNIC agent)
- Raise temporal threshold to CV < 0.5 to catch jitter-equipped farms
- Define explicit **HUMINT trigger criteria** and legal handoff checklist
- Specify computational budget and approximation strategy for graph analysis""",

    "synthesizer": """\
## Executive Summary

This framework provides a multi-layered detection system for SIM farm operations in Pakistan, combining automated CDR/network analysis with human intelligence gathering, designed to produce legally defensible evidence.

## Detection Framework: TIER 1 Strategic Brain Output

### Layer 1: Automated Signal Detection
| Signal | Threshold | Confidence | Action |
|--------|-----------|-----------|--------|
| Tower concentration | >15 SIMs per tower per carrier | Medium | Flag for L2 |
| SMS:Voice ratio | >8:1 over 30 days | Medium | Flag for L2 |
| Temporal regularity | CV < 0.5 (adjusted per Critic) | Medium | Flag for L2 |
| IMEI rotation | >2 changes per 90 days | High | Flag for L2 |
| Retailer velocity | >50 activations per CNIC agent per day | High | Direct escalation |

### Layer 2: Contact-Graph Forensics
- Reciprocity < 0.15 AND clustering < 0.10 → Strong lead
- Apply to all Layer 1 flagged subscribers
- Computational strategy: MinHash approximation for clustering, process in 24-hour batch windows

### Layer 3: HUMINT Confirmation
**Trigger criteria** (any 2 of):
- Layer 2 positive result
- Physical address shared by 5+ flagged SIMs
- Retailer flagged in Layer 1

**Handoff checklist:**
1. Document automated evidence chain (timestamps, algorithms, thresholds)
2. Obtain PTA authorization for physical surveillance
3. Coordinate with FIA Cybercrime Wing
4. Execute under Section 164 CrPC requirements
5. Maintain chain of custody for all physical evidence

### Next Steps
1. Deploy Layer 1 automated detection on historical CDR dataset (90-day window)
2. Validate thresholds against known SIM farm cases (2023 PTA dataset)
3. Establish MOUs with FIA and PTA for HUMINT escalation path
4. Build training curriculum for SOC analysts (use this lab's Beginner → Legendary progression)

### Risk Assessment
- **False positive rate**: Estimated 8-12% at Layer 1, reduced to <2% after Layer 2
- **Legal risk**: Framework designed for PECA 2016 compliance; all HUMINT requires PTA authorization
- **Operational risk**: Retailer-level detection may face industry pushback; recommend phased rollout""",
}


async def run_demo_pipeline(task: str, session_id: str) -> AsyncGenerator[str, None]:
    """Run a demo pipeline with pre-recorded responses (no LLM needed)."""
    run_id = str(uuid.uuid4())

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    yield sse({"type": "pipeline_start", "run_id": run_id, "model": "demo-mode", "demo": True, "framework": "demo"})

    history: list[dict] = []
    for agent in ALL_AGENTS:
        yield sse({
            "type": "agent_start",
            "agent": agent.id,
            "role": agent.role,
            "color": agent.color,
            "icon": agent.icon,
            "description": agent.description,
            "tools": agent.tools,
        })

        content = DEMO_RESPONSES.get(agent.id, f"[Demo response for {agent.role}]")

        for i in range(0, len(content), 3):
            chunk = content[i:i + 3]
            yield sse({"type": "token", "agent": agent.id, "content": chunk})

        history.append({"agent": agent.id, "role": agent.role, "content": content})
        yield sse({"type": "agent_done", "agent": agent.id})

    memory.save_run(session_id, run_id, task, history)
    yield sse({"type": "done", "run_id": run_id, "demo": True})
