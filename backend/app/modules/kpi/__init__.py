"""KPI Foundation package (TASK-026 / DEC-015) + KPI Projection (TASK-051).

TASK-026: read-only analytics API over operational tables.
TASK-051: in-memory KpiProjection updated from Complaint events only.
"""

from app.modules.kpi.projection_handler import KpiProjectionHandler
from app.modules.kpi.projection_models import KpiProjection
from app.modules.kpi.projection_registration import register_kpi_projection_handler
from app.modules.kpi.projection_store import KpiProjectionStore

__all__ = [
    "KpiProjection",
    "KpiProjectionHandler",
    "KpiProjectionStore",
    "register_kpi_projection_handler",
]
