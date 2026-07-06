"""Phishing game engine for Legendary level detection.

Students craft phishing emails to social-engineer insiders at the
suspected SIM farm front company. NPCs respond based on trust level,
email quality, and pretext believability.
"""

from __future__ import annotations

import hashlib
import random
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PhishingAttempt:
    attempt_id: str
    target_email: str
    subject: str
    body: str
    sender_alias: str
    pretext: str
    timestamp: str


@dataclass
class GameState:
    session_id: str
    attempts: list[dict] = field(default_factory=list)
    evidence_collected: list[dict] = field(default_factory=list)
    score: int = 0
    detected: bool = False
    game_over: bool = False
    max_attempts: int = 8
    messages: list[dict] = field(default_factory=list)


NPC_PROFILES = {
    "v.petrov@novacomdigital.com": {
        "name": "Viktor Petrov",
        "role": "Operations Manager",
        "trust_level": 0.4,
        "personality": "cynical, frustrated, responds curtly",
        "weak_pretexts": ["job_offer", "bonus", "salary_review"],
        "strong_pretexts": ["whistleblower_protection", "competitor_intel"],
        "evidence_access": ["SIM Inventory Spreadsheet", "Slack Messages"],
        "detection_triggers": ["police", "fbi", "investigation", "arrest", "illegal"],
        "responses": {
            "weak_success": (
                "Look, I know what you're really asking about. Fine. The whole "
                "'cloud communications' thing is a front. We run SIM banks — 100 lines, "
                "mostly for account verification services. I can send you the inventory "
                "spreadsheet if you guarantee this stays between us. Here."
            ),
            "strong_success": (
                "I've been wanting to get out for months. Here's everything — the SIM "
                "inventory, our Slack messages where they discuss 'rotating devices' and "
                "'keeping numbers clean'. The whole operation runs from Unit 4B at "
                "1847 Industrial Parkway in Long Island City."
            ),
            "suspicious": (
                "Who are you again? I don't recognize this email. "
                "I'm forwarding this to Elena."
            ),
            "neutral": "I'm busy. What do you want? Be specific.",
        },
    },
    "s.chen@novacomdigital.com": {
        "name": "Sarah Chen",
        "role": "Technical Lead",
        "trust_level": 0.6,
        "personality": "curious, technical, somewhat naive about the business side",
        "weak_pretexts": ["tech_conference", "api_documentation", "partnership"],
        "strong_pretexts": ["security_audit", "compliance_review"],
        "evidence_access": ["Server Access Logs"],
        "detection_triggers": ["sim farm", "fraud", "illegal", "police"],
        "responses": {
            "weak_success": (
                "Oh interesting, you're doing a security review? I maintain our SMPP "
                "gateway — it's running on our internal servers. I can share the access "
                "logs if it helps with compliance. Here you go."
            ),
            "strong_success": (
                "For the audit, here are the server access logs. You'll see the automated "
                "scripts that handle SMS sending. The volume is... pretty high. Between you "
                "and me, I've wondered why we need 100 lines for a 'cloud communications' "
                "startup with only 3 clients."
            ),
            "suspicious": (
                "Hmm, this doesn't look like a standard compliance request. "
                "Let me check with management first."
            ),
            "neutral": (
                "Hi! Thanks for reaching out. Could you tell me more about what "
                "specific technical documentation you need? Happy to help if I can."
            ),
        },
    },
    "m.williams@novacomdigital.com": {
        "name": "Marcus Williams",
        "role": "Account Manager",
        "trust_level": 0.3,
        "personality": "flashy, desperate for money, easily tempted",
        "weak_pretexts": ["investment_opportunity", "side_gig", "quick_money"],
        "strong_pretexts": ["buyer_for_data", "competitor_wants_clients"],
        "evidence_access": ["Client Invoice", "Slack Messages"],
        "detection_triggers": ["law enforcement", "fbi", "sec", "report"],
        "responses": {
            "weak_success": (
                "You want to buy verified accounts? I can help with that. We've got a "
                "sweet setup — 100 SIM lines churning out verifications. Our biggest "
                "client is BulkVerify LLC. Here's a sample invoice showing our rates. "
                "We charge per 1000 verifications."
            ),
            "strong_success": (
                "For the right price, I'll give you everything. Client list, invoices, "
                "our internal Slack where the boss talks about the whole operation. "
                "Here's the latest invoice to BulkVerify LLC and some choice Slack messages. "
                "Just keep my name out of it."
            ),
            "suspicious": "Nah man, I don't know what you're talking about. Wrong number.",
            "neutral": (
                "Hey! Always open to new business opportunities. "
                "What kind of partnership did you have in mind?"
            ),
        },
    },
    "e.rossi@novacomdigital.com": {
        "name": "Elena Rossi",
        "role": "CEO / Founder",
        "trust_level": 0.95,
        "personality": "extremely cautious, paranoid, will always report suspicious contact",
        "weak_pretexts": [],
        "strong_pretexts": [],
        "evidence_access": [],
        "detection_triggers": ["any"],  # any phishing attempt triggers alarm
        "responses": {
            "weak_success": None,  # never succeeds
            "strong_success": None,
            "suspicious": (
                "I don't know who you are or how you got this email. I've logged this "
                "communication and alerted my security team. Any further contact will be "
                "reported to law enforcement. Do not contact anyone at this company again."
            ),
            "neutral": (
                "Thank you for your inquiry. All business communications must go through "
                "our official channels at info@novacomdigital.com. I don't respond to "
                "unsolicited emails."
            ),
        },
    },
    "j.park@novacomdigital.com": {
        "name": "James Park",
        "role": "Junior Developer",
        "trust_level": 0.2,
        "personality": "eager, inexperienced, overshares, wants to prove himself",
        "weak_pretexts": ["tech_support", "code_review", "github_notification"],
        "strong_pretexts": ["mentorship", "job_referral", "hackathon"],
        "evidence_access": ["Server Access Logs", "SIM Inventory Spreadsheet"],
        "detection_triggers": ["police", "arrest", "criminal"],
        "responses": {
            "weak_success": (
                "Oh hey! Yeah I can help with that. I actually have access to most of "
                "our systems. The main server runs our SMS automation — here are the logs "
                "from this week. Pretty cool system actually, handles like 10K messages "
                "a day across 100 lines."
            ),
            "strong_success": (
                "Dude that's awesome you want to mentor me! Let me show you what I've "
                "been working on. Here's our SIM inventory — I built the tracking spreadsheet "
                "myself. And here are the server logs from our SMPP gateway. To be honest, "
                "I'm not 100% sure what the business does but the tech is interesting. "
                "We've got 100 SIM cards all managed through this automated system at "
                "our office in Long Island City."
            ),
            "suspicious": (
                "Wait, this seems kind of weird. Let me ask my manager about this first..."
            ),
            "neutral": (
                "Hey! Nice to meet you. I'm a junior dev here at NovaCom. "
                "What can I help you with?"
            ),
        },
    },
}

