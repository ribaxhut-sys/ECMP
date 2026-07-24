"""Create / update QueueCounter HTTP request models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.queue.api.validators import strip_required
from app.modules.queue.models import QueueStatus


class CreateCounterRequest(BaseModel):
    """POST /api/v1/queues/{queue_id}/counters"""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=200)
    status: QueueStatus = QueueStatus.CLOSED

    @field_validator("name")
    @classmethod
    def _name(cls, value: str) -> str:
        return strip_required(value, "name")


class UpdateCounterRequest(BaseModel):
    """PUT /api/v1/counters/{counter_id}"""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    status: QueueStatus | None = None

    @field_validator("name")
    @classmethod
    def _name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return strip_required(value, "name")
