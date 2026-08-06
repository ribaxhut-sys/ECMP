"""Factories that map Batch 1 operations → DomainEvent (catalog EVT-CM-* only)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.modules.cm_batch1.domain_events import DomainEvent


def complaint_created(
    *,
    complaint_id: str,
    complaint_number: str,
    customer_id: str,
    request_id: str,
    channel_message_id: str | None,
    actor_id: str | None,
    created_at: datetime | None = None,
    recording_unit_id: str | None = None,
) -> DomainEvent:
    now = created_at or datetime.now(UTC)
    after = {
        "complaintId": complaint_id,
        "complaintNumber": complaint_number,
        "customerId": customer_id,
        "status": "REGISTERED",
        "requestId": request_id,
        "channelMessageId": channel_message_id,
        "createdAt": now.isoformat(),
        "createdBy": actor_id,
        "recordingUnitId": (recording_unit_id or "").strip() or None,
    }
    return DomainEvent(
        name="ComplaintCreated",
        aggregate_type="Complaint",
        aggregate_id=complaint_id,
        actor_id=actor_id,
        payload=after,
        idempotency_key=f"EVT-CM-001:{complaint_id}",
        audit_operation="ComplaintCreated",
        audit_action="CREATE",
        after=after,
        timeline_event_type="ComplaintRegistered",
        timeline_title="Complaint Registered",
        timeline_description=f"Complaint {complaint_number} registered",
        timeline_metadata={"complaintNumber": complaint_number, "customerId": customer_id},
        outbox_event_id="EVT-CM-001",
        occurred_at=now,
    )


def create_replayed(
    *,
    complaint_id: str,
    request_id: str,
    channel_message_id: str | None,
    actor_id: str | None,
) -> DomainEvent:
    now = datetime.now(UTC)
    payload = {
        "complaintId": complaint_id,
        "requestId": request_id,
        "channelMessageId": channel_message_id,
        "replayedAt": now.isoformat(),
        "actorId": actor_id,
    }
    return DomainEvent(
        name="CreateReplayed",
        aggregate_type="Complaint",
        aggregate_id=complaint_id,
        actor_id=actor_id,
        payload=payload,
        # Stable per requestId — repeated replays do not duplicate side effects.
        idempotency_key=f"EVT-CM-002:{request_id}",
        audit_operation="CreateReplayed",
        audit_action="CREATE",
        after=payload,
        timeline_event_type=None,
        timeline_title=None,
        outbox_event_id="EVT-CM-002",
        occurred_at=now,
    )


def duplicate_warned(
    *,
    customer_id: str,
    candidate_count: int,
    actor_id: str | None,
    aggregate_id: str | None = None,
) -> DomainEvent:
    now = datetime.now(UTC)
    payload = {
        "customerId": customer_id,
        "candidateCount": candidate_count,
        "warnedAt": now.isoformat(),
    }
    # Deduplicate warn bursts within same second bucket for same customer.
    key = f"EVT-CM-020:{customer_id}:{now.strftime('%Y%m%d%H%M%S')}"
    return DomainEvent(
        name="DuplicateWarned",
        aggregate_type="Complaint",
        aggregate_id=aggregate_id or customer_id,
        actor_id=actor_id,
        payload=payload,
        idempotency_key=key,
        audit_operation="DuplicateWarned",
        audit_action="CREATE",
        after=payload,
        timeline_event_type="DuplicateFound",
        timeline_title="Duplicate Found",
        timeline_description=f"{candidate_count} duplicate candidate(s) detected",
        timeline_metadata={"customerId": customer_id, "candidateCount": candidate_count},
        outbox_event_id="EVT-CM-020",
        occurred_at=now,
    )


def duplicate_check_degraded(
    *,
    customer_id: str,
    work_item_id: str | None,
    actor_id: str | None,
    reason: str = "index_unavailable",
) -> list[DomainEvent]:
    now = datetime.now(UTC)
    events: list[DomainEvent] = []
    payload_025 = {
        "degradedFlag": True,
        "reason": reason,
        "occurredAt": now.isoformat(),
    }
    events.append(
        DomainEvent(
            name="DuplicateCheckDegraded",
            aggregate_type="Complaint",
            aggregate_id=customer_id,
            actor_id=actor_id,
            payload=payload_025,
            idempotency_key=f"EVT-CM-025:{customer_id}:{work_item_id or now.isoformat()}",
            audit_operation="DuplicateCheckDegraded",
            audit_action="CREATE",
            after=payload_025,
            outbox_event_id="EVT-CM-025",
            occurred_at=now,
        )
    )
    if work_item_id:
        payload_026 = {
            "workItemId": work_item_id,
            "customerId": customer_id,
            "enqueuedAt": now.isoformat(),
        }
        events.append(
            DomainEvent(
                name="DuplicateLaterReviewEnqueued",
                aggregate_type="Complaint",
                aggregate_id=customer_id,
                actor_id=actor_id,
                payload=payload_026,
                idempotency_key=f"EVT-CM-026:{work_item_id}",
                audit_operation="DuplicateLaterReviewEnqueued",
                audit_action="CREATE",
                after=payload_026,
                outbox_event_id="EVT-CM-026",
                occurred_at=now,
            )
        )
    return events


def duplicate_decision_events(
    *,
    decision: str,
    customer_id: str,
    surviving_complaint_id: str | None,
    actor_id: str | None,
    decision_id: str,
    justification_present: bool,
) -> list[DomainEvent]:
    """Map API-506 decisions → catalog EVT-CM-021…024 (+ audit/timeline)."""
    now = datetime.now(UTC)
    aggregate_id = surviving_complaint_id or customer_id
    events: list[DomainEvent] = []

    def _base_after(extra: dict[str, Any]) -> dict[str, Any]:
        body: dict[str, Any] = {
            "decision": decision,
            "customerId": customer_id,
            "decisionId": decision_id,
            "recordedAt": now.isoformat(),
            "actorId": actor_id,
            **extra,
        }
        if surviving_complaint_id:
            body["survivingComplaintId"] = surviving_complaint_id
            body["targetComplaintId"] = surviving_complaint_id
            body["existingComplaintId"] = surviving_complaint_id
        return body

    if decision == "override":
        after = _base_after(
            {
                "justificationRef": (
                    f"decision:{decision_id}" if justification_present else None
                ),
                "complaintId": surviving_complaint_id or customer_id,
                "overriddenAt": now.isoformat(),
            }
        )
        events.append(
            DomainEvent(
                name="DuplicateOverridden",
                aggregate_type="Complaint",
                aggregate_id=aggregate_id,
                actor_id=actor_id,
                payload=after,
                idempotency_key=f"EVT-CM-021:{decision_id}",
                audit_operation="DuplicateDecision:override",
                after=after,
                timeline_event_type="DuplicateOverridden",
                timeline_title="Duplicate Overridden",
                timeline_description="Override with justification recorded",
                timeline_metadata={
                    "decision": decision,
                    "customerId": customer_id,
                    "justificationPresent": justification_present,
                },
                outbox_event_id="EVT-CM-021",
                occurred_at=now,
            )
        )
    elif decision == "link_existing":
        linked = _base_after(
            {
                "sourceComplaintId": None,
                "linkType": "possible-duplicate",
                "linkedAt": now.isoformat(),
            }
        )
        events.append(
            DomainEvent(
                name="DuplicateLinked",
                aggregate_type="Complaint",
                aggregate_id=aggregate_id,
                actor_id=actor_id,
                payload=linked,
                idempotency_key=f"EVT-CM-022:{decision_id}",
                audit_operation="DuplicateDecision:link_existing",
                after=linked,
                timeline_event_type="DuplicateLinked",
                timeline_title="Duplicate Linked",
                timeline_description="Possible-duplicate linkage recorded",
                timeline_metadata={
                    "decision": decision,
                    "customerId": customer_id,
                    "survivingComplaintId": surviving_complaint_id,
                },
                outbox_event_id="EVT-CM-022",
                occurred_at=now,
            )
        )
        redirected = {
            "survivingComplaintId": surviving_complaint_id,
            "actorId": actor_id,
            "redirectedAt": now.isoformat(),
            "decisionId": decision_id,
        }
        events.append(
            DomainEvent(
                name="DuplicateRedirectedToExisting",
                aggregate_type="Complaint",
                aggregate_id=aggregate_id,
                actor_id=actor_id,
                payload=redirected,
                idempotency_key=f"EVT-CM-023:{decision_id}",
                audit_operation="DuplicateDecision:redirect",
                after=redirected,
                timeline_event_type="DuplicateRedirected",
                timeline_title="Duplicate Redirected",
                timeline_description="Redirect decision to existing Complaint",
                timeline_metadata={
                    "decision": decision,
                    "survivingComplaintId": surviving_complaint_id,
                },
                outbox_event_id="EVT-CM-023",
                occurred_at=now,
            )
        )
    elif decision == "recommend_only":
        after = _base_after(
            {
                "recommendation": "continue_on_existing",
                "recommendedAt": now.isoformat(),
            }
        )
        events.append(
            DomainEvent(
                name="DuplicateRecommendedExisting",
                aggregate_type="Complaint",
                aggregate_id=aggregate_id,
                actor_id=actor_id,
                payload=after,
                idempotency_key=f"EVT-CM-024:{decision_id}",
                audit_operation="DuplicateDecision:recommend_only",
                after=after,
                timeline_event_type="DuplicateRecommended",
                timeline_title="Duplicate Recommended",
                timeline_description="Recommend continue on existing Complaint",
                timeline_metadata={
                    "decision": decision,
                    "customerId": customer_id,
                    "survivingComplaintId": surviving_complaint_id,
                },
                outbox_event_id="EVT-CM-024",
                occurred_at=now,
            )
        )
    elif decision == "blocked":
        after = _base_after({"blockedAt": now.isoformat(), "hardBlock": True})
        events.append(
            DomainEvent(
                name="DuplicateDecisionBlocked",
                aggregate_type="Complaint",
                aggregate_id=aggregate_id,
                actor_id=actor_id,
                payload=after,
                idempotency_key=f"AUDIT:blocked:{decision_id}",
                audit_operation="DuplicateDecision:blocked",
                after=after,
                timeline_event_type="DuplicateBlocked",
                timeline_title="Duplicate Hard Blocked",
                timeline_description="Hard-block decision recorded",
                timeline_metadata={
                    "decision": decision,
                    "customerId": customer_id,
                },
                outbox_event_id=None,
                occurred_at=now,
            )
        )
    return events


# Back-compat single-event helper (first mapped event).
def duplicate_decision(
    *,
    decision: str,
    customer_id: str,
    surviving_complaint_id: str | None,
    actor_id: str | None,
    decision_id: str,
    justification_present: bool,
) -> DomainEvent:
    events = duplicate_decision_events(
        decision=decision,
        customer_id=customer_id,
        surviving_complaint_id=surviving_complaint_id,
        actor_id=actor_id,
        decision_id=decision_id,
        justification_present=justification_present,
    )
    if not events:
        raise ValueError(f"unsupported duplicate decision: {decision}")
    return events[0]


def attachment_uploaded(
    *,
    attachment_id: str,
    complaint_id: str | None,
    checksum: str,
    actor_id: str | None,
    status: str,
) -> DomainEvent:
    now = datetime.now(UTC)
    payload = {
        "attachmentId": attachment_id,
        "complaintId": complaint_id,
        "integrityHash": checksum,
        "uploadedAt": now.isoformat(),
        "status": status,
    }
    return DomainEvent(
        name="AttachmentUploaded",
        aggregate_type="Complaint",
        aggregate_id=complaint_id or attachment_id,
        actor_id=actor_id,
        payload=payload,
        idempotency_key=f"EVT-CM-030:{attachment_id}",
        audit_operation="AttachmentUploaded",
        audit_action="CREATE",
        after=payload,
        timeline_event_type="AttachmentUploaded",
        timeline_title="Attachment Uploaded",
        timeline_description=None if complaint_id is None else "Evidence uploaded",
        timeline_metadata={"attachmentId": attachment_id, "status": status},
        outbox_event_id="EVT-CM-030",
        occurred_at=now,
    )


def attachment_bound(
    *,
    attachment_id: str,
    complaint_id: str,
    actor_id: str | None,
) -> DomainEvent:
    now = datetime.now(UTC)
    payload = {
        "attachmentId": attachment_id,
        "complaintId": complaint_id,
        "boundAt": now.isoformat(),
    }
    return DomainEvent(
        name="AttachmentBound",
        aggregate_type="Complaint",
        aggregate_id=complaint_id,
        actor_id=actor_id,
        payload=payload,
        idempotency_key=f"AttachmentBound:{attachment_id}:{complaint_id}",
        audit_operation="AttachmentBound",
        audit_action="UPDATE",
        after=payload,
        timeline_event_type="AttachmentBound",
        timeline_title="Attachment Bound",
        timeline_metadata={"attachmentId": attachment_id},
        outbox_event_id=None,  # no dedicated EVT-CM for bind in catalog
        occurred_at=now,
    )


def attachment_superseded(
    *,
    attachment_id: str,
    superseded_attachment_id: str,
    complaint_id: str | None,
    actor_id: str | None,
) -> DomainEvent:
    now = datetime.now(UTC)
    payload = {
        "attachmentId": attachment_id,
        "supersededAttachmentId": superseded_attachment_id,
        "supersededAt": now.isoformat(),
    }
    return DomainEvent(
        name="AttachmentSuperseded",
        aggregate_type="Complaint",
        aggregate_id=complaint_id or attachment_id,
        actor_id=actor_id,
        payload=payload,
        idempotency_key=f"EVT-CM-031:{attachment_id}:{superseded_attachment_id}",
        audit_operation="AttachmentSuperseded",
        audit_action="UPDATE",
        after=payload,
        timeline_event_type="AttachmentSuperseded",
        timeline_title="Attachment Superseded",
        timeline_metadata=payload,
        outbox_event_id="EVT-CM-031",
        occurred_at=now,
    )


def attachment_voided(
    *,
    attachment_id: str,
    reason: str,
    complaint_id: str | None,
    actor_id: str | None,
) -> DomainEvent:
    now = datetime.now(UTC)
    payload = {
        "attachmentId": attachment_id,
        "reason": reason,
        "voidedAt": now.isoformat(),
        "actorId": actor_id,
    }
    return DomainEvent(
        name="AttachmentVoided",
        aggregate_type="Complaint",
        aggregate_id=complaint_id or attachment_id,
        actor_id=actor_id,
        payload=payload,
        idempotency_key=f"EVT-CM-032:{attachment_id}",
        audit_operation="AttachmentVoided",
        audit_action="DELETE",
        after=payload,
        timeline_event_type="AttachmentVoided",
        timeline_title="Attachment Voided",
        timeline_metadata={"attachmentId": attachment_id},
        outbox_event_id="EVT-CM-032",
        occurred_at=now,
    )


def attachment_transferred(
    *,
    attachment_id: str,
    staging_token: str,
    surviving_complaint_id: str,
    actor_id: str | None,
) -> DomainEvent:
    now = datetime.now(UTC)
    payload = {
        "attachmentId": attachment_id,
        "fromStagingToken": staging_token,
        "survivingComplaintId": surviving_complaint_id,
        "transferredAt": now.isoformat(),
    }
    return DomainEvent(
        name="AttachmentTransferred",
        aggregate_type="Complaint",
        aggregate_id=surviving_complaint_id,
        actor_id=actor_id,
        payload=payload,
        idempotency_key=f"EVT-CM-033:{attachment_id}:{surviving_complaint_id}",
        audit_operation="AttachmentTransferred",
        audit_action="UPDATE",
        after=payload,
        timeline_event_type="AttachmentTransferred",
        timeline_title="Attachment Transferred",
        timeline_description="Staged evidence transferred (D-06)",
        timeline_metadata=payload,
        outbox_event_id="EVT-CM-033",
        occurred_at=now,
    )


def intake_escalation_decided(
    *,
    complaint_id: str,
    complaint_number: str,
    decision: str,
    next_disposition: str,
    actor_id: str | None,
    note_present: bool,
) -> DomainEvent:
    """Audit/timeline only — no EVT-CM catalog row for intake escalation decision."""
    now = datetime.now(UTC)
    payload = {
        "complaintId": complaint_id,
        "complaintNumber": complaint_number,
        "decision": decision,
        "intakeDisposition": next_disposition,
        "notePresent": note_present,
        "decidedAt": now.isoformat(),
        "actorId": actor_id,
    }
    title = (
        "Intake Escalation Approved"
        if decision == "APPROVE"
        else "Intake Escalation Rejected"
    )
    return DomainEvent(
        name="IntakeEscalationDecided",
        aggregate_type="Complaint",
        aggregate_id=complaint_id,
        actor_id=actor_id,
        payload=payload,
        idempotency_key=f"IntakeEscalationDecided:{complaint_id}:{decision}:{now.isoformat()}",
        audit_operation=f"IntakeEscalation:{decision}",
        audit_action="UPDATE",
        after=payload,
        timeline_event_type="IntakeEscalationDecided",
        timeline_title=title,
        timeline_description=(
            f"Complaint {complaint_number} intake escalation {decision.lower()}"
        ),
        timeline_metadata={
            "decision": decision,
            "intakeDisposition": next_disposition,
        },
        outbox_event_id=None,
        occurred_at=now,
    )
