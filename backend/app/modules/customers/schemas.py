"""Customer API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    external_customer_id: str = Field(alias="externalCustomerId")
    full_name: str = Field(alias="fullName")
    email: str | None = None
    phone: str | None = None


class CustomerPhoneUpdateRequest(BaseModel):
    """Local reference-cache phone update (Mode A lab) — not Customer Master SoR."""

    model_config = ConfigDict(populate_by_name=True)

    phone: str = Field(min_length=0, max_length=32)
