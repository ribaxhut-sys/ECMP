"""Queue REST API package (TASK-064).

HTTP adapters only — Controllers translate HTTP ↔ Application.
No business rules. No ORM. No repository usage inside controllers.
"""

from app.modules.queue.api.routers import queue_api_router

__all__ = ["queue_api_router"]
