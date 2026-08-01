"""Identity & Password Management API tests."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.password_policy import get_password_policy
from app.core.security import (
    create_access_token,
    generate_password_reset_token,
    hash_password,
    hash_password_reset_token,
    verify_password,
)
from app.db.session import get_db_session
from app.main import create_app
from app.models import PasswordResetToken, RefreshToken, Role, User
from app.modules.email import NoOpEmailService
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
    reason="PostgreSQL not available for password management tests",
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


def _ensure_role(session: Session, code: str = "AGENT") -> Role:
    role = session.scalar(select(Role).where(Role.code == code, Role.deleted_at.is_(None)))
    if role is None:
        role = Role(code=code, name=code.title(), is_active=True)
        session.add(role)
        session.flush()
    return role


def _make_user(
    session: Session,
    *,
    password: str = "Secret123!",
    force_password_change: bool = False,
    role_code: str = "AGENT",
) -> User:
    role = _ensure_role(session, role_code)
    user = User(
        username=f"pw_{uuid.uuid4().hex[:8]}",
        email=f"pw_{uuid.uuid4().hex[:8]}@example.com",
        full_name="Password Test User",
        password_hash=hash_password(password),
        role_id=role.id,
        is_active=True,
        force_password_change=force_password_change,
    )
    session.add(user)
    session.flush()
    if (
        session.scalar(
            select(UserRole).where(
                UserRole.user_id == user.id, UserRole.role_id == role.id
            )
        )
        is None
    ):
        session.add(UserRole(user_id=user.id, role_id=role.id))
        session.flush()
    session.commit()
    session.refresh(user)
    return user


def _auth_header(user: User, *, permissions: list[str] | None = None) -> dict[str, str]:
    settings = get_settings()
    claims: dict = {"roles": ["AGENT"]}
    if permissions is not None:
        claims["permissions"] = permissions
    token = create_access_token(
        subject=str(user.id), settings=settings, claims=claims
    )
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Password policy (unit)
# ---------------------------------------------------------------------------


def test_password_policy_rejects_short_and_same() -> None:
    policy = get_password_policy(min_length=8)
    with pytest.raises(Exception):
        policy.validate("short")
    with pytest.raises(Exception):
        policy.validate("")
    hashed = hash_password("SamePass1!")
    with pytest.raises(Exception):
        policy.validate("SamePass1!", current_hash=hashed)
    policy.validate("Different9!")


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------


def test_change_password_success(client: TestClient, db_session: Session) -> None:
    user = _make_user(db_session, password="OldPass12!")
    resp = client.post(
        "/api/v1/users/me/change-password",
        headers=_auth_header(user),
        json={
            "currentPassword": "OldPass12!",
            "newPassword": "NewPass34!",
            "confirmPassword": "NewPass34!",
        },
    )
    assert resp.status_code == 200, resp.text
    db_session.refresh(user)
    assert verify_password("NewPass34!", user.password_hash)
    assert user.force_password_change is False


def test_change_password_wrong_current(client: TestClient, db_session: Session) -> None:
    user = _make_user(db_session, password="OldPass12!")
    resp = client.post(
        "/api/v1/users/me/change-password",
        headers=_auth_header(user),
        json={
            "currentPassword": "WrongPass1!",
            "newPassword": "NewPass34!",
            "confirmPassword": "NewPass34!",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_change_password_mismatch(client: TestClient, db_session: Session) -> None:
    user = _make_user(db_session, password="OldPass12!")
    resp = client.post(
        "/api/v1/users/me/change-password",
        headers=_auth_header(user),
        json={
            "currentPassword": "OldPass12!",
            "newPassword": "NewPass34!",
            "confirmPassword": "OtherPass9!",
        },
    )
    assert resp.status_code == 400


def test_change_password_rejects_same(client: TestClient, db_session: Session) -> None:
    user = _make_user(db_session, password="SamePass1!")
    resp = client.post(
        "/api/v1/users/me/change-password",
        headers=_auth_header(user),
        json={
            "currentPassword": "SamePass1!",
            "newPassword": "SamePass1!",
            "confirmPassword": "SamePass1!",
        },
    )
    assert resp.status_code == 400


def test_change_password_revokes_refresh_tokens(
    client: TestClient, db_session: Session
) -> None:
    user = _make_user(db_session, password="OldPass12!")
    token_row = RefreshToken(
        user_id=user.id,
        token_hash=uuid.uuid4().hex + uuid.uuid4().hex[:32],
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    db_session.add(token_row)
    db_session.commit()

    resp = client.post(
        "/api/v1/users/me/change-password",
        headers=_auth_header(user),
        json={
            "currentPassword": "OldPass12!",
            "newPassword": "NewPass34!",
            "confirmPassword": "NewPass34!",
        },
    )
    assert resp.status_code == 200
    db_session.refresh(token_row)
    assert token_row.revoked_at is not None


# ---------------------------------------------------------------------------
# Forgot / reset password
# ---------------------------------------------------------------------------


def test_forgot_password_always_same_message(
    client: TestClient, db_session: Session
) -> None:
    user = _make_user(db_session)
    known = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": user.email},
    )
    unknown = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nobody_exists@example.com"},
    )
    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json()["data"]["message"] == unknown.json()["data"]["message"]
    assert known.json()["data"]["message"]


def test_forgot_password_message_localized_by_accept_language(
    client: TestClient, db_session: Session
) -> None:
    user = _make_user(db_session)
    id_resp = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": user.email},
        headers={"Accept-Language": "id"},
    )
    en_resp = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nobody_exists@example.com"},
        headers={"Accept-Language": "en-US,en;q=0.9"},
    )
    assert id_resp.status_code == 200
    assert en_resp.status_code == 200
    # Same wording regardless of account existence — no leakage — but the
    # language differs based solely on the request header.
    assert id_resp.json()["data"]["message"] != en_resp.json()["data"]["message"]
    assert "reset link" in en_resp.json()["data"]["message"].lower()


def test_forgot_password_stores_hash_only(db_session: Session) -> None:
    user = _make_user(db_session)
    captured: dict[str, str] = {}

    class CapturingEmail(NoOpEmailService):
        def send_password_reset(
            self, *, to_email: str, reset_url: str, expires_at, language=None
        ):
            captured["url"] = reset_url
            captured["email"] = to_email
            captured["language"] = language

    from app.modules.auth.repository import AuthRepository
    from app.modules.auth.schemas import ForgotPasswordRequest
    from app.modules.auth.service import AuthService

    service = AuthService(
        AuthRepository(db_session), get_settings(), CapturingEmail()
    )
    service.forgot_password(ForgotPasswordRequest(email=user.email))
    assert "url" in captured
    assert captured["language"] == "id"
    assert "token=" in captured["url"]
    raw = captured["url"].split("token=", 1)[1]
    rows = list(
        db_session.scalars(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        ).all()
    )
    assert len(rows) >= 1
    assert rows[-1].token_hash == hash_password_reset_token(raw)
    assert raw != rows[-1].token_hash


def test_reset_password_success(client: TestClient, db_session: Session) -> None:
    user = _make_user(db_session, password="OldPass12!")
    raw = generate_password_reset_token()
    row = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_password_reset_token(raw),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(row)
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": raw,
            "password": "FreshPass9!",
            "confirmPassword": "FreshPass9!",
        },
    )
    assert resp.status_code == 200, resp.text
    db_session.refresh(user)
    db_session.refresh(row)
    assert verify_password("FreshPass9!", user.password_hash)
    assert row.used_at is not None


def test_reset_password_expired(client: TestClient, db_session: Session) -> None:
    user = _make_user(db_session)
    raw = generate_password_reset_token()
    row = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_password_reset_token(raw),
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    db_session.add(row)
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": raw,
            "password": "FreshPass9!",
            "confirmPassword": "FreshPass9!",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["details"]["reason"] == "expired"


def test_reset_password_used_token(client: TestClient, db_session: Session) -> None:
    user = _make_user(db_session)
    raw = generate_password_reset_token()
    row = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_password_reset_token(raw),
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        used_at=datetime.now(UTC),
    )
    db_session.add(row)
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": raw,
            "password": "FreshPass9!",
            "confirmPassword": "FreshPass9!",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["details"]["reason"] == "reused"


def test_reset_password_invalid_token(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "not-a-real-token",
            "password": "FreshPass9!",
            "confirmPassword": "FreshPass9!",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["details"]["reason"] == "invalid"


# ---------------------------------------------------------------------------
# Admin reset + force password change
# ---------------------------------------------------------------------------


def test_admin_reset_password(client: TestClient, db_session: Session) -> None:
    admin = _make_user(db_session, role_code="ADMIN")
    target = _make_user(db_session, password="OldPass12!")
    resp = client.post(
        f"/api/v1/users/{target.id}/reset-password",
        headers=_auth_header(admin, permissions=["users:reset_password"]),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()["data"]
    assert body["forcePasswordChange"] is True
    assert body["temporaryPassword"]
    db_session.refresh(target)
    assert target.force_password_change is True
    assert verify_password(body["temporaryPassword"], target.password_hash)


def test_admin_reset_forbidden_without_permission(
    client: TestClient, db_session: Session
) -> None:
    agent = _make_user(db_session)
    target = _make_user(db_session)
    resp = client.post(
        f"/api/v1/users/{target.id}/reset-password",
        headers=_auth_header(agent, permissions=["users:read"]),
    )
    assert resp.status_code == 403


def test_force_password_change_blocks_app_access(
    client: TestClient, db_session: Session
) -> None:
    user = _make_user(db_session, force_password_change=True)
    headers = _auth_header(user, permissions=["users:read", "complaints:read"])

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["data"]["forcePasswordChange"] is True

    blocked = client.get("/api/v1/users", headers=headers)
    assert blocked.status_code == 403
    assert blocked.json()["code"] == "PASSWORD_CHANGE_REQUIRED"

    allowed = client.post(
        "/api/v1/users/me/change-password",
        headers=headers,
        json={
            "currentPassword": "Secret123!",
            "newPassword": "Changed99!",
            "confirmPassword": "Changed99!",
        },
    )
    assert allowed.status_code == 200, allowed.text
    db_session.refresh(user)
    assert user.force_password_change is False


# ---------------------------------------------------------------------------
# Preferred language
# ---------------------------------------------------------------------------


def test_new_user_defaults_to_id_preferred_language(db_session: Session) -> None:
    user = _make_user(db_session)
    assert user.preferred_language == "id"


def test_auth_me_includes_preferred_language(
    client: TestClient, db_session: Session
) -> None:
    user = _make_user(db_session)
    resp = client.get("/api/v1/auth/me", headers=_auth_header(user))
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["preferredLanguage"] == "id"


def test_update_preferred_language_success(
    client: TestClient, db_session: Session
) -> None:
    user = _make_user(db_session)
    resp = client.patch(
        "/api/v1/users/me/preferred-language",
        headers=_auth_header(user),
        json={"preferredLanguage": "en"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["preferredLanguage"] == "en"
    db_session.refresh(user)
    assert user.preferred_language == "en"

    me = client.get("/api/v1/auth/me", headers=_auth_header(user))
    assert me.json()["data"]["preferredLanguage"] == "en"


def test_update_preferred_language_rejects_invalid_value(
    client: TestClient, db_session: Session
) -> None:
    user = _make_user(db_session)
    resp = client.patch(
        "/api/v1/users/me/preferred-language",
        headers=_auth_header(user),
        json={"preferredLanguage": "fr"},
    )
    assert resp.status_code in (400, 422)


def test_update_preferred_language_requires_auth(client: TestClient) -> None:
    resp = client.patch(
        "/api/v1/users/me/preferred-language",
        json={"preferredLanguage": "en"},
    )
    assert resp.status_code == 401


def test_password_reset_email_uses_user_preferred_language(
    db_session: Session,
) -> None:
    user = _make_user(db_session)
    user.preferred_language = "en"
    db_session.add(user)
    db_session.commit()

    captured: dict[str, str] = {}

    class CapturingEmail(NoOpEmailService):
        def send_password_reset(
            self, *, to_email: str, reset_url: str, expires_at, language=None
        ):
            captured["language"] = language

    from app.modules.auth.repository import AuthRepository
    from app.modules.auth.schemas import ForgotPasswordRequest
    from app.modules.auth.service import AuthService

    service = AuthService(AuthRepository(db_session), get_settings(), CapturingEmail())
    service.forgot_password(ForgotPasswordRequest(email=user.email))
    assert captured["language"] == "en"
