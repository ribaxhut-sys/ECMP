"""In-memory KpiProjectionStore — single projection (TASK-051).

No database, cache, or materialized view. Updates only via Complaint events.
Does not call ComplaintService or query Complaint aggregates.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.enums import ComplaintStatus
from app.modules.complaint_events.models import ComplaintEvent, ComplaintEventType
from app.modules.kpi.projection_models import KpiProjection

_TERMINAL = frozenset(
    {
        ComplaintStatus.RESOLVED.value,
        ComplaintStatus.CLOSED.value,
    }
)


def _is_open(status: str | None) -> bool:
    return status is not None and status not in _TERMINAL


def _safe_rate(numerator: int, denominator: int) -> float:
    """Derived rate with divide-by-zero protection."""
    if denominator <= 0:
        return 0.0
    return numerator / denominator


class KpiProjectionStore:
    """Process-local single KPI projection (discarded on process end)."""

    def __init__(self) -> None:
        self._total_received = 0
        self._total_closed = 0
        self._total_resolved = 0
        self._total_escalated = 0
        self._current_open = 0
        self._current_in_progress = 0
        self._sla_breached = 0
        self._updated_at = datetime.now(UTC)

    def snapshot(self) -> KpiProjection:
        """Return an immutable snapshot of current counters and derived rates."""
        return KpiProjection(
            total_received=self._total_received,
            total_closed=self._total_closed,
            total_resolved=self._total_resolved,
            total_escalated=self._total_escalated,
            current_open=self._current_open,
            current_in_progress=self._current_in_progress,
            sla_breached=self._sla_breached,
            closure_rate=_safe_rate(self._total_closed, self._total_received),
            resolution_rate=_safe_rate(self._total_resolved, self._total_received),
            updated_at=self._updated_at,
        )

    def reset(self) -> None:
        """Clear counters (tests / diagnostics)."""
        self._total_received = 0
        self._total_closed = 0
        self._total_resolved = 0
        self._total_escalated = 0
        self._current_open = 0
        self._current_in_progress = 0
        self._sla_breached = 0
        self._updated_at = datetime.now(UTC)

    def apply(self, event: ComplaintEvent) -> KpiProjection:
        """Apply one ComplaintEvent and return the new immutable snapshot."""
        et = event.event_type
        if et == ComplaintEventType.CREATED:
            self._apply_created(event)
        elif et == ComplaintEventType.ACCEPTED:
            # Lifecycle marker only — Assigned→InProgress also emits InProgress;
            # current counters move on that event to avoid double-count.
            self._touch(event.occurred_at)
        elif et == ComplaintEventType.RESOLVED:
            self._total_resolved += 1
            self._apply_transition(event)
        elif et == ComplaintEventType.CLOSED:
            self._total_closed += 1
            self._apply_transition(event)
        elif et == ComplaintEventType.ESCALATED:
            self._total_escalated += 1
            self._apply_transition(event)
        else:
            # ASSIGNED, IN_PROGRESS, and any other lifecycle transition events
            self._apply_transition(event)

        if event.payload.get("slaBreached") is True:
            self._sla_breached += 1

        return self.snapshot()

    def _touch(self, occurred_at: datetime) -> None:
        self._updated_at = (
            occurred_at if occurred_at.tzinfo else occurred_at.replace(tzinfo=UTC)
        )

    def _apply_created(self, event: ComplaintEvent) -> None:
        self._total_received += 1
        self._current_open += 1
        self._touch(event.occurred_at)

    def _apply_transition(self, event: ComplaintEvent) -> None:
        to_status = event.current_status
        raw_from = event.payload.get("fromStatus")
        from_status = raw_from if isinstance(raw_from, str) else None

        if from_status is not None and from_status == to_status:
            self._touch(event.occurred_at)
            return

        if from_status is not None:
            if from_status == ComplaintStatus.IN_PROGRESS.value:
                self._current_in_progress = max(0, self._current_in_progress - 1)
            if _is_open(from_status) and not _is_open(to_status):
                self._current_open = max(0, self._current_open - 1)
            elif not _is_open(from_status) and _is_open(to_status):
                self._current_open += 1

        if to_status == ComplaintStatus.IN_PROGRESS.value:
            if from_status != ComplaintStatus.IN_PROGRESS.value:
                self._current_in_progress += 1

        self._touch(event.occurred_at)
