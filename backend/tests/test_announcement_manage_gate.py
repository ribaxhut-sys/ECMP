"""Announcement manage gate — pure predicate + wiring (permission correction).

Mirrors tests/test_hq_intake_action_gate.py. SUPERVISOR/MANAGER are
BRANCH_SCOPED_ROLE_CODES shared with Cabang staff, so role alone must never
be treated as proof of "Pusat" — only is_pusat_unit(org_unit_id) does.
"""

from __future__ import annotations

import uuid

from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.core.authorization.gates import (
    principal_may_manage_announcements,
    require_announcement_manage,
)
from app.core.authorization.principal import Principal
from app.modules.announcement.router import router as announcement_router

MANAGE_PERMS = frozenset({"complaints:read", "announcement:read", "announcement:manage"})


def _dependant_calls(dependant: Dependant) -> set[object]:
    found: set[object] = set()
    stack = [dependant]
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if current.call is not None:
            found.add(current.call)
        stack.extend(current.dependencies)
    return found


def test_admin_pusat_may_manage_without_org_unit() -> None:
    """ADMIN never carries a branch — no org unit at all still means Pusat."""
    principal = Principal(
        user_id=uuid.uuid4(), roles=("ADMIN",), permissions=MANAGE_PERMS
    )
    assert principal_may_manage_announcements(principal, org_unit_id=None) is True


def test_admin_pusat_may_manage_with_pusat_org_unit() -> None:
    principal = Principal(
        user_id=uuid.uuid4(), roles=("ADMIN",), permissions=MANAGE_PERMS
    )
    assert principal_may_manage_announcements(principal, org_unit_id="PUSAT") is True


def test_admin_cabang_denied_even_though_admin_role() -> None:
    """Adversarial: an ADMIN token carrying a Cabang org marker is still denied."""
    principal = Principal(
        user_id=uuid.uuid4(), roles=("ADMIN",), permissions=MANAGE_PERMS
    )
    assert (
        principal_may_manage_announcements(principal, org_unit_id="UPPPD-A")
        is False
    )


def test_supervisor_pusat_may_manage() -> None:
    principal = Principal(
        user_id=uuid.uuid4(), roles=("SUPERVISOR",), permissions=MANAGE_PERMS
    )
    assert principal_may_manage_announcements(principal, org_unit_id="PUSAT") is True
    assert principal_may_manage_announcements(principal, org_unit_id="HO") is True


def test_supervisor_cabang_denied() -> None:
    """Same SUPERVISOR role code as a Pusat supervisor — org unit is what differs."""
    principal = Principal(
        user_id=uuid.uuid4(), roles=("SUPERVISOR",), permissions=MANAGE_PERMS
    )
    assert (
        principal_may_manage_announcements(principal, org_unit_id="UPPPD-A")
        is False
    )


def test_supervisor_with_no_org_unit_denied() -> None:
    """Branch-scoped role with no resolvable org — fail closed, not open."""
    principal = Principal(
        user_id=uuid.uuid4(), roles=("SUPERVISOR",), permissions=MANAGE_PERMS
    )
    assert principal_may_manage_announcements(principal, org_unit_id=None) is False


def test_manager_pusat_may_manage() -> None:
    principal = Principal(
        user_id=uuid.uuid4(), roles=("MANAGER",), permissions=MANAGE_PERMS
    )
    assert principal_may_manage_announcements(principal, org_unit_id="PUSAT") is True


def test_manager_cabang_denied() -> None:
    principal = Principal(
        user_id=uuid.uuid4(), roles=("MANAGER",), permissions=MANAGE_PERMS
    )
    assert (
        principal_may_manage_announcements(principal, org_unit_id="UPPPD-A")
        is False
    )


def test_agent_denied_regardless_of_org() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:read", "announcement:read"}),
    )
    assert principal_may_manage_announcements(principal, org_unit_id="PUSAT") is False


def test_no_permission_denied_even_with_admin_role() -> None:
    """Permission check is the first gate — role alone never unlocks manage."""
    principal = Principal(user_id=uuid.uuid4(), roles=("ADMIN",), permissions=frozenset())
    assert principal_may_manage_announcements(principal, org_unit_id="PUSAT") is False


def test_manage_routes_depend_on_require_announcement_manage() -> None:
    """Mutation/management endpoints must use the org-aware gate. Reader and
    catalog endpoints use plain announcement:read (catalog routes are still
    access-filtered in service layer)."""
    routes_by_key = {
        (r.path, next(iter(r.methods - {"HEAD"}))): r
        for r in announcement_router.routes
        if isinstance(r, APIRoute)
    }

    manage_keys = {
        ("/api/v1/announcements", "GET"),
        ("/api/v1/announcements", "POST"),
        ("/api/v1/announcements/{id}", "PUT"),
        ("/api/v1/announcements/{id}", "DELETE"),
        ("/api/v1/announcements/{id}/publish", "PUT"),
        ("/api/v1/announcements/{id}/unpublish", "PUT"),
        ("/api/v1/announcements/{id}/attachments", "POST"),
        ("/api/v1/announcements/{id}/attachments/link", "POST"),
        ("/api/v1/announcements/{id}/attachments/{attachment_id}", "PUT"),
        ("/api/v1/announcements/{id}/attachments/{attachment_id}", "DELETE"),
    }
    read_only_keys = {
        ("/api/v1/announcements/active", "GET"),
        ("/api/v1/announcements/history", "GET"),
        ("/api/v1/announcements/unread", "GET"),
        ("/api/v1/announcements/{id}", "GET"),
        ("/api/v1/announcements/{id}/read", "PUT"),
        # Catalog — announcement:read (access-filtered in service layer).
        ("/api/v1/announcements/attachment-library", "GET"),
        ("/api/v1/announcements/attachment-library", "POST"),
        ("/api/v1/announcements/attachment-library/{attachment_id}", "DELETE"),
        ("/api/v1/announcements/attachment-library/{attachment_id}/access", "PUT"),
        # Pin (0103) — presentation only, per-caller; announcement:read is enough.
        ("/api/v1/announcements/attachment-library/{attachment_id}/pin", "PUT"),
        ("/api/v1/announcements/attachment-library/{attachment_id}/pin", "DELETE"),
    }

    assert set(routes_by_key) == manage_keys | read_only_keys, set(routes_by_key)

    for key in manage_keys:
        calls = _dependant_calls(routes_by_key[key].dependant)
        assert require_announcement_manage in calls, key

    for key in read_only_keys:
        calls = _dependant_calls(routes_by_key[key].dependant)
        assert require_announcement_manage not in calls, key
