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
