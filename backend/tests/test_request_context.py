"""Core Request Context tests (CAPABILITY-002).

Unit · Provider · Missing headers · Generated ids · Dependency injection.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.request_context import (
    HEADER_BRANCH_ID,
    HEADER_CORRELATION_ID,
    HEADER_ORGANIZATION_ID,
    HEADER_REQUEST_ID,
    HEADER_USER_ID,
    RequestContext,
    RequestContextFactory,
    get_request_context,
)


def test_context_factory_builds_immutable_context() -> None:
    factory = RequestContextFactory()
    org = uuid4()
    branch = uuid4()
    user = uuid4()
    ctx = factory.create(
        request_id="req-1",
        correlation_id="corr-1",
        organization_id=org,
        branch_id=branch,
        user_id=user,
        roles=("AGENT",),
        permissions=("queues:read",),
        locale="en-US",
        timezone="UTC",
    )
    assert isinstance(ctx, RequestContext)
    assert ctx.request_id == "req-1"
    assert ctx.correlation_id == "corr-1"
    assert ctx.organization_id == org
    assert ctx.branch_id == branch
    assert ctx.user_id == user
    assert ctx.roles == frozenset({"AGENT"})
    assert ctx.permissions == frozenset({"queues:read"})
    assert ctx.locale == "en-US"
    assert ctx.timezone == "UTC"
    try:
        ctx.request_id = "mutated"  # type: ignore[misc]
        raised = False
    except Exception:
        raised = True
    assert raised


def test_context_factory_generates_ids_when_omitted() -> None:
    factory = RequestContextFactory()
    ctx = factory.create()
    assert ctx.request_id
    assert ctx.correlation_id
    assert ctx.organization_id is None
    assert ctx.branch_id is None
    assert ctx.user_id is None
    assert ctx.roles == frozenset()
    assert ctx.permissions == frozenset()


def test_fastapi_provider_reads_headers() -> None:
    org = uuid4()
    branch = uuid4()
    user = uuid4()
    ctx = get_request_context(
        x_request_id="hdr-req",
        x_correlation_id="hdr-corr",
        x_organization_id=org,
        x_branch_id=branch,
        x_user_id=user,
        x_locale="id-ID",
        x_timezone="Asia/Jakarta",
    )
    assert ctx.request_id == "hdr-req"
    assert ctx.correlation_id == "hdr-corr"
    assert ctx.organization_id == org
    assert ctx.branch_id == branch
    assert ctx.user_id == user
    assert ctx.locale == "id-ID"
    assert ctx.timezone == "Asia/Jakarta"


def test_missing_headers_yield_none_without_raising() -> None:
    ctx = get_request_context()
    assert ctx.organization_id is None
    assert ctx.branch_id is None
    assert ctx.user_id is None
    assert ctx.locale is None
    assert ctx.timezone is None
    assert ctx.roles == frozenset()
    assert ctx.permissions == frozenset()


def test_generated_request_id_when_header_absent() -> None:
    ctx = get_request_context(x_correlation_id="fixed-corr")
    assert ctx.request_id
    assert ctx.request_id != "fixed-corr"
    assert ctx.correlation_id == "fixed-corr"
    UUID(ctx.request_id)  # valid UUID string


def test_generated_correlation_id_when_header_absent() -> None:
    ctx = get_request_context(x_request_id="fixed-req")
    assert ctx.correlation_id
    assert ctx.correlation_id != "fixed-req"
    assert ctx.request_id == "fixed-req"
    UUID(ctx.correlation_id)


def test_dependency_injection_via_fastapi() -> None:
    app = FastAPI()

    @app.get("/probe")
    async def probe(
        ctx: Annotated[RequestContext, Depends(get_request_context)],
    ) -> dict[str, str | None]:
        return {
            "request_id": ctx.request_id,
            "correlation_id": ctx.correlation_id,
            "organization_id": (
                str(ctx.organization_id) if ctx.organization_id else None
            ),
            "branch_id": str(ctx.branch_id) if ctx.branch_id else None,
            "user_id": str(ctx.user_id) if ctx.user_id else None,
        }

    org = uuid4()
    branch = uuid4()
    user = uuid4()
    with TestClient(app) as client:
        bare = client.get("/probe")
        assert bare.status_code == 200
        bare_body = bare.json()
        assert bare_body["request_id"]
        assert bare_body["correlation_id"]
        assert bare_body["organization_id"] is None

        headed = client.get(
            "/probe",
            headers={
                HEADER_REQUEST_ID: "di-req",
                HEADER_CORRELATION_ID: "di-corr",
                HEADER_ORGANIZATION_ID: str(org),
                HEADER_BRANCH_ID: str(branch),
                HEADER_USER_ID: str(user),
            },
        )
        assert headed.status_code == 200
        body = headed.json()
        assert body["request_id"] == "di-req"
        assert body["correlation_id"] == "di-corr"
        assert body["organization_id"] == str(org)
        assert body["branch_id"] == str(branch)
        assert body["user_id"] == str(user)


def test_domain_module_has_no_fastapi_import() -> None:
    from pathlib import Path

    domain_file = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "core"
        / "request_context"
        / "domain"
        / "request_context.py"
    )
    source = domain_file.read_text(encoding="utf-8")
    assert "import fastapi" not in source
    assert "from fastapi" not in source
    assert "Header(" not in source


def test_application_factory_has_no_fastapi_import() -> None:
    from pathlib import Path

    factory_file = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "core"
        / "request_context"
        / "application"
        / "context_factory.py"
    )
    source = factory_file.read_text(encoding="utf-8")
    assert "import fastapi" not in source
    assert "from fastapi" not in source
    assert "Header(" not in source
