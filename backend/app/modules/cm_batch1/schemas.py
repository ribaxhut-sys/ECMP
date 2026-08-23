"""Pydantic contracts for CM Batch 1 (API-500…506) — camelCase."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class CustomerSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_number: str | None = Field(default=None, alias="customerNumber")
    identity_number: str | None = Field(default=None, alias="identityNumber")
    reference_number: str | None = Field(default=None, alias="referenceNumber")


class CustomerCandidate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    display_name: str = Field(alias="displayName")
    customer_number: str | None = Field(default=None, alias="customerNumber")
    masked_identity: str | None = Field(default=None, alias="maskedIdentity")
    phone: str | None = None


class CustomerSearchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    verification_status: Literal[
        "verified",
        "not_found",
        "ambiguous",
        "degraded",
        "blocked",
    ] = Field(alias="verificationStatus")
    customer_id: str | None = Field(default=None, alias="customerId")
    as_of: datetime = Field(alias="asOf")
    candidates: list[CustomerCandidate] = Field(default_factory=list)
    enumeration_outcome: Literal["allowed", "delayed", "blocked", "alerted"] = Field(
        alias="enumerationOutcome"
    )
    brief_profile: dict[str, Any] | None = Field(default=None, alias="briefProfile")


class ConfirmCustomerRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")


class ConfirmCustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    locked: bool = True
    as_of: datetime = Field(alias="asOf")


class Customer360Batch1Response(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    profile: dict[str, Any]
    active_complaints: list[dict[str, Any]] = Field(alias="activeComplaints")
    complaint_history: list[dict[str, Any]] = Field(
        default_factory=list, alias="complaintHistory"
    )
    complaint_count: int = Field(alias="complaintCount")
    as_of: datetime = Field(alias="asOf")


class CreateComplaintBatch1Request(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    category: str
    channel: str
    subject: str
    description: str
    priority: str | None = None
    recording_unit_id: str | None = Field(default=None, alias="recordingUnitId")
    duplicate_override_justification: str | None = Field(
        default=None, alias="duplicateOverrideJustification"
    )
    staging_token: str | None = Field(default=None, alias="stagingToken")
    intake_disposition: Literal["BRANCH_CLOSED", "ESCALATE_PENDING_APPROVAL"] | None = (
        Field(default=None, alias="intakeDisposition")
    )
    proposed_arrival_date: date | None = Field(
        default=None,
        alias="proposedArrivalDate",
        description=(
            "Branch-proposed HQ arrival date on escalation — advisory only, "
            "Pusat still decides the final schedule."
        ),
    )
    proposed_arrival_time: str | None = Field(
        default=None,
        alias="proposedArrivalTime",
        description="Branch-proposed HQ arrival time HH:MM, paired with proposedArrivalDate.",
    )


class ComplaintSlaView(BaseModel):
    """Resolution-SLA position of one complaint (DEC-031).

    Every value is computed server-side at read time; the client never
    recalculates from its own clock (DEC-031 §2.9). ``null`` on the parent
    field means "not measured" — either measurement is switched off or the
    closure timestamp is unknown.
    """

    model_config = ConfigDict(populate_by_name=True)

    status: Literal["ON_TRACK", "OVERDUE", "MET", "MISSED"]
    target_days: int = Field(alias="targetDays")
    due_at: datetime = Field(alias="dueAt")
    elapsed_days: int = Field(
        alias="elapsedDays",
        description="Whole days from registration to closure, or to now if open",
    )
    remaining_days: int | None = Field(
        default=None,
        alias="remainingDays",
        description="Whole days left before dueAt; null once overdue or settled",
    )
    overdue_days: int | None = Field(
        default=None,
        alias="overdueDays",
        description="Whole days past dueAt; null while inside the target",
    )
    is_warning: bool = Field(
        default=False,
        alias="isWarning",
        description="Open and past the warning threshold, not yet overdue",
    )


class ComplaintBatch1Response(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    status: Literal["REGISTERED", "IN_PROGRESS", "CLOSED"] = "REGISTERED"
    customer_id: str = Field(alias="customerId")
    customer_display_name: str | None = Field(
        default=None, alias="customerDisplayName"
    )
    customer_number: str | None = Field(default=None, alias="customerNumber")
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="Actor id of the intake officer (PIC) — identity is not ECMP SoR",
    )
    created_by_name: str | None = Field(
        default=None,
        alias="createdByName",
        description="Operator-facing name of the intake officer, resolved via directory",
    )
    intake_disposition: str | None = Field(default=None, alias="intakeDisposition")
    case_created: bool = Field(default=False, alias="caseCreated")
    replayed: bool = False
    category: str | None = None
    channel: str | None = None
    subject: str | None = None
    description: str | None = Field(
        default=None,
        description="Full intake narrative blob (history for Supervisor / HQ)",
    )
    intake_narrative: str | None = Field(
        default=None,
        alias="intakeNarrative",
        description="Customer complaint body parsed from description",
    )
    branch_resolution: str | None = Field(
        default=None,
        alias="branchResolution",
        description="Branch close note when intakeDisposition=BRANCH_CLOSED",
    )
    escalation_reason: str | None = Field(
        default=None,
        alias="escalationReason",
        description="Why escalate to HQ — history when ESCALATE_* dispositions",
    )
    supervisor_note: str | None = Field(
        default=None,
        alias="supervisorNote",
        description="Supervisor/Manager note for HQ — required on APPROVE (API-515)",
    )
    rejection_note: str | None = Field(
        default=None,
        alias="rejectionNote",
        description="Reject reason history (Penolakan Eskalasi section)",
    )
    cancellation_note: str | None = Field(
        default=None,
        alias="cancellationNote",
        description="Batalkan Eskalasi reason history — CANCEL when ESCALATE_APPROVED",
    )
    hq_accepted_at: datetime | None = Field(
        default=None,
        alias="hqAcceptedAt",
        description=(
            "When set, Pusat has accepted/claimed the escalation — "
            "Batalkan Eskalasi is blocked and UI button hidden."
        ),
    )
    hq_arrival_date: date | None = Field(
        default=None,
        alias="hqArrivalDate",
        description="Scheduled customer arrival date at HQ (Batch-1 lab)",
    )
    hq_arrival_time: str | None = Field(
        default=None,
        alias="hqArrivalTime",
        description="Scheduled customer arrival time HH:MM at HQ (Batch-1 lab)",
    )
    hq_destination_unit_id: str | None = Field(
        default=None,
        alias="hqDestinationUnitId",
        description=(
            "Pusat unit the taxpayer reports to (PUSAT-CRO / PUSAT-SEKRE / "
            "PUSAT-SUBAN-…). Decided by Pusat, shown read-only to the branch."
        ),
    )
    hq_destination_set_by: str | None = Field(
        default=None, alias="hqDestinationSetBy"
    )
    hq_destination_set_at: datetime | None = Field(
        default=None, alias="hqDestinationSetAt"
    )
    hq_acceptance_note: str | None = Field(
        default=None,
        alias="hqAcceptanceNote",
        description="Penerimaan Pusat history section",
    )
    hq_arrival_note: str | None = Field(
        default=None,
        alias="hqArrivalNote",
        description="Jadwal kedatangan history section",
    )
    proposed_arrival_date: date | None = Field(
        default=None,
        alias="proposedArrivalDate",
        description=(
            "Branch-proposed HQ arrival date, still awaiting Pusat decision. "
            "Cleared once Pusat accepts/returns the escalation."
        ),
    )
    proposed_arrival_time: str | None = Field(
        default=None, alias="proposedArrivalTime"
    )
    proposed_by: str | None = Field(
        default=None,
        alias="proposedBy",
        description="Actor id of the branch officer who proposed the slot",
    )
    proposed_at: datetime | None = Field(default=None, alias="proposedAt")
    hq_return_note: str | None = Field(
        default=None,
        alias="hqReturnNote",
        description="Pengembalian Pusat history section (HQ return to branch)",
    )
    hq_completion_note: str | None = Field(
        default=None,
        alias="hqCompletionNote",
        description="Penyelesaian Pusat history section (HQ complete after visit)",
    )
    owning_unit_id: str | None = Field(
        default=None,
        alias="owningUnitId",
        description=(
            "Organization unit key for the Aggregate (Branch.code or PUSAT). "
            "Server-side list visibility SoT (DEC-024 pattern)."
        ),
    )
    priority: str | None = None
    created_at: datetime | None = Field(default=None, alias="createdAt")
    closed_at: datetime | None = Field(
        default=None,
        alias="closedAt",
        description="When the complaint reached CLOSED; cleared on reopen (DEC-031)",
    )
    sla: ComplaintSlaView | None = Field(
        default=None,
        description="Resolution SLA position; null when not measured (DEC-031)",
    )
    duplicate_check_result: str | None = Field(
        default=None, alias="duplicateCheckResult"
    )


class IntakeEscalationDecisionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    decision: Literal["APPROVE", "REJECT", "CANCEL"]
    note: str | None = Field(
        default=None,
        description=(
            "Required on APPROVE (≥20) — Catatan Supervisor for HQ. "
            "Required on REJECT (≥20) — Penolakan Eskalasi history. "
            "Required on CANCEL (≥20) — Batalkan Eskalasi history "
            "(only when ESCALATE_APPROVED and HQ has not accepted)."
        ),
        max_length=2000,
    )
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = Field(
        default=None,
        description=(
            "Required on APPROVE — Supervisor/Manager priority for HQ triage. "
            "Ignored on REJECT and CANCEL."
        ),
    )


class IntakeEscalationRequestBody(BaseModel):
    """Re-request escalate after CANCELLED / REJECTED (history append-only)."""

    model_config = ConfigDict(populate_by_name=True)

    reason: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description=(
            "Alasan eskalasi for ajuan ulang (≥20 after trim). "
            "Appended to Alasan eskalasi history; prior cancel/reject notes kept."
        ),
    )
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = Field(
        default=None,
        description="Optional HQ triage priority refresh on re-request.",
    )
    proposed_arrival_date: date | None = Field(
        default=None,
        alias="proposedArrivalDate",
        description="Branch-proposed HQ arrival date — advisory only.",
    )
    proposed_arrival_time: str | None = Field(
        default=None,
        alias="proposedArrivalTime",
        description="Branch-proposed HQ arrival time HH:MM, paired with proposedArrivalDate.",
    )


class HqAcceptRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    note: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional note (≥20 if provided) — Penerimaan Pusat history",
    )


class HqAcceptAndScheduleRequest(BaseModel):
    """Pusat accepts escalation, sets the final time **and** the unit (lab).

    Sets intakeDisposition=HQ_SCHEDULED — distinct from RETURNED_TO_BRANCH
    (incomplete package). The branch only ever *proposes* a slot; Pusat may
    keep or override it and then informs the taxpayer itself, so time and
    destination unit must both be decided here.
    """

    model_config = ConfigDict(populate_by_name=True)

    arrival_date: date = Field(alias="arrivalDate")
    arrival_time: str = Field(
        alias="arrivalTime",
        min_length=4,
        max_length=5,
        description="HH:MM (24h)",
    )
    destination_unit_id: str = Field(
        alias="destinationUnitId",
        min_length=1,
        max_length=128,
        description=(
            "Pusat unit the taxpayer reports to (PUSAT-CRO / PUSAT-SEKRE / "
            "PUSAT-SUBAN-…) — mandatory: Pusat is not one door"
        ),
    )
    note: str = Field(
        min_length=1,
        max_length=2000,
        description=(
            "Mandatory info for the taxpayer (min 10 after trim) — "
            "stored under Jadwal kedatangan / Penerimaan Pusat history"
        ),
    )


_HQ_RETURN_REASON_CODES = Literal[
    "MISSING_ATTACHMENT",
    "INCOMPLETE_CHRONOLOGY",
    "UNCLEAR_CUSTOMER_DATA",
    "WRONG_CATEGORY_OR_ROUTING",
    "ADDITIONAL_EVIDENCE_REQUIRED",
    "OTHER",
]


class HqReturnRequest(BaseModel):
    """Pusat returns approved escalation to originating branch (DEC-F4 lab)."""

    model_config = ConfigDict(populate_by_name=True)

    reason_code: _HQ_RETURN_REASON_CODES = Field(alias="reasonCode")
    note: str = Field(
        min_length=1,
        max_length=2000,
        description="Mandatory free-text note (min 10 after trim) — Pengembalian Pusat",
    )


class HqScheduleArrivalRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    arrival_date: date = Field(alias="arrivalDate")
    arrival_time: str = Field(
        alias="arrivalTime",
        min_length=4,
        max_length=5,
        description="HH:MM (24h)",
    )
    destination_unit_id: str | None = Field(
        default=None,
        alias="destinationUnitId",
        max_length=128,
        description=(
            "Redirect the taxpayer to another Pusat unit; omit to keep the "
            "current destination"
        ),
    )
    note: str | None = Field(default=None, max_length=2000)


class HqCompleteRequest(BaseModel):
    """Pusat completes the visit and closes the Aggregate (lab).

    Sets status=CLOSED and intakeDisposition=HQ_CLOSED. The visit stays listed
    on that day's HQ calendar with completed=true; live occupancy excludes it.
    """

    model_config = ConfigDict(populate_by_name=True)

    note: str = Field(
        min_length=1,
        max_length=2000,
        description="Mandatory completion note (min 10 after trim) — Penyelesaian Pusat",
    )


class DuplicateCheckRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    category: str | None = None
    subject: str | None = None
    channel: str | None = None


class DuplicateCheckResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    warning: bool = False
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    degraded: bool = False
    later_review_work_item_id: str | None = Field(
        default=None, alias="laterReviewWorkItemId"
    )


class DuplicateDecisionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    decision: Literal["link_existing", "override", "recommend_only", "blocked"]
    surviving_complaint_id: str | None = Field(
        default=None, alias="survivingComplaintId"
    )
    justification: str | None = None
    staging_token: str | None = Field(default=None, alias="stagingToken")
    customer_id: str | None = Field(default=None, alias="customerId")


class DuplicateDecisionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    decision_id: str = Field(alias="decisionId")
    decision: str
    customer_id: str = Field(alias="customerId")
    surviving_complaint_id: str | None = Field(
        default=None, alias="survivingComplaintId"
    )
    warning: bool = False
    hard_block: bool = Field(default=False, alias="hardBlock")
    case_created: Literal[False] = Field(default=False, alias="caseCreated")
    policy_version: str = Field(alias="policyVersion")
    created_at: datetime = Field(alias="createdAt")


class Batch1AttachmentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    attachment_id: str = Field(alias="attachmentId")
    platform_attachment_id: str = Field(alias="platformAttachmentId")
    status: Literal["STAGED", "ACTIVE", "TRANSFERRED", "VOID", "SUPERSEDED"]
    classification: str
    staging_token: str | None = Field(default=None, alias="stagingToken")
    complaint_id: str | None = Field(default=None, alias="complaintId")
    customer_id: str | None = Field(default=None, alias="customerId")
    case_id: str | None = Field(
        default=None,
        alias="caseId",
        description="Optional Case pin; Case MUST belong to complaintId (FR-004).",
    )
    original_name: str = Field(alias="originalName")
    mime_type: str = Field(alias="mimeType")
    size_bytes: int = Field(alias="sizeBytes")
    checksum_sha256: str = Field(alias="checksumSha256")
    supersedes_id: str | None = Field(default=None, alias="supersedesId")
    void_reason: str | None = Field(default=None, alias="voidReason")
    created_at: datetime = Field(alias="createdAt")


class TransferAttachmentsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    staging_token: str = Field(alias="stagingToken")
    surviving_complaint_id: str = Field(alias="survivingComplaintId")


class TransferAttachmentsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    staging_token: str = Field(alias="stagingToken")
    surviving_complaint_id: str = Field(alias="survivingComplaintId")
    transferred_count: int = Field(alias="transferredCount")
    attachments: list[Batch1AttachmentResponse] = Field(default_factory=list)
    discarded: Literal[False] = False


class VoidAttachmentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reason: str


class LaterReviewWorkItemResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    work_item_id: str = Field(alias="workItemId")
    customer_id: str = Field(alias="customerId")
    complaint_id: str | None = Field(default=None, alias="complaintId")
    reason: str
    status: str
    created_at: datetime = Field(alias="createdAt")
    age_hours: float = Field(alias="ageHours")


class AgingComplaintItemResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    customer_id: str = Field(alias="customerId")
    status: str
    subject: str | None = None
    priority: str | None = None
    created_at: datetime = Field(alias="createdAt")
    age_hours: float = Field(alias="ageHours")
    case_created: bool = Field(default=False, alias="caseCreated")


class IntakeHistoryEntry(BaseModel):
    """One chronological intake event (API-517 read model)."""

    model_config = ConfigDict(populate_by_name=True)

    entry_id: str = Field(alias="entryId")
    event_code: str = Field(
        alias="eventCode",
        description="Stable UI code, e.g. ESCALATION_APPROVED — label is client-side",
    )
    event_type: str = Field(alias="eventType")
    occurred_at: datetime = Field(alias="occurredAt")
    actor_id: str | None = Field(default=None, alias="actorId")
    actor_name: str | None = Field(default=None, alias="actorName")
    priority: str | None = None
    note: str | None = Field(
        default=None,
        description="Operator note captured with this event; null for older rows",
    )
    case_number: str | None = Field(
        default=None,
        alias="caseNumber",
        description="Case number when this event is scoped to one Case",
    )
    intake_action: str | None = Field(
        default=None,
        alias="intakeAction",
        description="Intake putusan when recorded on CaseCreated (register, close, escalate)",
    )
    arrival_date: str | None = Field(
        default=None,
        alias="arrivalDate",
        description=(
            "HQ taxpayer-visit calendar date (YYYY-MM-DD, Asia/Jakarta) when this "
            "event is HQ_ARRIVAL_SCHEDULED; not occurredAt"
        ),
    )
    arrival_time: str | None = Field(
        default=None,
        alias="arrivalTime",
        description="HQ taxpayer-visit clock time (HH:MM, 24h Asia/Jakarta)",
    )


class SupervisorQueueResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    later_review_items: list[LaterReviewWorkItemResponse] = Field(
        alias="laterReviewItems"
    )
    aging_complaints: list[AgingComplaintItemResponse] = Field(
        alias="agingComplaints"
    )
    aging_threshold_hours: int = Field(alias="agingThresholdHours")
    as_of: datetime = Field(alias="asOf")


class UserWorkStatsResponse(BaseModel):
    """Per-user complaint work counters for the Users directory panel (UM-BUG-006)."""

    model_config = ConfigDict(populate_by_name=True)

    created_count: int = Field(alias="createdCount")
    escalation_requested_count: int = Field(alias="escalationRequestedCount")
    escalation_approved_count: int = Field(alias="escalationApprovedCount")
    escalation_rejected_count: int = Field(alias="escalationRejectedCount")
