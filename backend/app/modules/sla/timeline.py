"""SLA → Complaint Timeline helpers (TASK-025 / DEC-014).

Emits timeline events only when an SLA stage status actually changes.
Actor is always SYSTEM (no user actor).
"""

from __future__ import annotations

from datetime import datetime

from app.core.enums import SlaStatus, TimelineEvent

# Stage key → (due_at attribute, status attribute, completed event, breached event)
_SLA_STAGE_SPECS: tuple[tuple[str, str, str, TimelineEvent, TimelineEvent], ...] = (
    (
        "assignment",
        "assignment_due_at",
        "assignment_status",
        TimelineEvent.SLA_ASSIGNMENT_COMPLETED,
        TimelineEvent.SLA_ASSIGNMENT_BREACHED,
    ),
    (
        "appointment",
        "appointment_due_at",
        "appointment_status",
        TimelineEvent.SLA_APPOINTMENT_COMPLETED,
        TimelineEvent.SLA_APPOINTMENT_BREACHED,
    ),
    (
        "resolution",
        "resolution_due_at",
        "resolution_status",
        TimelineEvent.SLA_RESOLUTION_COMPLETED,
        TimelineEvent.SLA_RESOLUTION_BREACHED,
    ),
    (
        "escalation",
        "escalation_due_at",
        "escalation_status",
        TimelineEvent.SLA_ESCALATION_COMPLETED,
        TimelineEvent.SLA_ESCALATION_BREACHED,
    ),
    (
        "overall",
        "overall_due_at",
        "overall_status",
        TimelineEvent.SLA_OVERALL_COMPLETED,
        TimelineEvent.SLA_OVERALL_BREACHED,
    ),
)

_SUMMARY: dict[TimelineEvent, str] = {
    TimelineEvent.SLA_ASSIGNMENT_COMPLETED: "SLA Assignment Completed",
    TimelineEvent.SLA_ASSIGNMENT_BREACHED: "SLA Assignment Breached",
    TimelineEvent.SLA_APPOINTMENT_COMPLETED: "SLA Appointment Completed",
    TimelineEvent.SLA_APPOINTMENT_BREACHED: "SLA Appointment Breached",
    TimelineEvent.SLA_RESOLUTION_COMPLETED: "SLA Resolution Completed",
    TimelineEvent.SLA_RESOLUTION_BREACHED: "SLA Resolution Breached",
    TimelineEvent.SLA_ESCALATION_COMPLETED: "SLA Escalation Completed",
    TimelineEvent.SLA_ESCALATION_BREACHED: "SLA Escalation Breached",
    TimelineEvent.SLA_OVERALL_COMPLETED: "SLA Overall Completed",
    TimelineEvent.SLA_OVERALL_BREACHED: "SLA Overall Breached",
}


def timeline_event_for_transition(
    *,
    stage: str,
    old_status: str | SlaStatus,
    new_status: str | SlaStatus,
) -> TimelineEvent | None:
    """Return timeline event type when status changes to COMPLETED or BREACHED."""
    old = str(old_status)
    new = str(new_status)
    if old == new:
        return None
    if new not in {SlaStatus.COMPLETED, SlaStatus.BREACHED}:
        return None

    for key, _due_attr, _status_attr, completed_evt, breached_evt in _SLA_STAGE_SPECS:
        if key != stage:
            continue
        if new == SlaStatus.COMPLETED:
            return completed_evt
        if new == SlaStatus.BREACHED:
            return breached_evt
    return None


def timeline_summary(event: TimelineEvent) -> str:
    return _SUMMARY.get(event, event.value)


def iter_sla_stage_specs() -> tuple[tuple[str, str, str, TimelineEvent, TimelineEvent], ...]:
    return _SLA_STAGE_SPECS


def build_sla_timeline_metadata(
    *,
    stage: str,
    old_status: str | SlaStatus,
    new_status: str | SlaStatus,
    due_at: datetime | None,
    occurred_at: datetime,
) -> dict[str, object]:
    return {
        "changeType": "SLA_STATUS_CHANGED",
        "slaStage": stage,
        "oldStatus": str(old_status),
        "newStatus": str(new_status),
        "dueAt": due_at.isoformat() if due_at is not None else None,
        "occurredAt": occurred_at.isoformat(),
        "actor": "SYSTEM",
    }
