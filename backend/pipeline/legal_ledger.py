"""Legal-authorization ledger sync.

Provides the authorization *references* that a human legal-proxy approver may cite
when clearing a flagged Video Stack request. This module NEVER auto-clears a
request and NEVER fabricates consent — it only maintains a local, verifiable copy
of the authorizations issued by the legal authority, against which an approver's
per-request `authorization_ref` can be validated.

Sources (in the order an operator would try them):
  1. HTTPS  — primary. URL + bearer token come from the environment / secret
     manager; nothing is hard-coded. TLS verification is on by default.
  2. SSH    — manual fallback only. Triggered by an explicit operator action that
     supplies the username/password at request time; credentials are used for the
     single fetch and never stored or logged. The host key MUST be verified
     against a configured fingerprint — an unknown host is rejected.
  3. Upload — last-resort admin CSV upload through the app.

Every fetch is recorded in the audit log. Security posture:
  * No credentials are ever committed, stored, or written to disk/logs.
  * The SSH host/port/path are operator-configured (no baked-in target).
  * Unknown SSH host keys are rejected (no blind auto-accept).
  * A failed fetch keeps the last verified ledger and marks it stale rather than
    silently degrading.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import os
import time

import httpx

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)
LEDGER_PATH = os.path.join(DATA_DIR, "legal_ledger.csv")

# Columns we understand in the ledger CSV. `authorization_ref` is required.
_REQUIRED_COLUMN = "authorization_ref"


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def config() -> dict:
    """Non-secret ledger configuration (safe to expose to the UI)."""
    return {
        "https_configured": bool(_env("LEGAL_LEDGER_URL")),
        "https_url": _env("LEGAL_LEDGER_URL"),
        "ssh_configured": bool(_env("LEGAL_LEDGER_SSH_HOST"))
        and bool(_env("LEGAL_LEDGER_SSH_HOSTKEY")),
        "ssh_host": _env("LEGAL_LEDGER_SSH_HOST"),
        "ssh_port": int(_env("LEGAL_LEDGER_SSH_PORT", "22") or "22"),
        "ssh_path": _env("LEGAL_LEDGER_SSH_PATH"),
        "verify_tls": _env("LEGAL_LEDGER_VERIFY_TLS", "true").lower()
        not in ("0", "false", "no"),
    }


# ── Parsing / validation ────────────────────────────────────────────


def parse_ledger(text: str) -> list[dict]:
    """Parse a ledger CSV into a list of authorization rows.

    Raises ValueError if the required column is missing.
    """
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or _REQUIRED_COLUMN not in reader.fieldnames:
        raise ValueError(
            f"ledger CSV must contain a '{_REQUIRED_COLUMN}' column; "
            f"got {reader.fieldnames}"
        )
    rows: list[dict] = []
    for raw in reader:
        ref = (raw.get(_REQUIRED_COLUMN) or "").strip()
        if not ref:
            continue
        rows.append({k: (v or "").strip() for k, v in raw.items()})
    return rows


def _save(text: str, source: str) -> dict:
    """Validate and persist a freshly-fetched ledger. Returns status."""
    rows = parse_ledger(text)  # validate before persisting
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)
    meta = {
        "source": source,
        "fetched_at": time.time(),
        "count": len(rows),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    _write_meta(meta)
    return meta


_META_PATH = os.path.join(DATA_DIR, "legal_ledger.meta")


def _write_meta(meta: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_META_PATH, "w", encoding="utf-8") as fh:
        fh.write(
            f"{meta['source']}\n{meta['fetched_at']}\n{meta['count']}\n{meta['sha256']}\n"
        )


def _read_meta() -> dict | None:
    if not os.path.exists(_META_PATH):
        return None
    try:
        with open(_META_PATH, encoding="utf-8") as fh:
            source, fetched_at, count, sha256 = [
                ln.strip() for ln in fh.readlines()[:4]
            ]
        return {
            "source": source,
            "fetched_at": float(fetched_at),
            "count": int(count),
            "sha256": sha256,
        }
    except (ValueError, IndexError):
        return None


def _load_rows() -> list[dict]:
    if not os.path.exists(LEDGER_PATH):
        return []
    try:
        with open(LEDGER_PATH, encoding="utf-8") as fh:
            return parse_ledger(fh.read())
    except (ValueError, OSError):
        return []


def status() -> dict:
    """Current ledger status for the UI (no secrets)."""
    meta = _read_meta()
    cfg = config()
    if not meta:
        return {
            "loaded": False,
            "count": 0,
            "config": cfg,
        }
    age = time.time() - meta["fetched_at"]
    # Consider the ledger stale after 26h (daily feed + grace).
    stale = age > 26 * 3600
    return {
        "loaded": True,
        "source": meta["source"],
        "fetched_at": meta["fetched_at"],
        "count": meta["count"],
        "sha256": meta["sha256"][:16],
        "stale": stale,
        "config": cfg,
    }


def is_authorized(ref: str) -> tuple[bool, str]:
    """Validate a per-request authorization reference against the ledger.

    Returns (ok, detail). If no ledger is loaded, returns (False, reason) so the
    caller can decide whether to fall back to manual approver+ref only.
    """
    ref = (ref or "").strip()
    if not ref:
        return False, "no authorization reference supplied"
    rows = _load_rows()
    if not rows:
        return False, "no ledger loaded"
    for row in rows:
        if row.get(_REQUIRED_COLUMN) == ref:
            valid_until = row.get("valid_until", "")
            if valid_until:
                try:
                    # Accept YYYY-MM-DD; expire at end of that day.
                    exp = time.mktime(time.strptime(valid_until, "%Y-%m-%d")) + 86400
                    if time.time() > exp:
                        return False, f"authorization {ref} expired {valid_until}"
                except ValueError:
                    pass  # unparseable date → treat as non-expiring, still valid
            subject = row.get("subject") or row.get("entity") or ""
            issuer = row.get("issuer") or ""
            detail = f"validated against ledger (subject='{subject}', issuer='{issuer}')"
            return True, detail
    return False, f"authorization reference {ref} not found in ledger"


def ledger_configured() -> bool:
    return bool(_read_meta()) or os.path.exists(LEDGER_PATH)


# ── Fetch sources ───────────────────────────────────────────────────


def fetch_https() -> dict:
    """Fetch the ledger over HTTPS using env-provided URL + bearer token."""
    url = _env("LEGAL_LEDGER_URL")
    if not url:
        raise ValueError("LEGAL_LEDGER_URL is not configured")
    token = _env("LEGAL_LEDGER_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    verify = config()["verify_tls"]
    with httpx.Client(timeout=15.0, verify=verify) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return _save(resp.text, "https")


class _PinnedHostKeyPolicy:
    """Accept a host key only if its SHA256 fingerprint matches the configured pin.

    This avoids paramiko's insecure AutoAddPolicy — an unknown/mismatched host is
    rejected so the SSH fallback can't be pointed at an impostor server.
    """

    def __init__(self, expected_fp: str):
        # Normalise: allow "SHA256:base64" or bare base64/hex.
        self._expected = expected_fp.split("SHA256:")[-1].strip()

    def missing_host_key(self, client, hostname, key):  # noqa: D401 (paramiko API)
        raw = key.asbytes()
        digest = hashlib.sha256(raw).digest()
        fp_b64 = base64.b64encode(digest).decode().rstrip("=")
        fp_hex = digest.hex()
        if self._expected in (fp_b64, fp_hex):
            return
        raise Exception(
            "SSH host key fingerprint mismatch — refusing to connect "
            "(possible impostor host)"
        )


def fetch_ssh(username: str, password: str) -> dict:
    """Manual SSH fallback. Credentials are used once and never stored.

    Requires LEGAL_LEDGER_SSH_HOST, LEGAL_LEDGER_SSH_PATH and a pinned
    LEGAL_LEDGER_SSH_HOSTKEY fingerprint; an unpinned host is refused.
    """
    import paramiko  # imported lazily so the app still runs without SSH deps

    host = _env("LEGAL_LEDGER_SSH_HOST")
    path = _env("LEGAL_LEDGER_SSH_PATH")
    port = int(_env("LEGAL_LEDGER_SSH_PORT", "22") or "22")
    hostkey_fp = _env("LEGAL_LEDGER_SSH_HOSTKEY")
    if not host or not path:
        raise ValueError("LEGAL_LEDGER_SSH_HOST / LEGAL_LEDGER_SSH_PATH not configured")
    if not hostkey_fp:
        raise ValueError(
            "LEGAL_LEDGER_SSH_HOSTKEY (pinned fingerprint) is required — "
            "refusing to connect to an unverified host"
        )
    if not username or not password:
        raise ValueError("SSH username and password are required for this fetch")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(_PinnedHostKeyPolicy(hostkey_fp))
    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=15,
            allow_agent=False,
            look_for_keys=False,
        )
        sftp = client.open_sftp()
        try:
            with sftp.open(path, "r") as remote:
                text = remote.read().decode("utf-8")
        finally:
            sftp.close()
    finally:
        client.close()
        # Do not retain credentials in memory beyond this call.
        del password
    return _save(text, "ssh")


def load_from_upload(content: bytes) -> dict:
    """Last-resort admin CSV upload."""
    text = content.decode("utf-8")
    return _save(text, "upload")
