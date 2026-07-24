"""Permission Management service — master data CRUD (TASK-034).

System permissions (is_system=true) cannot be deleted. Role↔permission
matrix and Authorization Engine changes are out of scope.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.iam.permission.models import Permission
from app.modules.iam.permission.repository import PermissionRepository
from app.modules.iam.permission.schemas import (
    PermissionCreateRequest,
    PermissionResponse,
    PermissionUpdateRequest,
)

# module:action — lowercase alphanumeric / underscore segments.
_PERMISSION_CODE_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}:[a-z][a-z0-9_]{0,63}$")
_MODULE_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


def _to_response(row: Permission) -> PermissionResponse:
    return PermissionResponse.model_validate(row)


class PermissionService:
    """Sole write path for permission master data."""

    def __init__(self, repository: PermissionRepository) -> None:
        self._repo = repository

    def list(
        self,
        *,
        active_only: bool = False,
        include_system: bool = True,
        module: str | None = None,
    ) -> list[PermissionResponse]:
        return [
            _to_response(row)
            for row in self._repo.list(
                active_only=active_only,
                include_system=include_system,
                module=module,
            )
        ]

    def get(self, permission_id: uuid.UUID) -> PermissionResponse:
        return _to_response(self._require(permission_id))

    def create(self, payload: PermissionCreateRequest) -> PermissionResponse:
        code = self._normalize_code(payload.code)
        module = self._normalize_module(payload.module)
        self._assert_code_matches_module(code, module)
        if self._repo.get_by_code(code) is not None:
            raise ConflictError(
                f"Permission code already exists: {code}",
                details={"code": code},
            )
        now = datetime.now(UTC)
        row = Permission(
            id=uuid.uuid4(),
            code=code,
            name=payload.name,
            module=module,
            description=payload.description,
            is_system=False,
            is_active=payload.is_active,
            created_at=now,
            updated_at=now,
        )
        self._repo.add(row)
        self._repo.commit()
        return _to_response(row)

    def update(
        self, permission_id: uuid.UUID, payload: PermissionUpdateRequest
    ) -> PermissionResponse:
        row = self._require(permission_id)
        if payload.name is not None:
            row.name = payload.name
        if "description" in payload.model_fields_set:
            row.description = payload.description
        if payload.is_active is not None:
            row.is_active = payload.is_active
        row.updated_at = datetime.now(UTC)
        self._repo.commit()
        return _to_response(row)

    def delete(self, permission_id: uuid.UUID) -> None:
        row = self._require(permission_id)
        if row.is_system:
            raise ConflictError(
                "System permission cannot be deleted",
                details={
                    "id": str(permission_id),
                    "code": row.code,
                    "isSystem": True,
                },
            )
        self._repo.soft_delete(row)
        self._repo.commit()

    def _require(self, permission_id: uuid.UUID) -> Permission:
        row = self._repo.get_by_id(permission_id)
        if row is None:
            raise NotFoundError("Permission not found")
        return row

    @staticmethod
    def _normalize_code(raw: str) -> str:
        code = raw.strip().lower()
        if not _PERMISSION_CODE_RE.match(code):
            raise ValidationAppError(
                "code must match module:action "
                "(lowercase letters, digits, underscores)",
                details={"code": raw},
            )
        return code

    @staticmethod
    def _normalize_module(raw: str) -> str:
        module = raw.strip().lower()
        if not _MODULE_RE.match(module):
            raise ValidationAppError(
                "module must be lowercase letters, digits, and underscores "
                "(start with a letter)",
                details={"module": raw},
            )
        return module

    @staticmethod
    def _assert_code_matches_module(code: str, module: str) -> None:
        prefix, _, _action = code.partition(":")
        if prefix != module:
            raise ValidationAppError(
                "code module prefix must match module field",
                details={"code": code, "module": module},
            )
