"""Data Scope API contracts (camelCase) — TASK-037."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.iam.data_scope.models import (
    ScopeType,
    scope_forbids_value,
    scope_requires_value,
)


def _normalize_scope_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DataScopeItem(BaseModel):
    """One scope entry in a replace payload."""

    model_config = ConfigDict(populate_by_name=True)

    scope_type: ScopeType = Field(alias="scopeType")
    scope_value: str | None = Field(default=None, max_length=255, alias="scopeValue")

    @field_validator("scope_value")
    @classmethod
    def strip_value(cls, value: str | None) -> str | None:
        return _normalize_scope_value(value)

    @model_validator(mode="after")
    def validate_type_value_combo(self) -> DataScopeItem:
        if scope_forbids_value(self.scope_type) and self.scope_value is not None:
            raise ValueError(
                f"{self.scope_type} must not have scopeValue"
            )
        if scope_requires_value(self.scope_type) and self.scope_value is None:
            raise ValueError(
                f"{self.scope_type} requires a non-empty scopeValue"
            )
        return self


class DataScopeReplaceRequest(BaseModel):
    """API-355 replace role data scopes (full set)."""

    model_config = ConfigDict(populate_by_name=True)

    scopes: list[DataScopeItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def no_duplicates(self) -> DataScopeReplaceRequest:
        keys = [(item.scope_type, item.scope_value) for item in self.scopes]
        if len(keys) != len(set(keys)):
            raise ValueError("scopes must not contain duplicates")
        return self


class DataScopeCreateRequest(BaseModel):
    """Service-level create for a single scope row."""

    model_config = ConfigDict(populate_by_name=True)

    role_id: uuid.UUID = Field(alias="roleId")
    scope_type: ScopeType = Field(alias="scopeType")
    scope_value: str | None = Field(default=None, max_length=255, alias="scopeValue")

    @field_validator("scope_value")
    @classmethod
    def strip_value(cls, value: str | None) -> str | None:
        return _normalize_scope_value(value)

    @model_validator(mode="after")
    def validate_type_value_combo(self) -> DataScopeCreateRequest:
        if scope_forbids_value(self.scope_type) and self.scope_value is not None:
            raise ValueError(f"{self.scope_type} must not have scopeValue")
        if scope_requires_value(self.scope_type) and self.scope_value is None:
            raise ValueError(f"{self.scope_type} requires a non-empty scopeValue")
        return self


class DataScopeUpdateRequest(BaseModel):
    """Service-level update (partial)."""

    model_config = ConfigDict(populate_by_name=True)

    scope_type: ScopeType | None = Field(default=None, alias="scopeType")
    scope_value: str | None = Field(default=None, max_length=255, alias="scopeValue")

    @field_validator("scope_value")
    @classmethod
    def strip_value(cls, value: str | None) -> str | None:
        return _normalize_scope_value(value)

    @model_validator(mode="after")
    def at_least_one_field(self) -> DataScopeUpdateRequest:
        if self.scope_type is None and "scope_value" not in self.model_fields_set:
            raise ValueError("at least one field is required")
        return self


class DataScopeResponse(BaseModel):
    """Data scope payload (API-354–355)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    role_id: uuid.UUID = Field(alias="roleId")
    scope_type: str = Field(alias="scopeType")
    scope_value: str | None = Field(default=None, alias="scopeValue")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
