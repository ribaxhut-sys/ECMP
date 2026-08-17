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
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.integrations.directory import LocalUserDirectory
from app.models import Branch
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.predicates import CLOSED_STATUS
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.dashboard.schemas import (
    DashboardAggregateKpiResponse,
    DashboardRecentActivityItem,
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
}
_DECISION_EVENT_TYPE_MAP: dict[str, str] = {
    "APPROVE": "complaint.escalation_approved",
    "REJECT": "complaint.escalation_rejected",
    "RE_ESCALATE": "complaint.escalation_requested",
    "CANCEL": "complaint.escalation_cancelled",
}
_DISPOSITION_EVENT_TYPE_MAP: dict[str, str] = {
    "ESCALATE_PENDING_APPROVAL": "complaint.escalation_requested",
    "BRANCH_CLOSED": "complaint.closed",
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
_DASHBOARD_HIDDEN_EVENT_TYPES = frozenset(
    {
        "AttachmentUploaded",
        "AttachmentBound",
        "AttachmentSuperseded",
        "AttachmentVoided",
        "AttachmentTransferred",
        "CaseWorkStarted",
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
    if entry.event_type == "CaseClosed":
        return True
    if entry.event_type != "IntakeDispositionRecorded":
        return False
    disposition = str((entry.metadata or {}).get("intakeDisposition") or "").upper()
    return disposition == "BRANCH_CLOSED"


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
        ]
        visible = _omit_close_path_precursors(visible)[:limit]
        if not visible:
            return []

        actor_ids = {e.actor_id for e in visible if e.actor_id}
        actor_names = self._directory.display_names(actor_ids) if actor_ids else {}

        items: list[DashboardRecentActivityItem] = []
        for entry in visible:
            complaint = self._complaints.get(str(entry.aggregate_id))
            complaint_number = (
                complaint.complaint_number
                if complaint is not None
                else str(entry.metadata.get("complaintNumber") or entry.aggregate_id)
            )
            actor_name = (
                (actor_names.get(entry.actor_id) if entry.actor_id else None)
                or entry.actor_name
                or _SYSTEM_ACTOR
            )
            case_number = str((entry.metadata or {}).get("caseNumber") or "").strip() or None
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
        self, *, branch_id: uuid.UUID | None = None
    ) -> DashboardAggregateKpiResponse:
        """COUNT Aggregate complaints, optionally locked to one branch unit.

        Scope = ``owning_unit_id`` equal to ``Branch.code`` for ``branch_id``.
        Matches Aggregate list UNIT visibility (not creator membership).
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
                    inProgress=0,
                )

        total = self._count_complaints(owning_unit)
        # Open = not CLOSED (DEC-025 M-025-1 / predicates.is_open), matching
        # KPI/dashboard summary — an out-of-set stored status stays open here
        # too, so open+closed=total.
        open_count = self._count_complaints(
            owning_unit,
            CmBatch1ComplaintORM.status != CLOSED_STATUS,
        )
        closed = self._count_complaints(
            owning_unit, CmBatch1ComplaintORM.status == CLOSED_STATUS
        )
        # Donut slices are mutually exclusive and sum to total: REGISTERED
        # unescalated / pending / approved + IN_PROGRESS + CLOSED.
        escalate_pending = self._count_complaints(
            owning_unit,
            CmBatch1ComplaintORM.status == "REGISTERED",
            CmBatch1ComplaintORM.intake_disposition == "ESCALATE_PENDING_APPROVAL",
        )
        # REGISTERED but not held in an escalation path — not "Baru" if
        # already ESCALATE_APPROVED (that is a different operational state).
        waiting_assignment = self._count_complaints(
            owning_unit,
            CmBatch1ComplaintORM.status == "REGISTERED",
            or_(
                CmBatch1ComplaintORM.intake_disposition.is_(None),
                CmBatch1ComplaintORM.intake_disposition.notin_(
                    (
                        "ESCALATE_PENDING_APPROVAL",
                        "ESCALATE_APPROVED",
                    )
                ),
            ),
        )
        escalate_approved = self._count_complaints(
            owning_unit,
            CmBatch1ComplaintORM.status == "REGISTERED",
            CmBatch1ComplaintORM.intake_disposition == "ESCALATE_APPROVED",
        )
        in_progress = self._count_complaints(
            owning_unit, CmBatch1ComplaintORM.status == "IN_PROGRESS"
        )
        return DashboardAggregateKpiResponse(
            total=total,
            open=open_count,
            closed=closed,
            escalatePending=escalate_pending,
            waitingAssignment=waiting_assignment,
            escalateApproved=escalate_approved,
            inProgress=in_progress,
        )

    def _count_complaints(
        self,
        owning_unit_id: str | None,
        *extra: Any,
    ) -> int:
        """``owning_unit_id is None`` = unrestricted; otherwise exact unit match."""
        stmt = select(func.count()).select_from(CmBatch1ComplaintORM)
        if owning_unit_id is not None:
            stmt = stmt.where(CmBatch1ComplaintORM.owning_unit_id == owning_unit_id)
        for clause in extra:
            stmt = stmt.where(clause)
        return int(self._session.scalar(stmt) or 0)

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
