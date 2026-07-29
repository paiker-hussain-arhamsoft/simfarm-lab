"""TIER 4 — simulated content distribution detection crew."""
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class CrewAgentDef:
    id: str; role: str; framework: str; color: str; icon: str; description: str
    system_prompt: str; tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict, list[dict]], str] | None = None
    def to_meta(self): return {"id":self.id,"role":self.role,"framework":self.framework,"color":self.color,"icon":self.icon,"description":self.description,"tools":self.tools}

_NOTE=(" Operate only in lawful authorized defensive detection-research/training contexts. "
       "Email, CMS and social distribution scaffolding is simulated. Never create real emails, "
       "posts, subscribers, campaigns or deployments. Real execution requires specific communications-secretariat "
       "orders and is never performed; all activity is audit-logged.")
def _prompt(inp,hist):
    prior="\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist) or "(none yet)"
    return (f"Objective: \"{inp['objective']}\"\nScenario: {inp['scenario']}\n"
            f"CMS platform: {inp.get('cms_platform','')}\nDistribution channel: {inp.get('distribution_channel','')}\n"
            f"Authorization attested: {inp.get('authorized',False)}\n\nPrior crew outputs:\n{prior}\n\n"
            "Produce structured, numbered, detection-oriented simulated analysis that builds on the prior outputs.")
CONTENT_CREW=[
 CrewAgentDef("marketing_automation_architect","Marketing Automation Architect","Mautic · Docker","#38bdf8","📧","Modeled campaign and authentication telemetry","Design simulated drip, scoring and email-authentication models for detection research."+_NOTE,["mautic_campaign_model","lead_scoring_model","email_auth_model"],_prompt),
 CrewAgentDef("cms_engineer","CMS Engineer","Strapi · AI plugins","#a78bfa","📝","Modeled CMS lifecycle and webhook signals","Design simulated CMS lifecycle and webhook topology for defensive analysis."+_NOTE,["strapi_lifecycle_model","webhook_chain_model"],_prompt),
 CrewAgentDef("social_media_manager","Social Media Manager","Postiz · AI captions","#fb923c","📱","Modeled scheduling and repurposing telemetry","Design simulated scheduling and cross-platform detection signals."+_NOTE,["postiz_scheduler_model","cross_platform_model"],_prompt),
 CrewAgentDef("content_operations_director","Operations Director","Docker Compose · Calendar","#34d399","🎛️","Modeled content operations and cost controls","Synthesize a simulated compose plan, calendar and cost model with Compliance Checklist and Detection & Countermeasures."+_NOTE,["content_calendar_model","content_cost_model"],_prompt),
]
SCENARIOS=["Drip Campaign Modeling (lab)","Lead Nurture Automation Study","Multi-Channel Content Strategy","Satellite Site Distribution Study","Social Scheduler Comparison","Email Deliverability Audit"]
CMS_PLATFORMS=[{"id":"strapi","label":"Strapi"},{"id":"wordpress","label":"WordPress (modeled)"},{"id":"ghost","label":"Ghost (modeled)"}]
DISTRIBUTION_CHANNELS=[{"id":"email","label":"Email (Mautic)"},{"id":"social","label":"Social (Postiz)"},{"id":"blog","label":"Blog/CMS"},{"id":"webhook","label":"Webhook chain"}]
