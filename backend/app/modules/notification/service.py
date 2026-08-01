"""Notification Foundation service (TASK-030 + CAPABILITY-009).

Creates / queues / lifecycle-transitions notification rows.
Transport goes through NotificationProvider stubs only — no SMTP / Twilio.
Complaint must never import this module for delivery decisions.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.enums import NotificationChannel, NotificationQueueStatus
from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.core.user_messages import m
from app.modules.notification.domain.entity import NotificationRecord
from app.modules.notification.infrastructure.providers import (
    NotificationProvider,
    StubNotificationProvider,
)
from app.modules.notification.mappers import apply_record, new_queue_row, to_record
from app.modules.notification.models import NotificationQueue, NotificationTemplate
from app.modules.notification.repository import NotificationRepository
from app.modules.notification.schemas import (
    NotificationCreateRequest,
    NotificationQueueResponse,
    NotificationTemplateCreateRequest,
    NotificationTemplateResponse,
    NotificationTemplateUpdateRequest,
)
from app.modules.settings.service import SettingsService

# Setting keys (seeded by migration 0018; not hardcoded operational values).
SETTING_ENABLED = "notification.enabled"
SETTING_DEFAULT_CHANNEL = "notification.default.channel"
SETTING_MAX_RETRY = "notification.max.retry"

_DEFAULT_ENABLED = True
_DEFAULT_CHANNEL = NotificationChannel.EMAIL.value
_DEFAULT_MAX_RETRY = 3

_TEMPLATE_CODE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.\-]{0,99}$")
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def _to_template_response(row: NotificationTemplate) -> NotificationTemplateResponse:
    return NotificationTemplateResponse.model_validate(row)


def _to_queue_response(row: NotificationQueue) -> NotificationQueueResponse:
    return NotificationQueueResponse.model_validate(row)


def _render_text(template: str, variables: dict[str, Any]) -> str:
    """Replace ``{{key}}`` placeholders; unknown keys left unchanged."""

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            return match.group(0)
        value = variables[key]
        return "" if value is None else str(value)

    return _PLACEHOLDER_RE.sub(_replace, template)


class NotificationService:
    """Template CRUD + notification domain lifecycle (stub providers only)."""

    def __init__(
        self,
        repository: NotificationRepository,
        settings: SettingsService,
        provider: NotificationProvider | None = None,
    ) -> None:
        self._repo = repository
        self._settings = settings
        self._provider: NotificationProvider = provider or StubNotificationProvider()

    # --- settings helpers --------------------------------------------------

    def is_enabled(self) -> bool:
        return self._settings.get_bool(SETTING_ENABLED, default=_DEFAULT_ENABLED)

    def default_channel(self) -> str:
        return self._settings.get_string(
            SETTING_DEFAULT_CHANNEL, default=_DEFAULT_CHANNEL
        ).strip().upper()

    def max_retry(self) -> int:
        return self._settings.get_int(SETTING_MAX_RETRY, default=_DEFAULT_MAX_RETRY)

    # --- template CRUD -----------------------------------------------------

    def list_templates(
        self, *, active_only: bool = False
    ) -> list[NotificationTemplateResponse]:
        return [
            _to_template_response(row)
            for row in self._repo.list_templates(active_only=active_only)
        ]

    def get_template(self, template_id: uuid.UUID) -> NotificationTemplateResponse:
        return _to_template_response(self._require_template(template_id))

    def create_template(
        self, payload: NotificationTemplateCreateRequest
    ) -> NotificationTemplateResponse:
        self._validate_template_code(payload.code)
        self._validate_channel(payload.channel)
        if self._repo.get_template_by_code(payload.code) is not None:
            raise ConflictError(
                f"Kode template notifikasi sudah ada: {payload.code}",
                details={"code": payload.code},
            )
        now = datetime.now(UTC)
        row = NotificationTemplate(
            id=uuid.uuid4(),
            code=payload.code,
            name=payload.name,
            channel=payload.channel,
            subject=payload.subject,
            content=payload.content,
            is_active=payload.is_active,
            created_at=now,
            updated_at=now,
        )
        self._repo.add_template(row)
        self._repo.commit()
        return _to_template_response(row)

    def update_template(
        self,
        template_id: uuid.UUID,
        payload: NotificationTemplateUpdateRequest,
    ) -> NotificationTemplateResponse:
        row = self._require_template(template_id)
        data = payload.model_dump(exclude_unset=True)
        if "channel" in data and data["channel"] is not None:
            self._validate_channel(data["channel"])
        if not data:
            raise ValidationAppError(
                m("config.at_least_one_field"),
                details={"fields": []},
            )
        for key, value in data.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(UTC)
        self._repo.commit()
        return _to_template_response(row)

    def delete_template(self, template_id: uuid.UUID) -> None:
        """Soft-delete: set is_active=False (no deleted_at column on templates)."""
        row = self._require_template(template_id)
        if not row.is_active:
            raise NotFoundError(m("notification.template_not_found"))
        self._repo.soft_delete_template(row)
        self._repo.commit()

    # --- queue / domain API ------------------------------------------------

    def create(
        self, payload: NotificationCreateRequest
    ) -> NotificationQueueResponse:
        """Validate template + settings, generate payload, enqueue as PENDING."""
        if not self.is_enabled():
            raise ValidationAppError(
                m("notification.disabled"),
                details={"key": SETTING_ENABLED, "value": False},
            )

        template = self._repo.get_template_by_code(payload.template_code)
        if template is None or not template.is_active:
            raise NotFoundError(
                f"Template notifikasi aktif tidak ditemukan: {payload.template_code}"
            )

        self._validate_channel(template.channel)
        _ = self.default_channel()
        max_retry = self.max_retry()
        if max_retry < 0:
            raise ValidationAppError(
                m("notification.max_retry_min"),
                details={"key": SETTING_MAX_RETRY, "value": max_retry},
            )

        rendered_payload = self._generate_payload(
            template=template,
            recipient=payload.recipient,
            variables=payload.variables,
            max_retry=max_retry,
        )
        return self.queue(
            template_code=template.code,
            recipient=payload.recipient,
            payload=rendered_payload,
            channel=template.channel,
            subject=rendered_payload.get("subject"),
            message=rendered_payload.get("content"),
            notification_type="TemplateEnqueue",
            scheduled_at=payload.scheduled_at,
        )

    def queue(
        self,
        *,
        template_code: str | None,
        recipient: str,
        payload: dict[str, Any],
        channel: str | None = None,
        subject: str | None = None,
        message: str | None = None,
        notification_type: str | None = None,
        scheduled_at: datetime | None = None,
        notification_id: uuid.UUID | None = None,
        commit: bool = True,
    ) -> NotificationQueueResponse:
        """Insert a PENDING notification row. Does not send."""
        resolved_channel = (
            channel
            or (payload.get("channel") if isinstance(payload.get("channel"), str) else None)
            or self.default_channel()
        )
        record = NotificationRecord.create(
            channel=resolved_channel,
            recipient=recipient,
            notification_type=notification_type,
            subject=subject if subject is not None else payload.get("subject"),
            message=message if message is not None else payload.get("content"),
            template=template_code,
            payload=payload,
            notification_id=notification_id,
            scheduled_at=scheduled_at,
        )
        row = new_queue_row(record)
        self._repo.add_queue(row)
        if commit:
            self._repo.commit()
        return _to_queue_response(row)

    def enqueue_domain_notification(
        self,
        *,
        notification_type: str,
        recipient: str,
        subject: str,
        message: str,
        payload: dict[str, Any],
        channel: str | None = None,
        template_code: str | None = None,
        notification_id: uuid.UUID | None = None,
        commit: bool = True,
    ) -> NotificationQueueResponse:
        """Persist a domain Notification request (event-driven path)."""
        if not self.is_enabled():
            raise ValidationAppError(
                m("notification.disabled"),
                details={"key": SETTING_ENABLED, "value": False},
            )
        return self.queue(
            template_code=template_code,
            recipient=recipient,
            payload=payload,
            channel=channel or self.default_channel(),
            subject=subject,
            message=message,
            notification_type=notification_type,
            notification_id=notification_id,
            commit=commit,
        )

    def cancel(self, queue_id: uuid.UUID) -> NotificationQueueResponse:
        row = self._require_queue(queue_id)
        record = to_record(row)
        record.cancel()
        apply_record(row, record)
        self._repo.commit()
        return _to_queue_response(row)

    def mark_sent(self, queue_id: uuid.UUID) -> NotificationQueueResponse:
        row = self._require_queue(queue_id)
        record = to_record(row)
        record.mark_sent()
        apply_record(row, record)
        self._repo.commit()
        return _to_queue_response(row)

    def mark_failed(
        self, queue_id: uuid.UUID, *, error: str
    ) -> NotificationQueueResponse:
        row = self._require_queue(queue_id)
        record = to_record(row)
        record.mark_failed(error=error)
        apply_record(row, record)
        self._repo.commit()
        return _to_queue_response(row)

    def retry(self, queue_id: uuid.UUID) -> NotificationQueueResponse:
        row = self._require_queue(queue_id)
        record = to_record(row)
        record.retry(max_retry=self.max_retry())
        apply_record(row, record)
        self._repo.commit()
        return _to_queue_response(row)

    def process(self, queue_id: uuid.UUID) -> NotificationQueueResponse:
        """Attempt stub delivery: Pending/Failed → Sending → Sent|Failed.

        No real email / WhatsApp / SMS / Push / webhook.
        """
        row = self._require_queue(queue_id)
        record = to_record(row)
        if record.status == NotificationQueueStatus.FAILED.value:
            # Re-enter sending without consuming a retry slot here.
            record.status = NotificationQueueStatus.PENDING.value
        record.mark_sending()
        apply_record(row, record)
        self._repo.flush()

        result = self._provider.send(record)
        if result.success:
            record.mark_sent()
        else:
            record.mark_failed(
                error=result.detail or f"{result.provider} delivery failed"
            )
        apply_record(row, record)
        self._repo.commit()
        return _to_queue_response(row)

    def get(self, queue_id: uuid.UUID) -> NotificationQueueResponse:
        return _to_queue_response(self._require_queue(queue_id))

    def list(
        self, *, status: str | None = None, limit: int = 100
    ) -> list[NotificationQueueResponse]:
        if status is not None:
            self._validate_status(status)
        return [
            _to_queue_response(row)
            for row in self._repo.list_queue(status=status, limit=limit)
        ]

    # --- internals ---------------------------------------------------------

    def _generate_payload(
        self,
        *,
        template: NotificationTemplate,
        recipient: str,
        variables: dict[str, Any],
        max_retry: int,
    ) -> dict[str, Any]:
        vars_copy = dict(variables)
        rendered_subject = (
            _render_text(template.subject, vars_copy)
            if template.subject is not None
            else None
        )
        rendered_content = _render_text(template.content, vars_copy)
        return {
            "channel": template.channel,
            "templateCode": template.code,
            "templateName": template.name,
            "recipient": recipient,
            "subject": rendered_subject,
            "content": rendered_content,
            "variables": vars_copy,
            "maxRetry": max_retry,
        }

    def _require_template(self, template_id: uuid.UUID) -> NotificationTemplate:
        row = self._repo.get_template_by_id(template_id)
        if row is None:
            raise NotFoundError(m("notification.template_not_found"))
        return row

    def _require_queue(self, queue_id: uuid.UUID) -> NotificationQueue:
        row = self._repo.get_queue_by_id(queue_id)
        if row is None:
            raise NotFoundError(m("notification.queue_item_not_found"))
        return row

    @staticmethod
    def _validate_template_code(code: str) -> None:
        if not _TEMPLATE_CODE_RE.match(code):
            raise ValidationAppError(
                m("config.template_code_format"),
                details={"code": code},
            )

    @staticmethod
    def _validate_channel(channel: str) -> None:
        try:
            NotificationChannel(channel)
        except ValueError as exc:
            raise ValidationAppError(
                f"kanal notifikasi tidak didukung: {channel}",
                details={
                    "channel": channel,
                    "allowed": [c.value for c in NotificationChannel],
                },
            ) from exc

    @staticmethod
    def _validate_status(status: str) -> None:
        try:
            NotificationQueueStatus(status)
        except ValueError as exc:
            raise ValidationAppError(
                f"status notifikasi tidak didukung: {status}",
                details={
                    "status": status,
                    "allowed": [s.value for s in NotificationQueueStatus],
                },
            ) from exc
