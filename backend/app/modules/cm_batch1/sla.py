"""Complaint resolution SLA — DEC-031 (30 calendar days, uniform).

Pure computation: no DB, no clock of its own, no side effects. Every value is
derived at read time from ``created_at``, ``closed_at`` and the configured
target. FR-030 / ADR-CAP006-002 Fase 2 reuses **this** function from the
scheduled sweep — do not invent a second calendar formula (G3.1).

Calendar is 24x7 (BR-ECMF-05 / DEC-004): Saturdays, Sundays and public
holidays are counted. BR-006 Working Day SLA remains Deferred; activating it
would be its own DEC restating the target in working days.

Measured on the **Complaint**, not the Case — a recorded deviation from BR-006
(DEC-031 §2.3): what is promised to the customer is the resolution of the
complaint they filed, not of an internal work unit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.modules.cm_batch1.predicates import is_closed

#: Still open, inside the target.
SLA_ON_TRACK = "ON_TRACK"
#: Still open, target already passed.
SLA_OVERDUE = "OVERDUE"
#: Closed within the target.
SLA_MET = "MET"
#: Closed after the target had passed.
SLA_MISSED = "MISSED"

SLA_STATUSES: tuple[str, ...] = (SLA_ON_TRACK, SLA_OVERDUE, SLA_MET, SLA_MISSED)

#: Statuses that still need someone to act. ``MET``/``MISSED`` are settled.
SLA_OPEN_STATUSES: tuple[str, ...] = (SLA_ON_TRACK, SLA_OVERDUE)


def _as_utc(value: datetime) -> datetime:
    """Naive timestamps are stored UTC; make that explicit before arithmetic."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class _ClosableComplaint(Protocol):
    """Shared shape of the ORM row and the in-memory ``ComplaintAggregate``."""

    status: str
    closed_at: datetime | None


def apply_complaint_status(
    row: _ClosableComplaint,
    new_status: str,
    *,
    now: datetime | None = None,
) -> None:
    """Set ``status`` and keep ``closed_at`` in lockstep (DEC-031).

    The single place either field changes. Complaints close along several
    routes — branch walk-away at intake, HQ completion, auto-close once every
    Case is settled — and can go back to IN_PROGRESS when a new Case starts
    work. Stamping at each of those call sites separately is how the counts in
    ``predicates.py`` drifted before it existed; one helper keeps the pair
    consistent by construction.

    Re-closing a complaint that is already CLOSED does **not** move an existing
    stamp: the first closure is when the work finished. Reopening clears it, so
    the next closure stamps afresh and the SLA measures the current cycle.
    """
    closing = is_closed(new_status)
    if closing and row.closed_at is None:
        row.closed_at = now or datetime.now(UTC)
    elif not closing:
        row.closed_at = None
    row.status = new_status


@dataclass(frozen=True)
class ComplaintSla:
    """One complaint's SLA position at a given instant."""

    target_days: int
    started_at: datetime
    due_at: datetime
    closed_at: datetime | None
    status: str
    #: Whole days elapsed from registration to closure (or to ``now`` if open).
    elapsed_days: int
    #: Whole days left before ``due_at``; ``0`` once due. ``None`` when settled.
    remaining_days: int | None
    #: Whole days past ``due_at``. ``None`` while inside the target.
    overdue_days: int | None
    #: Open, past the warning threshold, not yet overdue (DEC-031 §2.7).
    is_warning: bool

    @property
    def is_open(self) -> bool:
        return self.status in SLA_OPEN_STATUSES

    @property
    def needs_attention(self) -> bool:
        """Drives the in-app alert feed: approaching breach, or breached."""
        return self.status == SLA_OVERDUE or self.is_warning


def resolve_complaint_sla(
    *,
    created_at: datetime | None,
    closed_at: datetime | None,
    status: str | None,
    target_days: int,
    warning_percent: int = 80,
    now: datetime | None = None,
) -> ComplaintSla | None:
    """SLA position, or ``None`` when it cannot be stated.

    ``None`` means "no SLA to show", for one of three honest reasons:
    measurement is switched off (``target_days <= 0``), the complaint has no
    registration timestamp, or it is closed but its closure time was never
    stamped. The last case should not occur — every closure path stamps
    ``closed_at`` and migration 0100 backfilled the existing rows — but
    guessing from ``updated_at`` would be wrong (any edit moves it), so an
    unknown stays unknown rather than becoming a fabricated MET/MISSED.
    """
    if target_days <= 0 or created_at is None:
        return None

    started_at = _as_utc(created_at)
    due_at = started_at + timedelta(days=target_days)
    closed = is_closed(status)

    if closed:
        if closed_at is None:
            return None
        end = _as_utc(closed_at)
        # A closure stamped before registration would make elapsed negative;
        # clamp so a clock-skew artifact cannot read as "resolved in -1 days".
        elapsed = max(timedelta(0), end - started_at)
        return ComplaintSla(
            target_days=target_days,
            started_at=started_at,
            due_at=due_at,
            closed_at=end,
            status=SLA_MET if end <= due_at else SLA_MISSED,
            elapsed_days=elapsed.days,
            remaining_days=None,
            overdue_days=max(0, (end - due_at).days) if end > due_at else None,
            is_warning=False,
        )

    current = _as_utc(now) if now is not None else datetime.now(UTC)
    elapsed = max(timedelta(0), current - started_at)
    overdue = current > due_at
    # Warning fires from ``warning_percent`` of the target onward. Compared on
    # exact instants, not on whole days, so the 80%-of-30-days boundary lands
    # on day 24 without an off-by-one at the edge.
    warning_at = started_at + timedelta(
        seconds=timedelta(days=target_days).total_seconds() * (warning_percent / 100)
    )
    return ComplaintSla(
        target_days=target_days,
        started_at=started_at,
        due_at=due_at,
        closed_at=None,
        status=SLA_OVERDUE if overdue else SLA_ON_TRACK,
        elapsed_days=elapsed.days,
        remaining_days=None if overdue else max(0, (due_at - current).days),
        overdue_days=(current - due_at).days if overdue else None,
        is_warning=(not overdue) and current >= warning_at,
    )
