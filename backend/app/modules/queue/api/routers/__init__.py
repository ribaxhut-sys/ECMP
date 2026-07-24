"""Aggregate Queue REST routers (TASK-064 / CAPABILITY-003)."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.queue.api.routers.counters import (
    counters_router,
    nested_router as counters_nested_router,
)
from app.modules.queue.api.routers.queues import router as queues_router
from app.modules.queue.api.routers.tickets import (
    nested_router as tickets_nested_router,
    ops_queue_router,
    ops_tickets_router,
    tickets_router,
)

queue_api_router = APIRouter()
queue_api_router.include_router(queues_router)
queue_api_router.include_router(tickets_nested_router)
queue_api_router.include_router(tickets_router)
queue_api_router.include_router(ops_queue_router)
queue_api_router.include_router(ops_tickets_router)
queue_api_router.include_router(counters_nested_router)
queue_api_router.include_router(counters_router)

__all__ = ["queue_api_router"]
