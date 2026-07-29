"""TIER 4 — simulated IVR detection-research crew."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class CrewAgentDef:
    id: str; role: str; framework: str; color: str; icon: str; description: str
    system_prompt: str; tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict, list[dict]], str] | None = None
    def to_meta(self): return {"id":self.id,"role":self.role,"framework":self.framework,"color":self.color,"icon":self.icon,"description":self.description,"tools":self.tools}

_COMPLIANCE_NOTE = (" Operate only in lawful authorized detection-research/training contexts. "
 "IVR, SIM, GSM and DTMF scaffolding is simulated. Never provide operational instructions "
 "for real robocalls, OTP handling, call fraud or telecom abuse. Real telecom execution "
 "requires specific communications-secretariat orders and is never performed; all activity "
 "is audit-logged.")

def _prompt(inp, hist):
    prior = "\n\n---\n\n".join(
        f"[{h['role']}]\n{h['content']}" for h in hist
    ) or "(none yet)"
    return (f"Objective: \"{inp['objective']}\"\nScenario: {inp['scenario']}\n"
            f"Hardware: {inp.get('hardware_kit','')}\nReach model: {inp.get('reach_model','')}\n"
            f"Authorization attested: {inp.get('authorized',False)}\n\n"
            f"Prior crew outputs:\n{prior}\n\n"
            "Produce structured, numbered, detection-oriented simulated analysis that builds on the prior outputs.")

IVR_HARDWARE_ARCHITECT = CrewAgentDef("ivr_hardware_architect","IVR Hardware Architect","Raspberry Pi + GSM · RASP-IVR","#38bdf8","🍓","Modeled IVR hardware and detection telemetry","Design a simulated IVR hardware topology for blue-team detection. Use numbered output and include detection hooks."+_COMPLIANCE_NOTE,["ivr_hardware_setup"],_prompt)
CALL_FLOW_ENGINEER = CrewAgentDef("call_flow_engineer","Call Flow Engineer","Verboice · VBVoice","#a78bfa","🌳","Modeled call trees and DTMF safety controls","Design a simulated call-flow and DTMF model, never real calls. Include abuse signals and guardrails."+_COMPLIANCE_NOTE,["call_flow_design","dtmf_handler"],_prompt)
RURAL_PENETRATION_STRATEGIST = CrewAgentDef("rural_penetration_strategist","Rural Penetration Strategist","Low-bandwidth · Feature-phone","#fb923c","📻","Modeled reach, latency and accessibility signals","Model low-bandwidth reach strictly for detection and usability research. Include countermeasures."+_COMPLIANCE_NOTE,["rural_reach_model"],_prompt)
IVR_OPERATIONS_DIRECTOR = CrewAgentDef("ivr_operations_director","Operations Director","Routing · Cost","#34d399","🎛️","Modeled routing, cost and abuse detection","Synthesize a simulated IVR operations model with a Compliance Checklist and Detection & Countermeasures section."+_COMPLIANCE_NOTE,["call_route_plan","ivr_cost_model"],_prompt)
IVR_CREW=[IVR_HARDWARE_ARCHITECT,CALL_FLOW_ENGINEER,RURAL_PENETRATION_STRATEGIST,IVR_OPERATIONS_DIRECTOR]
SCENARIOS=["IVR-Fraud Detection (blue-team)","OTP-Scam Awareness IVR (lab)","Rural Outreach Modeling (lab)","Robocall-Abuse Detection Study","Regulator Tabletop (PTA)","Call-Tree Usability Study"]
HARDWARE_KITS=[{"id":"rpi-gsm-sim800","label":"Raspberry Pi + SIM800 GSM HAT"},{"id":"rpi-gsm-usb","label":"Raspberry Pi + USB GSM modem"},{"id":"asterisk-softswitch","label":"Asterisk soft-switch (modeled)"}]
REACH_MODELS=[{"id":"feature-phone","label":"Feature-phone / 2G"},{"id":"low-bandwidth","label":"Low-bandwidth voice"},{"id":"smartphone","label":"Smartphone IVR"}]
