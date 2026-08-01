"""SLA deadline calculator integration tests (TASK-023 / DEC-012)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import Customer, SlaPolicy, SlaRecord, User


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
    reason="PostgreSQL not available for SLA deadline API tests",
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
def auth_header(db_session: Session) -> dict[str, str]:
    from sqlalchemy import select

    user = db_session.scalar(select(User).where(User.deleted_at.is_(None)).limit(1))
    if user is None:
        pytest.skip("No seed user available")
    settings = get_settings()
    token = create_access_token(
        subject=str(user.id),
        settings=settings,
        claims={
            "permissions": [
                "complaints:create",
                "complaints:read",
                "sla:read",
                "sla:manage",
            ],
            "roles": ["ADMIN"],
        },
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def customer_id(db_session: Session) -> uuid.UUID:
    customer = Customer(
        external_customer_id=f"CUST-{uuid.uuid4().hex[:8].upper()}",
        full_name="SLA Deadline Customer",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer.id


def _activate_policy(
    db_session: Session,
    *,
    assignment: int = 60,
    appointment: int = 1440,
    resolution: int = 2880,
    escalation: int = 480,
    overall: int = 4320,
    name: str | None = None,
) -> SlaPolicy:
    now = datetime.now(UTC)
    db_session.execute(
        text("UPDATE sla_policies SET is_active = false, updated_at = :now WHERE is_active = true"),
        {"now": now},
    )
    policy = SlaPolicy(
        name=name or f"Policy-{uuid.uuid4().hex[:8]}",
        description="Integration test policy",
        assignment_target_minutes=assignment,
        appointment_target_minutes=appointment,
        resolution_target_minutes=resolution,
        escalation_target_minutes=escalation,
        overall_target_minutes=overall,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy


def test_complaint_automatically_receives_sla_record(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
) -> None:
    policy = _activate_policy(
        db_session,
        assignment=30,
        appointment=120,
        resolution=240,
        escalation=90,
        overall=480,
    )

    created = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "SLA deadline integration",
            "description": "Verify SLA snapshot on create",
            "priority": "MEDIUM",
            "channel": "WEB",
        },
        headers=auth_header,
    )
    assert created.status_code == 201, created.text
    complaint = created.json()["data"]
    complaint_id = complaint["id"]
    created_at = datetime.fromisoformat(
        complaint["createdAt"].replace("Z", "+00:00")
    )

    sla_resp = client.get(
        f"/api/v1/complaints/{complaint_id}/sla",
        headers=auth_header,
    )
    assert sla_resp.status_code == 200, sla_resp.text
    sla = sla_resp.json()["data"]
    assert sla["complaintId"] == complaint_id
    for key in (
        "assignmentStatus",
        "appointmentStatus",
        "resolutionStatus",
        "escalationStatus",
        "overallStatus",
    ):
        assert sla[key] == "PENDING"

    def _parse(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    assert _parse(sla["assignmentDueAt"]) == created_at + timedelta(
        minutes=policy.assignment_target_minutes
    )
    assert _parse(sla["appointmentDueAt"]) == created_at + timedelta(
        minutes=policy.appointment_target_minutes
    )
    assert _parse(sla["resolutionDueAt"]) == created_at + timedelta(
        minutes=policy.resolution_target_minutes
    )
    assert _parse(sla["escalationDueAt"]) == created_at + timedelta(
        minutes=policy.escalation_target_minutes
    )
    assert _parse(sla["overallDueAt"]) == created_at + timedelta(
        minutes=policy.overall_target_minutes
    )

    row = db_session.get(SlaRecord, uuid.UUID(sla["id"]))
    assert row is not None
    assert row.assignment_due_at is not None
    assert row.overall_due_at is not None


def test_create_rejected_without_active_policy(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
) -> None:
    db_session.execute(
        text(
            "UPDATE sla_policies SET is_active = false, updated_at = :now "
            "WHERE is_active = true"
        ),
        {"now": datetime.now(UTC)},
    )
    db_session.commit()

    response = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "No policy",
            "description": "Should reject",
            "priority": "LOW",
            "channel": "WEB",
        },
        headers=auth_header,
    )
    assert response.status_code == 400, response.text
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "Kebijakan SLA aktif" in body["message"]


def test_existing_deadlines_unchanged_after_policy_switch(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
) -> None:
    _activate_policy(
        db_session,
        assignment=60,
        appointment=120,
        resolution=180,
        escalation=90,
        overall=240,
        name="Policy-A",
    )
    first = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "First complaint",
            "description": "Snapshot under policy A",
            "priority": "HIGH",
            "channel": "EMAIL",
        },
        headers=auth_header,
    )
    assert first.status_code == 201, first.text
    cid = first.json()["data"]["id"]
    sla_before = client.get(
        f"/api/v1/complaints/{cid}/sla", headers=auth_header
    ).json()["data"]

    _activate_policy(
        db_session,
        assignment=15,
        appointment=30,
        resolution=45,
        escalation=20,
        overall=60,
        name="Policy-B",
    )

    sla_after = client.get(
        f"/api/v1/complaints/{cid}/sla", headers=auth_header
    ).json()["data"]
    assert sla_after["assignmentDueAt"] == sla_before["assignmentDueAt"]
    assert sla_after["appointmentDueAt"] == sla_before["appointmentDueAt"]
    assert sla_after["resolutionDueAt"] == sla_before["resolutionDueAt"]
    assert sla_after["escalationDueAt"] == sla_before["escalationDueAt"]
    assert sla_after["overallDueAt"] == sla_before["overallDueAt"]

    second = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "Second complaint",
            "description": "Snapshot under policy B",
            "priority": "LOW",
            "channel": "WEB",
        },
        headers=auth_header,
    )
    assert second.status_code == 201, second.text
    cid2 = second.json()["data"]["id"]
    created2 = datetime.fromisoformat(
        second.json()["data"]["createdAt"].replace("Z", "+00:00")
    )
    sla2 = client.get(
        f"/api/v1/complaints/{cid2}/sla", headers=auth_header
    ).json()["data"]
    due2 = datetime.fromisoformat(
        sla2["assignmentDueAt"].replace("Z", "+00:00")
    )
    assert due2 == created2 + timedelta(minutes=15)
