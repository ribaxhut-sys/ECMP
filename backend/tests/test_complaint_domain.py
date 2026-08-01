"""Complaint Domain Foundation tests (CAPABILITY-004)."""

from __future__ import annotations

import ast
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.modules.complaint import Complaint, ComplaintPriority, ComplaintStatus
from app.modules.complaint.domain.lifecycle import (
    assert_transition,
    can_transition,
)


def _id() -> uuid.UUID:
    return uuid.uuid4()


def _complaint(**overrides: object) -> Complaint:
    now = datetime(2026, 7, 24, 10, 0, 0, tzinfo=timezone.utc)
    data: dict[str, object] = {
        "complaint_id": _id(),
        "organization_id": _id(),
        "branch_id": _id(),
        "queue_ticket_id": _id(),
        "category": "Billing",
        "title": "Invoice mismatch",
        "description": "Customer disputes last invoice",
        "priority": ComplaintPriority.NORMAL,
        "status": ComplaintStatus.OPEN,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return Complaint(**data)  # type: ignore[arg-type]


def test_complaint_pass() -> None:
    c = _complaint()
    assert c.status is ComplaintStatus.OPEN
    assert c.priority is ComplaintPriority.NORMAL
    data = c.as_dict()
    assert data["title"] == "Invoice mismatch"
    assert data["status"] == "OPEN"
    assert "queueTicketId" in data


def test_complaint_rejects_blank_title() -> None:
    with pytest.raises(ValueError, match="title"):
        _complaint(title="  ")


def test_complaint_rejects_blank_description() -> None:
    with pytest.raises(ValueError, match="description"):
        _complaint(description="")


def test_complaint_rejects_invalid_priority_type() -> None:
    with pytest.raises(TypeError, match="ComplaintPriority"):
        _complaint(priority="NORMAL")  # type: ignore[arg-type]


def test_complaint_rejects_invalid_status_type() -> None:
    with pytest.raises(TypeError, match="ComplaintStatus"):
        _complaint(status="OPEN")  # type: ignore[arg-type]


def test_naive_datetime_normalized_to_utc() -> None:
    c = _complaint(
        created_at=datetime(2026, 7, 24, 12, 0, 0),
        updated_at=datetime(2026, 7, 24, 12, 0, 0),
    )
    assert c.created_at.tzinfo == timezone.utc
    assert c.updated_at.tzinfo == timezone.utc


def test_lifecycle_happy_path() -> None:
    assert can_transition(ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS)
    assert can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED)
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED)
    assert_transition(ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS)


def test_lifecycle_forbids_open_to_closed() -> None:
    assert not can_transition(ComplaintStatus.OPEN, ComplaintStatus.CLOSED)
    from app.modules.complaint.domain.errors import ComplaintDomainError

    with pytest.raises(ComplaintDomainError, match="transisi status pengaduan tidak valid"):
        assert_transition(ComplaintStatus.OPEN, ComplaintStatus.CLOSED)


def test_lifecycle_forbids_open_to_resolved() -> None:
    from app.modules.complaint.domain.errors import ComplaintDomainError

    with pytest.raises(ComplaintDomainError, match="OPEN → RESOLVED"):
        assert_transition(ComplaintStatus.OPEN, ComplaintStatus.RESOLVED)


def test_lifecycle_closed_is_terminal() -> None:
    from app.modules.complaint.domain.errors import ComplaintDomainError

    assert not can_transition(ComplaintStatus.CLOSED, ComplaintStatus.OPEN)
    with pytest.raises(ComplaintDomainError, match="CLOSED"):
        assert_transition(ComplaintStatus.CLOSED, ComplaintStatus.IN_PROGRESS)


def test_lifecycle_allows_reopen() -> None:
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.IN_PROGRESS)
    assert_transition(ComplaintStatus.RESOLVED, ComplaintStatus.IN_PROGRESS)


def test_package_exports_domain_only() -> None:
    import app.modules.complaint as pkg

    assert set(pkg.__all__) == {
        "Complaint",
        "ComplaintPriority",
        "ComplaintSLA",
        "ComplaintStatus",
        "Resolution",
        "SLAPolicy",
    }


def test_domain_has_no_sqlalchemy_or_fastapi_imports() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "complaint"
    forbidden = ("sqlalchemy", "fastapi", "app.modules.queue")
    for path in (root / "domain").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for bad in forbidden:
                        assert bad not in alias.name, f"{path}: imports {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                for bad in forbidden:
                    assert bad not in node.module, f"{path}: imports {node.module}"


def test_domain_has_no_queue_model_import() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "complaint"
    for path in root.rglob("*.py"):
        if "tests" in path.parts or "documentation" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        assert "app.modules.queue" not in source, f"Queue coupling in {path}"


def test_start_resolve_close_reopen_on_aggregate() -> None:
    from app.modules.complaint.domain.errors import ComplaintDomainError
    from app.modules.complaint.domain.models import Resolution

    c = _complaint()
    started = c.start_processing()
    assert started.status is ComplaintStatus.IN_PROGRESS

    resolved = started.resolve("Fixed billing", "agent-1")
    assert resolved.status is ComplaintStatus.RESOLVED
    assert isinstance(resolved.resolution, Resolution)
    assert resolved.resolution.summary == "Fixed billing"
    assert resolved.resolution.resolved_by == "agent-1"

    closed = resolved.close()
    assert closed.status is ComplaintStatus.CLOSED
    assert closed.resolution is not None
    with pytest.raises(ComplaintDomainError) as imm:
        closed.assert_resolution_mutable()
    assert imm.value.code == "RESOLUTION_IMMUTABLE"

    # reopen only from RESOLVED
    with pytest.raises(ComplaintDomainError, match="reopen memerlukan status RESOLVED"):
        closed.reopen()

    reopened = resolved.reopen(reason="customer disputed")
    assert reopened.status is ComplaintStatus.IN_PROGRESS
    assert reopened.resolution is None


def test_invalid_aggregate_transitions() -> None:
    from app.modules.complaint.domain.errors import ComplaintDomainError

    open_c = _complaint()
    with pytest.raises(ComplaintDomainError, match="OPEN → RESOLVED"):
        open_c.resolve("x", "y")
    with pytest.raises(ComplaintDomainError, match="OPEN → CLOSED"):
        open_c.close()

    in_progress = open_c.start_processing()
    with pytest.raises(ComplaintDomainError, match="IN_PROGRESS → CLOSED"):
        in_progress.close()
