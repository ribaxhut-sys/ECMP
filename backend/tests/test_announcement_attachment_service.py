"""Unit tests for announcement attachment link / remove (mocked)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

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


def test_list_library_org_scope_cabang_keeps_own_unit_only() -> None:
    from app.core.authorization.principal import Principal
    from app.modules.announcement.catalog_access import ACCESS_PUBLIC

    own_id = uuid.uuid4()
    other_id = uuid.uuid4()
    pusat_id = uuid.uuid4()
    actor = uuid.uuid4()

    def _row(aid: uuid.UUID, org: str, level: str = "PRIVATE"):
        return SimpleNamespace(
            id=aid,
            original_name=f"{org}.pdf",
            mime_type="application/pdf",
            size_bytes=10,
            created_at=datetime.now(UTC),
            access_level=level,
            uploaded_org_unit_id=org,
            uploaded_by=actor,
            uploaded_by_name="Tester",
            usage_count=0,
        )

    rows = [
        _row(own_id, "UPPPD-TANAH-ABANG"),
        _row(other_id, "UPPPD-GAMBIR", ACCESS_PUBLIC),
        _row(pusat_id, "PUSAT", ACCESS_PUBLIC),
    ]
    platforms = {
        own_id: _platform(id=own_id, uploaded_org_unit_id="UPPPD-TANAH-ABANG"),
        other_id: _platform(
            id=other_id,
            uploaded_org_unit_id="UPPPD-GAMBIR",
            access_level=ACCESS_PUBLIC,
        ),
        pusat_id: _platform(
            id=pusat_id, uploaded_org_unit_id="PUSAT", access_level=ACCESS_PUBLIC
        ),
    }

    join_repo = MagicMock()
    join_repo.list_reusable.return_value = rows
    attachments = MagicMock()
    attachments.get.side_effect = lambda aid: platforms[aid]
    session = MagicMock()

    principal = Principal(
        user_id=actor,
        roles=("AGENT",),
        permissions=frozenset({"announcement:read"}),
        org_unit_id="UPPPD-TANAH-ABANG",
    )

    with (
        patch(
            "app.modules.announcement.attachment_service.can_view_catalog_attachment",
            return_value=True,
        ),
        patch(
            "app.modules.announcement.attachment_service.apply_sticky_public_if_active",
            side_effect=lambda **kw: kw["attachment"],
        ),
        patch(
            "app.modules.announcement.attachment_service.resolve_caller_org_unit",
            return_value="UPPPD-TANAH-ABANG",
        ),
        patch(
            "app.modules.announcement.attachment_service.caller_is_pusat",
            return_value=False,
        ),
        patch(
            "app.modules.announcement.attachment_service.resolve_attachment_org_unit",
            side_effect=lambda _s, att: att.uploaded_org_unit_id,
        ),
    ):
        svc = AnnouncementAttachmentService(
            announcements=MagicMock(),
            join_repo=join_repo,
            attachments=attachments,
            session=session,
        )
        cabang = svc.list_library(principal=principal, org_scope="cabang")
        assert {item.id for item in cabang} == {own_id}

        pusat = svc.list_library(principal=principal, org_scope="pusat")
        assert {item.id for item in pusat} == {pusat_id}

        all_items = svc.list_library(principal=principal, org_scope="all")
        assert {item.id for item in all_items} == {own_id, other_id, pusat_id}


def test_list_library_rejects_invalid_org_scope() -> None:
    from app.core.authorization.principal import Principal

    svc = AnnouncementAttachmentService(
        announcements=MagicMock(),
        join_repo=MagicMock(),
        attachments=MagicMock(),
        session=MagicMock(),
    )
    with pytest.raises(ValidationAppError):
        svc.list_library(
            principal=Principal(
                user_id=uuid.uuid4(),
                roles=("AGENT",),
                permissions=frozenset({"announcement:read"}),
            ),
            org_scope="galaxy",
        )


def test_update_access_level_sets_public() -> None:
    from app.core.authorization.principal import Principal

    attachment_id = uuid.uuid4()
    actor = uuid.uuid4()
    platform = _platform(id=attachment_id, uploaded_by=actor)
    orm = SimpleNamespace(access_level="PRIVATE", uploaded_org_unit_id="PUSAT")
    session = MagicMock()
    session.get.return_value = orm
    join_repo = MagicMock()
    join_repo.is_announcement_domain_attachment.return_value = True
    join_repo.count_for_attachment.return_value = 2
    attachments = MagicMock()
    attachments.get.return_value = platform

    with (
        patch(
            "app.modules.announcement.attachment_service.can_change_access_level",
            return_value=True,
        ),
        patch(
            "app.modules.announcement.attachment_service._user_display_name",
            return_value="Admin",
        ),
    ):
        result = AnnouncementAttachmentService(
            announcements=MagicMock(),
            join_repo=join_repo,
            attachments=attachments,
            session=session,
        ).update_access_level(
            attachment_id,
            access_level="PUBLIC",
            principal=Principal(
                user_id=actor,
                roles=("ADMIN",),
                permissions=frozenset({"announcement:read", "announcement:manage"}),
            ),
        )

    assert result.access_level == "PUBLIC"
    assert result.usage_count == 2
    assert orm.access_level == "PUBLIC"
    session.commit.assert_called_once()


def test_delete_from_catalog_soft_deletes() -> None:
    from app.core.authorization.principal import Principal
    from app.core.errors import PermissionDeniedError

    attachment_id = uuid.uuid4()
    platform = _platform(id=attachment_id)
    join_repo = MagicMock()
    join_repo.is_announcement_domain_attachment.return_value = True
    attachments = MagicMock()
    attachments.get.return_value = platform
    session = MagicMock()

    with patch(
        "app.modules.announcement.attachment_service.can_delete_from_catalog",
        return_value=True,
    ):
        AnnouncementAttachmentService(
            announcements=MagicMock(),
            join_repo=join_repo,
            attachments=attachments,
            session=session,
        ).delete_from_catalog(
            attachment_id,
            principal=Principal(
                user_id=uuid.uuid4(),
                roles=("ADMIN",),
                permissions=frozenset({"announcement:read"}),
            ),
        )

    join_repo.delete_all_joins_for_attachment.assert_called_once_with(attachment_id)
    attachments.soft_delete.assert_called_once()
    join_repo.commit.assert_called_once()

    with patch(
        "app.modules.announcement.attachment_service.can_delete_from_catalog",
        return_value=False,
    ):
        with pytest.raises(PermissionDeniedError):
            AnnouncementAttachmentService(
                announcements=MagicMock(),
                join_repo=join_repo,
                attachments=attachments,
                session=session,
            ).delete_from_catalog(
                attachment_id,
                principal=Principal(
                    user_id=uuid.uuid4(),
                    roles=("AGENT",),
                    permissions=frozenset({"announcement:read"}),
                ),
            )


def test_list_library_pusat_cabang_scope_excludes_pusat_files() -> None:
    from app.core.authorization.principal import Principal
    from app.modules.announcement.catalog_access import ACCESS_PUBLIC

    cabang_id = uuid.uuid4()
    pusat_id = uuid.uuid4()
    actor = uuid.uuid4()

    def _row(aid: uuid.UUID, org: str):
        return SimpleNamespace(
            id=aid,
            original_name=f"{org}.pdf",
            mime_type="application/pdf",
            size_bytes=10,
            created_at=datetime.now(UTC),
            access_level=ACCESS_PUBLIC,
            uploaded_org_unit_id=org,
            uploaded_by=actor,
            uploaded_by_name="Tester",
            usage_count=0,
        )

    rows = [_row(cabang_id, "UPPPD-GAMBIR"), _row(pusat_id, "PUSAT")]
    platforms = {
        cabang_id: _platform(id=cabang_id, uploaded_org_unit_id="UPPPD-GAMBIR"),
        pusat_id: _platform(id=pusat_id, uploaded_org_unit_id="PUSAT"),
    }
    join_repo = MagicMock()
    join_repo.list_reusable.return_value = rows
    attachments = MagicMock()
    attachments.get.side_effect = lambda aid: platforms[aid]

    with (
        patch(
            "app.modules.announcement.attachment_service.can_view_catalog_attachment",
            return_value=True,
        ),
        patch(
            "app.modules.announcement.attachment_service.apply_sticky_public_if_active",
            side_effect=lambda **kw: kw["attachment"],
        ),
        patch(
            "app.modules.announcement.attachment_service.resolve_caller_org_unit",
            return_value="PUSAT",
        ),
        patch(
            "app.modules.announcement.attachment_service.caller_is_pusat",
            return_value=True,
        ),
        patch(
            "app.modules.announcement.attachment_service.resolve_attachment_org_unit",
            side_effect=lambda _s, att: att.uploaded_org_unit_id,
        ),
    ):
        items = AnnouncementAttachmentService(
            announcements=MagicMock(),
            join_repo=join_repo,
            attachments=attachments,
            session=MagicMock(),
        ).list_library(
            principal=Principal(
                user_id=actor,
                roles=("ADMIN",),
                permissions=frozenset({"announcement:read", "announcement:manage"}),
                org_unit_id="PUSAT",
            ),
            org_scope="cabang",
        )
    assert {item.id for item in items} == {cabang_id}
