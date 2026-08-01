"""Complaint status lifecycle rules (CAPABILITY-004 / CAPABILITY-005).

Domain-owned transitions. No infrastructure. No HTTP.

Happy path:
  OPEN → IN_PROGRESS → RESOLVED → CLOSED

Reopen:
  RESOLVED → IN_PROGRESS
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from app.modules.complaint.domain.errors import ComplaintDomainError
from app.modules.complaint.domain.models import ComplaintStatus

_ALLOWED: Mapping[ComplaintStatus, frozenset[ComplaintStatus]] = MappingProxyType(
    {
        ComplaintStatus.OPEN: frozenset({ComplaintStatus.IN_PROGRESS}),
        ComplaintStatus.IN_PROGRESS: frozenset({ComplaintStatus.RESOLVED}),
        ComplaintStatus.RESOLVED: frozenset(
            {ComplaintStatus.CLOSED, ComplaintStatus.IN_PROGRESS}
        ),
        ComplaintStatus.CLOSED: frozenset(),
    }
)


def allowed_transitions(status: ComplaintStatus) -> frozenset[ComplaintStatus]:
    """Return the set of statuses reachable in one step from ``status``."""
    if not isinstance(status, ComplaintStatus):
        raise TypeError(
            f"status must be ComplaintStatus, got {type(status).__name__}"
        )
    return _ALLOWED[status]


def can_transition(current: ComplaintStatus, new_status: ComplaintStatus) -> bool:
    """True when ``current → new_status`` is a single allowed step."""
    if not isinstance(new_status, ComplaintStatus):
        raise TypeError(
            f"new_status must be ComplaintStatus, got {type(new_status).__name__}"
        )
    return new_status in allowed_transitions(current)


def assert_transition(current: ComplaintStatus, new_status: ComplaintStatus) -> None:
    """Raise ``ComplaintDomainError`` when the transition is illegal."""
    if current is new_status:
        return
    if not can_transition(current, new_status):
        raise ComplaintDomainError(
            "INVALID_COMPLAINT_TRANSITION",
            f"transisi status pengaduan tidak valid: "
            f"{current.value} → {new_status.value}",
        )


__all__ = [
    "allowed_transitions",
    "assert_transition",
    "can_transition",
]
