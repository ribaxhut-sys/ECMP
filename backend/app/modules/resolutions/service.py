"""Resolution application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import (
    AppointmentStatus,
    ComplaintStatus,
    EscalationRequestStatus,
    FinalResolutionStatus,
    TimelineEvent,
)
from app.core.errors import NotFoundError, ValidationAppError
from app.models import ComplaintResolution
from app.modules.resolutions.repository import ResolutionRepository
from app.modules.resolutions.schemas import (
    FinalResolutionRequest,
    FinalResolutionResponse,
    FinalResolutionResult,
    ResolutionResponse,
    ResolveComplaintRequest,
    ResolveComplaintResult,
)
from app.core.user_messages import m

RESOLVABLE_STATUS = ComplaintStatus.IN_PROGRESS
TARGET_STATUS = ComplaintStatus.RESOLVED
NOT_IN_PROGRESS_MESSAGE = m("complaint.must_be_in_progress_resolve")

FINAL_RESOLUTION_ELIGIBLE_STATUS = ComplaintStatus.IN_PROGRESS
NOT_IN_PROGRESS_FOR_FINAL_MESSAGE = (
    m("complaint.must_be_in_progress_final")
)
APPOINTMENT_NOT_COMPLETED_MESSAGE = (
    m("appointment.must_be_completed_for_final_resolution")
)
APPOINTMENT_NO_SHOW_MESSAGE = (
    m("resolution.not_allowed_no_show")
)
APPOINTMENT_REQUIRED_MESSAGE = (
    m("appointment.required_before_final_resolution")
)
ALREADY_FINAL_RESOLUTION_MESSAGE = m("resolution.already_submitted")
# Placeholder category for resolution-row scaffolding (complaint stays IN_PROGRESS).
_FINAL_RESOLUTION_CATEGORY = "SOLVED"


def _to_response(resolution: ComplaintResolution) -> ResolutionResponse:
    resolver = resolution.__dict__.get("resolver")
    resolved_by_name = (
        getattr(resolver, "full_name", None) if resolver is not None else None
    )
    return ResolutionResponse(
        id=resolution.id,
        complaintId=resolution.complaint_id,
        resolutionCategory=resolution.resolution_category,  # type: ignore[arg-type]
        rootCause=resolution.root_cause,
        resolutionNotes=resolution.resolution_notes,
        resolvedBy=resolution.resolved_by,
        resolvedByName=resolved_by_name,
        resolvedAt=resolution.resolved_at,
        isCurrent=resolution.is_current,
    )


def _to_final_response(resolution: ComplaintResolution) -> FinalResolutionResponse:
    final_resolver = resolution.__dict__.get("final_resolver")
    submitted_by_name = (
        getattr(final_resolver, "full_name", None)
        if final_resolver is not None
        else None
    )
    assert resolution.final_resolution_at is not None
    assert resolution.final_resolution_by is not None
    assert resolution.final_resolution_summary is not None
    assert resolution.final_resolution_notes is not None
    return FinalResolutionResponse(
        complaintId=resolution.complaint_id,
        status=FinalResolutionStatus.FINAL_RESOLUTION_SUBMITTED,
        summary=resolution.final_resolution_summary,
        notes=resolution.final_resolution_notes,
        followUpRequired=resolution.follow_up_required,
        submittedAt=resolution.final_resolution_at,
        submittedBy=resolution.final_resolution_by,
        submittedByName=submitted_by_name,
    )


class ResolutionService:
    def __init__(self, repository: ResolutionRepository) -> None:
        self._repo = repository

    def get_current(self, complaint_id: uuid.UUID) -> ResolutionResponse | None:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))
        current = self._repo.get_current_resolution(complaint_id)
        if current is None:
            return None
        return _to_response(current)

    def get_final_resolution(
        self, complaint_id: uuid.UUID
    ) -> FinalResolutionResponse | None:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))
        row = self._repo.get_final_resolution(complaint_id)
        if row is None:
            return None
        return _to_final_response(row)

    def resolve(
        self,
        complaint_id: uuid.UUID,
        payload: ResolveComplaintRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ResolveComplaintResult:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        if complaint.status != RESOLVABLE_STATUS:
            raise ValidationAppError(
                NOT_IN_PROGRESS_MESSAGE,
                details={"status": complaint.status},
            )

        resolved_by = payload.resolved_by or actor_user_id
        if payload.resolved_by is not None and payload.resolved_by != actor_user_id:
            raise ValidationAppError(
                m("resolution.resolved_by_must_match_user"),
                details={
                    "resolvedBy": str(payload.resolved_by),
                    "actorUserId": str(actor_user_id),
                },
            )

        resolver = self._repo.get_user(resolved_by)
        if resolver is None:
            raise ValidationAppError(
                m("resolution.resolver_not_found"),
                details={"resolvedBy": str(resolved_by)},
            )

        now = datetime.now(UTC)
        from_status = complaint.status

        current = self._repo.get_current_resolution(complaint_id)
        if current is not None:
            self._repo.close_current_resolution(
                current,
                actor_user_id=actor_user_id,
                when=now,
            )

        resolution = ComplaintResolution(
            complaint_id=complaint.id,
            resolution_category=payload.resolution_category,
            root_cause=payload.root_cause,
            resolution_notes=payload.resolution_notes,
            resolved_by=resolved_by,
            resolved_at=now,
            is_current=True,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        # Attach resolver for response display name without extra query.
        resolution.resolver = resolver
        self._repo.add_resolution(resolution)

        complaint.status = TARGET_STATUS
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.resolve",
            entity_id=complaint.id,
            new_value={
                "complaintId": str(complaint.id),
                "status": TARGET_STATUS.value,
                "resolutionCategory": payload.resolution_category,
                "rootCause": payload.root_cause,
                "resolutionNotes": payload.resolution_notes,
                "resolvedBy": str(resolved_by),
                "resolvedAt": now.isoformat(),
            },
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.RESOLVED,
            event_at=now,
            from_status=from_status,
            to_status=TARGET_STATUS.value,
            summary="Complaint resolved",
            metadata={
                "changeType": "RESOLVED",
                "resolutionCategory": payload.resolution_category,
                "rootCause": payload.root_cause,
                "resolvedBy": str(resolved_by),
            },
        )

        # TASK-024 — evaluate resolution (and other) SLA statuses.
        from app.modules.sla.hooks import evaluate_sla_for_complaint

        evaluate_sla_for_complaint(self._repo.session, complaint.id, now=now)

        result = ResolveComplaintResult(
            resolution=_to_response(resolution),
            complaintId=complaint.id,
            status=TARGET_STATUS,
        )
        self._repo.commit()
        return result

    def submit_final_resolution(
        self,
        complaint_id: uuid.UUID,
        payload: FinalResolutionRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> FinalResolutionResult:
        """API-310 — Final Resolution after appointment COMPLETED (DEC-011)."""
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        if complaint.status != FINAL_RESOLUTION_ELIGIBLE_STATUS:
            raise ValidationAppError(
                NOT_IN_PROGRESS_FOR_FINAL_MESSAGE,
                details={"status": complaint.status},
            )

        existing = self._repo.get_final_resolution(complaint_id)
        if existing is not None:
            raise ValidationAppError(
                ALREADY_FINAL_RESOLUTION_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        appointment = self._repo.get_latest_appointment_for_complaint(complaint_id)
        if appointment is None:
            raise ValidationAppError(
                APPOINTMENT_REQUIRED_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        if (
            appointment.status == AppointmentStatus.NO_SHOW
            or appointment.no_show_at is not None
        ):
            raise ValidationAppError(
                APPOINTMENT_NO_SHOW_MESSAGE,
                details={
                    "appointmentId": str(appointment.id),
                    "status": appointment.status,
                },
            )

        if (
            appointment.status != AppointmentStatus.COMPLETED
            or appointment.completed_at is None
        ):
            raise ValidationAppError(
                APPOINTMENT_NOT_COMPLETED_MESSAGE,
                details={
                    "appointmentId": str(appointment.id),
                    "status": appointment.status,
                },
            )

        escalation = self._repo.get_escalation(appointment.escalation_id)
        if escalation is None:
            raise NotFoundError(m("escalation.not_found"))

        submitter = self._repo.get_user(actor_user_id)
        if submitter is None:
            raise ValidationAppError(
                m("complaint.submitter_not_found"),
                details={"submittedBy": str(actor_user_id)},
            )

        now = datetime.now(UTC)
        current = self._repo.get_current_resolution(complaint_id)

        if current is not None:
            current.final_resolution_at = now
            current.final_resolution_by = actor_user_id
            current.final_resolution_summary = payload.summary
            current.final_resolution_notes = payload.notes
            current.follow_up_required = payload.follow_up_required
            current.updated_at = now
            current.updated_by = actor_user_id
            current.final_resolver = submitter
            resolution = current
        else:
            # Scaffold row holds Final Resolution only; is_current=False so it does
            # not appear as TASK-010 current resolution while complaint stays IN_PROGRESS.
            resolution = ComplaintResolution(
                complaint_id=complaint.id,
                resolution_category=_FINAL_RESOLUTION_CATEGORY,
                root_cause=payload.summary[:500],
                resolution_notes=payload.notes,
                resolved_by=actor_user_id,
                resolved_at=now,
                is_current=False,
                final_resolution_at=now,
                final_resolution_by=actor_user_id,
                final_resolution_summary=payload.summary,
                final_resolution_notes=payload.notes,
                follow_up_required=payload.follow_up_required,
                created_at=now,
                updated_at=now,
                created_by=actor_user_id,
                updated_by=actor_user_id,
            )
            resolution.final_resolver = submitter
            self._repo.add_resolution(resolution)

        # Complaint remains IN_PROGRESS; escalation remains APPROVED.
        # Do NOT close complaint or escalation.
        complaint.updated_at = now
        complaint.updated_by = actor_user_id
        escalation.updated_at = now
        escalation.updated_by = actor_user_id

        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.final_resolution",
            entity_id=complaint.id,
            new_value={
                "complaintId": str(complaint.id),
                "status": FinalResolutionStatus.FINAL_RESOLUTION_SUBMITTED.value,
                "complaintStatus": complaint.status,
                "escalationStatus": escalation.status,
                "appointmentId": str(appointment.id),
                "escalationId": str(escalation.id),
                "summary": payload.summary,
                "notes": payload.notes,
                "followUpRequired": payload.follow_up_required,
                "submittedBy": str(actor_user_id),
                "submittedAt": now.isoformat(),
            },
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.FINAL_RESOLUTION_SUBMITTED,
            event_at=now,
            from_status=complaint.status,
            to_status=complaint.status,
            summary="Final resolution submitted",
            metadata={
                "changeType": "FINAL_RESOLUTION_SUBMITTED",
                "complaintId": str(complaint.id),
                "appointmentId": str(appointment.id),
                "escalationId": str(escalation.id),
                "submittedBy": str(actor_user_id),
                "submittedAt": now.isoformat(),
                "followUpRequired": payload.follow_up_required,
            },
        )

        assert complaint.status == ComplaintStatus.IN_PROGRESS
        assert escalation.status == EscalationRequestStatus.APPROVED

        # TASK-024 — evaluate resolution (and other) SLA statuses.
        from app.modules.sla.hooks import evaluate_sla_for_complaint

        evaluate_sla_for_complaint(self._repo.session, complaint.id, now=now)

        result = FinalResolutionResult(
            complaintId=complaint.id,
            status=FinalResolutionStatus.FINAL_RESOLUTION_SUBMITTED,
            submittedAt=now,
            submittedBy=actor_user_id,
        )
        self._repo.commit()
        return result
