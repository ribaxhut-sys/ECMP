"""Dashboard aggregation (CAPABILITY-013) + projection foundation (TASK-050).

CAPABILITY-013: read-only SQL aggregation providers (complaint / queue / SLA /
notification) + KPI rates. No dashboard tables. No domain writes.

API-319 (TASK-027): ``GET /dashboard/overview`` composition via KPI / Timeline /
Complaint services.

TASK-050: in-memory DashboardProjection updated from Complaint events.
"""

from app.modules.dashboard.projection_handler import DashboardProjectionHandler
from app.modules.dashboard.projection_models import DashboardProjection
from app.modules.dashboard.projection_registration import (
    register_dashboard_projection_handler,
)
from app.modules.dashboard.projection_store import DashboardProjectionStore

__all__ = [
    "DashboardProjection",
    "DashboardProjectionHandler",
    "DashboardProjectionStore",
    "register_dashboard_projection_handler",
]
