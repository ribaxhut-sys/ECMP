"""Authentication API tests (login / refresh / logout / me)."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.db.session import get_db_session
from app.main import create_app
from app.models import RefreshToken, Role, User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import LoginRequest
from app.modules.auth.service import AuthService
from app.modules.iam.user_role.models import UserRole


def _postgres_available() -> bool:
    settings = get_settings()
    try:
        eng = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for auth API tests",
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    settings = get_settings()
    eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        eng.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def _override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_user(db_session: Session) -> User:
    from app.modules.iam.permission.models import Permission
    from app.modules.iam.role_permission.models import RolePermission

    role = db_session.scalar(
        select(Role).where(Role.code == "AGENT", Role.deleted_at.is_(None))
    )
    if role is None:
        role = Role(code="AGENT", name="Agent", is_active=True)
        db_session.add(role)
        db_session.flush()

    user = User(
        username=f"agent_{uuid.uuid4().hex[:8]}",
        email=f"agent_{uuid.uuid4().hex[:8]}@example.com",
        full_name="Auth Test Agent",
        password_hash=hash_password("Secret123!"),
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    # TASK-038: Authorization Engine resolves via user_roles junction.
    if (
        db_session.scalar(
            select(UserRole).where(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id,
            )
        )
        is None
    ):
        db_session.add(UserRole(user_id=user.id, role_id=role.id))

    # Ensure AGENT can read complaints (resolver path) even if seed matrix lagging.
    read = db_session.scalar(
        select(Permission).where(
            Permission.code == "complaints:read",
            Permission.deleted_at.is_(None),
        )
    )
    if read is None:
        table = db_session.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_name = 'permissions'"
            )
        ).scalar()
        if table:
            read = Permission(
                code="complaints:read",
                name="Complaints Read",
                module="complaints",
                is_system=True,
                is_active=True,
            )
            db_session.add(read)
            db_session.flush()
    if read is not None and (
        db_session.scalar(
            select(RolePermission).where(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == read.id,
            )
        )
        is None
    ):
        db_session.add(RolePermission(role_id=role.id, permission_id=read.id))

    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_refresh_me_logout_flow(
    client: TestClient, db_session: Session, auth_user: User
) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": "Secret123!"},
    )
    assert login.status_code == 200, login.text
    body = login.json()["data"]
    assert body["tokenType"] == "Bearer"
    assert body["expiresIn"] == get_settings().access_token_expire_seconds
    assert body["accessToken"]

    refresh_cookie = login.cookies.get(get_settings().refresh_cookie_name)
    assert refresh_cookie

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['accessToken']}"},
    )
    assert me.status_code == 200
    me_data = me.json()["data"]
    assert me_data["id"] == str(auth_user.id)
    assert me_data["username"] == auth_user.username
    assert "AGENT" in me_data["roles"]
    assert "complaints:read" in me_data["permissions"]
    assert "passwordHash" not in me_data

    refresh = client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    assert refresh.json()["data"]["accessToken"]

    rows = list(
        db_session.scalars(
            select(RefreshToken).where(RefreshToken.user_id == auth_user.id)
        ).all()
    )
    assert any(row.revoked_at is not None for row in rows)
    assert any(row.revoked_at is None for row in rows)

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    refresh_after = client.post("/api/v1/auth/refresh")
    assert refresh_after.status_code == 401
    assert refresh_after.json()["code"] == "UNAUTHENTICATED"


def _set_cookie_headers(response) -> list[str]:
    headers = response.headers
    if hasattr(headers, "get_list"):
        values = headers.get_list("set-cookie")
        if values:
            return list(values)
    value = headers.get("set-cookie")
    return [value] if value else []


def _cookie_header_for(response, cookie_name: str) -> str | None:
    prefix = f"{cookie_name}="
    for header in _set_cookie_headers(response):
        if header.startswith(prefix):
            return header
    return None


def _cookie_attr(header: str, name: str) -> str | None:
    """Return cookie attribute value (e.g. Path) or '' for flags like HttpOnly."""
    parts = [p.strip() for p in header.split(";")]
    target = name.lower()
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            if key.strip().lower() == target:
                return value.strip()
        elif part.lower() == target:
            return ""
    return None


def test_logout_clears_refresh_cookie_on_returned_response(
    client: TestClient, auth_user: User
) -> None:
    """UAT-019: logout Set-Cookie must be a browser-compatible deletion."""
    settings = get_settings()
    login = client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": "Secret123!"},
    )
    assert login.status_code == 200
    login_cookie = _cookie_header_for(login, settings.refresh_cookie_name)
    assert login_cookie is not None

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    clear_cookie = _cookie_header_for(logout, settings.refresh_cookie_name)
    assert clear_cookie is not None, "logout must emit Set-Cookie deletion header"

    # Browser-compatible deletion: empty value + Max-Age=0 (or Expires in the past).
    assert clear_cookie.startswith(f"{settings.refresh_cookie_name}=")
    value = clear_cookie.split(";", 1)[0].split("=", 1)[1]
    assert value in {"", '""'}
    max_age = _cookie_attr(clear_cookie, "Max-Age")
    assert max_age == "0"

    # Deletion attributes must match the cookie that was set on login.
    assert _cookie_attr(clear_cookie, "Path") == _cookie_attr(login_cookie, "Path")
    assert _cookie_attr(clear_cookie, "Path") == settings.refresh_cookie_path
    assert _cookie_attr(login_cookie, "Domain") == _cookie_attr(clear_cookie, "Domain")
    assert ("HttpOnly" in clear_cookie) == ("HttpOnly" in login_cookie)
    login_samesite = (_cookie_attr(login_cookie, "SameSite") or "").lower()
    clear_samesite = (_cookie_attr(clear_cookie, "SameSite") or "").lower()
    assert clear_samesite == login_samesite == "lax"
    assert ("Secure" in clear_cookie) == ("Secure" in login_cookie)


def test_logout_idempotent_returns_204_twice(
    client: TestClient, auth_user: User
) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": "Secret123!"},
    )
    assert login.status_code == 200

    first = client.post("/api/v1/auth/logout")
    second = client.post("/api/v1/auth/logout")
    assert first.status_code == 204
    assert second.status_code == 204
    # Second logout still clears cookie on the returned response.
    assert _cookie_header_for(second, get_settings().refresh_cookie_name) is not None


def test_refresh_unauthorized_after_logout(
    client: TestClient, auth_user: User
) -> None:
    settings = get_settings()
    login = client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": "Secret123!"},
    )
    assert login.status_code == 200
    raw_refresh = login.cookies.get(settings.refresh_cookie_name)
    assert raw_refresh

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    # Even if a stale cookie value is replayed, refresh must fail (token revoked).
    refresh = client.post(
        "/api/v1/auth/refresh",
        cookies={settings.refresh_cookie_name: raw_refresh},
    )
    assert refresh.status_code == 401
    assert refresh.json()["code"] == "UNAUTHENTICATED"


def test_login_refresh_logout_login_again(
    client: TestClient, auth_user: User
) -> None:
    """Regression: full auth cycle remains healthy after cookie-clear fix."""
    settings = get_settings()
    password = "Secret123!"

    login1 = client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": password},
    )
    assert login1.status_code == 200
    assert login1.cookies.get(settings.refresh_cookie_name)

    refresh = client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    assert refresh.json()["data"]["accessToken"]

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert _cookie_header_for(logout, settings.refresh_cookie_name) is not None

    assert client.post("/api/v1/auth/refresh").status_code == 401

    login2 = client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": password},
    )
    assert login2.status_code == 200
    assert login2.cookies.get(settings.refresh_cookie_name)
    assert client.post("/api/v1/auth/refresh").status_code == 200


def test_login_rejects_bad_password(client: TestClient, auth_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_me_requires_bearer(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_auth_service_does_not_store_plaintext_refresh(
    db_session: Session, auth_user: User
) -> None:
    settings = get_settings()
    service = AuthService(AuthRepository(db_session), settings)
    session = service.login(
        LoginRequest(username=auth_user.username, password="Secret123!")
    )
    rows = list(
        db_session.scalars(
            select(RefreshToken).where(RefreshToken.user_id == auth_user.id)
        ).all()
    )
    assert len(rows) >= 1
    latest = max(rows, key=lambda r: r.created_at)
    assert latest.token_hash != session.refresh_token
    assert len(latest.token_hash) == 64
    assert verify_password("Secret123!", auth_user.password_hash)
