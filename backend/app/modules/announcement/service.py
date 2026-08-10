"""Announcement application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.errors import InvalidStateError, NotFoundError, ValidationAppError
from app.core.user_messages import m
from app.modules.announcement.attachment_service import AnnouncementAttachmentService
from app.modules.announcement.repository import (
    AnnouncementRepository,
    is_scheduled_announcement,
)
from app.modules.announcement.schemas import (
    AnnouncementAttachmentResponse,
    AnnouncementCreateRequest,
    AnnouncementResponse,
    AnnouncementUpdateRequest,
)

ANNOUNCEMENT_NOT_FOUND_MESSAGE = m("announcement.not_found")
ANNOUNCEMENT_NOT_PUBLISHED_MESSAGE = m("announcement.not_published")


def _effective_status(
    status: str,
    start_at: datetime | None,
    end_at: datetime | None,
    *,
    now: datetime,
) -> str:
    """Derived display status — never stored (DEC: no scheduler).

    SCHEDULED = PUBLISHED with start_at in the future.
    EXPIRED = PUBLISHED whose end_at has elapsed.
    """
    if status == "DRAFT":
        return "DRAFT"
    if status == "PUBLISHED":
        if start_at is not None and start_at > now:
            return "SCHEDULED"
        if end_at is not None and end_at <= now:
            return "EXPIRED"
        return "PUBLISHED"
    return status


def _to_response(
    row: object,
    *,
    now: datetime | None = None,
    attachments: list[AnnouncementAttachmentResponse] = (),  # type: ignore[assignment]
) -> AnnouncementResponse:
    when = now or datetime.now(UTC)
    attachment_list = list(attachments)
    return AnnouncementResponse(
        id=row.id,  # type: ignore[attr-defined]
        reference_number=row.reference_number,  # type: ignore[attr-defined]
        title=row.title,  # type: ignore[attr-defined]
        body=row.body,  # type: ignore[attr-defined]
        priority=row.priority,  # type: ignore[attr-defined]
        status=row.status,  # type: ignore[attr-defined]
        effective_status=_effective_status(
            row.status,  # type: ignore[attr-defined]
            row.start_at,  # type: ignore[attr-defined]
            row.end_at,  # type: ignore[attr-defined]
            now=when,
        ),
        start_at=row.start_at,  # type: ignore[attr-defined]
        end_at=row.end_at,  # type: ignore[attr-defined]
        published_at=row.published_at,  # type: ignore[attr-defined]
        published_by=row.published_by,  # type: ignore[attr-defined]
        created_by=row.created_by,  # type: ignore[attr-defined]
        created_at=row.created_at,  # type: ignore[attr-defined]
        updated_by=row.updated_by,  # type: ignore[attr-defined]
        updated_at=row.updated_at,  # type: ignore[attr-defined]
        attachments=attachment_list,
        attachment_count=len(attachment_list),
    )


class AnnouncementService:
    def __init__(
        self,
        repository: AnnouncementRepository,
        attachments: AnnouncementAttachmentService | None = None,
    ) -> None:
        self._repo = repository
        self._attachments = attachments

    # --- Management (announcement:manage) ---

    def list_for_management(self) -> list[AnnouncementResponse]:
        now = datetime.now(UTC)
        rows = self._repo.list_all()
        attachments_by_id = (
            self._attachments.bulk_for_management([r.id for r in rows])
            if self._attachments is not None
            else {}
        )
        return [
            _to_response(row, now=now, attachments=attachments_by_id.get(row.id, []))
            for row in rows
        ]

    def get_for_management(self, announcement_id: uuid.UUID) -> AnnouncementResponse:
        """Detail view for the 3 manage roles — every attachment, any visibility."""
        row = self._repo.get(announcement_id)
        if row is None:
            raise NotFoundError(ANNOUNCEMENT_NOT_FOUND_MESSAGE)
        attachments = (
            self._attachments.list_for_management(announcement_id)
            if self._attachments is not None
            else []
        )
        return _to_response(row, attachments=attachments)

    def get_for_reader(self, announcement_id: uuid.UUID) -> AnnouncementResponse:
        """Detail view for any announcement:read holder — visibility-filtered.

        DRAFT and SCHEDULED never leak to a reader, even with a known UUID.
        Published-past-end_at stays open (effectiveStatus reads EXPIRED).
        """
        now = datetime.now(UTC)
        row = self._repo.get(announcement_id)
        if (
            row is None
            or row.status == "DRAFT"
            or is_scheduled_announcement(row.status, row.start_at, now=now)
        ):
            raise NotFoundError(ANNOUNCEMENT_NOT_FOUND_MESSAGE)
        attachments = (
            self._attachments.list_visible(
                announcement_id, announcement_status=row.status
            )
            if self._attachments is not None
            else []
        )
        return _to_response(row, now=now, attachments=attachments)

    def create(
        self,
        payload: AnnouncementCreateRequest,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> AnnouncementResponse:
        """Always creates DRAFT — publishing is a separate, explicit action."""
        row = self._repo.create(
            title=payload.title,
            body=payload.body,
            priority=payload.priority,
            end_at=payload.end_at,
            created_by=actor_id,
        )
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_response(row)

    def update(
        self,
        announcement_id: uuid.UUID,
        payload: AnnouncementUpdateRequest,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> AnnouncementResponse:
        """No approval workflow — editable regardless of current status."""
        row = self._repo.get(announcement_id)
        if row is None:
            raise NotFoundError(ANNOUNCEMENT_NOT_FOUND_MESSAGE)
        update_start_at = "start_at" in payload.model_fields_set
        next_start = payload.start_at if update_start_at else row.start_at
        next_end = payload.end_at
        if (
            next_start is not None
            and next_end is not None
            and next_start >= next_end
        ):
            raise ValidationAppError(m("validation.end_after_start"))
        row = self._repo.update_fields(
            row,
            title=payload.title,
            body=payload.body,
            priority=payload.priority,
            end_at=payload.end_at,
            start_at=payload.start_at if update_start_at else None,
            update_start_at=update_start_at,
            updated_by=actor_id,
        )
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_response(row)

    def publish(
        self,
        announcement_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        start_at: datetime | None = None,
        commit: bool = True,
    ) -> AnnouncementResponse:
        """Direct publish — no approval step (business decision, LOCKED).

        ``start_at is None`` → publish now (start_at := now).
        Future ``start_at`` → DB status PUBLISHED, visibility delayed until
        that instant (read-time; DEC: no scheduler).
        """
        row = self._repo.get(announcement_id)
        if row is None:
            raise NotFoundError(ANNOUNCEMENT_NOT_FOUND_MESSAGE)
        if (
            start_at is not None
            and row.end_at is not None
            and start_at >= row.end_at
        ):
            raise ValidationAppError(m("validation.end_after_start"))
        row = self._repo.publish(row, published_by=actor_id, start_at=start_at)
        # Sticky PUBLIC when the announcement is active immediately (not scheduled).
        if self._attachments is not None and not is_scheduled_announcement(
            row.status, row.start_at
        ):
            self._attachments.mark_public_for_announcement(announcement_id)
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_response(row)

    def unpublish(
        self,
        announcement_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> AnnouncementResponse:
        row = self._repo.get(announcement_id)
        if row is None:
            raise NotFoundError(ANNOUNCEMENT_NOT_FOUND_MESSAGE)
        if row.status != "PUBLISHED":
            raise InvalidStateError(ANNOUNCEMENT_NOT_PUBLISHED_MESSAGE)
        row = self._repo.unpublish(row, updated_by=actor_id)
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return _to_response(row)

    def delete(
        self,
        announcement_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> None:
        row = self._repo.get(announcement_id)
        if row is None:
            raise NotFoundError(ANNOUNCEMENT_NOT_FOUND_MESSAGE)
        self._repo.soft_delete(row, deleted_by=actor_id)
        if commit:
            self._repo.commit()

    # --- Public / landing (announcement:read) ---

    def list_active(self) -> list[AnnouncementResponse]:
        """PUBLISHED + in-window. Global for every announcement:read holder —
        announcements have no audience/target (business decision, LOCKED)."""
        now = datetime.now(UTC)
        rows = self._repo.list_active(now=now)
        attachments_by_id = (
            self._attachments.bulk_visible([(r.id, r.status) for r in rows])
            if self._attachments is not None
            else {}
        )
        return [
            _to_response(row, now=now, attachments=attachments_by_id.get(row.id, []))
            for row in rows
        ]

    def has_unread_active(self, *, user_id: uuid.UUID) -> bool:
        """Post-login entry-point gate — same "active" definition as
        list_active, plus "no read record for this user yet"."""
        return self._repo.has_unread_active(user_id=user_id)

    def mark_read(
        self, announcement_id: uuid.UUID, *, user_id: uuid.UUID, commit: bool = True
    ) -> None:
        """Reader marks an announcement as read — same visibility gate as
        get_for_reader (DRAFT/deleted/missing all 404; a reader can never
        mark-read something they could not otherwise open). ``user_id``
        always comes from the authenticated Principal, never the request
        body (§15)."""
        now = datetime.now(UTC)
        row = self._repo.get(announcement_id)
        if (
            row is None
            or row.status == "DRAFT"
            or is_scheduled_announcement(row.status, row.start_at, now=now)
        ):
            raise NotFoundError(ANNOUNCEMENT_NOT_FOUND_MESSAGE)
        self._repo.mark_read(announcement_id=announcement_id, user_id=user_id)
        if commit:
            self._repo.commit()

    def list_history(self) -> list[AnnouncementResponse]:
        """Reader archive — PUBLISHED (incl. EXPIRED) + ARCHIVED.

        DRAFT and SCHEDULED are excluded. Unlike /active, expired (past end_at)
        remains visible — this is "what has already been visible", not "active now".
        """
        now = datetime.now(UTC)
        rows = self._repo.list_history(now=now)
        attachments_by_id = (
            self._attachments.bulk_visible([(r.id, r.status) for r in rows])
            if self._attachments is not None
            else {}
        )
        return [
            _to_response(row, now=now, attachments=attachments_by_id.get(row.id, []))
            for row in rows
        ]
