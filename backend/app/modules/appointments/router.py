"""Appointment HTTP routes (API-305 / API-306 / API-307 / API-308 / API-309)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import (
    Principal,
    require_appointment_complete,
    require_escalation_review,
    require_permissions,
)
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.appointments.repository import AppointmentRepository
from app.modules.appointments.schemas import (
    AppointmentBookResult,
    AppointmentCheckInRequest,
    AppointmentCheckInResult,
    AppointmentCompleteRequest,
    AppointmentCompleteResult,
    AppointmentCreate,
    AppointmentNoShowRequest,
    AppointmentNoShowResult,
    AppointmentResponse,
)
from app.modules.appointments.service import AppointmentService

# Nested under escalations for API-305
escalation_appointments_router = APIRouter(
    prefix="/api/v1/escalations", tags=["Appointments"]
)

# Top-level appointments for API-306 / API-307 / API-308 / API-309
appointments_router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])


def get_appointment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AppointmentService:
    return AppointmentService(AppointmentRepository(session))


@escalation_appointments_router.post(
    "/{id}/appointments",
    response_model=DataResponse[AppointmentBookResult],
    status_code=status.HTTP_200_OK,
    summary="Book appointment for approved escalation",
)
def book_appointment(
    id: uuid.UUID,
    payload: AppointmentCreate,
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
    principal: Annotated[Principal, Depends(require_escalation_review)],
) -> DataResponse[AppointmentBookResult]:
    """API-305 — book appointment (HO Scheduler / Admin)."""
    result = service.book(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@appointments_router.get(
    "/{id}",
    response_model=DataResponse[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get appointment by id",
)
def get_appointment(
    id: uuid.UUID,
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[AppointmentResponse]:
    """API-306 — get appointment detail."""
    _ = principal
    return DataResponse(data=service.get_appointment(id))


@appointments_router.post(
    "/{id}/check-in",
    response_model=DataResponse[AppointmentCheckInResult],
    status_code=status.HTTP_200_OK,
    summary="Check in customer for booked appointment",
)
def check_in_appointment(
    id: uuid.UUID,
    payload: AppointmentCheckInRequest,
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
    principal: Annotated[Principal, Depends(require_escalation_review)],
) -> DataResponse[AppointmentCheckInResult]:
    """API-307 — customer check-in (HO Scheduler / Admin)."""
    result = service.check_in(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@appointments_router.post(
    "/{id}/complete",
    response_model=DataResponse[AppointmentCompleteResult],
    status_code=status.HTTP_200_OK,
    summary="Complete checked-in appointment",
)
def complete_appointment(
    id: uuid.UUID,
    payload: AppointmentCompleteRequest,
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
    principal: Annotated[Principal, Depends(require_appointment_complete)],
) -> DataResponse[AppointmentCompleteResult]:
    """API-308 — appointment completion (HO Engineer / Admin)."""
    result = service.complete(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@appointments_router.post(
    "/{id}/no-show",
    response_model=DataResponse[AppointmentNoShowResult],
    status_code=status.HTTP_200_OK,
    summary="Mark booked appointment as customer no-show",
)
def mark_appointment_no_show(
    id: uuid.UUID,
    payload: AppointmentNoShowRequest,
    service: Annotated[AppointmentService, Depends(get_appointment_service)],
    principal: Annotated[Principal, Depends(require_escalation_review)],
) -> DataResponse[AppointmentNoShowResult]:
    """API-309 — customer no-show (HO Scheduler / Admin)."""
    result = service.mark_no_show(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)
