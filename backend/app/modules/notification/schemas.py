"""Notification Foundation API contracts (camelCase) — TASK-030."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.user_messages import m

NotificationChannelLiteral = Literal[
    "EMAIL", "WHATSAPP", "SMS", "PUSH", "WEBHOOK"
]
NotificationStatusLiteral = Literal[
    "PENDING", "PROCESSING", "SENT", "FAILED", "CANCELLED"
]


class NotificationTemplateCreateRequest(BaseModel):
    """API-328 create notification template."""

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    channel: NotificationChannelLiteral
    subject: str | None = Field(default=None, max_length=255)
    content: str = Field(min_length=1)
    is_active: bool = Field(default=True, alias="isActive")

    @field_validator("code", "name", "content")
    @classmethod
    def strip_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.value_required"))
        return cleaned

    @field_validator("subject")
    @classmethod
    def strip_subject(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class NotificationTemplateUpdateRequest(BaseModel):
    """API-330 update notification template (partial)."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    channel: NotificationChannelLiteral | None = None
    subject: str | None = Field(default=None, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    is_active: bool | None = Field(default=None, alias="isActive")

    @field_validator("name", "content")
    @classmethod
    def strip_optional_required(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.value_required"))
        return cleaned

    @field_validator("subject")
    @classmethod
    def strip_subject(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class NotificationTemplateResponse(BaseModel):
    """Notification template payload (API-327–331)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    channel: NotificationChannelLiteral
    subject: str | None = None
    content: str
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class NotificationCreateRequest(BaseModel):
    """API-332 enqueue a notification (PENDING only — no send)."""

    model_config = ConfigDict(populate_by_name=True)

    template_code: str = Field(alias="templateCode", min_length=1, max_length=100)
    recipient: str = Field(min_length=1, max_length=255)
    variables: dict[str, Any] = Field(default_factory=dict)
    scheduled_at: datetime | None = Field(default=None, alias="scheduledAt")

    @field_validator("template_code", "recipient")
    @classmethod
    def strip_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.value_required"))
        return cleaned


class NotificationQueueResponse(BaseModel):
    """Notification row (API-332–335, API-356–357 / CAPABILITY-009)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    template_code: str | None = Field(default=None, alias="templateCode")
    notification_type: str | None = Field(default=None, alias="type")
    channel: NotificationChannelLiteral | None = None
    recipient: str | None = None
    subject: str | None = None
    message: str | None = None
    payload: dict[str, Any] | None = None
    status: NotificationStatusLiteral
    retry_count: int = Field(alias="retryCount")
    scheduled_at: datetime | None = Field(default=None, alias="scheduledAt")
    sent_at: datetime | None = Field(default=None, alias="sentAt")
    failed_at: datetime | None = Field(default=None, alias="failedAt")
    last_error: str | None = Field(default=None, alias="lastError")
    created_at: datetime = Field(alias="createdAt")
