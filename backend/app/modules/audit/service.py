"""Audit Log service (TASK-031).

Synchronous append-only logging. No async, event bus, or workers.
Sensitive fields are sanitized via the P5-002 secrets redaction library
before persistence.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.enums import AuditAction
from app.core.errors import NotFoundError, ValidationAppError
from app.core.secrets import REDACTED, redact_mapping
from app.core.user_messages import m
from app.modules.audit.models import SystemAuditLog
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditLogResponse


def redact_sensitive(value: Any) -> Any:
    """Sanitize audit payloads using the shared P5-002 redaction library."""
    return redact_mapping(value)


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
                m("config.event_type_required"),
                details={"eventType": event_type},
            )
        if len(event) > 100:
            raise ValidationAppError(
                m("config.event_type_max_length"),
                details={"eventType": event_type},
            )
        if not entity:
            raise ValidationAppError(
                m("config.entity_type_required"),
                details={"entityType": entity_type},
            )
        if len(entity) > 100:
            raise ValidationAppError(
                m("config.entity_type_max_length"),
                details={"entityType": entity_type},
            )

        scrubbed_old = redact_sensitive(old_values) if old_values is not None else None
        scrubbed_new = redact_sensitive(new_values) if new_values is not None else None
        scrubbed_meta = redact_sensitive(metadata) if metadata is not None else None
        if scrubbed_old is not None and not isinstance(scrubbed_old, dict):
            scrubbed_old = {"value": scrubbed_old}
        if scrubbed_new is not None and not isinstance(scrubbed_new, dict):
            scrubbed_new = {"value": scrubbed_new}
        if scrubbed_meta is not None and not isinstance(scrubbed_meta, dict):
            scrubbed_meta = {"value": scrubbed_meta}

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
            old_values=scrubbed_old,
            new_values=scrubbed_new,
            metadata_json=scrubbed_meta,
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
            raise NotFoundError(m("audit.not_found"))
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
                m("config.date_from_lte_date_to_snake"),
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
                f"aksi audit tidak didukung: {action}",
                details={
                    "action": str(action),
                    "allowed": [a.value for a in AuditAction],
                },
            ) from exc


# Re-export for callers/tests that assert the shared mask token.
__all__ = ["AuditService", "redact_sensitive", "REDACTED"]
