"""SLA timeline integration API tests (TASK-025 / DEC-014)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.enums import TimelineEvent
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import ComplaintTimeline, Customer, SlaPolicy, SlaRecord, User


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
    reason="PostgreSQL not available for SLA timeline API tests",
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


@pytest.fixture()
def auth_header(actor: User) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={
            "permissions": [
                "complaints:create",
                "complaints:read",
                "complaints:assign",
                "sla:read",
                "sla:manage",
            ],
            "roles": ["ADMIN", "SUPERVISOR"],
        },
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def customer_id(db_session: Session) -> uuid.UUID:
    customer = Customer(
        external_customer_id=f"CUST-{uuid.uuid4().hex[:8].upper()}",
        full_name="SLA Timeline Customer",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer.id


def _activate_policy(db_session: Session) -> SlaPolicy:
    now = datetime.now(UTC)
    db_session.execute(
        text(
            "UPDATE sla_policies SET is_active = false, updated_at = :now "
            "WHERE is_active = true"
        ),
        {"now": now},
    )
    policy = SlaPolicy(
        name=f"Timeline-Policy-{uuid.uuid4().hex[:8]}",
        description="SLA timeline integration",
        assignment_target_minutes=120,
        appointment_target_minutes=1440,
        resolution_target_minutes=2880,
        escalation_target_minutes=480,
        overall_target_minutes=4320,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy


def test_lifecycle_generates_sla_timeline_entries(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
    actor: User,
) -> None:
    _activate_policy(db_session)

    created = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "SLA timeline completed",
            "description": "Expect assignment completed event",
            "priority": "MEDIUM",
            "channel": "WEB",
        },
        headers=auth_header,
    )
    assert created.status_code == 201, created.text
    cid = created.json()["data"]["id"]

    assigned = client.post(
        f"/api/v1/complaints/{cid}/assign",
        json={"assigneeId": str(actor.id)},
        headers=auth_header,
    )
    assert assigned.status_code == 200, assigned.text

    timeline = client.get(
        f"/api/v1/complaints/{cid}/timeline",
        headers=auth_header,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["data"]
    sla_events = [e for e in events if e["eventType"].startswith("sla.")]
    assert any(
        e["eventType"] == TimelineEvent.SLA_ASSIGNMENT_COMPLETED.value
        for e in sla_events
    )
    completed = next(
        e
        for e in sla_events
        if e["eventType"] == TimelineEvent.SLA_ASSIGNMENT_COMPLETED.value
    )
    assert completed["summary"] == "SLA Assignment Completed"
    assert completed["actorUserId"] is None
    assert completed["actorName"] is None
    assert completed["metadata"]["actor"] == "SYSTEM"
    assert completed["metadata"]["newStatus"] == "COMPLETED"

    # Re-fetch SLA (re-evaluate) — no duplicate SLA assignment completed.
    client.get(f"/api/v1/complaints/{cid}/sla", headers=auth_header)
    timeline2 = client.get(
        f"/api/v1/complaints/{cid}/timeline",
        headers=auth_header,
    ).json()["data"]
    completed_count = sum(
        1
        for e in timeline2
        if e["eventType"] == TimelineEvent.SLA_ASSIGNMENT_COMPLETED.value
    )
    assert completed_count == 1


def test_breach_timeline_and_no_duplicates(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
) -> None:
    _activate_policy(db_session)

    created = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "SLA timeline breached",
            "description": "Expect breach events",
            "priority": "HIGH",
            "channel": "EMAIL",
        },
        headers=auth_header,
    )
    assert created.status_code == 201, created.text
    cid = uuid.UUID(created.json()["data"]["id"])

    past = datetime.now(UTC) - timedelta(hours=2)
    row = db_session.scalar(select(SlaRecord).where(SlaRecord.complaint_id == cid))
    assert row is not None
    row.assignment_due_at = past
    row.appointment_due_at = past
    row.resolution_due_at = past
    row.escalation_due_at = past
    row.overall_due_at = past
    db_session.commit()

    sla = client.get(f"/api/v1/complaints/{cid}/sla", headers=auth_header)
    assert sla.status_code == 200
    assert sla.json()["data"]["assignmentStatus"] == "BREACHED"

    timeline = client.get(
        f"/api/v1/complaints/{cid}/timeline",
        headers=auth_header,
    ).json()["data"]
    breached = [
        e for e in timeline if e["eventType"] == "sla.assignment.breached"
    ]
    assert len(breached) == 1
    assert breached[0]["summary"] == "SLA Assignment Breached"
    assert breached[0]["metadata"]["actor"] == "SYSTEM"

    # Second evaluation must not duplicate.
    client.get(f"/api/v1/complaints/{cid}/sla", headers=auth_header)
    timeline2 = client.get(
        f"/api/v1/complaints/{cid}/timeline",
        headers=auth_header,
    ).json()["data"]
    assert (
        sum(1 for e in timeline2 if e["eventType"] == "sla.assignment.breached")
        == 1
    )

    db_count = len(
        list(
            db_session.scalars(
                select(ComplaintTimeline).where(
                    ComplaintTimeline.complaint_id == cid,
                    ComplaintTimeline.event_type
                    == TimelineEvent.SLA_ASSIGNMENT_BREACHED.value,
                )
            )
        )
    )
    assert db_count == 1
