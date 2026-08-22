"""Case-scoped Timeline projection (API-537 / BR-017 / UC-CAP02-07).

Reads the parent Complaint Timeline stream and keeps events that belong
to one Case. Complaint-scoped HQ-path events (accept / schedule / return)
are included even without caseId — they bind every open Case of the parent.
Does not hide operational Case events that API-517 omits from the intake
narrative.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.integrations.directory import NullUserDirectory, UserDirectory
from app.modules.cm_batch1.history import event_code
from app.modules.cm_case.api.schemas import CaseHistoryEntry
from app.modules.cm_case.application.dto import CaseDTO
from app.modules.timeline.domain.entity import TimelineEntry

AGGREGATE_TYPE = "Complaint"
_PAGE_SIZE = 100
_MAX_PAGES = 10

_EXTRA_EVENT_CODES = {
    "CaseHandlingUnitAccepted": "CASE_HANDLING_UNIT_ACCEPTED",
    "CaseOwnerAccepted": "CASE_OWNER_ACCEPTED",
    "CaseHandlingUnitRejected": "CASE_HANDLING_UNIT_REJECTED",
    "CaseOwnerRejected": "CASE_OWNER_REJECTED",
    "ResolutionUpdated": "RESOLUTION_UPDATED",
    "CaseEscalatedToPusat": "CASE_ESCALATED_TO_PUSAT",
}

# Complaint-scoped HQ path — no caseId on the timeline row, but Penanganan
# groups every open Case of this parent under Pusat once these fire.
_PARENT_HQ_EVENT_TYPES = frozenset(
    {
        "HqAccepted",
        "HqReturned",
        "HqArrivalScheduled",
    }
)


def _meta_text(meta: dict[str, Any], key: str) -> str | None:
    raw = meta.get(key)
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _ids_equal(left: str | None, right: str | None) -> bool:
    a = (left or "").strip()
    b = (right or "").strip()
    if not a or not b:
        return False
    if a == b:
        return True
    try:
        return uuid.UUID(a) == uuid.UUID(b)
    except ValueError:
        return a.casefold() == b.casefold()


def belongs_to_case(
    entry: TimelineEntry,
    *,
    case_id: str,
    case_number: str,
) -> bool:
    """True when the row is tagged as this Case, or is a parent HQ-path event.

    Sibling Case rows and generic intake (REGISTERED, BRANCH_CLOSED, …) stay out.
    """
    meta = dict(entry.metadata or {})
    entry_case_id = _meta_text(meta, "caseId")
    if entry_case_id:
        return _ids_equal(entry_case_id, case_id)
    entry_case_number = _meta_text(meta, "caseNumber")
    wanted_number = (case_number or "").strip()
    if entry_case_number and wanted_number:
        return entry_case_number == wanted_number
    return entry.event_type in _PARENT_HQ_EVENT_TYPES


def case_event_code(entry: TimelineEntry) -> str:
    extra = _EXTRA_EVENT_CODES.get(entry.event_type)
    if extra:
        return extra
    return event_code(entry)


class CaseHistoryService:
    """Read-only projection over Complaint Timeline, filtered to one Case."""

    def __init__(
        self,
        timeline_repository: Any,
        *,
        user_directory: UserDirectory | None = None,
    ) -> None:
        self._timeline = timeline_repository
        self._directory = user_directory or NullUserDirectory()

    def list_for_case(self, case: CaseDTO) -> list[CaseHistoryEntry]:
        try:
            aggregate_id = uuid.UUID(str(case.complaint_id))
        except (TypeError, ValueError):
            return []

        entries: list[TimelineEntry] = []
        page = 1
        total = 0
        while page <= _MAX_PAGES:
            chunk, total = self._timeline.list_by_aggregate(
                aggregate_type=AGGREGATE_TYPE,
                aggregate_id=aggregate_id,
                page=page,
                page_size=_PAGE_SIZE,
            )
            entries.extend(chunk)
            if len(entries) >= total or not chunk:
                break
            page += 1

        scoped = [
            entry
            for entry in entries
            if belongs_to_case(
                entry, case_id=case.case_id, case_number=case.case_number
            )
        ]
        names = self._actor_names(scoped)

        return [self._to_item(entry, names) for entry in scoped]

    def _to_item(
        self, entry: TimelineEntry, names: dict[str, str]
    ) -> CaseHistoryEntry:
        meta = dict(entry.metadata or {})
        return CaseHistoryEntry(
            entryId=str(entry.id),
            eventCode=case_event_code(entry),
            eventType=entry.event_type,
            occurredAt=entry.created_at,
            actorId=entry.actor_id,
            actorName=self._display_actor_name(entry, names),
            actorUnitId=_meta_text(meta, "actorUnitId"),
            note=_meta_text(meta, "note"),
            priority=_meta_text(meta, "priority"),
            caseNumber=_meta_text(meta, "caseNumber"),
            caseStatus=_meta_text(meta, "caseStatus"),
            arrivalDate=_meta_text(meta, "arrivalDate"),
            arrivalTime=_meta_text(meta, "arrivalTime"),
        )

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
