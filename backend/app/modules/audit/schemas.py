"""Audit Log API contracts (camelCase) — TASK-031."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

AuditActionLiteral = Literal[
    "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT", "IMPORT"
]


class AuditLogResponse(BaseModel):
    """API-336 / API-337 audit log payload."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    event_type: str = Field(alias="eventType")
    entity_type: str = Field(alias="entityType")
    entity_id: uuid.UUID | None = Field(default=None, alias="entityId")
    action: AuditActionLiteral
    actor_id: uuid.UUID | None = Field(default=None, alias="actorId")
    actor_name: str | None = Field(default=None, alias="actorName")
    ip_address: str | None = Field(default=None, alias="ipAddress")
    user_agent: str | None = Field(default=None, alias="userAgent")
    old_values: dict[str, Any] | None = Field(default=None, alias="oldValues")
    new_values: dict[str, Any] | None = Field(default=None, alias="newValues")
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="metadata_json",
        serialization_alias="metadata",
    )
    created_at: datetime = Field(alias="createdAt")
