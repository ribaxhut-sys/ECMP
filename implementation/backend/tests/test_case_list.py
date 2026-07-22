"""TC-006 (FR-005 / API-005): list cases, paginated and filtered.

Sort is fixed createdAt descending (CTO decision, Sprint-03B design review) —
no sortBy/sortDir parameter exists in the contract.
"""

from __future__ import annotations

from conftest import ASSIGN_PAYLOAD, HEADERS, NOPERM_HEADERS, SUPERVISOR_HEADERS, VALID_PAYLOAD


def _create_case(client, **overrides):
    payload = {**VALID_PAYLOAD, **overrides}
    res = client.post("/v1/cases", json=payload, headers=HEADERS)
    assert res.status_code == 201
    return res.json()


def test_list_default_pagination_returns_created_cases(client):
    created = [_create_case(client) for _ in range(3)]
    created_ids = {c["caseId"] for c in created}

    res = client.get("/v1/cases", headers=HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert body["page"] == 1
    assert body["pageSize"] == 20
    assert body["totalItems"] >= 3
    returned_ids = {item["caseId"] for item in body["items"]}
    assert created_ids.issubset(returned_ids)


def test_list_sorted_by_created_at_descending(client):
    first = _create_case(client, subject="First case")
    second = _create_case(client, subject="Second case")

    res = client.get("/v1/cases?pageSize=100", headers=HEADERS)
    assert res.status_code == 200
    ids_in_order = [item["caseId"] for item in res.json()["items"]]
    assert ids_in_order.index(second["caseId"]) < ids_in_order.index(first["caseId"])


def test_list_filter_by_status(client):
    registered = _create_case(client, subject="Stays registered")
    to_assign = _create_case(client, subject="Will be assigned")
    assign_res = client.post(
        f"/v1/cases/{to_assign['caseId']}/assign",
        json=ASSIGN_PAYLOAD,
        headers=SUPERVISOR_HEADERS,
    )
    assert assign_res.status_code == 200

    res = client.get("/v1/cases?status=ASSIGNED&pageSize=100", headers=HEADERS)
    assert res.status_code == 200
    returned_ids = {item["caseId"] for item in res.json()["items"]}
    assert to_assign["caseId"] in returned_ids
    assert registered["caseId"] not in returned_ids


def test_list_filter_by_priority_and_case_type_combined(client):
    match = _create_case(client, priority="CRITICAL", caseType="INQUIRY", subject="Matches both")
    no_match_priority = _create_case(
        client, priority="LOW", caseType="INQUIRY", subject="Wrong priority"
    )
    no_match_type = _create_case(
        client, priority="CRITICAL", caseType="COMPLAINT", subject="Wrong type"
    )

    res = client.get(
        "/v1/cases?priority=CRITICAL&caseType=INQUIRY&pageSize=100", headers=HEADERS
    )
    assert res.status_code == 200
    returned_ids = {item["caseId"] for item in res.json()["items"]}
    assert match["caseId"] in returned_ids
    assert no_match_priority["caseId"] not in returned_ids
    assert no_match_type["caseId"] not in returned_ids


def test_list_filter_by_assignee_id(client):
    target = _create_case(client, subject="Assigned to USR-2001")
    other = _create_case(client, subject="Not assigned")
    assign_res = client.post(
        f"/v1/cases/{target['caseId']}/assign",
        json=ASSIGN_PAYLOAD,
        headers=SUPERVISOR_HEADERS,
    )
    assert assign_res.status_code == 200

    res = client.get(f"/v1/cases?assigneeId={ASSIGN_PAYLOAD['assigneeId']}", headers=HEADERS)
    assert res.status_code == 200
    returned_ids = {item["caseId"] for item in res.json()["items"]}
    assert target["caseId"] in returned_ids
    assert other["caseId"] not in returned_ids


def test_list_filter_no_match_returns_empty_items_not_error(client):
    _create_case(client)
    res = client.get("/v1/cases?assigneeId=USR-DOES-NOT-EXIST", headers=HEADERS)
    assert res.status_code == 200
    assert res.json()["items"] == []


def test_list_page_beyond_last_returns_empty_with_correct_total(client):
    _create_case(client)
    res = client.get("/v1/cases?page=999&pageSize=20", headers=HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert body["items"] == []
    assert body["totalItems"] >= 1


def test_list_page_size_over_100_returns_400_validation_error(client):
    res = client.get("/v1/cases?pageSize=101", headers=HEADERS)
    assert res.status_code == 400
    assert res.json()["code"] == "VALIDATION_ERROR"


def test_list_missing_token_401(client):
    res = client.get("/v1/cases")
    assert res.status_code == 401
    assert res.json()["code"] == "UNAUTHENTICATED"


def test_list_without_permission_403(client):
    res = client.get("/v1/cases", headers=NOPERM_HEADERS)
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"
