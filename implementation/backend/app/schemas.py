"""API contracts (camelCase) aligned to case-service.v1.yaml (DEC-006 D6/U-6 consolidation)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

CaseType = Literal["COMPLAINT", "INQUIRY"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
# Full baseline enum (DOM-ECMF-003), now the single definition in case-service.v1.yaml
# v1.4.0 (U-6 consolidation done, Sprint-03A).
CaseStatus = Literal[
    "REGISTERED",
    "ASSIGNED",
    "IN_PROGRESS",
    "PENDING_REVIEW",
    "CLOSED",
    "REOPENED",
]


class QueueEntry(BaseModel):
    """API-040 queue bucket (dashboard-queues.v1.yaml QueueEntry)."""

    unitId: str
    status: CaseStatus
    count: int = Field(ge=0)
    oldestCreatedAt: datetime | None = None


class DashboardQueuesResponse(BaseModel):
    """API-040 GET /v1/dashboard/queues response (normative, unwrapped)."""

    asOf: datetime
    queues: list[QueueEntry]


class CaseCreateRequest(BaseModel):
    customerId: str = Field(min_length=1, max_length=64)
    caseType: CaseType
    priority: Priority
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    # max_length matches the VARCHAR(32) column — validation and storage must agree.
    channel: str | None = Field(default=None, max_length=32)


class AssignRequest(BaseModel):
    assigneeId: str = Field(min_length=1, max_length=64)
    unitId: str = Field(min_length=1, max_length=64)


class StatusChangeRequest(BaseModel):
    toStatus: CaseStatus
    resolutionCode: str | None = Field(default=None, max_length=64)
    reason: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def _closed_requires_resolution(self) -> StatusChangeRequest:
        # BR-ECMF-06 / DEC-006: resolutionCode MANDATORY for →CLOSED (400 VALIDATION_ERROR).
        if self.toStatus == "CLOSED" and not (self.resolutionCode and self.resolutionCode.strip()):
            raise ValueError("resolutionCode is required when toStatus is CLOSED")
        return self


class Case(BaseModel):
    caseId: str
    customerId: str
    caseType: CaseType
    priority: Priority
    subject: str
    description: str
    status: CaseStatus
    channel: str | None = None
    customerVerified: bool = False
    assigneeId: str | None = None
    unitId: str | None = None
    createdAt: datetime
    createdBy: str
    updatedAt: datetime


class CasePage(BaseModel):
    """API-005 response (FR-005). Sort is fixed createdAt descending (CTO decision, Sprint-03B)."""

    items: list[Case]
    page: int = Field(ge=1)
    pageSize: int = Field(ge=1, le=100)
    totalItems: int = Field(ge=0)


class TimelineEntry(BaseModel):
    """One audit_log row projected for Timeline (summary) and Audit History (detail)."""

    entryId: str
    actionCode: str
    actorUserId: str
    occurredAt: datetime
    summary: str
    detail: dict


class CaseTimeline(BaseModel):
    """API-006 — chronological ascending (oldest first)."""

    entries: list[TimelineEntry]


class NoteCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class CaseNote(BaseModel):
    noteId: str
    caseId: str
    authorUserId: str
    body: str
    createdAt: datetime


class CaseNoteList(BaseModel):
    """API-007 — chronological ascending (comment-thread order)."""

    items: list[CaseNote]


class Error(BaseModel):
    code: str
    message: str
    details: dict | None = None
