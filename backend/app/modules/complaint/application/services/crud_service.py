"""Persistence-backed Complaint CRUD application service (CAPABILITY-004).

Controllers call this layer. Repositories are injected via interfaces.
No FastAPI. No ORM imports. No Queue domain imports.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone

from app.core.request_context import RequestContext
from app.modules.complaint.application.dto import ComplaintDto
from app.modules.complaint.application.services.domain_service import (
    ComplaintDomainService,
)
from app.modules.complaint.application.services.errors import ComplaintApplicationError
from app.modules.complaint.domain.models import (
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
)
from app.modules.complaint.domain.repositories import ComplaintRepository


@dataclass(frozen=True, slots=True)
class CreateComplaintInput:
    organization_id: uuid.UUID
    branch_id: uuid.UUID
    queue_ticket_id: uuid.UUID
    category: str
    title: str
    description: str
    priority: ComplaintPriority = ComplaintPriority.NORMAL
    status: ComplaintStatus = ComplaintStatus.OPEN
    complaint_id: uuid.UUID | None = None
    created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UpdateComplaintInput:
    category: str | None = None
    title: str | None = None
    description: str | None = None
    priority: ComplaintPriority | None = None
    status: ComplaintStatus | None = None


class ComplaintCrudApplicationService:
    """CRUD use cases over repository ports + domain rules."""

    def __init__(
        self,
        complaints: ComplaintRepository,
        domain: ComplaintDomainService | None = None,
    ) -> None:
        self._complaints = complaints
        self._domain = domain if domain is not None else ComplaintDomainService()

    async def create_complaint(
        self, context: RequestContext, data: CreateComplaintInput
    ) -> ComplaintDto:
        _ = context
        self._domain.validate_priority(data.priority)
        self._domain.validate_status(data.status)
        if data.status is not ComplaintStatus.OPEN:
            raise ComplaintApplicationError(
                "INVALID_COMPLAINT_STATUS",
                "new complaints must start in OPEN status",
            )
        now = data.created_at or datetime.now(timezone.utc)
        try:
            complaint = Complaint(
                complaint_id=data.complaint_id or uuid.uuid4(),
                organization_id=data.organization_id,
                branch_id=data.branch_id,
                queue_ticket_id=data.queue_ticket_id,
                category=data.category,
                title=data.title,
                description=data.description,
                priority=data.priority,
                status=data.status,
                created_at=now,
                updated_at=now,
            )
        except (TypeError, ValueError) as exc:
            raise ComplaintApplicationError("VALIDATION_ERROR", str(exc)) from exc
        saved = await self._complaints.add(complaint)
        return ComplaintDto.from_domain(saved)

    async def list_complaints(
        self, context: RequestContext, organization_id: uuid.UUID
    ) -> tuple[ComplaintDto, ...]:
        _ = context
        rows = await self._complaints.list_by_organization(organization_id)
        return tuple(ComplaintDto.from_domain(c) for c in rows)

    async def list_by_queue_ticket(
        self, context: RequestContext, queue_ticket_id: uuid.UUID
    ) -> tuple[ComplaintDto, ...]:
        _ = context
        rows = await self._complaints.list_by_queue_ticket(queue_ticket_id)
        return tuple(ComplaintDto.from_domain(c) for c in rows)

    async def get_complaint(
        self, context: RequestContext, complaint_id: uuid.UUID
    ) -> ComplaintDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        return ComplaintDto.from_domain(complaint)

    async def update_complaint(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        data: UpdateComplaintInput,
    ) -> ComplaintDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        category = data.category if data.category is not None else complaint.category
        title = data.title if data.title is not None else complaint.title
        description = (
            data.description if data.description is not None else complaint.description
        )
        priority = data.priority if data.priority is not None else complaint.priority
        if data.priority is not None:
            self._domain.validate_priority(priority)

        now = datetime.now(timezone.utc)
        try:
            updated = replace(
                complaint,
                category=category,
                title=title,
                description=description,
                priority=priority,
                updated_at=now,
            )
        except (TypeError, ValueError) as exc:
            raise ComplaintApplicationError("VALIDATION_ERROR", str(exc)) from exc

        if data.status is not None and data.status is not complaint.status:
            updated = self._domain.transition(updated, data.status, now=now)

        saved = await self._complaints.update(updated)
        return ComplaintDto.from_domain(saved)

    async def delete_complaint(
        self, context: RequestContext, complaint_id: uuid.UUID
    ) -> None:
        _ = context
        deleted = await self._complaints.delete(complaint_id)
        if not deleted:
            raise ComplaintApplicationError(
                "COMPLAINT_NOT_FOUND",
                f"complaint not found: {complaint_id}",
            )

    async def _require_complaint(self, complaint_id: uuid.UUID) -> Complaint:
        complaint = await self._complaints.get_by_id(complaint_id)
        if complaint is None:
            raise ComplaintApplicationError(
                "COMPLAINT_NOT_FOUND",
                f"complaint not found: {complaint_id}",
            )
        return complaint


__all__ = [
    "ComplaintCrudApplicationService",
    "CreateComplaintInput",
    "UpdateComplaintInput",
]
