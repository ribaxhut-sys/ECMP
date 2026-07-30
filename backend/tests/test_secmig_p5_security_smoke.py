"""TASK-PLATFORM-SECMIG-P5-006 — HTTP security smoke + client-IP integration.

No runtime behavior changes — verification coverage only.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker
from starlette.datastructures import Headers

from app.core.client_ip import resolve_client_ip
from app.core.config import Settings, get_settings
from app.core.security import create_access_token, hash_password
from app.db.session import get_db_session
from app.main import create_app
from app.models import Role, User
from app.modules.audit.models import SystemAuditLog
from app.modules.audit.security_events import SecurityEventType
from app.modules.auth.login_protection import reset_login_attempt_guard_for_tests
from app.modules.auth.router import _login_guard_key
from app.modules.iam.permission.permissions import PERMISSION_READ
from app.modules.iam.user_role.models import UserRole

pytestmark = pytest.mark.security


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


requires_postgres = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for security HTTP smoke tests",
)


def _settings(**kwargs: object) -> Settings:
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


def _request(
    *,
    headers: dict[str, str] | None = None,
    client_host: str | None = "127.0.0.1",
) -> MagicMock:
    req = MagicMock(spec=Request)
    req.headers = Headers(headers or {})
    if client_host is None:
        req.client = None
    else:
        req.client = SimpleNamespace(host=client_host)
    return req


# --- resolve_client_ip + login guard key integration -------------------------


def test_resolve_client_ip_trust_false_uses_peer() -> None:
    settings = _settings(trust_forwarded_client_ip=False)
    req = _request(
        headers={"x-forwarded-for": "203.0.113.50, 10.0.0.1"},
        client_host="192.0.2.20",
    )
    assert resolve_client_ip(req, settings=settings) == "192.0.2.20"


def test_resolve_client_ip_trust_true_uses_xff() -> None:
    settings = _settings(trust_forwarded_client_ip=True)
    req = _request(
        headers={"x-forwarded-for": "203.0.113.50, 10.0.0.1"},
        client_host="192.0.2.20",
    )
    assert resolve_client_ip(req, settings=settings) == "203.0.113.50"


def test_login_guard_key_respects_trust_false() -> None:
    settings = _settings(trust_forwarded_client_ip=False)
    req = _request(
        headers={"x-forwarded-for": "198.51.100.7"},
        client_host="127.0.0.1",
    )
    assert _login_guard_key(req, "Alice", settings) == "127.0.0.1:alice"


def test_login_guard_key_respects_trust_true() -> None:
    settings = _settings(trust_forwarded_client_ip=True)
    req = _request(
        headers={"x-forwarded-for": "198.51.100.7, 10.1.1.1"},
        client_host="127.0.0.1",
    )
    assert _login_guard_key(req, "Bob", settings) == "198.51.100.7:bob"


# --- HTTP smoke (Postgres) ---------------------------------------------------


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
def auth_user(db_session: Session) -> User:
    role = db_session.scalar(
        select(Role).where(Role.code == "AGENT", Role.deleted_at.is_(None))
    )
    if role is None:
        role = Role(code="AGENT", name="Agent", is_active=True)
        db_session.add(role)
        db_session.flush()

    user = User(
        username=f"sec_{uuid.uuid4().hex[:8]}",
        email=f"sec_{uuid.uuid4().hex[:8]}@example.com",
        full_name="Security Smoke User",
        password_hash=hash_password("Secret123!"),
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
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
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    get_settings.cache_clear()
    reset_login_attempt_guard_for_tests()
    app = create_app()

    def _override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    reset_login_attempt_guard_for_tests()
    get_settings.cache_clear()


@pytest.fixture()
def lockout_client(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("LOGIN_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("LOGIN_MAX_FAILED_ATTEMPTS", "1")
    monkeypatch.setenv("LOGIN_LOCKOUT_SECONDS", "120")
    get_settings.cache_clear()
    reset_login_attempt_guard_for_tests()
    app = create_app()

    def _override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    reset_login_attempt_guard_for_tests()
    get_settings.cache_clear()


@requires_postgres
def test_http_failed_login_lockout_returns_429_with_retry_after(
    lockout_client: TestClient,
    db_session: Session,
    auth_user: User,
) -> None:
    first = lockout_client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": "WrongPassword!"},
    )
    assert first.status_code == 401, first.text

    second = lockout_client.post(
        "/api/v1/auth/login",
        json={"username": auth_user.username, "password": "WrongPassword!"},
    )
    assert second.status_code == 429, second.text
    assert second.headers.get("Retry-After") is not None
    assert int(second.headers["Retry-After"]) >= 1
    body = second.json()
    assert body["code"] == "RATE_LIMITED"
    assert body["details"]["retryAfterSeconds"] >= 1
    assert second.headers["Retry-After"] == str(int(body["details"]["retryAfterSeconds"]))

    db_session.expire_all()
    lockouts = list(
        db_session.scalars(
            select(SystemAuditLog)
            .where(SystemAuditLog.event_type == SecurityEventType.LOCKOUT.value)
            .order_by(SystemAuditLog.created_at.desc())
            .limit(5)
        )
    )
    assert lockouts, "expected security.lockout audit row after lockout"


@requires_postgres
def test_http_bad_bearer_returns_401_and_token_rejected_audit(
    client: TestClient,
    db_session: Session,
) -> None:
    before = db_session.scalar(
        select(SystemAuditLog.id)
        .where(SystemAuditLog.event_type == SecurityEventType.TOKEN_REJECTED.value)
        .order_by(SystemAuditLog.created_at.desc())
        .limit(1)
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert response.status_code == 401, response.text
    assert response.json()["code"] == "UNAUTHENTICATED"

    db_session.expire_all()
    rows = list(
        db_session.scalars(
            select(SystemAuditLog)
            .where(SystemAuditLog.event_type == SecurityEventType.TOKEN_REJECTED.value)
            .order_by(SystemAuditLog.created_at.desc())
            .limit(5)
        )
    )
    assert rows, "expected security.token_rejected audit row"
    if before is not None:
        assert any(row.id != before for row in rows)
    latest = rows[0]
    assert latest.entity_type == "Security"
    assert (latest.metadata_json or {}).get("reasonCode") == "UNAUTHENTICATED"
    assert (latest.metadata_json or {}).get("path") == "/api/v1/auth/me"


@requires_postgres
def test_http_permission_denied_returns_403_and_permission_denied_audit(
    client: TestClient,
    db_session: Session,
    auth_user: User,
) -> None:
    token = create_access_token(
        subject=str(auth_user.id),
        settings=get_settings(),
        claims={"permissions": [], "roles": ["AGENT"]},
    )
    response = client.get(
        "/api/v1/permissions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403, response.text
    body = response.json()
    assert body["code"] == "FORBIDDEN"
    missing = (body.get("details") or {}).get("missingPermissions") or []
    assert PERMISSION_READ in missing

    db_session.expire_all()
    rows = list(
        db_session.scalars(
            select(SystemAuditLog)
            .where(
                SystemAuditLog.event_type == SecurityEventType.PERMISSION_DENIED.value,
                SystemAuditLog.actor_id == auth_user.id,
            )
            .order_by(SystemAuditLog.created_at.desc())
            .limit(5)
        )
    )
    assert rows, "expected security.permission_denied audit row"
    latest = rows[0]
    assert latest.entity_type == "Security"
    assert (latest.metadata_json or {}).get("reasonCode") == "FORBIDDEN"
    assert (latest.metadata_json or {}).get("path") == "/api/v1/permissions"
