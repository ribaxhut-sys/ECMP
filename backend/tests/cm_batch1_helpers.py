"""Shared helpers for CM Batch-1 tests (confirm lock before create — TD-CM-001)."""

from __future__ import annotations

from app.modules.cm_batch1.schemas import CreateComplaintBatch1Request
from app.modules.cm_batch1.service import CmBatch1Service


def confirmed_create(
    service: CmBatch1Service,
    body: CreateComplaintBatch1Request,
    *,
    request_id: str,
    channel_message_id: str | None = None,
    actor_id: str = "actor-1",
    principal_key: str | None = None,
):
    """Confirm/lock customer for principal then create (FR-002 AC1 / TD-CM-001)."""
    pk = (principal_key or actor_id or "actor-1")
    if isinstance(pk, str):
        pk = pk.strip()
    else:
        pk = "actor-1"
    service.confirm_customer(body.customer_id.strip(), principal_key=pk)
    return service.create_complaint(
        body,
        request_id=request_id,
        channel_message_id=channel_message_id,
        actor_id=actor_id or pk,
        principal_key=pk,
    )
