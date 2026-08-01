"""ComplaintAssignmentApplicationService (CAPABILITY-006).



Orchestrates repository ports + domain assignment rules.

No FastAPI. No ORM. No business logic beyond calling Domain.

Assignment does not mutate Complaint lifecycle status.

"""



from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.core.request_context import RequestContext
from app.modules.complaint.application.dto import AssignmentDto
from app.modules.complaint.application.services.domain_service import (
    ComplaintDomainService,
)
from app.modules.complaint.application.services.errors import ComplaintApplicationError
from app.modules.complaint.domain.models import AssigneeType, Complaint
from app.modules.complaint.domain.repositories import (
    AssignmentRepository,
    ComplaintRepository,
)


@dataclass(frozen=True, slots=True)

class AssignComplaintInput:

    assignee_type: AssigneeType

    assignee_id: str

    assigned_by: str

    assigned_at: datetime | None = None





@dataclass(frozen=True, slots=True)

class ReassignComplaintInput:

    assignee_type: AssigneeType

    assignee_id: str

    assigned_by: str

    assigned_at: datetime | None = None





@dataclass(frozen=True, slots=True)

class UnassignComplaintInput:

    released_by: str

    reason: str | None = None





class ComplaintAssignmentApplicationService:

    """Assignment use cases (not CRUD / not processing lifecycle)."""



    def __init__(

        self,

        complaints: ComplaintRepository,

        assignments: AssignmentRepository,

        domain: ComplaintDomainService | None = None,

    ) -> None:

        self._complaints = complaints

        self._assignments = assignments

        self._domain = domain if domain is not None else ComplaintDomainService()



    async def assign(

        self,

        context: RequestContext,

        complaint_id: uuid.UUID,

        data: AssignComplaintInput,

    ) -> AssignmentDto:

        _ = context

        complaint = await self._require_complaint(complaint_id)

        active = await self._assignments.get_active_by_complaint(complaint_id)

        created = self._domain.assign(

            complaint,

            assignee_type=data.assignee_type,

            assignee_id=data.assignee_id,

            assigned_by=data.assigned_by,

            active=active,

            now=data.assigned_at,

        )

        saved = await self._assignments.add(created)

        return AssignmentDto.from_domain(saved)



    async def reassign(

        self,

        context: RequestContext,

        complaint_id: uuid.UUID,

        data: ReassignComplaintInput,

    ) -> AssignmentDto:

        _ = context

        complaint = await self._require_complaint(complaint_id)

        active = await self._assignments.get_active_by_complaint(complaint_id)

        released, created = self._domain.reassign(

            complaint,

            assignee_type=data.assignee_type,

            assignee_id=data.assignee_id,

            assigned_by=data.assigned_by,

            active=active,

            now=data.assigned_at,

        )

        await self._assignments.update(released)

        saved = await self._assignments.add(created)

        return AssignmentDto.from_domain(saved)



    async def unassign(

        self,

        context: RequestContext,

        complaint_id: uuid.UUID,

        data: UnassignComplaintInput,

    ) -> AssignmentDto:

        _ = context

        # released_by is accepted for API contract; Timeline/Audit OOS — not persisted.

        _ = data.released_by

        complaint = await self._require_complaint(complaint_id)

        active = await self._assignments.get_active_by_complaint(complaint_id)

        released = self._domain.unassign(

            complaint,

            active=active,

            reason=data.reason,

        )

        saved = await self._assignments.update(released)

        return AssignmentDto.from_domain(saved)



    async def get_current(

        self, context: RequestContext, complaint_id: uuid.UUID

    ) -> AssignmentDto:

        _ = context

        await self._require_complaint(complaint_id)

        active = await self._assignments.get_active_by_complaint(complaint_id)

        if active is None:

            raise ComplaintApplicationError(

                "ASSIGNMENT_NOT_FOUND",

                f"tidak ada penugasan aktif untuk pengaduan: {complaint_id}",

            )

        return AssignmentDto.from_domain(active)



    async def list_history(

        self, context: RequestContext, complaint_id: uuid.UUID

    ) -> tuple[AssignmentDto, ...]:

        _ = context

        await self._require_complaint(complaint_id)

        rows = await self._assignments.list_by_complaint(complaint_id)

        return tuple(AssignmentDto.from_domain(row) for row in rows)



    async def _require_complaint(self, complaint_id: uuid.UUID) -> Complaint:

        complaint = await self._complaints.get_by_id(complaint_id)

        if complaint is None:

            raise ComplaintApplicationError(

                "COMPLAINT_NOT_FOUND",

                f"pengaduan tidak ditemukan: {complaint_id}",

            )

        return complaint





__all__ = [

    "AssignComplaintInput",

    "ComplaintAssignmentApplicationService",

    "ReassignComplaintInput",

    "UnassignComplaintInput",

]

