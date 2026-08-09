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


def test_manager_f4_complaint_permissions() -> None:
    """F4: Manager has create/read/update/assign/escalate/close (no wildcard)."""
    perms = permissions_for_role("MANAGER")
    for code in (
        "complaints:create",
        "complaints:read",
        "complaints:update",
        "complaints:assign",
        "complaints:escalate",
        "complaints:close",
    ):
        assert code in perms
    assert "*" not in perms


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


def test_ho_engineer_can_submit_final_resolution() -> None:
    """API-310 write gate reuses appointments:complete (HO Engineer / Admin)."""
    assert "appointments:complete" in permissions_for_role("HO_ENGINEER")
    assert "appointments:complete" in permissions_for_role("ADMIN")
    assert "appointments:complete" not in permissions_for_role("BRANCH_OFFICER")
    assert "appointments:complete" not in permissions_for_role("HO_SCHEDULER")


def test_branch_supervisor_can_close_complaint() -> None:
    """API-312 write gate: complaints:close (Branch Supervisor / Manager / Admin)."""
    assert "complaints:close" in permissions_for_role("BRANCH_SUPERVISOR")
    assert "complaints:close" in permissions_for_role("SUPERVISOR")
    assert "complaints:close" in permissions_for_role("MANAGER")
    assert "complaints:close" in permissions_for_role("ADMIN")
    assert "complaints:close" not in permissions_for_role("BRANCH_OFFICER")
    assert "complaints:close" not in permissions_for_role("HO_ENGINEER")
    assert "complaints:close" not in permissions_for_role("HO_SCHEDULER")


def test_admin_can_close_escalation() -> None:
    """API-313 write gate: escalations:close (Head Office Admin only)."""
    assert "escalations:close" in permissions_for_role("ADMIN")
    assert "escalations:close" not in permissions_for_role("BRANCH_SUPERVISOR")
    assert "escalations:close" not in permissions_for_role("HO_SCHEDULER")
    assert "escalations:close" not in permissions_for_role("HO_ENGINEER")
    assert "escalations:close" not in permissions_for_role("BRANCH_OFFICER")


def test_escalations_read_permission() -> None:
    """Read gate for escalation detail / closure UI."""
    assert "escalations:read" in permissions_for_role("BRANCH_OFFICER")
    assert "escalations:read" in permissions_for_role("BRANCH_SUPERVISOR")
    assert "escalations:read" in permissions_for_role("HO_SCHEDULER")
    assert "escalations:read" in permissions_for_role("HO_ENGINEER")
    assert "escalations:read" in permissions_for_role("ADMIN")
    assert "escalations:read" in permissions_for_role("VIEWER")


