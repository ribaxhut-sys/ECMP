"""Queue HTTP response DTO."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.modules.queue.application.dto import QueueDto
from app.modules.queue.models import QueuePolicy, QueueStatus


class QueueResponse(BaseModel):
    """Never Domain Entity. Never ORM."""

    model_config = ConfigDict(populate_by_name=True)

    queue_id: uuid.UUID = Field(alias="queueId")
    organization_id: uuid.UUID = Field(alias="organizationId")
    name: str
    description: str
    status: QueueStatus
    policy: QueuePolicy

    @classmethod
    def from_dto(cls, dto: QueueDto) -> QueueResponse:
        return cls(
            queue_id=dto.queue_id,
            organization_id=dto.organization_id,
            name=dto.name,
            description=dto.description,
            status=dto.status,
            policy=dto.policy,
        )
