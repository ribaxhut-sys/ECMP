"""Additional service-layer edge cases for Sprint-02B org-scope and validation."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from conftest import VALID_PAYLOAD
from sqlalchemy.orm import Session

from app import service
from app.db import get_engine
from app.errors import ForbiddenError, ValidationAppError
from app.models import CaseModel

USER = {"userId": "cs.agent.1", "permissions": {"cases:create", "cases:read"}}


def test_cross_unit_denied_when_owning_unit_not_supervised():
    """Supervisor may target UNIT-99 but cannot move a UNIT-01-owned case (BR-002)."""
    supervisor = {
        "userId": "supervisor.x",
        "permissions": {"cases:assign"},
        "orgUnitId": "UNIT-99",
        "supervisedUnitIds": {"UNIT-99"},
    }
    now = datetime.now(timezone.utc)
    with Session(get_engine()) as session:
        session.add(
            CaseModel(
                case_id="CASE-OWNUNIT01",
                customer_id="CUST-1",
                case_type="INQUIRY",
                priority="LOW",
                subject="Owned",
                description="Case already owned by UNIT-01",
                status="REGISTERED",
                channel=None,
                customer_verified=False,
                assignee_id=None,
                unit_id="UNIT-01",
                created_at=now,
                created_by="seed",
                updated_at=now,
                updated_by="seed",
            )
        )
        session.commit()
        with pytest.raises(ForbiddenError) as exc:
            service.assign_case(
                session,
                "CASE-OWNUNIT01",
                {"assigneeId": "USR-1", "unitId": "UNIT-99"},
                supervisor,
            )
        assert exc.value.code == "FORBIDDEN"


def test_change_status_resolution_code_guard_via_service():
    """Defense-in-depth when schema is bypassed (direct service call)."""
    handler = {
        "userId": "USR-2001",
        "permissions": {"cases:status"},
        "orgUnitId": "UNIT-01",
        "supervisedUnitIds": set(),
    }
    supervisor = {
        "userId": "supervisor.1",
        "permissions": {"cases:assign"},
        "orgUnitId": "UNIT-01",
        "supervisedUnitIds": {"UNIT-01"},
    }
    with Session(get_engine()) as session:
        created = service.register_case(session, dict(VALID_PAYLOAD), USER)
        case_id = created["caseId"]
        service.assign_case(
            session, case_id, {"assigneeId": "USR-2001", "unitId": "UNIT-01"}, supervisor
        )
        service.change_status(session, case_id, {"toStatus": "IN_PROGRESS"}, handler)
        service.change_status(session, case_id, {"toStatus": "PENDING_REVIEW"}, handler)
        with pytest.raises(ValidationAppError) as exc:
            service.change_status(session, case_id, {"toStatus": "CLOSED"}, handler)
        assert exc.value.code == "VALIDATION_ERROR"


def test_admin_override_requires_reason():
    admin = {
        "userId": "USR-2001",
        "permissions": {"cases:status", "admin:override"},
        "orgUnitId": "UNIT-01",
        "supervisedUnitIds": set(),
    }
    supervisor = {
        "userId": "supervisor.1",
        "permissions": {"cases:assign"},
        "orgUnitId": "UNIT-01",
        "supervisedUnitIds": {"UNIT-01"},
    }
    with Session(get_engine()) as session:
        created = service.register_case(session, dict(VALID_PAYLOAD), USER)
        case_id = created["caseId"]
        service.assign_case(
            session, case_id, {"assigneeId": "USR-2001", "unitId": "UNIT-01"}, supervisor
        )
        with pytest.raises(ValidationAppError):
            service.change_status(session, case_id, {"toStatus": "IN_PROGRESS"}, admin)
        result = service.change_status(
            session,
            case_id,
            {"toStatus": "IN_PROGRESS", "reason": "Supervisor escalated"},
            admin,
        )
        assert result["status"] == "IN_PROGRESS"
