"""Base agent definition shared by all four pipeline agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AgentDef:
    id: str
    role: str
    color: str
    icon: str  # emoji fallback for terminal / API consumers
    description: str
    system_prompt: str
    build_user_prompt: Callable[[str, list[dict]], str]
    tools: list[str] = field(default_factory=list)

    def to_meta(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "color": self.color,
            "icon": self.icon,
            "description": self.description,
            "tools": self.tools,
        }
