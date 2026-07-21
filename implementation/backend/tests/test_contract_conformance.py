"""Implementation-vs-spec conformance: the running app must match the catalog.

CI previously only validated spec *syntax*; this suite catches drift between
`07 API Catalog/openapi/case-service.v1.yaml` and the FastAPI runtime schema
(paths, response codes, field constraints, enums).
"""

from __future__ import annotations

import re

import pytest
import yaml
from conftest import REPO_ROOT

from app.main import app

CATALOG_PATH = REPO_ROOT / "07 API Catalog" / "openapi" / "case-service.v1.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


@pytest.fixture(scope="module")
def catalog() -> dict:
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


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


def test_every_catalog_operation_is_implemented(catalog, runtime):
    missing = set(_catalog_operations(catalog)) - set(_runtime_operations(runtime))
    assert not missing, f"In catalog but not implemented: {missing}"


def test_no_uncataloged_product_endpoints(catalog, runtime):
    """Catalog-first rule (TS-001 §2): only /_dev/-flagged endpoints are exempt."""
    extra = set(_runtime_operations(runtime)) - set(_catalog_operations(catalog))
    assert not extra, f"Implemented but not in catalog: {extra}"


def test_response_codes_match(catalog, runtime):
    catalog_ops = _catalog_operations(catalog)
    runtime_ops = _runtime_operations(runtime)
    for key, cat_op in catalog_ops.items():
        cat_codes = set(cat_op["responses"].keys())
        run_codes = set(runtime_ops[key]["responses"].keys())
        assert cat_codes == run_codes, (
            f"{key}: catalog {sorted(cat_codes)} != app {sorted(run_codes)}"
        )


def test_create_request_constraints_match(catalog, runtime):
    cat = catalog["components"]["schemas"]["CaseCreateRequest"]
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


def test_enums_match(catalog, runtime):
    # Pydantic inlines Literal enums into the property; compare there.
    field_by_schema = {"CaseType": "caseType", "Priority": "priority", "CaseStatus": "status"}
    case_props = runtime["components"]["schemas"]["Case"]["properties"]
    for name, field in field_by_schema.items():
        cat_enum = set(catalog["components"]["schemas"][name]["enum"])
        prop = case_props[field]
        # Single-value Literal renders as `const`, multi-value as `enum`.
        run_enum = set(prop["enum"]) if "enum" in prop else {prop["const"]}
        assert cat_enum == run_enum, name


def test_case_response_fields_match(catalog, runtime):
    cat = catalog["components"]["schemas"]["Case"]
    run = runtime["components"]["schemas"]["Case"]
    assert set(cat["properties"]) == set(run["properties"])
    assert "updated_by" not in run["properties"]


def test_runtime_does_not_advertise_422(runtime):
    """Validation failures are 400 with the envelope (FRD §10) — never 422."""
    for path, item in runtime["paths"].items():
        for method, op in item.items():
            if method in HTTP_METHODS:
                assert "422" not in op.get("responses", {}), f"{method.upper()} {path}"
    assert "HTTPValidationError" not in runtime.get("components", {}).get("schemas", {})
