"""CAPABILITY-010 — migration + repository/mapper tests."""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import MagicMock

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.domain.enums import AggregateType, TimelineEventType
from app.modules.timeline.models import TimelineEntryORM
from app.modules.timeline.repository import TimelineRepository, _to_entity, _to_orm


def test_alembic_head_includes_timeline_entries() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    # Head moves forward; timeline revision must remain on the linear chain.
    assert "0034_timeline_entries" in {r.revision for r in script.walk_revisions()}
    assert script.get_heads() == ["0044_admin_rbac_repair"]


def test_migration_file_structure() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0034_timeline_entries.py"
    )
    text = path.read_text(encoding="utf-8")
    for needle in (
        'revision: str = "0034_timeline_entries"',
        "0033_notification_domain",
        "timeline_entries",
        "ix_timeline_entries_aggregate_type",
        "ix_timeline_entries_aggregate_id",
        "ix_timeline_entries_event_type",
        "ix_timeline_entries_created_at",
        "timeline:read",
        "timeline:create",
    ):
        assert needle in text


def test_orm_columns_and_indexes() -> None:
    cols = {c.name for c in TimelineEntryORM.__table__.columns}
    assert {
        "id",
        "aggregate_type",
        "aggregate_id",
        "event_type",
        "title",
        "description",
        "actor_type",
        "actor_id",
        "actor_name",
        "metadata",
        "created_at",
    }.issubset(cols)
    # No soft-delete / updated_at — append-only
    assert "deleted_at" not in cols
    assert "updated_at" not in cols


def test_mapper_roundtrip() -> None:
    entry = TimelineEntry.create(
        aggregate_type=AggregateType.QUEUE.value,
        aggregate_id=uuid.uuid4(),
        event_type="QueueOpened",
        title="Queue opened",
        metadata={"n": 1},
    )
    row = _to_orm(entry)
    assert isinstance(row, TimelineEntryORM)
    assert row.metadata_json == {"n": 1}
    back = _to_entity(row)
    assert back.id == entry.id
    assert back.aggregate_type == AggregateType.QUEUE.value


def test_repository_add_uses_session() -> None:
    session = MagicMock()
    repo = TimelineRepository(session)
    entry = TimelineEntry.create(
        aggregate_type=AggregateType.NOTIFICATION.value,
        aggregate_id=uuid.uuid4(),
        event_type=TimelineEventType.NOTIFICATION_CREATED.value,
        title="Notification created",
    )
    saved = repo.add(entry)
    session.add.assert_called_once()
    session.flush.assert_called_once()
    assert saved.event_type == entry.event_type
