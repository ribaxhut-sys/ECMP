"""Create / update QueueTicket HTTP request models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.modules.queue.models import QueuePriority, QueueTicketStatus


class CreateTicketRequest(BaseModel):
    """POST /api/v1/queues/{queue_id}/tickets"""

    model_config = ConfigDict(populate_by_name=True)

    priority: QueuePriority = QueuePriority.NORMAL


class UpdateTicketRequest(BaseModel):
    """PUT /api/v1/tickets/{ticket_id}"""

    model_config = ConfigDict(populate_by_name=True)

    priority: QueuePriority | None = None
    status: QueueTicketStatus | None = None
