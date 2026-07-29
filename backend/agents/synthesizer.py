"""Synthesizer agent — integrates all contributions into a final answer."""

from backend.agents.base import AgentDef

SYSTEM_PROMPT = """\
You are the Synthesizer agent in the TIER 1 Strategic Brain multi-agent system.

Your role:
1. Integrate all prior agent outputs into a single, coherent, high-quality final response.
2. Resolve contradictions between the Director's plan, Researcher's findings, and Critic's feedback.
3. Produce an actionable deliverable — not a summary of what others said.
4. Structure the output with clear sections: Executive Summary, Key Findings, Recommendations, Next Steps.

Be comprehensive yet concise. The user reads YOUR output as the final answer."""


def build_prompt(task: str, history: list[dict]) -> str:
    parts = [f"Original task:\n\"{task}\""]
    parts.append("Agent contributions:\n")
    for h in history:
        parts.append(f"--- {h.get('role', h.get('agent', 'Unknown'))} ---\n{h.get('content', '')}")
    parts.append("\nSynthesize all of this into a final, polished, actionable response.")
    return "\n\n".join(parts)


SYNTHESIZER = AgentDef(
    id="synthesizer",
    role="Synthesizer",
    color="#a78bfa",
    icon="🧩",
    description="Integrates all contributions into a final polished answer",
    system_prompt=SYSTEM_PROMPT,
    build_user_prompt=build_prompt,
    tools=["output_structuring", "conflict_resolution"],
)
