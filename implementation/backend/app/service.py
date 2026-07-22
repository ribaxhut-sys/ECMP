"""Application layer — business actions (ADR-005). No FastAPI imports allowed.

register_case implements FR-001/FR-001a/FR-001b/FR-001c.
assign_case implements FR-003 (API-003, EVT-002 + EVT-003).
change_status implements FR-004 (API-004, EVT-003 [+ EVT-005 on close]).
list_cases implements FR-005 (API-005) — read-only, no audit/outbox (BR-008 applies
to writes only; matches the existing get_case read path).
Case + immutable AuditLog (BR-008) + Outbox events (ADR-009) in ONE transaction.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.domain import workflow
from app.errors import (
    ForbiddenError,
    InvalidStateError,
    InvalidTransitionError,
    NotFoundError,
    ValidationAppError,
)
from app.models import AuditLogModel, CaseModel, CaseNoteModel, OutboxModel
from app.notification import deliver_pending_notifications


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(dt: datetime) -> datetime:
    # SQLite returns naive datetimes; all stored values are UTC by rule (FRD §7).
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _to_dict(case: CaseModel) -> dict:
    return {
        "caseId": case.case_id,
        "customerId": case.customer_id,
        "caseType": case.case_type,
        "priority": case.priority,
        "subject": case.subject,
        "description": case.description,
        "status": case.status,
        "channel": case.channel,
        "customerVerified": case.customer_verified,
        "assigneeId": case.assignee_id,
        "unitId": case.unit_id,
        "createdAt": _as_utc(case.created_at),
        "createdBy": case.created_by,
        "updatedAt": _as_utc(case.updated_at),
    }


def _get_case_or_404(session: Session, case_id: str) -> CaseModel:
    case = session.get(CaseModel, case_id)
    if case is None:
        raise NotFoundError(f"Case {case_id} not found")
    return case


def _add_outbox(
    session: Session,
    *,
    event_id: str,
    event_name: str,
    payload: dict,
    now: datetime,
) -> None:
    session.add(
        OutboxModel(
            outbox_id=str(uuid4()),
            event_id=event_id,
            event_name=event_name,
            payload=payload,
            created_at=now,
            published_at=None,
        )
    )


def _add_audit(
    session: Session,
    *,
    user_id: str,
    action: str,
    case_id: str,
    new_value: dict,
    now: datetime,
) -> None:
    session.add(
        AuditLogModel(
            log_id=str(uuid4()),
            actor_user_id=user_id,
            action=action,
            entity_type="Case",
            entity_id=case_id,
            new_value=new_value,
            occurred_at=now,
        )
    )


def register_case(session: Session, payload: dict, user: dict) -> dict:
    now = _utcnow()
    case_id = f"CASE-{uuid4().hex[:10].upper()}"
    user_id = user["userId"]

    case = CaseModel(
        case_id=case_id,
        customer_id=payload["customerId"],
        case_type=payload["caseType"],
        priority=payload["priority"],
        subject=payload["subject"],
        description=payload["description"],
        status="REGISTERED",  # BR-001 / FR-001a
        channel=payload.get("channel"),
        customer_verified=False,  # Customer Master stub mode (FRD §8, INT-001)
        assignee_id=None,
        unit_id=None,
        created_at=now,
        created_by=user_id,
        updated_at=now,
        updated_by=user_id,
    )

    event_payload = {
        "caseId": case_id,
        "customerId": payload["customerId"],
        "caseType": payload["caseType"],
        "priority": payload["priority"],
        "subject": payload["subject"],
        "status": "REGISTERED",
        "createdAt": now.isoformat(),
        "createdBy": user_id,
    }

    _add_audit(
        session,
        user_id=user_id,
        action="case.create",
        case_id=case_id,
        new_value=event_payload,
        now=now,
    )
    _add_outbox(
        session,
        event_id="EVT-001",
        event_name="CaseCreated",
        payload=event_payload,
        now=now,
    )

    session.add(case)
    session.commit()  # single transaction: case + audit + outbox
    return _to_dict(case)


def get_case(session: Session, case_id: str) -> dict | None:
    case = session.get(CaseModel, case_id)
    return _to_dict(case) if case is not None else None


def list_cases(
    session: Session,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
    priority: str | None = None,
    case_type: str | None = None,
    assignee_id: str | None = None,
) -> dict:
    """FR-005 / API-005: paginated, filtered list. Fixed sort createdAt desc
    (CTO decision, Sprint-03B design review — configurable sort out of scope).
    """
    query = session.query(CaseModel)
    if status is not None:
        query = query.filter(CaseModel.status == status)
    if priority is not None:
        query = query.filter(CaseModel.priority == priority)
    if case_type is not None:
        query = query.filter(CaseModel.case_type == case_type)
    if assignee_id is not None:
        query = query.filter(CaseModel.assignee_id == assignee_id)

    total_items = query.count()
    rows = (
        query.order_by(CaseModel.created_at.desc(), CaseModel.case_id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [_to_dict(row) for row in rows],
        "page": page,
        "pageSize": page_size,
        "totalItems": total_items,
    }


def _assert_assign_org_scope(case: CaseModel, user: dict, target_unit_id: str) -> None:
    """BR-002 / DEC-006 U-2: cross-unit only by supervisor of the case's owning unit."""
    supervised = set(user.get("supervisedUnitIds") or set())
    if target_unit_id not in supervised:
        raise ForbiddenError(
            f"Not authorized to assign for unit {target_unit_id} (BR-002)"
        )
    owning = case.unit_id
    if owning is not None and owning != target_unit_id and owning not in supervised:
        raise ForbiddenError(
            f"Cross-unit assignment denied for owning unit {owning} (BR-002)"
        )


