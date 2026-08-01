"""Complaint HTTP controllers (CAPABILITY-004…008).

Translate HTTP ↔ Application only. No repository. No ORM. No business rules.
No header parsing — RequestContext comes from Core DI.
"""

from __future__ import annotations

import uuid

from fastapi import Response, status

from app.core.request_context import RequestContext
from app.core.schemas import DataResponse
from app.core.user_messages import m
from app.modules.complaint.api.exception_handlers import raise_as_api_error
from app.modules.complaint.api.requests import (
    AssignRequest,
    CloseRequest,
    CreateComplaintRequest,
    EscalateRequest,
    ReassignRequest,
    RecalculateRequest,
    ReopenRequest,
    ResolveRequest,
    StartSLARequest,
    UnassignRequest,
    UpdateComplaintRequest,
)
from app.modules.complaint.api.responses import (
    AssignmentResponse,
    ComplaintResponse,
    ComplaintSLAResponse,
    EscalationResponse,
)
from app.modules.complaint.application.services import (
    AssignComplaintInput,
    ComplaintApplicationError,
    ComplaintAssignmentApplicationService,
    ComplaintCrudApplicationService,
    ComplaintEscalationApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintSLAApplicationService,
    CreateComplaintInput,
    EscalateComplaintInput,
    ReassignComplaintInput,
    RecalculateSlaInput,
    ReopenComplaintInput,
    ResolveComplaintInput,
    StartSlaInput,
    UnassignComplaintInput,
    UpdateComplaintInput,
)


