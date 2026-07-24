"""ComplaintDomainService — pure domain rules (CAPABILITY-004…008).

No database. No repository. No infrastructure I/O.
Lifecycle and priority validation live here — not in controllers.
Processing, assignment, escalation, and SLA operations delegate to Complaint.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from app.modules.complaint.application.services.errors import ComplaintApplicationError
from app.modules.complaint.domain.errors import ComplaintDomainError
from app.modules.complaint.domain.lifecycle import assert_transition
from app.modules.complaint.domain.models import (
    AssigneeType,
    Assignment,
    Complaint,
    ComplaintPriority,
    ComplaintSLA,
    ComplaintStatus,
    Escalation,
    EscalationLevel,
    SLAPolicy,
)


def _map_domain(exc: ComplaintDomainError) -> ComplaintApplicationError:
    return ComplaintApplicationError(exc.code, exc.message)


class ComplaintDomainService:
    """Domain service for complaint business rules."""

    def validate_priority(self, priority: ComplaintPriority) -> None:
        """Ensure priority is a known foundation priority."""
        if not isinstance(priority, ComplaintPriority):
            raise ComplaintApplicationError(
                "INVALID_PRIORITY",
                f"invalid complaint priority: {priority!r}",
            )

    def validate_status(self, status: ComplaintStatus) -> None:
        """Ensure status is a known foundation status."""
        if not isinstance(status, ComplaintStatus):
            raise ComplaintApplicationError(
                "INVALID_COMPLAINT_STATUS",
                f"invalid complaint status: {status!r}",
            )

    def transition(
        self,
        complaint: Complaint,
        new_status: ComplaintStatus,
        *,
        now: datetime | None = None,
    ) -> Complaint:
        """Return a new immutable complaint with updated status (replace, not mutate)."""
        self.validate_status(new_status)
        try:
            assert_transition(complaint.status, new_status)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc
        stamp = now if now is not None else datetime.now(timezone.utc)
        clear_resolution = (
            complaint.status is ComplaintStatus.RESOLVED
            and new_status is ComplaintStatus.IN_PROGRESS
        )
        try:
            if clear_resolution:
                return replace(
                    complaint,
                    status=new_status,
                    resolution=None,
                    updated_at=stamp,
                )
            return replace(complaint, status=new_status, updated_at=stamp)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def start_processing(
        self,
        complaint: Complaint,
        *,
        now: datetime | None = None,
    ) -> Complaint:
        """OPEN → IN_PROGRESS via aggregate."""
        try:
            return complaint.start_processing(now=now)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def resolve(
        self,
        complaint: Complaint,
        summary: str,
        resolved_by: str,
        *,
        now: datetime | None = None,
    ) -> Complaint:
        """IN_PROGRESS → RESOLVED with Resolution VO via aggregate."""
        try:
            return complaint.resolve(summary, resolved_by, now=now)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def close(
        self,
        complaint: Complaint,
        *,
        now: datetime | None = None,
    ) -> Complaint:
        """RESOLVED → CLOSED via aggregate."""
        try:
            return complaint.close(now=now)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def reopen(
        self,
        complaint: Complaint,
        *,
        reason: str | None = None,
        now: datetime | None = None,
    ) -> Complaint:
        """RESOLVED → IN_PROGRESS via aggregate."""
        try:
            return complaint.reopen(reason=reason, now=now)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def assign(
        self,
        complaint: Complaint,
        *,
        assignee_type: AssigneeType,
        assignee_id: str,
        assigned_by: str,
        active: Assignment | None,
        now: datetime | None = None,
    ) -> Assignment:
        """First assign via aggregate — does not change complaint status."""
        try:
            return complaint.assign(
                assignee_type=assignee_type,
                assignee_id=assignee_id,
                assigned_by=assigned_by,
                active=active,
                now=now,
            )
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def reassign(
        self,
        complaint: Complaint,
        *,
        assignee_type: AssigneeType,
        assignee_id: str,
        assigned_by: str,
        active: Assignment | None,
        now: datetime | None = None,
    ) -> tuple[Assignment, Assignment]:
        """Reassign via aggregate — release old + append new; status unchanged."""
        try:
            return complaint.reassign(
                assignee_type=assignee_type,
                assignee_id=assignee_id,
                assigned_by=assigned_by,
                active=active,
                now=now,
            )
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def unassign(
        self,
        complaint: Complaint,
        *,
        active: Assignment | None,
        reason: str | None = None,
        now: datetime | None = None,
    ) -> Assignment:
        """Unassign via aggregate — release active; status unchanged."""
        try:
            return complaint.unassign(active=active, reason=reason, now=now)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def escalate(
        self,
        complaint: Complaint,
        *,
        level: EscalationLevel,
        reason: str,
        escalated_by: str,
        current: Escalation | None,
        now: datetime | None = None,
    ) -> tuple[Escalation | None, Escalation]:
        """Escalate via aggregate — status and assignment unchanged."""
        try:
            return complaint.escalate(
                level=level,
                reason=reason,
                escalated_by=escalated_by,
                current=current,
                now=now,
            )
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def start_sla(
        self,
        complaint: Complaint,
        *,
        policy: SLAPolicy,
        active: ComplaintSLA | None,
        now: datetime | None = None,
    ) -> ComplaintSLA:
        """Start SLA via aggregate — status unchanged."""
        try:
            return complaint.start_sla(policy=policy, active=active, now=now)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def complete_sla(
        self,
        complaint: Complaint,
        *,
        active: ComplaintSLA | None,
        now: datetime | None = None,
    ) -> ComplaintSLA:
        """Complete active SLA via aggregate — status unchanged."""
        try:
            return complaint.complete_sla(active=active, now=now)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc

    def detect_sla_breach(
        self,
        sla: ComplaintSLA,
        *,
        current_time: datetime | None = None,
    ) -> ComplaintSLA:
        """Apply Rule 5 breach detection (idempotent)."""
        try:
            return sla.detect_breach(current_time=current_time)
        except ComplaintDomainError as exc:
            raise _map_domain(exc) from exc


__all__ = ["ComplaintDomainService"]
