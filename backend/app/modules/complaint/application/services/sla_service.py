"""ComplaintSLAApplicationService (CAPABILITY-008).

Orchestrates repository ports + domain SLA rules.
No FastAPI. No ORM. No business logic beyond calling Domain.
SLA does not mutate Complaint lifecycle status, Escalation, or Notification.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.core.request_context import RequestContext
from app.modules.complaint.application.dto import ComplaintSlaDto
from app.modules.complaint.application.services.domain_service import (
    ComplaintDomainService,
)
from app.modules.complaint.application.services.errors import ComplaintApplicationError
from app.modules.complaint.domain.models import Complaint, ComplaintSLA, SLAPolicy
from app.modules.complaint.domain.repositories import (
    ComplaintRepository,
    ComplaintSlaRepository,
    SLAPolicyRepository,
)


@dataclass(frozen=True, slots=True)
class StartSlaInput:
    policy_id: uuid.UUID | None = None
    started_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RecalculateSlaInput:
    current_time: datetime


class ComplaintSLAApplicationService:
    """SLA use cases (start / complete / recalculate / get)."""

    def __init__(
        self,
        complaints: ComplaintRepository,
        slas: ComplaintSlaRepository,
        policies: SLAPolicyRepository,
        domain: ComplaintDomainService | None = None,
    ) -> None:
        self._complaints = complaints
        self._slas = slas
        self._policies = policies
        self._domain = domain if domain is not None else ComplaintDomainService()

    async def start(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        data: StartSlaInput | None = None,
    ) -> ComplaintSlaDto:
        _ = context
        payload = data if data is not None else StartSlaInput()
        complaint = await self._require_complaint(complaint_id)
        policy = await self._resolve_policy(payload.policy_id)
        active = await self._slas.get_active_by_complaint(complaint_id)
        created = self._domain.start_sla(
            complaint,
            policy=policy,
            active=active,
            now=payload.started_at,
        )
        saved = await self._slas.add(created)
        return self._to_dto(saved, policy, current_time=saved.started_at)

    async def complete(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        *,
        now: datetime | None = None,
    ) -> ComplaintSlaDto:
        _ = context
        complaint = await self._require_complaint(complaint_id)
        active = await self._slas.get_active_by_complaint(complaint_id)
        completed = self._domain.complete_sla(complaint, active=active, now=now)
        saved = await self._slas.update(completed)
        policy = await self._require_policy(saved.policy_id)
        return self._to_dto(saved, policy, current_time=saved.completed_at)

    async def recalculate(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        data: RecalculateSlaInput,
    ) -> ComplaintSlaDto:
        _ = context
        await self._require_complaint(complaint_id)
        active = await self._slas.get_active_by_complaint(complaint_id)
        if active is None:
            raise ComplaintApplicationError(
                "NO_ACTIVE_SLA",
                f"no active SLA for complaint: {complaint_id}",
            )
        updated = self._domain.detect_sla_breach(
            active, current_time=data.current_time
        )
        saved = active
        if (
            updated.is_breached != active.is_breached
            or updated.breached_at != active.breached_at
        ):
            saved = await self._slas.update(updated)
        policy = await self._require_policy(saved.policy_id)
        return self._to_dto(saved, policy, current_time=data.current_time)

    async def get(
        self,
        context: RequestContext,
        complaint_id: uuid.UUID,
        *,
        current_time: datetime | None = None,
    ) -> ComplaintSlaDto:
        _ = context
        await self._require_complaint(complaint_id)
        active = await self._slas.get_active_by_complaint(complaint_id)
        row = active
        if row is None:
            row = await self._slas.get_latest_by_complaint(complaint_id)
        if row is None:
            raise ComplaintApplicationError(
                "SLA_NOT_FOUND",
                f"no SLA for complaint: {complaint_id}",
            )
        # Refresh breach detection for active SLA on read (no scheduler).
        if row.is_active:
            refreshed = self._domain.detect_sla_breach(
                row, current_time=current_time
            )
            if (
                refreshed.is_breached != row.is_breached
                or refreshed.breached_at != row.breached_at
            ):
                row = await self._slas.update(refreshed)
        policy = await self._require_policy(row.policy_id)
        return self._to_dto(row, policy, current_time=current_time)

    async def complete_active_for_close(
        self,
        complaint: Complaint,
        *,
        now: datetime | None = None,
    ) -> ComplaintSLA | None:
        """Rule 4 — when Complaint is CLOSED, complete active SLA if present."""
        active = await self._slas.get_active_by_complaint(complaint.complaint_id)
        if active is None or not active.is_active:
            return None
        completed = self._domain.complete_sla(complaint, active=active, now=now)
        return await self._slas.update(completed)

    async def _require_complaint(self, complaint_id: uuid.UUID) -> Complaint:
        complaint = await self._complaints.get_by_id(complaint_id)
        if complaint is None:
            raise ComplaintApplicationError(
                "COMPLAINT_NOT_FOUND",
                f"complaint not found: {complaint_id}",
            )
        return complaint

    async def _resolve_policy(self, policy_id: uuid.UUID | None) -> SLAPolicy:
        if policy_id is not None:
            return await self._require_policy(policy_id)
        policy = await self._policies.get_default()
        if policy is None:
            raise ComplaintApplicationError(
                "SLA_POLICY_NOT_FOUND",
                "no default SLA policy configured",
            )
        return policy

    async def _require_policy(self, policy_id: uuid.UUID) -> SLAPolicy:
        policy = await self._policies.get_by_id(policy_id)
        if policy is None:
            raise ComplaintApplicationError(
                "SLA_POLICY_NOT_FOUND",
                f"SLA policy not found: {policy_id}",
            )
        return policy

    def _to_dto(
        self,
        sla: ComplaintSLA,
        policy: SLAPolicy,
        *,
        current_time: datetime | None = None,
    ) -> ComplaintSlaDto:
        return ComplaintSlaDto.from_domain(
            sla,
            policy_name=policy.name,
            target_minutes=policy.target_minutes,
            current_time=current_time,
        )


__all__ = [
    "ComplaintSLAApplicationService",
    "RecalculateSlaInput",
    "StartSlaInput",
]
