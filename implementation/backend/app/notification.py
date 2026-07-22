"""Notification consumer stub (FR-020 / S2-5).

Consumes drained outbox events in-process (ADR-009 §2). Writes idempotent rows to
notification_log. Failures are recorded (no silent drop) — not a generic framework.
"""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import NotificationLogModel

logger = logging.getLogger("ecmp.notification")

# FR-020: CaseAssigned is the required consumer; CaseCreated included for create→notify path.
_CONSUMED_EVENTS = frozenset({"EVT-001", "EVT-002"})


def _stub_channel_send(event_id: str, outbox_id: str, payload: dict) -> None:
    """Sink hook — replace/patch in tests; real channels land later without a framework."""
    logger.info(
        "notification stub delivered event=%s outbox=%s caseId=%s",
        event_id,
        outbox_id,
        payload.get("caseId"),
    )


def deliver_pending_notifications(
    session: Session,
    published: list[dict],
    *,
    now: datetime,
) -> list[dict]:
    """Deliver stub notifications for newly published outbox rows. Idempotent per outbox_id."""
    results: list[dict] = []
    for item in published:
        if item["id"] not in _CONSUMED_EVENTS:
            continue
        outbox_id = item["outboxId"]
        existing = (
            session.query(NotificationLogModel)
            .filter(NotificationLogModel.outbox_id == outbox_id)
            .one_or_none()
        )
        if existing is not None:
            results.append(
                {
                    "outboxId": outbox_id,
                    "status": existing.status,
                    "duplicate": True,
                }
            )
            continue

        payload = item.get("payload") or {}
        try:
            _stub_channel_send(item["id"], outbox_id, payload)
            session.add(
                NotificationLogModel(
                    notification_id=str(uuid4()),
                    outbox_id=outbox_id,
                    event_id=item["id"],
                    event_name=item["name"],
                    payload=payload,
                    status="DELIVERED",
                    error_message=None,
                    created_at=now,
                )
            )
            results.append({"outboxId": outbox_id, "status": "DELIVERED", "duplicate": False})
        except Exception as exc:  # noqa: BLE001 — must not silent-drop (FR-020)
            logger.exception("notification stub failed outbox=%s", outbox_id)
            session.add(
                NotificationLogModel(
                    notification_id=str(uuid4()),
                    outbox_id=outbox_id,
                    event_id=item["id"],
                    event_name=item["name"],
                    payload=payload,
                    status="FAILED",
                    error_message=str(exc)[:1000],
                    created_at=now,
                )
            )
            results.append({"outboxId": outbox_id, "status": "FAILED", "duplicate": False})
    return results
