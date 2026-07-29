"""Analysis tools that the Strategic Brain agents conceptually use.

These represent the tools each agent has access to. In the current implementation
they describe capabilities; future versions will wire them to real tool-calling APIs.
"""

from __future__ import annotations

AGENT_TOOLS: dict[str, list[dict]] = {
    "director": [
        {
            "id": "task_decomposition",
            "name": "Task Decomposition Engine",
            "description": "Breaks complex cybersecurity tasks into structured sub-tasks with dependency graphs.",
            "category": "orchestration",
        },
        {
            "id": "scope_analysis",
            "name": "Scope Analyzer",
            "description": "Evaluates task boundaries, identifies constraints, and maps stakeholders.",
            "category": "orchestration",
        },
    ],
    "researcher": [
        {
            "id": "threat_research",
            "name": "Threat Intelligence Lookup",
            "description": "Queries threat intelligence databases (MITRE ATT&CK, CVE, NVD) for relevant TTPs and vulnerabilities.",
            "category": "intelligence",
        },
        {
            "id": "framework_mapping",
            "name": "Framework Mapper",
            "description": "Maps findings to established frameworks (NIST, OWASP, ISO 27001, CIS Controls).",
            "category": "compliance",
        },
        {
            "id": "case_study_lookup",
            "name": "Case Study Database",
            "description": "Retrieves relevant real-world incident case studies and lessons learned.",
            "category": "intelligence",
        },
    ],
    "critic": [
        {
            "id": "assumption_testing",
            "name": "Assumption Stress-Tester",
            "description": "Systematically challenges stated and unstated assumptions in the analysis.",
            "category": "validation",
        },
        {
            "id": "risk_analysis",
            "name": "Risk Matrix Generator",
            "description": "Evaluates likelihood and impact of identified risks; produces risk matrices.",
            "category": "validation",
        },
        {
            "id": "gap_detection",
            "name": "Gap Detector",
            "description": "Identifies missing coverage areas, blind spots, and unaddressed threat vectors.",
            "category": "validation",
        },
    ],
    "synthesizer": [
        {
            "id": "output_structuring",
            "name": "Output Structuring Engine",
            "description": "Organizes multi-agent contributions into coherent, actionable deliverables.",
            "category": "synthesis",
        },
        {
            "id": "conflict_resolution",
            "name": "Conflict Resolver",
            "description": "Identifies and resolves contradictions between agent outputs.",
            "category": "synthesis",
        },
    ],
}


def get_all_tools() -> list[dict]:
    """Return a flat list of all tools across all agents."""
    tools = []
    for agent_id, agent_tools in AGENT_TOOLS.items():
        for tool in agent_tools:
            tools.append({**tool, "agent": agent_id})
    return tools


def get_tools_for_agent(agent_id: str) -> list[dict]:
    return AGENT_TOOLS.get(agent_id, [])
