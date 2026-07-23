"""Timeline application service (read-only, no FastAPI imports)."""

from __future__ import annotations

import uuid

from app.core.errors import NotFoundError
from app.models import ComplaintTimeline
from app.modules.timelines.repository import TimelineRepository
from app.modules.timelines.schemas import TimelineEntryResponse


def _to_response(row: ComplaintTimeline) -> TimelineEntryResponse:
    return TimelineEntryResponse(
        id=row.id,
        complaintId=row.complaint_id,
        actorUserId=row.actor_user_id,
        eventType=row.event_type,
        eventAt=row.event_at,
        fromStatus=row.from_status,
        toStatus=row.to_status,
        summary=row.summary,
        metadata=row.metadata_json,
        createdAt=row.created_at,
    )


class TimelineService:
    def __init__(self, repository: TimelineRepository) -> None:
        self._repo = repository

    def list_timeline(self, complaint_id: uuid.UUID) -> list[TimelineEntryResponse]:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        rows = self._repo.list_by_complaint(complaint_id)
        return [_to_response(row) for row in rows]
