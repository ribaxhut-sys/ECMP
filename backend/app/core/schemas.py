"""Standard API response and error envelopes (Pydantic v2)."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class PageMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(alias="pageSize", ge=1, le=100)
    total_items: int = Field(alias="totalItems", ge=0)

    model_config = ConfigDict(populate_by_name=True)


class DataResponse(BaseModel, Generic[T]):
    data: T


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PageMeta
