"""DeliveryValidator — validate delivery preparation inputs (TASK-057).

Checks recipient, channel, template, and payload presence.
Never calls providers or transports.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.delivery.models import DeliveryChannel, DeliveryResult
from app.modules.execution.dispatch_models import DispatchRequest

_KNOWN_CHANNELS = frozenset(c.value for c in DeliveryChannel)

_CHANNEL_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        "email": DeliveryChannel.EMAIL.value,
        "whatsapp": DeliveryChannel.WHATSAPP.value,
        "push": DeliveryChannel.PUSH.value,
        "sms": DeliveryChannel.SMS.value,
        "websocket": DeliveryChannel.WEBSOCKET.value,
        "ws": DeliveryChannel.WEBSOCKET.value,
    }
)


@dataclass(frozen=True, slots=True)
class DeliveryValidation:
    """Internal validation outcome with optional resolved fields."""

    result: DeliveryResult
    channel: DeliveryChannel | None = None
    recipient: str | None = None
    template_id: str | None = None
    payload: Mapping[str, Any] | None = None


def _resolve_channel_token(raw: str) -> str | None:
    token = raw.strip()
    if not token:
        return None
    upper = token.upper()
    if upper in _KNOWN_CHANNELS:
        return upper
    return _CHANNEL_ALIASES.get(token.lower())


def extract_channel(dispatch: DispatchRequest) -> str | None:
    """Resolve channel from configuration or target. No provider call."""
    cfg = dispatch.configuration
    if "channel" in cfg and cfg["channel"] is not None:
        return _resolve_channel_token(str(cfg["channel"]))

    target = (dispatch.target or "").strip()
    if not target:
        return None

    # Supports "channel:email", "EMAIL", "email"
    if ":" in target:
        prefix, _, value = target.partition(":")
        if prefix.strip().lower() in {"channel", "delivery"}:
            return _resolve_channel_token(value)
        return _resolve_channel_token(value) or _resolve_channel_token(target)

    return _resolve_channel_token(target)


def extract_recipient(dispatch: DispatchRequest) -> str | None:
    cfg = dispatch.configuration
    if "recipient" not in cfg or cfg["recipient"] is None:
        return None
    value = str(cfg["recipient"]).strip()
    return value or None


def extract_template_id(dispatch: DispatchRequest) -> str | None:
    cfg = dispatch.configuration
    for key in ("template_id", "templateId", "template"):
        if key in cfg and cfg[key] is not None:
            value = str(cfg[key]).strip()
            if value:
                return value
    return None


def extract_payload(dispatch: DispatchRequest) -> Mapping[str, Any] | None:
    cfg = dispatch.configuration
    if "payload" not in cfg:
        return None
    value = cfg["payload"]
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value
    return None


class DeliveryValidator:
    """Validate delivery inputs. Catalog / shape checks only — never send."""

    def validate(self, dispatch: DispatchRequest) -> DeliveryValidation:
        if not isinstance(dispatch, DispatchRequest):
            raise TypeError(
                f"dispatch must be DispatchRequest, got {type(dispatch).__name__}"
            )

        recipient = extract_recipient(dispatch)
        if recipient is None:
            return DeliveryValidation(
                result=DeliveryResult(
                    success=False,
                    reason="INVALID_RECIPIENT: recipient is missing or empty",
                    provider_selected=None,
                )
            )

        channel_token = extract_channel(dispatch)
        if channel_token is None:
            raw = dispatch.configuration.get("channel") or dispatch.target or ""
            raw_s = str(raw).strip()
            if not raw_s:
                reason = "INVALID_CHANNEL: channel is missing"
            else:
                reason = f"INVALID_CHANNEL: unknown channel={raw_s!r}"
            return DeliveryValidation(
                result=DeliveryResult(
                    success=False,
                    reason=reason,
                    provider_selected=None,
                )
            )

        template_id = extract_template_id(dispatch)
        if template_id is None:
            return DeliveryValidation(
                result=DeliveryResult(
                    success=False,
                    reason="INVALID_TEMPLATE: template_id is missing or empty",
                    provider_selected=None,
                )
            )

        payload = extract_payload(dispatch)
        if payload is None:
            return DeliveryValidation(
                result=DeliveryResult(
                    success=False,
                    reason="INVALID_PAYLOAD: payload is missing or not a mapping",
                    provider_selected=None,
                )
            )

        channel = DeliveryChannel(channel_token)
        return DeliveryValidation(
            result=DeliveryResult(
                success=True,
                reason=f"DELIVERY_READY: channel={channel.value}",
                provider_selected=None,
            ),
            channel=channel,
            recipient=recipient,
            template_id=template_id,
            payload=payload,
        )
