"""Application layer — business actions (ADR-005). No FastAPI imports allowed.

register_case implements FR-001/FR-001a/FR-001b/FR-001c:
Case + immutable AuditLog (BR-008) + Outbox event (ADR-009) in ONE transaction.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import AuditLogModel, CaseModel, OutboxModel


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
        "createdAt": _as_utc(case.created_at),
        "createdBy": case.created_by,
        "updatedAt": _as_utc(case.updated_at),
    }


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

    audit = AuditLogModel(
        log_id=str(uuid4()),
        actor_user_id=user_id,
        action="case.create",
        entity_type="Case",
        entity_id=case_id,
        new_value=event_payload,
        occurred_at=now,
    )

    outbox = OutboxModel(
        outbox_id=str(uuid4()),
        event_id="EVT-001",
        event_name="CaseCreated",
        payload=event_payload,
        created_at=now,
        published_at=None,
    )

    session.add_all([case, audit, outbox])
    session.commit()  # single transaction: case + audit + outbox
    return _to_dict(case)


def get_case(session: Session, case_id: str) -> dict | None:
    case = session.get(CaseModel, case_id)
    return _to_dict(case) if case is not None else None


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


def drain_outbox(session: Session, limit: int = 100) -> list[dict]:
    """Minimal in-process publisher (ADR-009 §2, DEV phase).

    Marks pending rows as published (logging publisher: no broker exists yet).
    Real broker delivery replaces this at the ADR-009 revisit trigger.
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
        published.append({"id": r.event_id, "name": r.event_name, "outboxId": r.outbox_id})
    session.commit()
    return published
