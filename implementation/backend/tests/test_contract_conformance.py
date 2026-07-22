"""Implementation-vs-spec conformance: runtime must match the frozen catalog.

Sprint-03A (governance sync, DEC-006 D6/U-6): case-service.v1.yaml v1.4.0 is now
the single normative OpenAPI spec for the ECMP Case Service — it covers
API-001/002 (Sprint-01) and API-003/004 (Sprint-02B). The formerly separate
case-actions.v1.yaml is superseded (x-status: superseded, empty paths) and is
no longer read here. This file changes only which spec is loaded; the
assertions themselves are unchanged, so this sprint verifies zero behavior
drift rather than introducing new checks.
"""

from __future__ import annotations

import re

import pytest
import yaml
from conftest import REPO_ROOT

from app.main import app

CASE_SERVICE_PATH = REPO_ROOT / "07 API Catalog" / "openapi" / "case-service.v1.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


@pytest.fixture(scope="module")
def case_service() -> dict:
    return yaml.safe_load(CASE_SERVICE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def runtime() -> dict:
    return app.openapi()


def _normalize(path: str) -> str:
    """Param names differ (caseId vs case_id); compare structure only."""
    return re.sub(r"\{[^}]+\}", "{}", path)


def _catalog_operations(catalog: dict) -> dict[tuple[str, str], dict]:
    """Catalog paths are relative to the /v1 server (except /health at root)."""
    ops = {}
    for path, item in catalog["paths"].items():
        full = path if path == "/health" else f"/v1{path}"
        for method, op in item.items():
            if method in HTTP_METHODS:
                ops[(_normalize(full), method)] = op
    return ops


def _runtime_operations(runtime: dict) -> dict[tuple[str, str], dict]:
    return {
        (_normalize(path), method): op
        for path, item in runtime["paths"].items()
        if not path.startswith("/_dev")
        for method, op in item.items()
        if method in HTTP_METHODS
    }


def test_every_catalog_operation_is_implemented(case_service, runtime):
    catalog_ops = _catalog_operations(case_service)
    missing = set(catalog_ops) - set(_runtime_operations(runtime))
    assert not missing, f"In catalog but not implemented: {missing}"


def test_no_uncataloged_product_endpoints(case_service, runtime):
    """Catalog-first rule (TS-001 §2): only /_dev/-flagged endpoints are exempt."""
    catalog_ops = _catalog_operations(case_service)
    extra = set(_runtime_operations(runtime)) - set(catalog_ops)
    assert not extra, f"Implemented but not in catalog: {extra}"


def test_response_codes_match(case_service, runtime):
    catalog_ops = _catalog_operations(case_service)
    runtime_ops = _runtime_operations(runtime)
    for key, cat_op in catalog_ops.items():
        cat_codes = set(cat_op["responses"].keys())
        run_codes = set(runtime_ops[key]["responses"].keys())
        assert cat_codes == run_codes, (
            f"{key}: catalog {sorted(cat_codes)} != app {sorted(run_codes)}"
        )


def test_create_request_constraints_match(case_service, runtime):
    cat = case_service["components"]["schemas"]["CaseCreateRequest"]
    run = runtime["components"]["schemas"]["CaseCreateRequest"]

    assert set(cat["required"]) == set(run["required"])
    assert set(cat["properties"]) == set(run["properties"])

    for field, limit_key in [
        ("customerId", "maxLength"),
        ("subject", "maxLength"),
        ("description", "maxLength"),
    ]:
        assert cat["properties"][field][limit_key] == run["properties"][field][limit_key], field

    # channel: nullable in catalog (3.0 style) → anyOf in runtime (3.1 style); compare maxLength.
    cat_channel_max = cat["properties"]["channel"]["maxLength"]
    run_channel = run["properties"]["channel"]
    run_max = run_channel.get("maxLength") or next(
        v.get("maxLength") for v in run_channel.get("anyOf", []) if v.get("maxLength")
    )
    assert cat_channel_max == run_max


def test_enums_match(case_service, runtime):
    # CaseType/Priority/CaseStatus all now live in the single consolidated spec.
    case_props = runtime["components"]["schemas"]["Case"]["properties"]
    for name, field in [
        ("CaseType", "caseType"),
        ("Priority", "priority"),
        ("CaseStatus", "status"),
    ]:
        cat_enum = set(case_service["components"]["schemas"][name]["enum"])
        prop = case_props[field]
        run_enum = set(prop["enum"]) if "enum" in prop else {prop["const"]}
        assert cat_enum == run_enum, name


def test_case_response_fields_match(case_service, runtime):
    """Runtime Case matches the catalog Case (assigneeId/unitId + full status)."""
    cat = case_service["components"]["schemas"]["Case"]
    run = runtime["components"]["schemas"]["Case"]
    assert set(cat["properties"]) == set(run["properties"])
    assert "updated_by" not in run["properties"]


def test_assign_and_status_request_schemas(case_service, runtime):
    for name in ("AssignRequest", "StatusChangeRequest"):
        cat = case_service["components"]["schemas"][name]
        run = runtime["components"]["schemas"][name]
        assert set(cat["required"]) == set(run["required"]), name
        assert set(cat["properties"]) == set(run["properties"]), name


def test_runtime_does_not_advertise_422(runtime):
    """Validation failures are 400 with the envelope (FRD §10) — never 422."""
    for path, item in runtime["paths"].items():
        for method, op in item.items():
            if method in HTTP_METHODS:
                assert "422" not in op.get("responses", {}), f"{method.upper()} {path}"
    assert "HTTPValidationError" not in runtime.get("components", {}).get("schemas", {})
