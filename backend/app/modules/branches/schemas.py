"""Branch API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class BranchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
