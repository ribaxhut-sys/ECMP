"""Complaint status transition matrix (TASK-009 / TASK-010).

NEW → ASSIGNED is performed by the Assign endpoint (API-205), not this matrix.
IN_PROGRESS → RESOLVED is performed by the Resolution endpoint (API-225).
Escalation to ESCALATED remains owned by the Escalation endpoint (out of TASK-009).
"""

from __future__ import annotations

from app.core.enums import ComplaintStatus

ALLOWED_TRANSITIONS: dict[ComplaintStatus, frozenset[ComplaintStatus]] = {
    ComplaintStatus.NEW: frozenset(),  # use Assign (API-205)
    ComplaintStatus.ASSIGNED: frozenset({ComplaintStatus.IN_PROGRESS}),
    ComplaintStatus.IN_PROGRESS: frozenset({ComplaintStatus.PENDING}),
    ComplaintStatus.PENDING: frozenset({ComplaintStatus.IN_PROGRESS}),
    ComplaintStatus.RESOLVED: frozenset(
        {ComplaintStatus.CLOSED, ComplaintStatus.IN_PROGRESS}
    ),
    ComplaintStatus.CLOSED: frozenset(),
    # Escalation path is separate; no status-transition actions from ESCALATED here.
    ComplaintStatus.ESCALATED: frozenset(),
}


def can_transition(current: ComplaintStatus, target: ComplaintStatus) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, frozenset())


def allowed_targets(current: ComplaintStatus) -> frozenset[ComplaintStatus]:
    return ALLOWED_TRANSITIONS.get(current, frozenset())
