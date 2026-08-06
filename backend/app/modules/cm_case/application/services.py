"""Application service — CAP-008 Mode A Case use cases (Epic 4).

No Notification / Assignment / SLA / Event engines. Audit + Complaint Timeline only.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService
from app.modules.cm_case.application.dto import (
    AddCaseCommand,
    CaseDTO,
    CaseSummaryDTO,
    CloseCaseCommand,
    CreateCaseCommand,
    ResolutionDTO,
    ResolveCaseCommand,
    UpdateStatusCommand,
)
from app.modules.cm_case.application.visibility import (
    DEFAULT_PUSAT_UNIT_CODES,
    resolve_case_visibility,
)
from app.core.authorization.principal import Principal
from app.modules.cm_case.domain import errors as err
from app.modules.cm_case.domain.aggregate import CaseAggregate, ResolutionRecord
from app.modules.cm_case.domain.repositories import CaseRepository
from app.modules.cm_case.domain.value_objects import (
    MAX_CASES_PER_COMPLAINT,
    CaseNumber,
    ResolveAction,
)
from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.domain.enums import ActorType, AggregateType
from app.modules.timeline.repository import TimelineRepository


class SideEffects(Protocol):
    def record_case_event(
        self,
        *,
        case: CaseAggregate,
        event_name: str,
        title: str,
        actor_id: str,
        before: dict | None = None,
        after: dict | None = None,
    ) -> None: ...


class NoOpSideEffects:
    def record_case_event(
        self,
        *,
        case: CaseAggregate,
        event_name: str,
        title: str,
        actor_id: str,
        before: dict | None = None,
        after: dict | None = None,
    ) -> None:
        _ = (case, event_name, title, actor_id, before, after)


class AuditTimelineSideEffects:
    """BR-016 / BR-017 via existing Audit + Timeline (Complaint stream). No Event Engine."""

    def __init__(
        self,
        session,
        *,
        audit: AuditService | None = None,
        timeline: TimelineRepository | None = None,
    ) -> None:
        self._audit = audit or AuditService(AuditRepository(session))
        self._timeline = timeline or TimelineRepository(session)

    def record_case_event(
        self,
        *,
        case: CaseAggregate,
        event_name: str,
        title: str,
        actor_id: str,
        before: dict | None = None,
        after: dict | None = None,
    ) -> None:
        actor_uuid: UUID | None = None
        try:
            actor_uuid = UUID(actor_id)
        except ValueError:
            actor_uuid = None

        self._audit.log(
            event_type=event_name,
            entity_type="Case",
            action="CREATE" if event_name == "CaseCreated" else "UPDATE",
            entity_id=case.case_id,
            actor_id=actor_uuid,
            old_values=before,
            new_values=after or case.to_snapshot(),
            metadata={
                "complaintId": case.complaint_id,
                "caseNumber": case.case_number.value,
                "domainEvent": event_name,
            },
            commit=False,
        )

        try:
            complaint_uuid = UUID(case.complaint_id)
        except ValueError:
            return

        entry = TimelineEntry.create(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=complaint_uuid,
            event_type=event_name,
            title=title,
            description=f"Case {case.case_number.value} — {case.status.value}",
            actor_type=ActorType.USER.value,
            actor_id=actor_id,
            metadata={
                "caseId": str(case.case_id),
                "caseNumber": case.case_number.value,
                "caseStatus": case.status.value,
            },
        )
        self._timeline.add(entry)


def _resolution_dto(r: ResolutionRecord) -> ResolutionDTO:
    return ResolutionDTO(
        resolution_id=r.resolution_id,
        resolution_code=r.resolution_code,
        summary=r.summary,
        status=r.status.value,
        comment=r.comment,
        detail=r.detail,
        customer_impact=r.customer_impact,
        attachment_ids=list(r.attachment_ids),
        proposed_by=r.proposed_by,
        proposed_at=r.proposed_at,
        decided_by=r.decided_by,
        decided_at=r.decided_at,
        rejection_reason=r.rejection_reason,
    )


def to_case_dto(case: CaseAggregate) -> CaseDTO:
    return CaseDTO(
        case_id=str(case.case_id),
        case_number=case.case_number.value,
        complaint_id=case.complaint_id,
        customer_id=case.customer_id,
        status=case.status.value,
        case_type=case.case_type,
        subject=case.subject,
        description=case.description,
        priority=case.priority,
        created_at=case.created_at,
        created_by=case.created_by,
        category=case.category,
        owning_unit_id=case.owning_unit_id,
        assigned_user_id=None,
        sla_policy_version_id=case.sla_policy_version_id,
        sla_countdown_active=False,
        cancel_reason=case.cancel_reason.value if case.cancel_reason else None,
        closed_by=case.closed_by,
        closed_at=case.closed_at,
        updated_at=case.updated_at,
        resolution=_resolution_dto(case.resolution) if case.resolution else None,
        resolution_history=[_resolution_dto(r) for r in case.resolution_history],
        complaint_status_after_create=case.complaint_status_after_create,
    )


class CaseApplicationService:
    def __init__(
        self,
        repository: CaseRepository,
        *,
        side_effects: SideEffects | None = None,
    ) -> None:
        self._repo = repository
        self._effects = side_effects or NoOpSideEffects()

    def create_case(self, cmd: CreateCaseCommand) -> CaseDTO:
        return self._create_under_complaint(cmd)

    def add_case(self, cmd: AddCaseCommand) -> CaseDTO:
        return self._create_under_complaint(
            CreateCaseCommand(
                complaint_id=cmd.complaint_id,
                case_type=cmd.case_type,
                subject=cmd.subject,
                description=cmd.description,
                priority=cmd.priority,
                category=cmd.category,
                destination_unit_id=cmd.destination_unit_id,
                assigned_user_id=cmd.assigned_user_id,
                sla_policy_version_id=cmd.sla_policy_version_id,
                actor_id=cmd.actor_id,
            )
        )

    def _create_under_complaint(self, cmd: CreateCaseCommand) -> CaseDTO:
        if cmd.assigned_user_id:
            raise err.conflict(
                "ASSIGNED_USER_NOT_ALLOWED_MODE_A",
                "Assigned User is outside Mode A (BQ-006).",
            )
        for field_name, value in (
            ("caseType", cmd.case_type),
            ("subject", cmd.subject),
            ("description", cmd.description),
            ("priority", cmd.priority),
            ("complaintId", cmd.complaint_id),
        ):
            if not (value or "").strip():
                raise err.validation(
                    f"{field_name} is required",
                    details={"field": field_name},
                )

        parent = self._repo.get_parent_complaint(cmd.complaint_id)
        if parent is None:
            raise err.not_found("Parent Complaint does not exist.")
        if parent.status == "CLOSED":
            raise err.conflict(
                "COMPLAINT_CLOSED",
                "Create Case on CLOSED Complaint is rejected.",
            )
        if parent.case_count >= MAX_CASES_PER_COMPLAINT:
            raise err.conflict(
                "MAX_CASES_EXCEEDED",
                "Maximum 5 Cases per Complaint reached (BQ-003).",
            )

        year = datetime.now(UTC).year
        number = CaseNumber(self._repo.next_case_number(year))
        first_case = parent.case_count == 0 and parent.status == "REGISTERED"
        case = CaseAggregate.create(
            complaint_id=parent.complaint_id,
            customer_id=parent.customer_id,
            case_number=number,
            case_type=cmd.case_type,
            subject=cmd.subject,
            description=cmd.description,
            priority=cmd.priority,
            created_by=cmd.actor_id,
            category=cmd.category,
            destination_unit_id=cmd.destination_unit_id,
            sla_policy_version_id=cmd.sla_policy_version_id or "MODE-A-BIND-ONLY",
            complaint_became_in_progress=first_case,
        )
        self._repo.save(case)
        if first_case or parent.case_count == 0:
            self._repo.mark_complaint_in_progress(parent.complaint_id)
            if first_case:
                case.complaint_status_after_create = "IN_PROGRESS"
        self._effects.record_case_event(
            case=case,
            event_name="CaseCreated",
            title="Case Created",
            actor_id=cmd.actor_id,
            after=case.to_snapshot(),
        )
        self._repo.commit()
        return to_case_dto(case)

    def get_case(
        self, case_id: str, *, complaint_id_context: str | None = None
    ) -> CaseDTO:
        case = self._repo.get(case_id)
        if case is None:
            raise err.not_found("Case does not exist.")
        if complaint_id_context:
            ctx = complaint_id_context.strip()
            parent = self._repo.get_parent_complaint(ctx)
            if parent is None:
                if case.complaint_id != ctx:
                    raise err.conflict(
                        "CASE_COMPLAINT_MEMBERSHIP_MISMATCH",
                        "CaseId is not a member of the supplied Complaint context.",
                    )
            elif case.complaint_id != parent.complaint_id:
                raise err.conflict(
                    "CASE_COMPLAINT_MEMBERSHIP_MISMATCH",
                    "CaseId is not a member of the supplied Complaint context.",
                )
        return to_case_dto(case)

    def list_cases(
        self,
        principal: Principal,
        *,
        page: int = 1,
        page_size: int = 20,
        complaint_id: str | None = None,
        status: str | None = None,
    ) -> tuple[list[CaseSummaryDTO], int]:
        visibility = resolve_case_visibility(principal)
        rows, total = self._repo.list_summaries(
            visibility=visibility.value,
            actor_id=str(principal.user_id),
            org_unit_id=principal.org_unit_id,
            pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
            complaint_id=complaint_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        items = [
            CaseSummaryDTO(
                case_id=str(row.id),
                case_number=row.case_number,
                complaint_id=row.complaint_id,
                status=row.status,
                case_type=row.case_type,
                subject=row.subject,
                priority=row.priority,
                created_at=row.created_at,
                created_by=row.created_by,
                category=row.category,
                owning_unit_id=row.owning_unit_id,
                customer_id=row.customer_id,
            )
            for row in rows
        ]
        return items, total

    def update_status(self, cmd: UpdateStatusCommand) -> CaseDTO:
        case = self._require(cmd.case_id)
        before = case.to_snapshot()
        if cmd.to_status and cmd.to_status.strip().upper() == "CANCELLED":
            if not (cmd.reason or "").strip() and not cmd.cancel_reason:
                raise err.validation(
                    "reason or cancelReason is required for CANCELLED",
                    details={"fields": ["reason", "cancelReason"]},
                )
        case.transition_status(
            to_status=cmd.to_status,
            actor_id=cmd.actor_id,
            destination_unit_id=cmd.destination_unit_id,
            cancel_reason=cmd.cancel_reason,
            reason=cmd.reason,
            assigned_user_id=cmd.assigned_user_id,
        )
        self._repo.save(case)
        event = "CaseCancelled" if case.status.value == "CANCELLED" else "CaseStatusChanged"
        if case.status.value == "ASSIGNED":
            event = "CaseAssigned"
        elif case.status.value == "IN_PROGRESS":
            event = "CaseWorkStarted"
        self._effects.record_case_event(
            case=case,
            event_name=event,
            title="Case Status Updated",
            actor_id=cmd.actor_id,
            before=before,
            after=case.to_snapshot(),
        )
        self._repo.commit()
        return to_case_dto(case)

    def resolve(self, cmd: ResolveCaseCommand) -> CaseDTO:
        case = self._require(cmd.case_id)
        before = case.to_snapshot()
        try:
            action = ResolveAction(cmd.action.strip().upper())
        except ValueError as exc:
            raise err.validation(
                "Invalid resolve action",
                details={"field": "action", "value": cmd.action},
            ) from exc
        case.resolve(
            action=action,
            actor_id=cmd.actor_id,
            comment=cmd.comment,
            resolution_code=cmd.resolution_code,
            summary=cmd.summary,
            detail=cmd.detail,
            customer_impact=cmd.customer_impact,
            attachment_ids=list(cmd.attachment_ids or []),
            rejection_reason=cmd.rejection_reason,
            evidence_required=False,  # category evidence policy catalog: NOT SPECIFIED
        )
        self._repo.save(case)
        self._effects.record_case_event(
            case=case,
            event_name="CaseResolved" if case.status.value == "RESOLVED" else "ResolutionUpdated",
            title="Case Resolution",
            actor_id=cmd.actor_id,
            before=before,
            after=case.to_snapshot(),
        )
        self._repo.commit()
        return to_case_dto(case)

    def close(self, cmd: CloseCaseCommand) -> CaseDTO:
        _ = cmd.note  # optional; NOT SPECIFIED as mandatory
        case = self._require(cmd.case_id)
        before = case.to_snapshot()
        case.close(actor_id=cmd.actor_id)
        self._repo.save(case)
        self._effects.record_case_event(
            case=case,
            event_name="CaseClosed",
            title="Case Closed",
            actor_id=cmd.actor_id,
            before=before,
            after=case.to_snapshot(),
        )
        self._repo.commit()
        # BQ-007: do NOT close Complaint Aggregate
        return to_case_dto(case)

    def _require(self, case_id: str) -> CaseAggregate:
        case = self._repo.get(case_id)
        if case is None:
            raise err.not_found("Case does not exist.")
        return case
