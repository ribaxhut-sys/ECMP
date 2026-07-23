"""Appointment application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import AppointmentStatus, EscalationRequestStatus, TimelineEvent
from app.core.errors import NotFoundError, ValidationAppError
from app.models import Appointment
from app.modules.appointments.repository import AppointmentRepository
from app.modules.appointments.schemas import (
    AppointmentBookResult,
    AppointmentCreate,
    AppointmentResponse,
    AppointmentSummary,
)

NOT_APPROVED_MESSAGE = "Escalation must be APPROVED before booking an appointment."
HAS_ACTIVE_APPOINTMENT_MESSAGE = "Escalation already has an active appointment."
ENGINEER_NOT_FOUND_MESSAGE = "Assigned engineer not found or inactive."
OVERLAP_MESSAGE = "Appointment overlaps an existing booking for this engineer."


def _format_hhmm(value: object) -> str:
    return value.strftime("%H:%M") if hasattr(value, "strftime") else str(value)


def _to_response(row: Appointment) -> AppointmentResponse:
    engineer = row.__dict__.get("assigned_engineer")
    name = getattr(engineer, "full_name", None) if engineer is not None else None
    data = AppointmentResponse.model_validate(row)
    return data.model_copy(update={"assigned_engineer_name": name})


def to_summary(row: Appointment) -> AppointmentSummary:
    return AppointmentSummary.model_validate(row)


class AppointmentService:
    def __init__(self, repository: AppointmentRepository) -> None:
        self._repo = repository

    def book(
        self,
        escalation_id: uuid.UUID,
        payload: AppointmentCreate,
        *,
        actor_user_id: uuid.UUID,
    ) -> AppointmentBookResult:
        """API-305 — book appointment on APPROVED escalation."""
        escalation = self._repo.get_escalation(escalation_id)
        if escalation is None:
            raise NotFoundError("Escalation not found")

        if escalation.status != EscalationRequestStatus.APPROVED:
            raise ValidationAppError(
                NOT_APPROVED_MESSAGE,
                details={"status": escalation.status},
            )

        existing = self._repo.get_active_by_escalation(escalation_id)
        if existing is not None:
            raise ValidationAppError(
                HAS_ACTIVE_APPOINTMENT_MESSAGE,
                details={
                    "escalationId": str(escalation_id),
                    "appointmentId": str(existing.id),
                },
            )

        if not self._repo.user_exists(payload.assigned_engineer_id):
            raise ValidationAppError(
                ENGINEER_NOT_FOUND_MESSAGE,
                details={"assignedEngineerId": str(payload.assigned_engineer_id)},
            )

        overlap = self._repo.find_engineer_overlap(
            engineer_id=payload.assigned_engineer_id,
            on_date=payload.appointment_date,
            start=payload.start_time,
            end=payload.end_time,
        )
        if overlap is not None:
            raise ValidationAppError(
                OVERLAP_MESSAGE,
                details={
                    "assignedEngineerId": str(payload.assigned_engineer_id),
                    "appointmentDate": payload.appointment_date.isoformat(),
                    "conflictingAppointmentId": str(overlap.id),
                },
            )

        complaint = self._repo.get_complaint(escalation.complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        now = datetime.now(UTC)
        appointment = Appointment(
            escalation_id=escalation.id,
            appointment_date=payload.appointment_date,
            appointment_start_time=payload.start_time,
            appointment_end_time=payload.end_time,
            status=AppointmentStatus.BOOKED,
            assigned_engineer_id=payload.assigned_engineer_id,
            notes=payload.notes,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._repo.add(appointment)

        # Complaint remains IN_PROGRESS; escalation remains APPROVED.
        complaint.updated_at = now
        complaint.updated_by = actor_user_id
        escalation.updated_at = now
        escalation.updated_by = actor_user_id

        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.APPOINTMENT_BOOKED,
            event_at=now,
            from_status=complaint.status,
            to_status=complaint.status,
            summary="Appointment booked",
            metadata={
                "changeType": "APPOINTMENT_BOOKED",
                "appointmentId": str(appointment.id),
                "escalationId": str(escalation.id),
                "appointmentDate": payload.appointment_date.isoformat(),
                "startTime": _format_hhmm(payload.start_time),
                "endTime": _format_hhmm(payload.end_time),
                "assignedEngineerId": str(payload.assigned_engineer_id),
                "bookedBy": str(actor_user_id),
            },
        )

        result = AppointmentBookResult(
            id=appointment.id,
            status=AppointmentStatus.BOOKED,
        )
        self._repo.commit()
        return result

    def get_appointment(self, appointment_id: uuid.UUID) -> AppointmentResponse:
        """API-306 — get appointment by id."""
        row = self._repo.get_by_id(appointment_id)
        if row is None:
            raise NotFoundError("Appointment not found")
        return _to_response(row)

    def get_active_summary(
        self, escalation_id: uuid.UUID
    ) -> AppointmentSummary | None:
        row = self._repo.get_active_by_escalation(escalation_id)
        if row is None:
            return None
        return to_summary(row)
