"""System Settings integration tests (TASK-028 / API-320–322)."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import Setting, User
from app.modules.settings.registry import SettingsKey


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
    reason="PostgreSQL not available for Settings API tests",
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
def actor(db_session: Session) -> User:
    user = db_session.scalar(select(User).where(User.deleted_at.is_(None)).limit(1))
    if user is None:
        pytest.skip("No seed user available")
    return user


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


def test_public_settings_no_auth(client: TestClient, db_session: Session) -> None:
    count = db_session.scalar(select(Setting.id).limit(1))
    if count is None:
        pytest.skip("settings seed not migrated")

    resp = client.get("/api/v1/settings/public")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(item["visibility"] == "PUBLIC" for item in data)
    keys = {item["key"] for item in data}
    assert SettingsKey.COMPANY_NAME.value in keys
    assert SettingsKey.DASHBOARD_RECENT_LIMIT.value not in keys


def test_list_settings_requires_permission(
    client: TestClient, actor: User, db_session: Session
) -> None:
    if db_session.scalar(select(Setting.id).limit(1)) is None:
        pytest.skip("settings seed not migrated")

    denied = client.get("/api/v1/settings", headers=_auth(actor, "complaints:read"))
    assert denied.status_code == 403

    ok = client.get("/api/v1/settings", headers=_auth(actor, "settings:read"))
    assert ok.status_code == 200
    keys = {item["key"] for item in ok.json()["data"]}
    assert SettingsKey.COMPANY_NAME.value in keys
    assert SettingsKey.DASHBOARD_RECENT_LIMIT.value in keys
    assert SettingsKey.COMPLAINT_NUMBER_PREFIX.value in keys


def test_update_setting_validates_and_persists(
    client: TestClient, actor: User, db_session: Session
) -> None:
    row = db_session.scalar(
        select(Setting).where(Setting.key == SettingsKey.COMPANY_NAME.value)
    )
    if row is None:
        pytest.skip("settings seed not migrated")
    original = row.value

    headers = _auth(actor, "settings:update", "settings:read")
    resp = client.put(
        f"/api/v1/settings/{SettingsKey.COMPANY_NAME.value}",
        headers=headers,
        json={"value": "ECMP Test Co"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["value"] == "ECMP Test Co"
    assert resp.json()["data"]["key"] == SettingsKey.COMPANY_NAME.value

    db_session.expire_all()
    refreshed = db_session.scalar(
        select(Setting).where(Setting.key == SettingsKey.COMPANY_NAME.value)
    )
    assert refreshed is not None
    assert refreshed.value == "ECMP Test Co"

    # restore
    client.put(
        f"/api/v1/settings/{SettingsKey.COMPANY_NAME.value}",
        headers=headers,
        json={"value": original},
    )


def test_update_integer_setting_rejects_invalid(
    client: TestClient, actor: User, db_session: Session
) -> None:
    if db_session.scalar(select(Setting.id).limit(1)) is None:
        pytest.skip("settings seed not migrated")

    headers = _auth(actor, "settings:update")
    resp = client.put(
        f"/api/v1/settings/{SettingsKey.DASHBOARD_RECENT_LIMIT.value}",
        headers=headers,
        json={"value": "not-int"},
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_update_requires_permission(
    client: TestClient, actor: User, db_session: Session
) -> None:
    if db_session.scalar(select(Setting.id).limit(1)) is None:
        pytest.skip("settings seed not migrated")

    resp = client.put(
        f"/api/v1/settings/{SettingsKey.APP_LANGUAGE.value}",
        headers=_auth(actor, "settings:read"),
        json={"value": "en"},
    )
    assert resp.status_code == 403


def test_update_unknown_key_404(client: TestClient, actor: User) -> None:
    resp = client.put(
        "/api/v1/settings/does.not.exist",
        headers=_auth(actor, "settings:update"),
        json={"value": "x"},
    )
    assert resp.status_code == 404
