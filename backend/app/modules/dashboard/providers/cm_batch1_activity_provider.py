"""Dashboard 'Recent Activity' sourced from the CM Batch 1 Aggregate.

UM-BUG-008 — dashboard/service.py's overview() previously composed recent
activity from the legacy ``complaint_timelines`` + ``complaints`` tables
(app.modules.timelines / app.modules.complaints), which the running system
no longer writes to (DEC-020 coexistence: complaints are now created via
CM Batch 1). Real history lives in ``timeline_entries``
(app.modules.timeline, CAPABILITY-010), written by CmBatch1HistoryService.
This provider reads from there instead.

Branch scope (UM-BUG-009 / P1): filter by ``cm_batch1_complaints.owning_unit_id``
matched to ``Branch.code`` — same SoT as Aggregate list visibility (DEC-024
pattern). Creator ``User.branch_id`` is no longer used for complaint KPI/activity.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Interval, and_, case, func, literal, not_, or_, select
from sqlalchemy.orm import Session

from app.integrations.directory import LocalUserDirectory
from app.models import Branch
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.predicates import CLOSED_STATUS, ESCALATION_ACTIVE, HQ_SCHEDULED
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.sla import SLA_OVERDUE, resolve_complaint_sla
from app.modules.cm_batch1.sla_thresholds import classify_in_app_threshold
from app.modules.cm_case.infrastructure.orm import CmCaseORM
from app.modules.dashboard.schemas import (
    ComplaintSlaAlertItem,
    ComplaintSlaAlertsResponse,
    DashboardAggregateKpiResponse,
    DashboardRecentActivityItem,
    DashboardResolutionSla,
)
from app.modules.timeline.repository import TimelineRepository

_AGGREGATE_TYPE = "Complaint"  # matches app/modules/cm_batch1/history.py
_SYSTEM_ACTOR = "SYSTEM"

# CM Batch 1 event_type (+ metadata.decision for IntakeEscalationDecided) ->
# legacy-style dotted eventType the frontend's activityLabels.ts already
# resolves to a label/badge. Keeps the UI vocabulary stable across the
# SoT switch — only the read source changed.
# Unknown timeline rows must not look like a business "update".
_UNKNOWN_DASHBOARD_EVENT = "complaint.other"

_EVENT_TYPE_MAP: dict[str, str] = {
    "ComplaintRegistered": "complaint.created",
    "HqAccepted": "complaint.hq_accepted",
    "HqReturned": "complaint.hq_returned",
    "HqArrivalScheduled": "complaint.hq_arrival_scheduled",
    "HqCompleted": "complaint.closed",
    "HandlingContinued": "complaint.handling_continued",
    "HandlingTakenOver": "complaint.handling_taken_over",
    "CaseCreated": "complaint.case_created",
    "CaseAssigned": "complaint.assigned",
    "CaseCancelled": "complaint.case_cancelled",
    "CaseStatusChanged": "complaint.case_status_changed",
    "CaseClosed": "complaint.closed",
    "CaseResolved": "complaint.resolved",
    "ResolutionUpdated": "complaint.resolution_updated",
    "CaseHandlingUnitAccepted": "complaint.handling_unit_accepted",
    "CaseOwnerAccepted": "complaint.owner_accepted",
    "CaseHandlingUnitRejected": "complaint.handling_unit_rejected",
    "CaseOwnerRejected": "complaint.owner_rejected",
    "CaseEscalatedToPusat": "complaint.escalated_to_pusat",
    "CaseEscalationToPusatCancelled": "complaint.escalation_to_pusat_cancelled",
    "CaseEscalationReturned": "complaint.escalation_returned",
    "SLABreached": "sla.resolution.breached",
}
_DECISION_EVENT_TYPE_MAP: dict[str, str] = {
    "APPROVE": "complaint.escalation_approved",
    "REJECT": "complaint.escalation_rejected",
    "RE_ESCALATE": "complaint.escalation_requested",
    "CANCEL": "complaint.escalation_cancelled",
}
_DISPOSITION_EVENT_TYPE_MAP: dict[str, str] = {
    "ESCALATE_PENDING_APPROVAL": "complaint.escalation_requested",
    "ESCALATE_APPROVED": "complaint.escalation_approved",
    "HQ_SCHEDULED": "complaint.hq_arrival_scheduled",
    "RETURNED_TO_BRANCH": "complaint.hq_returned",
    "BRANCH_CLOSED": "complaint.closed",
    "HQ_CLOSED": "complaint.closed",
}


def _map_event_type(event_type: str, metadata: dict) -> str:
    if event_type == "IntakeEscalationDecided":
        decision = str(metadata.get("decision") or "").upper()
        return _DECISION_EVENT_TYPE_MAP.get(decision, _UNKNOWN_DASHBOARD_EVENT)
    if event_type == "IntakeDispositionRecorded":
        disposition = str(metadata.get("intakeDisposition") or "").upper()
        return _DISPOSITION_EVENT_TYPE_MAP.get(disposition, _UNKNOWN_DASHBOARD_EVENT)
    return _EVENT_TYPE_MAP.get(event_type, _UNKNOWN_DASHBOARD_EVENT)


# Attachment bind/upload/void is complaint history, not dashboard "Pembaruan".
# Duplicate / SLA-threshold ticks belong on the complaint log, not the 10-row feed.
_DASHBOARD_HIDDEN_EVENT_TYPES = frozenset(
    {
        "AttachmentUploaded",
        "AttachmentBound",
        "AttachmentSuperseded",
        "AttachmentVoided",
        "AttachmentTransferred",
        "CaseWorkStarted",
        "DuplicateFound",
        "DuplicateOverridden",
        "DuplicateLinked",
        "DuplicateRedirected",
        "DuplicateRecommended",
        "DuplicateBlocked",
        "ComplaintSlaThreshold",
    }
)

# F4 close path is one business outcome on the dashboard. Keep CaseClosed;
# drop resolve + dual-accept rows for the same complaint when close is present.
# Do not hide ComplaintRegistered — creation remains a visible activity.
_CLOSE_PATH_PRECURSOR_EVENT_TYPES = frozenset(
    {
        "CaseResolved",
        "ResolutionUpdated",
        "CaseHandlingUnitAccepted",
        "CaseOwnerAccepted",
    }
)


def _is_case_closed_event(entry: Any) -> bool:
    if entry.event_type in {"CaseClosed", "HqCompleted"}:
        return True
    if entry.event_type != "IntakeDispositionRecorded":
        return False
    disposition = str((entry.metadata or {}).get("intakeDisposition") or "").upper()
    return disposition in {"BRANCH_CLOSED", "HQ_CLOSED"}


def _omit_close_path_precursors(entries: list[Any]) -> list[Any]:
    closed_ids = {entry.aggregate_id for entry in entries if _is_case_closed_event(entry)}
    if not closed_ids:
        return entries
    return [
        entry
        for entry in entries
        if not (
            entry.event_type in _CLOSE_PATH_PRECURSOR_EVENT_TYPES
            and entry.aggregate_id in closed_ids
        )
    ]


def _tally(condition: Any, label: str) -> Any:
    """One conditional count column — a slice of the single grouped pass."""
    return func.coalesce(func.sum(case((condition, 1), else_=0)), 0).label(label)


def _empty_sla(target_days: int) -> DashboardResolutionSla | None:
    if target_days <= 0:
        return None
    return DashboardResolutionSla(targetDays=target_days)


def _sla_columns(
    target_days: int, warning_percent: int, now: datetime | None
) -> list[Any]:
    """DEC-031 slices, expressed against ``created_at`` / ``closed_at``.

    Thresholds are resolved to absolute instants here rather than in SQL so the
    statement stays free of database-side ``now()`` — the same instant then
    governs every slice, and a caller can pin it for a deterministic test.
    """
    current = now or datetime.now(UTC)
    target = timedelta(days=target_days)
    # Registered at or before this instant means the target has elapsed.
    overdue_cutoff = current - target
    warning_cutoff = current - timedelta(
        seconds=target.total_seconds() * (warning_percent / 100)
    )

    created = CmBatch1ComplaintORM.created_at
    closed_at = CmBatch1ComplaintORM.closed_at
    is_open = CmBatch1ComplaintORM.status != CLOSED_STATUS
    is_closed_row = CmBatch1ComplaintORM.status == CLOSED_STATUS
    # Resolution duration compared in the database: closed_at <= created_at +
    # target. Postgres does the interval arithmetic per row, so a complaint
    # registered in January and one registered in June are judged alike.
    within_target = closed_at <= created + literal(target, Interval())

    return [
        _tally(and_(is_open, created > warning_cutoff), "sla_on_track"),
        _tally(
            and_(is_open, created <= warning_cutoff, created > overdue_cutoff),
            "sla_warning",
        ),
        _tally(and_(is_open, created <= overdue_cutoff), "sla_overdue"),
        _tally(
            and_(is_closed_row, closed_at.is_not(None), within_target), "sla_met"
        ),
        _tally(
            and_(is_closed_row, closed_at.is_not(None), not_(within_target)),
            "sla_missed",
        ),
        # Closed but never stamped. Reported as its own number instead of being
        # folded into met/missed, so a gap in the data cannot flatter the
        # compliance figure.
        _tally(and_(is_closed_row, closed_at.is_(None)), "sla_unknown"),
    ]


def _sla_from_row(row: Any, target_days: int) -> DashboardResolutionSla:
    met = int(row.sla_met or 0)
    missed = int(row.sla_missed or 0)
    settled = met + missed
    return DashboardResolutionSla(
        targetDays=target_days,
        onTrack=int(row.sla_on_track or 0),
        warning=int(row.sla_warning or 0),
        overdue=int(row.sla_overdue or 0),
        met=met,
        missed=missed,
        unknown=int(row.sla_unknown or 0),
        compliancePercentage=(
            round(met / settled * 100.0, 2) if settled > 0 else None
        ),
    )


class CmBatch1ActivityDashboardProvider:
    """Read-only recent-activity feed backed by timeline_entries + cm_batch1_complaints."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._timeline = TimelineRepository(session)
        self._complaints = CmBatch1Repository(session)
        self._directory = LocalUserDirectory(session)

    def list_recent(
        self, *, limit: int, branch_id: uuid.UUID | None = None
    ) -> list[DashboardRecentActivityItem]:
        aggregate_ids: set[uuid.UUID] | None = None
        if branch_id is not None:
            aggregate_ids = self._complaint_ids_for_branch(branch_id)
            if not aggregate_ids:
                return []

        entries = self._timeline.list_recent(
            aggregate_type=_AGGREGATE_TYPE,
            limit=min(100, max(limit * 4, limit)),
            aggregate_ids=aggregate_ids,
        )
        if not entries:
            return []

        visible = [
            entry
            for entry in entries
            if entry.event_type not in _DASHBOARD_HIDDEN_EVENT_TYPES
            and _map_event_type(entry.event_type, entry.metadata)
            != _UNKNOWN_DASHBOARD_EVENT
        ]
        visible = _omit_close_path_precursors(visible)[:limit]
        if not visible:
            return []

        actor_ids = {e.actor_id for e in visible if e.actor_id}
        actor_names = self._directory.display_names(actor_ids) if actor_ids else {}
        complaint_numbers = self._complaints.complaint_numbers_by_ids(
            {e.aggregate_id for e in visible}
        )
        # Pre-case events (registered, HQ accepted/scheduled, ...) carry no
        # caseNumber on their own metadata even once a Case exists for the
        # same complaint — fall back to the Case that complaint actually has.
        case_numbers_by_complaint = self._case_numbers_by_complaint_ids(
            {e.aggregate_id for e in visible}
        )

        items: list[DashboardRecentActivityItem] = []
        for entry in visible:
            complaint_number = complaint_numbers.get(entry.aggregate_id) or str(
                entry.metadata.get("complaintNumber") or entry.aggregate_id
            )
            actor_name = (
                (actor_names.get(entry.actor_id) if entry.actor_id else None)
                or entry.actor_name
                or _SYSTEM_ACTOR
            )
            case_number = (
                str((entry.metadata or {}).get("caseNumber") or "").strip()
                or case_numbers_by_complaint.get(entry.aggregate_id)
            )
            items.append(
                DashboardRecentActivityItem(
                    eventType=_map_event_type(entry.event_type, entry.metadata),
                    complaintNumber=complaint_number,
                    timestamp=entry.created_at,
                    actor=actor_name,
                    caseNumber=case_number,
                )
            )
        # Same-second create+escalate often lists "created" above "escalation"
        # (registration is written first). Prefer pending-approval on top for
        # that pair only — do not re-sort the whole feed by timestamp.
        out = list(items)
        i = 0
        while i < len(out) - 1:
            a, b = out[i], out[i + 1]
            close_in_time = (
                a.timestamp is not None
                and b.timestamp is not None
                and abs((a.timestamp - b.timestamp).total_seconds()) <= 1
            )
            if (
                a.complaint_number == b.complaint_number
                and close_in_time
                and a.event_type == "complaint.created"
                and b.event_type
                in {"complaint.escalation_requested", "complaint.closed"}
            ):
                out[i], out[i + 1] = b, a
                i += 2
                continue
            i += 1
        return out

    def complaint_kpis(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        target_days: int = 0,
        warning_percent: int = 80,
        now: datetime | None = None,
    ) -> DashboardAggregateKpiResponse:
        """COUNT Aggregate complaints, optionally locked to one branch unit.

        Scope = ``owning_unit_id`` equal to ``Branch.code`` for ``branch_id``.
        Matches Aggregate list UNIT visibility (not creator membership).

        ``date_from``/``date_to`` narrow the same counts to a registration
        window (``created_at``) so /reports can report per period while still
        reading the one Aggregate SoT the dashboard reads (DEC-026).

        ``target_days > 0`` adds the DEC-031 resolution-SLA rollup. It rides
        along in the same statement deliberately: this endpoint is polled every
        60s by the dashboard, and it used to issue eight sequential COUNT(*)
        round-trips for what one grouped pass answers. Adding six more counts
        the old way would have made a known cost worse.
        """
        owning_unit: str | None
        if branch_id is None:
            owning_unit = None  # unrestricted
        else:
            owning_unit = self._owning_unit_for_branch(branch_id)
            if not owning_unit:
                return DashboardAggregateKpiResponse(
                    total=0,
                    open=0,
                    closed=0,
                    escalatePending=0,
                    waitingAssignment=0,
                    escalateApproved=0,
                    escalateScheduled=0,
                    hqAcceptedOpen=0,
                    returnedToBranch=0,
                    inProgress=0,
                    sla=_empty_sla(target_days),
                )

        status_col = CmBatch1ComplaintORM.status
        disposition = CmBatch1ComplaintORM.intake_disposition
        is_open = status_col != CLOSED_STATUS
        is_closed_row = status_col == CLOSED_STATUS
        # "Registered" is every non-closed, non-in-progress row — an out-of-set
        # stored status is exposed as REGISTERED by cm_batch1/service.py and
        # must land here too, so open+closed==total holds.
        registered = status_col.notin_((CLOSED_STATUS, "IN_PROGRESS"))
        not_escalating = or_(
            disposition.is_(None),
            disposition.notin_(ESCALATION_ACTIVE),
        )

        columns: list[Any] = [
            func.count().label("total"),
            # Open = not CLOSED (DEC-025 M-025-1 / predicates.is_open).
            _tally(is_open, "open_count"),
            _tally(is_closed_row, "closed"),
            _tally(
                and_(registered, disposition == "ESCALATE_PENDING_APPROVAL"),
                "escalate_pending",
            ),
            # Registered but not held in an escalation path — the whole
            # ESCALATION_ACTIVE set has its own slice, HQ_SCHEDULED included.
            _tally(and_(registered, not_escalating), "waiting_assignment"),
            _tally(
                and_(registered, disposition == "ESCALATE_APPROVED"),
                "escalate_approved",
            ),
            # A scheduled HQ visit binds a Case, so these rows are usually
            # IN_PROGRESS; they are still escalation, not ordinary handling.
            _tally(and_(is_open, disposition == HQ_SCHEDULED), "escalate_scheduled"),
            # Cabang work-book exclusion: Pusat has already taken the row.
            _tally(
                and_(
                    is_open,
                    or_(
                        CmBatch1ComplaintORM.hq_accepted_at.is_not(None),
                        disposition == HQ_SCHEDULED,
                    ),
                ),
                "hq_accepted_open",
            ),
            _tally(
                and_(is_open, disposition == "RETURNED_TO_BRANCH"),
                "returned_to_branch",
            ),
            _tally(
                and_(
                    status_col == "IN_PROGRESS",
                    or_(disposition.is_(None), disposition != HQ_SCHEDULED),
                ),
                "in_progress",
            ),
        ]

        measuring = target_days > 0
        if measuring:
            columns.extend(_sla_columns(target_days, warning_percent, now))

        stmt = select(*columns).select_from(CmBatch1ComplaintORM)
        if owning_unit is not None:
            stmt = stmt.where(CmBatch1ComplaintORM.owning_unit_id == owning_unit)
        if date_from is not None:
            stmt = stmt.where(CmBatch1ComplaintORM.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(CmBatch1ComplaintORM.created_at <= date_to)
        row = self._session.execute(stmt).one()

        return DashboardAggregateKpiResponse(
            total=int(row.total or 0),
            open=int(row.open_count or 0),
            closed=int(row.closed or 0),
            escalatePending=int(row.escalate_pending or 0),
            waitingAssignment=int(row.waiting_assignment or 0),
            escalateApproved=int(row.escalate_approved or 0),
            escalateScheduled=int(row.escalate_scheduled or 0),
            hqAcceptedOpen=int(row.hq_accepted_open or 0),
            returnedToBranch=int(row.returned_to_branch or 0),
            inProgress=int(row.in_progress or 0),
            sla=_sla_from_row(row, target_days) if measuring else None,
        )

    def sla_alerts(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        target_days: int,
        warning_percent: int = 80,
        limit: int = 20,
        now: datetime | None = None,
    ) -> ComplaintSlaAlertsResponse:
        """Open complaints at or past the warning threshold, worst first.

        The list is capped, but ``overdueCount``/``warningCount`` are counted
        over the whole scope so a badge never under-reports because the feed
        was truncated.
        """
        if target_days <= 0:
            return ComplaintSlaAlertsResponse(targetDays=target_days)

        owning_unit: str | None = None
        if branch_id is not None:
            owning_unit = self._owning_unit_for_branch(branch_id)
            if not owning_unit:
                return ComplaintSlaAlertsResponse(targetDays=target_days)

        current = now or datetime.now(UTC)
        warning_cutoff = current - timedelta(
            seconds=timedelta(days=target_days).total_seconds()
            * (warning_percent / 100)
        )

        stmt = (
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.status != CLOSED_STATUS)
            .where(CmBatch1ComplaintORM.created_at <= warning_cutoff)
            # Oldest first: the most overdue complaint is the one to act on.
            .order_by(CmBatch1ComplaintORM.created_at.asc())
        )
        if owning_unit is not None:
            stmt = stmt.where(CmBatch1ComplaintORM.owning_unit_id == owning_unit)
        rows = list(self._session.scalars(stmt).all())

        items: list[ComplaintSlaAlertItem] = []
        overdue_count = 0
        warning_count = 0
        for row in rows:
            # Same function the complaint detail and list use — one definition
            # of "overdue", so a badge and a row can never disagree.
            sla = resolve_complaint_sla(
                created_at=row.created_at,
                closed_at=row.closed_at,
                status=row.status,
                target_days=target_days,
                warning_percent=warning_percent,
                now=current,
            )
            if sla is None or not sla.needs_attention:
                continue
            if sla.status == SLA_OVERDUE:
                overdue_count += 1
            else:
                warning_count += 1
            if len(items) < limit:
                items.append(
                    ComplaintSlaAlertItem(
                        complaintId=str(row.id),
                        complaintNumber=row.complaint_number,
                        subject=row.subject,
                        owningUnitId=row.owning_unit_id,
                        priority=row.priority,
                        dueAt=sla.due_at,
                        elapsedDays=sla.elapsed_days,
                        remainingDays=sla.remaining_days,
                        overdueDays=sla.overdue_days,
                        isOverdue=sla.status == SLA_OVERDUE,
                        threshold=classify_in_app_threshold(sla),
                    )
                )
        return ComplaintSlaAlertsResponse(
            targetDays=target_days,
            overdueCount=overdue_count,
            warningCount=warning_count,
            items=items,
        )

    def _owning_unit_for_branch(self, branch_id: uuid.UUID) -> str | None:
        """Map dashboard ``branchId`` (UUID) → org unit key stored on Aggregate."""
        branch = self._session.get(Branch, branch_id)
        if branch is None or getattr(branch, "deleted_at", None) is not None:
            return None
        code = (getattr(branch, "code", None) or "").strip()
        return code or None

    def _complaint_ids_for_branch(self, branch_id: uuid.UUID) -> set[uuid.UUID]:
        """Complaint ids whose ``owning_unit_id`` matches the branch code."""
        unit = self._owning_unit_for_branch(branch_id)
        if not unit:
            return set()
        complaint_ids = self._session.scalars(
            select(CmBatch1ComplaintORM.id).where(
                CmBatch1ComplaintORM.owning_unit_id == unit
            )
        ).all()
        return set(complaint_ids)

    def _case_numbers_by_complaint_ids(
        self, complaint_ids: set[uuid.UUID]
    ) -> dict[uuid.UUID, str]:
        """Most recent Case number per complaint (``cm_cases.complaint_id`` is a
        string column, so lookups happen by string then map back to UUID)."""
        if not complaint_ids:
            return {}
        id_strings = {str(cid) for cid in complaint_ids}
        rows = self._session.execute(
            select(CmCaseORM.complaint_id, CmCaseORM.case_number)
            .where(CmCaseORM.complaint_id.in_(id_strings))
            .order_by(CmCaseORM.complaint_id, CmCaseORM.created_at.desc())
        ).all()
        latest: dict[str, str] = {}
        for complaint_id, case_number in rows:
            latest.setdefault(complaint_id, case_number)
        return {
            cid: latest[str(cid)] for cid in complaint_ids if str(cid) in latest
        }
