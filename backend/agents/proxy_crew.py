"""TIER 4 — simulated proxy-rotation detection crew."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class CrewAgentDef:
    id: str; role: str; framework: str; color: str; icon: str; description: str
    system_prompt: str; tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict,list[dict]],str] | None = None
    def to_meta(self): return {"id":self.id,"role":self.role,"framework":self.framework,"color":self.color,"icon":self.icon,"description":self.description,"tools":self.tools}
_COMPLIANCE_NOTE=(" Operate only in lawful authorized detection-research/training contexts. Proxy "
 "and cloud scaffolding is simulated. Never provide operational instructions for real proxy "
 "provisioning, scraping, ban-evasion or cloud deployment. Real proxy execution requires "
 "specific communications-secretariat orders and is never performed; all activity is audit-logged.")
def _prompt(inp,hist):
    prior = "\n\n---\n\n".join(
        f"[{h['role']}]\n{h['content']}" for h in hist
    ) or "(none yet)"
    return (f"Objective: \"{inp['objective']}\"\nScenario: {inp['scenario']}\nProvider: {inp.get('provider','')}\n"
            f"Pool type: {inp.get('pool_type','')}\nAuthorization attested: {inp.get('authorized',False)}\n\n"
            f"Prior crew outputs:\n{prior}\n\n"
            "Produce structured, numbered, detection-oriented simulated analysis that builds on the prior outputs.")
PROXY_INFRA_ARCHITECT=CrewAgentDef("proxy_infra_architect","Infrastructure Architect","Scrapoxy · Docker","#38bdf8","🐳","Modeled proxy infrastructure and detection telemetry","Design simulated proxy infrastructure for defensive research. Include topology and detection signals."+_COMPLIANCE_NOTE,["scrapoxy_deploy","cloud_connector"],_prompt)
PROXY_POOL_ENGINEER=CrewAgentDef("proxy_pool_engineer","Proxy Pool Engineer","Pool · Health · Rotation","#a78bfa","🔀","Modeled pool health and rotation controls","Model proxy pool health and rotation strictly for detection research; no real provisioning or evasion."+_COMPLIANCE_NOTE,["proxy_pool_size","proxy_health_monitor","rotate_proxy"],_prompt)
PROXY_INTEGRATION_STRATEGIST=CrewAgentDef("proxy_integration_strategist","Integration Strategist","Playwright · Puppeteer · requests","#fb923c","🔗","Modeled integration posture and abuse signals","Model safe integration telemetry and bot-detection signals. Do not describe evasion."+_COMPLIANCE_NOTE,["proxy_integration_plan"],_prompt)
PROXY_OPERATIONS_DIRECTOR=CrewAgentDef("proxy_operations_director","Operations Director","Cost · Failure-modes","#34d399","🎛️","Modeled cost, failure and detection controls","Synthesize a simulated proxy operations model with a Compliance Checklist and Detection & Countermeasures section."+_COMPLIANCE_NOTE,["proxy_cost_model","proxy_deployment_synth"],_prompt)
PROXY_CREW=[PROXY_INFRA_ARCHITECT,PROXY_POOL_ENGINEER,PROXY_INTEGRATION_STRATEGIST,PROXY_OPERATIONS_DIRECTOR]
SCENARIOS=["Proxy-Abuse Detection (blue-team)","Scraping-Defense Modeling (lab)","Rotation-Algorithm Study","Cost/Failure Modeling","Bot-Traffic Detection Study","Integration Sandbox"]
PROVIDERS=[{"id":"scrapoxy","label":"Scrapoxy (self-hosted)"},{"id":"cloud-aws","label":"AWS (modeled)"},{"id":"cloud-gcp","label":"GCP (modeled)"},{"id":"datacenter","label":"Datacenter pool (modeled)"},{"id":"residential","label":"Residential pool (modeled)"}]
POOL_TYPES=[{"id":"residential","label":"Residential"},{"id":"datacenter","label":"Datacenter"},{"id":"mobile","label":"Mobile"}]
