"""User-Role Assignment API contracts (camelCase) — TASK-036."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRolesReplaceRequest(BaseModel):
    """API-352 replace user roles (full set)."""

    model_config = ConfigDict(populate_by_name=True)

    role_ids: list[uuid.UUID] = Field(default_factory=list, alias="roleIds")

    @field_validator("role_ids")
    @classmethod
    def no_duplicates(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(value) != len(set(value)):
            raise ValueError("roleIds must not contain duplicates")
        return value
