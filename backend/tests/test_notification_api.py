"""Notification Foundation integration tests (TASK-030 / API-327–335)."""

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
from app.models import NotificationQueue, NotificationTemplate, Setting, User
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
    reason="PostgreSQL not available for Notification API tests",
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
def ensure_notification_settings(db_session: Session) -> None:
    row = db_session.scalar(
        select(Setting).where(Setting.key == "notification.enabled")
    )
    if row is None:
        pytest.skip("notification settings seed not migrated (0018_notification)")
    row.value = "true"
    db_session.commit()


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


def _unique_code() -> str:
    return f"TPL_{uuid.uuid4().hex[:12].upper()}"


def test_template_crud_flow(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    headers = _auth(
        actor,
        NOTIFICATION_READ,
        NOTIFICATION_CREATE,
        NOTIFICATION_UPDATE,
        NOTIFICATION_DELETE,
    )
    code = _unique_code()

    created = client.post(
        "/api/v1/notification/templates",
        headers=headers,
        json={
            "code": code,
            "name": "Test Template",
            "channel": "EMAIL",
            "subject": "Hello {{name}}",
            "content": "Body for {{name}}",
            "isActive": True,
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()["data"]
    template_id = body["id"]
    assert body["code"] == code
    assert body["isActive"] is True

    listed = client.get("/api/v1/notification/templates", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == template_id for item in listed.json()["data"])

    got = client.get(f"/api/v1/notification/templates/{template_id}", headers=headers)
    assert got.status_code == 200
    assert got.json()["data"]["name"] == "Test Template"

    updated = client.put(
        f"/api/v1/notification/templates/{template_id}",
        headers=headers,
        json={"name": "Updated Template", "channel": "WHATSAPP"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["name"] == "Updated Template"
    assert updated.json()["data"]["channel"] == "WHATSAPP"

    deleted = client.delete(
        f"/api/v1/notification/templates/{template_id}", headers=headers
    )
    assert deleted.status_code == 204

    row = db_session.get(NotificationTemplate, uuid.UUID(template_id))
    assert row is not None
    assert row.is_active is False


def test_queue_create_get_list_cancel(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    headers = _auth(
        actor,
        NOTIFICATION_READ,
        NOTIFICATION_CREATE,
        NOTIFICATION_UPDATE,
    )
    code = _unique_code()

    tpl = client.post(
        "/api/v1/notification/templates",
        headers=headers,
        json={
            "code": code,
            "name": "Queue Template",
            "channel": "EMAIL",
            "subject": "Case {{complaintNumber}}",
            "content": "Assigned to {{assigneeName}}",
            "isActive": True,
        },
    )
    assert tpl.status_code == 201, tpl.text

    created = client.post(
        "/api/v1/notifications",
        headers=headers,
        json={
            "templateCode": code,
            "recipient": "handler@example.com",
            "variables": {
                "complaintNumber": "CMP-QUEUE-1",
                "assigneeName": "Budi",
            },
        },
    )
    assert created.status_code == 201, created.text
    queue_body = created.json()["data"]
    queue_id = queue_body["id"]
    assert queue_body["status"] == "PENDING"
    assert queue_body["channel"] == "EMAIL"
    assert queue_body["type"] == "TemplateEnqueue"
    assert queue_body["subject"] == "Case CMP-QUEUE-1"
    assert queue_body["message"] == "Assigned to Budi"
    assert queue_body["payload"]["subject"] == "Case CMP-QUEUE-1"
    assert queue_body["payload"]["content"] == "Assigned to Budi"
    assert queue_body["payload"]["maxRetry"] == 3

    detail = client.get(f"/api/v1/notifications/{queue_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["id"] == queue_id

    listed = client.get(
        "/api/v1/notifications",
        headers=headers,
        params={"status": "PENDING"},
    )
    assert listed.status_code == 200
    assert any(item["id"] == queue_id for item in listed.json()["data"])

    cancelled = client.post(
        f"/api/v1/notifications/{queue_id}/cancel", headers=headers
    )
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["data"]["status"] == "CANCELLED"

    row = db_session.get(NotificationQueue, uuid.UUID(queue_id))
    assert row is not None
    assert row.status == "CANCELLED"


def test_no_send_endpoint(client: TestClient, actor: User) -> None:
    headers = _auth(actor, NOTIFICATION_CREATE, NOTIFICATION_UPDATE)
    fake_id = uuid.uuid4()
    response = client.post(f"/api/v1/notifications/{fake_id}/send", headers=headers)
    assert response.status_code == 404


def test_process_and_retry_stub_provider(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    """CAPABILITY-009 — process via stub + retry FAILED (API-356/357)."""
    # Ensure migration 0033 columns exist
    try:
        db_session.execute(text("SELECT channel, failed_at FROM notification_queue LIMIT 0"))
    except Exception:
        pytest.skip("notification domain columns missing (0033_notification_domain)")

    headers = _auth(
        actor,
        NOTIFICATION_READ,
        NOTIFICATION_CREATE,
        NOTIFICATION_UPDATE,
    )
    code = _unique_code()
    tpl = client.post(
        "/api/v1/notification/templates",
        headers=headers,
        json={
            "code": code,
            "name": "Process Template",
            "channel": "SMS",
            "subject": None,
            "content": "SMS body {{name}}",
            "isActive": True,
        },
    )
    assert tpl.status_code == 201, tpl.text

    created = client.post(
        "/api/v1/notifications",
        headers=headers,
        json={
            "templateCode": code,
            "recipient": "+62123456789",
            "variables": {"name": "Ada"},
        },
    )
    assert created.status_code == 201, created.text
    queue_id = created.json()["data"]["id"]
    assert created.json()["data"]["channel"] == "SMS"

    processed = client.post(
        f"/api/v1/notifications/{queue_id}/process", headers=headers
    )
    assert processed.status_code == 200, processed.text
    assert processed.json()["data"]["status"] == "SENT"
    assert processed.json()["data"]["sentAt"] is not None

    # Force FAILED to exercise retry
    row = db_session.get(NotificationQueue, uuid.UUID(queue_id))
    assert row is not None
    row.status = "FAILED"
    row.failed_at = row.sent_at
    row.sent_at = None
    row.last_error = "forced"
    db_session.commit()

    retried = client.post(
        f"/api/v1/notifications/{queue_id}/retry", headers=headers
    )
    assert retried.status_code == 200, retried.text
    assert retried.json()["data"]["status"] == "PENDING"
    assert retried.json()["data"]["retryCount"] == 1
    assert retried.json()["data"]["failedAt"] is None


def test_queue_forbidden_without_permission(
    client: TestClient, actor: User
) -> None:
    headers = _auth(actor)  # no notification permissions
    response = client.get("/api/v1/notifications", headers=headers)
    assert response.status_code == 403
