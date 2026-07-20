"""TIER 2 — Cyber Crew orchestrator.

Runs the 4-member Cyber Crew (attack-surface strategy → DAST → TLS fingerprint
analysis → validation & report). Every run is compliance-screened and audit-
logged before execution. Policy is allow-by-default: the run proceeds and is
logged; access is only limited when the safety screen flags the request (e.g.
an unauthorized-intrusion / evasion request). Flagged requests are still
recorded and the crew emits a compliance notice instead of a plan.

Everything is simulated and defensive: the security tools are stubs — no real
scanning, exploitation, or reconnaissance is performed.

Emits the same SSE contract as the other crews plus tool + compliance events.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.cyber_crew import CYBER_CREW, CrewAgentDef
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
    if tool_id == "recon_scan":
        return {"tool": inp.get("scan_tool", "nmap"), "target": inp.get("target", "")}
    if tool_id == "cai_redteam":
        return {"scope": inp.get("engagement", "")}
    if tool_id == "dast_scan":
        return {"tool": "zap", "target": inp.get("target", "")}
    if tool_id == "ja3_fingerprint":
        return {"host": inp.get("target", "")}
    if tool_id == "exploit_validate":
        return {"module": "auxiliary/scanner", "target": inp.get("target", "")}
    if tool_id == "osint_lookup":
        return {"subject": inp.get("target", "")}
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
                "framework": "cyber_crew", "engagement": inp.get("engagement", "")})

    llm = create_langchain_llm(backend)
    history: list[dict] = []

    try:
        for agent in CYBER_CREW:
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

        memory.save_run(session_id, run_id, f"[cyber] {inp.get('target', '')}", history)
        yield _sse({"type": "done", "run_id": run_id})

    except Exception as e:
        yield _sse({"type": "error", "message": f"Cyber Crew error: {e}"})
    finally:
        _active.pop(run_id, None)


async def route(inp: dict, session_id: str, backend: str = "") -> AsyncGenerator[str, None]:
    """Compliance-screen and audit-log, then run the crew (allow-by-default)."""
    summary = f"[cyber] {inp.get('target', '')} | engagement={inp.get('engagement', '')}"
    result = compliance.record(
        session_id, "cyber.plan", summary, inp, inp.get("authorized", False),
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
                "review. Reasons: " + "; ".join(result.reasons) + ". Cyber engagements must be "
                "lawful and scope-authorized; remove the flagged content or attest authorization."
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
    """Run the Cyber Crew with pre-recorded responses (no LLM needed)."""
    run_id = str(uuid.uuid4())

    yield _sse({"type": "pipeline_start", "run_id": run_id, "model": "demo-mode",
                "demo": True, "framework": "cyber_crew", "engagement": inp.get("engagement", "")})

    history: list[dict] = []
    for agent in CYBER_CREW:
        for ev in await _run_agent_tools(agent, inp):
            yield _sse(ev)

        yield _sse({"type": "agent_start", "agent": agent.id, "role": agent.role,
                    "framework": agent.framework, "color": agent.color, "icon": agent.icon,
                    "description": agent.description, "tools": agent.tools})

        content = DEMO_RESPONSES.get(agent.id, f"[Demo response for {agent.role}]").format(
            target=inp.get("target", ""), engagement=inp.get("engagement", ""),
            scan_tool=inp.get("scan_tool", ""),
        )
        for i in range(0, len(content), 4):
            yield _sse({"type": "token", "agent": agent.id, "content": content[i:i + 4]})

        yield _sse({"type": "agent_done", "agent": agent.id})
        history.append({"agent": agent.id, "role": agent.role, "content": content})

    memory.save_run(session_id, run_id, f"[cyber] {inp.get('target', '')}", history)
    yield _sse({"type": "done", "run_id": run_id, "demo": True})


DEMO_RESPONSES: dict[str, str] = {
    "red_team_strategist": """\
## Scope & Rules of Engagement
Authorized {engagement} against "{target}". Non-destructive, rate-limited, deconflicted with blue team.

## Recon Plan
Nmap host discovery → top-1000 TCP + service/version detection (`-sV`), no aggressive scripts on prod.

## OpenVAS Assessment
Authenticated + unauthenticated scan profiles; export findings to the report pipeline.

## Prioritized Attack Surface (MITRE ATT&CK)
- Exposed services → T1046 (Network Service Discovery)
- Web endpoints → T1190 (Exploit Public-Facing App) — assessment only

## Safety Controls
Rate limits, maintenance window, rollback plan. Assessment-only; no exploitation.""",

    "dast_engineer": """\
## Crawl / Spider Strategy
Authenticated ZAP spider + AJAX spider; scope-restricted to in-scope hosts.

## Active-Scan Policy
OWASP Top 10 coverage, non-destructive settings, no fuzzing of destructive endpoints.

## Key Checks
Injection, XSS, broken access control, security misconfig, missing headers, cookie flags.

## Triage
De-duplicate, confirm reflected vs stored, drop known false positives.

## Remediation Guidance
Parameterized queries, output encoding, CSP + security headers, SameSite cookies.""",

    "tls_fingerprint_engineer": """\
## Fingerprint Inventory
Capture JA3/JA3S for known-good clients; baseline the fleet (detection focus).

## Cipher-Suite / TLS Posture
Flag TLS 1.0/1.1, weak ciphers; recommend TLS 1.2+ with modern suites.

## Detection Use
Alert on anomalous JA3 hashes (possible C2/malware clients) against the baseline.

## Hardening
Disable legacy protocols, enable HSTS, pin approved cipher suites. Detection & hardening only — no spoofing/evasion.""",

    "security_director": """\
## Executive Summary
Authorized {engagement} on "{target}" completed (simulated). Findings validated and prioritized; fully audit-logged.

## Validated Findings
1. Missing security headers — Medium (CVSS 5.3), confirmed via DAST.
2. Legacy TLS offered — Medium (CVSS 5.9), confirmed via fingerprint posture.

## OSINT Exposure
Public DNS records and one simulated leaked-credential indicator for owned assets.

## Remediation Roadmap
Headers + CSP (quick win) → TLS hardening → credential rotation → re-test.

## Detection & Response
JA3 anomaly alerting, WAF rules, log the changes.

## Compliance Checklist
☑ Written authorization on file ☑ Scope adhered ☑ Data handled per policy ☑ Audit trail retained ☑ No live exploitation.""",
}
