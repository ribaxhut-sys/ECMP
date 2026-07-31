"""ADR-014 / audit K-3 — local credential AuthN dependency tests."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.errors import ApiError, ForbiddenError
from app.core.local_credential_auth import (
    assert_local_credential_auth_enabled,
    require_local_credential_auth,
)
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.users.schemas import UserUpdateRequest

pytestmark = pytest.mark.security

_GATED_AUTH_PATHS = (
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/forgot-password"),
    ("POST", "/api/v1/auth/reset-password"),
)

_GATED_USERS_PATHS = (
    ("POST", "/api/v1/users/me/change-password"),
    ("POST", "/api/v1/users/{id}/reset-password"),
    ("POST", "/api/v1/users"),
)


def _error_body(code: str, message: str, details: object) -> dict[str, object]:
    return {"code": code, "message": message, "details": details}


def _settings(*, enabled: bool) -> Settings:
    return Settings(
        _env_file=None,
        environment="development",
        jwt_secret_key="a" * 32,
        postgres_password="S3cure-Db-Pass!",
        ecmp_auth_mode="dev",
        ecmp_env="local",
        ecmp_local_credential_auth=enabled,
        ecmp_enterprise_mode=False,
    )


def _app_with_gate(enabled: bool) -> TestClient:
    settings = _settings(enabled=enabled)

    app = FastAPI()

    @app.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.get("/probe")
    def probe(_settings: Settings = Depends(require_local_credential_auth)) -> dict[str, bool]:
        return {"ok": True}

    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app, raise_server_exceptions=False)


def _app_with_credential_routers(enabled: bool) -> TestClient:
    """Mount real Mode A credential routers; gate must fail before DB work."""
    settings = _settings(enabled=enabled)
    app = FastAPI()

    @app.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    app.include_router(auth_router)
    app.include_router(users_router)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app, raise_server_exceptions=False)


def _route_depends_on_local_credential(route: APIRoute) -> bool:
    stack = list(route.dependant.dependencies)
    seen: set[int] = set()
    while stack:
        dep = stack.pop()
        if id(dep) in seen:
            continue
        seen.add(id(dep))
        call = dep.call
        if call is require_local_credential_auth:
            return True
        stack.extend(dep.dependencies)
    return False


def test_local_credential_auth_allows_when_enabled() -> None:
    client = _app_with_gate(True)
    response = client.get("/probe")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_local_credential_auth_forbids_when_disabled() -> None:
    client = _app_with_gate(False)
    response = client.get("/probe")
    assert response.status_code == 403
    body = response.json()
    assert body["code"] == "LOCAL_CREDENTIAL_AUTH_DISABLED"


@pytest.mark.parametrize(("method", "path"), _GATED_AUTH_PATHS)
def test_auth_credential_endpoints_forbid_when_local_auth_disabled(
    method: str, path: str
) -> None:
    client = _app_with_credential_routers(False)
    response = client.request(
        method,
        path,
        json={
            "username": "agent",
            "password": "irrelevant",
            "email": "agent@example.com",
            "token": "irrelevant",
            "newPassword": "Irrelevant1!",
        },
    )
    assert response.status_code == 403
    body = response.json()
    assert body["code"] == "LOCAL_CREDENTIAL_AUTH_DISABLED"


@pytest.mark.parametrize(("method", "path"), _GATED_AUTH_PATHS + _GATED_USERS_PATHS)
def test_credential_routes_declare_local_credential_gate(
    method: str, path: str
) -> None:
    """Lock wiring: Mode A credential surfaces must depend on the K-3 gate."""
    routes: list[APIRoute] = [
        r
        for r in list(auth_router.routes) + list(users_router.routes)
        if isinstance(r, APIRoute)
    ]
    matched = [
        r
        for r in routes
        if r.path == path and method in r.methods
    ]
    assert matched, f"route not found: {method} {path}"
    assert _route_depends_on_local_credential(matched[0]), (
        f"{method} {path} must Depend(require_local_credential_auth)"
    )


def test_session_endpoints_do_not_require_local_credential_gate() -> None:
    """Refresh / logout / me remain available when credential AuthN is off."""
    ungated = {
        ("POST", "/api/v1/auth/refresh"),
        ("POST", "/api/v1/auth/logout"),
        ("GET", "/api/v1/auth/me"),
    }
    for route in auth_router.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods or ():
            key = (method, route.path)
            if key in ungated:
                assert not _route_depends_on_local_credential(route), key


def test_assert_local_credential_auth_enabled_forbids_when_disabled() -> None:
    with pytest.raises(ForbiddenError) as exc:
        assert_local_credential_auth_enabled(_settings(enabled=False))
    assert exc.value.code == "LOCAL_CREDENTIAL_AUTH_DISABLED"


def test_assert_local_credential_auth_enabled_allows_when_enabled() -> None:
    assert_local_credential_auth_enabled(_settings(enabled=True))


def test_user_update_password_field_requires_local_credential_gate() -> None:
    """Profile-only updates stay open; password field is Mode A credential surface."""
    with_password = UserUpdateRequest.model_validate(
        {"fullName": "Ada", "password": "Secret123!"}
    )
    assert with_password.password is not None
    with pytest.raises(ForbiddenError) as exc:
        assert_local_credential_auth_enabled(_settings(enabled=False))
    assert exc.value.code == "LOCAL_CREDENTIAL_AUTH_DISABLED"

    profile_only = UserUpdateRequest.model_validate({"fullName": "Ada Lovelace"})
    assert profile_only.password is None
