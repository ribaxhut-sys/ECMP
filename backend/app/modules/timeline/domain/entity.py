"""CAPABILITY-010 TimelineEntry domain entity (immutable after create)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping

from app.core.errors import ValidationAppError
from app.modules.timeline.domain.enums import ActorType, AggregateType
from app.core.user_messages import m


@dataclass(frozen=True, slots=True)
class TimelineEntry:
    """Append-only activity history record.

    Never mutate after construction — persist once, read forever.
    """

    id: uuid.UUID
    aggregate_type: str
    aggregate_id: uuid.UUID
    event_type: str
    title: str
    description: str | None
    actor_type: str | None
    actor_id: str | None
    actor_name: str | None
    metadata: Mapping[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        *,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        event_type: str,
        title: str,
        description: str | None = None,
        actor_type: str | None = ActorType.SYSTEM.value,
        actor_id: str | None = None,
        actor_name: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        entry_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ) -> TimelineEntry:
        try:
            AggregateType(aggregate_type)
        except ValueError as exc:
            raise ValidationAppError(
                f"tipe agregat tidak didukung: {aggregate_type}",
                details={
                    "aggregateType": aggregate_type,
                    "allowed": [a.value for a in AggregateType],
                },
            ) from exc

        cleaned_type = (event_type or "").strip()
        if not cleaned_type:
            raise ValidationAppError(
                m("config.event_type_required"),
                details={"eventType": event_type},
            )
        cleaned_title = (title or "").strip()
        if not cleaned_title:
            raise ValidationAppError(
                m("config.title_required"),
                details={"title": title},
            )
        if actor_type is not None:
            try:
                ActorType(actor_type)
            except ValueError as exc:
                raise ValidationAppError(
                    f"tipe aktor tidak didukung: {actor_type}",
                    details={
                        "actorType": actor_type,
                        "allowed": [a.value for a in ActorType],
                    },
                ) from exc

        created = created_at or datetime.now(UTC)
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)

        return cls(
            id=entry_id or uuid.uuid4(),
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=cleaned_type,
            title=cleaned_title,
            description=(description.strip() if description else None) or None,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            metadata=dict(metadata or {}),
            created_at=created,
        )
