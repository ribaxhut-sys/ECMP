"""Case Aggregate root — Mode A CAP-008 (child of Complaint Aggregate)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from app.modules.cm_case.domain import errors as err
from app.modules.cm_case.domain.transitions import (
    can_transition_status,
    is_not_exposed_status,
)
from app.modules.cm_case.domain.value_objects import (
    CancelReason,
    CaseNumber,
    CaseStatus,
    ResolutionProposalStatus,
    ResolveAction,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass
class ResolutionRecord:
    resolution_id: str
    resolution_code: str
    summary: str
    status: ResolutionProposalStatus
    comment: str
    detail: str | None = None
    customer_impact: str | None = None
    attachment_ids: list[str] = field(default_factory=list)
    proposed_by: str | None = None
    proposed_at: datetime | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None
    rejection_reason: str | None = None


@dataclass
class CaseAggregate:
    """Operational Case under Complaint (BR-004). Hard-delete forbidden."""

    case_id: UUID
    case_number: CaseNumber
    complaint_id: str
    customer_id: str
    status: CaseStatus
    case_type: str
    subject: str
    description: str
    priority: str
    created_by: str
    created_at: datetime
    category: str | None = None
    owning_unit_id: str | None = None
    sla_policy_version_id: str | None = None
    sla_countdown_active: bool = False  # Always False Mode A (BQ-005)
    cancel_reason: CancelReason | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    updated_at: datetime | None = None
    resolution: ResolutionRecord | None = None
    resolution_history: list[ResolutionRecord] = field(default_factory=list)
    supervisor_approved_after_resolved: bool = False
    complaint_status_after_create: str | None = None

    @classmethod
    def create(
        cls,
        *,
        complaint_id: str,
        customer_id: str,
        case_number: CaseNumber,
        case_type: str,
        subject: str,
        description: str,
        priority: str,
        created_by: str,
        category: str | None = None,
        destination_unit_id: str | None = None,
        sla_policy_version_id: str | None = None,
        complaint_became_in_progress: bool = False,
    ) -> CaseAggregate:
        unit = (destination_unit_id or "").strip() or None
        status = CaseStatus.ASSIGNED if unit else CaseStatus.CREATED
        now = _utcnow()
        return cls(
            case_id=uuid4(),
            case_number=case_number,
            complaint_id=complaint_id,
            customer_id=customer_id,
            status=status,
            case_type=case_type.strip(),
            subject=subject.strip(),
            description=description.strip(),
            priority=priority.strip(),
            created_by=created_by,
            created_at=now,
            category=(category.strip() if category else None),
            owning_unit_id=unit,
            sla_policy_version_id=sla_policy_version_id,
            sla_countdown_active=False,
            updated_at=now,
            complaint_status_after_create=(
                "IN_PROGRESS" if complaint_became_in_progress else None
            ),
        )

    def transition_status(
        self,
        *,
        to_status: str,
        actor_id: str,
        destination_unit_id: str | None = None,
        cancel_reason: str | None = None,
        reason: str | None = None,
        assigned_user_id: str | None = None,
    ) -> None:
        _ = reason  # free-text; validated at application layer when required
        if assigned_user_id:
            raise err.conflict(
                "ASSIGNED_USER_NOT_ALLOWED_MODE_A",
                "Assigned User is outside Mode A (BQ-006).",
            )
        raw = (to_status or "").strip().upper()
        if is_not_exposed_status(raw):
            raise err.conflict(
                "STATE_NOT_EXPOSED_MODE_A",
                "PENDING/ESCALATED are not exposed in Mode A Delivery (BQ-009).",
            )
        if self.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED):
            raise err.invalid_state("Case is terminal; status cannot change.")
        try:
            target = CaseStatus(raw)
        except ValueError as exc:
            raise err.validation(
                "Invalid toStatus for Mode A",
                details={"field": "toStatus", "value": to_status},
            ) from exc

        if target in (CaseStatus.RESOLVED, CaseStatus.CLOSED):
            raise err.conflict(
                "INVALID_TRANSITION",
                "RESOLVED/CLOSED must use Resolve/Close endpoints (FR-005/FR-006).",
            )

        if not can_transition_status(self.status, target):
            raise err.conflict(
                "INVALID_TRANSITION",
                f"Transition {self.status.value} → {target.value} is not allowed.",
                details={"from": self.status.value, "to": target.value},
            )

        if target == CaseStatus.ASSIGNED:
            unit = (destination_unit_id or "").strip() or self.owning_unit_id
            if not unit:
                raise err.validation(
                    "destinationUnitId is required when transitioning to ASSIGNED",
                    details={"field": "destinationUnitId"},
                )
            self.owning_unit_id = unit

        if target == CaseStatus.CANCELLED:
            if not cancel_reason:
                raise err.validation(
                    "cancelReason is required when toStatus=CANCELLED",
                    details={"field": "cancelReason"},
                )
            try:
                self.cancel_reason = CancelReason(cancel_reason.strip().upper())
            except ValueError as exc:
                raise err.validation(
                    "Invalid cancelReason for Mode A (BQ-014)",
                    details={"field": "cancelReason", "value": cancel_reason},
                ) from exc

        self.status = target
        self.updated_at = _utcnow()
        _ = actor_id

    def resolve(
        self,
        *,
        action: ResolveAction,
        actor_id: str,
        comment: str,
        resolution_code: str | None = None,
        summary: str | None = None,
        detail: str | None = None,
        customer_impact: str | None = None,
        attachment_ids: list[str] | None = None,
        rejection_reason: str | None = None,
        evidence_required: bool = False,
    ) -> None:
        if self.status != CaseStatus.IN_PROGRESS:
            raise err.invalid_state(
                "Mode A Resolve requires Case status IN_PROGRESS.",
                details={"status": self.status.value},
            )
        comment_text = (comment or "").strip()
        if not comment_text:
            raise err.conflict(
                "COMMENT_REQUIRED",
                "Resolve requires Comment (BQ-010).",
            )
        if evidence_required and not (attachment_ids or []):
            raise err.conflict(
                "RESOLUTION_EVIDENCE_REQUIRED",
                "Mandatory category evidence is missing (BR-008 E1).",
            )

        now = _utcnow()
        if action == ResolveAction.PROPOSE:
            code = (resolution_code or "").strip()
            summ = (summary or "").strip()
            if not code or not summ:
                raise err.validation(
                    "resolutionCode and summary are required for PROPOSE",
                    details={"fields": ["resolutionCode", "summary"]},
                )
            record = ResolutionRecord(
                resolution_id=str(uuid4()),
                resolution_code=code,
                summary=summ,
                status=ResolutionProposalStatus.PENDING_APPROVAL,
                comment=comment_text,
                detail=detail,
                customer_impact=customer_impact,
                attachment_ids=list(attachment_ids or []),
                proposed_by=actor_id,
                proposed_at=now,
            )
            self.resolution_history.append(record)
            self.resolution = record
            self.supervisor_approved_after_resolved = False
        elif action == ResolveAction.ACCEPT:
            code = (resolution_code or "").strip()
            summ = (summary or "").strip()
            pending = self.resolution
            if pending and pending.status == ResolutionProposalStatus.PENDING_APPROVAL:
                code = code or pending.resolution_code
                summ = summ or pending.summary
                detail = detail if detail is not None else pending.detail
                customer_impact = (
                    customer_impact
                    if customer_impact is not None
                    else pending.customer_impact
                )
                attachment_ids = attachment_ids or pending.attachment_ids
            if not code or not summ:
                raise err.validation(
                    "resolutionCode and summary are required for ACCEPT",
                    details={"fields": ["resolutionCode", "summary"]},
                )
            record = ResolutionRecord(
                resolution_id=str(uuid4()),
                resolution_code=code,
                summary=summ,
                status=ResolutionProposalStatus.ACCEPTED,
                comment=comment_text,
                detail=detail,
                customer_impact=customer_impact,
                attachment_ids=list(attachment_ids or []),
                proposed_by=(pending.proposed_by if pending else actor_id),
                proposed_at=(pending.proposed_at if pending else now),
                decided_by=actor_id,
                decided_at=now,
            )
            self.resolution_history.append(record)
            self.resolution = record
            self.status = CaseStatus.RESOLVED
            self.supervisor_approved_after_resolved = True
        elif action == ResolveAction.REJECT:
            rej = (rejection_reason or "").strip()
            if not rej:
                raise err.validation(
                    "rejectionReason is required when action=REJECT",
                    details={"field": "rejectionReason"},
                )
            pending = self.resolution
            record = ResolutionRecord(
                resolution_id=str(uuid4()),
                resolution_code=(pending.resolution_code if pending else ""),
                summary=(pending.summary if pending else ""),
                status=ResolutionProposalStatus.REJECTED,
                comment=comment_text,
                detail=(pending.detail if pending else None),
                attachment_ids=list(pending.attachment_ids if pending else []),
                proposed_by=(pending.proposed_by if pending else None),
                proposed_at=(pending.proposed_at if pending else None),
                decided_by=actor_id,
                decided_at=now,
                rejection_reason=rej,
            )
            self.resolution_history.append(record)
            self.resolution = record
            # Case stays IN_PROGRESS
        else:
            raise err.validation("Unsupported resolve action")
        self.updated_at = now

    def close(self, *, actor_id: str) -> None:
        # Checklist #1–#4 (FR-006)
        if self.status != CaseStatus.RESOLVED:
            raise err.invalid_state("Close requires Case status RESOLVED.")
        if (
            self.resolution is None
            or self.resolution.status != ResolutionProposalStatus.ACCEPTED
        ):
            raise err.conflict(
                "CLOSE_CHECKLIST_NOT_MET",
                "Final Resolution Accepted is required before Close.",
            )
        if not self.supervisor_approved_after_resolved:
            raise err.conflict(
                "SUPERVISOR_APPROVAL_REQUIRED",
                "Supervisor Approval after RESOLVED is required (BQ-008).",
            )
        now = _utcnow()
        self.status = CaseStatus.CLOSED
        self.closed_by = actor_id
        self.closed_at = now
        self.updated_at = now

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "caseId": str(self.case_id),
            "caseNumber": self.case_number.value,
            "complaintId": self.complaint_id,
            "status": self.status.value,
            "owningUnitId": self.owning_unit_id,
        }
