"""Email delivery abstraction — swappable providers (no SMTP coupling)."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache
from typing import Literal

from app.core.config import Settings, get_settings
from app.core.i18n_messages import get_message, normalize_language

logger = logging.getLogger("ecmp.email")


class EmailService(ABC):
    """Provider-agnostic email interface.

    Future providers: SMTP, SendGrid, SES, Mailgun — implement this ABC
    and select via ``EMAIL_PROVIDER`` without changing call sites.
    """

    @abstractmethod
    def send_password_reset(
        self,
        *,
        to_email: str,
        reset_url: str,
        expires_at: datetime,
        language: str | None = None,
    ) -> None:
        """Deliver a password-reset link. Never log the recipient's password."""

    def send_password_changed(
        self,
        *,
        to_email: str,
        language: str | None = None,
    ) -> None:
        """Notify the user their password changed. Stub — no provider wires this yet."""
        _ = (to_email, language)


class LoggingEmailService(EmailService):
    """Development provider — logs the localized subject/body (never use in production mail)."""

    def send_password_reset(
        self,
        *,
        to_email: str,
        reset_url: str,
        expires_at: datetime,
        language: str | None = None,
    ) -> None:
        lang = normalize_language(language)
        subject = get_message("password_reset_subject", lang)
        body = get_message("password_reset_body", lang).format(
            reset_url=reset_url, expires_at=expires_at.isoformat()
        )
        logger.info(
            "DEV email provider: password reset for %s language=%s subject=%r "
            "expires_at=%s url=%s body=%r",
            to_email,
            lang,
            subject,
            expires_at.isoformat(),
            reset_url,
            body,
        )

    def send_password_changed(
        self,
        *,
        to_email: str,
        language: str | None = None,
    ) -> None:
        lang = normalize_language(language)
        subject = get_message("password_changed_subject", lang)
        body = get_message("password_changed_body", lang)
        logger.info(
            "DEV email provider: password changed for %s language=%s subject=%r body=%r",
            to_email,
            lang,
            subject,
            body,
        )


class NoOpEmailService(EmailService):
    """Silent provider for tests."""

    def send_password_reset(
        self,
        *,
        to_email: str,
        reset_url: str,
        expires_at: datetime,
        language: str | None = None,
    ) -> None:
        _ = (to_email, reset_url, expires_at, language)

    def send_password_changed(
        self,
        *,
        to_email: str,
        language: str | None = None,
    ) -> None:
        _ = (to_email, language)


EmailProviderName = Literal["logging", "noop"]


def create_email_service(settings: Settings | None = None) -> EmailService:
    cfg = settings or get_settings()
    provider = (cfg.email_provider or "logging").strip().lower()
    if provider == "noop":
        return NoOpEmailService()
    if provider == "logging":
        return LoggingEmailService()
    # Unknown → logging (safe default for development; staging should set explicitly)
    logger.warning("Unknown EMAIL_PROVIDER=%s; using logging provider", provider)
    return LoggingEmailService()


@lru_cache
def get_email_service() -> EmailService:
    return create_email_service()
