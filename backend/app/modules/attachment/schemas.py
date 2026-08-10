"""CAPABILITY-011 Attachment API schemas (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AggregateTypeLiteral = Literal["Complaint", "Queue", "Notification", "Announcement"]
AttachmentStatusLiteral = Literal["UPLOADED", "AVAILABLE", "DELETED", "FAILED"]


class AttachmentResponse(BaseModel):
    """Attachment metadata payload (bytes never included)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    aggregate_type: AggregateTypeLiteral = Field(alias="aggregateType")
    aggregate_id: uuid.UUID = Field(alias="aggregateId")
    file_name: str = Field(alias="fileName")
    original_name: str = Field(alias="originalName")
    mime_type: str = Field(alias="mimeType")
    extension: str | None = None
    size_bytes: int = Field(alias="sizeBytes")
    storage_provider: str = Field(alias="storageProvider")
    checksum_sha256: str = Field(alias="checksumSha256")
    uploaded_by: uuid.UUID | None = Field(default=None, alias="uploadedBy")
    uploaded_at: datetime = Field(alias="uploadedAt")
    status: AttachmentStatusLiteral
    access_level: Literal["PUBLIC", "PRIVATE"] | None = Field(
        default=None, alias="accessLevel"
    )
    uploaded_org_unit_id: str | None = Field(default=None, alias="uploadedOrgUnitId")
