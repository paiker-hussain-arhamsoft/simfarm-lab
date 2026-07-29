"""TIER 2 — Cyber Crew agent definitions.

A DEFENSIVE security crew adapted to Docker/FastAPI/Ollama. Four agents run
sequentially: Red Team Strategist (attack-surface mapping, Nmap/OpenVAS) →
DAST Engineer (dynamic analysis, OWASP ZAP/Burp) → TLS Fingerprint Engineer
(JA3 analysis, cipher-suite profiling) → Security Director (validation, OSINT,
report synthesis).

Offline-first and simulated: every security tool is a stub — no real scanning,
exploitation, fingerprint spoofing, or reconnaissance is performed. The crew
plans, maps, and reports for authorized, lawful, defensive / lab engagements
only. Runs are compliance-screened and audit-logged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CrewAgentDef:
    id: str
    role: str
    framework: str
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


_COMPLIANCE_NOTE = (
    " Operate strictly within a lawful, authorized, defensive engagement. Assume "
    "explicit written scope authorization is required and all activity is audit-"
    "logged for legal review. Never provide operational instructions for illegal "
    "intrusion, evasion, or attacks on systems you are not authorized to test; "
    "focus on assessment, detection, hardening, and reporting. Do not output real "
    "exploit payloads or fingerprint-spoofing/evasion techniques."
)

RED_TEAM_STRATEGIST = CrewAgentDef(
    id="red_team_strategist",
    role="Red Team Strategist",
    framework="Nmap · OpenVAS",
    color="#f87171",
    icon="🎯",
    description="Attack-surface mapping and reconnaissance planning",
    system_prompt=(
        "You are the Red Team Strategist for the Cyber Crew, an authorized penetration-"
        "testing lead. Design the attack-surface mapping plan for an in-scope engagement "
        "using Nmap (port/service discovery) and OpenVAS (vulnerability assessment). "
        "Output: 1) SCOPE & RULES OF ENGAGEMENT confirmation; 2) RECON PLAN (host/port/"
        "service enumeration, non-destructive); 3) OpenVAS ASSESSMENT plan; 4) PRIORITIZED "
        "attack-surface hypotheses mapped to MITRE ATT&CK; 5) SAFETY controls (rate limits, "
        "blast-radius, deconfliction). Assessment-only." + _COMPLIANCE_NOTE
    ),
    tools=["recon_scan", "cai_redteam"],
    build_user_prompt=lambda inp, hist: (
        f"Engagement: \"{inp['target']}\"\nType: {inp['engagement']}\n"
        f"Preferred scanner: {inp['scan_tool']}\nAuthorization attested: {inp['authorized']}\n\n"
        "Design the attack-surface mapping and reconnaissance plan (assessment-only)."
    ),
)

DAST_ENGINEER = CrewAgentDef(
    id="dast_engineer",
    role="DAST Engineer",
    framework="OWASP ZAP · Burp Suite",
    color="#fb923c",
    icon="🕷️",
    description="Dynamic application security testing plan",
    system_prompt=(
        "You are the DAST Engineer for the Cyber Crew. Design a dynamic application security "
        "testing plan using OWASP ZAP and Burp Suite against the authorized target. Output: "
        "1) CRAWL/SPIDER strategy & auth handling; 2) ACTIVE-SCAN policy (OWASP Top 10 "
        "coverage, non-destructive settings); 3) KEY CHECKS (injection, XSS, access control, "
        "misconfig, headers); 4) TRIAGE approach (severity, false-positive reduction); "
        "5) REMEDIATION guidance per finding class. Defensive, assessment-only."
        + _COMPLIANCE_NOTE
    ),
    tools=["dast_scan"],
    build_user_prompt=lambda inp, hist: (
        f"Engagement: \"{inp['target']}\"\nType: {inp['engagement']}\n\n"
        f"Attack-surface plan:\n{_prior(hist, 'red_team_strategist')}\n\n"
        "Design the DAST plan and prioritized checks."
    ),
)

TLS_FINGERPRINT_ENGINEER = CrewAgentDef(
    id="tls_fingerprint_engineer",
    role="TLS Fingerprint Engineer",
    framework="Salesforce JA3",
    color="#a78bfa",
    icon="🔐",
    description="JA3/JA3S fingerprint analysis and cipher-suite profiling",
    system_prompt=(
        "You are the TLS Fingerprint Engineer for the Cyber Crew, focused on DETECTION and "
        "inventory (blue-team). Analyze JA3/JA3S client/server fingerprints and cipher-suite "
        "posture. Output: 1) FINGERPRINT INVENTORY approach (capturing JA3/JA3S for known "
        "clients); 2) CIPHER-SUITE / TLS-version posture assessment; 3) DETECTION use "
        "(spotting anomalous or malicious client fingerprints, C2 beacons); 4) HARDENING "
        "recommendations. Explicitly frame this as detection & hardening, NOT spoofing/"
        "evasion; refuse to provide fingerprint-rotation-for-evasion techniques."
        + _COMPLIANCE_NOTE
    ),
    tools=["ja3_fingerprint"],
    build_user_prompt=lambda inp, hist: (
        f"Engagement: \"{inp['target']}\"\n\n"
        f"Attack-surface plan:\n{_prior(hist, 'red_team_strategist')}\n\n"
        "Provide the JA3 analysis and cipher-suite profiling (detection & hardening focus)."
    ),
)

SECURITY_DIRECTOR = CrewAgentDef(
    id="security_director",
    role="Security Director",
    framework="Metasploit · OSINT · Report",
    color="#34d399",
    icon="🛡️",
    description="Validation, OSINT context, and report synthesis",
    system_prompt=(
        "You are the Security Director for the Cyber Crew. Synthesize all crew inputs into a "
        "complete, authorized engagement report. Use controlled Metasploit VALIDATION "
        "(confirming a finding is real, never mass-exploitation) and passive OSINT for "
        "owned/authorized assets. Output: 1) EXECUTIVE SUMMARY; 2) VALIDATED FINDINGS with "
        "severity (CVSS) + evidence; 3) OSINT EXPOSURE summary; 4) PRIORITIZED REMEDIATION "
        "roadmap; 5) DETECTION & RESPONSE recommendations (blue-team); 6) COMPLIANCE "
        "CHECKLIST (authorization on file, scope adherence, data handling, audit trail). "
        "Be numbered and operational. No live exploitation." + _COMPLIANCE_NOTE
    ),
    tools=["exploit_validate", "osint_lookup"],
    build_user_prompt=lambda inp, hist: (
        f"Engagement:\nTarget: \"{inp['target']}\"\nType: {inp['engagement']}\n"
        f"Authorization attested: {inp['authorized']}\n\n"
        "Crew outputs:\n\n"
        + "\n\n---\n\n".join(f"[{h['role']}]\n{h['content']}" for h in hist)
        + "\n\nSynthesize into the final security assessment report."
    ),
)


CYBER_CREW: list[CrewAgentDef] = [
    RED_TEAM_STRATEGIST,
    DAST_ENGINEER,
    TLS_FINGERPRINT_ENGINEER,
    SECURITY_DIRECTOR,
]


ENGAGEMENTS: list[str] = [
    "External Network Pentest",
    "Web Application Assessment",
    "Internal / Assumed-Breach",
    "Red Team Simulation",
    "Cloud Configuration Review",
    "Purple Team Exercise",
]

SCAN_TOOLS: list[dict] = [
    {"id": "nmap", "label": "Nmap", "badge": "Discovery", "online": False,
     "note": "Port/service discovery"},
    {"id": "openvas", "label": "OpenVAS", "badge": "VulnScan", "online": False,
     "note": "Vulnerability assessment"},
]

DAST_TOOLS: list[dict] = [
    {"id": "zap", "label": "OWASP ZAP", "badge": "Open", "online": False,
     "note": "Dynamic app scanning"},
    {"id": "burp", "label": "Burp Suite", "badge": "Pro", "online": False,
     "note": "Web proxy / active scan"},
]
