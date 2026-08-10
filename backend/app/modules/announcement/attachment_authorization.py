"""Authorization for Announcement-owned attachments (business decision, LOCKED).

Used by the *shared* attachment router (CAPABILITY-011) when an attachment's
aggregate_type is "Announcement" — see app/modules/attachment/router.py.
Backend-only enforcement; the frontend is never trusted (§8).

Visibility rule:
  - IMMEDIATE — visible to anyone with announcement:read as soon as the file
    exists, even while the announcement is still DRAFT.
  - PUBLISHED (default) — follows the announcement's own status; only
    visible once the announcement is PUBLISHED.

When one platform attachment is linked to multiple announcements, access is
granted if *any* join satisfies the rule (do not rely on a single arbitrary join).

Admin/Supervisor/Manager Pusat (require_announcement_manage) bypass the
visibility rule entirely — they can preview any attachment while editing,
same as they can already edit a DRAFT announcement.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.authorization.gates import principal_may_manage_announcements
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.errors import NotFoundError, PermissionDeniedError
from app.core.user_messages import m
from app.modules.announcement.attachment_repository import AnnouncementAttachmentRepository
from app.modules.announcement.repository import (
    AnnouncementRepository,
    is_scheduled_announcement,
)


def _resolve_org_unit(principal: Principal, session: Session) -> str | None:
    resolver = OrgUnitResolver(session)
    return resolver.normalize(principal.org_unit_id) or resolver.resolve_principal_membership(
        principal.user_id
    )


def assert_can_access_announcement_attachment(
    *,
    principal: Principal,
    session: Session,
    attachment_id: uuid.UUID,
) -> None:
    """Gate for reading metadata / downloading bytes (GET, GET .../download).

    Combines:
      1) Catalog PUBLIC/PRIVATE access (who may know the file exists)
      2) Join IMMEDIATE/PUBLISHED + announcement lifecycle (reader context)
    """
    from app.modules.announcement.catalog_access import can_view_catalog_attachment
    from app.modules.attachment.registration import build_attachment_service

    try:
        platform = build_attachment_service(session).get(attachment_id)
    except NotFoundError:
        raise NotFoundError(m("attachment.not_found")) from None

    if not can_view_catalog_attachment(
        principal=principal, session=session, attachment=platform
    ):
        # Do not leak Private existence to other branches.
        raise NotFoundError(m("attachment.not_found"))

    join_repo = AnnouncementAttachmentRepository(session)
    joins = join_repo.list_by_attachment_id(attachment_id)

    # Catalog-only orphan (unlinked) — manage/owner already passed catalog check.
    if not joins:
        if principal_may_manage_announcements(
            principal, org_unit_id=_resolve_org_unit(principal, session)
        ):
            return
        if platform.uploaded_by is not None and platform.uploaded_by == principal.user_id:
            return
        # PUBLIC catalog orphans are downloadable by any announcement:read holder.
        return

    if not principal.has_permission("announcement:read"):
        raise PermissionDeniedError(m("common.forbidden"))

    if principal_may_manage_announcements(
        principal, org_unit_id=_resolve_org_unit(principal, session)
    ):
        return

    announcements = AnnouncementRepository(session)
    now = datetime.now(UTC)
    saw_denied_live = False
    for join in joins:
        announcement = announcements.get(join.announcement_id)
        if announcement is None:
            continue
        if is_scheduled_announcement(
            announcement.status,
            announcement.start_at,
            now=now,
        ):
            continue
        if join.visibility == "IMMEDIATE":
            return
        if announcement.status == "PUBLISHED":
            return
        saw_denied_live = True

    if saw_denied_live:
        raise PermissionDeniedError(m("common.forbidden"))
    raise NotFoundError(m("attachment.not_found"))


def assert_can_manage_announcement_attachment(
    *,
    principal: Principal,
    session: Session,
    attachment_id: uuid.UUID,
) -> None:
    """Gate for mutating (DELETE via the generic attachment endpoint) — defense
    in depth. The primary removal path is the dedicated announcement-scoped
    endpoint (require_announcement_manage); this closes the same hole on the
    generic one."""
    join_repo = AnnouncementAttachmentRepository(session)
    joins = join_repo.list_by_attachment_id(attachment_id)
    if not joins:
        raise NotFoundError(m("attachment.not_found"))

    if not principal_may_manage_announcements(
        principal, org_unit_id=_resolve_org_unit(principal, session)
    ):
        raise PermissionDeniedError(
            m("announcement.only_admin_supervisor_manager_pusat")
        )
