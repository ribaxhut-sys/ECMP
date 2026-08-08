"""Intake history read model — chronological event log for one Complaint.

The ``description`` blob keeps at most one note per section label, so it can
never answer "what happened, in what order". This reads the append-only
timeline instead and maps each entry to a stable code the UI can label.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.integrations.directory import NullUserDirectory, UserDirectory
from app.modules.cm_batch1.schemas import IntakeHistoryEntry
from app.modules.timeline.domain.entity import TimelineEntry

AGGREGATE_TYPE = "Complaint"

_ESCALATION_DECISION_CODES = {
    "APPROVE": "ESCALATION_APPROVED",
    "REJECT": "ESCALATION_REJECTED",
    "CANCEL": "ESCALATION_CANCELLED",
    "RE_ESCALATE": "ESCALATION_RE_REQUESTED",
}

_DISPOSITION_CODES = {
    "BRANCH_CLOSED": "BRANCH_CLOSED",
    "ESCALATE_PENDING_APPROVAL": "ESCALATION_REQUESTED",
}

_EVENT_TYPE_CODES = {
    "ComplaintRegistered": "REGISTERED",
    "HqAccepted": "HQ_ACCEPTED",
    "HqArrivalScheduled": "HQ_ARRIVAL_SCHEDULED",
    "AttachmentUploaded": "ATTACHMENT_UPLOADED",
    "AttachmentBound": "ATTACHMENT_BOUND",
    "AttachmentSuperseded": "ATTACHMENT_SUPERSEDED",
    "AttachmentVoided": "ATTACHMENT_VOIDED",
    "AttachmentTransferred": "ATTACHMENT_TRANSFERRED",
    "DuplicateFound": "DUPLICATE_FOUND",
    "DuplicateOverridden": "DUPLICATE_OVERRIDDEN",
    "DuplicateLinked": "DUPLICATE_LINKED",
    "DuplicateRedirected": "DUPLICATE_REDIRECTED",
    "DuplicateRecommended": "DUPLICATE_RECOMMENDED",
    "DuplicateBlocked": "DUPLICATE_BLOCKED",
}


def event_code(entry: TimelineEntry) -> str:
    """Stable UI code — never the raw English title, which is not translatable."""
    meta: dict[str, Any] = dict(entry.metadata or {})
    if entry.event_type == "IntakeEscalationDecided":
        decision = str(meta.get("decision") or "").strip().upper()
        return _ESCALATION_DECISION_CODES.get(decision, "ESCALATION_DECIDED")
    if entry.event_type == "IntakeDispositionRecorded":
        disposition = str(meta.get("intakeDisposition") or "").strip().upper()
        return _DISPOSITION_CODES.get(disposition, "INTAKE_RECORDED")
    return _EVENT_TYPE_CODES.get(entry.event_type, "OTHER")


class CmBatch1HistoryService:
    """Read-only projection over the timeline; never writes."""

    def __init__(
        self,
        timeline_repository: Any,
        *,
        user_directory: UserDirectory | None = None,
    ) -> None:
        self._timeline = timeline_repository
        self._directory = user_directory or NullUserDirectory()

    def list_history(
        self, complaint_id: str, *, page_size: int = 100
    ) -> list[IntakeHistoryEntry]:
        try:
            aggregate_id = uuid.UUID(str(complaint_id))
        except (TypeError, ValueError):
            return []
        entries, _ = self._timeline.list_by_aggregate(
            aggregate_type=AGGREGATE_TYPE,
            aggregate_id=aggregate_id,
            page=1,
            page_size=page_size,
        )
        names = self._actor_names(entries)
        return [
            IntakeHistoryEntry(
                entryId=str(entry.id),
                eventCode=event_code(entry),
                eventType=entry.event_type,
                occurredAt=entry.created_at,
                actorId=entry.actor_id,
                actorName=(
                    entry.actor_name
                    or (names.get(entry.actor_id) if entry.actor_id else None)
                ),
                priority=(dict(entry.metadata or {}).get("priority") or None),
                note=(dict(entry.metadata or {}).get("note") or None),
            )
            for entry in entries
        ]

    def _actor_names(self, entries: list[TimelineEntry]) -> dict[str, str]:
        wanted = {e.actor_id for e in entries if e.actor_id and not e.actor_name}
        if not wanted:
            return {}
        try:
            return self._directory.display_names(wanted)
        except Exception:
            return {}
