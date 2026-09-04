"""Unit tests for announcement attachment download authorization."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.authorization.principal import Principal
from app.core.errors import NotFoundError, PermissionDeniedError
from app.modules.announcement.attachment_authorization import (
    assert_can_access_announcement_attachment,
    assert_can_manage_announcement_attachment,
)
from app.modules.attachment.domain.enums import AttachmentStatus


def _principal(**kwargs) -> Principal:
    defaults = {
        "user_id": uuid.uuid4(),
        "roles": ("AGENT",),
        "permissions": frozenset({"announcement:read", "attachment:read"}),
        "org_unit_id": "UPPPD-TANAH-ABANG",
    }
    defaults.update(kwargs)
    return Principal(**defaults)


def test_orphan_public_download_allowed_for_reader() -> None:
    attachment_id = uuid.uuid4()
    platform = SimpleNamespace(
        id=attachment_id,
        status=AttachmentStatus.AVAILABLE.value,
        access_level="PUBLIC",
        uploaded_by=uuid.uuid4(),
        uploaded_org_unit_id="PUSAT",
    )
    session = MagicMock()
    with (
        patch(
            "app.modules.attachment.registration.build_attachment_service"
        ) as build,
        patch(
            "app.modules.announcement.catalog_access.can_view_catalog_attachment",
            return_value=True,
        ),
        patch(
            "app.modules.announcement.attachment_authorization.AnnouncementAttachmentRepository"
        ) as repo_cls,
        patch(
            "app.modules.announcement.attachment_authorization.principal_may_manage_announcements",
            return_value=False,
        ),
    ):
        build.return_value.get.return_value = platform
        repo_cls.return_value.list_by_attachment_id.return_value = []
        assert_can_access_announcement_attachment(
            principal=_principal(),
            session=session,
            attachment_id=attachment_id,
        )


def test_orphan_private_hidden_raises_not_found() -> None:
    attachment_id = uuid.uuid4()
    platform = SimpleNamespace(
        id=attachment_id,
        status=AttachmentStatus.AVAILABLE.value,
        access_level="PRIVATE",
        uploaded_by=uuid.uuid4(),
        uploaded_org_unit_id="PUSAT",
    )
    session = MagicMock()
    with (
        patch(
            "app.modules.attachment.registration.build_attachment_service"
        ) as build,
        patch(
            "app.modules.announcement.catalog_access.can_view_catalog_attachment",
            return_value=False,
        ),
        patch(
            "app.modules.announcement.attachment_authorization.AnnouncementAttachmentRepository"
        ) as repo_cls,
        patch(
            "app.modules.announcement.attachment_authorization.principal_may_manage_announcements",
            return_value=False,
        ),
    ):
        build.return_value.get.return_value = platform
        repo_cls.return_value.list_by_attachment_id.return_value = []
        with pytest.raises(NotFoundError):
            assert_can_access_announcement_attachment(
                principal=_principal(),
                session=session,
                attachment_id=attachment_id,
            )


def test_manage_gate_requires_join_and_pusat() -> None:
    attachment_id = uuid.uuid4()
    session = MagicMock()
    with (
        patch(
            "app.modules.announcement.attachment_authorization.AnnouncementAttachmentRepository"
        ) as repo_cls,
        patch(
            "app.modules.announcement.attachment_authorization.principal_may_manage_announcements",
            return_value=False,
        ),
    ):
        repo_cls.return_value.list_by_attachment_id.return_value = [
            SimpleNamespace(announcement_id=uuid.uuid4())
        ]
        with pytest.raises(PermissionDeniedError):
            assert_can_manage_announcement_attachment(
                principal=_principal(),
                session=session,
                attachment_id=attachment_id,
            )


def test_manage_gate_missing_join_is_not_found() -> None:
    attachment_id = uuid.uuid4()
    session = MagicMock()
    with patch(
        "app.modules.announcement.attachment_authorization.AnnouncementAttachmentRepository"
    ) as repo_cls:
        repo_cls.return_value.list_by_attachment_id.return_value = []
        with pytest.raises(NotFoundError):
            assert_can_manage_announcement_attachment(
                principal=_principal(roles=("ADMIN",), org_unit_id=None),
                session=session,
                attachment_id=attachment_id,
            )
