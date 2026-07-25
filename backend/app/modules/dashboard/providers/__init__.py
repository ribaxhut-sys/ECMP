"""CAPABILITY-013 Dashboard metric providers (read-only SQL aggregates)."""

from app.modules.dashboard.providers.complaint_provider import ComplaintDashboardProvider
from app.modules.dashboard.providers.notification_provider import (
    NotificationDashboardProvider,
)
from app.modules.dashboard.providers.queue_provider import QueueDashboardProvider
from app.modules.dashboard.providers.sla_provider import SlaDashboardProvider

__all__ = [
    "ComplaintDashboardProvider",
    "NotificationDashboardProvider",
    "QueueDashboardProvider",
    "SlaDashboardProvider",
]
