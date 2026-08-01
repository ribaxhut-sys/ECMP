"""CAPABILITY-010 Timeline application service (append + read)."""

from __future__ import annotations

import uuid
from typing import Any

from app.core.errors import NotFoundError
from app.core.schemas import PageMeta
from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.domain.enums import ActorType, AggregateType
from app.modules.timeline.repository import TimelineRepository
from app.modules.timeline.schemas import (
    TimelineEntryCreateRequest,
    TimelineEntryResponse,
)
from app.core.user_messages import m


def _to_response(entry: TimelineEntry) -> TimelineEntryResponse:
    return TimelineEntryResponse(
        id=entry.id,
        aggregateType=entry.aggregate_type,  # type: ignore[arg-type]
        aggregateId=entry.aggregate_id,
        eventType=entry.event_type,
        title=entry.title,
        description=entry.description,
        actorType=entry.actor_type,  # type: ignore[arg-type]
        actorId=entry.actor_id,
        actorName=entry.actor_name,
        metadata=dict(entry.metadata) if entry.metadata else None,
        createdAt=entry.created_at,
    )


class ActivityTimelineService:
    """Reusable activity history — no update / delete."""

    def __init__(self, repository: TimelineRepository) -> None:
        self._repo = repository

    def create(self, payload: TimelineEntryCreateRequest) -> TimelineEntryResponse:
        entry = TimelineEntry.create(
            aggregate_type=payload.aggregate_type,
            aggregate_id=payload.aggregate_id,
            event_type=payload.event_type,
            title=payload.title,
            description=payload.description,
            actor_type=payload.actor_type,
            actor_id=payload.actor_id,
            actor_name=payload.actor_name,
            metadata=payload.metadata,
        )
        saved = self._repo.add(entry)
        self._repo.commit()
        return _to_response(saved)

    def record(
        self,
        *,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        event_type: str,
        title: str,
        description: str | None = None,
        actor_type: str | None = ActorType.SYSTEM.value,
        actor_id: str | None = None,
        actor_name: str | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> TimelineEntryResponse:
        """Internal append used by event handlers."""
        entry = TimelineEntry.create(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            title=title,
            description=description,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            metadata=metadata,
        )
        saved = self._repo.add(entry)
        if commit:
            self._repo.commit()
        return _to_response(saved)

    def get(self, entry_id: uuid.UUID) -> TimelineEntryResponse:
        entry = self._repo.get(entry_id)
        if entry is None:
            raise NotFoundError(m("timeline.not_found"))
        return _to_response(entry)

    def list(
        self,
        *,
        aggregate_type: str | None = None,
        aggregate_id: uuid.UUID | None = None,
        event_type: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[TimelineEntryResponse], PageMeta]:
        rows, total = self._repo.list(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            page=page,
            page_size=page_size,
        )
        return (
            [_to_response(r) for r in rows],
            PageMeta(page=page, pageSize=page_size, totalItems=total),
        )

    def list_for_complaint(
        self,
        complaint_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[TimelineEntryResponse], PageMeta]:
        return self.list(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=complaint_id,
            page=page,
            page_size=page_size,
        )
