"""Announcement file catalog access (PUBLIC / PRIVATE).

Orthogonal to ``announcement_attachments.visibility`` (IMMEDIATE / PUBLISHED),
which only controls when a file appears in an announcement reader context.

Rules (LOCKED for this delivery):
  - PUBLIC  — any authenticated caller with announcement:read (or manage)
  - PRIVATE — Pusat sees all; Cabang sees all files of the same org unit
  - Owner (uploader or same org unit) may set PUBLIC/PRIVATE
  - Pusat may override PUBLIC/PRIVATE
  - When linked to an *active* announcement → sticky PUBLIC
  - Catalog upload (no announcement join) uses Announcement aggregate +
    well-known catalog aggregate id
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.authorization.gates import principal_may_manage_announcements
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import is_pusat_unit
from app.modules.announcement.attachment_repository import AnnouncementAttachmentRepository
from app.modules.announcement.repository import AnnouncementRepository, is_scheduled_announcement
from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AttachmentStatus
from app.modules.attachment.models import AttachmentORM

ACCESS_PUBLIC = "PUBLIC"
ACCESS_PRIVATE = "PRIVATE"

# Placeholder aggregate_id for catalog-only uploads (not yet linked to an
# announcement). CAP-011 requires a non-null UUID; joins still use real ids.
ANNOUNCEMENT_CATALOG_AGGREGATE_ID = uuid.UUID("00000000-0000-4000-8000-0000000000a1")


def resolve_caller_org_unit(principal: Principal, session: Session) -> str | None:
    """Canonical Branch.code for the caller (claim UUID → code when needed)."""
    resolver = OrgUnitResolver(session)
    return resolver.resolve_declared(principal.org_unit_id) or (
        resolver.resolve_principal_membership(principal.user_id)
    )


def resolve_attachment_org_unit(
    session: Session, attachment: Attachment
) -> str | None:
    """Org unit stamped on the file, with uploader-membership fallback."""
    resolver = OrgUnitResolver(session)
    stamped = resolver.resolve_declared(attachment.uploaded_org_unit_id)
    if stamped:
        return stamped
    if attachment.uploaded_by is None:
        return None
    return resolver.resolve_principal_membership(attachment.uploaded_by)


def caller_is_pusat(principal: Principal, session: Session) -> bool:
    org = resolve_caller_org_unit(principal, session)
    if is_pusat_unit(org):
        return True
    # Unscoped ADMIN manage path — treat as Pusat for catalog override.
    return principal_may_manage_announcements(principal, org_unit_id=org) and (
        org is None or is_pusat_unit(org)
    )


def effective_access_level(attachment: Attachment) -> str:
    return (attachment.access_level or ACCESS_PRIVATE).upper()


def announcement_is_currently_active(
    *,
    status: str,
    start_at: datetime | None,
    end_at: datetime | None,
    now: datetime | None = None,
) -> bool:
    """Same window idea as landing /active — PUBLISHED, started, not expired."""
    when = now or datetime.now(UTC)
    if status != "PUBLISHED":
        return False
    if is_scheduled_announcement(status, start_at, now=when):
        return False
    if end_at is not None and end_at <= when:
        return False
    return True


def apply_sticky_public_if_active(
    *,
    session: Session,
    attachment: Attachment,
    now: datetime | None = None,
) -> Attachment:
    """If any linked announcement is active, force access_level=PUBLIC (sticky)."""
    if effective_access_level(attachment) == ACCESS_PUBLIC:
        return attachment
    join_repo = AnnouncementAttachmentRepository(session)
    joins = join_repo.list_by_attachment_id(attachment.id)
    if not joins:
        return attachment
    announcements = AnnouncementRepository(session)
    when = now or datetime.now(UTC)
    for join in joins:
        row = announcements.get(join.announcement_id)
        if row is None:
            continue
        if announcement_is_currently_active(
            status=row.status,
            start_at=row.start_at,
            end_at=row.end_at,
            now=when,
        ):
            orm = session.get(AttachmentORM, attachment.id)
            if orm is None:
                return attachment
            orm.access_level = ACCESS_PUBLIC
            session.flush()
            attachment.access_level = ACCESS_PUBLIC
            return attachment
    return attachment


def can_view_catalog_attachment(
    *,
    principal: Principal,
    session: Session,
    attachment: Attachment,
) -> bool:
    if attachment.status == AttachmentStatus.DELETED.value:
        return False
    if not (
        principal.has_permission("announcement:read")
        or principal.has_permission("announcement:manage")
        or principal.has_permission("attachment:read")
    ):
        return False

    attachment = apply_sticky_public_if_active(session=session, attachment=attachment)
    level = effective_access_level(attachment)
    if level == ACCESS_PUBLIC:
        return True

    # Uploader always sees their own catalog files (even if org metadata is empty).
    if attachment.uploaded_by is not None and attachment.uploaded_by == principal.user_id:
        return True

    caller_org = resolve_caller_org_unit(principal, session)
    if is_pusat_unit(caller_org) or caller_is_pusat(principal, session):
        return True
    uploaded_org = resolve_attachment_org_unit(session, attachment)
    return bool(uploaded_org and caller_org and uploaded_org == caller_org)


def can_change_access_level(
    *,
    principal: Principal,
    session: Session,
    attachment: Attachment,
) -> bool:
    """Owner (same uploader or same org) or Pusat override."""
    caller_org = resolve_caller_org_unit(principal, session)
    if is_pusat_unit(caller_org) or caller_is_pusat(principal, session):
        return True
    if attachment.uploaded_by is not None and attachment.uploaded_by == principal.user_id:
        return True
    uploaded_org = resolve_attachment_org_unit(session, attachment)
    return bool(uploaded_org and caller_org and uploaded_org == caller_org)


def can_delete_from_catalog(
    *,
    principal: Principal,
    session: Session,
    attachment: Attachment,
) -> bool:
    return can_change_access_level(
        principal=principal, session=session, attachment=attachment
    )


def mark_attachment_public(session: Session, attachment_id: uuid.UUID) -> None:
    orm = session.get(AttachmentORM, attachment_id)
    if orm is None:
        return
    orm.access_level = ACCESS_PUBLIC
    session.flush()
