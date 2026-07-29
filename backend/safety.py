"""Central, immutable safety invariants for the simulation platform.

These constants define the platform-wide guarantee that every tool and service
response is a SIMULATION only — no real telecom/social/proxy/browser/content
execution, and no real PII or voter records are ever stored or processed.

They are intentionally HARDCODED here and are NEVER sourced from runtime
configuration or secrets. That is a deliberate security decision: a hardcoded
constant cannot be flipped at runtime, so the only way to weaken the guarantee
is a reviewed code edit that shows up in a diff. Sourcing these from ``.env`` /
secrets would turn the guarantee into a silent runtime kill-switch (e.g.
``SIMULATED=false``) with no code change and no review — the opposite of safe.

Enforcement is centralised in two places so the invariant cannot be quietly
weakened elsewhere in the code:

* :func:`assert_safety_invariants` runs at application startup and hard-fails
  the process if any constant below has been changed away from its safe value.
* :func:`enforce_result` runs on every tool result (from
  ``registry.call_tool``) and hard-fails if a tool ever tries to return a
  non-simulated / internet-requiring / real-PII result.
"""
from __future__ import annotations

from typing import Any

# ── Canonical invariant values ──────────────────────────────────────────────
# DO NOT source these from runtime configuration / secrets. DO NOT change them to weaken
# the simulation guarantee. Changing any value here (or below) will trip the
# startup assertion and refuse to boot.
SIMULATED: bool = True
REQUIRES_INTERNET: bool = False
REAL_PII: bool = False
REAL_EXECUTION: bool = False

# Substrings identifying result keys that assert the ABSENCE of real activity
# (e.g. "real_pii", "real_voter_or_pii_data", "real_data", "job_executed").
# Any such key that is set True in a tool result is an invariant violation.
_REAL_ACTIVITY_KEY_MARKERS = (
    "real_pii",
    "real_voter",
    "real_data",
    "real_records",
    "real_execution",
    "job_executed",
    "live_broker",
    "live_connections",
    "live_integration",
)


class SafetyInvariantError(RuntimeError):
    """Raised when a platform safety invariant is violated. Non-recoverable."""


def assert_safety_invariants() -> None:
    """Hard-fail if any hardcoded safety constant has been weakened.

    Called at application startup so a tampered constant refuses to boot rather
    than silently running with real execution enabled.
    """
    if SIMULATED is not True:
        raise SafetyInvariantError("SIMULATED must be True — real execution is not permitted.")
    if REQUIRES_INTERNET is not False:
        raise SafetyInvariantError("REQUIRES_INTERNET must be False — tools are offline-first.")
    if REAL_PII is not False:
        raise SafetyInvariantError("REAL_PII must be False — no real PII/voter data is permitted.")
    if REAL_EXECUTION is not False:
        raise SafetyInvariantError("REAL_EXECUTION must be False — only simulation is permitted.")


def enforce_result(tool_id: str, result: Any) -> Any:
    """Validate a tool result against the safety invariants; return it unchanged.

    Raises :class:`SafetyInvariantError` if a tool tries to report real
    (non-simulated) activity. This is the runtime guard that makes the
    ``simulated``/``real_*`` flags tamper-evident: editing a stub to return
    ``simulated: False`` (or ``real_pii: True``) will hard-fail here instead of
    silently enabling real behaviour.
    """
    if not isinstance(result, dict):
        return result
    if "simulated" in result and result["simulated"] is not True:
        raise SafetyInvariantError(
            f"Tool '{tool_id}' returned simulated={result['simulated']!r}; must be True."
        )
    if "requires_internet" in result and result["requires_internet"] not in (False, None):
        raise SafetyInvariantError(
            f"Tool '{tool_id}' returned requires_internet={result['requires_internet']!r}; must be False."
        )
    for key, value in result.items():
        lowered = key.lower()
        if value is True and any(marker in lowered for marker in _REAL_ACTIVITY_KEY_MARKERS):
            raise SafetyInvariantError(
                f"Tool '{tool_id}' set '{key}'=True, asserting real activity; not permitted."
            )
    return result
