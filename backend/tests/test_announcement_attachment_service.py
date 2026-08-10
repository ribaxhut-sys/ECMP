"""Unit tests for announcement attachment link / remove (mocked)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.announcement.attachment_service import AnnouncementAttachmentService
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus


def _platform(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "original_name": "SOP.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 128,
        "uploaded_at": now,
        "status": AttachmentStatus.AVAILABLE.value,
        "aggregate_type": AggregateType.ANNOUNCEMENT.value,
        "access_level": "PRIVATE",
        "uploaded_org_unit_id": "PUSAT",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _draft_announcement(announcement_id: uuid.UUID | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        id=announcement_id or uuid.uuid4(),
        status="DRAFT",
        start_at=None,
        end_at=None,
    )


def test_link_creates_join_without_upload() -> None:
    announcement_id = uuid.uuid4()
    attachment_id = uuid.uuid4()
    platform = _platform(id=attachment_id)
    actor = uuid.uuid4()

    announcements = MagicMock()
    announcements.get.return_value = _draft_announcement(announcement_id)
    join_repo = MagicMock()
    join_repo.is_announcement_domain_attachment.return_value = True
    join_repo.get.return_value = None
    join_repo.create.return_value = SimpleNamespace(created_at=datetime.now(UTC))
    attachments = MagicMock()
    attachments.get.return_value = platform

    result = AnnouncementAttachmentService(
        announcements=announcements,
        join_repo=join_repo,
        attachments=attachments,
        session=MagicMock(),
    ).link(
        announcement_id,
        attachment_id=attachment_id,
        visibility="IMMEDIATE",
        actor_id=actor,
    )

    assert result.id == attachment_id
    assert result.visibility == "IMMEDIATE"
    attachments.upload.assert_not_called()
    join_repo.create.assert_called_once()
    join_repo.commit.assert_called_once()


def test_link_rejects_non_announcement_domain() -> None:
    announcements = MagicMock()
    announcements.get.return_value = _draft_announcement()
    join_repo = MagicMock()
    join_repo.is_announcement_domain_attachment.return_value = False
    attachments = MagicMock()
    attachments.get.return_value = _platform()

    with pytest.raises(ValidationAppError):
        AnnouncementAttachmentService(
            announcements=announcements,
            join_repo=join_repo,
            attachments=attachments,
            session=MagicMock(),
        ).link(
            uuid.uuid4(),
            attachment_id=uuid.uuid4(),
            visibility="PUBLISHED",
            actor_id=uuid.uuid4(),
        )


def test_link_rejects_duplicate() -> None:
    announcements = MagicMock()
    announcements.get.return_value = _draft_announcement()
    join_repo = MagicMock()
    join_repo.is_announcement_domain_attachment.return_value = True
    join_repo.get.return_value = SimpleNamespace(id=uuid.uuid4())
    attachments = MagicMock()
    attachments.get.return_value = _platform()

    with pytest.raises(ConflictError):
        AnnouncementAttachmentService(
            announcements=announcements,
            join_repo=join_repo,
            attachments=attachments,
            session=MagicMock(),
        ).link(
            uuid.uuid4(),
            attachment_id=uuid.uuid4(),
            visibility="PUBLISHED",
            actor_id=uuid.uuid4(),
        )


def test_remove_keeps_file_in_catalog_even_when_last_join() -> None:
    announcement_id = uuid.uuid4()
    attachment_id = uuid.uuid4()
    join = SimpleNamespace(
        announcement_id=announcement_id, attachment_id=attachment_id
    )

    join_repo = MagicMock()
    join_repo.get.return_value = join
    attachments = MagicMock()

    AnnouncementAttachmentService(
        announcements=MagicMock(),
        join_repo=join_repo,
        attachments=attachments,
        session=MagicMock(),
    ).remove(announcement_id, attachment_id)

    join_repo.delete.assert_called_once_with(join)
    attachments.soft_delete.assert_not_called()
    join_repo.commit.assert_called_once()


def test_remove_missing_join_raises() -> None:
    join_repo = MagicMock()
    join_repo.get.return_value = None

    with pytest.raises(NotFoundError):
        AnnouncementAttachmentService(
            announcements=MagicMock(),
            join_repo=join_repo,
            attachments=MagicMock(),
            session=MagicMock(),
        ).remove(uuid.uuid4(), uuid.uuid4())


def test_upload_to_catalog_no_join() -> None:
    from app.modules.announcement.catalog_access import ANNOUNCEMENT_CATALOG_AGGREGATE_ID

    actor = uuid.uuid4()
    attachment_id = uuid.uuid4()
    platform = _platform(id=attachment_id, uploaded_at=datetime.now(UTC))
    attachments = MagicMock()
    attachments.upload.return_value = platform
    orm = MagicMock()
    session = MagicMock()
    session.get.return_value = orm

    result = AnnouncementAttachmentService(
        announcements=MagicMock(),
        join_repo=MagicMock(),
        attachments=attachments,
        session=session,
    ).upload_to_catalog(
        filename="sop.pdf",
        content_type="application/pdf",
        data=b"%PDF",
        actor_id=actor,
        uploaded_org_unit_id="BANDUNG",
        access_level="PRIVATE",
    )

    assert result.id == attachment_id
    assert result.access_level == "PRIVATE"
    assert result.uploaded_org_unit_id == "BANDUNG"
    assert result.usage_count == 0
    attachments.upload.assert_called_once()
    call_kw = attachments.upload.call_args.kwargs
    assert call_kw["aggregate_type"] == AggregateType.ANNOUNCEMENT.value
    assert call_kw["aggregate_id"] == ANNOUNCEMENT_CATALOG_AGGREGATE_ID
    assert orm.access_level == "PRIVATE"
    assert orm.uploaded_org_unit_id == "BANDUNG"
    session.commit.assert_called_once()
