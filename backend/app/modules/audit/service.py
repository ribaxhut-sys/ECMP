"""Audit Log service (TASK-031).

Synchronous append-only logging. No async, event bus, or workers.
Sensitive fields are masked/removed before persistence.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.enums import AuditAction
from app.core.errors import NotFoundError, ValidationAppError
from app.modules.audit.models import SystemAuditLog
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditLogResponse

_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|authorization|"
    r"refresh[_-]?token|access[_-]?token|cookie|jwt|bearer|private[_-]?key)",
    re.IGNORECASE,
)
_MASK = "***REDACTED***"


def redact_sensitive(value: Any) -> Any:
    """Recursively mask or drop secrets from dict/list payloads."""
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if _SENSITIVE_KEY_RE.search(str(key)):
                cleaned[str(key)] = _MASK
            else:
                cleaned[str(key)] = redact_sensitive(item)
        return cleaned
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, tuple):
        return [redact_sensitive(item) for item in value]
    return value


def _to_response(row: SystemAuditLog) -> AuditLogResponse:
    return AuditLogResponse.model_validate(row)


class AuditService:
    """Platform audit writer/reader (synchronous)."""

    def __init__(self, repository: AuditRepository) -> None:
        self._repo = repository

    def log(
        self,
        *,
        event_type: str,
        entity_type: str,
        action: str | AuditAction,
        entity_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        actor_name: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> AuditLogResponse:
        """Persist one audit row. Masks secrets in old/new/metadata."""
        action_value = self._validate_action(action)
        event = (event_type or "").strip()
        entity = (entity_type or "").strip()
        if not event:
            raise ValidationAppError(
                "event_type is required",
                details={"eventType": event_type},
            )
        if len(event) > 100:
            raise ValidationAppError(
                "event_type max length is 100",
                details={"eventType": event_type},
            )
        if not entity:
            raise ValidationAppError(
                "entity_type is required",
                details={"entityType": entity_type},
            )
        if len(entity) > 100:
            raise ValidationAppError(
                "entity_type max length is 100",
                details={"entityType": entity_type},
            )

        row = SystemAuditLog(
            id=uuid.uuid4(),
            event_type=event,
            entity_type=entity,
            entity_id=entity_id,
            action=action_value,
            actor_id=actor_id,
            actor_name=(actor_name.strip()[:255] if actor_name else None),
            ip_address=(ip_address.strip()[:64] if ip_address else None),
            user_agent=(user_agent.strip() if user_agent else None) or None,
            old_values=redact_sensitive(old_values) if old_values is not None else None,
            new_values=redact_sensitive(new_values) if new_values is not None else None,
            metadata_json=redact_sensitive(metadata) if metadata is not None else None,
            created_at=datetime.now(UTC),
        )
        self._repo.add(row)
        if commit:
            self._repo.commit()
        else:
            self._repo.flush()
        return _to_response(row)

    def get(self, audit_id: uuid.UUID) -> AuditLogResponse:
        row = self._repo.get_by_id(audit_id)
        if row is None:
            raise NotFoundError("Audit log not found")
        return _to_response(row)

    def list(
        self,
        *,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLogResponse]:
        if action is not None:
            self._validate_action(action)
        if date_from is not None and date_to is not None and date_from > date_to:
            raise ValidationAppError(
                "date_from must be <= date_to",
                details={"dateFrom": date_from.isoformat(), "dateTo": date_to.isoformat()},
            )
        rows = self._repo.list(
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            action=action,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return [_to_response(row) for row in rows]

    @staticmethod
    def _validate_action(action: str | AuditAction) -> str:
        value = action.value if isinstance(action, AuditAction) else str(action).strip().upper()
        try:
            return AuditAction(value).value
        except ValueError as exc:
            raise ValidationAppError(
                f"unsupported audit action: {action}",
                details={
                    "action": str(action),
                    "allowed": [a.value for a in AuditAction],
                },
            ) from exc
