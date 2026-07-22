"""Presentation layer (ADR-005): routes + error handlers only.

API base path /v1 per ADR-006. Error envelope per OpenAPI Error{code,message,details?}
for ALL 4xx/5xx responses (TS-001 §2.2), including unknown routes, 405, and 500.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import service, settings
from app.auth import need
from app.db import Base, get_engine, get_session
from app.errors import ApiError, NotFoundError
from app.schemas import (
    AssignRequest,
    Case,
    CaseCreateRequest,
    CasePage,
    CaseStatus,
    CaseType,
    Error,
    Priority,
    StatusChangeRequest,
)

ERROR_RESPONSES = {
    401: {"model": Error, "description": "Not authenticated"},
    403: {"model": Error, "description": "Missing permission"},
    500: {"model": Error, "description": "Internal server error"},
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.validate_runtime_config()
    if settings.database_url().startswith("sqlite"):
        # SQLite fallback only; on PostgreSQL the schema comes from Alembic —
        # create_all there would mask a missing migration (ai/08_standards.md).
        Base.metadata.create_all(get_engine())
    yield


# Interactive docs expose the runtime schema; keep them off unless dev mode is on
# (catalog-first rule, TS-001 §2 — only /_dev/-flagged surfaces are exempt).
_dev = settings.dev_endpoints_enabled()

app = FastAPI(
    title="ECMP Case Service",
    version="1.5.0",
    description=(
        "Sprint-03B: create/get + assign/status + list (FR-001/002/003/004/005) "
        "— PostgreSQL per ADR-004"
    ),
    lifespan=lifespan,
    docs_url="/_dev/docs" if _dev else None,
    redoc_url="/_dev/redoc" if _dev else None,
    openapi_url="/_dev/openapi.json" if _dev else None,
)


def _envelope(status_code: int, code: str, message: str, details: dict | None = None):
    body: dict = {"code": code, "message": message}
    if details:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(ApiError)
def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return _envelope(exc.status_code, exc.code, exc.message, exc.details)


@app.exception_handler(RequestValidationError)
def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    # FRD §10: validation failures return 400 with the Error envelope.
    details = {
        ".".join(str(p) for p in err["loc"] if p != "body"): err["msg"] for err in exc.errors()
    }
    return _envelope(400, "VALIDATION_ERROR", "Request validation failed", details)


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    # Unknown route (404) and wrong method (405) must also use the envelope.
    code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR")
    return _envelope(exc.status_code, code, str(exc.detail))


@app.exception_handler(Exception)
def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    # No exception details in the response body (10 Security standards).
    return _envelope(500, "INTERNAL_ERROR", "Internal server error")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ecmp-case-service", "sprint": "Sprint-03B"}


@app.get(
    "/v1/cases",
    response_model=CasePage,
    responses={400: {"model": Error, "description": "Validation failed"}, **ERROR_RESPONSES},
)
def list_cases(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    status: CaseStatus | None = Query(default=None),
    priority: Priority | None = Query(default=None),
    caseType: CaseType | None = Query(default=None),
    assigneeId: str | None = Query(default=None),
    user: dict = Depends(need("cases:read")),
    session: Session = Depends(get_session),
):
    return service.list_cases(
        session,
        page=page,
        page_size=pageSize,
        status=status,
        priority=priority,
        case_type=caseType,
        assignee_id=assigneeId,
    )


@app.post(
    "/v1/cases",
    response_model=Case,
    status_code=201,
    responses={400: {"model": Error, "description": "Validation failed"}, **ERROR_RESPONSES},
)
def create_case(
    payload: CaseCreateRequest,
    user: dict = Depends(need("cases:create")),
    session: Session = Depends(get_session),
):
    return service.register_case(session, payload.model_dump(), user)


@app.get(
    "/v1/cases/{case_id}",
    response_model=Case,
    responses={**ERROR_RESPONSES, 404: {"model": Error, "description": "Case not found"}},
)
def get_case(
    case_id: str,
    user: dict = Depends(need("cases:read")),
    session: Session = Depends(get_session),
):
    case = service.get_case(session, case_id)
    if case is None:
        raise NotFoundError(f"Case {case_id} not found")
    return case


@app.post(
    "/v1/cases/{case_id}/assign",
    response_model=Case,
    responses={
        400: {"model": Error, "description": "Validation failed"},
        404: {"model": Error, "description": "Case not found"},
        409: {"model": Error, "description": "Case not in an assignable status"},
        **ERROR_RESPONSES,
    },
)
def assign_case(
    case_id: str,
    payload: AssignRequest,
    user: dict = Depends(need("cases:assign")),
    session: Session = Depends(get_session),
):
    return service.assign_case(session, case_id, payload.model_dump(), user)


@app.post(
    "/v1/cases/{case_id}/status",
    response_model=Case,
    responses={
        400: {"model": Error, "description": "Validation failed"},
        404: {"model": Error, "description": "Case not found"},
        409: {"model": Error, "description": "Illegal transition"},
        **ERROR_RESPONSES,
    },
)
def change_case_status(
    case_id: str,
    payload: StatusChangeRequest,
    user: dict = Depends(need("cases:status")),
    session: Session = Depends(get_session),
):
    return service.change_status(session, case_id, payload.model_dump(), user)


if _dev:

    @app.get("/_dev/events")
    def list_events(
        user: dict = Depends(need("cases:read")),
        session: Session = Depends(get_session),
    ):
        """Dev-only outbox inspector; enabled via ECMP_ENABLE_DEV_ENDPOINTS."""
        return {"events": service.list_outbox_events(session)}

    @app.post("/_dev/outbox/drain")
    def drain_outbox(
        user: dict = Depends(need("cases:read")),
        session: Session = Depends(get_session),
    ):
        """Dev-only in-process outbox publisher (ADR-009 §2) — marks rows published."""
        published = service.drain_outbox(session)
        return {"published": published, "count": len(published)}


def custom_openapi() -> dict:
    """Runtime schema aligned to the catalog: validation errors are 400 (envelope), not 422."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = FastAPI.openapi(app)
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict):
                operation.get("responses", {}).pop("422", None)
    for name in ("HTTPValidationError", "ValidationError"):
        schema.get("components", {}).get("schemas", {}).pop(name, None)
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
