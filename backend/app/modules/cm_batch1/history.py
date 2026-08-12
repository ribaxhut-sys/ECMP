"""Intake history read model — chronological event log for one Complaint.

The ``description`` blob keeps at most one note per section label, so it can
never answer "what happened, in what order". This reads the append-only
timeline instead and maps each entry to a stable code the UI can label.

Display order is chronological with one narrative adjustment: on branch-close
intake, ``BRANCH_CLOSED`` is written at create time while attachments bind in a
later request — slide close past the following attachment cluster so the
business outcome stays last in that burst (Mode A Riwayat intake).
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

from app.integrations.directory import NullUserDirectory, UserDirectory
from app.modules.cm_batch1.schemas import IntakeHistoryEntry
from app.modules.timeline.domain.entity import TimelineEntry

AGGREGATE_TYPE = "Complaint"

# Attachments bound shortly after BRANCH_CLOSED on create still belong to the
# same intake action — keep them before the close row in the narrative.
_ATTACHMENT_FOLLOW_WINDOW = timedelta(minutes=2)

_ATTACHMENT_EVENT_TYPES = frozenset(
    {
        "AttachmentUploaded",
        "AttachmentBound",
        "AttachmentSuperseded",
        "AttachmentVoided",
        "AttachmentTransferred",
    }
)

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
    "HqReturned": "HQ_RETURNED",
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


def _is_attachment_event(entry: TimelineEntry) -> bool:
    if entry.event_type in _ATTACHMENT_EVENT_TYPES:
        return True
    return event_code(entry).startswith("ATTACHMENT_")


def apply_narrative_intake_order(
    entries: list[TimelineEntry],
    *,
    follow_window: timedelta = _ATTACHMENT_FOLLOW_WINDOW,
) -> list[TimelineEntry]:
    """Chronological list with BRANCH_CLOSED after same-burst ATTACHMENT_* rows.

    Create+close writes disposition before staging binds finish, so raw chrono
    shows Ditutup di tengah. Slide each BRANCH_CLOSED past the contiguous
    attachment cluster that follows within ``follow_window``.
    """
    result = list(entries)
    i = 0
    while i < len(result):
        if event_code(result[i]) != "BRANCH_CLOSED":
            i += 1
            continue
        closed = result[i]
        closed_at = closed.created_at
        j = i + 1
        while j < len(result):
            nxt = result[j]
            if not _is_attachment_event(nxt):
                break
            delta = nxt.created_at - closed_at
            if delta < timedelta(0) or delta > follow_window:
                break
            j += 1
        if j > i + 1:
            item = result.pop(i)
            # After pop, former index j-1 is the last attachment.
            result.insert(j - 1, item)
            i = j
        else:
            i += 1
    return result


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
        entries = apply_narrative_intake_order(entries)
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
