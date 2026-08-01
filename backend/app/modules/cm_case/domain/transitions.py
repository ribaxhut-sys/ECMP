"""Mode A Delivery Transition Subset (FRD Appendix B / BQ-006/008/009/014)."""

from __future__ import annotations

from app.modules.cm_case.domain.value_objects import CaseStatus

# Explicit allowed edges for FR-004 status PATCH (resolve/close are separate ops).
_STATUS_EDGES: frozenset[tuple[CaseStatus, CaseStatus]] = frozenset(
    {
        (CaseStatus.CREATED, CaseStatus.ASSIGNED),
        (CaseStatus.CREATED, CaseStatus.CANCELLED),
        (CaseStatus.ASSIGNED, CaseStatus.IN_PROGRESS),
        (CaseStatus.ASSIGNED, CaseStatus.ASSIGNED),  # Unit reassign
        (CaseStatus.ASSIGNED, CaseStatus.CANCELLED),
        (CaseStatus.IN_PROGRESS, CaseStatus.ASSIGNED),
        (CaseStatus.IN_PROGRESS, CaseStatus.CANCELLED),
    }
)

_NOT_EXPOSED = frozenset({"PENDING", "ESCALATED"})


def is_not_exposed_status(value: str) -> bool:
    return value.strip().upper() in _NOT_EXPOSED


def can_transition_status(current: CaseStatus, target: CaseStatus) -> bool:
    return (current, target) in _STATUS_EDGES
