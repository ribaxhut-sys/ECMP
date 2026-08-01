"""Role-Permission Matrix API contracts (camelCase) — TASK-035."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.user_messages import m


class RolePermissionsReplaceRequest(BaseModel):
    """API-349 replace role permissions (full set)."""

    model_config = ConfigDict(populate_by_name=True)

    permission_ids: list[uuid.UUID] = Field(default_factory=list, alias="permissionIds")

    @field_validator("permission_ids")
    @classmethod
    def no_duplicates(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(value) != len(set(value)):
            raise ValueError(m("config.permission_ids_no_duplicates"))
        return value
