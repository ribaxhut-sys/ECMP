"""Announcement application-service unit tests (mocked repository).

Mirrors tests/test_sla_policy.py — pure service-layer coverage, no DB.
Authorization-matrix / API-level coverage lives in test_announcement_api.py.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import InvalidStateError, NotFoundError, ValidationAppError
from app.modules.announcement.schemas import (
    AnnouncementCreateRequest,
    AnnouncementUpdateRequest,
)
from app.modules.announcement.service import AnnouncementService


def _row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "reference_number": "PGM-2608-0001",
        "title": "Pemeliharaan sistem",
        "body": "Sistem akan pemeliharaan pukul 22:00.",
        "priority": "NORMAL",
        "status": "DRAFT",
        "start_at": None,
        "end_at": None,
        "published_at": None,
        "published_by": None,
        "created_by": uuid.uuid4(),
        "created_at": now,
        "updated_by": None,
        "updated_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _create_payload(**overrides: object) -> AnnouncementCreateRequest:
    body = {
        "title": "Pemeliharaan sistem",
        "body": "Sistem akan pemeliharaan pukul 22:00.",
        "priority": "NORMAL",
    }
    body.update(overrides)
    return AnnouncementCreateRequest.model_validate(body)


def _update_payload(**overrides: object) -> AnnouncementUpdateRequest:
    body = {
        "title": "Judul diperbarui",
        "body": "Isi diperbarui.",
        "priority": "IMPORTANT",
    }
    body.update(overrides)
    return AnnouncementUpdateRequest.model_validate(body)


def test_create_always_starts_draft() -> None:
    created = _row(status="DRAFT")
    repo = MagicMock()
    repo.create.return_value = created

    result = AnnouncementService(repo).create(
        _create_payload(), actor_id=created.created_by
    )

    assert result.status == "DRAFT"
    assert result.effective_status == "DRAFT"
    repo.create.assert_called_once()
    repo.commit.assert_called_once()


def test_update_allowed_regardless_of_status() -> None:
    """No approval workflow — editing a PUBLISHED item must not be blocked."""
    row = _row(status="PUBLISHED")
    repo = MagicMock()
    repo.get.return_value = row

    def _apply(r: SimpleNamespace, **kwargs: object) -> SimpleNamespace:
        for key in ("title", "body", "priority", "end_at"):
            setattr(r, key, kwargs[key])
        return r

    repo.update_fields.side_effect = _apply

    result = AnnouncementService(repo).update(
        row.id, _update_payload(), actor_id=uuid.uuid4()
    )

    assert result.title == "Judul diperbarui"
    assert result.status == "PUBLISHED"
    repo.commit.assert_called_once()
    assert repo.update_fields.call_args.kwargs["update_start_at"] is False


def test_update_can_reschedule_start_at() -> None:
    future = datetime.now(UTC) + timedelta(days=3)
    row = _row(status="PUBLISHED", start_at=datetime.now(UTC) + timedelta(days=1))
    repo = MagicMock()
    repo.get.return_value = row

    def _apply(r: SimpleNamespace, **kwargs: object) -> SimpleNamespace:
        for key in ("title", "body", "priority", "end_at"):
            setattr(r, key, kwargs[key])
        if kwargs.get("update_start_at"):
            r.start_at = kwargs["start_at"]
        return r

    repo.update_fields.side_effect = _apply

    result = AnnouncementService(repo).update(
        row.id,
        _update_payload(startAt=future.isoformat()),
        actor_id=uuid.uuid4(),
    )

    assert result.start_at == future
    assert result.effective_status == "SCHEDULED"
    assert repo.update_fields.call_args.kwargs["update_start_at"] is True
    assert repo.update_fields.call_args.kwargs["start_at"] == future


def test_update_rejects_start_at_not_before_end_at() -> None:
    end = datetime.now(UTC) + timedelta(days=1)
    row = _row(status="PUBLISHED", end_at=end)
    repo = MagicMock()
    repo.get.return_value = row

    with pytest.raises(ValidationAppError):
        AnnouncementService(repo).update(
            row.id,
            _update_payload(
                startAt=(end + timedelta(hours=1)).isoformat(),
                endAt=end.isoformat(),
            ),
            actor_id=uuid.uuid4(),
        )

    repo.update_fields.assert_not_called()


def test_update_not_found() -> None:
    repo = MagicMock()
    repo.get.return_value = None

    with pytest.raises(NotFoundError):
        AnnouncementService(repo).update(
            uuid.uuid4(), _update_payload(), actor_id=uuid.uuid4()
        )


def test_publish_sets_start_at_and_published_fields() -> None:
    row = _row(status="DRAFT")
    repo = MagicMock()
    repo.get.return_value = row
    actor = uuid.uuid4()

    def _publish(
        r: SimpleNamespace,
        *,
        published_by: uuid.UUID,
        start_at=None,
        now=None,
    ):
        when = now or datetime.now(UTC)
        r.status = "PUBLISHED"
        r.start_at = start_at if start_at is not None else when
        r.published_at = when
        r.published_by = published_by
        return r

    repo.publish.side_effect = _publish

    result = AnnouncementService(repo).publish(row.id, actor_id=actor)

    assert result.status == "PUBLISHED"
    assert result.effective_status == "PUBLISHED"
    assert result.start_at is not None
    assert result.published_at is not None
    assert result.published_by == actor
    repo.publish.assert_called_once()
    assert repo.publish.call_args.kwargs.get("start_at") is None
    repo.commit.assert_called_once()


def test_publish_with_future_start_at_is_scheduled() -> None:
    now = datetime.now(UTC)
    future = now + timedelta(days=2)
    row = _row(status="DRAFT")
    repo = MagicMock()
    repo.get.return_value = row
    actor = uuid.uuid4()

    def _publish(
        r: SimpleNamespace,
        *,
        published_by: uuid.UUID,
        start_at=None,
        now=None,
    ):
        when = now or datetime.now(UTC)
        r.status = "PUBLISHED"
        r.start_at = start_at if start_at is not None else when
        r.published_at = when
        r.published_by = published_by
        return r

    repo.publish.side_effect = _publish

    result = AnnouncementService(repo).publish(
        row.id, actor_id=actor, start_at=future
    )

    assert result.status == "PUBLISHED"
    assert result.effective_status == "SCHEDULED"
    assert result.start_at == future
    assert result.published_at is not None
    assert result.published_at < future
    assert repo.publish.call_args.kwargs["start_at"] == future


def test_publish_rejects_start_at_not_before_end_at() -> None:
    now = datetime.now(UTC)
    row = _row(status="DRAFT", end_at=now + timedelta(days=1))
    repo = MagicMock()
    repo.get.return_value = row

    with pytest.raises(ValidationAppError):
        AnnouncementService(repo).publish(
            row.id,
            actor_id=uuid.uuid4(),
            start_at=now + timedelta(days=2),
        )
    repo.publish.assert_not_called()


def test_publish_not_found() -> None:
    repo = MagicMock()
    repo.get.return_value = None

    with pytest.raises(NotFoundError):
        AnnouncementService(repo).publish(uuid.uuid4(), actor_id=uuid.uuid4())


def test_unpublish_requires_published_status() -> None:
    row = _row(status="DRAFT")
    repo = MagicMock()
    repo.get.return_value = row

    with pytest.raises(InvalidStateError):
        AnnouncementService(repo).unpublish(row.id, actor_id=uuid.uuid4())
    repo.unpublish.assert_not_called()


def test_unpublish_archives_published_announcement() -> None:
    row = _row(status="PUBLISHED")
    repo = MagicMock()
    repo.get.return_value = row

    def _archive(r: SimpleNamespace, **kwargs: object) -> SimpleNamespace:
        r.status = "ARCHIVED"
        return r

    repo.unpublish.side_effect = _archive

    result = AnnouncementService(repo).unpublish(row.id, actor_id=uuid.uuid4())

    assert result.status == "ARCHIVED"
    repo.commit.assert_called_once()


def test_delete_soft_deletes_and_not_found() -> None:
    row = _row()
    repo = MagicMock()
    repo.get.return_value = row

    AnnouncementService(repo).delete(row.id, actor_id=uuid.uuid4())
    repo.soft_delete.assert_called_once()
    repo.commit.assert_called_once()

    repo.get.return_value = None
    with pytest.raises(NotFoundError):
        AnnouncementService(repo).delete(uuid.uuid4(), actor_id=uuid.uuid4())


def test_list_active_delegates_to_repository() -> None:
    repo = MagicMock()
    repo.list_active.return_value = []

    AnnouncementService(repo).list_active()

    repo.list_active.assert_called_once()


def test_effective_status_expired_when_end_at_elapsed() -> None:
    now = datetime.now(UTC)
    row = _row(
        status="PUBLISHED",
        start_at=now - timedelta(days=2),
        end_at=now - timedelta(days=1),
        published_at=now - timedelta(days=2),
    )
    repo = MagicMock()
    repo.list_all.return_value = [row]

    result = AnnouncementService(repo).list_for_management()

    assert result[0].status == "PUBLISHED"
    assert result[0].effective_status == "EXPIRED"


def test_effective_status_scheduled_when_start_at_in_future() -> None:
    now = datetime.now(UTC)
    row = _row(
        status="PUBLISHED",
        start_at=now + timedelta(days=1),
        end_at=now + timedelta(days=7),
        published_at=now - timedelta(hours=1),
    )
    repo = MagicMock()
    repo.list_all.return_value = [row]

    result = AnnouncementService(repo).list_for_management()

    assert result[0].status == "PUBLISHED"
    assert result[0].effective_status == "SCHEDULED"


def test_effective_status_published_when_window_open() -> None:
    now = datetime.now(UTC)
    row = _row(
        status="PUBLISHED",
        start_at=now - timedelta(hours=1),
        end_at=now + timedelta(days=1),
        published_at=now - timedelta(hours=1),
    )
    repo = MagicMock()
    repo.list_all.return_value = [row]

    result = AnnouncementService(repo).list_for_management()

    assert result[0].effective_status == "PUBLISHED"


def test_effective_status_published_when_end_at_in_future() -> None:
    now = datetime.now(UTC)
    row = _row(
        status="PUBLISHED",
        start_at=now - timedelta(hours=1),
        end_at=now + timedelta(days=1),
        published_at=now - timedelta(hours=1),
    )
    repo = MagicMock()
    repo.list_all.return_value = [row]

    result = AnnouncementService(repo).list_for_management()

    assert result[0].effective_status == "PUBLISHED"


def test_effective_status_draft_unaffected_by_end_at() -> None:
    now = datetime.now(UTC)
    row = _row(status="DRAFT", end_at=now - timedelta(days=1))
    repo = MagicMock()
    repo.list_all.return_value = [row]

    result = AnnouncementService(repo).list_for_management()

    assert result[0].effective_status == "DRAFT"


# --- Unread count + per-caller read-state (mocked repo) -------------------


def test_count_unread_active_delegates_to_repository() -> None:
    repo = MagicMock()
    repo.count_unread_active.return_value = 2
    user_id = uuid.uuid4()

    result = AnnouncementService(repo).count_unread_active(user_id=user_id)

    assert result == 2
    args, kwargs = repo.count_unread_active.call_args
    assert kwargs["user_id"] == user_id


def test_mark_read_rejects_missing_announcement() -> None:
    repo = MagicMock()
    repo.get.return_value = None

    with pytest.raises(NotFoundError):
        AnnouncementService(repo).mark_read(uuid.uuid4(), user_id=uuid.uuid4())

    repo.mark_read.assert_not_called()


def test_mark_read_rejects_draft() -> None:
    row = _row(status="DRAFT")
    repo = MagicMock()
    repo.get.return_value = row

    with pytest.raises(NotFoundError):
        AnnouncementService(repo).mark_read(row.id, user_id=uuid.uuid4())

    repo.mark_read.assert_not_called()


def test_mark_read_rejects_scheduled() -> None:
    now = datetime.now(UTC)
    row = _row(
        status="PUBLISHED",
        start_at=now + timedelta(days=2),
        published_at=now,
    )
    repo = MagicMock()
    repo.get.return_value = row

    with pytest.raises(NotFoundError):
        AnnouncementService(repo).mark_read(row.id, user_id=uuid.uuid4())

    repo.mark_read.assert_not_called()


def test_get_for_reader_rejects_scheduled() -> None:
    now = datetime.now(UTC)
    row = _row(
        status="PUBLISHED",
        start_at=now + timedelta(days=2),
        published_at=now,
    )
    repo = MagicMock()
    repo.get.return_value = row

    with pytest.raises(NotFoundError):
        AnnouncementService(repo).get_for_reader(row.id)


def test_list_history_passes_now_to_repository() -> None:
    repo = MagicMock()
    repo.list_history.return_value = []
    repo.list_read_ids.return_value = set()
    user_id = uuid.uuid4()

    AnnouncementService(repo).list_history(user_id=user_id)

    repo.list_history.assert_called_once()
    assert "now" in repo.list_history.call_args.kwargs
    repo.list_read_ids.assert_called_once_with(user_id=user_id, announcement_ids=[])


def test_mark_read_delegates_for_published_announcement() -> None:
    row = _row(status="PUBLISHED")
    repo = MagicMock()
    repo.get.return_value = row
    user_id = uuid.uuid4()

    AnnouncementService(repo).mark_read(row.id, user_id=user_id)

    repo.mark_read.assert_called_once_with(announcement_id=row.id, user_id=user_id)
    repo.commit.assert_called_once()
