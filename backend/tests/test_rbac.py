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
