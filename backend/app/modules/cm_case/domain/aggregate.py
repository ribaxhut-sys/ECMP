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
    AcceptanceDecision,
    AcceptanceParty,
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


@dataclass(frozen=True, slots=True)
class AcceptanceRecord:
    """One party's closure decision — immutable once created (F4 closure rule).

    Appended to ``CaseAggregate.acceptance_history`` and never edited; the
    aggregate's ``handling_unit_acceptance`` / ``owner_acceptance`` fields
    are current-state pointers to the latest record per party, not a
    replacement for the history list.
    """

    acceptance_id: str
    party: AcceptanceParty
    decision: AcceptanceDecision
    actor_id: str
    actor_unit_id: str | None
    decided_at: datetime
    note: str | None = None


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
    # Operational claim (who is working the Case). Not BQ-006 Assigned User.
    handling_claimed_by: str | None = None
    category: str | None = None
    # Current handling unit — the unit presently responsible for working the
    # Case. Mutated on transfer (ASSIGNED). Historically named "owning" but
    # behaves as handling unit; kept as-is to avoid a wide rename (see
    # `owner_unit_id` below for the immutable creator unit).
    owning_unit_id: str | None = None
    # Owner — unit that created the parent Complaint. Set once at Case
    # creation from the parent Complaint's owning unit and never mutated
    # again (F4 owner rule). Transfers only ever change owning_unit_id.
    owner_unit_id: str | None = None
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
    # F4 closure rule — CLOSED requires both current-state pointers ACCEPTED.
    # acceptance_history is the append-only audit trail; never cleared.
    handling_unit_acceptance: AcceptanceRecord | None = None
    owner_acceptance: AcceptanceRecord | None = None
    acceptance_history: list[AcceptanceRecord] = field(default_factory=list)
    # DEC-029 / API-520 lab — Pusat ownership without status ESCALATED (BQ-009)
    # and without overwriting originating owning_unit_id (DEC-028).
    escalated_to_pusat: bool = False
    escalation_reason: str | None = None
    escalated_at: datetime | None = None

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
        owner_unit_id: str | None = None,
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
            handling_claimed_by=created_by,
            category=(category.strip() if category else None),
            # Current handling unit — starts as the initial destination, if any.
            owning_unit_id=unit,
            # F4 owner rule: snapshot the parent Complaint's owning unit once,
            # at creation. Never reassigned afterward by any other method.
            owner_unit_id=(owner_unit_id or "").strip() or None,
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
        """Transfer to ASSIGNED changes ``owning_unit_id`` (handling unit)
        only — ``owner_unit_id`` (F4 owner) is never touched here or by any
        other method after ``create()``."""
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
        actor_unit_id: str | None = None,
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
            # DEC-021: code/summary optional — sentinel BRANCH_DONE + comment summary.
            code = (resolution_code or "").strip() or "BRANCH_DONE"
            summ = (summary or "").strip() or comment_text
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
            # DEC-021 Mode A branch Tutup: comment sufficient; persist sentinel fields.
            code = code or "BRANCH_DONE"
            summ = summ or comment_text
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
            # F4 closure rule: reaching RESOLVED via ACCEPT *is* the Handling
            # Unit declaring the case done — stamp it explicitly rather than
            # only implying it via `supervisor_approved_after_resolved`.
            # A fresh RESOLVED cycle always starts a fresh acceptance cycle.
            acceptance = AcceptanceRecord(
                acceptance_id=str(uuid4()),
                party=AcceptanceParty.HANDLING_UNIT,
                decision=AcceptanceDecision.ACCEPT,
                actor_id=actor_id,
                actor_unit_id=actor_unit_id,
                decided_at=now,
                note=None,
            )
            self.acceptance_history.append(acceptance)
            self.handling_unit_acceptance = acceptance
            self.owner_acceptance = None
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

    def record_acceptance(
        self,
        *,
        party: AcceptanceParty,
        decision: AcceptanceDecision,
        actor_id: str,
        actor_unit_id: str | None = None,
        note: str | None = None,
    ) -> None:
        """F4 closure rule — Handling Unit and Owner each decide independently.

        Only meaningful once a resolution has been proposed and accepted by
        the Handling Unit (status RESOLVED) — closure agreement is about
        *that* resolution. REJECT (either party) sends the Case back to
        IN_PROGRESS for further handling per the existing state machine (no
        new status introduced) and clears both current-acceptance pointers
        so a stale ACCEPTED from a prior cycle can never satisfy a later
        Close — the next RESOLVED cycle must earn both acceptances again.
        Nothing in ``acceptance_history`` is ever removed or edited.
        """
        if self.status != CaseStatus.RESOLVED:
            raise err.invalid_state(
                "Acceptance requires Case status RESOLVED.",
                details={"status": self.status.value},
            )
        cleaned_note = (note or "").strip() or None
        if decision == AcceptanceDecision.REJECT and not cleaned_note:
            raise err.validation(
                "note is required when rejecting",
                details={"field": "note", "decision": decision.value},
            )
        now = _utcnow()
        record = AcceptanceRecord(
            acceptance_id=str(uuid4()),
            party=party,
            decision=decision,
            actor_id=actor_id,
            actor_unit_id=actor_unit_id,
            decided_at=now,
            note=cleaned_note,
        )
        self.acceptance_history.append(record)
        if party == AcceptanceParty.HANDLING_UNIT:
            self.handling_unit_acceptance = record
        else:
            self.owner_acceptance = record

        if decision == AcceptanceDecision.REJECT:
            # Back to handling — existing IN_PROGRESS status represents this;
            # no new CaseStatus needed. Both pointers reset for the next cycle.
            self.status = CaseStatus.IN_PROGRESS
            self.handling_unit_acceptance = None
            self.owner_acceptance = None
            self.updated_at = now
            return

        # F4 closure: the party that supplies the *second* ACCEPT causes CLOSED
        # when all existing close guards are already satisfied (resolution
        # accepted, HU ACCEPT, Owner ACCEPT). No third "approval" step.
        if (
            self.handling_unit_acceptance is not None
            and self.handling_unit_acceptance.decision == AcceptanceDecision.ACCEPT
            and self.owner_acceptance is not None
            and self.owner_acceptance.decision == AcceptanceDecision.ACCEPT
        ):
            self.close(actor_id=actor_id)
            return

        self.updated_at = now

    def close(self, *, actor_id: str) -> None:
        # Compatibility: already CLOSED (e.g. via dual-acceptance trigger) —
        # idempotent success. Never invent acceptances; never bypass when
        # still open without both parties.
        if self.status == CaseStatus.CLOSED:
            return
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
        # F4 closure rule — CLOSED requires BOTH parties' explicit agreement.
        # Neither acceptance alone is sufficient (rule §CLOSURE).
        # POST .../close cannot bypass this gate.
        if (
            self.handling_unit_acceptance is None
            or self.handling_unit_acceptance.decision != AcceptanceDecision.ACCEPT
        ):
            raise err.conflict(
                "HANDLING_UNIT_ACCEPTANCE_REQUIRED",
                "Handling Unit must accept the resolution before Close.",
            )
        if (
            self.owner_acceptance is None
            or self.owner_acceptance.decision != AcceptanceDecision.ACCEPT
        ):
            raise err.conflict(
                "OWNER_ACCEPTANCE_REQUIRED",
                "Owner must accept the resolution before Close.",
            )
        now = _utcnow()
        self.status = CaseStatus.CLOSED
        self.closed_by = actor_id
        self.closed_at = now
        self.updated_at = now

    def escalate_to_pusat(self, *, reason: str) -> None:
        """Branch → Pusat on this Case only (DEC-029). Does not set ESCALATED."""
        if self.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED, CaseStatus.RESOLVED):
            raise err.invalid_state(
                "Only an open Case can be escalated to Pusat.",
                details={"status": self.status.value},
            )
        if self.escalated_to_pusat:
            raise err.conflict(
                "CASE_ALREADY_ESCALATED_TO_PUSAT",
                "This Case is already with Pusat.",
            )
        text = (reason or "").strip()
        if len(text) < 20:
            raise err.validation(
                "escalation reason must be at least 20 characters",
                details={"field": "reason", "minLength": 20},
            )
        if self.status in (CaseStatus.CREATED, CaseStatus.ASSIGNED):
            self.status = CaseStatus.IN_PROGRESS
        now = _utcnow()
        self.escalated_to_pusat = True
        self.escalation_reason = text
        self.escalated_at = now
        # Pusat must claim; branch cancel stays open until that claim.
        self.handling_claimed_by = None
        self.updated_at = now

    def cancel_escalation_to_pusat(self, *, reason: str) -> None:
        """Branch pulls back API-520 while Pusat has not claimed handling."""
        if not self.escalated_to_pusat:
            raise err.conflict(
                "CASE_NOT_ESCALATED_TO_PUSAT",
                "This Case is not with Pusat.",
            )
        if self.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED, CaseStatus.RESOLVED):
            raise err.invalid_state(
                "A finished Case cannot cancel escalation to Pusat.",
                details={"status": self.status.value},
            )
        if (self.handling_claimed_by or "").strip():
            raise err.conflict(
                "CASE_PUSAT_WORK_STARTED",
                "Pusat has already taken this Case; branch cannot cancel escalation.",
            )
        text = (reason or "").strip()
        if len(text) < 20:
            raise err.validation(
                "cancellation reason must be at least 20 characters",
                details={"field": "reason", "minLength": 20},
            )
        self.escalated_to_pusat = False
        # Branch again: restore handling to Case creator (cleared on escalate).
        self.handling_claimed_by = (self.created_by or "").strip() or None
        self.updated_at = _utcnow()

    def return_escalation_from_pusat(self, *, note: str) -> None:
        """API-521 lab — Pusat returns this Case; free-text reason/note only."""
        if not self.escalated_to_pusat:
            raise err.conflict(
                "CASE_NOT_ESCALATED_TO_PUSAT",
                "This Case is not with Pusat.",
            )
        if self.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED, CaseStatus.RESOLVED):
            raise err.invalid_state(
                "A finished Case cannot be returned to the branch.",
                details={"status": self.status.value},
            )
        text = (note or "").strip()
        if len(text) < 10:
            raise err.validation(
                "return note must be at least 10 characters",
                details={"field": "returnNote", "minLength": 10},
            )
        self.escalated_to_pusat = False
        # Back at branch: Case stays with the creator — no peer “take over” prompt.
        self.handling_claimed_by = (self.created_by or "").strip() or None
        self.updated_at = _utcnow()

    def claim_handling(self, user_id: str) -> None:
        uid = (user_id or "").strip()
        if not uid:
            raise err.validation(
                "handlingClaimedBy is required",
                details={"field": "handlingClaimedBy"},
            )
        self.handling_claimed_by = uid
        self.updated_at = _utcnow()

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "caseId": str(self.case_id),
            "caseNumber": self.case_number.value,
            "complaintId": self.complaint_id,
            "status": self.status.value,
            "handlingClaimedBy": self.handling_claimed_by,
            "ownerUnitId": self.owner_unit_id,
            "owningUnitId": self.owning_unit_id,
            "escalatedToPusat": self.escalated_to_pusat,
            "owningUnit": "PUSAT" if self.escalated_to_pusat else "BRANCH",
            "handlingUnitAcceptance": (
                self.handling_unit_acceptance.decision.value
                if self.handling_unit_acceptance
                else None
            ),
            "ownerAcceptance": (
                self.owner_acceptance.decision.value if self.owner_acceptance else None
            ),
        }
