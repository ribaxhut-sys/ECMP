"""User API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(min_length=3, max_length=64)
    email: str = Field(min_length=3, max_length=320)
    full_name: str = Field(alias="fullName", min_length=1, max_length=200)
    password: str = Field(min_length=8, max_length=72)
    role_id: uuid.UUID = Field(alias="roleId")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    is_active: bool = Field(default=True, alias="isActive")

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not _EMAIL_RE.match(cleaned):
            raise ValueError("invalid email format")
        return cleaned

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("must not have leading or trailing whitespace")
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str | None = Field(default=None, min_length=3, max_length=64)
    email: str | None = Field(default=None, min_length=3, max_length=320)
    full_name: str | None = Field(default=None, alias="fullName", min_length=1, max_length=200)
    password: str | None = Field(default=None, min_length=8, max_length=72)
    role_id: uuid.UUID | None = Field(default=None, alias="roleId")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        if not _EMAIL_RE.match(cleaned):
            raise ValueError("invalid email format")
        return cleaned

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.strip() != value:
            raise ValueError("must not have leading or trailing whitespace")
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def at_least_one_field(self) -> UserUpdateRequest:
        provided = self.model_dump(exclude_unset=True)
        if not provided:
            raise ValueError("at least one field must be provided")
        return self


class UserStatusUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_active: bool = Field(alias="isActive")


class UserResponse(BaseModel):
    """Public user representation — password hash is never exposed."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    full_name: str = Field(alias="fullName")
    role_id: uuid.UUID = Field(alias="roleId")
    role_code: str | None = Field(default=None, alias="roleCode")
    role_name: str | None = Field(default=None, alias="roleName")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    is_active: bool = Field(alias="isActive")
    last_login_at: datetime | None = Field(default=None, alias="lastLoginAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
