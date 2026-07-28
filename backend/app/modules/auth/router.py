"""Authentication HTTP routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.auth import CurrentPrincipal
from app.core.config import Settings, get_settings
from app.core.errors import UnauthenticatedError
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.auth.login_protection import get_login_attempt_guard
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    AuthMeResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.modules.email import get_email_service

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


def get_auth_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(AuthRepository(session), settings, get_email_service())


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first = forwarded.split(",", 1)[0].strip()
        if first:
            return first
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _login_guard_key(request: Request, username: str) -> str:
    return f"{_client_ip(request)}:{username.strip().lower()}"


def _set_refresh_cookie(
    response: Response,
    *,
    raw_token: str,
    settings: Settings,
) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=raw_token,
        max_age=settings.refresh_token_expire_seconds,
        path=settings.refresh_cookie_path,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
    )


def _clear_refresh_cookie(response: Response, *, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
    )


def _read_refresh_cookie(request: Request, settings: Settings) -> str | None:
    value = request.cookies.get(settings.refresh_cookie_name)
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@router.post(
    "/login",
    response_model=DataResponse[TokenResponse],
    status_code=200,
    summary="Login",
)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[TokenResponse]:
    guard_key = _login_guard_key(request, payload.username)
    guard = None
    if settings.login_rate_limit_enabled:
        guard = get_login_attempt_guard(settings)
        guard.check(guard_key)

    try:
        session = service.login(payload)
    except UnauthenticatedError:
        if guard is not None:
            guard.record_failure(guard_key)
        raise

    if guard is not None:
        guard.reset(guard_key)

    _set_refresh_cookie(response, raw_token=session.refresh_token, settings=settings)
    return DataResponse(data=session.tokens)


@router.post(
    "/refresh",
    response_model=DataResponse[TokenResponse],
    status_code=200,
    summary="Refresh access token",
)
def refresh(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[TokenResponse]:
    session = service.refresh(_read_refresh_cookie(request, settings))
    _set_refresh_cookie(response, raw_token=session.refresh_token, settings=settings)
    return DataResponse(data=session.tokens)


@router.post(
    "/logout",
    status_code=204,
    response_class=Response,
    response_model=None,
    summary="Logout",
)
def logout(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    # UAT-019: clear cookie on the SAME Response instance that is returned.
    # Returning a new Response(status_code=204) drops Set-Cookie headers.
    service.logout(_read_refresh_cookie(request, settings))
    _clear_refresh_cookie(response, settings=settings)
    response.status_code = 204
    return response


@router.get(
    "/me",
    response_model=DataResponse[AuthMeResponse],
    status_code=200,
    summary="Current user",
)
def me(
    principal: CurrentPrincipal,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> DataResponse[AuthMeResponse]:
    return DataResponse(data=service.me(principal.user_id))


@router.post(
    "/forgot-password",
    response_model=DataResponse[ForgotPasswordResponse],
    status_code=200,
    summary="Request password reset",
)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> DataResponse[ForgotPasswordResponse]:
    return DataResponse(data=service.forgot_password(payload, request=request))


@router.post(
    "/reset-password",
    response_model=DataResponse[ResetPasswordResponse],
    status_code=200,
    summary="Reset password with token",
)
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> DataResponse[ResetPasswordResponse]:
    return DataResponse(data=service.reset_password(payload, request=request))
