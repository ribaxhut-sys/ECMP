"""Authorization Middleware pipeline tests (TASK-040)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import (
    Principal,
    authenticate_bearer,
    check_data_scope,
    check_permissions,
    check_roles,
    require_data_scope,
    require_permissions,
    require_roles,
    resolve_effective_scope,
)
from app.core.config import Settings
from app.core.errors import (
    DataScopeDeniedError,
    ForbiddenError,
    PermissionDeniedError,
    UnauthenticatedError,
)
from app.core.security import create_access_token
from app.modules.iam.data_scope.models import ScopeType
from app.modules.iam.data_scope_resolver import EffectiveScope


def _settings() -> Settings:
    return Settings(
        environment="development",
        jwt_secret_key="test-secret-key-for-authorization-middleware",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=15,
    )


# --- Authentication ---------------------------------------------------------


def test_authenticate_bearer_requires_token() -> None:
    with pytest.raises(UnauthenticatedError) as exc:
        authenticate_bearer(None, _settings())
    assert exc.value.status_code == 401
    assert exc.value.code == "UNAUTHENTICATED"


def test_authenticate_bearer_rejects_non_bearer() -> None:
    creds = HTTPAuthorizationCredentials(scheme="Basic", credentials="x")
    with pytest.raises(UnauthenticatedError):
        authenticate_bearer(creds, _settings())


def test_authenticate_bearer_accepts_valid_jwt() -> None:
    settings = _settings()
    user_id = uuid.uuid4()
    token = create_access_token(
        subject=str(user_id),
        settings=settings,
        claims={"roles": ["AGENT"]},
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    resolved_id, roles, payload = authenticate_bearer(creds, settings)
    assert resolved_id == user_id
    assert roles == ("AGENT",)
    assert payload.get("sub") == str(user_id)


# --- Permission check -------------------------------------------------------


def test_check_permissions_pass() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        permissions=frozenset({"complaints:read", "complaints:create"}),
    )
    check_permissions(principal, "complaints:read")


def test_check_permissions_wildcard() -> None:
    principal = Principal(user_id=uuid.uuid4(), permissions=frozenset({"*"}))
    check_permissions(principal, "anything:goes")


def test_check_permissions_denied() -> None:
    principal = Principal(user_id=uuid.uuid4(), permissions=frozenset())
    with pytest.raises(PermissionDeniedError) as exc:
        check_permissions(principal, "complaints:read")
    assert exc.value.status_code == 403
    assert exc.value.code == "FORBIDDEN"
    assert exc.value.message == "Permission denied"
    assert isinstance(exc.value, ForbiddenError)


def test_require_permissions_dependency() -> None:
    gate = require_permissions("complaints:read")
    ok = Principal(
        user_id=uuid.uuid4(),
        permissions=frozenset({"complaints:read"}),
    )
    assert gate(principal=ok) is ok

    denied = Principal(user_id=uuid.uuid4(), permissions=frozenset())
    with pytest.raises(PermissionDeniedError):
        gate(principal=denied)


def test_require_roles_dependency() -> None:
    gate = require_roles("SUPERVISOR", "ADMIN")
    ok = Principal(user_id=uuid.uuid4(), roles=("SUPERVISOR",))
    assert gate(principal=ok) is ok

    denied = Principal(user_id=uuid.uuid4(), roles=("AGENT",))
    with pytest.raises(PermissionDeniedError) as exc:
        gate(principal=denied)
    assert exc.value.message == "Permission denied"


def test_check_roles_denied() -> None:
    principal = Principal(user_id=uuid.uuid4(), roles=("AGENT",))
    with pytest.raises(PermissionDeniedError):
        check_roles(principal, "ADMIN")


# --- Data scope check -------------------------------------------------------


def test_check_data_scope_noop_without_types() -> None:
    scope = EffectiveScope(entries=frozenset())
    check_data_scope(scope)


def test_check_data_scope_allows_global() -> None:
    scope = EffectiveScope(
        entries=frozenset({(ScopeType.GLOBAL.value, None)})
    )
    check_data_scope(scope, "BRANCH")


def test_check_data_scope_allows_matching_type() -> None:
    scope = EffectiveScope(
        entries=frozenset({(ScopeType.BRANCH.value, "b-1")})
    )
    check_data_scope(scope, "BRANCH", "SELF")


def test_check_data_scope_denied() -> None:
    scope = EffectiveScope(
        entries=frozenset({(ScopeType.SELF.value, None)})
    )
    with pytest.raises(DataScopeDeniedError) as exc:
        check_data_scope(scope, "BRANCH")
    assert exc.value.status_code == 403
    assert exc.value.code == "DATA_SCOPE_DENIED"
    assert exc.value.message == "Data scope denied"
    assert isinstance(exc.value, ForbiddenError)


def test_require_data_scope_forbidden_without_match() -> None:
    gate = require_data_scope("BRANCH")
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset(),
    )
    session = MagicMock()
    session.execute.return_value.all.return_value = []

    with pytest.raises(DataScopeDeniedError):
        gate(principal=principal, session=session)


def test_require_data_scope_allows_global() -> None:
    gate = require_data_scope("BRANCH")
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset(),
    )
    session = MagicMock()
    session.execute.return_value.all.return_value = [
        (ScopeType.GLOBAL.value, None)
    ]

    scope = gate(principal=principal, session=session)
    assert scope.has_global() is True


def test_resolve_effective_scope_delegates() -> None:
    session = MagicMock()
    session.execute.return_value.all.return_value = [
        (ScopeType.SELF.value, None)
    ]
    user_id = uuid.uuid4()
    scope = resolve_effective_scope(user_id, session)
    assert scope.is_self_only()
