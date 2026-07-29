"""Optional daily scheduler for the legal-authorization ledger.

When LEGAL_LEDGER_AUTO_SYNC is enabled and an HTTPS URL is configured, this runs
a background task that fetches the ledger once per day at the configured local
time (default 17:00 America/New_York). Only the HTTPS source is automated — the
SSH and upload fallbacks are always manual, operator-initiated actions.

A failed automatic fetch keeps the last verified ledger (marked stale by
`legal_ledger.status()`); it never falls back to credential-based sources on its
own and never auto-clears any request.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from backend.pipeline import legal_ledger

_task: asyncio.Task | None = None


def _enabled() -> bool:
    return os.environ.get("LEGAL_LEDGER_AUTO_SYNC", "").lower() in ("1", "true", "yes")


def _seconds_until_next_run() -> float:
    hhmm = os.environ.get("LEGAL_LEDGER_SYNC_TIME", "17:00")
    tz_name = os.environ.get("LEGAL_LEDGER_SYNC_TZ", "America/New_York")
    try:
        hour, minute = (int(x) for x in hhmm.split(":"))
    except ValueError:
        hour, minute = 17, 0
    tz = ZoneInfo(tz_name) if ZoneInfo else None
    now = datetime.now(tz)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def _loop() -> None:
    while True:
        await asyncio.sleep(_seconds_until_next_run())
        try:
            await asyncio.to_thread(legal_ledger.fetch_https)
        except Exception as exc:  # keep last ledger; just log
            print(f"[ledger-scheduler] scheduled HTTPS fetch failed: {exc}")


def start() -> None:
    """Start the daily scheduler if enabled and an HTTPS URL is configured."""
    global _task
    if _task is not None or not _enabled():
        return
    if not os.environ.get("LEGAL_LEDGER_URL", "").strip():
        return
    try:
        _task = asyncio.get_event_loop().create_task(_loop())
        print("[ledger-scheduler] daily HTTPS ledger sync scheduled")
    except RuntimeError:
        pass
