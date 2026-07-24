"""QueueCounter HTTP response DTO."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.modules.queue.application.services.crud_service import QueueCounterView
from app.modules.queue.models import QueueStatus


class QueueCounterResponse(BaseModel):
    """Never Domain Entity. Never ORM. Includes queue association for REST."""

    model_config = ConfigDict(populate_by_name=True)

    counter_id: uuid.UUID = Field(alias="counterId")
    queue_id: uuid.UUID = Field(alias="queueId")
    name: str
    status: QueueStatus

    @classmethod
    def from_view(cls, view: QueueCounterView) -> QueueCounterResponse:
        return cls(
            counter_id=view.counter_id,
            queue_id=view.queue_id,
            name=view.name,
            status=view.status,
        )