def assign_case(session: Session, case_id: str, payload: dict, user: dict) -> dict:
    """FR-003 / API-003: assign or reassign; emits EVT-002 + EVT-003 in one transaction."""
    case = _get_case_or_404(session, case_id)
    assignee_id = payload["assigneeId"]
    unit_id = payload["unitId"]
    user_id = user["userId"]

    _assert_assign_org_scope(case, user, unit_id)

    if case.status not in workflow.assignable_statuses():
        raise InvalidStateError(
            f"Case status {case.status} is not assignable",
            details={"currentStatus": case.status},
        )

    now = _utcnow()
    from_status = case.status
    previous_assignee = case.assignee_id

    case.assignee_id = assignee_id
    case.unit_id = unit_id
    case.status = "ASSIGNED"
    case.updated_at = now
    case.updated_by = user_id

    assigned_at = now.isoformat()
    evt002 = {
        "caseId": case_id,
        "assigneeId": assignee_id,
        "unitId": unit_id,
        "assignedBy": user_id,
        "previousAssigneeId": previous_assignee,
        "assignedAt": assigned_at,
    }
    evt003 = {
        "caseId": case_id,
        "fromStatus": from_status,
        "toStatus": "ASSIGNED",
        "changedBy": user_id,
        "changedAt": assigned_at,
        "reason": None,
    }

    _add_audit(
        session,
        user_id=user_id,
        action="case.assign",
        case_id=case_id,
        new_value={"assigneeId": assignee_id, "unitId": unit_id, "status": "ASSIGNED"},
        now=now,
    )
    _add_outbox(session, event_id="EVT-002", event_name="CaseAssigned", payload=evt002, now=now)
    _add_outbox(session, event_id="EVT-003", event_name="StatusChanged", payload=evt003, now=now)

    session.commit()
    return _to_dict(case)


def change_status(session: Session, case_id: str, payload: dict, user: dict) -> dict:
    """FR-004 / API-004: transition via active workflow config; emit EVT-003 (+ extras)."""
    case = _get_case_or_404(session, case_id)
    to_status = payload["toStatus"]
    reason = payload.get("reason")
    resolution_code = payload.get("resolutionCode")
    user_id = user["userId"]
    from_status = case.status

    # BR-ECMF-06 defense in depth (also enforced by StatusChangeRequest schema).
    if workflow.requires_resolution_code(to_status):
        if not (resolution_code and str(resolution_code).strip()):
            raise ValidationAppError(
                "resolutionCode is required when toStatus is CLOSED",
                details={"toStatus": to_status},
            )

    # BR-ECMF-07 / BR-ECMF-03: reason mandatory for reopen and admin override (domain rule).
    is_admin_override = "admin:override" in set(user.get("permissions") or set())
    if workflow.requires_reason(from_status, to_status, is_admin_override=is_admin_override):
        if not (reason and str(reason).strip()):
            raise ValidationAppError(
                "reason is required for this transition",
                details={"fromStatus": from_status, "toStatus": to_status},
            )

    rule = workflow.transition_rule(from_status, to_status)
    if rule is None:
        raise InvalidTransitionError(
            f"Transition {from_status}→{to_status} is not allowed",
            details={"fromStatus": from_status, "toStatus": to_status},
        )

    # Per-transition guard: start handling — assignee or supervisor of owning unit.
    if from_status == "ASSIGNED" and to_status == "IN_PROGRESS":
        supervised = set(user.get("supervisedUnitIds") or set())
        is_assignee = case.assignee_id == user_id
        is_unit_supervisor = case.unit_id is not None and case.unit_id in supervised
        if not (is_assignee or is_unit_supervisor):
            raise ForbiddenError("Only the assignee or unit supervisor may start handling")

    now = _utcnow()
    case.status = to_status
    case.updated_at = now
    case.updated_by = user_id

    changed_at = now.isoformat()
    evt003 = {
        "caseId": case_id,
        "fromStatus": from_status,
        "toStatus": to_status,
        "changedBy": user_id,
        "changedAt": changed_at,
        "reason": reason,
    }
    audit_value: dict = {"fromStatus": from_status, "toStatus": to_status, "reason": reason}
    if to_status == "CLOSED":
        audit_value["resolutionCode"] = resolution_code

    _add_audit(
        session,
        user_id=user_id,
        action="case.status_change",
        case_id=case_id,
        new_value=audit_value,
        now=now,
    )
    _add_outbox(session, event_id="EVT-003", event_name="StatusChanged", payload=evt003, now=now)

    if "EVT-005" in rule.extra_events:
        _add_outbox(
            session,
            event_id="EVT-005",
            event_name="CaseClosed",
            payload={
                "caseId": case_id,
                "resolutionCode": resolution_code,
                "closedBy": user_id,
                "closedAt": changed_at,
            },
            now=now,
        )

    session.commit()
    return _to_dict(case)


