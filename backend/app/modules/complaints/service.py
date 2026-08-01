"""Complaint application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.enums import (
    INITIAL_COMPLAINT_STATUS,
    ComplaintReceiverType,
    ComplaintSourceType,
    ComplaintStatus,
    ComplaintTargetType,
    TimelineEvent,
)
from app.core.errors import NotFoundError, ValidationAppError
from app.core.status_transitions import can_transition
from app.core.user_messages import m
from app.models import Complaint
from app.modules.complaint_context import ComplaintContext, ComplaintContextService
from app.modules.complaint_events import (
    ComplaintEvent,
    ComplaintEventFactory,
    EventSourceRef,
    EventTargetRef,
)
from app.modules.complaints.repository import ComplaintRepository
from app.modules.complaints.schemas import (
    CloseComplaintRequest,
    CloseComplaintResult,
    ComplaintCreateRequest,
    ComplaintResponse,
    ComplaintStatusChangeRequest,
    ComplaintUpdateRequest,
)
from app.modules.event_dispatcher import DispatchResult, EventDispatcher
from app.modules.routing import ComplaintRoute, ComplaintRoutingService
from app.modules.sla.repository import SlaRepository
from app.modules.sla.service import SlaService

CLOSABLE_STATUS = ComplaintStatus.IN_PROGRESS
TARGET_CLOSED_STATUS = ComplaintStatus.CLOSED
NOT_IN_PROGRESS_FOR_CLOSE_MESSAGE = (
    m("complaint.must_be_in_progress_close")
)
ALREADY_CLOSED_MESSAGE = m("complaint.already_closed")
FINAL_RESOLUTION_REQUIRED_MESSAGE = (
    m("complaint.final_resolution_required_close")
)
ESCALATION_REQUIRED_MESSAGE = (
    m("escalation.must_exist_before_close_complaint")
)


def _generate_complaint_number() -> str:
    return f"CMP-{uuid.uuid4().hex[:10].upper()}"


def _to_response(complaint: Complaint) -> ComplaintResponse:
    return ComplaintResponse.model_validate(complaint)


def _snapshot(complaint: Complaint) -> dict[str, Any]:
    return {
        "id": str(complaint.id),
        "complaintNumber": complaint.complaint_number,
        "customerId": str(complaint.customer_id) if complaint.customer_id else None,
        "branchId": str(complaint.branch_id) if complaint.branch_id else None,
        "sourceType": complaint.source_type,
        "sourceId": str(complaint.source_id),
        "targetType": complaint.target_type,
        "targetId": str(complaint.target_id) if complaint.target_id else None,
        "subject": complaint.subject,
        "description": complaint.description,
        "status": complaint.status,
        "priority": complaint.priority,
        "channel": complaint.channel,
        "category": complaint.category,
        "reportedAt": complaint.reported_at.isoformat(),
        "closedAt": complaint.closed_at.isoformat() if complaint.closed_at else None,
        "closedBy": str(complaint.closed_by) if complaint.closed_by else None,
        "closureNotes": complaint.closure_notes,
        "createdAt": complaint.created_at.isoformat() if complaint.created_at else None,
        "createdBy": str(complaint.created_by) if complaint.created_by else None,
        "updatedAt": complaint.updated_at.isoformat() if complaint.updated_at else None,
        "updatedBy": str(complaint.updated_by) if complaint.updated_by else None,
    }


def _customer_id_from_source(
    source_type: ComplaintSourceType,
    source_id: uuid.UUID,
) -> uuid.UUID | None:
    """Project source onto legacy customer_id (not a routing decision)."""
    if source_type == ComplaintSourceType.CUSTOMER:
        return source_id
    return None


def _branch_id_from_route(route: ComplaintRoute) -> uuid.UUID | None:
    """Apply routing assignment_context for Assignment Engine consumers."""
    if route.receiver_type == ComplaintReceiverType.BRANCH:
        return route.receiver_id
    return None


def _event_source(complaint: Complaint) -> EventSourceRef:
    return EventSourceRef(
        source_type=complaint.source_type,
        source_id=complaint.source_id,
    )


def _event_target(complaint: Complaint) -> EventTargetRef:
    return EventTargetRef(
        target_type=complaint.target_type,
        target_id=complaint.target_id,
    )


# Status → factory method for Complaint Service–owned transitions (TASK-045).
_STATUS_EVENT_BUILDERS: dict[ComplaintStatus, Any] = {
    ComplaintStatus.ASSIGNED: ComplaintEventFactory.create_assigned,
    ComplaintStatus.IN_PROGRESS: ComplaintEventFactory.create_in_progress,
    ComplaintStatus.RESOLVED: ComplaintEventFactory.create_resolved,
    ComplaintStatus.CLOSED: ComplaintEventFactory.create_closed,
    ComplaintStatus.ESCALATED: ComplaintEventFactory.create_escalated,
}


class ComplaintService:
    def __init__(
        self,
        repository: ComplaintRepository,
        sla_service: SlaService | None = None,
        routing_service: ComplaintRoutingService | None = None,
        context_service: ComplaintContextService | None = None,
        event_dispatcher: EventDispatcher | None = None,
    ) -> None:
        self._repo = repository
        self._sla = sla_service or SlaService(SlaRepository(repository.session))
        self._routing = routing_service or ComplaintRoutingService()
        self._context = context_service or ComplaintContextService(
            repository.session,
            routing_service=self._routing,
            complaint_repository=repository,
        )
        # TASK-046 — producer dispatches; never knows registered consumers.
        self._dispatcher = event_dispatcher or EventDispatcher()
        # TASK-045 — in-memory diagnostic buffer; no bus / no persistence.
        self._recent_events: list[ComplaintEvent] = []
        self._last_dispatch_results: list[DispatchResult] = []

    def _route_for_event(self, complaint: Complaint) -> ComplaintRoute | None:
        """Best-effort route snapshot for events (does not mutate complaint)."""
        try:
            return self._routing.resolve_route(
                source_type=ComplaintSourceType(complaint.source_type),
                source_id=complaint.source_id,
                target_type=ComplaintTargetType(complaint.target_type),
                target_id=complaint.target_id,
            )
        except (ValidationAppError, ValueError):
            return None

    def _record_event(self, event: ComplaintEvent) -> ComplaintEvent:
        """Keep recent in-memory events for diagnostics; discard on process end."""
        self._recent_events.append(event)
        return event

    def _emit_lifecycle_event(
        self,
        builder: Any,
        complaint: Complaint,
        *,
        occurred_at: datetime,
        payload: dict[str, Any] | None = None,
        routing: ComplaintRoute | None = None,
    ) -> ComplaintEvent:
        """Create via factory, then dispatch in-process (producer ≠ consumer)."""
        route = routing if routing is not None else self._route_for_event(complaint)
        event = self._record_event(
            builder(
                complaint_id=complaint.id,
                complaint_number=complaint.complaint_number,
                current_status=complaint.status,
                priority=complaint.priority,
                source=_event_source(complaint),
                target=_event_target(complaint),
                routing=route,
                payload=payload,
                occurred_at=occurred_at,
            )
        )
        # Handler failures must not fail the business write path.
        result = self._dispatcher.dispatch(event)
        self._last_dispatch_results.append(result)
        return event

    def _validate_entities(self, payload: ComplaintCreateRequest) -> None:
        """Entity existence checks only — route rules live in RoutingService."""
        assert payload.source_type is not None
        assert payload.source_id is not None
        assert payload.target_type is not None

        if payload.source_type == ComplaintSourceType.CUSTOMER:
            if not self._repo.customer_exists(payload.source_id):
                raise ValidationAppError(
                    m("customer.not_found"),
                    details={"sourceId": str(payload.source_id)},
                )
        elif payload.source_type == ComplaintSourceType.BRANCH:
            if not self._repo.branch_exists(payload.source_id):
                raise ValidationAppError(
                    m("branch.not_found"),
                    details={"sourceId": str(payload.source_id)},
                )
        elif payload.source_type in {
            ComplaintSourceType.HEAD_OFFICE,
            ComplaintSourceType.SYSTEM,
        }:
            pass
        else:
            raise ValidationAppError(
                m("common.unsupported_source_type"),
                details={"sourceType": payload.source_type},
            )

        if payload.target_type == ComplaintTargetType.BRANCH:
            if payload.target_id is not None and not self._repo.branch_exists(
                payload.target_id
            ):
                raise ValidationAppError(
                    m("branch.not_found"),
                    details={"targetId": str(payload.target_id)},
                )
        elif payload.target_type == ComplaintTargetType.HEAD_OFFICE:
            pass
        else:
            raise ValidationAppError(
                m("common.unsupported_target_type"),
                details={"targetType": payload.target_type},
            )

        if (
            payload.customer_id is not None
            and payload.source_type == ComplaintSourceType.CUSTOMER
            and not self._repo.customer_exists(payload.customer_id)
        ):
            raise ValidationAppError(
                m("customer.not_found"),
                details={"customerId": str(payload.customer_id)},
            )
        if payload.branch_id is not None and not self._repo.branch_exists(
            payload.branch_id
        ):
            raise ValidationAppError(
                m("branch.not_found"),
                details={"branchId": str(payload.branch_id)},
            )

    def create(
        self,
        payload: ComplaintCreateRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ComplaintResponse:
        self._validate_entities(payload)

        assert payload.source_type is not None
        assert payload.source_id is not None
        assert payload.target_type is not None

        # TASK-043 — all destination decisions via Routing Foundation only.
        route = self._routing.resolve_route(
            source_type=payload.source_type,
            source_id=payload.source_id,
            target_type=payload.target_type,
            target_id=payload.target_id,
        )
        customer_id = _customer_id_from_source(
            payload.source_type, payload.source_id
        )
        branch_id = _branch_id_from_route(route)

        now = datetime.now(UTC)
        reported_at = payload.reported_at or now
        if reported_at.tzinfo is None:
            reported_at = reported_at.replace(tzinfo=UTC)

        complaint = Complaint(
            complaint_number=_generate_complaint_number(),
            customer_id=customer_id,
            branch_id=branch_id,
            source_type=payload.source_type.value,
            source_id=payload.source_id,
            target_type=payload.target_type.value,
            target_id=payload.target_id,
            subject=payload.subject,
            description=payload.description,
            status=INITIAL_COMPLAINT_STATUS,
            priority=payload.priority,
            channel=payload.channel,
            category=payload.category,
            reported_at=reported_at,
            created_at=now,
            updated_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._repo.add(complaint)
        # TASK-023 / DEC-012 — immutable deadline snapshot from active policy.
        # TASK-024 / DEC-013 — evaluate statuses at create (typically PENDING).
        self._sla.create_for_complaint(complaint.id, created_at=now, commit=False)
        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.create",
            entity_id=complaint.id,
            new_value={
                **_snapshot(complaint),
                "route": {
                    "receiverType": route.receiver_type.value,
                    "receiverId": (
                        str(route.receiver_id) if route.receiver_id else None
                    ),
                    "assignmentContext": dict(route.assignment_context),
                    "routingReason": route.routing_reason,
                },
            },
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.CREATED,
            event_at=now,
            from_status=None,
            to_status=INITIAL_COMPLAINT_STATUS,
            summary="Complaint created",
            metadata={
                "complaintNumber": complaint.complaint_number,
                "sourceType": complaint.source_type,
                "targetType": complaint.target_type,
                "receiverType": route.receiver_type.value,
                "receiverId": (
                    str(route.receiver_id) if route.receiver_id else None
                ),
                "routingReason": route.routing_reason,
            },
        )
        # TASK-045 — standardized in-memory domain event (no bus / no store).
        self._emit_lifecycle_event(
            ComplaintEventFactory.create_created,
            complaint,
            occurred_at=now,
            routing=route,
            payload={
                "actorUserId": str(actor_user_id),
                "changeType": "COMPLAINT_CREATED",
            },
        )
        self._repo.commit()
        self._repo.refresh(complaint)
        return _to_response(complaint)

    def get(self, complaint_id: uuid.UUID) -> ComplaintResponse:
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))
        return _to_response(complaint)

    def get_context(self, complaint_id: uuid.UUID) -> ComplaintContext:
        """Build ComplaintContext read model (TASK-044). No API surface yet."""
        return self._context.build_context(complaint_id)

    def refresh_context(self, complaint_id: uuid.UUID) -> ComplaintContext:
        """Refresh ComplaintContext from live data (TASK-044)."""
        return self._context.refresh_context(complaint_id)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        priority: str | None = None,
        customer_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
    ) -> tuple[list[ComplaintResponse], int]:
        if page < 1:
            raise ValidationAppError(m("config.page_min"), details={"page": page})
        if page_size < 1 or page_size > 100:
            raise ValidationAppError(
                m("config.page_size_range"),
                details={"pageSize": page_size},
            )

        items, total = self._repo.list_page(
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            customer_id=customer_id,
            branch_id=branch_id,
        )
        return [_to_response(item) for item in items], total

    def update(
        self,
        complaint_id: uuid.UUID,
        payload: ComplaintUpdateRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ComplaintResponse:
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        changes = payload.model_dump(exclude_unset=True)
        if "branch_id" in changes and changes["branch_id"] is not None:
            if not self._repo.branch_exists(changes["branch_id"]):
                raise ValidationAppError(
                    m("branch.not_found"),
                    details={"branchId": str(changes["branch_id"])},
                )

        old_value = _snapshot(complaint)
        old_priority = complaint.priority
        now = datetime.now(UTC)

        for field_name, value in changes.items():
            setattr(complaint, field_name, value)

        # Keep target polymorphic fields aligned when branchId is updated and
        # the complaint is still BRANCH-targeted (assignment context).
        if "branch_id" in changes and complaint.target_type == ComplaintTargetType.BRANCH:
            complaint.target_id = changes["branch_id"]

        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.update",
            entity_id=complaint.id,
            old_value=old_value,
            new_value=_snapshot(complaint),
            occurred_at=now,
        )

        # Priority change is a first-class timeline activity (TASK-008).
        if "priority" in changes and changes["priority"] != old_priority:
            self._repo.add_timeline(
                complaint_id=complaint.id,
                actor_user_id=actor_user_id,
                event_type=TimelineEvent.UPDATED,
                event_at=now,
                from_status=complaint.status,
                to_status=complaint.status,
                summary=f"Priority changed from {old_priority} to {complaint.priority}",
                metadata={
                    "changeType": "PRIORITY_CHANGED",
                    "fromPriority": old_priority,
                    "toPriority": complaint.priority,
                },
            )

        self._repo.commit()
        self._repo.refresh(complaint)
        return _to_response(complaint)

    def change_status(
        self,
        complaint_id: uuid.UUID,
        payload: ComplaintStatusChangeRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> ComplaintResponse:
        """Validated lifecycle transition — sole path for non-assign status changes."""
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        try:
            current = ComplaintStatus(complaint.status)
        except ValueError as exc:
            raise ValidationAppError(
                m("complaint.unsupported_status"),
                details={"status": complaint.status},
            ) from exc

        target = payload.status
        if current == target:
            raise ValidationAppError(
                m("common.invalid_status_transition"),
                details={
                    "fromStatus": current.value,
                    "toStatus": target.value,
                    "reason": "status unchanged",
                },
            )

        if not can_transition(current, target):
            raise ValidationAppError(
                m("common.invalid_status_transition"),
                details={
                    "fromStatus": current.value,
                    "toStatus": target.value,
                },
            )

        old_value = _snapshot(complaint)
        now = datetime.now(UTC)
        complaint.status = target
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        if target == ComplaintStatus.CLOSED:
            complaint.closed_at = now
            complaint.closed_by = actor_user_id
        elif target != ComplaintStatus.CLOSED:
            # Leaving RESOLVED/CLOSED (reopen) clears closure timestamp.
            if current in {ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED}:
                complaint.closed_at = None
                complaint.closed_by = None
                complaint.closure_notes = None

        if target == ComplaintStatus.RESOLVED:
            event_type: TimelineEvent = TimelineEvent.RESOLVED
        elif target == ComplaintStatus.CLOSED:
            event_type = TimelineEvent.CLOSED
        else:
            event_type = TimelineEvent.UPDATED

        summary = f"Status changed from {current.value} to {target.value}"
        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.status_change",
            entity_id=complaint.id,
            old_value=old_value,
            new_value=_snapshot(complaint),
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            event_at=now,
            from_status=current.value,
            to_status=target.value,
            summary=summary,
            metadata={
                "changeType": "STATUS_CHANGED",
                "fromStatus": current.value,
                "toStatus": target.value,
                "reason": payload.reason,
            },
        )
        # TASK-045 — emit lifecycle domain event for significant transitions.
        transition_payload = {
            "actorUserId": str(actor_user_id),
            "changeType": "STATUS_CHANGED",
            "fromStatus": current.value,
            "toStatus": target.value,
            "reason": payload.reason,
        }
        if (
            current == ComplaintStatus.ASSIGNED
            and target == ComplaintStatus.IN_PROGRESS
        ):
            # Assignee acceptance is modeled as Assigned → In Progress.
            self._emit_lifecycle_event(
                ComplaintEventFactory.create_accepted,
                complaint,
                occurred_at=now,
                payload=transition_payload,
            )
        builder = _STATUS_EVENT_BUILDERS.get(target)
        if builder is not None:
            self._emit_lifecycle_event(
                builder,
                complaint,
                occurred_at=now,
                payload=transition_payload,
            )
        self._repo.commit()
        self._repo.refresh(complaint)
        return _to_response(complaint)

    def close(
        self,
        complaint_id: uuid.UUID,
        payload: CloseComplaintRequest,
        *,
        actor_user_id: uuid.UUID,
    ) -> CloseComplaintResult:
        """API-312 — Explicit Complaint Closure after Final Resolution (TASK-019)."""
        complaint = self._repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))

        if complaint.status == ComplaintStatus.CLOSED or complaint.closed_at is not None:
            raise ValidationAppError(
                ALREADY_CLOSED_MESSAGE,
                details={"status": complaint.status},
            )

        if complaint.status != CLOSABLE_STATUS:
            raise ValidationAppError(
                NOT_IN_PROGRESS_FOR_CLOSE_MESSAGE,
                details={"status": complaint.status},
            )

        final_resolution = self._repo.get_final_resolution(complaint_id)
        if final_resolution is None:
            raise ValidationAppError(
                FINAL_RESOLUTION_REQUIRED_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        escalation = self._repo.get_latest_escalation(complaint_id)
        if escalation is None:
            raise ValidationAppError(
                ESCALATION_REQUIRED_MESSAGE,
                details={"complaintId": str(complaint_id)},
            )

        closer = self._repo.get_user(actor_user_id)
        if closer is None:
            raise ValidationAppError(
                m("complaint.closer_not_found"),
                details={"closedBy": str(actor_user_id)},
            )

        from_status = complaint.status
        escalation_status_before = escalation.status
        now = datetime.now(UTC)

        complaint.status = TARGET_CLOSED_STATUS
        complaint.closed_at = now
        complaint.closed_by = actor_user_id
        complaint.closure_notes = payload.notes
        complaint.updated_at = now
        complaint.updated_by = actor_user_id

        # Escalation remains as-is — do NOT close escalation.
        escalation.updated_at = now
        escalation.updated_by = actor_user_id

        self._repo.add_audit_log(
            actor_user_id=actor_user_id,
            action="complaint.close",
            entity_id=complaint.id,
            new_value={
                "complaintId": str(complaint.id),
                "status": TARGET_CLOSED_STATUS.value,
                "closedAt": now.isoformat(),
                "closedBy": str(actor_user_id),
                "closureNotes": payload.notes,
                "escalationId": str(escalation.id),
                "escalationStatus": escalation.status,
            },
            occurred_at=now,
        )
        self._repo.add_timeline(
            complaint_id=complaint.id,
            actor_user_id=actor_user_id,
            event_type=TimelineEvent.CLOSED,
            event_at=now,
            from_status=from_status,
            to_status=TARGET_CLOSED_STATUS.value,
            summary="Complaint closed",
            metadata={
                "changeType": "COMPLAINT_CLOSED",
                "complaintId": str(complaint.id),
                "escalationId": str(escalation.id),
                "closedBy": str(actor_user_id),
                "closedAt": now.isoformat(),
            },
        )

        assert complaint.status == ComplaintStatus.CLOSED
        assert escalation.status == escalation_status_before

        # TASK-045 — in-memory ComplaintClosed (API-312 path).
        self._emit_lifecycle_event(
            ComplaintEventFactory.create_closed,
            complaint,
            occurred_at=now,
            payload={
                "actorUserId": str(actor_user_id),
                "changeType": "COMPLAINT_CLOSED",
                "escalationId": str(escalation.id),
                "closureNotes": payload.notes,
            },
        )

        # TASK-024 — evaluate overall (and other) SLA statuses after close.
        from app.modules.sla.hooks import evaluate_sla_for_complaint

        evaluate_sla_for_complaint(self._repo.session, complaint.id, now=now)

        result = CloseComplaintResult(
            complaintId=complaint.id,
            status=TARGET_CLOSED_STATUS,
            closedAt=now,
            closedBy=actor_user_id,
        )
        self._repo.commit()
        return result
