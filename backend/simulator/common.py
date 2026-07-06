"""Shared helpers for the SIM farm simulators.

These utilities collect data-generation and scoring patterns that were
previously copy-pasted across the beginner/easy/legendary generators and the
playground/UK-demo metric calculators.
"""

from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta
from typing import Iterable, TypeVar

T = TypeVar("T")


def random_us_msisdn() -> str:
    """A random North-American MSISDN (``+1NXXNXXXXXX``)."""
    return f"+1{random.randint(200, 999)}{random.randint(1000000, 9999999)}"


def random_public_ipv4() -> str:
    """A random routable-looking IPv4 address."""
    return (
        f"{random.randint(1, 223)}.{random.randint(0, 255)}."
        f"{random.randint(0, 255)}.{random.randint(1, 254)}"
    )


def sms_content_hash(content: str) -> str:
    """Truncated SHA-256 digest used as an opaque SMS content fingerprint."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def random_timestamp(
    base_time: datetime, hours: int, with_seconds: bool = True
) -> datetime:
    """A random timestamp within ``[base_time, base_time + hours)``.

    The random draws happen in hour/minute(/second) order so callers that seed
    ``random`` get a reproducible sequence.
    """
    hour = random.randint(0, hours - 1)
    minute = random.randint(0, 59)
    if with_seconds:
        second = random.randint(0, 59)
        return base_time + timedelta(hours=hour, minutes=minute, seconds=second)
    return base_time + timedelta(hours=hour, minutes=minute)


def sort_by_timestamp(records: list[T]) -> list[T]:
    """Sort records in place by their ``timestamp`` attribute and return them."""
    records.sort(key=lambda r: r.timestamp)
    return records


def grade_by_thresholds(
    value: float, tiers: Iterable[tuple[float, T]], default: T
) -> T:
    """Return the first ``result`` whose ``value <= inclusive_upper_bound``.

    ``tiers`` should be ordered from the lowest bound upward. Used for the
    ascending stealth-grade tables.
    """
    for bound, result in tiers:
        if value <= bound:
            return result
    return default


def bucket_by_thresholds(
    value: float, tiers: Iterable[tuple[float, T]], default: T
) -> T:
    """Return the first ``result`` whose ``value > exclusive_lower_bound``.

    ``tiers`` should be ordered from the highest bound downward. Used for the
    descending detection-timeline tables.
    """
    for bound, result in tiers:
        if value > bound:
            return result
    return default
