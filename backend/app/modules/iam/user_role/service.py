"""User-Role Assignment service (TASK-036).

PUT replace semantics: the provided roleIds become the full set.
Does not mutate users.role_id.
Invalidates IAM caches via invalidate_iam_user on assignment changes (TASK-041).
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.core.authorization.role_assignment_policy import assert_can_assign_role
from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.core.user_messages import m
from app.models import User
from app.modules.iam.permission_cache import invalidate_iam_user
from app.modules.iam.role.schemas import RoleResponse
from app.modules.iam.user_role.models import UserRole
from app.modules.iam.user_role.repository import UserRoleRepository
from app.modules.iam.user_role.schemas import UserRolesReplaceRequest
from app.modules.users.schemas import UserResponse


def _role_response(row: object) -> RoleResponse:
    return RoleResponse.model_validate(row)


def _user_response(user: User) -> UserResponse:
    role = user.__dict__.get("role")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        fullName=user.full_name,
        roleId=user.role_id,
        roleCode=getattr(role, "code", None) if role is not None else None,
        roleName=getattr(role, "name", None) if role is not None else None,
        branchId=user.branch_id,
        isActive=user.is_active,
        lastLoginAt=user.last_login_at,
        createdAt=user.created_at,
        updatedAt=user.updated_at,
        initials=getattr(user, "initials", None) or "USR",
    )


class UserRoleService:
    """Sole write path for user↔role links (junction table)."""

    def __init__(self, repository: UserRoleRepository) -> None:
        self._repo = repository

    def get_user_roles(self, user_id: uuid.UUID) -> list[RoleResponse]:
        self._require_user(user_id)
        return [
            _role_response(row) for row in self._repo.list_roles_for_user(user_id)
        ]

    def get_role_users(self, role_id: uuid.UUID) -> list[UserResponse]:
        self._require_role(role_id)
        return [
            _user_response(row) for row in self._repo.list_users_for_role(role_id)
        ]

    def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        *,
        actor_roles: Sequence[str] = (),
    ) -> list[RoleResponse]:
        self._require_user(user_id)
        role = self._repo.get_role(role_id)
        if role is None:
            raise NotFoundError(m("iam.role_not_found"))
        # UAT-020: same privilege matrix as users create/update.
        assert_can_assign_role(
            actor_roles,
            role.code,
            target_role_id=str(role_id),
        )
        if self._repo.get_link(user_id, role_id) is not None:
            raise ConflictError(
                m("iam.role_already_assigned"),
                details={"userId": str(user_id), "roleId": str(role_id)},
            )
        self._repo.add_link(
            UserRole(id=uuid.uuid4(), user_id=user_id, role_id=role_id)
        )
        self._repo.commit()
        invalidate_iam_user(user_id)
        return self.get_user_roles(user_id)

    def remove_role(
        self, user_id: uuid.UUID, role_id: uuid.UUID
    ) -> list[RoleResponse]:
        self._require_user(user_id)
        self._require_role(role_id)
        link = self._repo.get_link(user_id, role_id)
        if link is None:
            raise NotFoundError(m("iam.user_role_not_found"))
        self._repo.delete_link(link)
        self._repo.commit()
        invalidate_iam_user(user_id)
        return self.get_user_roles(user_id)

    def replace_roles(
        self,
        user_id: uuid.UUID,
        payload: UserRolesReplaceRequest,
        *,
        actor_roles: Sequence[str] = (),
    ) -> list[RoleResponse]:
        """Replace the full role set for a user (empty list clears all)."""
        self._require_user(user_id)
        desired_ids = list(payload.role_ids)
        if len(desired_ids) != len(set(desired_ids)):
            raise ValidationAppError(
                m("config.role_ids_no_duplicates"),
                details={"roleIds": [str(i) for i in desired_ids]},
            )

        found = self._repo.get_roles_by_ids(desired_ids)
        found_ids = {row.id for row in found}
        missing = [rid for rid in desired_ids if rid not in found_ids]
        if missing:
            raise NotFoundError(m("iam.roles_not_found"))

        current_links = self._repo.list_links_for_user(user_id)
        current_ids = {link.role_id for link in current_links}
        desired_set = set(desired_ids)

        to_remove = current_ids - desired_set
        to_add = desired_set - current_ids

        # UAT-020: enforce assignable matrix for newly added roles only.
        roles_by_id = {row.id: row for row in found}
        for role_id in sorted(to_add, key=str):
            role = roles_by_id[role_id]
            assert_can_assign_role(
                actor_roles,
                role.code,
                target_role_id=str(role_id),
            )

        if to_remove:
            self._repo.delete_links_for_user(user_id, to_remove)
        for role_id in sorted(to_add, key=str):
            self._repo.add_link(
                UserRole(id=uuid.uuid4(), user_id=user_id, role_id=role_id)
            )
        self._repo.commit()
        invalidate_iam_user(user_id)
        return [
            _role_response(row) for row in self._repo.list_roles_for_user(user_id)
        ]

    def _require_user(self, user_id: uuid.UUID) -> None:
        if self._repo.get_user(user_id) is None:
            raise NotFoundError(m("user.not_found"))

    def _require_role(self, role_id: uuid.UUID) -> None:
        if self._repo.get_role(role_id) is None:
            raise NotFoundError(m("iam.role_not_found"))
