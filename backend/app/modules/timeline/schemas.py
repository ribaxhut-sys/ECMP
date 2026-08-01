"""CAPABILITY-010 Timeline API schemas (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.user_messages import m

AggregateTypeLiteral = Literal["Complaint", "Queue", "Notification"]
ActorTypeLiteral = Literal["USER", "SYSTEM", "SERVICE"]


class TimelineEntryCreateRequest(BaseModel):
    """POST /timeline — internal/testing create (normal flow uses events)."""

    model_config = ConfigDict(populate_by_name=True)

    aggregate_type: AggregateTypeLiteral = Field(alias="aggregateType")
    aggregate_id: uuid.UUID = Field(alias="aggregateId")
    event_type: str = Field(alias="eventType", min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    actor_type: ActorTypeLiteral | None = Field(default="SYSTEM", alias="actorType")
    actor_id: str | None = Field(default=None, alias="actorId", max_length=100)
    actor_name: str | None = Field(default=None, alias="actorName", max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_type", "title")
    @classmethod
    def strip_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.value_required"))
        return cleaned


class TimelineEntryResponse(BaseModel):
    """CAPABILITY-010 timeline entry (immutable history)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    aggregate_type: AggregateTypeLiteral = Field(alias="aggregateType")
    aggregate_id: uuid.UUID = Field(alias="aggregateId")
    event_type: str = Field(alias="eventType")
    title: str
    description: str | None = None
    actor_type: ActorTypeLiteral | None = Field(default=None, alias="actorType")
    actor_id: str | None = Field(default=None, alias="actorId")
    actor_name: str | None = Field(default=None, alias="actorName")
    metadata: dict[str, Any] | None = None
    created_at: datetime = Field(alias="createdAt")
