"""Complaint resource FastAPI routes (CAPABILITY-004…008).

Note: paths overlap the legacy ``complaints`` ECMF module. This router is
mounted for the Clean Architecture foundation BC. Ticket-nested routes are
unique to CAPABILITY-004. SLA paths under ``…/sla/start|complete|recalculate``
do not collide with legacy GET ``…/sla`` (ECMF).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, Response, status

from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import DataResponse, ErrorResponse
from app.modules.complaint.api.controllers import ComplaintController
from app.modules.complaint.api.dependencies import (
    get_complaint_assignment_service,
    get_complaint_crud_service,
    get_complaint_escalation_service,
    get_complaint_processing_service,
    get_complaint_sla_service,
)
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
    ComplaintAssignmentApplicationService,
    ComplaintCrudApplicationService,
    ComplaintEscalationApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintSLAApplicationService,
)

router = APIRouter(prefix="/api/v1/complaints", tags=["Complaint Domain"])

_ERROR = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}


def get_complaint_controller(
    service: Annotated[
        ComplaintCrudApplicationService, Depends(get_complaint_crud_service)
    ],
    processing: Annotated[
        ComplaintProcessingApplicationService,
        Depends(get_complaint_processing_service),
    ],
    assignment: Annotated[
        ComplaintAssignmentApplicationService,
        Depends(get_complaint_assignment_service),
    ],
    escalation: Annotated[
        ComplaintEscalationApplicationService,
        Depends(get_complaint_escalation_service),
    ],
    sla: Annotated[
        ComplaintSLAApplicationService,
        Depends(get_complaint_sla_service),
    ],
) -> ComplaintController:
    return ComplaintController(service, processing, assignment, escalation, sla)


@router.post(
    "",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create complaint",
    operation_id="createComplaintDomain",
    description=(
        "Create a visit-context Complaint linked to queueTicketId. "
        "Initial status is OPEN. Does not call Queue operations."
    ),
    responses=_ERROR,
)
async def create_complaint(
    payload: CreateComplaintRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintResponse]:
    """API-390 — Create Complaint."""
    return await controller.create(payload, ctx)


@router.get(
    "",
    response_model=DataResponse[list[ComplaintResponse]],
    status_code=status.HTTP_200_OK,
    summary="List complaints by organization",
    operation_id="listComplaintDomain",
    description="List complaints owned by organizationId (required query parameter).",
    responses=_ERROR,
)
async def list_complaints(
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[list[ComplaintResponse]]:
    """API-391 — List Complaints."""
    return await controller.list(organization_id, ctx)


@router.get(
    "/{complaint_id}",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Get complaint by id",
    operation_id="getComplaintDomain",
    description="Return a single Complaint response DTO by complaint_id.",
    responses=_ERROR,
)
async def get_complaint(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintResponse]:
    """API-392 — Get Complaint."""
    return await controller.get(complaint_id, ctx)


@router.put(
    "/{complaint_id}",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Update complaint",
    operation_id="updateComplaintDomain",
    description=(
        "Update mutable Complaint fields. Status transitions must follow "
        "OPEN → IN_PROGRESS → RESOLVED → CLOSED (reopen: RESOLVED → IN_PROGRESS)."
    ),
    responses=_ERROR,
)
async def update_complaint(
    complaint_id: uuid.UUID,
    payload: UpdateComplaintRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintResponse]:
    """API-393 — Update Complaint."""
    return await controller.update(complaint_id, payload, ctx)


@router.delete(
    "/{complaint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete complaint",
    operation_id="deleteComplaintDomain",
    description="Hard-delete a Complaint.",
    response_class=Response,
    responses={
        204: {"description": "Deleted"},
        **_ERROR,
    },
)
async def delete_complaint(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> Response:
    """API-394 — Delete Complaint."""
    return await controller.delete(complaint_id, ctx)


@router.post(
    "/{complaint_id}/start",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Start complaint processing",
    operation_id="startComplaintProcessing",
    description="OPEN → IN_PROGRESS. Domain-validated lifecycle transition.",
    responses=_ERROR,
)
async def start_complaint_processing(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintResponse]:
    """API-397 — Start Processing."""
    return await controller.start_processing(complaint_id, ctx)


@router.post(
    "/{complaint_id}/resolve",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Resolve complaint",
    operation_id="resolveComplaint",
    description=(
        "IN_PROGRESS → RESOLVED. Requires summary and resolvedBy. "
        "Creates a Resolution value object."
    ),
    responses=_ERROR,
)
async def resolve_complaint(
    complaint_id: uuid.UUID,
    payload: ResolveRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintResponse]:
    """API-398 — Resolve Complaint."""
    return await controller.resolve(complaint_id, payload, ctx)


@router.post(
    "/{complaint_id}/close",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Close complaint",
    operation_id="closeComplaintDomain",
    description=(
        "RESOLVED → CLOSED. Resolution becomes immutable. "
        "Request body is optional."
    ),
    responses=_ERROR,
)
async def close_complaint(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    payload: Annotated[CloseRequest | None, Body()] = None,
) -> DataResponse[ComplaintResponse]:
    """API-399 — Close Complaint."""
    return await controller.close(complaint_id, ctx, payload)


@router.post(
    "/{complaint_id}/reopen",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Reopen complaint",
    operation_id="reopenComplaint",
    description=(
        "RESOLVED → IN_PROGRESS. Optional reason (not persisted — Timeline OOS). "
        "Clears prior Resolution so a new resolve may be recorded."
    ),
    responses=_ERROR,
)
async def reopen_complaint(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    payload: Annotated[ReopenRequest, Body()] = ReopenRequest(),
) -> DataResponse[ComplaintResponse]:
    """API-400 — Reopen Complaint."""
    return await controller.reopen(complaint_id, ctx, payload)


@router.post(
    "/{complaint_id}/assign",
    response_model=DataResponse[AssignmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Assign complaint",
    operation_id="assignComplaintDomain",
    description=(
        "Create the first active Assignment for a Complaint. "
        "Rejects when an active assignment already exists (use reassign). "
        "Does not change Complaint lifecycle status."
    ),
    responses=_ERROR,
)
async def assign_complaint(
    complaint_id: uuid.UUID,
    payload: AssignRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[AssignmentResponse]:
    """API-401 — Assign Complaint."""
    return await controller.assign(complaint_id, payload, ctx)


@router.post(
    "/{complaint_id}/reassign",
    response_model=DataResponse[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Reassign complaint",
    operation_id="reassignComplaintDomain",
    description=(
        "Release the active Assignment and append a new active Assignment. "
        "History rows are not rewritten. Does not change Complaint status."
    ),
    responses=_ERROR,
)
async def reassign_complaint(
    complaint_id: uuid.UUID,
    payload: ReassignRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[AssignmentResponse]:
    """API-402 — Reassign Complaint."""
    return await controller.reassign(complaint_id, payload, ctx)


@router.post(
    "/{complaint_id}/unassign",
    response_model=DataResponse[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Unassign complaint",
    operation_id="unassignComplaintDomain",
    description=(
        "Release the active Assignment. Complaint has no active assignee. "
        "Does not change Complaint lifecycle status."
    ),
    responses=_ERROR,
)
async def unassign_complaint(
    complaint_id: uuid.UUID,
    payload: UnassignRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[AssignmentResponse]:
    """API-403 — Unassign Complaint."""
    return await controller.unassign(complaint_id, payload, ctx)


@router.get(
    "/{complaint_id}/assignment",
    response_model=DataResponse[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current assignment",
    operation_id="getComplaintAssignmentDomain",
    description="Return the single active Assignment for a Complaint, if any.",
    responses=_ERROR,
)
async def get_complaint_assignment(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[AssignmentResponse]:
    """API-404 — Current Assignment."""
    return await controller.get_assignment(complaint_id, ctx)


@router.get(
    "/{complaint_id}/assignments",
    response_model=DataResponse[list[AssignmentResponse]],
    status_code=status.HTTP_200_OK,
    summary="List assignment history",
    operation_id="listComplaintAssignmentsDomain",
    description="Append-only Assignment history for a Complaint (oldest first).",
    responses=_ERROR,
)
async def list_complaint_assignments(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[list[AssignmentResponse]]:
    """API-405 — Assignment History."""
    return await controller.list_assignments(complaint_id, ctx)


@router.post(
    "/{complaint_id}/escalate",
    response_model=DataResponse[EscalationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Escalate complaint",
    operation_id="escalateComplaintDomain",
    description=(
        "Append a new current Escalation. Prior current becomes historical. "
        "Level must increase when a current escalation exists. "
        "Does not change Assignment or Complaint lifecycle status."
    ),
    responses=_ERROR,
)
async def escalate_complaint(
    complaint_id: uuid.UUID,
    payload: EscalateRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[EscalationResponse]:
    """API-406 — Escalate Complaint."""
    return await controller.escalate(complaint_id, payload, ctx)


@router.get(
    "/{complaint_id}/escalation",
    response_model=DataResponse[EscalationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current escalation",
    operation_id="getComplaintEscalationDomain",
    description="Return the single current Escalation for a Complaint, if any.",
    responses=_ERROR,
)
async def get_complaint_escalation(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[EscalationResponse]:
    """API-407 — Current Escalation."""
    return await controller.get_escalation(complaint_id, ctx)


@router.get(
    "/{complaint_id}/escalations",
    response_model=DataResponse[list[EscalationResponse]],
    status_code=status.HTTP_200_OK,
    summary="List escalation history",
    operation_id="listComplaintEscalationsDomain",
    description="Append-only Escalation history for a Complaint (oldest first).",
    responses=_ERROR,
)
async def list_complaint_escalations(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[list[EscalationResponse]]:
    """API-408 — Escalation History."""
    return await controller.list_escalations(complaint_id, ctx)


@router.post(
    "/{complaint_id}/sla/start",
    response_model=DataResponse[ComplaintSLAResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Start complaint SLA",
    operation_id="startComplaintSlaDomain",
    description=(
        "Start ComplaintSLA from SLAPolicy (default when policyId omitted). "
        "At most one active SLA per complaint. Does not change Complaint status."
    ),
    responses=_ERROR,
)
async def start_complaint_sla(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    payload: Annotated[StartSLARequest | None, Body()] = None,
) -> DataResponse[ComplaintSLAResponse]:
    """API-409 — Start Complaint SLA."""
    return await controller.start_sla(complaint_id, payload, ctx)


@router.post(
    "/{complaint_id}/sla/complete",
    response_model=DataResponse[ComplaintSLAResponse],
    status_code=status.HTTP_200_OK,
    summary="Complete complaint SLA",
    operation_id="completeComplaintSlaDomain",
    description=(
        "Complete the active ComplaintSLA. Does not change Complaint status, "
        "create Escalation, or send Notification."
    ),
    responses=_ERROR,
)
async def complete_complaint_sla(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintSLAResponse]:
    """API-410 — Complete Complaint SLA."""
    return await controller.complete_sla(complaint_id, ctx)


@router.post(
    "/{complaint_id}/sla/recalculate",
    response_model=DataResponse[ComplaintSLAResponse],
    status_code=status.HTTP_200_OK,
    summary="Recalculate complaint SLA",
    operation_id="recalculateComplaintSlaDomain",
    description=(
        "Manual breach detection + remaining time against currentTime. "
        "No scheduler. breachedAt is set once when due is exceeded."
    ),
    responses=_ERROR,
)
async def recalculate_complaint_sla(
    complaint_id: uuid.UUID,
    payload: RecalculateRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintSLAResponse]:
    """API-411 — Recalculate Complaint SLA."""
    return await controller.recalculate_sla(complaint_id, payload, ctx)


@router.get(
    "/{complaint_id}/sla",
    response_model=DataResponse[ComplaintSLAResponse],
    status_code=status.HTTP_200_OK,
    summary="Get complaint SLA",
    operation_id="getComplaintSlaDomain",
    description=(
        "Return active ComplaintSLA when present, otherwise the latest "
        "completed/historical SLA. May refresh breach detection on active rows."
    ),
    responses=_ERROR,
)
async def get_complaint_sla(
    complaint_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintSLAResponse]:
    """API-412 — Get Complaint SLA."""
    return await controller.get_sla(complaint_id, ctx)


__all__ = ["router"]
