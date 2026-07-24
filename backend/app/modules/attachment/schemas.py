"""Attachment API contracts (camelCase) — TASK-029."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttachmentResponse(BaseModel):
    """Attachment metadata payload (API-323 / API-324)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    object_type: str = Field(alias="objectType", max_length=50)
    object_id: uuid.UUID = Field(alias="objectId")
    filename: str
    stored_filename: str = Field(alias="storedFilename")
    mime_type: str = Field(alias="mimeType")
    extension: str | None = None
    size_bytes: int = Field(alias="sizeBytes")
    checksum: str
    storage_provider: str = Field(alias="storageProvider")
    uploaded_by: uuid.UUID | None = Field(default=None, alias="uploadedBy")
    created_at: datetime = Field(alias="createdAt")
