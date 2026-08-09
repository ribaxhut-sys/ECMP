"""Allowed status transitions for Pengaduan Internal (resolve/close via dedicated ops)."""

from __future__ import annotations

from app.modules.internal_complaint.domain.value_objects import InternalStatus

_STATUS_EDGES: frozenset[tuple[InternalStatus, InternalStatus]] = frozenset(
    {
        (InternalStatus.CREATED, InternalStatus.ASSIGNED),
        (InternalStatus.CREATED, InternalStatus.IN_PROGRESS),
        (InternalStatus.ASSIGNED, InternalStatus.IN_PROGRESS),
        (InternalStatus.ASSIGNED, InternalStatus.ASSIGNED),
        (InternalStatus.IN_PROGRESS, InternalStatus.ASSIGNED),
    }
)


def can_transition_status(current: InternalStatus, target: InternalStatus) -> bool:
    return (current, target) in _STATUS_EDGES
