"""Aggregate Complaint REST routers (CAPABILITY-004…007).

``complaint_api_router`` — production mount: ticket-nested routes only
(unique paths; does not shadow legacy ECMF ``/api/v1/complaints`` CRUD).

``complaint_foundation_router`` — full CAPABILITY-004…007 surface (CRUD +
processing + assignment + escalation + ticket nested) for isolated tests
and future cutover.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.complaint.api.routers.complaints import router as complaints_router
from app.modules.complaint.api.routers.tickets import router as tickets_router

complaint_api_router = APIRouter()
complaint_api_router.include_router(tickets_router)

complaint_foundation_router = APIRouter()
complaint_foundation_router.include_router(complaints_router)
complaint_foundation_router.include_router(tickets_router)

__all__ = ["complaint_api_router", "complaint_foundation_router"]
