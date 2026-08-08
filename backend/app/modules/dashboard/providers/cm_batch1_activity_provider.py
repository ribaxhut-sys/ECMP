"""Dashboard 'Recent Activity' sourced from the CM Batch 1 Aggregate.

UM-BUG-008 — dashboard/service.py's overview() previously composed recent
activity from the legacy ``complaint_timelines`` + ``complaints`` tables
(app.modules.timelines / app.modules.complaints), which the running system
no longer writes to (DEC-020 coexistence: complaints are now created via
CM Batch 1). Real history lives in ``timeline_entries``
(app.modules.timeline, CAPABILITY-010), written by CmBatch1HistoryService.
This provider reads from there instead.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.directory import LocalUserDirectory
from app.models import User
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.dashboard.schemas import DashboardRecentActivityItem
from app.modules.timeline.repository import TimelineRepository

_AGGREGATE_TYPE = "Complaint"  # matches app/modules/cm_batch1/history.py
_SYSTEM_ACTOR = "SYSTEM"

# CM Batch 1 event_type (+ metadata.decision for IntakeEscalationDecided) ->
# legacy-style dotted eventType the frontend's activityLabels.ts already
# resolves to a label/badge. Keeps the UI vocabulary stable across the
# SoT switch — only the read source changed.
_EVENT_TYPE_MAP: dict[str, str] = {
    "ComplaintRegistered": "complaint.created",
}
_DECISION_EVENT_TYPE_MAP: dict[str, str] = {
    "APPROVE": "complaint.escalation_approved",
    "REJECT": "complaint.escalation_rejected",
    "RE_ESCALATE": "complaint.escalation_requested",
    "CANCEL": "complaint.updated",
}


def _map_event_type(event_type: str, metadata: dict) -> str:
    if event_type == "IntakeEscalationDecided":
        decision = str(metadata.get("decision") or "").upper()
        return _DECISION_EVENT_TYPE_MAP.get(decision, "complaint.updated")
    return _EVENT_TYPE_MAP.get(event_type, "complaint.updated")


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
            aggregate_type=_AGGREGATE_TYPE, limit=limit, aggregate_ids=aggregate_ids
        )
        if not entries:
            return []

        actor_ids = {e.actor_id for e in entries if e.actor_id}
        actor_names = self._directory.display_names(actor_ids) if actor_ids else {}

        items: list[DashboardRecentActivityItem] = []
        for entry in entries:
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
            items.append(
                DashboardRecentActivityItem(
                    eventType=_map_event_type(entry.event_type, entry.metadata),
                    complaintNumber=complaint_number,
                    timestamp=entry.created_at,
                    actor=actor_name,
                )
            )
        return items

    def _complaint_ids_for_branch(self, branch_id: uuid.UUID) -> set[uuid.UUID]:
        """Complaint ids created by a member of ``branch_id``.

        cm_batch1_complaints has no branch column (recordingUnitId only lives
        in the outbox JSON payload) — branch is derived from the creating
        officer's own membership, same convention as elsewhere in the module.
        created_by is a plain string (not a UUID FK), so this stays a Python
        IN-list join rather than a SQL cast, matching _agent_labels_for's
        directory-lookup pattern.
        """
        member_ids = self._session.scalars(
            select(User.id).where(
                User.branch_id == branch_id, User.deleted_at.is_(None)
            )
        ).all()
        if not member_ids:
            return set()
        created_by_keys = {str(uid) for uid in member_ids}
        complaint_ids = self._session.scalars(
            select(CmBatch1ComplaintORM.id).where(
                CmBatch1ComplaintORM.created_by.in_(created_by_keys)
            )
        ).all()
        return set(complaint_ids)
