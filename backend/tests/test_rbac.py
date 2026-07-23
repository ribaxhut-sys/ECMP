"""Unit tests for role → permission mapping (no DB)."""

from app.core.rbac import permissions_for_role


def test_agent_permissions() -> None:
    perms = permissions_for_role("AGENT")
    assert "complaints:create" in perms
    assert "complaints:assign" not in perms


def test_supervisor_permissions() -> None:
    perms = permissions_for_role("SUPERVISOR")
    assert "complaints:assign" in perms
    assert "complaints:escalate" in perms
    assert "users:create" in perms


def test_unknown_role_empty() -> None:
    assert permissions_for_role("UNKNOWN") == []
    assert permissions_for_role(None) == []


def test_ho_engineer_can_complete_appointments() -> None:
    perms = permissions_for_role("HO_ENGINEER")
    assert "appointments:complete" in perms
    assert "complaints:read" in perms


def test_ho_scheduler_cannot_complete_appointments() -> None:
    perms = permissions_for_role("HO_SCHEDULER")
    assert "escalations:review" in perms
    assert "appointments:complete" not in perms


def test_admin_can_complete_appointments() -> None:
    assert "appointments:complete" in permissions_for_role("ADMIN")


def test_ho_scheduler_can_review_for_no_show() -> None:
    """API-309 write gate reuses escalations:review (HO Scheduler / Admin)."""
    assert "escalations:review" in permissions_for_role("HO_SCHEDULER")
    assert "escalations:review" in permissions_for_role("ADMIN")


def test_branch_officer_cannot_mark_no_show() -> None:
    assert "escalations:review" not in permissions_for_role("BRANCH_OFFICER")
    assert "escalations:review" not in permissions_for_role("HO_ENGINEER")
