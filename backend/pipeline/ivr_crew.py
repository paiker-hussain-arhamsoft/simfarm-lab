"""TIER 4 IVR simulation pipeline."""
from __future__ import annotations
import json, uuid
from collections.abc import AsyncGenerator
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agents.ivr_crew import IVR_CREW, CrewAgentDef
from backend.pipeline.compliance import ComplianceRecorder
from backend.pipeline.llm_config import LLMBackend, create_langchain_llm, detect_llm_backend, is_ollama_model_ready, is_openai_configured
from backend.pipeline.memory import PipelineMemory
from backend.tools import registry
memory=PipelineMemory(); compliance=ComplianceRecorder(); _active={}
def cancel(run_id): _active[run_id]=False; return True
def _sse(data): return f"data: {json.dumps(data)}\n\n"
def _tool_params(tool_id,inp):
    return {"ivr_hardware_setup":{"hardware_kit":inp.get("hardware_kit",""),"scenario":inp.get("scenario","")},
            "call_flow_design":{"scenario":inp.get("scenario",""),"objective":inp.get("objective","")},
            "dtmf_handler":{"scenario":inp.get("scenario",""),"objective":inp.get("objective","")},
            "rural_reach_model":{"reach_model":inp.get("reach_model",""),"scenario":inp.get("scenario","")},
            "call_route_plan":{"scenario":inp.get("scenario",""),"objective":inp.get("objective","")},
            "ivr_cost_model":{"scenario":inp.get("scenario",""),"objective":inp.get("objective","")}}.get(tool_id,{})
async def _run_agent_tools(agent: CrewAgentDef,inp):
    out=[]
    for tool_id in agent.tools:
        spec=registry.get_tool(tool_id)
        if not spec: continue
        params=_tool_params(tool_id,inp); out.append({"type":"tool_call","worker":agent.id,"tool":tool_id,"provider":spec.provider,"params":params,"attempt":1})
        try: out.append({"type":"tool_result","worker":agent.id,"tool":tool_id,"ok":True,"result":await registry.call_tool(tool_id,**params)})
        except registry.ToolError as e: out.append({"type":"tool_result","worker":agent.id,"tool":tool_id,"ok":False,"error":str(e)})
    return out
async def run(inp,session_id,backend: LLMBackend)->AsyncGenerator[str,None]:
    run_id=str(uuid.uuid4()); _active[run_id]=True; yield _sse({"type":"pipeline_start","run_id":run_id,"model":backend.value,"framework":"ivr_crew","scenario":inp.get("scenario","")})
    llm=create_langchain_llm(backend); history=[]
    try:
        for agent in IVR_CREW:
            if not _active.get(run_id): yield _sse({"type":"cancelled"}); return
            for e in await _run_agent_tools(agent,inp): yield _sse(e)
            yield _sse({"type":"agent_start","agent":agent.id,"role":agent.role,"framework":agent.framework,"color":agent.color,"icon":agent.icon,"description":agent.description,"tools":agent.tools})
            r=await llm.ainvoke([SystemMessage(content=agent.system_prompt),HumanMessage(content=agent.build_user_prompt(inp,history))]); content=r.content if hasattr(r,"content") else str(r)
            for i in range(0,len(content),5): yield _sse({"type":"token","agent":agent.id,"content":content[i:i+5]})
            yield _sse({"type":"agent_done","agent":agent.id}); history.append({"agent":agent.id,"role":agent.role,"content":content})
        memory.save_run(session_id,run_id,f"[ivr] {inp.get('objective','')}",history); yield _sse({"type":"done","run_id":run_id})
    except Exception as e: yield _sse({"type":"error","message":f"IVR error: {e}"})
    finally: _active.pop(run_id,None)
async def route(inp,session_id,backend=""):
    r=compliance.record(session_id,"ivr.plan",f"[ivr] {inp.get('objective','')} | scenario={inp.get('scenario','')}",inp,inp.get("authorized",False),authorization_ref=inp.get("authorization_ref",""),approver=inp.get("approver",""))
    yield _sse({"type":"compliance","audit_id":r.audit_id,"allowed":r.allowed,"flagged":r.flagged,"reasons":r.reasons,"verdict":r.verdict,"sensitivity":r.sensitivity,"override":r.override})
    if not r.allowed:
        yield _sse({"type":"compliance_block","audit_id":r.audit_id,"message":"This request was flagged by the safety screen and cannot proceed as-is. It has been recorded in the audit log (id "+r.audit_id+") for legal review. Reasons: "+"; ".join(r.reasons)+". IVR is simulation / detection-research only — remove requests for real calls, DTMF, robocalls or OTP handling, or clear through the accountable Legal-Proxy Override with a real authorization reference and approver.","reasons":r.reasons}); yield _sse({"type":"done","blocked":True}); return
    resolved=LLMBackend.OPENAI if backend=="openai" and is_openai_configured() else LLMBackend.OLLAMA if backend=="ollama" and is_ollama_model_ready() else detect_llm_backend()
    if resolved is None:
        async for e in run_demo(inp,session_id): yield e
    else:
        async for e in run(inp,session_id,resolved): yield e
async def run_demo(inp,session_id):
    rid=str(uuid.uuid4()); yield _sse({"type":"pipeline_start","run_id":rid,"model":"demo-mode","demo":True,"framework":"ivr_crew","scenario":inp.get("scenario","")}); history=[]
    for a in IVR_CREW:
        for e in await _run_agent_tools(a,inp): yield _sse(e)
        yield _sse({"type":"agent_start","agent":a.id,"role":a.role,"framework":a.framework,"color":a.color,"icon":a.icon,"description":a.description,"tools":a.tools})
        content=DEMO_RESPONSES[a.id].format(objective=inp.get("objective",""),scenario=inp.get("scenario",""),hardware_kit=inp.get("hardware_kit",""),reach_model=inp.get("reach_model",""))
        for i in range(0,len(content),4): yield _sse({"type":"token","agent":a.id,"content":content[i:i+4]})
        yield _sse({"type":"agent_done","agent":a.id}); history.append({"agent":a.id,"role":a.role,"content":content})
    memory.save_run(session_id,rid,f"[ivr] {inp.get('objective','')}",history); yield _sse({"type":"done","run_id":rid,"demo":True})
DEMO_RESPONSES={a.id:f"## {a.role}\n1. Simulated {a.framework} model for {{scenario}} and \"{{objective}}\".\n2. No calls, DTMF, OTPs, recipients, or telecom systems are contacted.\n\n## Detection & Countermeasures\nModel call-tree timing, retry patterns, channel occupancy, and accessibility anomalies.\n\n## Compliance Checklist\n☑ Lab-only ☑ simulation-only ☑ communications-secretariat prerequisite recorded ☑ audit-logged." for a in IVR_CREW}