class ComplaintController:
    """Thin HTTP adapter for Complaint CRUD + processing + assignment + escalation + SLA."""

    def __init__(
        self,
        service: ComplaintCrudApplicationService,
        processing: ComplaintProcessingApplicationService | None = None,
        assignment: ComplaintAssignmentApplicationService | None = None,
        escalation: ComplaintEscalationApplicationService | None = None,
        sla: ComplaintSLAApplicationService | None = None,
    ) -> None:
        self._service = service
        self._processing = processing
        self._assignment = assignment
        self._escalation = escalation
        self._sla = sla

    def _require_processing(self) -> ComplaintProcessingApplicationService:
        if self._processing is None:
            raise RuntimeError(
                "ComplaintProcessingApplicationService is not configured"
            )
        return self._processing

    def _require_assignment(self) -> ComplaintAssignmentApplicationService:
        if self._assignment is None:
            raise RuntimeError(
                "ComplaintAssignmentApplicationService is not configured"
            )
        return self._assignment

    def _require_escalation(self) -> ComplaintEscalationApplicationService:
        if self._escalation is None:
            raise RuntimeError(
                "ComplaintEscalationApplicationService is not configured"
            )
        return self._escalation

    def _require_sla(self) -> ComplaintSLAApplicationService:
        if self._sla is None:
            raise RuntimeError("ComplaintSLAApplicationService is not configured")
        return self._sla

    async def create(
        self,
        payload: CreateComplaintRequest,
        ctx: RequestContext,
        *,
        queue_ticket_id: uuid.UUID | None = None,
    ) -> DataResponse[ComplaintResponse]:
        ticket_id = queue_ticket_id or payload.queue_ticket_id
        if ticket_id is None:
            raise_as_api_error(
                ComplaintApplicationError(
                    "VALIDATION_ERROR",
                    m("queue.ticket_id_required"),
                )
            )
        try:
            dto = await self._service.create_complaint(
                ctx,
                CreateComplaintInput(
                    organization_id=payload.organization_id,
                    branch_id=payload.branch_id,
                    queue_ticket_id=ticket_id,
                    category=payload.category,
                    title=payload.title,
                    description=payload.description,
                    priority=payload.priority,
                ),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintResponse.from_dto(dto))

    async def list(
        self,
        organization_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[list[ComplaintResponse]]:
        try:
            rows = await self._service.list_complaints(ctx, organization_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=[ComplaintResponse.from_dto(r) for r in rows])

    async def list_by_ticket(
        self,
        ticket_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[list[ComplaintResponse]]:
        try:
            rows = await self._service.list_by_queue_ticket(ctx, ticket_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=[ComplaintResponse.from_dto(r) for r in rows])

    async def get(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintResponse]:
        try:
            dto = await self._service.get_complaint(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintResponse.from_dto(dto))

    async def update(
        self,
        complaint_id: uuid.UUID,
        payload: UpdateComplaintRequest,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintResponse]:
        try:
            dto = await self._service.update_complaint(
                ctx,
                complaint_id,
                UpdateComplaintInput(
                    category=payload.category,
                    title=payload.title,
                    description=payload.description,
                    priority=payload.priority,
                    status=payload.status,
                ),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintResponse.from_dto(dto))

    async def delete(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> Response:
        try:
            await self._service.delete_complaint(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def start_processing(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintResponse]:
        try:
            dto = await self._require_processing().start_processing(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintResponse.from_dto(dto))

    async def resolve(
        self,
        complaint_id: uuid.UUID,
        payload: ResolveRequest,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintResponse]:
        try:
            dto = await self._require_processing().resolve(
                ctx,
                complaint_id,
                ResolveComplaintInput(
                    summary=payload.summary,
                    resolved_by=payload.resolved_by,
                ),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintResponse.from_dto(dto))

    async def close(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
        payload: CloseRequest | None = None,
    ) -> DataResponse[ComplaintResponse]:
        _ = payload
        try:
            dto = await self._require_processing().close(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintResponse.from_dto(dto))

    async def reopen(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
        payload: ReopenRequest | None = None,
    ) -> DataResponse[ComplaintResponse]:
        reason = payload.reason if payload is not None else None
        try:
            dto = await self._require_processing().reopen(
                ctx,
                complaint_id,
                ReopenComplaintInput(reason=reason),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintResponse.from_dto(dto))

    async def assign(
        self,
        complaint_id: uuid.UUID,
        payload: AssignRequest,
        ctx: RequestContext,
    ) -> DataResponse[AssignmentResponse]:
        try:
            dto = await self._require_assignment().assign(
                ctx,
                complaint_id,
                AssignComplaintInput(
                    assignee_type=payload.assignee_type,
                    assignee_id=payload.assignee_id,
                    assigned_by=payload.assigned_by,
                ),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=AssignmentResponse.from_dto(dto))

    async def reassign(
        self,
        complaint_id: uuid.UUID,
        payload: ReassignRequest,
        ctx: RequestContext,
    ) -> DataResponse[AssignmentResponse]:
        try:
            dto = await self._require_assignment().reassign(
                ctx,
                complaint_id,
                ReassignComplaintInput(
                    assignee_type=payload.assignee_type,
                    assignee_id=payload.assignee_id,
                    assigned_by=payload.assigned_by,
                ),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=AssignmentResponse.from_dto(dto))

    async def unassign(
        self,
        complaint_id: uuid.UUID,
        payload: UnassignRequest,
        ctx: RequestContext,
    ) -> DataResponse[AssignmentResponse]:
        try:
            dto = await self._require_assignment().unassign(
                ctx,
                complaint_id,
                UnassignComplaintInput(
                    released_by=payload.released_by,
                    reason=payload.reason,
                ),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=AssignmentResponse.from_dto(dto))

    async def get_assignment(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[AssignmentResponse]:
        try:
            dto = await self._require_assignment().get_current(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=AssignmentResponse.from_dto(dto))

    async def list_assignments(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[list[AssignmentResponse]]:
        try:
            rows = await self._require_assignment().list_history(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=[AssignmentResponse.from_dto(r) for r in rows])

    async def escalate(
        self,
        complaint_id: uuid.UUID,
        payload: EscalateRequest,
        ctx: RequestContext,
    ) -> DataResponse[EscalationResponse]:
        try:
            dto = await self._require_escalation().escalate(
                ctx,
                complaint_id,
                EscalateComplaintInput(
                    level=payload.level,
                    reason=payload.reason,
                    escalated_by=payload.escalated_by,
                ),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=EscalationResponse.from_dto(dto))

    async def get_escalation(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[EscalationResponse]:
        try:
            dto = await self._require_escalation().get_current(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=EscalationResponse.from_dto(dto))

    async def list_escalations(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[list[EscalationResponse]]:
        try:
            rows = await self._require_escalation().list_history(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=[EscalationResponse.from_dto(r) for r in rows])

    async def start_sla(
        self,
        complaint_id: uuid.UUID,
        payload: StartSLARequest | None,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintSLAResponse]:
        body = payload if payload is not None else StartSLARequest()
        try:
            dto = await self._require_sla().start(
                ctx,
                complaint_id,
                StartSlaInput(policy_id=body.policy_id),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintSLAResponse.from_dto(dto))

    async def complete_sla(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintSLAResponse]:
        try:
            dto = await self._require_sla().complete(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintSLAResponse.from_dto(dto))

    async def recalculate_sla(
        self,
        complaint_id: uuid.UUID,
        payload: RecalculateRequest,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintSLAResponse]:
        try:
            dto = await self._require_sla().recalculate(
                ctx,
                complaint_id,
                RecalculateSlaInput(current_time=payload.current_time),
            )
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintSLAResponse.from_dto(dto))

    async def get_sla(
        self,
        complaint_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[ComplaintSLAResponse]:
        try:
            dto = await self._require_sla().get(ctx, complaint_id)
        except ComplaintApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=ComplaintSLAResponse.from_dto(dto))


__all__ = ["ComplaintController"]
