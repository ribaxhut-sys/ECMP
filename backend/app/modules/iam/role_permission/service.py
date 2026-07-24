"""Role-Permission Matrix service (TASK-035).

PUT replace semantics: the provided permissionIds become the full set.
Invalidates IAM caches on matrix changes (TASK-038 / TASK-041).
"""

from __future__ import annotations

import uuid

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.iam.permission.schemas import PermissionResponse
from app.modules.iam.permission_cache import invalidate_iam_all
from app.modules.iam.role.schemas import RoleResponse
from app.modules.iam.role_permission.models import RolePermission
from app.modules.iam.role_permission.repository import RolePermissionRepository
from app.modules.iam.role_permission.schemas import RolePermissionsReplaceRequest


def _permission_response(row: object) -> PermissionResponse:
    return PermissionResponse.model_validate(row)


def _role_response(row: object) -> RoleResponse:
    return RoleResponse.model_validate(row)


class RolePermissionService:
    """Sole write path for role↔permission links."""

    def __init__(self, repository: RolePermissionRepository) -> None:
        self._repo = repository

    def get_role_permissions(self, role_id: uuid.UUID) -> list[PermissionResponse]:
        self._require_role(role_id)
        return [
            _permission_response(row)
            for row in self._repo.list_permissions_for_role(role_id)
        ]

    def get_permission_roles(self, permission_id: uuid.UUID) -> list[RoleResponse]:
        self._require_permission(permission_id)
        return [
            _role_response(row)
            for row in self._repo.list_roles_for_permission(permission_id)
        ]

    def assign_permission(
        self, role_id: uuid.UUID, permission_id: uuid.UUID
    ) -> list[PermissionResponse]:
        self._require_role(role_id)
        self._require_permission(permission_id)
        if self._repo.get_link(role_id, permission_id) is not None:
            raise ConflictError(
                "Permission already assigned to role",
                details={
                    "roleId": str(role_id),
                    "permissionId": str(permission_id),
                },
            )
        self._repo.add_link(
            RolePermission(
                id=uuid.uuid4(),
                role_id=role_id,
                permission_id=permission_id,
            )
        )
        self._repo.commit()
        invalidate_iam_all()
        return self.get_role_permissions(role_id)

    def remove_permission(
        self, role_id: uuid.UUID, permission_id: uuid.UUID
    ) -> list[PermissionResponse]:
        self._require_role(role_id)
        self._require_permission(permission_id)
        link = self._repo.get_link(role_id, permission_id)
        if link is None:
            raise NotFoundError("Role permission link not found")
        self._repo.delete_link(link)
        self._repo.commit()
        invalidate_iam_all()
        return self.get_role_permissions(role_id)

    def replace_permissions(
        self, role_id: uuid.UUID, payload: RolePermissionsReplaceRequest
    ) -> list[PermissionResponse]:
        """Replace the full permission set for a role (empty list clears all)."""
        self._require_role(role_id)
        desired_ids = list(payload.permission_ids)
        if len(desired_ids) != len(set(desired_ids)):
            raise ValidationAppError(
                "permissionIds must not contain duplicates",
                details={"permissionIds": [str(i) for i in desired_ids]},
            )

        found = self._repo.get_permissions_by_ids(desired_ids)
        found_ids = {row.id for row in found}
        missing = [pid for pid in desired_ids if pid not in found_ids]
        if missing:
            raise NotFoundError("One or more permissions not found")

        current_links = self._repo.list_links_for_role(role_id)
        current_ids = {link.permission_id for link in current_links}
        desired_set = set(desired_ids)

        to_remove = current_ids - desired_set
        to_add = desired_set - current_ids

        if to_remove:
            self._repo.delete_links_for_role(role_id, to_remove)
        for permission_id in sorted(to_add, key=str):
            self._repo.add_link(
                RolePermission(
                    id=uuid.uuid4(),
                    role_id=role_id,
                    permission_id=permission_id,
                )
            )
        self._repo.commit()
        invalidate_iam_all()
        return [
            _permission_response(row)
            for row in self._repo.list_permissions_for_role(role_id)
        ]

    def _require_role(self, role_id: uuid.UUID) -> None:
        if self._repo.get_role(role_id) is None:
            raise NotFoundError("Role not found")

    def _require_permission(self, permission_id: uuid.UUID) -> None:
        if self._repo.get_permission(permission_id) is None:
            raise NotFoundError("Permission not found")
