"""Pure SLA status evaluation (TASK-024 / DEC-013).

Uses immutable due_at snapshots only. Never reads SLA Policy.
Never recalculates deadlines.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.enums import SlaStatus


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def evaluate_stage_status(
    *,
    due_at: datetime | None,
    completed_at: datetime | None,
    now: datetime,
) -> SlaStatus:
    """Evaluate one SLA stage.

    Rules:
    - completed on/before due → COMPLETED
    - completed after due → BREACHED
    - else if now <= due → PENDING
    - else → BREACHED

    Missing due_at → PENDING (nothing to breach against).
    """
    if due_at is None:
        return SlaStatus.PENDING

    due = _ensure_utc(due_at)
    now_utc = _ensure_utc(now)

    if completed_at is not None:
        if _ensure_utc(completed_at) <= due:
            return SlaStatus.COMPLETED
        return SlaStatus.BREACHED
    if now_utc <= due:
        return SlaStatus.PENDING
    return SlaStatus.BREACHED


@dataclass(frozen=True, slots=True)
class SlaCompletionFacts:
    """Business completion timestamps for SLA stages (not policy targets)."""

    assignment_completed_at: datetime | None = None
    appointment_completed_at: datetime | None = None
    resolution_completed_at: datetime | None = None
    escalation_completed_at: datetime | None = None
    overall_completed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class SlaStatusSnapshot:
    assignment_status: SlaStatus
    appointment_status: SlaStatus
    resolution_status: SlaStatus
    escalation_status: SlaStatus
    overall_status: SlaStatus


def evaluate_statuses(
    *,
    assignment_due_at: datetime | None,
    appointment_due_at: datetime | None,
    resolution_due_at: datetime | None,
    escalation_due_at: datetime | None,
    overall_due_at: datetime | None,
    facts: SlaCompletionFacts,
    now: datetime,
) -> SlaStatusSnapshot:
    """Evaluate all SLA stages from stored due_at + completion facts."""
    return SlaStatusSnapshot(
        assignment_status=evaluate_stage_status(
            due_at=assignment_due_at,
            completed_at=facts.assignment_completed_at,
            now=now,
        ),
        appointment_status=evaluate_stage_status(
            due_at=appointment_due_at,
            completed_at=facts.appointment_completed_at,
            now=now,
        ),
        resolution_status=evaluate_stage_status(
            due_at=resolution_due_at,
            completed_at=facts.resolution_completed_at,
            now=now,
        ),
        escalation_status=evaluate_stage_status(
            due_at=escalation_due_at,
            completed_at=facts.escalation_completed_at,
            now=now,
        ),
        overall_status=evaluate_stage_status(
            due_at=overall_due_at,
            completed_at=facts.overall_completed_at,
            now=now,
        ),
    )
