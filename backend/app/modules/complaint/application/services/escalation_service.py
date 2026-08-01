"""ComplaintEscalationApplicationService (CAPABILITY-007).

Orchestrates repository ports + domain escalation rules.
No FastAPI. No ORM. No business logic beyond calling Domain.
Escalation does not mutate Complaint lifecycle status or Assignment.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.core.request_context import RequestContext
from app.modules.complaint.application.dto import EscalationDto
from app.modules.complaint.application.services.domain_service import (
    ComplaintDomainService,
)
from app.modules.complaint.application.services.errors import ComplaintApplicationError
from app.modules.complaint.domain.models import Complaint, EscalationLevel
from app.modules.complaint.domain.repositories import (
    ComplaintRepository,
    EscalationRepository,
)


@dataclass(frozen=True, slots=True)
class EscalateComplaintInput:
    level: EscalationLevel
    reason: str
    escalated_by: str
    escalated_at: datetime | None = None


class ComplaintEscalationApplicationService:
    """Escalation use cases (not CRUD / not processing / not assignment)."""

    def __init__(
        self,
        complaints: ComplaintRepository,
        escalations: EscalationRepository,
        domain: ComplaintDomainService | None = None,
    ) -> None:
        self._complaints = complaints
        self._escalations = escalations
        self._domain = domain if domain is not None else ComplaintDomainService()

    async def escalate(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        data: EscalateComplaintInput,
    ) -> EscalationDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        current = await self._escalations.get_current_by_complaint(complaint_id)
        released, created = self._domain.escalate(
            complaint,
            level=data.level,
            reason=data.reason,
            escalated_by=data.escalated_by,
            current=current,
            now=data.escalated_at,
        )
        if released is not None:
            await self._escalations.update(released)
        saved = await self._escalations.add(created)
        return EscalationDto.from_domain(saved)

    async def get_current(
        self, context: RequestContext, complaint_id: uuid.UUID
    ) -> EscalationDto:
        _ = context
        await self._require_complaint(complaint_id)
        current = await self._escalations.get_current_by_complaint(complaint_id)
        if current is None:
            raise ComplaintApplicationError(
                "ESCALATION_NOT_FOUND",
                f"tidak ada eskalasi saat ini untuk pengaduan: {complaint_id}",
            )
        return EscalationDto.from_domain(current)

    async def list_history(
        self, context: RequestContext, complaint_id: uuid.UUID
    ) -> tuple[EscalationDto, ...]:
        _ = context
        await self._require_complaint(complaint_id)
        rows = await self._escalations.list_by_complaint(complaint_id)
        return tuple(EscalationDto.from_domain(row) for row in rows)

    async def _require_complaint(self, complaint_id: uuid.UUID) -> Complaint:
        complaint = await self._complaints.get_by_id(complaint_id)
        if complaint is None:
            raise ComplaintApplicationError(
                "COMPLAINT_NOT_FOUND",
                f"pengaduan tidak ditemukan: {complaint_id}",
            )
        return complaint


__all__ = [
    "ComplaintEscalationApplicationService",
    "EscalateComplaintInput",
]
