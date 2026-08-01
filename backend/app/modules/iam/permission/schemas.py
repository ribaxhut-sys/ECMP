"""Permission Management API contracts (camelCase) — TASK-034."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.user_messages import m


class PermissionCreateRequest(BaseModel):
    """API-344 create permission."""

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(min_length=3, max_length=150)
    name: str = Field(min_length=1, max_length=200)
    module: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True, alias="isActive")

    @field_validator("code", "name", "module")
    @classmethod
    def strip_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.value_required"))
        return cleaned

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class PermissionUpdateRequest(BaseModel):
    """API-346 update permission (partial). Code and module are immutable."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None)
    is_active: bool | None = Field(default=None, alias="isActive")

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.value_required"))
        return cleaned

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def at_least_one_field(self) -> PermissionUpdateRequest:
        if self.name is None and self.description is None and self.is_active is None:
            raise ValueError(m("config.at_least_one_field"))
        return self


class PermissionResponse(BaseModel):
    """Permission payload (API-343–347)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    module: str
    description: str | None = None
    is_system: bool = Field(alias="isSystem")
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
