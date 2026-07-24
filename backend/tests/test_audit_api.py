"""Audit Log integration tests (TASK-031 / API-336–337)."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import User
from app.modules.audit.models import SystemAuditLog
from app.modules.audit.permissions import AUDIT_READ
from app.modules.notification.permissions import (
    NOTIFICATION_CREATE,
    NOTIFICATION_DELETE,
    NOTIFICATION_READ,
    NOTIFICATION_UPDATE,
)


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
    reason="PostgreSQL not available for Audit API tests",
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


@pytest.fixture(autouse=True)
def ensure_audit_table(db_session: Session) -> None:
    exists = db_session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'audit_logs' AND table_schema = 'public'"
        )
    ).scalar()
    if not exists:
        pytest.skip("audit_logs platform table not migrated (0019_audit)")
    # Ensure platform columns exist (not legacy-only).
    col = db_session.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'audit_logs' AND column_name = 'event_type'"
        )
    ).scalar()
    if not col:
        pytest.skip("audit_logs missing event_type (0019_audit not applied)")


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


def test_list_and_get_audit_after_template_create(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    headers = _auth(
        actor,
        AUDIT_READ,
        NOTIFICATION_CREATE,
        NOTIFICATION_READ,
        NOTIFICATION_UPDATE,
        NOTIFICATION_DELETE,
    )
    code = f"AUD_{uuid.uuid4().hex[:10].upper()}"

    created = client.post(
        "/api/v1/notification/templates",
        headers=headers,
        json={
            "code": code,
            "name": "Audit Template",
            "channel": "EMAIL",
            "subject": "S",
            "content": "C",
            "isActive": True,
        },
    )
    assert created.status_code == 201, created.text
    template_id = created.json()["data"]["id"]

    listed = client.get(
        "/api/v1/audit",
        headers=headers,
        params={
            "entityType": "NotificationTemplate",
            "entityId": template_id,
            "action": "CREATE",
        },
    )
    assert listed.status_code == 200, listed.text
    items = listed.json()["data"]
    assert len(items) >= 1
    item = items[0]
    assert item["eventType"] == "notification.template.created"
    assert item["action"] == "CREATE"
    assert item["actorId"] == str(actor.id)

    detail = client.get(f"/api/v1/audit/{item['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["id"] == item["id"]

    row = db_session.get(SystemAuditLog, uuid.UUID(item["id"]))
    assert row is not None
    assert row.entity_type == "NotificationTemplate"


def test_settings_update_writes_audit(
    client: TestClient,
    actor: User,
) -> None:
    headers = _auth(actor, AUDIT_READ, "settings:read", "settings:update")
    before = client.get("/api/v1/settings", headers=headers)
    assert before.status_code == 200
    keys = [row["key"] for row in before.json()["data"]]
    assert "company.name" in keys

    updated = client.put(
        "/api/v1/settings/company.name",
        headers=headers,
        json={"value": "ECMP-Audit"},
    )
    assert updated.status_code == 200, updated.text

    # restore
    client.put(
        "/api/v1/settings/company.name",
        headers=headers,
        json={"value": "ECMP"},
    )

    listed = client.get(
        "/api/v1/audit",
        headers=headers,
        params={"entityType": "Setting", "action": "UPDATE"},
    )
    assert listed.status_code == 200
    assert any(
        item["eventType"] == "setting.updated" for item in listed.json()["data"]
    )


def test_audit_forbidden_without_permission(
    client: TestClient, actor: User
) -> None:
    headers = _auth(actor)  # no audit:read
    response = client.get("/api/v1/audit", headers=headers)
    assert response.status_code == 403
