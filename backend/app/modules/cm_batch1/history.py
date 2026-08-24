"""Intake history read model — chronological event log for one Complaint.

The ``description`` blob keeps at most one note per section label, so it can
never answer "what happened, in what order". This reads the append-only
timeline instead and maps each entry to a stable code the UI can label.

Display order is chronological with narrative adjustments:
- On branch-close intake, ``BRANCH_CLOSED`` slides past the following
  attachment cluster so the business outcome stays last in that burst.
- Same-burst create+auto-approve ranks REGISTERED → REQUESTED → APPROVED →
  CASE_* so a historical +1s REQUESTED stamp cannot appear after approval.
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

# Same-burst create+auto-approve (or +1s disposition stamp) can reorder
# REQUESTED after APPROVED/Case — cluster and rank within this window.
_BURST_GAP = timedelta(seconds=2)

# Lower = earlier in the complaint-page narrative within one burst.
_NARRATIVE_RANK: dict[str, int] = {
    "REGISTERED": 0,
    "ATTACHMENT_UPLOADED": 5,
    "ATTACHMENT_BOUND": 5,
    "ATTACHMENT_SUPERSEDED": 5,
    "ATTACHMENT_VOIDED": 5,
    "ATTACHMENT_TRANSFERRED": 5,
    "ESCALATION_REQUESTED": 10,
    "ESCALATION_APPROVED": 20,
    "ESCALATION_REJECTED": 20,
    "ESCALATION_CANCELLED": 20,
    "ESCALATION_RE_REQUESTED": 25,
    "CASE_CREATED": 30,
    "CASE_ESCALATED_TO_PUSAT": 40,
    "CASE_ESCALATION_TO_PUSAT_CANCELLED": 41,
    "CASE_ESCALATION_RETURNED": 42,
    "BRANCH_CLOSED": 90,
}

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
    "HqCompleted": "HQ_COMPLETED",
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
    "CaseCreated": "CASE_CREATED",
    "CaseWorkStarted": "CASE_WORK_STARTED",
    "CaseAssigned": "CASE_ASSIGNED",
    "CaseCancelled": "CASE_CANCELLED",
    "CaseStatusChanged": "CASE_STATUS_CHANGED",
    "CaseClosed": "CASE_CLOSED",
    "CaseResolved": "CASE_RESOLVED",
    "HandlingContinued": "HANDLING_CONTINUED",
    "HandlingTakenOver": "HANDLING_TAKEN_OVER",
    "CaseEscalatedToPusat": "CASE_ESCALATED_TO_PUSAT",
    "CaseEscalationToPusatCancelled": "CASE_ESCALATION_TO_PUSAT_CANCELLED",
    "CaseEscalationReturned": "CASE_ESCALATION_RETURNED",
}


def _meta_text(meta: dict[str, Any], key: str) -> str | None:
    raw = meta.get(key)
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


# Internal Case lifecycle noise — CaseCreated stays visible (one row per Case).
_HISTORY_HIDDEN_EVENT_TYPES = frozenset(
    {
        "CaseWorkStarted",
        "CaseHandlingUnitAccepted",
        "CaseOwnerAccepted",
        "CaseHandlingUnitRejected",
        "CaseOwnerRejected",
    }
)


def _case_number(entry: TimelineEntry) -> str:
    return str((entry.metadata or {}).get("caseNumber") or "").strip()


def omit_resolved_when_closed(entries: list[TimelineEntry]) -> list[TimelineEntry]:
    """Keep CaseClosed as the business outcome; drop CaseResolved for that Case."""
    closed = {
        _case_number(entry)
        for entry in entries
        if entry.event_type == "CaseClosed" and _case_number(entry)
    }
    if not closed:
        return entries
    return [
        entry
        for entry in entries
        if not (entry.event_type == "CaseResolved" and _case_number(entry) in closed)
    ]


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


def _slide_branch_closed_after_attachments(
    entries: list[TimelineEntry],
    *,
    follow_window: timedelta,
) -> list[TimelineEntry]:
    """Create+close writes disposition before staging binds finish."""
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


def _reorder_same_burst_by_narrative(
    entries: list[TimelineEntry],
    *,
    burst_gap: timedelta = _BURST_GAP,
) -> list[TimelineEntry]:
    """Stable-rank codes inside a same-second intake burst.

    Auto-approve stamps APPROVE at wall-clock while REQUESTED was historically
    written at created_at+1s — so raw chrono shows disetujui before diajukan.
    """
    if len(entries) < 2:
        return list(entries)

    def rank(entry: TimelineEntry) -> int:
        return _NARRATIVE_RANK.get(event_code(entry), 50)

    out: list[TimelineEntry] = []
    i = 0
    while i < len(entries):
        j = i + 1
        while j < len(entries):
            gap = entries[j].created_at - entries[j - 1].created_at
            if gap < timedelta(0) or gap > burst_gap:
                break
            j += 1
        cluster = entries[i:j]
        if len(cluster) > 1:
            # Preserve original index for equal ranks / unknown codes.
            cluster = [
                entry
                for _, entry in sorted(
                    enumerate(cluster),
                    key=lambda pair: (rank(pair[1]), pair[0]),
                )
            ]
        out.extend(cluster)
        i = j
    return out


def apply_narrative_intake_order(
    entries: list[TimelineEntry],
    *,
    follow_window: timedelta = _ATTACHMENT_FOLLOW_WINDOW,
) -> list[TimelineEntry]:
    """Chronological list with narrative fixes for same-burst intake writes.

    1. BRANCH_CLOSED after same-burst ATTACHMENT_* rows.
    2. Within a short burst: REGISTERED → REQUESTED → APPROVED → CASE_*.
    """
    after_close = _slide_branch_closed_after_attachments(
        entries, follow_window=follow_window
    )
    return _reorder_same_burst_by_narrative(after_close)


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
        entries = [
            entry
            for entry in entries
            if entry.event_type not in _HISTORY_HIDDEN_EVENT_TYPES
        ]
        entries = omit_resolved_when_closed(entries)
        names = self._actor_names(entries)

        def to_item(entry: TimelineEntry) -> IntakeHistoryEntry:
            meta = dict(entry.metadata or {})
            return IntakeHistoryEntry(
                entryId=str(entry.id),
                eventCode=event_code(entry),
                eventType=entry.event_type,
                occurredAt=entry.created_at,
                actorId=entry.actor_id,
                actorName=self._display_actor_name(entry, names),
                priority=(meta.get("priority") or None),
                note=(meta.get("note") or None),
                caseNumber=(meta.get("caseNumber") or None),
                intakeAction=(meta.get("intakeAction") or None),
                arrivalDate=_meta_text(meta, "arrivalDate"),
                arrivalTime=_meta_text(meta, "arrivalTime"),
            )

        return [to_item(entry) for entry in entries]

    def _usable_person_name(self, raw: str | None) -> str | None:
        value = (raw or "").strip()
        if not value:
            return None
        try:
            uuid.UUID(value)
        except (TypeError, ValueError):
            return value
        return None

    def _display_actor_name(
        self, entry: TimelineEntry, names: dict[str, str]
    ) -> str | None:
        stored = self._usable_person_name(entry.actor_name)
        if stored:
            return stored
        if entry.actor_id:
            looked = self._usable_person_name(names.get(entry.actor_id))
            if looked:
                return looked
        return None

    def _actor_names(self, entries: list[TimelineEntry]) -> dict[str, str]:
        wanted: set[str] = set()
        for entry in entries:
            if not entry.actor_id:
                continue
            if self._usable_person_name(entry.actor_name) is None:
                wanted.add(entry.actor_id)
        if not wanted:
            return {}
        try:
            return self._directory.display_names(wanted)
        except Exception:
            return {}
