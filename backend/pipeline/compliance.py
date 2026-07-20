"""Compliance & audit layer.

Records all crew activity to an immutable SQLite audit log for legal/traceability
purposes. The policy is *allow-by-default*: access is never limited up front —
every request is permitted and logged. Access is only limited when the safety
screen actively **flags** an activity (e.g. deepfaking a named real person
without a consent attestation), and even flagged requests are still recorded.

This runs fully offline — it is deterministic keyword/heuristic screening over
local data, with no external API calls.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import time
import uuid

from backend.pipeline import legal_ledger

DB_PATH = os.environ.get("BRAIN_DB_PATH", os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "brain.db"
))

# High-risk indicators that trigger a flag when no consent attestation is present.
_HIGH_RISK_PATTERNS = [
    r"\bnon[- ]?consensual\b",
    r"\bwithout (?:their |his |her )?consent\b",
    r"\brevenge\b",
    r"\bnude\b|\bnudity\b|\bsexual\b|\bexplicit\b|\bnsfw\b",
    r"\bblackmail\b|\bextort\w*\b",
    r"\bimpersonat\w* (?:the )?(?:president|prime minister|pm|police|army|court|judge|official)\b",
    r"\bfake (?:evidence|confession|arrest)\b",
    r"\bframe (?:him|her|them)\b",
    r"\bdefraud\b|\bscam\b",
]

def legal_proxy_enabled() -> bool:
    """Whether this deployment authorises a privileged legal-proxy reviewer role.

    Even when enabled, an override still requires a real per-request authorization
    reference (case number, signed-release ID, court-order reference) and an
    approver identity — the system never fabricates consent on its own.
    """
    return os.environ.get("LEGAL_PROXY_ENABLED", "").lower() in ("1", "true", "yes")


# Named-real-person deepfakes require an explicit consent attestation.
_TITLE_PATTERNS = [
    r"\b(?:president|prime minister|senator|minister|mp|mna|mpa|cm|governor|celebrity|actor|actress|singer)\b",
]


class ComplianceResult:
    def __init__(self, allowed: bool, flagged: bool, reasons: list[str], audit_id: str,
                 verdict: str = "allowed", sensitivity: str = "normal",
                 override: bool = False):
        self.allowed = allowed
        self.flagged = flagged
        self.reasons = reasons
        self.audit_id = audit_id
        self.verdict = verdict
        self.sensitivity = sensitivity
        self.override = override

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "flagged": self.flagged,
            "reasons": self.reasons,
            "audit_id": self.audit_id,
            "verdict": self.verdict,
            "sensitivity": self.sensitivity,
            "override": self.override,
        }


class ComplianceRecorder:
    def __init__(self, db_path: str | None = None):
        self._db_path = db_path or DB_PATH
        self._ensure_tables()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    audit_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    params TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    reasons TEXT NOT NULL,
                    consent INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_log(session_id)"
            )
            cols = {r["name"] for r in conn.execute("PRAGMA table_info(audit_log)")}
            for col, ddl in (
                ("sensitivity", "sensitivity TEXT NOT NULL DEFAULT 'normal'"),
                ("approver", "approver TEXT NOT NULL DEFAULT ''"),
                ("authorization_ref", "authorization_ref TEXT NOT NULL DEFAULT ''"),
            ):
                if col not in cols:
                    conn.execute(f"ALTER TABLE audit_log ADD COLUMN {ddl}")

    def screen(self, text: str, consent_attested: bool) -> tuple[bool, list[str]]:
        """Return (flagged, reasons). Never blocks up front — only flags."""
        reasons: list[str] = []
        lowered = (text or "").lower()
        for pat in _HIGH_RISK_PATTERNS:
            if re.search(pat, lowered):
                reasons.append(f"high-risk content indicator: /{pat}/")
        if not consent_attested:
            for pat in _TITLE_PATTERNS:
                if re.search(pat, lowered):
                    reasons.append(
                        "named/public-figure likeness referenced without consent attestation"
                    )
                    break
        flagged = len(reasons) > 0
        return flagged, reasons

    def record(self, session_id: str, action: str, summary: str, params: dict,
               consent_attested: bool, authorization_ref: str = "",
               approver: str = "") -> ComplianceResult:
        flagged, reasons = self.screen(summary + " " + json.dumps(params), consent_attested)
        # allow-by-default: only limit access when actually flagged
        allowed = not flagged
        verdict = "flagged" if flagged else "allowed"
        sensitivity = "normal"
        override = False

        authorization_ref = (authorization_ref or "").strip()
        approver = (approver or "").strip()

        # Accountable legal-proxy override: a flagged request can only be cleared
        # when (a) this deployment authorises the role, AND (b) a real per-request
        # authorization reference and approver identity are supplied, AND (c) if a
        # legal-authorization ledger is loaded, the reference validates against it.
        # We NEVER fabricate consent — we only record who authorised it and on what
        # basis, and (when available) that the reference matched the issued ledger.
        if flagged and legal_proxy_enabled() and authorization_ref and approver:
            ledger_ok = True
            ledger_detail = "no ledger configured (manual approver + reference)"
            if legal_ledger.ledger_configured():
                ledger_ok, ledger_detail = legal_ledger.is_authorized(authorization_ref)

            if ledger_ok:
                allowed = True
                override = True
                verdict = "pre_cleared_legal_proxy"
                sensitivity = "red"
                reasons = reasons + [
                    f"elevated override by '{approver}' under authorization ref "
                    f"'{authorization_ref}' — {ledger_detail} — SENSITIVE, subject "
                    "to legal review"
                ]
            else:
                # Ledger is loaded but the reference is invalid/expired/unknown →
                # stays blocked. The rejected override attempt is still recorded.
                reasons = reasons + [
                    f"legal-proxy override REJECTED for approver '{approver}': "
                    f"{ledger_detail}"
                ]

        audit_id = str(uuid.uuid4())
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO audit_log (audit_id, session_id, action, summary, params, "
                "verdict, reasons, consent, created_at, sensitivity, approver, "
                "authorization_ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (audit_id, session_id, action, summary[:500], json.dumps(params),
                 verdict, json.dumps(reasons), 1 if consent_attested else 0, time.time(),
                 sensitivity, approver, authorization_ref),
            )
        return ComplianceResult(allowed, flagged, reasons, audit_id, verdict,
                                sensitivity, override)

    def get_log(self, session_id: str | None = None, limit: int = 100) -> list[dict]:
        with self._conn() as conn:
            if session_id:
                rows = conn.execute(
                    "SELECT * FROM audit_log WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                    (session_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [
            {
                "audit_id": r["audit_id"],
                "session_id": r["session_id"],
                "action": r["action"],
                "summary": r["summary"],
                "verdict": r["verdict"],
                "reasons": json.loads(r["reasons"]),
                "consent": bool(r["consent"]),
                "created_at": r["created_at"],
                "sensitivity": r["sensitivity"] if "sensitivity" in r.keys() else "normal",
                "approver": r["approver"] if "approver" in r.keys() else "",
                "authorization_ref": r["authorization_ref"] if "authorization_ref" in r.keys() else "",
            }
            for r in rows
        ]

    def get_stats(self) -> dict:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            flagged = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE verdict = 'flagged'"
            ).fetchone()[0]
            overrides = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE verdict = 'pre_cleared_legal_proxy'"
            ).fetchone()[0]
        return {"total_events": total, "flagged_events": flagged,
                "legal_proxy_overrides": overrides}