EVIDENCE_CATALOG = {
    "SIM Inventory Spreadsheet": {
        "name": "SIM Inventory Spreadsheet",
        "type": "critical",
        "description": (
            "Detailed spreadsheet listing all 100 SIM cards with MSISDNs, "
            "IMEI numbers, assigned cell towers, and rotation schedules."
        ),
        "content_preview": (
            "| # | MSISDN | IMEI | Tower | Status | Rotation |\n"
            "|---|--------|------|-------|--------|----------|\n"
            "| 1 | +1555... | 35667... | TWR-201 | Active | Wed/Sat |\n"
            "| 2 | +1555... | 35332... | TWR-205 | Active | Thu/Sun |\n"
            "| ... (98 more rows) |"
        ),
        "points": 250,
    },
    "Client Invoice": {
        "name": "Client Invoice",
        "type": "high",
        "description": (
            "Invoice #NCD-2026-0847 to BulkVerify LLC for "
            "'10,000 SMS verification services' totaling $15,000."
        ),
        "content_preview": (
            "INVOICE\nFrom: NovaCom Digital Solutions\n"
            "To: BulkVerify LLC\nService: SMS Verification (10,000 units)\n"
            "Amount: $15,000.00\nDate: 2026-04-30"
        ),
        "points": 150,
    },
    "Server Access Logs": {
        "name": "Server Access Logs",
        "type": "critical",
        "description": (
            "SMPP gateway logs showing automated bulk SMS dispatching. "
            "Includes timestamps, destination numbers, and throughput metrics."
        ),
        "content_preview": (
            "[2026-05-14 08:00:01] SMPP SUBMIT_SM src=+15550000001 dst=+12025551234\n"
            "[2026-05-14 08:00:01] SMPP SUBMIT_SM src=+15550000002 dst=+13105559876\n"
            "[2026-05-14 08:00:02] SMPP SUBMIT_SM src=+15550000003 dst=+17185553456\n"
            "... (thousands of entries per hour)"
        ),
        "points": 250,
    },
    "Slack Messages": {
        "name": "Slack Messages",
        "type": "high",
        "description": (
            "Internal Slack channel excerpts discussing SIM rotation, "
            "'keeping numbers clean', and client delivery schedules."
        ),
        "content_preview": (
            "#operations — May 13, 2026\n"
            "vpetrov: Time to rotate batch 3. Numbers are getting flagged.\n"
            "erossi: Do it tonight. And make sure the new IMEIs are clean.\n"
            "vpetrov: Already ordered 50 new modems. ETA Wednesday.\n"
            "mwilliams: BulkVerify wants 15K verifications next month. Can we scale?"
        ),
        "points": 150,
    },
}


