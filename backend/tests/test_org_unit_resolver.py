"""OrgUnitResolver.resolve_principal — claim-first, membership fallback.

Mode A dev auth issues no orgUnitId claim (UM-BUG-005), so any endpoint
that reads principal.org_unit_id directly instead of going through this
resolver silently treats every Cabang caller as unit-less. This guards the
fallback that fixes it, without touching a real DB (sqlite chokes on the
postgresql-native UUID column type used across app.models, so this uses a
duck-typed fake session instead of a real engine).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.models import Branch, User


@dataclass
class _FakeBranch:
    id: uuid.UUID
    code: str
    deleted_at: object = None


@dataclass
class _FakeUser:
    id: uuid.UUID
    branch_id: uuid.UUID | None
    deleted_at: object = None


@dataclass
class _FakeSession:
    users: dict = field(default_factory=dict)
    branches: dict = field(default_factory=dict)

    def get(self, model: type, pk: uuid.UUID) -> object | None:
        if model is User:
            return self.users.get(pk)
        if model is Branch:
            return self.branches.get(pk)
        raise AssertionError(f"unexpected model {model}")


def _principal(*, org_unit_id: str | None, user_id: uuid.UUID) -> Principal:
    return Principal(
        user_id=user_id, roles=(), permissions=frozenset(), org_unit_id=org_unit_id
    )


def test_resolve_principal_prefers_the_claim_when_present() -> None:
    resolver = OrgUnitResolver(_FakeSession())
    principal = _principal(org_unit_id="PUSAT", user_id=uuid.uuid4())
    assert resolver.resolve_principal(principal) == "PUSAT"


def test_resolve_principal_falls_back_to_membership_when_claim_is_empty() -> None:
    user_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    session = _FakeSession(
        users={user_id: _FakeUser(id=user_id, branch_id=branch_id)},
        branches={branch_id: _FakeBranch(id=branch_id, code="UPPPD-TANAH-ABANG")},
    )
    resolver = OrgUnitResolver(session)
    principal = _principal(org_unit_id=None, user_id=user_id)
    assert resolver.resolve_principal(principal) == "UPPPD-TANAH-ABANG"


def test_resolve_principal_fails_open_when_user_row_is_missing() -> None:
    resolver = OrgUnitResolver(_FakeSession())
    principal = _principal(org_unit_id="", user_id=uuid.uuid4())
    assert resolver.resolve_principal(principal) is None


def test_resolve_principal_fails_open_when_member_has_no_branch() -> None:
    user_id = uuid.uuid4()
    session = _FakeSession(users={user_id: _FakeUser(id=user_id, branch_id=None)})
    resolver = OrgUnitResolver(session)
    principal = _principal(org_unit_id=None, user_id=user_id)
    assert resolver.resolve_principal(principal) is None
