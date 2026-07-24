"""Dashboard repository — intentionally empty (TASK-027).

Dashboard stores no data and must never query the database.
Composition lives in ``DashboardService`` via KPI / Timeline / Complaint modules.
"""

from __future__ import annotations


class DashboardRepository:
    """No persistence. Present for module structure parity only."""

    pass