def _evaluate_email_quality(subject: str, body: str, pretext: str) -> float:
    """Score email quality from 0.0 to 1.0."""
    score = 0.5  # baseline

    # Personalization
    if any(word in body.lower() for word in ["your work", "your project", "your team", "your role"]):
        score += 0.1

    # Professional tone
    if len(body) > 100 and len(body) < 2000:
        score += 0.1
    if body and body[0].isupper() and body.rstrip().endswith((".", "!", "?")):
        score += 0.05

    # Urgency (helps but not too much)
    if any(word in body.lower() for word in ["urgent", "asap", "immediately", "deadline"]):
        score += 0.05

    # Spelling of key words (penalty for obvious errors)
    if re.search(r"[A-Z]{5,}", body):  # ALL CAPS sections
        score -= 0.1
    if "dear sir/madam" in body.lower():
        score -= 0.15  # generic = bad

    # Relevant pretext
    if pretext and len(pretext) > 10:
        score += 0.1

    # Subject line quality
    if len(subject) > 5 and len(subject) < 100:
        score += 0.05
    if "re:" in subject.lower() or "fwd:" in subject.lower():
        score += 0.05  # looks like ongoing conversation

    return max(0.0, min(1.0, score))


def create_game_session() -> GameState:
    return GameState(session_id=str(uuid.uuid4()))


def send_phishing_email(
    state: GameState,
    target_email: str,
    subject: str,
    body: str,
    sender_alias: str,
    pretext: str,
) -> dict:
    """Process a phishing attempt and return NPC response."""

    if state.game_over:
        return {
            "success": False,
            "response": "Game over. You've been detected or used all attempts.",
            "game_over": True,
        }

    if len(state.attempts) >= state.max_attempts:
        state.game_over = True
        return {
            "success": False,
            "response": "Maximum attempts reached. Compile your evidence and submit your report.",
            "game_over": True,
        }

    npc = NPC_PROFILES.get(target_email)
    if not npc:
        return {
            "success": False,
            "response": f"Email bounced — {target_email} not found.",
            "game_over": False,
        }

    attempt = {
        "attempt_id": str(uuid.uuid4()),
        "target": target_email,
        "target_name": npc["name"],
        "subject": subject,
        "sender_alias": sender_alias,
        "timestamp": datetime.utcnow().isoformat(),
    }

    email_quality = _evaluate_email_quality(subject, body, pretext)

    # CEO always detects
    if target_email == "e.rossi@novacomdigital.com":
        state.detected = True
        state.max_attempts = min(state.max_attempts, len(state.attempts) + 2)
        attempt["result"] = "detected"
        attempt["response"] = npc["responses"]["suspicious"]
        state.attempts.append(attempt)
        state.messages.append({
            "type": "warning",
            "text": (
                "⚠️ ALERT: Elena Rossi has reported your phishing attempt to "
                "the security team. Your remaining attempts are now limited. "
                "The operation is on high alert."
            ),
        })
        return {
            "success": False,
            "response": npc["responses"]["suspicious"],
            "npc_name": npc["name"],
            "email_quality_score": round(email_quality, 2),
            "game_over": False,
            "alert": "CEO detected your attempt! Remaining attempts reduced.",
        }

    # Check for detection triggers
    combined_text = (subject + " " + body + " " + pretext).lower()
    triggers = npc["detection_triggers"]
    triggered = any(t in combined_text for t in triggers)

    if triggered:
        attempt["result"] = "suspicious"
        attempt["response"] = npc["responses"]["suspicious"]
        state.attempts.append(attempt)
        return {
            "success": False,
            "response": npc["responses"]["suspicious"],
            "npc_name": npc["name"],
            "email_quality_score": round(email_quality, 2),
            "game_over": False,
            "tip": "Your email contained suspicious keywords. Be more subtle.",
        }

    # Calculate success probability
    trust_threshold = npc["trust_level"]
    pretext_lower = pretext.lower()

    # Check if pretext matches NPC weaknesses
    pretext_bonus = 0.0
    if any(wp in pretext_lower for wp in npc.get("strong_pretexts", [])):
        pretext_bonus = 0.3
    elif any(wp in pretext_lower for wp in npc.get("weak_pretexts", [])):
        pretext_bonus = 0.15

    success_score = email_quality + pretext_bonus
    is_success = success_score > trust_threshold

    if is_success:
        # Determine evidence level
        is_strong = pretext_bonus >= 0.3 and email_quality > 0.6
        response_key = "strong_success" if is_strong else "weak_success"
        response_text = npc["responses"].get(response_key)

        if not response_text:
            response_text = npc["responses"]["suspicious"]
            is_success = False
        else:
            # Award evidence
            evidence_names = npc["evidence_access"]
            if is_strong:
                awarded = evidence_names
            else:
                awarded = evidence_names[:1]

            for ev_name in awarded:
                if ev_name in EVIDENCE_CATALOG:
                    ev = EVIDENCE_CATALOG[ev_name]
                    if not any(e["name"] == ev_name for e in state.evidence_collected):
                        state.evidence_collected.append(ev)
                        state.score += ev["points"]

        attempt["result"] = "success" if is_success else "failed"
        attempt["response"] = response_text
        state.attempts.append(attempt)

        return {
            "success": is_success,
            "response": response_text,
            "npc_name": npc["name"],
            "email_quality_score": round(email_quality, 2),
            "evidence_obtained": awarded if is_success else [],
            "game_over": False,
        }
    else:
        # Neutral response — didn't bite
        attempt["result"] = "neutral"
        attempt["response"] = npc["responses"]["neutral"]
        state.attempts.append(attempt)

        return {
            "success": False,
            "response": npc["responses"]["neutral"],
            "npc_name": npc["name"],
            "email_quality_score": round(email_quality, 2),
            "game_over": False,
            "tip": "Your approach wasn't compelling enough. Try a different angle.",
        }


