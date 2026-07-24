"""SLA breach detection integration tests (TASK-024 / DEC-013)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
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
    reason="PostgreSQL not available for SLA breach API tests",
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
                "complaints:update",
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
        full_name="SLA Breach Customer",
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
) -> SlaPolicy:
    now = datetime.now(UTC)
    db_session.execute(
        text(
            "UPDATE sla_policies SET is_active = false, updated_at = :now "
            "WHERE is_active = true"
        ),
        {"now": now},
    )
    policy = SlaPolicy(
        name=f"Breach-Policy-{uuid.uuid4().hex[:8]}",
        description="Integration breach policy",
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


def test_lifecycle_updates_sla_assignment_completed(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
    actor: User,
) -> None:
    _activate_policy(db_session, assignment=120)

    created = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "SLA completed path",
            "description": "Assign before due",
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

    sla = client.get(f"/api/v1/complaints/{cid}/sla", headers=auth_header)
    assert sla.status_code == 200, sla.text
    data = sla.json()["data"]
    assert data["assignmentStatus"] == "COMPLETED"
    assert data["assignmentDueAt"] is not None


def test_overdue_marks_breached_without_changing_dues(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
) -> None:
    _activate_policy(db_session, assignment=60, overall=120)

    created = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": "SLA breached path",
            "description": "Pass due without completion",
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
    frozen = (
        row.assignment_due_at,
        row.appointment_due_at,
        row.resolution_due_at,
        row.escalation_due_at,
        row.overall_due_at,
    )
    row.assignment_due_at = past
    row.appointment_due_at = past
    row.resolution_due_at = past
    row.escalation_due_at = past
    row.overall_due_at = past
    db_session.commit()

    sla = client.get(f"/api/v1/complaints/{cid}/sla", headers=auth_header)
    assert sla.status_code == 200, sla.text
    data = sla.json()["data"]
    assert data["assignmentStatus"] == "BREACHED"
    assert data["appointmentStatus"] == "BREACHED"
    assert data["resolutionStatus"] == "BREACHED"
    assert data["escalationStatus"] == "BREACHED"
    assert data["overallStatus"] == "BREACHED"

    db_session.refresh(row)
    assert (
        row.assignment_due_at,
        row.appointment_due_at,
        row.resolution_due_at,
        row.escalation_due_at,
        row.overall_due_at,
    ) == (past, past, past, past, past)
    assert frozen != (
        row.assignment_due_at,
        row.appointment_due_at,
        row.resolution_due_at,
        row.escalation_due_at,
        row.overall_due_at,
    )
