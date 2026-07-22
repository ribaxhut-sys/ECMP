"""Notification stub unit tests (FR-020)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db import get_engine
from app.models import NotificationLogModel
from app.notification import deliver_pending_notifications


def test_notification_idempotent_per_outbox_id():
    now = datetime.now(timezone.utc)
    outbox_id = str(uuid4())
    item = {
        "id": "EVT-002",
        "name": "CaseAssigned",
        "outboxId": outbox_id,
        "payload": {"caseId": "CASE-1"},
    }
    with Session(get_engine()) as session:
        first = deliver_pending_notifications(session, [item], now=now)
        session.commit()
        assert first[0]["status"] == "DELIVERED"
        assert first[0]["duplicate"] is False

        second = deliver_pending_notifications(session, [item], now=now)
        session.commit()
        assert second[0]["duplicate"] is True
        assert session.query(NotificationLogModel).count() == 1


def test_notification_failure_is_recorded_not_silent(monkeypatch):
    now = datetime.now(timezone.utc)
    outbox_id = str(uuid4())
    item = {
        "id": "EVT-002",
        "name": "CaseAssigned",
        "outboxId": outbox_id,
        "payload": {"caseId": "CASE-1"},
    }

    def boom(*_args, **_kwargs):
        raise RuntimeError("sink down")

    monkeypatch.setattr("app.notification._stub_channel_send", boom)

    with Session(get_engine()) as session:
        results = deliver_pending_notifications(session, [item], now=now)
        session.commit()
        assert results[0]["status"] == "FAILED"
        row = session.query(NotificationLogModel).one()
        assert row.status == "FAILED"
        assert "sink down" in (row.error_message or "")


def test_non_consumed_events_skipped():
    now = datetime.now(timezone.utc)
    item = {
        "id": "EVT-003",
        "name": "StatusChanged",
        "outboxId": str(uuid4()),
        "payload": {},
    }
    with Session(get_engine()) as session:
        assert deliver_pending_notifications(session, [item], now=now) == []
        assert session.query(NotificationLogModel).count() == 0
