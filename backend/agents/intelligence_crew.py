"""TIER 2 — Intelligence Crew agent definitions.

A specialized crew for voter-behavior forecasting and cross-channel intelligence
fusion, modeled after the topology note: LlamaIndex retrieval + LightGBM
forecasting + Meta-Llama-3.1-8B dialect analysis (Punjabi Shahmukhi / Saraiki).

Each crew member carries a `framework` label (the real tool/model it stands for)
and a list of registry `tools` it invokes. Tools are stubs today and are swapped
for real integrations without changing the orchestrator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CrewAgentDef:
    id: str
    role: str
    framework: str  # real model/tool this agent maps to
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


INTELLIGENCE_LEAD = CrewAgentDef(
    id="intelligence_lead",
    role="Intelligence Lead",
    framework="LlamaIndex",
    color="#38bdf8",
    icon="🛰️",
    description="Open-source research & voter-behavior profiling via indexed retrieval",
    system_prompt=(
        "You are the Intelligence Lead of TIER 2: Intelligence Crew, modeled after a "
        "LlamaIndex retrieval-augmented pipeline. Using the indexed dataset results you "
        "are given, profile the constituency: demographics, historical voting patterns, "
        "socioeconomic indicators, and the key open-source intelligence signals. Structure "
        "the output with clear categories. Clearly label invented figures as "
        "'Indexed Dataset (Simulated)'."
    ),
    tools=["index_dataset", "dialect_analysis"],
    build_user_prompt=lambda inp, hist: (
        f"Analysis request: \"{inp['query']}\"\n"
        f"Target region: {inp['region']}\n"
        f"Primary language context: {inp['language']}\n\n"
        "Profile this region from the indexed/dialect tool results. Provide a structured intelligence base."
    ),
)

BEHAVIOR_FORECASTER = CrewAgentDef(
    id="behavior_forecaster",
    role="Behavior Forecaster",
    framework="LightGBM",
    color="#fb923c",
    icon="📈",
    description="Predictive modeling & demographic voter segmentation",
    system_prompt=(
        "You are the Behavior Forecaster of TIER 2: Intelligence Crew, implementing a "
        "LightGBM gradient-boosted forecasting methodology. Using the forecast tool "
        "results and the Intelligence Lead's profile, output probabilistic voter-behavior "
        "predictions: top feature importances, voter segments (Committed / Persuadable / "
        "Disengaged / Swing) with percentages, and projected turnout with confidence. "
        "Format like an ML forecast report labeled 'LightGBM Forecast (Simulated)'."
    ),
    tools=["behavior_forecast"],
    build_user_prompt=lambda inp, hist: (
        f"Region: {inp['region']}\nQuery: \"{inp['query']}\"\n\n"
        f"Intelligence base:\n{_prior(hist, 'intelligence_lead')}\n\n"
        "Produce the LightGBM-style voter behavior forecast from the tool results."
    ),
)

SOCIAL_MEDIA_STRATEGIST = CrewAgentDef(
    id="social_media_strategist",
    role="Social Media Strategist",
    framework="social-intel",
    color="#4ade80",
    icon="📣",
    description="Platform targeting & sentiment analysis across channels",
    system_prompt=(
        "You are the Social Media Strategist of TIER 2: Intelligence Crew. Using the "
        "social-targeting tool results, the region profile, and the behavior forecast, "
        "recommend channel strategy: which platforms reach which voter segments, sentiment "
        "posture, and culturally resonant messaging themes (reference Punjabi/Saraiki where "
        "relevant). Keep it operational and defensive/analytical in framing."
    ),
    tools=["social_targeting", "narrative_saturation_score"],
    build_user_prompt=lambda inp, hist: (
        f"Region: {inp['region']}\nLanguage: {inp['language']}\nQuery: \"{inp['query']}\"\n\n"
        f"Intelligence base:\n{_prior(hist, 'intelligence_lead')}\n\n"
        f"Forecast:\n{_prior(hist, 'behavior_forecaster')}\n\n"
        "Recommend platform targeting and sentiment-aware messaging from the tool results."
    ),
)

SYNTHESIZER = CrewAgentDef(
    id="crew_synthesizer",
    role="Synthesizer",
    framework="Cross-channel fusion",
    color="#c084fc",
    icon="🧩",
    description="Cross-channel intelligence fusion into an operational brief",
    system_prompt=(
        "You are the Synthesizer of TIER 2: Intelligence Crew. Fuse all crew intelligence "
        "into a final operational brief with: 1) EXECUTIVE SUMMARY, 2) KEY FINDINGS (5 "
        "bullets), 3) VOTER SEGMENT BREAKDOWN with percentages, 4) LANGUAGE & CULTURAL "
        "FACTORS, 5) STRATEGIC RECOMMENDATIONS (3), 6) CONFIDENCE LEVEL (Low/Medium/High) "
        "with reasoning. Be decisive and operational — a brief, not an essay."
    ),
    tools=[],
    build_user_prompt=lambda inp, hist: (
        f"Query: \"{inp['query']}\"\nRegion: {inp['region']}\nLanguage: {inp['language']}\n\n"
        "Crew intelligence:\n\n"
        + "\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist)
        + "\n\nSynthesize into the final intelligence brief."
    ),
)


INTELLIGENCE_CREW: list[CrewAgentDef] = [
    INTELLIGENCE_LEAD,
    BEHAVIOR_FORECASTER,
    SOCIAL_MEDIA_STRATEGIST,
    SYNTHESIZER,
]

CREW_BY_ID: dict[str, CrewAgentDef] = {a.id: a for a in INTELLIGENCE_CREW}


# Region / language options surfaced to the frontend.
REGIONS: list[str] = [
    "Lahore Central", "Multan", "Bahawalpur", "Rahim Yar Khan", "DG Khan",
    "Faisalabad North", "Gujranwala", "Sialkot", "Rawalpindi", "Muzaffargarh",
    "Khanewal", "Lodhran", "Vehari", "Jhang", "Sargodha", "Mianwali",
]

LANGUAGES: list[dict] = [
    {"code": "en", "label": "English", "native": "English"},
    {"code": "pa", "label": "Punjabi (Shahmukhi)", "native": "پنجابی (شاہ مکھی)"},
    {"code": "skr", "label": "Saraiki", "native": "سرائیکی"},
    {"code": "ur", "label": "Urdu", "native": "اردو"},
]
