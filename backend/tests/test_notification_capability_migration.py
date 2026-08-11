"""CAPABILITY-009 — migration + repository smoke tests."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.core.enums import NotificationChannel, NotificationQueueStatus
from app.modules.notification.domain.entity import NotificationRecord
from app.modules.notification.mappers import new_queue_row, to_record
from app.modules.notification.models import NotificationQueue


def test_alembic_chain_includes_notification_domain() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    revisions = {r.revision for r in script.walk_revisions()}
    assert "0033_notification_domain" in revisions
    assert "0036_search_indexes" in revisions
    # Head advances after search indexes (0037–0039); notification stays on chain.
    assert script.get_heads() == ["0071_knowledge_files"]


def test_migration_file_defines_required_indexes_and_columns() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0033_notification_domain.py"
    )
    text = path.read_text(encoding="utf-8")
    for needle in (
        "notification_type",
        "channel",
        "subject",
        "message",
        "failed_at",
        "ix_notification_queue_channel",
        "ix_notification_queue_recipient",
        "0032_complaint_sla",
    ):
        assert needle in text


def test_mapper_roundtrip_entity_to_orm() -> None:
    record = NotificationRecord.create(
        channel=NotificationChannel.WHATSAPP.value,
        recipient="wa:+1000",
        notification_type="ComplaintAssigned",
        subject="Assigned",
        message="You have a case",
        template="complaint.assigned",
        payload={"complaintId": str(uuid.uuid4())},
    )
    row = new_queue_row(record)
    assert isinstance(row, NotificationQueue)
    assert row.channel == NotificationChannel.WHATSAPP.value
    assert row.status == NotificationQueueStatus.PENDING.value

    back = to_record(row)
    assert back.id == record.id
    assert back.message == "You have a case"
    assert back.created_at.tzinfo is not None or isinstance(
        back.created_at, datetime
    )


def test_notification_queue_model_has_capability_009_columns() -> None:
    cols = {c.name for c in NotificationQueue.__table__.columns}
    assert {
        "notification_type",
        "channel",
        "subject",
        "message",
        "failed_at",
        "status",
        "recipient",
        "created_at",
    }.issubset(cols)
    index_names = {idx.name for idx in NotificationQueue.__table__.indexes}
    assert "ix_notification_queue_status" in index_names
    assert "ix_notification_queue_channel" in index_names
    assert "ix_notification_queue_recipient" in index_names
    assert "ix_notification_queue_created_at" in index_names
