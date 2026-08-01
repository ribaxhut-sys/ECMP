"""Data Scope Foundation service (TASK-037 / TASK-039).

PUT replace semantics for role scopes. Invalidates IAM caches on writes
(TASK-039 / TASK-041). Automatic endpoint filtering remains opt-in via helpers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.iam.data_scope.models import (
    DataScope,
    ScopeType,
    scope_forbids_value,
    scope_requires_value,
)
from app.modules.iam.data_scope.repository import DataScopeRepository
from app.modules.iam.data_scope.schemas import (
    DataScopeCreateRequest,
    DataScopeReplaceRequest,
    DataScopeResponse,
    DataScopeUpdateRequest,
)
from app.modules.iam.permission_cache import invalidate_iam_all
from app.core.user_messages import m


def _to_response(row: DataScope) -> DataScopeResponse:
    return DataScopeResponse.model_validate(row)


def _normalize_pair(
    scope_type: ScopeType | str, scope_value: str | None
) -> tuple[str, str | None]:
    st = ScopeType(scope_type)
    value = scope_value.strip() if isinstance(scope_value, str) else scope_value
    if value == "":
        value = None
    if scope_forbids_value(st) and value is not None:
        raise ValidationAppError(
            f"{st} must not have scopeValue",
            details={"scopeType": st.value, "scopeValue": value},
        )
    if scope_requires_value(st) and value is None:
        raise ValidationAppError(
            f"{st} requires a non-empty scopeValue",
            details={"scopeType": st.value},
        )
    return st.value, value


class DataScopeService:
    """Sole write path for role data scopes."""

    def __init__(self, repository: DataScopeRepository) -> None:
        self._repo = repository

    def list(
        self,
        *,
        role_id: uuid.UUID | None = None,
        scope_type: str | None = None,
    ) -> list[DataScopeResponse]:
        return [
            _to_response(row)
            for row in self._repo.list(role_id=role_id, scope_type=scope_type)
        ]

    def get(self, scope_id: uuid.UUID) -> DataScopeResponse:
        return _to_response(self._require(scope_id))

    def get_role_scopes(self, role_id: uuid.UUID) -> list[DataScopeResponse]:
        self._require_role(role_id)
        return [_to_response(row) for row in self._repo.list_for_role(role_id)]

    def create(self, payload: DataScopeCreateRequest) -> DataScopeResponse:
        self._require_role(payload.role_id)
        scope_type, scope_value = _normalize_pair(
            payload.scope_type, payload.scope_value
        )
        if (
            self._repo.get_by_key(payload.role_id, scope_type, scope_value)
            is not None
        ):
            raise ConflictError(
                m("iam.data_scope_exists"),
                details={
                    "roleId": str(payload.role_id),
                    "scopeType": scope_type,
                    "scopeValue": scope_value,
                },
            )
        now = datetime.now(UTC)
        row = DataScope(
            id=uuid.uuid4(),
            role_id=payload.role_id,
            scope_type=scope_type,
            scope_value=scope_value,
            created_at=now,
            updated_at=now,
        )
        self._repo.add(row)
        self._repo.commit()
        invalidate_iam_all()
        return _to_response(row)

    def update(
        self, scope_id: uuid.UUID, payload: DataScopeUpdateRequest
    ) -> DataScopeResponse:
        row = self._require(scope_id)
        next_type = (
            payload.scope_type
            if payload.scope_type is not None
            else ScopeType(row.scope_type)
        )
        if "scope_value" in payload.model_fields_set:
            next_value = payload.scope_value
        else:
            next_value = row.scope_value
        scope_type, scope_value = _normalize_pair(next_type, next_value)

        existing = self._repo.get_by_key(row.role_id, scope_type, scope_value)
        if existing is not None and existing.id != row.id:
            raise ConflictError(
                m("iam.data_scope_exists"),
                details={
                    "roleId": str(row.role_id),
                    "scopeType": scope_type,
                    "scopeValue": scope_value,
                },
            )
        row.scope_type = scope_type
        row.scope_value = scope_value
        row.updated_at = datetime.now(UTC)
        self._repo.commit()
        invalidate_iam_all()
        return _to_response(row)

    def delete(self, scope_id: uuid.UUID) -> None:
        row = self._require(scope_id)
        self._repo.delete(row)
        self._repo.commit()
        invalidate_iam_all()

    def replace_role_scopes(
        self, role_id: uuid.UUID, payload: DataScopeReplaceRequest
    ) -> list[DataScopeResponse]:
        """Replace the full data-scope set for a role (empty clears)."""
        self._require_role(role_id)
        normalized: list[tuple[str, str | None]] = []
        for item in payload.scopes:
            pair = _normalize_pair(item.scope_type, item.scope_value)
            normalized.append(pair)
        if len(normalized) != len(set(normalized)):
            raise ValidationAppError(
                m("config.scopes_no_duplicates"),
                details={
                    "scopes": [
                        {"scopeType": t, "scopeValue": v} for t, v in normalized
                    ]
                },
            )

        self._repo.delete_all_for_role(role_id)
        now = datetime.now(UTC)
        for scope_type, scope_value in normalized:
            self._repo.add(
                DataScope(
                    id=uuid.uuid4(),
                    role_id=role_id,
                    scope_type=scope_type,
                    scope_value=scope_value,
                    created_at=now,
                    updated_at=now,
                )
            )
        self._repo.commit()
        invalidate_iam_all()
        return [_to_response(row) for row in self._repo.list_for_role(role_id)]

    def _require(self, scope_id: uuid.UUID) -> DataScope:
        row = self._repo.get_by_id(scope_id)
        if row is None:
            raise NotFoundError(m("iam.data_scope_not_found"))
        return row

    def _require_role(self, role_id: uuid.UUID) -> None:
        if self._repo.get_role(role_id) is None:
            raise NotFoundError(m("iam.role_not_found"))
