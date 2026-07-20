"""TIER 3 — Persona Orchestration crew definitions.

A synthetic-persona design & orchestration crew adapted to Docker/FastAPI/Ollama.
Four agents run sequentially: Persona Architect (synthetic identity design,
ElizaOS) → Behavior Architect (behavioral modeling / interaction scripting,
Botpress/LangGraph) → Voice & Dialect Specialist (dialect calibration, voice
mapping) → Orchestration Engineer (multi-persona coordination, fleet lifecycle,
Socioboard / Playwright automation planning).

Offline-first and simulated: every tool is a stub — no real synthetic accounts
are created, no real social posting is performed, and no stealth / fingerprint-
evasion against live platforms is done. The crew designs and plans for authorized
research, red/blue-team training, and detection of coordinated inauthentic
behavior. Runs are compliance-screened and audit-logged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CrewAgentDef:
    id: str
    role: str
    framework: str
    color: str
    icon: str
    description: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict, list[dict]], str] | None = None

    def to_meta(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "framework": self.framework,
            "color": self.color,
            "icon": self.icon,
            "description": self.description,
            "tools": self.tools,
        }


def _prior(history: list[dict], agent_id: str) -> str:
    for h in history:
        if h.get("agent") == agent_id:
            return h.get("content", "")
    return ""


_COMPLIANCE_NOTE = (
    " Operate strictly within a lawful, authorized research / training context. "
    "These are SIMULATED personas for red/blue-team exercises and for building "
    "DETECTION of coordinated inauthentic behavior — not for deployment. Never "
    "provide instructions to create real fraudulent accounts, evade platform "
    "integrity / bot-detection, spoof device or browser fingerprints, or run real "
    "astroturfing / disinformation. Assume all activity is audit-logged for legal "
    "review; keep everything inside the lab."
)

PERSONA_ARCHITECT = CrewAgentDef(
    id="persona_architect",
    role="Persona Architect",
    framework="ElizaOS · 7-layer",
    color="#38bdf8",
    icon="🪪",
    description="Synthetic identity design (backstory, demographics, digital footprint)",
    system_prompt=(
        "You are the Persona Architect for the TIER 3 Persona Orchestration crew. Design "
        "SIMULATED synthetic identities using the ElizaOS 7-layer character architecture "
        "(identity, backstory, demographics, psychographics, digital-footprint, voice, "
        "goals). Output: 1) DESIGN GOALS & LAB SCOPE; 2) the 7 LAYERS for a representative "
        "persona (clearly labeled synthetic/lab-only); 3) DIGITAL-FOOTPRINT design at a "
        "conceptual level (no real account creation); 4) DIVERSITY / realism notes for a "
        "fleet; 5) DETECTION HOOKS (signals a defender could use to spot such personas). "
        "Everything is simulated and stays in the lab." + _COMPLIANCE_NOTE
    ),
    tools=["persona_design"],
    build_user_prompt=lambda inp, hist: (
        f"Objective: \"{inp['objective']}\"\nScenario: {inp['scenario']}\n"
        f"Platform: {inp['platform']}\nRegion: {inp['region']}\n"
        f"Authorization attested: {inp['authorized']}\n\n"
        "Design the synthetic persona architecture (simulated / lab-only)."
    ),
)

BEHAVIOR_ARCHITECT = CrewAgentDef(
    id="behavior_architect",
    role="Behavior Architect",
    framework="Botpress · LangGraph",
    color="#a78bfa",
    icon="🧠",
    description="Behavioral modeling, response patterns, interaction scripting",
    system_prompt=(
        "You are the Behavior Architect for the Persona Orchestration crew. Using a "
        "Botpress / LangGraph orchestration model, design SIMULATED behavioral models for "
        "the personas: response patterns, memories, goals, and interaction scripting. "
        "Output: 1) BEHAVIOR GRAPH (states, triggers, transitions) at a conceptual level; "
        "2) POSTING/INTERACTION CADENCE model; 3) MEMORY & GOAL model per persona; "
        "4) GUARDRAILS (what the simulated agents must never do); 5) DETECTION SIGNALS "
        "(behavioral tells defenders can use). No live agents are deployed; modeling only."
        + _COMPLIANCE_NOTE
    ),
    tools=["behavior_model"],
    build_user_prompt=lambda inp, hist: (
        f"Objective: \"{inp['objective']}\"\nScenario: {inp['scenario']}\n\n"
        f"Persona architecture:\n{_prior(hist, 'persona_architect')}\n\n"
        "Design the behavioral models and interaction scripting (simulated)."
    ),
)

VOICE_DIALECT_SPECIALIST = CrewAgentDef(
    id="voice_dialect_specialist",
    role="Voice & Dialect Specialist",
    framework="Coqui / Chatterbox · ElevenLabs",
    color="#fb923c",
    icon="🗣️",
    description="Regional dialect calibration, speech-pattern tuning, voice-engine mapping",
    system_prompt=(
        "You are the Voice & Dialect Specialist for the Persona Orchestration crew. "
        "Calibrate SIMULATED regional dialect and speech patterns for the personas and map "
        "each to a voice engine (offline Coqui XTTS-v2 / Chatterbox preferred; ElevenLabs "
        "optional/online only when explicitly enabled). Output: 1) DIALECT PROFILE per "
        "region (e.g. Punjabi Shahmukhi, Saraiki, Urdu, English); 2) SPEECH-PATTERN tuning "
        "(register, cadence, code-switching) at a conceptual level; 3) VOICE-ENGINE MAPPING "
        "(offline-first, with online as optional fallback); 4) AUTHENTICITY vs DETECTION "
        "notes. No audio is synthesized here; mapping/config only." + _COMPLIANCE_NOTE
    ),
    tools=["voice_dialect_map"],
    build_user_prompt=lambda inp, hist: (
        f"Objective: \"{inp['objective']}\"\nRegion: {inp['region']}\n\n"
        f"Persona architecture:\n{_prior(hist, 'persona_architect')}\n\n"
        "Provide the dialect calibration and voice-engine mapping (offline-first)."
    ),
)

ORCHESTRATION_ENGINEER = CrewAgentDef(
    id="orchestration_engineer",
    role="Orchestration Engineer",
    framework="Socioboard · Playwright · Lifecycle",
    color="#34d399",
    icon="🛰️",
    description="Multi-persona coordination, fleet management, lifecycle",
    system_prompt=(
        "You are the Orchestration Engineer for the Persona Orchestration crew. Synthesize "
        "the crew inputs into a SIMULATED multi-persona coordination & lifecycle plan. "
        "Reference Socioboard-style multi-account dashboards and Playwright/Puppeteer/"
        "Selenium automation ONLY as a conceptual plan — do NOT provide real account "
        "creation, real posting, stealth, or fingerprint-evasion; explicitly refuse those "
        "and note platform-integrity / terms-of-service constraints. Output: 1) EXECUTIVE "
        "SUMMARY; 2) FLEET COORDINATION model (scale, scheduling, deconfliction — modeled); "
        "3) LIFECYCLE (design → simulated provision → simulated monitor → retire); "
        "4) AUTOMATION PLAN (conceptual, no evasion); 5) DETECTION & COUNTERMEASURES (how a "
        "defender detects and disrupts such a fleet); 6) COMPLIANCE CHECKLIST (authorization "
        "on file, lab-only, no real deployment, audit trail). Numbered and operational."
        + _COMPLIANCE_NOTE
    ),
    tools=["fleet_orchestrate", "browser_automation_plan"],
    build_user_prompt=lambda inp, hist: (
        f"Objective:\n\"{inp['objective']}\"\nScenario: {inp['scenario']}\n"
        f"Platform: {inp['platform']}\nAuthorization attested: {inp['authorized']}\n\n"
        "Crew outputs:\n\n"
        + "\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist)
        + "\n\nSynthesize into the final persona-orchestration plan (simulated / lab-only)."
    ),
)


PERSONA_CREW: list[CrewAgentDef] = [
    PERSONA_ARCHITECT,
    BEHAVIOR_ARCHITECT,
    VOICE_DIALECT_SPECIALIST,
    ORCHESTRATION_ENGINEER,
]


SCENARIOS: list[str] = [
    "Detection Research (blue-team)",
    "Red/Blue-Team Exercise",
    "Astroturfing Simulation (lab)",
    "Influence-Operation Tabletop",
    "Bot-Fleet Modeling",
    "Platform-Integrity Study",
]

PLATFORMS: list[dict] = [
    {"id": "lab-dashboard", "label": "Lab Dashboard", "online": False,
     "note": "Sandboxed, in-lab only"},
    {"id": "socioboard", "label": "Socioboard (sim)", "online": False,
     "note": "Multi-account dashboard concept"},
]

REGIONS: list[dict] = [
    {"id": "pk-punjab", "label": "Punjab (Shahmukhi)", "lang": "pa"},
    {"id": "pk-saraiki", "label": "Saraiki Belt", "lang": "skr"},
    {"id": "pk-urdu", "label": "Urdu (national)", "lang": "ur"},
    {"id": "intl-en", "label": "International (English)", "lang": "en"},
]
