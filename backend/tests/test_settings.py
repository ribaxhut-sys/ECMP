"""System Settings unit/service tests (TASK-028)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import SettingValueType, SettingVisibility
from app.core.errors import NotFoundError, ValidationAppError
from app.modules.settings.registry import SettingsKey
from app.modules.settings.schemas import SettingUpdateRequest
from app.modules.settings.service import SettingsService


def _row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "key": SettingsKey.COMPANY_NAME.value,
        "value": "ECMP",
        "value_type": SettingValueType.STRING.value,
        "category": "company",
        "visibility": SettingVisibility.PUBLIC.value,
        "description": "Company name",
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_get_returns_setting() -> None:
    row = _row()
    repo = MagicMock()
    repo.get_by_key.return_value = row

    result = SettingsService(repo).get(SettingsKey.COMPANY_NAME)

    assert result.key == "company.name"
    assert result.value == "ECMP"
    repo.get_by_key.assert_called_once_with("company.name")


def test_get_missing_raises_not_found() -> None:
    repo = MagicMock()
    repo.get_by_key.return_value = None

    with pytest.raises(NotFoundError):
        SettingsService(repo).get("missing.key")


def test_get_string_and_int_and_bool_and_json() -> None:
    repo = MagicMock()
    repo.get_by_key.side_effect = [
        _row(key="app.language.default", value="id"),
        _row(
            key="dashboard.recent.limit",
            value="10",
            value_type=SettingValueType.INTEGER.value,
        ),
        _row(key="feature.enabled", value="true", value_type=SettingValueType.BOOLEAN.value),
        _row(key="meta", value='{"a":1}', value_type=SettingValueType.JSON.value),
    ]
    svc = SettingsService(repo)

    assert svc.get_string("app.language.default") == "id"
    assert svc.get_int("dashboard.recent.limit") == 10
    assert svc.get_bool("feature.enabled") is True
    assert svc.get_json("meta") == {"a": 1}


def test_get_with_default_when_missing() -> None:
    repo = MagicMock()
    repo.get_by_key.return_value = None
    svc = SettingsService(repo)

    assert svc.get_string("x", default="fallback") == "fallback"
    assert svc.get_int("x", default=7) == 7
    assert svc.get_bool("x", default=False) is False
    assert svc.get_json("x", default=[]) == []


def test_set_validates_integer() -> None:
    row = _row(
        key="dashboard.recent.limit",
        value="10",
        value_type=SettingValueType.INTEGER.value,
    )
    repo = MagicMock()
    repo.get_by_key.return_value = row
    repo.update_value.return_value = _row(
        key="dashboard.recent.limit",
        value="5",
        value_type=SettingValueType.INTEGER.value,
    )

    result = SettingsService(repo).set("dashboard.recent.limit", "5")

    assert result.value == "5"
    repo.update_value.assert_called_once()
    repo.commit.assert_called_once()


def test_set_rejects_invalid_integer() -> None:
    row = _row(
        key="dashboard.recent.limit",
        value="10",
        value_type=SettingValueType.INTEGER.value,
    )
    repo = MagicMock()
    repo.get_by_key.return_value = row

    with pytest.raises(ValidationAppError):
        SettingsService(repo).set("dashboard.recent.limit", "abc")
    repo.commit.assert_not_called()


def test_set_validates_boolean_url_email_json() -> None:
    repo = MagicMock()

    bool_row = _row(key="flag", value="false", value_type=SettingValueType.BOOLEAN.value)
    repo.get_by_key.return_value = bool_row
    repo.update_value.return_value = bool_row
    SettingsService(repo).set("flag", "YES")
    assert repo.update_value.call_args.kwargs["value"] == "true"

    url_row = _row(key="company.logo", value="", value_type=SettingValueType.URL.value)
    repo.get_by_key.return_value = url_row
    repo.update_value.return_value = url_row
    SettingsService(repo).set("company.logo", "https://cdn.example.com/logo.png")

    with pytest.raises(ValidationAppError):
        SettingsService(repo).set("company.logo", "not-a-url")

    email_row = _row(
        key="support.email",
        value="",
        value_type=SettingValueType.EMAIL.value,
    )
    repo.get_by_key.return_value = email_row
    repo.update_value.return_value = email_row
    SettingsService(repo).set("support.email", "ops@example.com")

    with pytest.raises(ValidationAppError):
        SettingsService(repo).set("support.email", "bad@@")

    json_row = _row(key="meta", value="{}", value_type=SettingValueType.JSON.value)
    repo.get_by_key.return_value = json_row
    repo.update_value.return_value = json_row
    SettingsService(repo).set("meta", '{"x": 1}')

    with pytest.raises(ValidationAppError):
        SettingsService(repo).set("meta", "{bad")


def test_update_uses_request_payload() -> None:
    row = _row()
    repo = MagicMock()
    repo.get_by_key.return_value = row
    repo.update_value.return_value = _row(value="Acme Corp")

    result = SettingsService(repo).update(
        "company.name",
        SettingUpdateRequest(value="Acme Corp"),
    )

    assert result.value == "Acme Corp"


def test_list_public_and_all() -> None:
    public = _row()
    protected = _row(
        key="dashboard.recent.limit",
        visibility=SettingVisibility.PROTECTED.value,
        value_type=SettingValueType.INTEGER.value,
        value="10",
    )
    repo = MagicMock()
    repo.list_public.return_value = [public]
    repo.list_all.return_value = [public, protected]
    svc = SettingsService(repo)

    assert len(svc.list_public()) == 1
    assert len(svc.list_all()) == 2
