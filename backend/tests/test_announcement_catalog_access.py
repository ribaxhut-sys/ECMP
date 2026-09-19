"""Unit tests for announcement catalog PUBLIC/PRIVATE access."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.modules.announcement.catalog_access import (
    ACCESS_PRIVATE,
    ACCESS_PUBLIC,
    announcement_is_currently_active,
    can_view_catalog_attachment,
    effective_access_level,
)
from app.modules.attachment.domain.enums import AttachmentStatus


def _principal(*, permissions: list[str], org: str | None = None, user_id=None):
    p = MagicMock()
    p.user_id = user_id or uuid.uuid4()
    p.org_unit_id = org
    p.has_permission = lambda code: code in permissions or "*" in permissions
    return p


def test_effective_access_defaults_private() -> None:
    att = SimpleNamespace(access_level=None)
    assert effective_access_level(att) == ACCESS_PRIVATE


def test_active_announcement_window() -> None:
    now = datetime.now(UTC)
    assert announcement_is_currently_active(
        status="PUBLISHED", start_at=None, end_at=None, now=now
    )
    assert not announcement_is_currently_active(
        status="PUBLISHED",
        start_at=now + timedelta(days=1),
        end_at=None,
        now=now,
    )
    assert not announcement_is_currently_active(
        status="DRAFT", start_at=None, end_at=None, now=now
    )


def test_public_visible_to_any_reader() -> None:
    session = MagicMock()
    # Avoid sticky DB work
    att = SimpleNamespace(
        id=uuid.uuid4(),
        status=AttachmentStatus.AVAILABLE.value,
        access_level=ACCESS_PUBLIC,
        uploaded_org_unit_id="BANDUNG",
        uploaded_by=uuid.uuid4(),
    )
    principal = _principal(permissions=["announcement:read"], org="BEKASI")

    # Monkeypatch sticky to no-op by making list_by_attachment empty via repo —
    # can_view imports apply_sticky which hits session. Stub session.get path:
    from app.modules.announcement import catalog_access as ca

    original = ca.apply_sticky_public_if_active
    ca.apply_sticky_public_if_active = lambda **kwargs: kwargs["attachment"]
    try:
        assert can_view_catalog_attachment(
            principal=principal, session=session, attachment=att
        )
    finally:
        ca.apply_sticky_public_if_active = original


def test_private_hidden_from_other_branch() -> None:
    session = MagicMock()
    att = SimpleNamespace(
        id=uuid.uuid4(),
        status=AttachmentStatus.AVAILABLE.value,
        access_level=ACCESS_PRIVATE,
        uploaded_org_unit_id="BANDUNG",
        uploaded_by=uuid.uuid4(),
    )
    principal = _principal(permissions=["announcement:read"], org="BEKASI")
    from app.modules.announcement import catalog_access as ca

    original = ca.apply_sticky_public_if_active
    ca.apply_sticky_public_if_active = lambda **kwargs: kwargs["attachment"]
    try:
        assert not can_view_catalog_attachment(
            principal=principal, session=session, attachment=att
        )
    finally:
        ca.apply_sticky_public_if_active = original


def test_private_visible_to_same_branch() -> None:
    session = MagicMock()
    att = SimpleNamespace(
        id=uuid.uuid4(),
        status=AttachmentStatus.AVAILABLE.value,
        access_level=ACCESS_PRIVATE,
        uploaded_org_unit_id="BANDUNG",
        uploaded_by=uuid.uuid4(),
    )
    principal = _principal(permissions=["announcement:read"], org="BANDUNG")
    from app.modules.announcement import catalog_access as ca

    original = ca.apply_sticky_public_if_active
    ca.apply_sticky_public_if_active = lambda **kwargs: kwargs["attachment"]
    try:
        assert can_view_catalog_attachment(
            principal=principal, session=session, attachment=att
        )
    finally:
        ca.apply_sticky_public_if_active = original


def test_private_visible_to_uploader_even_without_org() -> None:
    session = MagicMock()
    uploader = uuid.uuid4()
    att = SimpleNamespace(
        id=uuid.uuid4(),
        status=AttachmentStatus.AVAILABLE.value,
        access_level=ACCESS_PRIVATE,
        uploaded_org_unit_id=None,
        uploaded_by=uploader,
    )
    principal = _principal(
        permissions=["announcement:read"], org="BEKASI", user_id=uploader
    )
    from app.modules.announcement import catalog_access as ca

    sticky = ca.apply_sticky_public_if_active
    ca.apply_sticky_public_if_active = lambda **kwargs: kwargs["attachment"]
    try:
        assert can_view_catalog_attachment(
            principal=principal, session=session, attachment=att
        )
    finally:
        ca.apply_sticky_public_if_active = sticky


def test_private_visible_via_uploader_org_fallback() -> None:
    """When uploaded_org_unit_id is missing, same-branch uploader still matches."""
    session = MagicMock()
    uploader = uuid.uuid4()
    att = SimpleNamespace(
        id=uuid.uuid4(),
        status=AttachmentStatus.AVAILABLE.value,
        access_level=ACCESS_PRIVATE,
        uploaded_org_unit_id=None,
        uploaded_by=uploader,
    )
    principal = _principal(permissions=["announcement:read"], org="BANDUNG")
    from app.modules.announcement import catalog_access as ca

    sticky = ca.apply_sticky_public_if_active
    resolve_att = ca.resolve_attachment_org_unit
    ca.apply_sticky_public_if_active = lambda **kwargs: kwargs["attachment"]
    ca.resolve_attachment_org_unit = lambda _session, _att: "BANDUNG"
    try:
        assert can_view_catalog_attachment(
            principal=principal, session=session, attachment=att
        )
    finally:
        ca.apply_sticky_public_if_active = sticky
        ca.resolve_attachment_org_unit = resolve_att


def test_active_window_rejects_expired_end_at() -> None:
    now = datetime.now(UTC)
    assert not announcement_is_currently_active(
        status="PUBLISHED",
        start_at=None,
        end_at=now - timedelta(minutes=1),
        now=now,
    )


def test_caller_is_pusat_for_pusat_org() -> None:
    from app.modules.announcement import catalog_access as ca

    session = MagicMock()
    principal = _principal(permissions=["announcement:manage"], org="PUSAT")
    resolve = ca.resolve_caller_org_unit
    ca.resolve_caller_org_unit = lambda _p, _s: "PUSAT"
    try:
        assert ca.caller_is_pusat(principal, session) is True
    finally:
        ca.resolve_caller_org_unit = resolve


def test_can_change_access_for_uploader() -> None:
    from app.modules.announcement import catalog_access as ca

    session = MagicMock()
    uploader = uuid.uuid4()
    att = SimpleNamespace(uploaded_by=uploader, uploaded_org_unit_id="BANDUNG")
    principal = _principal(
        permissions=["announcement:read"], org="BEKASI", user_id=uploader
    )
    resolve = ca.resolve_caller_org_unit
    pusat = ca.caller_is_pusat
    ca.resolve_caller_org_unit = lambda _p, _s: "BEKASI"
    ca.caller_is_pusat = lambda _p, _s: False
    try:
        assert ca.can_change_access_level(
            principal=principal, session=session, attachment=att
        )
        assert ca.can_delete_from_catalog(
            principal=principal, session=session, attachment=att
        )
    finally:
        ca.resolve_caller_org_unit = resolve
        ca.caller_is_pusat = pusat


def test_can_change_access_same_org() -> None:
    from app.modules.announcement import catalog_access as ca

    session = MagicMock()
    att = SimpleNamespace(uploaded_by=uuid.uuid4(), uploaded_org_unit_id="BANDUNG")
    principal = _principal(permissions=["announcement:read"], org="BANDUNG")
    resolve = ca.resolve_caller_org_unit
    pusat = ca.caller_is_pusat
    resolve_att = ca.resolve_attachment_org_unit
    ca.resolve_caller_org_unit = lambda _p, _s: "BANDUNG"
    ca.caller_is_pusat = lambda _p, _s: False
    ca.resolve_attachment_org_unit = lambda _s, _a: "BANDUNG"
    try:
        assert ca.can_change_access_level(
            principal=principal, session=session, attachment=att
        )
    finally:
        ca.resolve_caller_org_unit = resolve
        ca.caller_is_pusat = pusat
        ca.resolve_attachment_org_unit = resolve_att


def test_mark_attachment_public_updates_orm() -> None:
    from app.modules.announcement.catalog_access import mark_attachment_public

    session = MagicMock()
    orm = SimpleNamespace(access_level=ACCESS_PRIVATE)
    session.get.return_value = orm
    mark_attachment_public(session, uuid.uuid4())
    assert orm.access_level == ACCESS_PUBLIC
    session.flush.assert_called_once()


def test_mark_attachment_public_noop_when_missing() -> None:
    from app.modules.announcement.catalog_access import mark_attachment_public

    session = MagicMock()
    session.get.return_value = None
    mark_attachment_public(session, uuid.uuid4())
    session.flush.assert_not_called()


def test_sticky_public_when_linked_announcement_active() -> None:
    from app.modules.announcement import catalog_access as ca

    session = MagicMock()
    att_id = uuid.uuid4()
    att = SimpleNamespace(
        id=att_id,
        access_level=ACCESS_PRIVATE,
        uploaded_org_unit_id="BANDUNG",
        uploaded_by=uuid.uuid4(),
    )
    orm = SimpleNamespace(access_level=ACCESS_PRIVATE)
    session.get.return_value = orm

    join_repo = MagicMock()
    join_repo.list_by_attachment_id.return_value = [
        SimpleNamespace(announcement_id=uuid.uuid4())
    ]
    announcements = MagicMock()
    announcements.get.return_value = SimpleNamespace(
        status="PUBLISHED", start_at=None, end_at=None
    )

    original_join = ca.AnnouncementAttachmentRepository
    original_ann = ca.AnnouncementRepository
    ca.AnnouncementAttachmentRepository = lambda _session: join_repo
    ca.AnnouncementRepository = lambda _session: announcements
    try:
        out = ca.apply_sticky_public_if_active(session=session, attachment=att)
        assert out.access_level == ACCESS_PUBLIC
        assert orm.access_level == ACCESS_PUBLIC
    finally:
        ca.AnnouncementAttachmentRepository = original_join
        ca.AnnouncementRepository = original_ann


def test_resolve_attachment_org_falls_back_to_uploader_membership() -> None:
    from app.modules.announcement.catalog_access import resolve_attachment_org_unit

    session = MagicMock()
    att = SimpleNamespace(uploaded_org_unit_id=None, uploaded_by=uuid.uuid4())
    resolver = MagicMock()
    resolver.resolve_declared.return_value = None
    resolver.resolve_principal_membership.return_value = "BANDUNG"
    with patch(
        "app.modules.announcement.catalog_access.OrgUnitResolver",
        return_value=resolver,
    ):
        assert resolve_attachment_org_unit(session, att) == "BANDUNG"
