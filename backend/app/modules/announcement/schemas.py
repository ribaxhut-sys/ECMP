"""Announcement API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.user_messages import m

AnnouncementPriorityLiteral = Literal["NORMAL", "IMPORTANT"]
AnnouncementStatusLiteral = Literal["DRAFT", "PUBLISHED", "ARCHIVED"]
# Read-only, derived — never stored. SCHEDULED = PUBLISHED with start_at in
# the future; EXPIRED = PUBLISHED whose end_at has elapsed (DEC: no scheduler).
AnnouncementEffectiveStatusLiteral = Literal[
    "DRAFT", "PUBLISHED", "ARCHIVED", "EXPIRED", "SCHEDULED"
]
# IMMEDIATE = visible as soon as uploaded, even while DRAFT. PUBLISHED
# (default, safest) = follows the announcement's own status.
AnnouncementAttachmentVisibilityLiteral = Literal["IMMEDIATE", "PUBLISHED"]


class AnnouncementAttachmentResponse(BaseModel):
    """Attachment as seen through an announcement — ``id`` is the underlying
    platform attachment id, so existing /api/v1/attachments/{id}/... routes
    (download, metadata) work unchanged from the frontend."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    file_name: str = Field(alias="fileName")
    mime_type: str = Field(alias="mimeType")
    size_bytes: int = Field(alias="sizeBytes")
    visibility: AnnouncementAttachmentVisibilityLiteral
    created_at: datetime = Field(alias="createdAt")


class AnnouncementAttachmentLibraryItem(BaseModel):
    """Reusable announcement-domain file for catalog / link picker."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    file_name: str = Field(alias="fileName")
    mime_type: str = Field(alias="mimeType")
    size_bytes: int = Field(alias="sizeBytes")
    created_at: datetime = Field(alias="createdAt")
    access_level: Literal["PUBLIC", "PRIVATE"] = Field(
        default="PRIVATE", alias="accessLevel"
    )
    uploaded_org_unit_id: str | None = Field(default=None, alias="uploadedOrgUnitId")
    uploaded_by: uuid.UUID | None = Field(default=None, alias="uploadedBy")
    uploaded_by_name: str | None = Field(default=None, alias="uploadedByName")
    usage_count: int = Field(default=0, alias="usageCount")


class AnnouncementAttachmentAccessUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_level: Literal["PUBLIC", "PRIVATE"] = Field(alias="accessLevel")


class AnnouncementAttachmentVisibilityUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    visibility: AnnouncementAttachmentVisibilityLiteral = Field(alias="visibility")


class AnnouncementAttachmentLinkRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    attachment_id: uuid.UUID = Field(alias="attachmentId")
    visibility: AnnouncementAttachmentVisibilityLiteral = Field(
        default="PUBLISHED", alias="visibility"
    )


class AnnouncementCreateRequest(BaseModel):
    """Create — always starts DRAFT. Publish is a separate action (no auto-publish)."""

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=200, alias="title")
    body: str = Field(min_length=1, alias="body")
    priority: AnnouncementPriorityLiteral = Field(default="NORMAL", alias="priority")
    end_at: datetime | None = Field(default=None, alias="endAt")

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.name_required"))
        return cleaned

    @field_validator("body")
    @classmethod
    def strip_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("announcement.body_required"))
        return cleaned


class AnnouncementUpdateRequest(BaseModel):
    """Update — allowed for any status (business rule: no approval workflow).

    ``startAt`` is optional: omit to leave schedule unchanged; send a value to
    reschedule (SCHEDULED / published); send null to clear schedule (visible now
    when status is PUBLISHED).
    """

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=200, alias="title")
    body: str = Field(min_length=1, alias="body")
    priority: AnnouncementPriorityLiteral = Field(alias="priority")
    start_at: datetime | None = Field(default=None, alias="startAt")
    end_at: datetime | None = Field(default=None, alias="endAt")

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.name_required"))
        return cleaned

    @field_validator("body")
    @classmethod
    def strip_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("announcement.body_required"))
        return cleaned


class AnnouncementPublishRequest(BaseModel):
    """Optional body for publish — omit / null startAt = publish now.

    A future startAt keeps DB status PUBLISHED but delays landing visibility
    until start_at (read-time evaluation; no scheduler).
    """

    model_config = ConfigDict(populate_by_name=True)

    start_at: datetime | None = Field(default=None, alias="startAt")


class AnnouncementResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    reference_number: str = Field(alias="referenceNumber")
    title: str
    body: str
    priority: AnnouncementPriorityLiteral
    status: AnnouncementStatusLiteral
    effective_status: AnnouncementEffectiveStatusLiteral = Field(alias="effectiveStatus")
    start_at: datetime | None = Field(default=None, alias="startAt")
    end_at: datetime | None = Field(default=None, alias="endAt")
    published_at: datetime | None = Field(default=None, alias="publishedAt")
    published_by: uuid.UUID | None = Field(default=None, alias="publishedBy")
    created_by: uuid.UUID | None = Field(default=None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_by: uuid.UUID | None = Field(default=None, alias="updatedBy")
    updated_at: datetime = Field(alias="updatedAt")
    # Already filtered per-caller by the service (manage sees all; read-only
    # sees only what the visibility rule allows) — never filter again in FE.
    attachments: list[AnnouncementAttachmentResponse] = Field(default_factory=list)
    attachment_count: int = Field(default=0, alias="attachmentCount")
    # Reader lists (/history, /active) set this from announcement_reads.
    # Management list leaves it null — read-state is a reader concern.
    is_read: bool | None = Field(default=None, alias="isRead")
