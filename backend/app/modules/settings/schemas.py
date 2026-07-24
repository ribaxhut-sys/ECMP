"""System Settings API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ValueTypeLiteral = Literal["STRING", "INTEGER", "BOOLEAN", "JSON", "URL", "EMAIL"]
VisibilityLiteral = Literal["PUBLIC", "PROTECTED"]


class SettingResponse(BaseModel):
    """API-320 / API-321 / API-322 setting payload."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    key: str
    value: str
    value_type: ValueTypeLiteral = Field(alias="valueType")
    category: str
    visibility: VisibilityLiteral
    description: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SettingUpdateRequest(BaseModel):
    """API-322 update setting value (type validated server-side)."""

    model_config = ConfigDict(populate_by_name=True)

    value: str = Field(min_length=0, max_length=10000)
