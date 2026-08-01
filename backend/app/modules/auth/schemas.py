"""Auth API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.user_messages import m


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value:
            raise ValueError(m("validation.must_not_blank"))
        return value


class TokenResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="Bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn", ge=1)


class AuthMeResponse(BaseModel):
    """Current authenticated user — password hash never exposed."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    full_name: str = Field(alias="fullName")
    role_id: uuid.UUID = Field(alias="roleId")
    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    is_active: bool = Field(alias="isActive")
    force_password_change: bool = Field(default=False, alias="forcePasswordChange")
    last_login_at: datetime | None = Field(default=None, alias="lastLoginAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    preferred_language: str = Field(default="id", alias="preferredLanguage")
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str = Field(min_length=3, max_length=320)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned or "@" not in cleaned:
            raise ValueError(m("validation.invalid_email"))
        return cleaned


class ForgotPasswordResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str = Field(
        default="If the account exists, a reset link has been sent."
    )


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str = Field(min_length=1, max_length=512)
    password: str = Field(min_length=1, max_length=72)
    confirm_password: str = Field(alias="confirmPassword", min_length=1, max_length=72)

    @field_validator("token")
    @classmethod
    def strip_token(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.must_not_blank"))
        return cleaned

    @model_validator(mode="after")
    def passwords_match(self) -> ResetPasswordRequest:
        if self.password != self.confirm_password:
            raise ValueError(m("validation.password_confirm_mismatch"))
        return self


class ResetPasswordResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str = m("auth.password_reset_ok")
