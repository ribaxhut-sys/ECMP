"""Unit tests for announcement catalog PUBLIC/PRIVATE access."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

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
