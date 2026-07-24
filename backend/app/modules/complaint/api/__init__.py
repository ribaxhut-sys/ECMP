"""Complaint REST API package (CAPABILITY-004).

HTTP adapters only — Controllers translate HTTP ↔ Application.
No business rules. No ORM. No repository usage inside controllers.
"""

from app.modules.complaint.api.routers import (
    complaint_api_router,
    complaint_foundation_router,
)

__all__ = ["complaint_api_router", "complaint_foundation_router"]
