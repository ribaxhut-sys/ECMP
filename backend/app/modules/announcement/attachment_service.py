"""Announcement attachment orchestration.

Delegates storage/upload/download/checksum to CAPABILITY-011 AttachmentService.
Owns join rows (IMMEDIATE/PUBLISHED) and catalog access (PUBLIC/PRIVATE).
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.authorization.principal import Principal
from app.core.authorization.visibility import is_pusat_unit
from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError, ValidationAppError
from app.core.user_messages import m
from app.models import User
from app.modules.announcement.attachment_repository import (
    AnnouncementAttachmentRepository,
    AnnouncementAttachmentRow,
)
from app.modules.announcement.catalog_access import (
    ACCESS_PRIVATE,
    ACCESS_PUBLIC,
    ANNOUNCEMENT_CATALOG_AGGREGATE_ID,
    announcement_is_currently_active,
    apply_sticky_public_if_active,
    caller_is_pusat,
    can_change_access_level,
    can_delete_from_catalog,
    can_view_catalog_attachment,
    mark_attachment_public,
    resolve_attachment_org_unit,
    resolve_caller_org_unit,
)
from app.modules.announcement.repository import AnnouncementRepository
from app.modules.announcement.schemas import (
    AnnouncementAttachmentLibraryItem,
    AnnouncementAttachmentResponse,
)
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
from app.modules.attachment.models import AttachmentORM
from app.modules.attachment.service import AttachmentService


def _row_to_response(row: AnnouncementAttachmentRow) -> AnnouncementAttachmentResponse:
    return AnnouncementAttachmentResponse(
        id=row.attachment_id,
        file_name=row.original_name,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        visibility=row.visibility,  # type: ignore[arg-type]
        created_at=row.created_at,
    )


def is_visible_to_reader(*, visibility: str, announcement_status: str) -> bool:
    if visibility == "IMMEDIATE":
        return True
    return announcement_status == "PUBLISHED"


def _library_item_from_row(row) -> AnnouncementAttachmentLibraryItem:
    level = (row.access_level or ACCESS_PRIVATE).upper()
    if level not in (ACCESS_PUBLIC, ACCESS_PRIVATE):
        level = ACCESS_PRIVATE
    return AnnouncementAttachmentLibraryItem(
        id=row.id,
        file_name=row.original_name,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        created_at=row.created_at,
        access_level=level,  # type: ignore[arg-type]
        uploaded_org_unit_id=row.uploaded_org_unit_id,
        uploaded_by=row.uploaded_by,
        uploaded_by_name=getattr(row, "uploaded_by_name", None),
        usage_count=row.usage_count,
    )


def _user_display_name(session: Session, user_id: uuid.UUID | None) -> str | None:
    if user_id is None:
        return None
    user = session.get(User, user_id)
    if user is None or getattr(user, "deleted_at", None) is not None:
        return None
    name = (user.full_name or "").strip()
    return name or None


class AnnouncementAttachmentService:
    def __init__(
        self,
        *,
        announcements: AnnouncementRepository,
        join_repo: AnnouncementAttachmentRepository,
        attachments: AttachmentService,
        session: Session | None = None,
    ) -> None:
        self._announcements = announcements
        self._join_repo = join_repo
        self._attachments = attachments
        self._session = session

    def _require_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("AnnouncementAttachmentService requires a DB session")
        return self._session

    def upload(
        self,
        announcement_id: uuid.UUID,
        *,
        filename: str | None,
        content_type: str | None,
        data: bytes,
        visibility: str,
        actor_id: uuid.UUID,
        uploaded_org_unit_id: str | None = None,
        access_level: str = ACCESS_PRIVATE,
    ) -> AnnouncementAttachmentResponse:
        if self._announcements.get(announcement_id) is None:
            raise NotFoundError(m("announcement.not_found"))

        level = (access_level or ACCESS_PRIVATE).upper()
        if level not in (ACCESS_PUBLIC, ACCESS_PRIVATE):
            raise ValidationAppError(m("attachment.invalid_access_level"))

        uploaded = self._attachments.upload(
            aggregate_type=AggregateType.ANNOUNCEMENT.value,
            aggregate_id=announcement_id,
            filename=filename,
            content_type=content_type,
            data=data,
            uploaded_by=actor_id,
            commit=False,
        )
        session = self._require_session()
        orm = session.get(AttachmentORM, uploaded.id)
        if orm is not None:
            orm.access_level = level
            orm.uploaded_org_unit_id = uploaded_org_unit_id
            session.flush()

        self._join_repo.create(
            announcement_id=announcement_id,
            attachment_id=uploaded.id,
            visibility=visibility,
            created_by=actor_id,
        )

        # Sticky public if the target announcement is already active.
        ann = self._announcements.get(announcement_id)
        if ann is not None and announcement_is_currently_active(
            status=ann.status, start_at=ann.start_at, end_at=ann.end_at
        ):
            mark_attachment_public(session, uploaded.id)
            level = ACCESS_PUBLIC

        self._join_repo.commit()
        return AnnouncementAttachmentResponse(
            id=uploaded.id,
            file_name=uploaded.original_name,
            mime_type=uploaded.mime_type,
            size_bytes=uploaded.size_bytes,
            visibility=visibility,  # type: ignore[arg-type]
            created_at=uploaded.uploaded_at,
        )

    def upload_to_catalog(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        data: bytes,
        actor_id: uuid.UUID,
        uploaded_org_unit_id: str | None,
        access_level: str = ACCESS_PRIVATE,
    ) -> AnnouncementAttachmentLibraryItem:
        """Upload into the announcement catalog without linking an announcement."""
        level = (access_level or ACCESS_PRIVATE).upper()
        if level not in (ACCESS_PUBLIC, ACCESS_PRIVATE):
            raise ValidationAppError(m("attachment.invalid_access_level"))

        uploaded = self._attachments.upload(
            aggregate_type=AggregateType.ANNOUNCEMENT.value,
            aggregate_id=ANNOUNCEMENT_CATALOG_AGGREGATE_ID,
            filename=filename,
            content_type=content_type,
            data=data,
            uploaded_by=actor_id,
            commit=False,
        )
        session = self._require_session()
        orm = session.get(AttachmentORM, uploaded.id)
        if orm is None:
            raise NotFoundError(m("attachment.not_found"))
        orm.access_level = level
        orm.uploaded_org_unit_id = uploaded_org_unit_id
        session.commit()

        return AnnouncementAttachmentLibraryItem(
            id=uploaded.id,
            file_name=uploaded.original_name,
            mime_type=uploaded.mime_type,
            size_bytes=uploaded.size_bytes,
            created_at=uploaded.uploaded_at,
            access_level=level,  # type: ignore[arg-type]
            uploaded_org_unit_id=uploaded_org_unit_id,
            uploaded_by=actor_id,
            uploaded_by_name=_user_display_name(session, actor_id),
            usage_count=0,
        )

    def link(
        self,
        announcement_id: uuid.UUID,
        *,
        attachment_id: uuid.UUID,
        visibility: str,
        actor_id: uuid.UUID,
        principal: Principal | None = None,
    ) -> AnnouncementAttachmentResponse:
        """Create a join to an existing announcement-domain attachment (no copy)."""
        if self._announcements.get(announcement_id) is None:
            raise NotFoundError(m("announcement.not_found"))

        try:
            platform = self._attachments.get(attachment_id)
        except NotFoundError:
            raise NotFoundError(m("attachment.not_found")) from None

        if platform.status == AttachmentStatus.DELETED.value:
            raise NotFoundError(m("attachment.not_found"))

        if not self._join_repo.is_announcement_domain_attachment(attachment_id):
            raise ValidationAppError(m("attachment.not_announcement_domain"))

        session = self._require_session()
        if principal is not None and not can_view_catalog_attachment(
            principal=principal, session=session, attachment=platform
        ):
            raise PermissionDeniedError(m("common.forbidden"))

        if self._join_repo.get(announcement_id, attachment_id) is not None:
            raise ConflictError(m("attachment.already_linked_announcement"))

        join = self._join_repo.create(
            announcement_id=announcement_id,
            attachment_id=attachment_id,
            visibility=visibility,
            created_by=actor_id,
        )

        ann = self._announcements.get(announcement_id)
        if ann is not None and announcement_is_currently_active(
            status=ann.status, start_at=ann.start_at, end_at=ann.end_at
        ):
            mark_attachment_public(session, attachment_id)

        self._join_repo.commit()
        return AnnouncementAttachmentResponse(
            id=platform.id,
            file_name=platform.original_name,
            mime_type=platform.mime_type,
            size_bytes=platform.size_bytes,
            visibility=visibility,  # type: ignore[arg-type]
            created_at=join.created_at or platform.uploaded_at,
        )

    def list_library(
        self,
        *,
        principal: Principal,
        q: str | None = None,
        exclude_announcement_id: uuid.UUID | None = None,
        include_orphans: bool = True,
        org_scope: str = "all",
    ) -> list[AnnouncementAttachmentLibraryItem]:
        """Catalog / picker — access rules, then optional orgScope narrow.

        orgScope (does not widen Private visibility):
          - all — authorized set (own unit + Public shares)
          - pusat — stamped Pusat-class units only
          - cabang — caller's own unit; Pusat callers see all non-Pusat
        """
        scope = (org_scope or "all").strip().lower()
        if scope not in ("all", "pusat", "cabang"):
            raise ValidationAppError(m("attachment.invalid_org_scope"))

        session = self._require_session()
        caller_org = resolve_caller_org_unit(principal, session)
        pusat_caller = caller_is_pusat(principal, session) or is_pusat_unit(caller_org)

        rows = self._join_repo.list_reusable(
            q=q,
            exclude_announcement_id=exclude_announcement_id,
            include_orphans=include_orphans,
        )
        items: list[AnnouncementAttachmentLibraryItem] = []
        for row in rows:
            platform = self._attachments.get(row.id)
            platform.access_level = row.access_level
            platform.uploaded_org_unit_id = row.uploaded_org_unit_id
            if not can_view_catalog_attachment(
                principal=principal, session=session, attachment=platform
            ):
                continue
            # Sticky may have updated ORM — refresh access on the row view.
            refreshed = apply_sticky_public_if_active(
                session=session, attachment=platform
            )
            row.access_level = refreshed.access_level

            if scope != "all":
                uploaded_org = resolve_attachment_org_unit(session, refreshed)
                if scope == "pusat":
                    if not is_pusat_unit(uploaded_org):
                        continue
                elif pusat_caller:
                    if is_pusat_unit(uploaded_org):
                        continue
                else:
                    if not (
                        uploaded_org
                        and caller_org
                        and uploaded_org == caller_org
                    ):
                        continue

            items.append(_library_item_from_row(row))
        session.commit()
        return items

    def update_access_level(
        self,
        attachment_id: uuid.UUID,
        *,
        access_level: str,
        principal: Principal,
    ) -> AnnouncementAttachmentLibraryItem:
        level = access_level.upper()
        if level not in (ACCESS_PUBLIC, ACCESS_PRIVATE):
            raise ValidationAppError(m("attachment.invalid_access_level"))
        if not self._join_repo.is_announcement_domain_attachment(attachment_id):
            # Orphan announcement aggregate still allowed.
            try:
                platform = self._attachments.get(attachment_id)
            except NotFoundError:
                raise NotFoundError(m("attachment.not_found")) from None
            if platform.aggregate_type != AggregateType.ANNOUNCEMENT.value:
                raise ValidationAppError(m("attachment.not_announcement_domain"))
        else:
            platform = self._attachments.get(attachment_id)

        session = self._require_session()
        if not can_change_access_level(
            principal=principal, session=session, attachment=platform
        ):
            raise PermissionDeniedError(m("common.forbidden"))

        orm = session.get(AttachmentORM, attachment_id)
        if orm is None:
            raise NotFoundError(m("attachment.not_found"))
        orm.access_level = level
        session.commit()

        usage = self._join_repo.count_for_attachment(attachment_id)
        return AnnouncementAttachmentLibraryItem(
            id=platform.id,
            file_name=platform.original_name,
            mime_type=platform.mime_type,
            size_bytes=platform.size_bytes,
            created_at=platform.uploaded_at,
            access_level=level,  # type: ignore[arg-type]
            uploaded_org_unit_id=orm.uploaded_org_unit_id,
            uploaded_by=platform.uploaded_by,
            uploaded_by_name=_user_display_name(session, platform.uploaded_by),
            usage_count=usage,
        )

    def delete_from_catalog(
        self,
        attachment_id: uuid.UUID,
        *,
        principal: Principal,
    ) -> None:
        """Remove from catalog: drop joins + soft-delete platform row."""
        try:
            platform = self._attachments.get(attachment_id)
        except NotFoundError:
            raise NotFoundError(m("attachment.not_found")) from None
        if not self._join_repo.is_announcement_domain_attachment(
            attachment_id
        ) and platform.aggregate_type != AggregateType.ANNOUNCEMENT.value:
            raise ValidationAppError(m("attachment.not_announcement_domain"))

        session = self._require_session()
        if not can_delete_from_catalog(
            principal=principal, session=session, attachment=platform
        ):
            raise PermissionDeniedError(m("common.forbidden"))

        self._join_repo.delete_all_joins_for_attachment(attachment_id)
        self._attachments.soft_delete(attachment_id, commit=False)
        self._join_repo.commit()

    def remove(
        self,
        announcement_id: uuid.UUID,
        attachment_id: uuid.UUID,
    ) -> None:
        """Unlink from one announcement — keep file in catalog."""
        join = self._join_repo.get(announcement_id, attachment_id)
        if join is None:
            raise NotFoundError(m("attachment.not_found"))
        self._join_repo.delete(join)
        self._join_repo.commit()

    def mark_public_for_announcement(self, announcement_id: uuid.UUID) -> None:
        """Sticky PUBLIC for every attachment linked to an active announcement."""
        session = self._require_session()
        rows = self._join_repo.list_for_announcement(announcement_id)
        for row in rows:
            mark_attachment_public(session, row.attachment_id)
        session.flush()

    def update_visibility(
        self,
        announcement_id: uuid.UUID,
        attachment_id: uuid.UUID,
        *,
        visibility: str,
        actor_id: uuid.UUID,
    ) -> AnnouncementAttachmentResponse:
        join = self._join_repo.get(announcement_id, attachment_id)
        if join is None:
            raise NotFoundError(m("attachment.not_found"))
        self._join_repo.update_visibility(join, visibility=visibility, updated_by=actor_id)
        self._join_repo.commit()
        attachment = self._attachments.get(attachment_id)
        return AnnouncementAttachmentResponse(
            id=attachment.id,
            file_name=attachment.original_name,
            mime_type=attachment.mime_type,
            size_bytes=attachment.size_bytes,
            visibility=join.visibility,  # type: ignore[arg-type]
            created_at=join.created_at,
        )

    def list_for_management(
        self, announcement_id: uuid.UUID
    ) -> list[AnnouncementAttachmentResponse]:
        rows = self._join_repo.list_for_announcement(announcement_id)
        return [_row_to_response(r) for r in rows]

    def list_visible(
        self, announcement_id: uuid.UUID, *, announcement_status: str
    ) -> list[AnnouncementAttachmentResponse]:
        rows = self._join_repo.list_for_announcement(announcement_id)
        return [
            _row_to_response(r)
            for r in rows
            if is_visible_to_reader(
                visibility=r.visibility, announcement_status=announcement_status
            )
        ]

    def bulk_for_management(
        self, announcement_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[AnnouncementAttachmentResponse]]:
        by_id = self._join_repo.list_for_announcements(announcement_ids)
        return {
            aid: [_row_to_response(r) for r in rows] for aid, rows in by_id.items()
        }

    def bulk_visible(
        self, announcements: list[tuple[uuid.UUID, str]]
    ) -> dict[uuid.UUID, list[AnnouncementAttachmentResponse]]:
        ids = [aid for aid, _ in announcements]
        by_id = self._join_repo.list_for_announcements(ids)
        result: dict[uuid.UUID, list[AnnouncementAttachmentResponse]] = {}
        for aid, status in announcements:
            rows = by_id.get(aid, [])
            result[aid] = [
                _row_to_response(r)
                for r in rows
                if is_visible_to_reader(visibility=r.visibility, announcement_status=status)
            ]
        return result