def test_admin_can_manage_sla_policies() -> None:
    """API-315–317: Admin has sla:read / sla:manage (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "sla:read" in perms
    assert "sla:manage" in perms
    assert "*" in perms


def test_viewer_can_read_sla_policies() -> None:
    perms = permissions_for_role("VIEWER")
    assert "sla:read" in perms
    assert "sla:manage" not in perms


def test_agent_cannot_manage_sla_policies() -> None:
    perms = permissions_for_role("AGENT")
    assert "sla:read" not in perms
    assert "sla:manage" not in perms


def test_roles_can_read_kpi() -> None:
    """API-318: kpi:read for agent/supervisor/viewer/admin paths."""
    assert "kpi:read" in permissions_for_role("AGENT")
    assert "kpi:read" in permissions_for_role("SUPERVISOR")
    assert "kpi:read" in permissions_for_role("VIEWER")
    assert "kpi:read" in permissions_for_role("HO_ENGINEER")
    assert "*" in permissions_for_role("ADMIN")


def test_roles_can_read_dashboard() -> None:
    """API-319: dashboard:read for agent/supervisor/viewer/admin paths."""
    assert "dashboard:read" in permissions_for_role("AGENT")
    assert "dashboard:read" in permissions_for_role("SUPERVISOR")
    assert "dashboard:read" in permissions_for_role("VIEWER")
    assert "dashboard:read" in permissions_for_role("HO_ENGINEER")
    assert "dashboard:read" in permissions_for_role("HO_SCHEDULER")
    assert "*" in permissions_for_role("ADMIN")


def test_admin_can_manage_settings() -> None:
    """API-320–322: Admin has settings:read / settings:update (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "settings:read" in perms
    assert "settings:update" in perms
    assert "*" in perms


def test_agent_cannot_manage_settings() -> None:
    perms = permissions_for_role("AGENT")
    assert "settings:read" not in perms
    assert "settings:update" not in perms


def test_viewer_cannot_manage_settings() -> None:
    perms = permissions_for_role("VIEWER")
    assert "settings:read" not in perms
    assert "settings:update" not in perms


def test_roles_can_manage_attachments() -> None:
    """API-323–326: attachment:create/read/delete for operational roles."""
    agent = permissions_for_role("AGENT")
    assert "attachment:create" in agent
    assert "attachment:read" in agent
    assert "attachment:delete" in agent

    viewer = permissions_for_role("VIEWER")
    assert "attachment:read" in viewer
    assert "attachment:create" not in viewer
    assert "attachment:delete" not in viewer

    admin = permissions_for_role("ADMIN")
    assert "*" in admin


def test_admin_can_manage_notifications() -> None:
    """API-327–335: Admin has notification:* (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "notification:read" in perms
    assert "notification:create" in perms
    assert "notification:update" in perms
    assert "notification:delete" in perms
    assert "*" in perms


def test_viewer_can_read_notifications() -> None:
    perms = permissions_for_role("VIEWER")
    assert "notification:read" in perms
    assert "notification:create" not in perms
    assert "notification:update" not in perms
    assert "notification:delete" not in perms


def test_agent_cannot_manage_notifications() -> None:
    perms = permissions_for_role("AGENT")
    assert "notification:read" not in perms
    assert "notification:create" not in perms
    assert "notification:update" not in perms
    assert "notification:delete" not in perms


def test_admin_can_read_audit() -> None:
    """API-336–337: Admin has audit:read (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "audit:read" in perms
    assert "*" in perms


def test_viewer_can_read_audit() -> None:
    perms = permissions_for_role("VIEWER")
    assert "audit:read" in perms


def test_agent_cannot_read_audit() -> None:
    perms = permissions_for_role("AGENT")
    assert "audit:read" not in perms


def test_admin_can_manage_roles() -> None:
    """API-338–342: Admin has role:* (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "role:read" in perms
    assert "role:create" in perms
    assert "role:update" in perms
    assert "role:delete" in perms
    assert "*" in perms


def test_super_admin_can_manage_roles() -> None:
    perms = permissions_for_role("SUPER_ADMIN")
    assert "role:read" in perms
    assert "role:create" in perms
    assert "*" in perms


def test_viewer_can_read_roles() -> None:
    perms = permissions_for_role("VIEWER")
    assert "role:read" in perms
    assert "role:create" not in perms
    assert "role:update" not in perms
    assert "role:delete" not in perms


def test_agent_cannot_manage_roles() -> None:
    perms = permissions_for_role("AGENT")
    assert "role:read" not in perms
    assert "role:create" not in perms
    assert "role:update" not in perms
    assert "role:delete" not in perms


def test_admin_can_manage_permissions() -> None:
    """API-343–347: Admin has permission:* (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "permission:read" in perms
    assert "permission:create" in perms
    assert "permission:update" in perms
    assert "permission:delete" in perms
    assert "*" in perms


def test_super_admin_can_manage_permissions() -> None:
    perms = permissions_for_role("SUPER_ADMIN")
    assert "permission:read" in perms
    assert "permission:create" in perms
    assert "*" in perms


def test_viewer_can_read_permissions() -> None:
    perms = permissions_for_role("VIEWER")
    assert "permission:read" in perms
    assert "permission:create" not in perms
    assert "permission:update" not in perms
    assert "permission:delete" not in perms


def test_agent_cannot_manage_permissions() -> None:
    perms = permissions_for_role("AGENT")
    assert "permission:read" not in perms
    assert "permission:create" not in perms
    assert "permission:update" not in perms
    assert "permission:delete" not in perms


def test_admin_can_manage_role_permissions() -> None:
    """API-348–350: Admin has role_permission:* (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "role_permission:read" in perms
    assert "role_permission:update" in perms
    assert "*" in perms


def test_viewer_can_read_role_permissions() -> None:
    perms = permissions_for_role("VIEWER")
    assert "role_permission:read" in perms
    assert "role_permission:update" not in perms


def test_agent_cannot_manage_role_permissions() -> None:
    perms = permissions_for_role("AGENT")
    assert "role_permission:read" not in perms
    assert "role_permission:update" not in perms


def test_admin_can_manage_user_roles() -> None:
    """API-351–353: Admin has user_role:* (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "user_role:read" in perms
    assert "user_role:update" in perms
    assert "*" in perms


def test_viewer_can_read_user_roles() -> None:
    perms = permissions_for_role("VIEWER")
    assert "user_role:read" in perms
    assert "user_role:update" not in perms


def test_agent_cannot_manage_user_roles() -> None:
    perms = permissions_for_role("AGENT")
    assert "user_role:read" not in perms
    assert "user_role:update" not in perms


def test_admin_can_manage_data_scopes() -> None:
    """API-354–355: Admin has data_scope:* (also via *)."""
    perms = permissions_for_role("ADMIN")
    assert "data_scope:read" in perms
    assert "data_scope:update" in perms
    assert "*" in perms


def test_viewer_can_read_data_scopes() -> None:
    perms = permissions_for_role("VIEWER")
    assert "data_scope:read" in perms
    assert "data_scope:update" not in perms


def test_agent_cannot_manage_data_scopes() -> None:
    perms = permissions_for_role("AGENT")
    assert "data_scope:read" not in perms
    assert "data_scope:update" not in perms
