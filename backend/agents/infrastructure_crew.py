"""TIER 4 — simulated SIM-farm and GSM-gateway detection crew."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class CrewAgentDef:
    id: str; role: str; framework: str; color: str; icon: str; description: str
    system_prompt: str; tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict, list[dict]], str] | None = None
    def to_meta(self): return {"id": self.id, "role": self.role, "framework": self.framework, "color": self.color, "icon": self.icon, "description": self.description, "tools": self.tools}

def _prior(history, agent_id):
    return next((h.get("content", "") for h in history if h.get("agent") == agent_id), "")

_COMPLIANCE_NOTE = (" Operate only in lawful authorized detection-research/training contexts. "
 "This is SIMULATED SIM-farm scaffolding for building DETECTION of telecom fraud. Never "
 "provide instructions to run a real SIM farm, activate real SIMs, send real SMS/OTP, harvest "
 "OTPs, or evade DIRBS/PTA/carrier controls. Real execution requires specific communications-"
 "secretariat orders and is never performed here; all output is audit-logged.")

def _prompt(inp, hist):
    prior = "\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist) or "(none yet)"
    return (f"Objective: \"{inp['objective']}\"\nScenario: {inp['scenario']}\n"
            f"Modem: {inp.get('modem_type','')}\nCarrier: {inp.get('carrier','')}\n"
            f"Authorization attested: {inp.get('authorized', False)}\n\nPrior crew outputs:\n{prior}\n\n"
            "Produce structured, numbered, detection-oriented simulated analysis that builds on the prior outputs.")

HARDWARE_ARCHITECT = CrewAgentDef("hardware_architect", "Hardware Architect", "SIM800/SIM900 · Gammu · USB-HUB", "#38bdf8", "🧰", "Modeled modem-pool topology and detection signals", "Design only a simulated modem topology for blue-team detection. Use numbered output and include hardware telemetry detection hooks."+_COMPLIANCE_NOTE, ["modem_topology"], _prompt)
SMSGATE_ENGINEER = CrewAgentDef("smsgate_engineer", "SMSGate Engineer", "SMSgate · Gammu", "#a78bfa", "📡", "Modeled gateway controls and audit signals", "Design a simulated SMS gateway model, never delivery. Include numbered controls and detection signals."+_COMPLIANCE_NOTE, ["smsgate_config", "modem_control"], _prompt)
SIMFARM_STRATEGIST = CrewAgentDef("simfarm_strategist", "SIM Farm Strategist", "Provisioning · Rotation", "#fb923c", "🧩", "Modeled provisioning and carrier-integrity detection", "Model provisioning and rotation strictly for detection research. Include countermeasures and compliance checklist."+_COMPLIANCE_NOTE, ["sim_provision_plan", "sim_activate", "carrier_access"], _prompt)
AUTOMATION_DIRECTOR = CrewAgentDef("automation_director", "Automation Director", "Celery · Orchestration", "#34d399", "⚙️", "Modeled campaign orchestration and abuse detection", "Synthesize a simulated orchestration model with COMPLIANCE CHECKLIST and DETECTION & COUNTERMEASURES sections."+_COMPLIANCE_NOTE, ["campaign_orchestrate", "sms_send", "celery_dispatch"], _prompt)
INFRASTRUCTURE_CREW = [HARDWARE_ARCHITECT, SMSGATE_ENGINEER, SIMFARM_STRATEGIST, AUTOMATION_DIRECTOR]
SCENARIOS = ["Detection Research (blue-team)", "Regulator Tabletop (PTA/DIRBS)", "SIM-Farm Modeling (lab)", "OTP-Abuse Detection Study", "Bulk-SMS Fraud Study", "Carrier-Integrity Study"]
MODEM_TYPES = [{"id":"sim800c-8","label":"SIM800C 8-port pool","ports":8},{"id":"sim900","label":"SIM900","ports":1},{"id":"openvox-vs-gw1600","label":"OpenVox VS-GW1600 16-port gateway","ports":16}]
CARRIERS = [{"id": x.lower(), "label": x} for x in ["Jazz", "Zong", "Telenor", "Ufone", "Intl"]]
