"""ComplaintProcessingApplicationService (CAPABILITY-005 + Rule 4 SLA close).

Orchestrates repository ports + domain processing rules.
No FastAPI. No ORM. No business logic beyond calling Domain.
When a Complaint is CLOSED, any active SLA is completed (CAPABILITY-008 Rule 4).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.core.request_context import RequestContext
from app.modules.complaint.application.dto import ComplaintDto
from app.modules.complaint.application.services.domain_service import (
    ComplaintDomainService,
)
from app.modules.complaint.application.services.errors import ComplaintApplicationError
from app.modules.complaint.domain.models import Complaint
from app.modules.complaint.domain.repositories import (
    ComplaintRepository,
    ComplaintSlaRepository,
)


@dataclass(frozen=True, slots=True)
class ResolveComplaintInput:
    summary: str
    resolved_by: str
    resolved_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ReopenComplaintInput:
    reason: str | None = None


class ComplaintProcessingApplicationService:
    """Processing lifecycle use cases (not CRUD)."""

    def __init__(
        self,
        complaints: ComplaintRepository,
        domain: ComplaintDomainService | None = None,
        slas: ComplaintSlaRepository | None = None,
    ) -> None:
        self._complaints = complaints
        self._domain = domain if domain is not None else ComplaintDomainService()
        self._slas = slas

    async def start_processing(
        self, context: RequestContext, complaint_id: uuid.UUID
    ) -> ComplaintDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        updated = self._domain.start_processing(complaint)
        saved = await self._complaints.update(updated)
        return ComplaintDto.from_domain(saved)

    async def resolve(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        data: ResolveComplaintInput,
    ) -> ComplaintDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        updated = self._domain.resolve(
            complaint,
            data.summary,
            data.resolved_by,
            now=data.resolved_at,
        )
        saved = await self._complaints.update(updated)
        return ComplaintDto.from_domain(saved)

    async def close(
        self, context: RequestContext, complaint_id: uuid.UUID
    ) -> ComplaintDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        updated = self._domain.close(complaint)
        saved = await self._complaints.update(updated)
        # Rule 4 — closing completes active SLA (no escalation / notification).
        if self._slas is not None:
            active = await self._slas.get_active_by_complaint(complaint_id)
            if active is not None and active.is_active:
                completed = self._domain.complete_sla(
                    saved, active=active, now=saved.updated_at
                )
                await self._slas.update(completed)
        return ComplaintDto.from_domain(saved)

    async def reopen(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        data: ReopenComplaintInput | None = None,
    ) -> ComplaintDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        reason = data.reason if data is not None else None
        updated = self._domain.reopen(complaint, reason=reason)
        saved = await self._complaints.update(updated)
        return ComplaintDto.from_domain(saved)

    async def _require_complaint(self, complaint_id: uuid.UUID) -> Complaint:
        complaint = await self._complaints.get_by_id(complaint_id)
        if complaint is None:
            raise ComplaintApplicationError(
                "COMPLAINT_NOT_FOUND",
                f"complaint not found: {complaint_id}",
            )
        return complaint


__all__ = [
    "ComplaintProcessingApplicationService",
    "ReopenComplaintInput",
    "ResolveComplaintInput",
]
