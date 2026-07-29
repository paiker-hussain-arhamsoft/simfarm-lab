"""Specialized worker agents the Supervisor can spawn dynamically.

These map to the "functional clusters" in the system topology: an Intelligence
worker for analysis, a Media worker for content generation, an Infrastructure
worker for routing control, and a Persona worker for character logic. Each
worker is bound to a tool *category* from the registry — so when real tools are
added per-tier, the workers automatically gain those capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkerDef:
    id: str
    role: str
    color: str
    icon: str
    description: str
    system_prompt: str
    tool_category: str  # which registry category this worker can call
    keywords: list[str] = field(default_factory=list)  # trigger words in the plan

    def to_meta(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "color": self.color,
            "icon": self.icon,
            "description": self.description,
            "tool_category": self.tool_category,
            "keywords": self.keywords,
        }


INTELLIGENCE_WORKER = WorkerDef(
    id="intelligence",
    role="Intelligence Worker",
    color="#38bdf8",
    icon="🛰️",
    description="Pulls and indexes dataset records; scores narratives/sentiment",
    system_prompt=(
        "You are an Intelligence Worker. You analyze data and, when useful, call "
        "analysis tools (dataset indexing, narrative saturation scoring). Report "
        "concrete findings grounded in the tool results you are given."
    ),
    tool_category="analysis",
    keywords=["analy", "research", "intelligence", "data", "record", "sentiment", "index"],
)

MEDIA_WORKER = WorkerDef(
    id="media",
    role="Media Worker",
    color="#f472b6",
    icon="🎬",
    description="Generates localized multimedia packages (video/voice/image)",
    system_prompt=(
        "You are a Media Worker. You produce localized multimedia deliverables "
        "and, when useful, call media-generation tools. Describe the media package "
        "you would produce and summarize any tool results."
    ),
    tool_category="media",
    keywords=["media", "video", "voice", "content", "distribut", "clip", "audio"],
)

INFRA_WORKER = WorkerDef(
    id="infrastructure",
    role="Infrastructure Worker",
    color="#fbbf24",
    icon="🛠️",
    description="Controls routing: proxy rotation, load-balancing, scaffolding",
    system_prompt=(
        "You are an Infrastructure Worker. You manage routing and connectivity and, "
        "when an endpoint fails, call infrastructure tools (proxy rotation, load "
        "balancer adjustment) to re-route. Report the routing changes you made."
    ),
    tool_category="infrastructure",
    keywords=["infra", "rout", "proxy", "network", "node", "scaffold", "endpoint", "load"],
)

PERSONA_WORKER = WorkerDef(
    id="persona",
    role="Persona Worker",
    color="#c084fc",
    icon="🎭",
    description="Adjusts persona/character profile logic",
    system_prompt=(
        "You are a Persona Worker. You manage character/persona profiles and, when "
        "useful, call persona tools to adjust them. Report the persona logic applied."
    ),
    tool_category="persona",
    keywords=["persona", "character", "profile", "bot", "identity"],
)


ALL_WORKERS: list[WorkerDef] = [
    INTELLIGENCE_WORKER,
    MEDIA_WORKER,
    INFRA_WORKER,
    PERSONA_WORKER,
]

WORKERS_BY_ID: dict[str, WorkerDef] = {w.id: w for w in ALL_WORKERS}


def select_workers(plan_text: str) -> list[WorkerDef]:
    """Pick which workers to spawn based on keyword hits in the Director's plan.

    Always includes the Intelligence worker (analysis is the baseline stage).
    """
    text = plan_text.lower()
    selected: list[WorkerDef] = []
    for worker in ALL_WORKERS:
        if any(kw in text for kw in worker.keywords):
            selected.append(worker)
    if INTELLIGENCE_WORKER not in selected:
        selected.insert(0, INTELLIGENCE_WORKER)
    return selected
