"""TC-040 — Dashboard queue view scoped by role/org (API-040 / CAP-007).

Contract: 07 API Catalog/openapi/dashboard-queues.v1.yaml 1.0.0 (B2-13).
Decision: DEC-CAP007-BQ-001.
"""

from __future__ import annotations

from conftest import (
    FOREIGN_SUPERVISOR_HEADERS,
    HEADERS,
    NOPERM_HEADERS,
    SUPERVISOR_HEADERS,
    VALID_PAYLOAD,
)


def _create_assigned(client, *, unit_id: str = "UNIT-01", headers=None):
    created = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert created.status_code == 201
    case_id = created.json()["caseId"]
    assign_headers = headers or SUPERVISOR_HEADERS
    assigned = client.post(
        f"/v1/cases/{case_id}/assign",
        json={"assigneeId": "USR-2001", "unitId": unit_id},
        headers=assign_headers,
    )
    assert assigned.status_code == 200
    return assigned.json()


def test_dashboard_queues_requires_auth(client):
    res = client.get("/v1/dashboard/queues")
    assert res.status_code == 401
    body = res.json()
    assert body["code"] == "UNAUTHENTICATED"


def test_dashboard_queues_forbidden_without_permission(client):
    """TC-040 step 4 — missing dashboard:read → 403 FORBIDDEN."""
    res = client.get("/v1/dashboard/queues", headers=NOPERM_HEADERS)
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"

    # Agent token has cases:create/read but not dashboard:read
    res2 = client.get("/v1/dashboard/queues", headers=HEADERS)
    assert res2.status_code == 403
    assert res2.json()["code"] == "FORBIDDEN"


def test_dashboard_queues_supervisor_unit_scoped(client):
    """TC-040 step 1 — Supervisor unit U sees only unit U; asOf present."""
    _create_assigned(client, unit_id="UNIT-01")
    _create_assigned(client, unit_id="UNIT-01")

    # Seed a case in another unit via foreign supervisor
    other = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    other_id = other.json()["caseId"]
    client.post(
        f"/v1/cases/{other_id}/assign",
        json={"assigneeId": "USR-9901", "unitId": "UNIT-99"},
        headers=FOREIGN_SUPERVISOR_HEADERS,
    )

    res = client.get("/v1/dashboard/queues", headers=SUPERVISOR_HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert "asOf" in body
    assert "queues" in body
    assert "data" not in body  # normative unwrapped response

    for entry in body["queues"]:
        assert entry["unitId"] == "UNIT-01"
        assert entry["status"] in {
            "REGISTERED",
            "ASSIGNED",
            "IN_PROGRESS",
            "PENDING_REVIEW",
            "CLOSED",
            "REOPENED",
        }
        assert entry["count"] >= 1
        assert "oldestCreatedAt" in entry

    assigned_bucket = next(
        (q for q in body["queues"] if q["status"] == "ASSIGNED"), None
    )
    assert assigned_bucket is not None
    assert assigned_bucket["count"] == 2


def test_dashboard_queues_foreign_supervisor_sees_other_unit(client):
    """TC-040 step 2 — different supervisor scope → different aggregates."""
    _create_assigned(client, unit_id="UNIT-01")
    other = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    other_id = other.json()["caseId"]
    client.post(
        f"/v1/cases/{other_id}/assign",
        json={"assigneeId": "USR-9901", "unitId": "UNIT-99"},
        headers=FOREIGN_SUPERVISOR_HEADERS,
    )

    mine = client.get("/v1/dashboard/queues", headers=SUPERVISOR_HEADERS).json()
    theirs = client.get(
        "/v1/dashboard/queues", headers=FOREIGN_SUPERVISOR_HEADERS
    ).json()

    assert all(q["unitId"] == "UNIT-01" for q in mine["queues"])
    assert all(q["unitId"] == "UNIT-99" for q in theirs["queues"])
    assert mine["queues"] != theirs["queues"] or (
        sum(q["count"] for q in mine["queues"])
        != sum(q["count"] for q in theirs["queues"])
    )


def test_dashboard_queues_reconciles_with_case_list(client):
    """TC-040 step 2 — aggregate count reconciles with API-005 filter."""
    _create_assigned(client, unit_id="UNIT-01")
    _create_assigned(client, unit_id="UNIT-01")

    dash = client.get("/v1/dashboard/queues", headers=SUPERVISOR_HEADERS).json()
    assigned = next(q for q in dash["queues"] if q["status"] == "ASSIGNED")

    listed = client.get(
        "/v1/cases",
        params={"status": "ASSIGNED", "page": 1, "pageSize": 100},
        headers=SUPERVISOR_HEADERS,
    ).json()
    unit_01 = [c for c in listed["items"] if c.get("unitId") == "UNIT-01"]
    assert assigned["count"] == len(unit_01)


def test_dashboard_queues_excludes_unassigned_registered(client):
    """REGISTERED cases without unitId are not in unit buckets."""
    created = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert created.status_code == 201
    assert created.json()["unitId"] is None

    res = client.get("/v1/dashboard/queues", headers=SUPERVISOR_HEADERS)
    assert res.status_code == 200
    assert res.json()["queues"] == []


def test_dashboard_queues_is_get_only(client):
    """TC-040 step 3 / BR-DASH-03 — no mutation via dashboard contract."""
    assert client.post("/v1/dashboard/queues", headers=SUPERVISOR_HEADERS).status_code == 405
    assert client.put("/v1/dashboard/queues", headers=SUPERVISOR_HEADERS).status_code == 405
    assert client.delete("/v1/dashboard/queues", headers=SUPERVISOR_HEADERS).status_code == 405
