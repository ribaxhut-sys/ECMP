"""User API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations
from app.core.user_messages import m

import re
import uuid
from datetime import datetime
from typing import Literal

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
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not _EMAIL_RE.match(cleaned):
            raise ValueError(m("validation.invalid_email"))
        return cleaned

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError(m("validation.no_edge_whitespace"))
        if not value.strip():
            raise ValueError(m("validation.must_not_blank"))
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
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        if not _EMAIL_RE.match(cleaned):
            raise ValueError(m("validation.invalid_email"))
        return cleaned

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.strip() != value:
            raise ValueError(m("validation.no_edge_whitespace"))
        if not value.strip():
            raise ValueError(m("validation.must_not_blank"))
        return value

    @model_validator(mode="after")
    def at_least_one_field(self) -> UserUpdateRequest:
        provided = self.model_dump(exclude_unset=True)
        if not provided:
            raise ValueError(m("validation.at_least_one_field"))
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
    force_password_change: bool = Field(default=False, alias="forcePasswordChange")
    last_login_at: datetime | None = Field(default=None, alias="lastLoginAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    preferred_language: str = Field(default="id", alias="preferredLanguage")


class PreferredLanguageUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    preferred_language: Literal["id", "en"] = Field(alias="preferredLanguage")


class PreferredLanguageUpdateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    preferred_language: str = Field(alias="preferredLanguage")


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    current_password: str = Field(alias="currentPassword", min_length=1, max_length=72)
    new_password: str = Field(alias="newPassword", min_length=1, max_length=72)
    confirm_password: str = Field(alias="confirmPassword", min_length=1, max_length=72)

    @model_validator(mode="after")
    def passwords_match(self) -> ChangePasswordRequest:
        if self.new_password != self.confirm_password:
            raise ValueError(m("validation.new_password_confirm_mismatch"))
        return self


class ChangePasswordResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str = m("auth.password_changed")


class AdminResetPasswordResponse(BaseModel):
    """Temporary password is returned once to the admin — never logged."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: uuid.UUID = Field(alias="userId")
    temporary_password: str = Field(alias="temporaryPassword")
    force_password_change: bool = Field(alias="forcePasswordChange", default=True)
    message: str = (
        "Temporary password generated. User must change password on next login."
    )
