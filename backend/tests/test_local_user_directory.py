"""Mode A LocalUserDirectory adapter unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.integrations.directory.local_adapter import LocalUserDirectory
from app.models import User


def test_display_names_skips_non_uuid_and_empty_set() -> None:
    session = MagicMock()
    adapter = LocalUserDirectory(session)
    assert adapter.display_names(set()) == {}
    assert adapter.display_names({"system", "job-runner", "not-uuid"}) == {}
    session.scalars.assert_not_called()


def test_display_names_maps_full_name_or_username() -> None:
    uid = uuid.uuid4()
    uid2 = uuid.uuid4()
    row_named = MagicMock(spec=User)
    row_named.id = uid
    row_named.full_name = "  Agent One  "
    row_named.username = "a1"
    row_named.deleted_at = None

    row_username = MagicMock(spec=User)
    row_username.id = uid2
    row_username.full_name = "   "
    row_username.username = "agent-two"
    row_username.deleted_at = None

    session = MagicMock()
    session.scalars.return_value.all.return_value = [row_named, row_username]
    adapter = LocalUserDirectory(session)

    out = adapter.display_names({str(uid), str(uid2), "ignore-me"})
    assert out[str(uid)] == "Agent One"
    assert out[str(uid2)] == "agent-two"


def test_display_names_omits_blank_names() -> None:
    uid = uuid.uuid4()
    row = MagicMock(spec=User)
    row.id = uid
    row.full_name = ""
    row.username = None
    row.deleted_at = datetime.now(UTC)

    session = MagicMock()
    session.scalars.return_value.all.return_value = [row]
    adapter = LocalUserDirectory(session)
    assert adapter.display_names({str(uid)}) == {}
