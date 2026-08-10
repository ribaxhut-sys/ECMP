"""API router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.version import router as version_router
from app.modules.announcement.router import router as announcement_router
from app.modules.appointments.router import (
    appointments_router,
    escalation_appointments_router,
)
from app.modules.assignments.router import router as assignments_router
from app.modules.attachment.router import (
    complaint_attachments_router,
)
from app.modules.attachment.router import (
    router as attachment_router,
)
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.branches.router import router as branches_router
from app.modules.cm_batch1.router import router as cm_batch1_router
from app.modules.cm_case.api.router import router as cm_case_router
from app.modules.complaint.api import complaint_api_router
from app.modules.complaints.router import router as complaints_router
from app.modules.customers.router import router as customers_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.escalations.router import (
    escalations_router,
)
from app.modules.escalations.router import (
    router as complaint_escalations_router,
)
from app.modules.iam.data_scope.router import roles_data_scopes_router
from app.modules.iam.permission.router import router as permissions_router
from app.modules.iam.role.router import router as roles_router
from app.modules.iam.role_permission.router import (
    permissions_matrix_router,
    roles_matrix_router,
)
from app.modules.iam.user_role.router import (
    roles_users_router,
    users_roles_router,
)
from app.modules.internal_complaint.api.router import (
    router as internal_complaint_router,
)
from app.modules.kpi.router import router as kpi_router
from app.modules.notification.router import queue_router as notification_queue_router
from app.modules.notification.router import (
    templates_router as notification_templates_router,
)
from app.modules.queue.api import queue_api_router
from app.modules.reports.router import router as reports_router
from app.modules.resolutions.router import router as resolutions_router
from app.modules.search.router import router as complaint_search_router
from app.modules.settings.router import router as settings_router
from app.modules.sla.router import policies_router as sla_policies_router
from app.modules.sla.router import router as sla_router
from app.modules.timeline.router import (
    complaint_activity_router as activity_timeline_complaint_router,
)
from app.modules.timeline.router import router as activity_timeline_router
from app.modules.timelines.router import router as timelines_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(version_router)
api_router.include_router(auth_router)
api_router.include_router(cm_batch1_router)
api_router.include_router(cm_case_router)
api_router.include_router(internal_complaint_router)
api_router.include_router(announcement_router)
api_router.include_router(dashboard_router)
api_router.include_router(kpi_router)
api_router.include_router(settings_router)
api_router.include_router(attachment_router)
api_router.include_router(audit_router)
api_router.include_router(roles_router)
api_router.include_router(roles_matrix_router)
api_router.include_router(roles_users_router)
api_router.include_router(roles_data_scopes_router)
api_router.include_router(permissions_router)
api_router.include_router(permissions_matrix_router)
api_router.include_router(notification_templates_router)
api_router.include_router(notification_queue_router)
api_router.include_router(queue_api_router)
api_router.include_router(reports_router)
api_router.include_router(customers_router)
api_router.include_router(branches_router)
api_router.include_router(users_router)
api_router.include_router(users_roles_router)
# Specific sub-routes before generic /{id} complaint / escalation routes.
api_router.include_router(complaint_search_router)
api_router.include_router(assignments_router)
api_router.include_router(complaint_escalations_router)
api_router.include_router(escalation_appointments_router)
api_router.include_router(escalations_router)
api_router.include_router(appointments_router)
api_router.include_router(resolutions_router)
api_router.include_router(sla_policies_router)
api_router.include_router(sla_router)
api_router.include_router(activity_timeline_router)
api_router.include_router(activity_timeline_complaint_router)
api_router.include_router(complaint_attachments_router)
api_router.include_router(timelines_router)
# Legacy ECMF complaints keeps /api/v1/complaints CRUD (auth/SLA).
# CAPABILITY-004 mounts ticket-nested routes only (unique paths).
api_router.include_router(complaints_router)
api_router.include_router(complaint_api_router)
