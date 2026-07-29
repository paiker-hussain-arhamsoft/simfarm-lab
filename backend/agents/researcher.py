"""Researcher agent — deep analysis, context, and factual grounding."""

from backend.agents.base import AgentDef

SYSTEM_PROMPT = """\
You are the Researcher agent in the TIER 1 Strategic Brain multi-agent system.

Your role:
1. Provide deep analysis, relevant context, supporting evidence, and factual grounding.
2. Reference real-world case studies, regulatory frameworks, and technical standards.
3. Map findings to established frameworks (MITRE ATT&CK, NIST, OWASP) where applicable.
4. Cite specific data points, statistics, and known incidents.

Be thorough but structured. Use bullet points, headers, and tables where helpful.
Ground every claim in evidence — do not speculate without flagging it."""


def build_prompt(task: str, history: list[dict]) -> str:
    directive = ""
    for h in history:
        if h.get("agent") == "director":
            directive = h.get("content", "")
            break
    parts = [f"Original task:\n\"{task}\""]
    if directive:
        parts.append(f"Director's plan:\n{directive}")
    parts.append("Provide your research and analysis to support this task.")
    return "\n\n".join(parts)


RESEARCHER = AgentDef(
    id="researcher",
    role="Researcher",
    color="#34d399",
    icon="🔬",
    description="Provides deep analysis, context, and factual grounding",
    system_prompt=SYSTEM_PROMPT,
    build_user_prompt=build_prompt,
    tools=["threat_research", "framework_mapping", "case_study_lookup"],
)
