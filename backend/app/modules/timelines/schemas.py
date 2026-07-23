"""Timeline API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import ComplaintStatus, TimelineEvent


class TimelineEntryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    complaint_id: uuid.UUID = Field(alias="complaintId")
    actor_user_id: uuid.UUID | None = Field(default=None, alias="actorUserId")
    actor_name: str | None = Field(default=None, alias="actorName")
    event_type: TimelineEvent = Field(alias="eventType")
    event_at: datetime = Field(alias="eventAt")
    from_status: ComplaintStatus | None = Field(default=None, alias="fromStatus")
    to_status: ComplaintStatus | None = Field(default=None, alias="toStatus")
    summary: str
    metadata: dict[str, Any] | None = None
    created_at: datetime = Field(alias="createdAt")

    @field_validator("event_type", mode="before")
    @classmethod
    def coerce_event_type(cls, value: object) -> object:
        if isinstance(value, TimelineEvent):
            return value
        if isinstance(value, str):
            return TimelineEvent(value)
        return value

    @field_validator("from_status", "to_status", mode="before")
    @classmethod
    def coerce_status(cls, value: object) -> object:
        if value is None or isinstance(value, ComplaintStatus):
            return value
        if isinstance(value, str):
            return ComplaintStatus(value)
        return value
