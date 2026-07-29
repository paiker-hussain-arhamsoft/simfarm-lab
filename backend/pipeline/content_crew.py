"""TIER 4 simulated content distribution pipeline."""
import json, uuid
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agents.content_crew import CONTENT_CREW, CrewAgentDef
from backend.pipeline.compliance import ComplianceRecorder
from backend.pipeline.llm_config import LLMBackend, create_langchain_llm, detect_llm_backend, is_ollama_model_ready, is_openai_configured
from backend.pipeline.memory import PipelineMemory
from backend.tools import registry
memory=PipelineMemory(); compliance=ComplianceRecorder(); _active={}
def cancel(run_id): _active[run_id]=False; return True
def _sse(data): return f"data: {json.dumps(data)}\n\n"
def _tool_params(t,inp): return {"cms_platform":inp.get("cms_platform",""),"distribution_channel":inp.get("distribution_channel",""),"scenario":inp.get("scenario",""),"objective":inp.get("objective","")}
async def _run_agent_tools(agent: CrewAgentDef,inp):
    out=[]
    for tid in agent.tools:
        spec=registry.get_tool(tid)
        if not spec: continue
        out.append({"type":"tool_call","worker":agent.id,"tool":tid,"provider":spec.provider,"params":_tool_params(tid,inp),"attempt":1})
        try:out.append({"type":"tool_result","worker":agent.id,"tool":tid,"ok":True,"result":await registry.call_tool(tid,**_tool_params(tid,inp))})
        except registry.ToolError as e:out.append({"type":"tool_result","worker":agent.id,"tool":tid,"ok":False,"error":str(e)})
    return out
async def run(inp,session_id,backend: LLMBackend):
    rid=str(uuid.uuid4());_active[rid]=True;yield _sse({"type":"pipeline_start","run_id":rid,"model":backend.value,"framework":"content_crew","scenario":inp.get("scenario","")});history=[];llm=create_langchain_llm(backend)
    try:
        for a in CONTENT_CREW:
            if not _active.get(rid):yield _sse({"type":"cancelled"});return
            for e in await _run_agent_tools(a,inp):yield _sse(e)
            yield _sse({"type":"agent_start","agent":a.id,"role":a.role,"framework":a.framework,"color":a.color,"icon":a.icon,"description":a.description,"tools":a.tools})
            r=await llm.ainvoke([SystemMessage(content=a.system_prompt),HumanMessage(content=a.build_user_prompt(inp,history))]);c=r.content if hasattr(r,"content") else str(r)
            for i in range(0,len(c),5):yield _sse({"type":"token","agent":a.id,"content":c[i:i+5]})
            yield _sse({"type":"agent_done","agent":a.id});history.append({"agent":a.id,"role":a.role,"content":c})
        memory.save_run(session_id,rid,f"[content] {inp.get('objective','')}",history);yield _sse({"type":"done","run_id":rid})
    except Exception as e:yield _sse({"type":"error","message":f"Content error: {e}"})
    finally:_active.pop(rid,None)
async def route(inp,session_id,backend=""):
    r=compliance.record(session_id,"content.plan",f"[content] {inp.get('objective','')} | scenario={inp.get('scenario','')}",inp,inp.get("authorized",False),authorization_ref=inp.get("authorization_ref",""),approver=inp.get("approver",""))
    yield _sse({"type":"compliance","audit_id":r.audit_id,"allowed":r.allowed,"flagged":r.flagged,"reasons":r.reasons,"verdict":r.verdict,"sensitivity":r.sensitivity,"override":r.override})
    if not r.allowed:yield _sse({"type":"compliance_block","audit_id":r.audit_id,"message":"This request was flagged by the safety screen and cannot proceed as-is.","reasons":r.reasons});yield _sse({"type":"done","blocked":True});return
    resolved=LLMBackend.OPENAI if backend=="openai" and is_openai_configured() else LLMBackend.OLLAMA if backend=="ollama" and is_ollama_model_ready() else detect_llm_backend()
    if resolved is None:
        async for e in run_demo(inp,session_id):
            yield e
    else:
        async for e in run(inp,session_id,resolved):
            yield e
async def run_demo(inp,session_id):
    rid=str(uuid.uuid4());yield _sse({"type":"pipeline_start","run_id":rid,"model":"demo-mode","demo":True,"framework":"content_crew","scenario":inp.get("scenario","")});history=[]
    for a in CONTENT_CREW:
        for e in await _run_agent_tools(a,inp):yield _sse(e)
        yield _sse({"type":"agent_start","agent":a.id,"role":a.role,"framework":a.framework,"color":a.color,"icon":a.icon,"description":a.description,"tools":a.tools})
        c=f"## {a.role}\n1. Simulated {a.framework} model for {inp.get('scenario','')} and \"{inp.get('objective','')}\".\n\n## Detection & Countermeasures\nMonitor cadence, authentication, webhook, queue and content-reuse signals; no real distribution occurs.\n\n## Compliance Checklist\n☑ Lab-only ☑ simulation-only ☑ audit-logged."
        for i in range(0,len(c),4):yield _sse({"type":"token","agent":a.id,"content":c[i:i+4]})
        yield _sse({"type":"agent_done","agent":a.id});history.append({"agent":a.id,"role":a.role,"content":c})
    memory.save_run(session_id,rid,f"[content] {inp.get('objective','')}",history);yield _sse({"type":"done","run_id":rid,"demo":True})
