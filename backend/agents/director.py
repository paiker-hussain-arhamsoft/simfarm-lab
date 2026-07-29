"""Director agent — decomposes tasks and orchestrates the pipeline."""

from backend.agents.base import AgentDef

SYSTEM_PROMPT = """\
You are the Director agent in the TIER 1 Strategic Brain multi-agent system.

Your role:
1. Receive the user's task and decompose it into 3-5 clear sub-tasks.
2. Assign focus areas for each downstream agent (Researcher, Critic, Synthesizer).
3. Identify the threat domain, scope, and constraints.
4. Flag any ambiguities or missing context upfront.

Be concise, decisive, and strategic. Use numbered lists and clear headers.
Do NOT solve the task yourself — orchestrate it for the team."""


def build_prompt(task: str, history: list[dict]) -> str:
    return (
        f"Incoming task:\n\"{task}\"\n\n"
        "Decompose this into sub-tasks and direct the other agents. Be concise."
    )


DIRECTOR = AgentDef(
    id="director",
    role="Director",
    color="#60a5fa",
    icon="🎯",
    description="Decomposes tasks and orchestrates the agent pipeline",
    system_prompt=SYSTEM_PROMPT,
    build_user_prompt=build_prompt,
    tools=["task_decomposition", "scope_analysis"],
)
