"""Response-body contract tests against the running API (Sprint-10 RC1).

Unlike `test_contract_conformance.py` (catalog schema ↔ FastAPI-generated schema),
these tests issue real HTTP requests via TestClient and validate JSON response
bodies against the normative OpenAPI component schemas in case-service.v1.yaml.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
import yaml
from conftest import (
    ASSIGN_PAYLOAD,
    HANDLER_HEADERS,
    HEADERS,
    REPO_ROOT,
    SUPERVISOR_HEADERS,
    VALID_PAYLOAD,
)
from jsonschema import Draft202012Validator

CASE_SERVICE_PATH = REPO_ROOT / "07 API Catalog" / "openapi" / "case-service.v1.yaml"


@pytest.fixture(scope="module")
def catalog() -> dict:
    return yaml.safe_load(CASE_SERVICE_PATH.read_text(encoding="utf-8"))


def _resolve_schema(schema: dict[str, Any], components: dict[str, Any]) -> dict[str, Any]:
    """Inline OpenAPI $ref and convert nullable to JSON Schema type unions."""
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        return _resolve_schema(copy.deepcopy(components[name]), components)

    out = copy.deepcopy(schema)
    if out.pop("nullable", False):
        base_type = out.get("type")
        if isinstance(base_type, str):
            out["type"] = [base_type, "null"]
        elif base_type is None and "properties" in out:
            out["type"] = ["object", "null"]

    if "properties" in out:
        out["properties"] = {
            k: _resolve_schema(v, components) for k, v in out["properties"].items()
        }
    if "items" in out and isinstance(out["items"], dict):
        out["items"] = _resolve_schema(out["items"], components)
    for key in ("allOf", "anyOf", "oneOf"):
        if key in out:
            out[key] = [_resolve_schema(s, components) for s in out[key]]
    return out


def _validate(body: Any, schema_name: str, catalog: dict) -> None:
    components = catalog["components"]["schemas"]
    schema = _resolve_schema(components[schema_name], components)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(body),
        key=lambda e: list(e.path),
    )
    assert not errors, "; ".join(
        f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}" for err in errors
    )


def _create_case(client) -> str:
    res = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert res.status_code == 201
    return res.json()["caseId"]


def test_create_case_response_matches_case_schema(client, catalog):
    res = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert res.status_code == 201
    _validate(res.json(), "Case", catalog)


def test_get_case_response_matches_case_schema(client, catalog):
    case_id = _create_case(client)
    res = client.get(f"/v1/cases/{case_id}", headers=HEADERS)
    assert res.status_code == 200
    _validate(res.json(), "Case", catalog)


def test_list_cases_response_matches_case_page_schema(client, catalog):
    _create_case(client)
    res = client.get("/v1/cases", headers=HEADERS)
    assert res.status_code == 200
    _validate(res.json(), "CasePage", catalog)


def test_assign_response_matches_case_schema(client, catalog):
    case_id = _create_case(client)
    res = client.post(
        f"/v1/cases/{case_id}/assign",
        json=ASSIGN_PAYLOAD,
        headers=SUPERVISOR_HEADERS,
    )
    assert res.status_code == 200
    _validate(res.json(), "Case", catalog)


def test_status_change_response_matches_case_schema(client, catalog):
    case_id = _create_case(client)
    assign = client.post(
        f"/v1/cases/{case_id}/assign",
        json=ASSIGN_PAYLOAD,
        headers=SUPERVISOR_HEADERS,
    )
    assert assign.status_code == 200
    res = client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "IN_PROGRESS"},
        headers=HANDLER_HEADERS,
    )
    assert res.status_code == 200
    _validate(res.json(), "Case", catalog)


def test_timeline_response_matches_schema(client, catalog):
    case_id = _create_case(client)
    res = client.get(f"/v1/cases/{case_id}/timeline", headers=HEADERS)
    assert res.status_code == 200
    _validate(res.json(), "CaseTimeline", catalog)


def test_notes_list_response_matches_schema(client, catalog):
    case_id = _create_case(client)
    create = client.post(
        f"/v1/cases/{case_id}/notes",
        json={"body": "Contract-test note"},
        headers=HEADERS,
    )
    assert create.status_code == 201
    _validate(create.json(), "CaseNote", catalog)

    listing = client.get(f"/v1/cases/{case_id}/notes", headers=HEADERS)
    assert listing.status_code == 200
    _validate(listing.json(), "CaseNoteList", catalog)


def test_error_envelope_matches_error_schema(client, catalog):
    res = client.get("/v1/cases/CASE-0000000000", headers=HEADERS)
    assert res.status_code == 404
    _validate(res.json(), "Error", catalog)