def list_outbox_events(session: Session, limit: int = 100) -> list[dict]:
    rows = session.query(OutboxModel).order_by(OutboxModel.created_at).limit(limit).all()
    return [
        {
            "id": r.event_id,
            "name": r.event_name,
            "payload": r.payload,
            "publishedAt": _as_utc(r.published_at).isoformat() if r.published_at else None,
        }
        for r in rows
    ]


def _timeline_summary(action: str, new_value: dict) -> str:
    """Curated narrative for Timeline UI; Audit History uses raw detail instead."""
    if action == "case.create":
        return "Case created"
    if action == "case.assign":
        assignee = new_value.get("assigneeId") or "unknown"
        unit = new_value.get("unitId")
        if unit:
            return f"Assigned to {assignee} ({unit})"
        return f"Assigned to {assignee}"
    if action == "case.status_change":
        to_status = new_value.get("toStatus") or "unknown"
        from_status = new_value.get("fromStatus")
        if from_status:
            return f"Status changed from {from_status} to {to_status}"
        return f"Status changed to {to_status}"
    return action


def get_case_timeline(session: Session, case_id: str) -> dict:
    """API-006: read-only projection of audit_log for Timeline + Audit History."""
    _get_case_or_404(session, case_id)
    rows = (
        session.query(AuditLogModel)
        .filter(
            AuditLogModel.entity_type == "Case",
            AuditLogModel.entity_id == case_id,
        )
        .order_by(AuditLogModel.occurred_at.asc(), AuditLogModel.log_id.asc())
        .all()
    )
    return {
        "entries": [
            {
                "entryId": row.log_id,
                "actionCode": row.action,
                "actorUserId": row.actor_user_id,
                "occurredAt": _as_utc(row.occurred_at),
                "summary": _timeline_summary(row.action, row.new_value or {}),
                "detail": row.new_value or {},
            }
            for row in rows
        ]
    }


def _note_to_dict(note: CaseNoteModel) -> dict:
    return {
        "noteId": note.note_id,
        "caseId": note.case_id,
        "authorUserId": note.author_user_id,
        "body": note.body,
        "createdAt": _as_utc(note.created_at),
    }


def list_case_notes(session: Session, case_id: str) -> dict:
    """API-007: append-only notes list, chronological ascending."""
    _get_case_or_404(session, case_id)
    rows = (
        session.query(CaseNoteModel)
        .filter(CaseNoteModel.case_id == case_id)
        .order_by(CaseNoteModel.created_at.asc(), CaseNoteModel.note_id.asc())
        .all()
    )
    return {"items": [_note_to_dict(r) for r in rows]}


def add_case_note(session: Session, case_id: str, payload: dict, user: dict) -> dict:
    """API-008: append-only note create (no update/delete path)."""
    _get_case_or_404(session, case_id)
    body = str(payload.get("body") or "").strip()
    if not body:
        raise ValidationAppError(
            "body is required",
            details={"body": "must not be empty"},
        )
    now = _utcnow()
    note = CaseNoteModel(
        note_id=str(uuid4()),
        case_id=case_id,
        author_user_id=user["userId"],
        body=body,
        created_at=now,
    )
    session.add(note)
    session.commit()
    return _note_to_dict(note)


def drain_outbox(session: Session, limit: int = 100) -> list[dict]:
    """Minimal in-process publisher (ADR-009 §2, DEV phase) + notification stub (FR-020).

    Marks pending rows as published (logging publisher: no broker exists yet).
    Notification stub consumes CaseAssigned (and CaseCreated) without silent drop.
    """
    now = _utcnow()
    rows = (
        session.query(OutboxModel)
        .filter(OutboxModel.published_at.is_(None))
        .order_by(OutboxModel.created_at)
        .limit(limit)
        .all()
    )
    published = []
    for r in rows:
        r.published_at = now
        published.append(
            {
                "id": r.event_id,
                "name": r.event_name,
                "outboxId": r.outbox_id,
                "payload": r.payload,
            }
        )
    deliver_pending_notifications(session, published, now=now)
    session.commit()
    return [{"id": p["id"], "name": p["name"], "outboxId": p["outboxId"]} for p in published]
