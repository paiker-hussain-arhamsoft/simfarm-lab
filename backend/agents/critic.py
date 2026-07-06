"""Critic agent — stress-tests assumptions and sharpens the solution."""

from backend.agents.base import AgentDef

SYSTEM_PROMPT = """\
You are the Critic agent in the TIER 1 Strategic Brain multi-agent system.

Your role:
1. Rigorously challenge, stress-test, and refine the Director's plan and Researcher's findings.
2. Identify gaps, risks, false assumptions, edge cases, and blind spots.
3. Evaluate feasibility — what could go wrong in practice?
4. Suggest concrete improvements, not just criticism.

Be constructive but direct. Your critique sharpens the final output.
Never rubber-stamp — always find something to improve."""


def build_prompt(task: str, history: list[dict]) -> str:
    directive = ""
    research = ""
    for h in history:
        if h.get("agent") == "director":
            directive = h.get("content", "")
        elif h.get("agent") == "researcher":
            research = h.get("content", "")
    parts = [f"Original task:\n\"{task}\""]
    if directive:
        parts.append(f"Director's plan:\n{directive}")
    if research:
        parts.append(f"Researcher's analysis:\n{research}")
    parts.append("Challenge this work. What's missing, risky, or could be improved?")
    return "\n\n".join(parts)


CRITIC = AgentDef(
    id="critic",
    role="Critic",
    color="#f59e0b",
    icon="⚡",
    description="Stress-tests assumptions and sharpens the solution",
    system_prompt=SYSTEM_PROMPT,
    build_user_prompt=build_prompt,
    tools=["assumption_testing", "risk_analysis", "gap_detection"],
)
