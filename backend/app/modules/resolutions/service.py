"""Resolution application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import ComplaintStatus, TimelineEvent
from app.core.errors import NotFoundError, ValidationAppError
from app.models import ComplaintResolution
from app.modules.resolutions.repository import ResolutionRepository
from app.modules.resolutions.schemas import (
    ResolutionResponse,
    ResolveComplaintRequest,
    ResolveComplaintResult,
)

RESOLVABLE_STATUS = ComplaintStatus.IN_PROGRESS
TARGET_STATUS = ComplaintStatus.RESOLVED
NOT_IN_PROGRESS_MESSAGE = "Complaint must be IN_PROGRESS before resolving."


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


class ResolutionService:
    def __init__(self, repository: ResolutionRepository) -> None:
        self._repo = repository

    def get_current(self, complaint_id: uuid.UUID) -> ResolutionResponse | None:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")
        current = self._repo.get_current_resolution(complaint_id)
        if current is None:
            return None
        return _to_response(current)

    def resolve(
        self,
        complaint_id: uuid.UUID,
        payload: ResolveComplaintRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ResolveComplaintResult:
        complaint = self._repo.get_complaint(complaint_id)
        if complaint is None:
            raise NotFoundError("Complaint not found")

        if complaint.status != RESOLVABLE_STATUS:
            raise ValidationAppError(
                NOT_IN_PROGRESS_MESSAGE,
                details={"status": complaint.status},
            )

        resolved_by = payload.resolved_by or actor_user_id
        if payload.resolved_by is not None and payload.resolved_by != actor_user_id:
            raise ValidationAppError(
                "resolvedBy must match the authenticated user",
                details={
                    "resolvedBy": str(payload.resolved_by),
                    "actorUserId": str(actor_user_id),
                },
            )

        resolver = self._repo.get_user(resolved_by)
        if resolver is None:
            raise ValidationAppError(
                "Resolver not found or inactive",
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
        result = ResolveComplaintResult(
            resolution=_to_response(resolution),
            complaintId=complaint.id,
            status=TARGET_STATUS,
        )
        self._repo.commit()
        return result
