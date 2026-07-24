"""In-memory DashboardProjectionStore — single projection (TASK-050).

No database, cache, or materialized view. Updates only via Complaint events.
Does not call ComplaintService or query Complaint aggregates.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.enums import ComplaintStatus
from app.modules.complaint_events.models import ComplaintEvent, ComplaintEventType
from app.modules.dashboard.projection_models import DashboardProjection

_TERMINAL = frozenset(
    {
        ComplaintStatus.RESOLVED.value,
        ComplaintStatus.CLOSED.value,
    }
)

# Status → private counter attribute on the store.
_STATUS_ATTR: dict[str, str] = {
    ComplaintStatus.ASSIGNED.value: "_assigned",
    ComplaintStatus.IN_PROGRESS.value: "_in_progress",
    ComplaintStatus.RESOLVED.value: "_resolved",
    ComplaintStatus.CLOSED.value: "_closed",
    ComplaintStatus.ESCALATED.value: "_escalated",
}


def _is_open(status: str | None) -> bool:
    return status is not None and status not in _TERMINAL


class DashboardProjectionStore:
    """Process-local single dashboard projection (discarded on process end)."""

    def __init__(self) -> None:
        self._total = 0
        self._open = 0
        self._assigned = 0
        self._in_progress = 0
        self._resolved = 0
        self._closed = 0
        self._escalated = 0
        self._breached_sla = 0
        self._updated_at = datetime.now(UTC)

    def snapshot(self) -> DashboardProjection:
        """Return an immutable snapshot of current counters."""
        return DashboardProjection(
            total_complaints=self._total,
            open_complaints=self._open,
            assigned_complaints=self._assigned,
            in_progress_complaints=self._in_progress,
            resolved_complaints=self._resolved,
            closed_complaints=self._closed,
            escalated_complaints=self._escalated,
            breached_sla=self._breached_sla,
            updated_at=self._updated_at,
        )

    def reset(self) -> None:
        """Clear counters (tests / diagnostics)."""
        self._total = 0
        self._open = 0
        self._assigned = 0
        self._in_progress = 0
        self._resolved = 0
        self._closed = 0
        self._escalated = 0
        self._breached_sla = 0
        self._updated_at = datetime.now(UTC)

    def apply(self, event: ComplaintEvent) -> DashboardProjection:
        """Apply one ComplaintEvent and return the new immutable snapshot."""
        if event.event_type == ComplaintEventType.CREATED:
            self._apply_created(event)
        elif event.event_type == ComplaintEventType.ACCEPTED:
            # Lifecycle marker only — Assigned→InProgress also emits InProgress;
            # counters move on that event to avoid double-count.
            self._touch(event.occurred_at)
        else:
            self._apply_transition(event)

        if event.payload.get("slaBreached") is True:
            self._breached_sla += 1

        return self.snapshot()

    def _touch(self, occurred_at: datetime) -> None:
        self._updated_at = (
            occurred_at if occurred_at.tzinfo else occurred_at.replace(tzinfo=UTC)
        )

    def _apply_created(self, event: ComplaintEvent) -> None:
        self._total += 1
        self._open += 1
        self._touch(event.occurred_at)

    def _adjust_status(self, status: str, delta: int) -> None:
        attr = _STATUS_ATTR.get(status)
        if attr is None:
            return
        setattr(self, attr, max(0, getattr(self, attr) + delta))

    def _apply_transition(self, event: ComplaintEvent) -> None:
        to_status = event.current_status
        raw_from = event.payload.get("fromStatus")
        from_status = raw_from if isinstance(raw_from, str) else None

        if from_status is not None and from_status == to_status:
            self._touch(event.occurred_at)
            return

        if from_status is not None:
            self._adjust_status(from_status, -1)
            if _is_open(from_status) and not _is_open(to_status):
                self._open = max(0, self._open - 1)
            elif not _is_open(from_status) and _is_open(to_status):
                self._open += 1

        self._adjust_status(to_status, +1)
        self._touch(event.occurred_at)
