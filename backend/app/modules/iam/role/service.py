"""Role Management service — master data CRUD (TASK-033).

System roles (is_system=true) cannot be deleted. User assignment and
permission matrix are out of scope.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.iam.role.models import Role
from app.modules.iam.role.repository import RoleRepository
from app.modules.iam.role.schemas import (
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
)

_ROLE_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,99}$")


def _to_response(row: Role) -> RoleResponse:
    return RoleResponse.model_validate(row)


class RoleService:
    """Sole write path for role master data."""

    def __init__(self, repository: RoleRepository) -> None:
        self._repo = repository

    def list(
        self,
        *,
        active_only: bool = False,
        include_system: bool = True,
    ) -> list[RoleResponse]:
        return [
            _to_response(row)
            for row in self._repo.list(
                active_only=active_only,
                include_system=include_system,
            )
        ]

    def get(self, role_id: uuid.UUID) -> RoleResponse:
        return _to_response(self._require(role_id))

    def create(self, payload: RoleCreateRequest) -> RoleResponse:
        code = self._normalize_code(payload.code)
        if self._repo.get_by_code(code) is not None:
            raise ConflictError(
                f"Role code already exists: {code}",
                details={"code": code},
            )
        now = datetime.now(UTC)
        row = Role(
            id=uuid.uuid4(),
            code=code,
            name=payload.name,
            description=payload.description,
            is_system=False,
            is_active=payload.is_active,
            created_at=now,
            updated_at=now,
        )
        self._repo.add(row)
        self._repo.commit()
        return _to_response(row)

    def update(self, role_id: uuid.UUID, payload: RoleUpdateRequest) -> RoleResponse:
        row = self._require(role_id)
        if payload.name is not None:
            row.name = payload.name
        if "description" in payload.model_fields_set:
            row.description = payload.description
        if payload.is_active is not None:
            row.is_active = payload.is_active
        row.updated_at = datetime.now(UTC)
        self._repo.commit()
        return _to_response(row)

    def delete(self, role_id: uuid.UUID) -> None:
        row = self._require(role_id)
        if row.is_system:
            raise ConflictError(
                "System role cannot be deleted",
                details={"id": str(role_id), "code": row.code, "isSystem": True},
            )
        self._repo.soft_delete(row)
        self._repo.commit()

    def _require(self, role_id: uuid.UUID) -> Role:
        row = self._repo.get_by_id(role_id)
        if row is None:
            raise NotFoundError("Role not found")
        return row

    @staticmethod
    def _normalize_code(raw: str) -> str:
        code = raw.strip().upper()
        if not _ROLE_CODE_RE.match(code):
            raise ValidationAppError(
                "code must be uppercase letters, digits, and underscores "
                "(max 100; start with a letter)",
                details={"code": raw},
            )
        return code
