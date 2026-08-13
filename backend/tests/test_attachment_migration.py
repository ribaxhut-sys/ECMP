"""CAPABILITY-011 — migration + repository/mapper tests."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from unittest.mock import MagicMock

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
from app.modules.attachment.models import AttachmentORM
from app.modules.attachment.repository import AttachmentRepository, _to_entity, _to_orm


def test_alembic_head_is_admin_rbac_repair() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    # Head advances with Identity/RBAC migrations; attachment revision stays on chain.
    assert script.get_heads() == ["0074_admin_no_complaint_create"]
    revisions = {r.revision for r in script.walk_revisions()}
    assert "0035_attachment_domain" in revisions
    assert "0036_search_indexes" in revisions


def test_migration_file_structure() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0035_attachment_domain.py"
    )
    text = path.read_text(encoding="utf-8")
    for needle in (
        'revision: str = "0035_attachment_domain"',
        "0034_timeline_entries",
        "aggregate_type",
        "aggregate_id",
        "checksum_sha256",
        "uploaded_at",
        "ix_attachments_aggregate_type",
        "ix_attachments_aggregate_id",
        "ix_attachments_uploaded_at",
        "ix_attachments_checksum_sha256",
        "status",
    ):
        assert needle in text


def test_orm_columns_and_indexes() -> None:
    cols = {c.name for c in AttachmentORM.__table__.columns}
    assert {
        "id",
        "aggregate_type",
        "aggregate_id",
        "file_name",
        "original_name",
        "mime_type",
        "extension",
        "size_bytes",
        "storage_provider",
        "storage_path",
        "checksum_sha256",
        "uploaded_by",
        "uploaded_at",
        "status",
    }.issubset(cols)
    assert "deleted_at" not in cols
    assert "object_type" not in cols
    assert "object_id" not in cols


def test_mapper_roundtrip() -> None:
    data = b"hello"
    entity = Attachment.create(
        aggregate_type=AggregateType.QUEUE.value,
        aggregate_id=uuid.uuid4(),
        file_name=f"{uuid.uuid4().hex}.txt",
        original_name="note.txt",
        mime_type="text/plain",
        extension=".txt",
        size_bytes=len(data),
        storage_provider="local",
        storage_path="2026/07/note.txt",
        checksum_sha256=hashlib.sha256(data).hexdigest(),
    )
    row = _to_orm(entity)
    assert isinstance(row, AttachmentORM)
    assert row.file_name == entity.file_name
    back = _to_entity(row)
    assert back.id == entity.id
    assert back.aggregate_type == AggregateType.QUEUE.value
    assert back.checksum_sha256 == entity.checksum_sha256


def test_repository_add_and_list_filters() -> None:
    session = MagicMock()
    session.scalar.return_value = 0
    session.scalars.return_value.all.return_value = []
    repo = AttachmentRepository(session)
    entity = Attachment.create(
        aggregate_type=AggregateType.NOTIFICATION.value,
        aggregate_id=uuid.uuid4(),
        file_name="a.pdf",
        original_name="a.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        size_bytes=1,
        storage_provider="local",
        storage_path="2026/07/a.pdf",
        checksum_sha256=hashlib.sha256(b"x").hexdigest(),
        status=AttachmentStatus.AVAILABLE.value,
    )
    saved = repo.add(entity)
    session.add.assert_called_once()
    session.flush.assert_called_once()
    assert saved.file_name == entity.file_name

    rows, total = repo.list(
        aggregate_type=AggregateType.NOTIFICATION.value,
        aggregate_id=entity.aggregate_id,
        page=1,
        page_size=10,
    )
    assert rows == []
    assert total == 0
