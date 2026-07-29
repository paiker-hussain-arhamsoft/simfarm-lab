"""Pre-built exercise scenarios for the Strategic Brain pipeline."""

from __future__ import annotations

SCENARIOS: list[dict] = [
    {
        "id": "sim_farm_detection",
        "name": "SIM Farm Detection Framework",
        "difficulty": "Beginner",
        "color": "#22c55e",
        "icon": "🟢",
        "description": "Design a detection framework for SIM farming operations in Pakistan's telecom ecosystem.",
        "task": "Analyze the SIM farming threat in Pakistan and design a multi-layered detection framework covering CDR analysis, IMEI tracking, and tower distribution monitoring. Consider Jazz, Zong, Telenor, and Ufone carrier ecosystems, PTA regulations, and DIRBS.",
        "expected_topics": [
            "CDR analysis (SMS:Voice ratio)",
            "IMEI rotation detection",
            "Tower concentration analysis",
            "Contact-graph forensics",
            "PTA/DIRBS regulatory framework",
            "PECA 2016 legal considerations",
        ],
        "hints": [
            "Start by identifying what makes SIM farm traffic different from legitimate subscribers.",
            "Consider both per-line statistics AND relationship patterns between lines.",
            "Think about what evidence would hold up in a Pakistani court under PECA 2016.",
        ],
    },
    {
        "id": "deepfake_ethics",
        "name": "AI Deepfake Policy Analysis",
        "difficulty": "Easy",
        "color": "#f59e0b",
        "icon": "🟡",
        "description": "Evaluate the ethical and legal implications of AI-generated deepfakes in political campaigns.",
        "task": "Analyze the ethical implications of AI-generated deepfakes in political campaigns. Design a framework for detecting and watermarking AI-generated media at scale, evaluating legal liability of platforms hosting synthetic media content.",
        "expected_topics": [
            "Deepfake detection methods (visual artifacts, metadata analysis)",
            "C2PA content provenance standard",
            "Platform liability frameworks",
            "Election integrity implications",
            "Watermarking techniques (visible and invisible)",
            "International regulatory comparison",
        ],
        "hints": [
            "Consider both technical detection methods AND legal frameworks.",
        ],
    },
    {
        "id": "apt_response",
        "name": "APT Incident Response",
        "difficulty": "Legendary",
        "color": "#ef4444",
        "icon": "🔴",
        "description": "Develop an incident response plan for a state-sponsored APT targeting critical infrastructure.",
        "task": "A nation-state APT group has compromised your organization's SCADA systems controlling water treatment facilities. Develop a comprehensive incident response plan covering containment, eradication, recovery, and attribution. Consider MITRE ATT&CK ICS framework, NIST SP 800-82, and cross-sector coordination requirements.",
        "expected_topics": [
            "MITRE ATT&CK for ICS mapping",
            "NIST SP 800-82 compliance",
            "SCADA-specific containment strategies",
            "Air-gapping and network segmentation",
            "Attribution methodology",
            "Cross-sector coordination (CISA, FBI, sector ISACs)",
            "Recovery and resilience planning",
        ],
        "hints": [],
    },
    {
        "id": "ransomware_playbook",
        "name": "Ransomware Response Playbook",
        "difficulty": "Beginner",
        "color": "#22c55e",
        "icon": "🟢",
        "description": "Build a step-by-step ransomware response playbook for a mid-size enterprise.",
        "task": "Create a comprehensive ransomware response playbook for a 500-employee manufacturing company. Cover detection, containment, negotiation decision tree, recovery procedures, and post-incident improvements. Include specific tools, timelines, and communication templates.",
        "expected_topics": [
            "Initial detection and triage",
            "Network isolation procedures",
            "Backup validation and recovery",
            "Law enforcement notification (FBI IC3)",
            "Ransom payment decision framework",
            "Communication templates (internal, external, regulatory)",
        ],
        "hints": [
            "Remember: the first 4 hours are critical for containment.",
            "Consider both the technical AND business continuity aspects.",
            "Include a decision tree for whether to pay the ransom.",
        ],
    },
    {
        "id": "zero_trust_migration",
        "name": "Zero Trust Architecture Migration",
        "difficulty": "Easy",
        "color": "#f59e0b",
        "icon": "🟡",
        "description": "Plan a phased migration from perimeter-based security to Zero Trust architecture.",
        "task": "Design a 12-month migration plan from traditional perimeter-based security to Zero Trust Architecture for a financial services firm with 2,000 employees, hybrid cloud (AWS + on-prem), and strict regulatory requirements (PCI-DSS, SOX). Include identity fabric, micro-segmentation, and continuous verification.",
        "expected_topics": [
            "NIST SP 800-207 Zero Trust framework",
            "Identity and Access Management (IAM) overhaul",
            "Micro-segmentation strategy",
            "Continuous verification mechanisms",
            "PCI-DSS and SOX compliance mapping",
            "Phased rollout with minimal disruption",
        ],
        "hints": [
            "Start with identity — it's the foundation of Zero Trust.",
        ],
    },
    {
        "id": "supply_chain_attack",
        "name": "Supply Chain Attack Investigation",
        "difficulty": "Legendary",
        "color": "#ef4444",
        "icon": "🔴",
        "description": "Investigate a suspected supply chain compromise in your CI/CD pipeline.",
        "task": "Your security team has detected anomalous network callbacks from production servers. Initial analysis suggests a compromised dependency in your Node.js CI/CD pipeline (similar to the event-stream or ua-parser-js incidents). Investigate the attack vector, determine blast radius, develop containment and remediation strategy, and design preventive controls.",
        "expected_topics": [
            "Dependency analysis and SBOM generation",
            "Network forensics (C2 beacon detection)",
            "CI/CD pipeline integrity verification",
            "Package registry security (npm audit, lockfile integrity)",
            "Blast radius assessment methodology",
            "Supply chain security controls (Sigstore, SLSA framework)",
        ],
        "hints": [],
    },
]


def get_all_scenarios() -> list[dict]:
    return [
        {k: v for k, v in s.items() if k != "task"}
        for s in SCENARIOS
    ]


def get_scenario(scenario_id: str) -> dict | None:
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return None


def get_scenarios_by_difficulty(difficulty: str) -> list[dict]:
    return [s for s in SCENARIOS if s["difficulty"].lower() == difficulty.lower()]
