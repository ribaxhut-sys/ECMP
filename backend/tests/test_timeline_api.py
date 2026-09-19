"""CAPABILITY-010 Activity Timeline API + event handler tests."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from types import MappingProxyType
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import User
from app.modules.complaint_events.models import (
    ComplaintEvent,
    ComplaintEventType,
    EventSourceRef,
    EventTargetRef,
)
from app.modules.event_dispatcher import EventDispatcher
from app.modules.timeline.domain.enums import AggregateType, TimelineEventType
from app.modules.timeline.handler import TimelineEventHandler
from app.modules.timeline.permissions import TIMELINE_CREATE, TIMELINE_READ
from app.modules.timeline.registration import register_timeline_handler
from app.modules.timeline.schemas import TimelineEntryResponse


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
    reason="PostgreSQL not available for Timeline API tests",
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
def require_timeline_table(db_session: Session) -> None:
    try:
        db_session.execute(text("SELECT 1 FROM timeline_entries LIMIT 0"))
    except Exception:
        pytest.skip("timeline_entries missing (run alembic upgrade to 0034)")


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


def test_create_list_get_activity_timeline(
    client: TestClient, actor: User
) -> None:
    headers = _auth(actor, TIMELINE_READ, TIMELINE_CREATE)
    aggregate_id = str(uuid.uuid4())
    created = client.post(
        "/api/v1/timeline",
        headers=headers,
        json={
            "aggregateType": "Complaint",
            "aggregateId": aggregate_id,
            "eventType": "ComplaintCreated",
            "title": "Complaint created",
            "description": "test",
            "actorType": "SYSTEM",
            "metadata": {"source": "api-test"},
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()["data"]
    entry_id = body["id"]
    assert body["aggregateType"] == "Complaint"
    assert body["eventType"] == "ComplaintCreated"

    listed = client.get(
        "/api/v1/timeline",
        headers=headers,
        params={"aggregateType": "Complaint", "aggregateId": aggregate_id},
    )
    assert listed.status_code == 200, listed.text
    assert listed.json()["meta"]["totalItems"] >= 1
    assert any(item["id"] == entry_id for item in listed.json()["data"])

    got = client.get(f"/api/v1/timeline/{entry_id}", headers=headers)
    assert got.status_code == 200
    assert got.json()["data"]["id"] == entry_id

    # DEC-026: nested Foundation activity-timeline is unmounted.
    by_complaint = client.get(
        f"/api/v1/complaints/{aggregate_id}/activity-timeline",
        headers=headers,
    )
    assert by_complaint.status_code == 404


def test_timeline_forbidden_without_permission(
    client: TestClient, actor: User
) -> None:
    headers = _auth(actor)
    response = client.get("/api/v1/timeline", headers=headers)
    assert response.status_code == 403


def test_no_update_or_delete_routes(client: TestClient, actor: User) -> None:
    headers = _auth(actor, TIMELINE_READ, TIMELINE_CREATE)
    fake = uuid.uuid4()
    assert client.put(f"/api/v1/timeline/{fake}", headers=headers).status_code == 405
    assert client.delete(f"/api/v1/timeline/{fake}", headers=headers).status_code == 405


def test_register_timeline_handler_idempotent() -> None:
    dispatcher = EventDispatcher()
    first = register_timeline_handler(dispatcher)
    second = register_timeline_handler(dispatcher)
    assert first is second
    assert sum(1 for h in dispatcher.registered_handlers() if isinstance(h, TimelineEventHandler)) == 1


def test_timeline_event_handler_records_complaint_event() -> None:
    complaint_id = uuid.uuid4()
    event = ComplaintEvent(
        event_id=uuid.uuid4(),
        event_type=ComplaintEventType.CREATED,
        occurred_at=datetime.now(UTC),
        complaint_id=complaint_id,
        complaint_number="CMP-TL-1",
        current_status="NEW",
        priority="MEDIUM",
        source=EventSourceRef(source_type="CUSTOMER", source_id=uuid.uuid4()),
        target=EventTargetRef(target_type="BRANCH", target_id=uuid.uuid4()),
        routing=None,
        context_reference=None,
        payload=MappingProxyType({}),
    )

    recorded: list[TimelineEntryResponse] = []

    class _FakeService:
        def record(self, **kwargs):  # type: ignore[no-untyped-def]
            resp = TimelineEntryResponse(
                id=uuid.uuid4(),
                aggregateType=kwargs["aggregate_type"],
                aggregateId=kwargs["aggregate_id"],
                eventType=kwargs["event_type"],
                title=kwargs["title"],
                description=kwargs.get("description"),
                actorType=kwargs.get("actor_type"),
                actorId=kwargs.get("actor_id"),
                actorName=kwargs.get("actor_name"),
                metadata=kwargs.get("metadata"),
                createdAt=datetime.now(UTC),
            )
            recorded.append(resp)
            return resp

    handler = TimelineEventHandler()
    fake_session = MagicMock()
    with (
        patch(
            "app.modules.timeline.handler.get_session_factory",
            return_value=lambda: fake_session,
        ),
        patch(
            "app.modules.timeline.handler.ActivityTimelineService",
            return_value=_FakeService(),
        ),
    ):
        handler.handle(event)

    assert len(recorded) == 1
    assert recorded[0].aggregate_type == AggregateType.COMPLAINT.value
    assert recorded[0].event_type == TimelineEventType.COMPLAINT_CREATED.value
    assert recorded[0].aggregate_id == complaint_id
    fake_session.close.assert_called_once()
