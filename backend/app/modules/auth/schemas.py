"""Auth API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be blank")
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
    last_login_at: datetime | None = Field(default=None, alias="lastLoginAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
