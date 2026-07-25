"""Delivery provider ports (CAPABILITY-009).

No SMTP / Twilio / FCM / webhook HTTP. Stub only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.modules.notification.domain.entity import NotificationRecord


@dataclass(frozen=True, slots=True)
class ProviderResult:
    """Outcome of a provider send attempt."""

    success: bool
    provider: str
    detail: str | None = None


class NotificationProvider(Protocol):
    """Channel-agnostic delivery port.

    Implementations must not be imported by Complaint.
    """

    name: str

    def send(self, notification: NotificationRecord) -> ProviderResult:
        """Attempt delivery for ``notification`` (may be stubbed)."""
        ...


class StubNotificationProvider:
    """Always-succeeds stub — no network, no SMTP, no WhatsApp."""

    name = "stub"

    def __init__(self, *, succeed: bool = True, detail: str | None = None) -> None:
        self._succeed = succeed
        self._detail = detail

    def send(self, notification: NotificationRecord) -> ProviderResult:
        _ = notification
        if self._succeed:
            return ProviderResult(
                success=True,
                provider=self.name,
                detail=self._detail or "stub delivery accepted",
            )
        return ProviderResult(
            success=False,
            provider=self.name,
            detail=self._detail or "stub delivery failed",
        )
