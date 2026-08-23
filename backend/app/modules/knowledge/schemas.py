"""Knowledge API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.user_messages import m

KnowledgeTypeLiteral = Literal["SOP", "PERATURAN", "SURAT_EDARAN", "KEPUTUSAN", "PANDUAN"]
KnowledgeStatusLiteral = Literal["DRAFT", "ACTIVE", "ARCHIVED"]
KnowledgeFileRoleLiteral = Literal["PRIMARY", "SUPPORTING"]


class KnowledgeFileResponse(BaseModel):
    """File as seen through a Knowledge record — ``id`` is the underlying
    platform attachment id, so existing /api/v1/attachments/{id}/... routes
    (download, metadata) work unchanged from the frontend."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    file_name: str = Field(alias="fileName")
    mime_type: str = Field(alias="mimeType")
    size_bytes: int = Field(alias="sizeBytes")
    role: KnowledgeFileRoleLiteral
    created_at: datetime = Field(alias="createdAt")


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class KnowledgeCreateRequest(BaseModel):
    """Create — always starts DRAFT. Publish is a separate, explicit action."""

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=200, alias="title")
    knowledge_type: KnowledgeTypeLiteral = Field(alias="knowledgeType")
    document_number: str | None = Field(
        default=None, max_length=100, alias="documentNumber"
    )
    summary: str | None = Field(default=None, alias="summary")
    version_label: str | None = Field(
        default=None, max_length=32, alias="versionLabel"
    )
    effective_from: datetime | None = Field(default=None, alias="effectiveFrom")
    effective_to: datetime | None = Field(default=None, alias="effectiveTo")
    supersedes_knowledge_id: uuid.UUID | None = Field(
        default=None, alias="supersedesKnowledgeId"
    )

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.name_required"))
        return cleaned

    @field_validator("document_number", "version_label")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)

    @field_validator("summary")
    @classmethod
    def strip_summary(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)

    @model_validator(mode="after")
    def check_effective_window(self) -> "KnowledgeCreateRequest":
        if (
            self.effective_from is not None
            and self.effective_to is not None
            and self.effective_from >= self.effective_to
        ):
            raise ValueError(m("knowledge.effective_to_before_from"))
        return self


class KnowledgeUpdateRequest(BaseModel):
    """Update — metadata only. Once ACTIVE, identity fields (title,
    knowledgeType, versionLabel) are locked server-side (KM-018); submit the
    same values or create a new Knowledge record (supersedes) instead."""

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=200, alias="title")
    knowledge_type: KnowledgeTypeLiteral = Field(alias="knowledgeType")
    document_number: str | None = Field(
        default=None, max_length=100, alias="documentNumber"
    )
    summary: str | None = Field(default=None, alias="summary")
    version_label: str | None = Field(
        default=None, max_length=32, alias="versionLabel"
    )
    effective_from: datetime | None = Field(default=None, alias="effectiveFrom")
    effective_to: datetime | None = Field(default=None, alias="effectiveTo")

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(m("validation.name_required"))
        return cleaned

    @field_validator("document_number", "version_label")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)

    @field_validator("summary")
    @classmethod
    def strip_summary(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)

    @model_validator(mode="after")
    def check_effective_window(self) -> "KnowledgeUpdateRequest":
        if (
            self.effective_from is not None
            and self.effective_to is not None
            and self.effective_from >= self.effective_to
        ):
            raise ValueError(m("knowledge.effective_to_before_from"))
        return self


class KnowledgeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    title: str
    knowledge_type: KnowledgeTypeLiteral = Field(alias="knowledgeType")
    status: KnowledgeStatusLiteral
    document_number: str | None = Field(default=None, alias="documentNumber")
    summary: str | None = Field(default=None)
    version_label: str | None = Field(default=None, alias="versionLabel")
    effective_from: datetime | None = Field(default=None, alias="effectiveFrom")
    effective_to: datetime | None = Field(default=None, alias="effectiveTo")
    owner_org_unit_id: str | None = Field(default=None, alias="ownerOrgUnitId")
    published_at: datetime | None = Field(default=None, alias="publishedAt")
    published_by: uuid.UUID | None = Field(default=None, alias="publishedBy")
    supersedes_knowledge_id: uuid.UUID | None = Field(
        default=None, alias="supersedesKnowledgeId"
    )
    supersedes_title: str | None = Field(default=None, alias="supersedesTitle")
    created_by: uuid.UUID | None = Field(default=None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_by: uuid.UUID | None = Field(default=None, alias="updatedBy")
    updated_at: datetime = Field(alias="updatedAt")
    # Post-publish edit window (DEC-030), computed server-side from
    # ``published_at`` — FE must never derive it from the client clock.
    # ``editable_until`` is null when the record is DRAFT (no deadline) or
    # already locked; read ``editable`` to tell those two apart.
    editable: bool = True
    editable_until: datetime | None = Field(default=None, alias="editableUntil")
    # Already access-filtered per-caller by the service — never filter again in FE.
    files: list[KnowledgeFileResponse] = Field(default_factory=list)


class KnowledgeTypeCounts(BaseModel):
    """Citable (ACTIVE + in-window) counts for the ``@`` type picker."""

    SOP: int = 0
    PERATURAN: int = 0
    SURAT_EDARAN: int = 0
    KEPUTUSAN: int = 0
    PANDUAN: int = 0
