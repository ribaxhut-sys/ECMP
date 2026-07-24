"""FastAPI dependency that builds RequestContext from stub headers.

Reads headers → resolves / generates ids → delegates to RequestContextFactory.
Does not authenticate or authorize.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Header

from app.core.request_context.application.context_factory import RequestContextFactory
from app.core.request_context.domain.request_context import RequestContext
from app.core.request_context.infrastructure.headers import (
    HEADER_BRANCH_ID,
    HEADER_CORRELATION_ID,
    HEADER_LOCALE,
    HEADER_ORGANIZATION_ID,
    HEADER_REQUEST_ID,
    HEADER_TIMEZONE,
    HEADER_USER_ID,
)

_factory = RequestContextFactory()


def get_request_context(
    x_request_id: Annotated[str | None, Header(alias=HEADER_REQUEST_ID)] = None,
    x_correlation_id: Annotated[
        str | None, Header(alias=HEADER_CORRELATION_ID)
    ] = None,
    x_organization_id: Annotated[
        UUID | None, Header(alias=HEADER_ORGANIZATION_ID)
    ] = None,
    x_branch_id: Annotated[UUID | None, Header(alias=HEADER_BRANCH_ID)] = None,
    x_user_id: Annotated[UUID | None, Header(alias=HEADER_USER_ID)] = None,
    x_locale: Annotated[str | None, Header(alias=HEADER_LOCALE)] = None,
    x_timezone: Annotated[str | None, Header(alias=HEADER_TIMEZONE)] = None,
) -> RequestContext:
    """FastAPI DI entry point for platform execution context.

    Missing headers yield ``None`` / empty collections — never raise.
    Generates ``request_id`` and ``correlation_id`` when absent.
    """
    request_id = x_request_id if x_request_id else str(uuid4())
    correlation_id = x_correlation_id if x_correlation_id else str(uuid4())
    return _factory.create(
        request_id=request_id,
        correlation_id=correlation_id,
        organization_id=x_organization_id,
        branch_id=x_branch_id,
        user_id=x_user_id,
        locale=x_locale,
        timezone=x_timezone,
    )


__all__ = ["get_request_context"]
