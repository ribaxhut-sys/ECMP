"""Appointment application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import (
    AppointmentStatus,
    EscalationRequestStatus,
    TimelineEvent,
)
from app.core.errors import NotFoundError, ValidationAppError
from app.models import Appointment
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
    AppointmentSummary,
)
from app.core.user_messages import m

NOT_APPROVED_MESSAGE = m("escalation.must_be_approved_for_booking")
HAS_ACTIVE_APPOINTMENT_MESSAGE = m("escalation.has_active_appointment")
ENGINEER_NOT_FOUND_MESSAGE = m("appointment.engineer_not_found")
OVERLAP_MESSAGE = m("appointment.overlap_booking")
NOT_BOOKED_MESSAGE = m("appointment.only_booked_check_in")
ALREADY_CHECKED_IN_MESSAGE = m("appointment.already_checked_in")
NOT_CHECKED_IN_MESSAGE = m("appointment.only_checked_in_complete")
ALREADY_COMPLETED_MESSAGE = m("appointment.already_completed")
NOT_BOOKED_FOR_NO_SHOW_MESSAGE = m("appointment.only_booked_no_show")
ALREADY_NO_SHOW_MESSAGE = m("appointment.already_no_show")
NO_SHOW_AFTER_CHECK_IN_MESSAGE = (
    m("appointment.no_show_already_checked_in")
)
NO_SHOW_AFTER_COMPLETED_MESSAGE = (
    m("appointment.no_show_already_completed")
)


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
            raise NotFoundError(m("escalation.not_found"))

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
            raise NotFoundError(m("complaint.not_found"))

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

    def check_in(
        self,
        appointment_id: uuid.UUID,
        payload: AppointmentCheckInRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> AppointmentCheckInResult:
        """API-307 — customer check-in for BOOKED appointment."""
        row = self._repo.get_by_id(appointment_id)
        if row is None:
            raise NotFoundError(m("appointment.not_found"))

        if row.status == AppointmentStatus.CHECKED_IN or row.checked_in_at is not None:
            raise ValidationAppError(
                ALREADY_CHECKED_IN_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )
        if row.status != AppointmentStatus.BOOKED:
            raise ValidationAppError(
                NOT_BOOKED_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )

        escalation = self._repo.get_escalation(row.escalation_id)
        if escalation is None:
            raise NotFoundError(m("escalation.not_found"))

        complaint = self._repo.get_complaint(escalation.complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        now = datetime.now(UTC)
        row.status = AppointmentStatus.CHECKED_IN
        row.checked_in_at = now
        row.checked_in_by = actor_user_id
        row.checkin_notes = payload.notes
        row.updated_at = now
        row.updated_by = actor_user_id

        # Complaint remains IN_PROGRESS; escalation remains APPROVED.
        complaint.updated_at = now
        complaint.updated_by = actor_user_id
        escalation.updated_at = now
        escalation.updated_by = actor_user_id

        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.APPOINTMENT_CHECKED_IN,
            event_at=now,
            from_status=complaint.status,
            to_status=complaint.status,
            summary="Customer checked in",
            metadata={
                "changeType": "APPOINTMENT_CHECKED_IN",
                "appointmentId": str(row.id),
                "escalationId": str(escalation.id),
                "checkedInBy": str(actor_user_id),
                "checkedInAt": now.isoformat(),
            },
        )

        result = AppointmentCheckInResult(
            id=row.id,
            status=AppointmentStatus.CHECKED_IN,
            checkedInAt=now,
            checkedInBy=actor_user_id,
        )
        self._repo.commit()
        return result

    def complete(
        self,
        appointment_id: uuid.UUID,
        payload: AppointmentCompleteRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> AppointmentCompleteResult:
        """API-308 — complete CHECKED_IN appointment."""
        row = self._repo.get_by_id(appointment_id)
        if row is None:
            raise NotFoundError(m("appointment.not_found"))

        if row.status == AppointmentStatus.COMPLETED or row.completed_at is not None:
            raise ValidationAppError(
                ALREADY_COMPLETED_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )
        if row.status != AppointmentStatus.CHECKED_IN:
            raise ValidationAppError(
                NOT_CHECKED_IN_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )

        escalation = self._repo.get_escalation(row.escalation_id)
        if escalation is None:
            raise NotFoundError(m("escalation.not_found"))

        complaint = self._repo.get_complaint(escalation.complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        now = datetime.now(UTC)
        row.status = AppointmentStatus.COMPLETED
        row.completed_at = now
        row.completed_by = actor_user_id
        row.completion_notes = payload.notes
        row.completion_result = payload.result
        row.updated_at = now
        row.updated_by = actor_user_id

        # Complaint remains IN_PROGRESS; escalation remains APPROVED.
        # Do NOT auto-close complaint or escalation.
        complaint.updated_at = now
        complaint.updated_by = actor_user_id
        escalation.updated_at = now
        escalation.updated_by = actor_user_id

        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.APPOINTMENT_COMPLETED,
            event_at=now,
            from_status=complaint.status,
            to_status=complaint.status,
            summary="Appointment completed",
            metadata={
                "changeType": "APPOINTMENT_COMPLETED",
                "appointmentId": str(row.id),
                "escalationId": str(escalation.id),
                "completedBy": str(actor_user_id),
                "completedAt": now.isoformat(),
                "completionResult": payload.result,
            },
        )

        # TASK-024 — evaluate appointment (and other) SLA statuses.
        from app.modules.sla.hooks import evaluate_sla_for_complaint

        evaluate_sla_for_complaint(self._repo.session, complaint.id, now=now)

        result = AppointmentCompleteResult(
            id=row.id,
            status=AppointmentStatus.COMPLETED,
            completionResult=payload.result,
            completedAt=now,
            completedBy=actor_user_id,
        )
        self._repo.commit()
        return result

    def mark_no_show(
        self,
        appointment_id: uuid.UUID,
        payload: AppointmentNoShowRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> AppointmentNoShowResult:
        """API-309 — mark BOOKED appointment as customer no-show."""
        row = self._repo.get_by_id(appointment_id)
        if row is None:
            raise NotFoundError(m("appointment.not_found"))

        if row.status == AppointmentStatus.NO_SHOW or row.no_show_at is not None:
            raise ValidationAppError(
                ALREADY_NO_SHOW_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )
        if (
            row.status == AppointmentStatus.COMPLETED
            or row.completed_at is not None
        ):
            raise ValidationAppError(
                NO_SHOW_AFTER_COMPLETED_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )
        if (
            row.status == AppointmentStatus.CHECKED_IN
            or row.checked_in_at is not None
        ):
            raise ValidationAppError(
                NO_SHOW_AFTER_CHECK_IN_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )
        if row.status != AppointmentStatus.BOOKED:
            raise ValidationAppError(
                NOT_BOOKED_FOR_NO_SHOW_MESSAGE,
                details={"status": row.status, "appointmentId": str(row.id)},
            )

        escalation = self._repo.get_escalation(row.escalation_id)
        if escalation is None:
            raise NotFoundError(m("escalation.not_found"))

        complaint = self._repo.get_complaint(escalation.complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        now = datetime.now(UTC)
        row.status = AppointmentStatus.NO_SHOW
        row.no_show_at = now
        row.no_show_by = actor_user_id
        row.no_show_reason = payload.reason
        row.updated_at = now
        row.updated_by = actor_user_id

        # Complaint remains IN_PROGRESS; escalation remains APPROVED.
        # Do NOT auto-close complaint or escalation.
        complaint.updated_at = now
        complaint.updated_by = actor_user_id
        escalation.updated_at = now
        escalation.updated_by = actor_user_id

        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.APPOINTMENT_NO_SHOW,
            event_at=now,
            from_status=complaint.status,
            to_status=complaint.status,
            summary="Customer marked as no-show",
            metadata={
                "changeType": "APPOINTMENT_NO_SHOW",
                "appointmentId": str(row.id),
                "escalationId": str(escalation.id),
                "noShowBy": str(actor_user_id),
                "noShowAt": now.isoformat(),
                "reason": payload.reason,
            },
        )

        result = AppointmentNoShowResult(
            id=row.id,
            status=AppointmentStatus.NO_SHOW,
            noShowAt=now,
            noShowBy=actor_user_id,
        )
        self._repo.commit()
        return result

    def get_appointment(self, appointment_id: uuid.UUID) -> AppointmentResponse:
        """API-306 — get appointment by id."""
        row = self._repo.get_by_id(appointment_id)
        if row is None:
            raise NotFoundError(m("appointment.not_found"))
        return _to_response(row)

    def get_active_summary(
        self, escalation_id: uuid.UUID
    ) -> AppointmentSummary | None:
        row = self._repo.get_active_by_escalation(escalation_id)
        if row is None:
            return None
        return to_summary(row)
