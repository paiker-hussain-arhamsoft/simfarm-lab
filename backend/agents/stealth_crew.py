"""TIER 4 — simulated stealth and anti-detection detection crew."""
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class CrewAgentDef:
    id: str; role: str; framework: str; color: str; icon: str; description: str
    system_prompt: str; tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict, list[dict]], str] | None = None
    def to_meta(self): return {"id":self.id,"role":self.role,"framework":self.framework,"color":self.color,"icon":self.icon,"description":self.description,"tools":self.tools}

_NOTE=(" Operate only in lawful authorized defensive detection-research/training contexts. "
       "Browser fingerprint, WAF and infrastructure scaffolding is simulated. Never provide "
       "instructions for real spoofing, Cloudflare bypass, scraping or evasion. Real execution "
       "requires specific communications-secretariat orders and is never performed; all activity is audit-logged.")

def _prompt(inp, hist):
    prior="\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist) or "(none yet)"
    return (f"Objective: \"{inp['objective']}\"\nScenario: {inp['scenario']}\n"
            f"Evasion target: {inp.get('evasion_target','')}\nBrowser engine: {inp.get('browser_engine','')}\n"
            f"Authorization attested: {inp.get('authorized',False)}\n\nPrior crew outputs:\n{prior}\n\n"
            "Produce structured, numbered, detection-oriented simulated analysis that builds on the prior outputs.")

STEALTH_CREW=[
 CrewAgentDef("stealth_browser_architect","Stealth Browser Architect","playwright-extra · evasion patches","#38bdf8","🥷","Modeled browser fingerprint signals and defensive telemetry","Model the 11 playwright-extra patch families and explain how blue teams detect each."+_NOTE,["stealth_patch_model","canvas_spoof_model","webrtc_spoof_model","human_behavior_model"],_prompt),
 CrewAgentDef("cloudflare_bypass_engineer","Cloudflare Bypass Engineer","FlareSolverr · Docker","#a78bfa","🛡️","Modeled WAF challenge telemetry","Model challenge-solving telemetry only and describe defensive WAF signals."+_NOTE,["flaresolverr_model","challenge_bypass_model"],_prompt),
 CrewAgentDef("browser_infra_strategist","Browser Infrastructure Strategist","Browserbase · Scrapoxy · Playwright","#fb923c","🏗️","Modeled browser infrastructure detection signals","Compare modeled infrastructure patterns for blue-team detection."+_NOTE,["fingerprint_pool_model","session_isolation_model","ip_warmup_model"],_prompt),
 CrewAgentDef("stealth_operations_director","Operations Director","Detection evasion · Stealth testing","#34d399","🎛️","Modeled evasion matrix and defensive checklist","Synthesize a 12-signal detection evasion matrix and checklist with Compliance Checklist and Detection & Countermeasures sections."+_NOTE,["evasion_matrix_model","stealth_checklist_model"],_prompt),
]
SCENARIOS=["Anti-Detection Research (blue-team)","Cloudflare Defense Modeling (lab)","Fingerprint-Evasion Detection Study","Bot-Detection Training","Stealth-Audit Tabletop","Browser Automation Security Review"]
EVASION_TARGETS=[{"id":"cloudflare","label":"Cloudflare"},{"id":"ddos-guard","label":"DDoS-GUARD"},{"id":"akamai","label":"Akamai (modeled)"},{"id":"generic-waf","label":"Generic WAF (modeled)"}]
BROWSER_ENGINES=[{"id":"chromium","label":"Chromium (Playwright)"},{"id":"firefox","label":"Firefox (Playwright)"},{"id":"webkit","label":"WebKit (Playwright)"}]
