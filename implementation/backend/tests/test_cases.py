"""Sprint-01 slice tests: TC-001, TC-002, TC-005 + error-envelope and authz paths.

Runs against ECMP_DATABASE_URL (SQLite file by default; PostgreSQL in CI) on the
Alembic-migrated schema (see conftest.py).
"""

from __future__ import annotations

from conftest import HEADERS, NOPERM_HEADERS, READONLY_HEADERS, VALID_PAYLOAD
from sqlalchemy.orm import Session

from app.db import get_engine, reset_engine
from app.main import app
from app.models import AuditLogModel, OutboxModel


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_create_and_get_case(client):
    created = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "REGISTERED"
    assert body["customerId"] == "CUST-10001"
    assert body["customerVerified"] is False
    assert body["caseId"].startswith("CASE-")

    fetched = client.get(f"/v1/cases/{body['caseId']}", headers=HEADERS)
    assert fetched.status_code == 200
    assert fetched.json()["caseId"] == body["caseId"]


def test_create_persists_audit_and_outbox_in_one_transaction(client):
    """TC-005 (FR-001c / BR-008) + EVT-001 via outbox (ADR-009)."""
    created = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert created.status_code == 201
    case_id = created.json()["caseId"]

    with Session(get_engine()) as session:
        audits = session.query(AuditLogModel).all()
        assert len(audits) == 1
        assert audits[0].action == "case.create"
        assert audits[0].entity_type == "Case"
        assert audits[0].entity_id == case_id
        assert audits[0].actor_user_id == "cs.agent.1"
        assert audits[0].new_value["caseId"] == case_id
        assert audits[0].occurred_at is not None

        outbox = session.query(OutboxModel).all()
        assert len(outbox) == 1
        assert outbox[0].event_id == "EVT-001"
        assert outbox[0].event_name == "CaseCreated"
        assert outbox[0].payload["caseId"] == case_id
        assert outbox[0].published_at is None


def test_case_survives_engine_reset(client):
    """Persistence: data must come from the database, not SQLAlchemy/process state.

    (True process-restart coverage belongs to SIT; here we drop the cached
    engine + all pooled connections and re-read from disk.)
    """
    created = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    case_id = created.json()["caseId"]

    reset_engine()
    from fastapi.testclient import TestClient

    fresh_client = TestClient(app)
    fetched = fresh_client.get(f"/v1/cases/{case_id}", headers=HEADERS)
    assert fetched.status_code == 200


def test_create_missing_token_401_with_error_envelope(client):
    res = client.post("/v1/cases", json=VALID_PAYLOAD)
    assert res.status_code == 401
    body = res.json()
    assert body["code"] == "UNAUTHENTICATED"
    assert "message" in body


def test_create_invalid_token_401(client):
    res = client.post(
        "/v1/cases", json=VALID_PAYLOAD, headers={"Authorization": "Bearer wrong-token"}
    )
    assert res.status_code == 401
    assert res.json()["code"] == "UNAUTHENTICATED"


def test_create_without_permission_403(client):
    """Valid token but principal lacks cases:create."""
    res = client.post("/v1/cases", json=VALID_PAYLOAD, headers=READONLY_HEADERS)
    assert res.status_code == 403
    body = res.json()
    assert body["code"] == "FORBIDDEN"
    assert "cases:create" in body["message"]


def test_get_missing_token_401(client):
    res = client.get("/v1/cases/CASE-0000000000")
    assert res.status_code == 401
    assert res.json()["code"] == "UNAUTHENTICATED"


def test_get_without_permission_403(client):
    """Permissionless principal: the documented GET 403 is producible (spec line coverage)."""
    created = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    case_id = created.json()["caseId"]
    res = client.get(f"/v1/cases/{case_id}", headers=NOPERM_HEADERS)
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"


def test_readonly_principal_can_read(client):
    created = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    case_id = created.json()["caseId"]
    res = client.get(f"/v1/cases/{case_id}", headers=READONLY_HEADERS)
    assert res.status_code == 200


def test_create_invalid_enum_400_with_details(client):
    payload = dict(VALID_PAYLOAD, caseType="INVALID_TYPE")
    res = client.post("/v1/cases", json=payload, headers=HEADERS)
    assert res.status_code == 400
    body = res.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "caseType" in body["details"]


def test_create_missing_mandatory_field_400(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "customerId"}
    res = client.post("/v1/cases", json=payload, headers=HEADERS)
    assert res.status_code == 400
    assert res.json()["code"] == "VALIDATION_ERROR"


def test_create_boundary_violations_400(client):
    """Boundary negatives per FRD §7 / Threat Model pentest scope."""
    boundary_payloads = {
        "subject_too_long": dict(VALID_PAYLOAD, subject="x" * 201),
        "subject_empty": dict(VALID_PAYLOAD, subject=""),
        "description_too_long": dict(VALID_PAYLOAD, description="x" * 5001),
        "customer_id_too_long": dict(VALID_PAYLOAD, customerId="C" * 65),
        "customer_id_empty": dict(VALID_PAYLOAD, customerId=""),
        "channel_too_long": dict(VALID_PAYLOAD, channel="x" * 33),
    }
    for label, payload in boundary_payloads.items():
        res = client.post("/v1/cases", json=payload, headers=HEADERS)
        assert res.status_code == 400, f"{label}: expected 400, got {res.status_code}"
        assert res.json()["code"] == "VALIDATION_ERROR", label


def test_get_not_found_404_with_error_envelope(client):
    res = client.get("/v1/cases/CASE-NOT-FOUND", headers=HEADERS)
    assert res.status_code == 404
    body = res.json()
    assert body["code"] == "NOT_FOUND"


def test_dev_events_endpoint_gated_and_working(client):
    client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    res = client.get("/_dev/events", headers=HEADERS)
    assert res.status_code == 200
    events = res.json()["events"]
    assert len(events) == 1
    assert events[0]["id"] == "EVT-001"
    assert events[0]["publishedAt"] is None


def test_dev_outbox_drain_marks_published(client):
    """ADR-009 §2: the in-process DEV publisher drains pending outbox rows."""
    client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    res = client.post("/_dev/outbox/drain", headers=HEADERS)
    assert res.status_code == 200
    assert res.json()["count"] == 1

    events = client.get("/_dev/events", headers=HEADERS).json()["events"]
    assert events[0]["publishedAt"] is not None

    # Idempotent: nothing left to drain.
    res2 = client.post("/_dev/outbox/drain", headers=HEADERS)
    assert res2.json()["count"] == 0
