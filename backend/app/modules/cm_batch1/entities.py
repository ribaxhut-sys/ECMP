"""Domain entities for CM Batch 1 Aggregate (FR-001 / D-03) + FR-003."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime


@dataclass
class ComplaintAggregate:
    complaint_id: str
    complaint_number: str
    customer_id: str
    category: str
    channel: str
    subject: str
    description: str
    priority: str
    status: str = "REGISTERED"
    #: Set/cleared with ``status`` by ``sla.apply_complaint_status`` (DEC-031).
    closed_at: datetime | None = None
    intake_disposition: str | None = None
    hq_accepted_at: datetime | None = None
    hq_arrival_date: date | None = None
    hq_arrival_time: str | None = None
    hq_destination_unit_id: str | None = None
    hq_destination_set_by: str | None = None
    hq_destination_set_at: datetime | None = None
    proposed_arrival_date: date | None = None
    proposed_arrival_time: str | None = None
    proposed_by: str | None = None
    proposed_at: datetime | None = None
    owning_unit_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None
    case_created: bool = False


@dataclass
class IdempotencyRecord:
    key: str
    complaint_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class LaterReviewWorkItem:
    """Supervisor later-review work item (FR-001 / FR-003 E1 / FR-004 E8)."""

    work_item_id: str
    customer_id: str
    reason: str
    status: str = "OPEN"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    complaint_id: str | None = None


@dataclass
class DuplicateDecisionRecord:
    decision_id: str
    customer_id: str
    decision: str
    surviving_complaint_id: str | None = None
    source_complaint_id: str | None = None
    justification: str | None = None
    staging_token: str | None = None
    warning: bool = False
    hard_block: bool = False
    policy_version: str = "cm-batch1-dup-v1"
    candidate_snapshot: str | None = None
    actor_id: str | None = None
    later_review_work_item_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    case_created: bool = False


# FR-004 Batch 1 business statuses (CAP-011 retains AVAILABLE/DELETED for bytes).
ATTACHMENT_STATUS_STAGED = "STAGED"
ATTACHMENT_STATUS_ACTIVE = "ACTIVE"
ATTACHMENT_STATUS_TRANSFERRED = "TRANSFERRED"
ATTACHMENT_STATUS_VOID = "VOID"
ATTACHMENT_STATUS_SUPERSEDED = "SUPERSEDED"


@dataclass
class Batch1AttachmentRecord:
    id: str
    platform_attachment_id: str
    status: str
    classification: str
    staging_token: str | None = None
    complaint_id: str | None = None
    customer_id: str | None = None
    case_id: str | None = None
    original_name: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    checksum_sha256: str | None = None
    supersedes_id: str | None = None
    void_reason: str | None = None
    uploaded_by: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Batch1AttachmentHistoryRecord:
    id: str
    attachment_id: str
    event_type: str
    from_status: str | None
    to_status: str | None
    reason: str | None
    actor_id: str | None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: str | None = None


@dataclass
class Batch1StagingSession:
    staging_token: str
    status: str
    expires_at: datetime
    created_by: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
