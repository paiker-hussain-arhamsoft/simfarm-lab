from backend.agents.base import AgentDef
from backend.agents.director import DIRECTOR
from backend.agents.researcher import RESEARCHER
from backend.agents.critic import CRITIC
from backend.agents.synthesizer import SYNTHESIZER

ALL_AGENTS: list[AgentDef] = [DIRECTOR, RESEARCHER, CRITIC, SYNTHESIZER]

__all__ = ["AgentDef", "ALL_AGENTS", "DIRECTOR", "RESEARCHER", "CRITIC", "SYNTHESIZER"]
