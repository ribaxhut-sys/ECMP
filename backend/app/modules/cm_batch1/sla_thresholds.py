"""SLA proactive thresholds for FR-030 / DEC-031 Fase 2 (C-6).

Pure helpers: which H-7 / H-3 / H-1 / BREACH instants have been crossed.
Uses ``due_at`` from ``resolve_complaint_sla`` — no second calendar formula.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

from app.modules.cm_batch1.sla import SLA_OVERDUE, ComplaintSla

SlaThresholdCode = Literal["H7", "H3", "H1", "BREACH"]

#: Ordered earliest → latest so a sweep can emit every newly crossed level.
SLA_THRESHOLD_ORDER: tuple[SlaThresholdCode, ...] = ("H7", "H3", "H1", "BREACH")

_THRESHOLD_OFFSETS: dict[SlaThresholdCode, timedelta] = {
    "H7": timedelta(days=7),
    "H3": timedelta(days=3),
    "H1": timedelta(days=1),
    "BREACH": timedelta(0),
}


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def sla_idempotency_key(*, complaint_id: str, threshold: SlaThresholdCode) -> str:
    """G3.4 — once per complaint × RESOLUTION × threshold."""
    return f"cm-sla:{complaint_id}:RESOLUTION:{threshold}"


def threshold_at(*, due_at: datetime, threshold: SlaThresholdCode) -> datetime:
    """Instant at which ``threshold`` becomes eligible (G3.2)."""
    return _as_utc(due_at) - _THRESHOLD_OFFSETS[threshold]


def crossed_thresholds(
    *,
    due_at: datetime,
    now: datetime,
) -> list[SlaThresholdCode]:
    """Thresholds with ``now >= threshold_at``, earliest first."""
    current = _as_utc(now)
    due = _as_utc(due_at)
    return [
        code
        for code in SLA_THRESHOLD_ORDER
        if current >= threshold_at(due_at=due, threshold=code)
    ]


def classify_in_app_threshold(sla: ComplaintSla) -> SlaThresholdCode | None:
    """Map a live SLA position to the C-6 in-app label (read path).

    BREACH when overdue; otherwise remaining whole days → H1 / H3 / H7.
    Returns ``None`` before the H7 window (e.g. 80% warning-only zone).
    """
    if sla.status == SLA_OVERDUE:
        return "BREACH"
    remaining = sla.remaining_days
    if remaining is None:
        return None
    if remaining <= 1:
        return "H1"
    if remaining <= 3:
        return "H3"
    if remaining <= 7:
        return "H7"
    return None


def candidate_created_at_cutoff(
    *,
    target_days: int,
    now: datetime,
) -> datetime:
    """Oldest ``created_at`` still too early for any threshold (exclusive upper).

    H7 fires at ``created_at + (target_days - 7)``; candidates satisfy
    ``created_at <= now - max(0, target_days - 7)``.
    """
    current = _as_utc(now)
    lead = max(0, target_days - 7)
    return current - timedelta(days=lead)


__all__ = [
    "SlaThresholdCode",
    "SLA_THRESHOLD_ORDER",
    "sla_idempotency_key",
    "threshold_at",
    "crossed_thresholds",
    "classify_in_app_threshold",
    "candidate_created_at_cutoff",
]
