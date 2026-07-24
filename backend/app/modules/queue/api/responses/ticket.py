"""QueueTicket HTTP response DTO."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.queue.application.dto import QueueTicketDto
from app.modules.queue.models import QueuePriority, QueueTicketStatus


class QueueTicketResponse(BaseModel):
    """Never Domain Entity. Never ORM."""

    model_config = ConfigDict(populate_by_name=True)

    ticket_id: uuid.UUID = Field(alias="ticketId")
    queue_id: uuid.UUID = Field(alias="queueId")
    ticket_number: str = Field(alias="ticketNumber")
    priority: QueuePriority
    status: QueueTicketStatus
    created_at: datetime = Field(alias="createdAt")

    @classmethod
    def from_dto(cls, dto: QueueTicketDto) -> QueueTicketResponse:
        return cls(
            ticket_id=dto.ticket_id,
            queue_id=dto.queue_id,
            ticket_number=dto.ticket_number,
            priority=dto.priority,
            status=dto.status,
            created_at=dto.created_at,
        )
