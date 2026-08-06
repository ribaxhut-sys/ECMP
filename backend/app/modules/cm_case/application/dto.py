"""Application DTOs (Epic 6) — transport-neutral command/result shapes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class CreateCaseCommand:
    complaint_id: str
    case_type: str
    subject: str
    description: str
    priority: str
    category: str | None = None
    destination_unit_id: str | None = None
    assigned_user_id: str | None = None
    sla_policy_version_id: str | None = None
    actor_id: str = "system"


@dataclass(frozen=True)
class AddCaseCommand:
    complaint_id: str
    case_type: str
    subject: str
    description: str
    priority: str
    category: str | None = None
    destination_unit_id: str | None = None
    assigned_user_id: str | None = None
    sla_policy_version_id: str | None = None
    actor_id: str = "system"


@dataclass(frozen=True)
class UpdateStatusCommand:
    case_id: str
    to_status: str
    actor_id: str
    destination_unit_id: str | None = None
    cancel_reason: str | None = None
    reason: str | None = None
    assigned_user_id: str | None = None


@dataclass(frozen=True)
class ResolveCaseCommand:
    case_id: str
    action: str
    comment: str
    actor_id: str
    resolution_code: str | None = None
    summary: str | None = None
    detail: str | None = None
    customer_impact: str | None = None
    attachment_ids: list[str] = field(default_factory=list)
    rejection_reason: str | None = None


@dataclass(frozen=True)
class CloseCaseCommand:
    case_id: str
    actor_id: str
    note: str | None = None


@dataclass
class ResolutionDTO:
    resolution_id: str
    resolution_code: str
    summary: str
    status: str
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
class CaseSummaryDTO:
    case_id: str
    case_number: str
    complaint_id: str
    status: str
    case_type: str
    subject: str
    priority: str
    created_at: datetime
    created_by: str
    category: str | None = None
    owning_unit_id: str | None = None
    customer_id: str | None = None


@dataclass
class CaseDTO:
    case_id: str
    case_number: str
    complaint_id: str
    customer_id: str
    status: str
    case_type: str
    subject: str
    description: str
    priority: str
    created_at: datetime
    created_by: str
    category: str | None = None
    owning_unit_id: str | None = None
    assigned_user_id: str | None = None
    sla_policy_version_id: str | None = None
    sla_countdown_active: bool = False
    cancel_reason: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    updated_at: datetime | None = None
    resolution: ResolutionDTO | None = None
    resolution_history: list[ResolutionDTO] = field(default_factory=list)
    complaint_status_after_create: str | None = None
