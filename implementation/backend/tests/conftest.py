"""Shared test setup.

Environment is configured here (not at module import in test files) so the suite
is order-independent. The schema is created by `alembic upgrade head` — tests run
against the migrated (authoritative) schema, never ORM create_all, so model vs
migration drift fails the suite.
"""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parents[1]

os.environ.setdefault(
    "ECMP_DATABASE_URL", f"sqlite:///{(BACKEND_DIR / 'ecmp_test.db').as_posix()}"
)
os.environ["ECMP_ENABLE_DEV_ENDPOINTS"] = "true"

import pytest  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import delete  # noqa: E402

from alembic import command  # noqa: E402
from app.db import get_engine, reset_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    AuditLogModel,
    CaseModel,
    CaseNoteModel,
    NotificationLogModel,
    OutboxModel,
)

HEADERS = {"Authorization": "Bearer dev-token"}
READONLY_HEADERS = {"Authorization": "Bearer dev-readonly-token"}
NOPERM_HEADERS = {"Authorization": "Bearer dev-noperm-token"}
SUPERVISOR_HEADERS = {"Authorization": "Bearer dev-supervisor-token"}
HANDLER_HEADERS = {"Authorization": "Bearer dev-handler-token"}
FOREIGN_SUPERVISOR_HEADERS = {"Authorization": "Bearer dev-foreign-supervisor-token"}

VALID_PAYLOAD = {
    "customerId": "CUST-10001",
    "caseType": "COMPLAINT",
    "priority": "HIGH",
    "subject": "Billing discrepancy",
    "description": "Incorrect charge on invoice",
    "channel": "CALL",
}

ASSIGN_PAYLOAD = {"assigneeId": "USR-2001", "unitId": "UNIT-01"}



def alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return cfg


@pytest.fixture(scope="session", autouse=True)
def migrated_schema():
    reset_engine()
    engine = get_engine()
    # Clean slate (incl. alembic_version) then build the schema from migrations.
    from app.db import Base

    Base.metadata.drop_all(engine)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    command.upgrade(alembic_config(), "head")
    yield


@pytest.fixture(autouse=True)
def clean_tables(migrated_schema):
    engine = get_engine()
    with engine.begin() as conn:
        for table in (
            CaseNoteModel.__table__,
            NotificationLogModel.__table__,
            OutboxModel.__table__,
            AuditLogModel.__table__,
            CaseModel.__table__,
        ):
            conn.execute(delete(table))
    yield


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def tolerant_client() -> TestClient:
    """Client that returns 500 responses instead of re-raising server exceptions."""
    return TestClient(app, raise_server_exceptions=False)
