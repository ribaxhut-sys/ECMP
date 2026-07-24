"""Dashboard orchestration + projection foundation.

TASK-027 / API-319: composes KPI + Timeline + Complaint responses.
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
