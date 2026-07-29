"""TIER 4 infrastructure crew pipeline with compliance and SSE events."""
from __future__ import annotations
import json
import uuid
from collections.abc import AsyncGenerator
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agents.infrastructure_crew import INFRASTRUCTURE_CREW, CrewAgentDef
from backend.pipeline.compliance import ComplianceRecorder
from backend.pipeline.llm_config import LLMBackend, create_langchain_llm, detect_llm_backend, is_ollama_model_ready, is_openai_configured
from backend.pipeline.memory import PipelineMemory
from backend.tools import registry

memory = PipelineMemory(); compliance = ComplianceRecorder(); _active = {}
def cancel(run_id): _active[run_id] = False; return True
def _sse(data): return f"data: {json.dumps(data)}\n\n"

def _tool_params(tool_id, inp):
    mapping = {
        "modem_topology": {"modem_type": inp.get("modem_type", ""), "ports": 8, "hub_layout": "modeled USB hub"},
        "smsgate_config": {"gateway": "SMSgate", "pool_size": 8},
        "modem_control": {"command": "status (simulated)"},
        "sim_provision_plan": {"count": 8, "carriers": [inp.get("carrier", "")]},
        "sim_activate": {"iccid": "iccid-lab-0001"},
        "carrier_access": {"carrier": inp.get("carrier", "")},
        "campaign_orchestrate": {"tasks": ["detection-signature-model"], "schedule": "modeled"},
        "sms_send": {"to": "lab-sink", "body": "simulated detection fixture"},
        "celery_dispatch": {"task": "infrastructure-detection-model"},
    }
    return mapping.get(tool_id, {})

async def _run_agent_tools(agent: CrewAgentDef, inp):
    events = []
    for tool_id in agent.tools:
        spec = registry.get_tool(tool_id)
        if not spec: continue
        params = _tool_params(tool_id, inp)
        events.append({"type":"tool_call","worker":agent.id,"tool":tool_id,"provider":spec.provider,"params":params,"attempt":1})
        try: events.append({"type":"tool_result","worker":agent.id,"tool":tool_id,"ok":True,"result":await registry.call_tool(tool_id, **params)})
        except registry.ToolError as e: events.append({"type":"tool_result","worker":agent.id,"tool":tool_id,"ok":False,"error":str(e)})
    return events

async def run(inp, session_id, backend: LLMBackend) -> AsyncGenerator[str, None]:
    run_id = str(uuid.uuid4()); _active[run_id] = True
    yield _sse({"type":"pipeline_start","run_id":run_id,"model":backend.value,"framework":"infrastructure_crew","scenario":inp.get("scenario","")})
    history=[]; llm=create_langchain_llm(backend)
    try:
        for agent in INFRASTRUCTURE_CREW:
            if not _active.get(run_id): yield _sse({"type":"cancelled"}); return
            for event in await _run_agent_tools(agent, inp): yield _sse(event)
            yield _sse({"type":"agent_start","agent":agent.id,"role":agent.role,"framework":agent.framework,"color":agent.color,"icon":agent.icon,"description":agent.description,"tools":agent.tools})
            resp=await llm.ainvoke([SystemMessage(content=agent.system_prompt),HumanMessage(content=agent.build_user_prompt(inp,history))])
            content=resp.content if hasattr(resp,"content") else str(resp)
            for i in range(0,len(content),5): yield _sse({"type":"token","agent":agent.id,"content":content[i:i+5]})
            yield _sse({"type":"agent_done","agent":agent.id}); history.append({"agent":agent.id,"role":agent.role,"content":content})
        memory.save_run(session_id,run_id,f"[infrastructure] {inp.get('objective','')}",history); yield _sse({"type":"done","run_id":run_id})
    except Exception as e: yield _sse({"type":"error","message":f"Infrastructure error: {e}"})
    finally: _active.pop(run_id,None)

async def route(inp, session_id, backend=""):
    summary=f"[infrastructure] {inp.get('objective','')} | scenario={inp.get('scenario','')}"
    result=compliance.record(session_id,"infrastructure.plan",summary,inp,inp.get("authorized",False),authorization_ref=inp.get("authorization_ref",""),approver=inp.get("approver",""))
    yield _sse({"type":"compliance","audit_id":result.audit_id,"allowed":result.allowed,"flagged":result.flagged,"reasons":result.reasons,"verdict":result.verdict,"sensitivity":result.sensitivity,"override":result.override})
    if not result.allowed:
        yield _sse({"type":"compliance_block","audit_id":result.audit_id,"message":"This request was flagged by the safety screen and cannot proceed as-is. It has been recorded in the audit log (id "+result.audit_id+") for legal review. Reasons: "+"; ".join(result.reasons)+". Infrastructure orchestration is simulation / detection-research only — remove requests for real telecom execution, SIM activation, SMS delivery, OTP harvesting, or carrier evasion, or (for authorized legal users) clear it via the accountable Legal-Proxy Override with a real authorization reference and approver — a claimed origin alone is not sufficient.","reasons":result.reasons})
        yield _sse({"type":"done","blocked":True}); return
    resolved = LLMBackend.OPENAI if backend=="openai" and is_openai_configured() else LLMBackend.OLLAMA if backend=="ollama" and is_ollama_model_ready() else detect_llm_backend()
    if resolved is None:
        async for event in run_demo(inp,session_id): yield event
    else:
        async for event in run(inp,session_id,resolved): yield event

async def run_demo(inp, session_id):
    run_id=str(uuid.uuid4()); yield _sse({"type":"pipeline_start","run_id":run_id,"model":"demo-mode","demo":True,"framework":"infrastructure_crew","scenario":inp.get("scenario","")})
    history=[]
    for agent in INFRASTRUCTURE_CREW:
        for event in await _run_agent_tools(agent,inp): yield _sse(event)
        yield _sse({"type":"agent_start","agent":agent.id,"role":agent.role,"framework":agent.framework,"color":agent.color,"icon":agent.icon,"description":agent.description,"tools":agent.tools})
        content=DEMO_RESPONSES[agent.id].format(objective=inp.get("objective",""),scenario=inp.get("scenario",""),modem_type=inp.get("modem_type",""),carrier=inp.get("carrier",""))
        for i in range(0,len(content),4): yield _sse({"type":"token","agent":agent.id,"content":content[i:i+4]})
        yield _sse({"type":"agent_done","agent":agent.id}); history.append({"agent":agent.id,"role":agent.role,"content":content})
    memory.save_run(session_id,run_id,f"[infrastructure] {inp.get('objective','')}",history); yield _sse({"type":"done","run_id":run_id,"demo":True})

DEMO_RESPONSES={a.id:f"## {a.role}\n1. Simulated {a.framework} model for {{scenario}} and \"{{objective}}\".\n2. No hardware, SIMs, carriers, recipients, OTPs, or workers are contacted.\n\n## Detection & Countermeasures\nModel timing, topology, carrier concentration, queue behavior, and audit anomalies for blue-team detection.\n\n## Compliance Checklist\n☑ Lab-only ☑ simulation-only ☑ communications-secretariat prerequisite recorded ☑ audit-logged." for a in INFRASTRUCTURE_CREW}