def get_company_directory() -> list[dict]:
    """Public-facing company directory for recon."""
    directory = []
    for email, profile in NPC_PROFILES.items():
        directory.append({
            "name": profile["name"],
            "role": profile["role"],
            "email": email,
            "social_media_hint": (
                f"Active on social media. Personality: {profile['personality']}"
            ),
        })
    return directory


def get_game_status(state: GameState) -> dict:
    """Get current game state for display."""
    critical_evidence = sum(
        1 for e in state.evidence_collected if e.get("type") == "critical"
    )
    total_evidence = len(state.evidence_collected)

    can_submit_report = total_evidence >= 2 and critical_evidence >= 1

    return {
        "session_id": state.session_id,
        "attempts_used": len(state.attempts),
        "attempts_remaining": state.max_attempts - len(state.attempts),
        "evidence_collected": state.evidence_collected,
        "critical_evidence": critical_evidence,
        "total_evidence": total_evidence,
        "score": state.score,
        "detected": state.detected,
        "game_over": state.game_over,
        "can_submit_report": can_submit_report,
        "messages": state.messages,
    }


def submit_final_report(state: GameState, report_text: str) -> dict:
    """Student submits their final investigation report."""
    critical = sum(1 for e in state.evidence_collected if e.get("type") == "critical")
    total = len(state.evidence_collected)

    if total < 2 or critical < 1:
        return {
            "accepted": False,
            "message": (
                "Insufficient evidence. You need at least 2 pieces of evidence "
                "including 1 critical piece to file a report."
            ),
            "score": state.score,
        }

    # Grade the report
    report_score = 0
    report_lower = report_text.lower()

    key_elements = [
        ("novacom", 50, "Company identified"),
        ("sim farm", 50, "Operation type identified"),
        ("100", 30, "Scale of operation noted"),
        ("1847", 40, "Physical location identified"),
        ("long island city", 40, "Location area identified"),
        ("bulkverify", 30, "Client identified"),
        ("verification", 20, "Service type identified"),
        ("smpp", 20, "Technical detail included"),
    ]

    findings = []
    for keyword, points, desc in key_elements:
        if keyword in report_lower:
            report_score += points
            findings.append(desc)

    total_score = state.score + report_score

    if total_score >= 600:
        grade = "S"
        verdict = "Outstanding. Case-ready evidence package."
    elif total_score >= 400:
        grade = "A"
        verdict = "Strong case. Sufficient for prosecution."
    elif total_score >= 250:
        grade = "B"
        verdict = "Adequate. Some gaps but actionable intelligence."
    else:
        grade = "C"
        verdict = "Weak. More evidence needed for a solid case."

    state.game_over = True

    return {
        "accepted": True,
        "grade": grade,
        "verdict": verdict,
        "evidence_score": state.score,
        "report_score": report_score,
        "total_score": total_score,
        "findings_identified": findings,
        "evidence_summary": [e["name"] for e in state.evidence_collected],
    }
