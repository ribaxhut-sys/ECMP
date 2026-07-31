"""Create / update Queue HTTP request models."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.queue.api.validators import strip_optional, strip_required
from app.modules.queue.models import QueuePolicy, QueueStatus


class CreateQueueRequest(BaseModel):
    """POST /api/v1/queues"""

    model_config = ConfigDict(populate_by_name=True)

    organization_id: uuid.UUID = Field(alias="organizationId")
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    policy: QueuePolicy = QueuePolicy.FIFO
    status: QueueStatus = QueueStatus.CLOSED

    @field_validator("name")
    @classmethod
    def _name(cls, value: str) -> str:
        return strip_required(value, "name")

    @field_validator("description")
    @classmethod
    def _description(cls, value: str) -> str:
        return strip_optional(value)


class UpdateQueueRequest(BaseModel):
    """PUT /api/v1/queues/{queue_id}"""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    policy: QueuePolicy | None = None
    status: QueueStatus | None = None

    @field_validator("name")
    @classmethod
    def _name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return strip_required(value, "name")

    @field_validator("description")
    @classmethod
    def _description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return strip_optional(value)
