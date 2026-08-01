"""System Settings service — typed get/set with value_type validation (TASK-028)."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

from app.core.enums import SettingValueType
from app.core.errors import NotFoundError, ValidationAppError
from app.core.user_messages import m
from app.modules.settings.models import Setting
from app.modules.settings.registry import SettingsKey
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.schemas import SettingResponse, SettingUpdateRequest

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
_TRUE_VALUES = frozenset({"true", "1", "yes", "on"})
_FALSE_VALUES = frozenset({"false", "0", "no", "off"})


def _normalize_bool_storage(raw: str) -> str:
    token = raw.strip().lower()
    if token in _TRUE_VALUES:
        return "true"
    if token in _FALSE_VALUES:
        return "false"
    raise ValidationAppError(
        m("config.value_boolean"),
        details={"value": raw},
    )


def _validate_and_normalize(value: str, value_type: str) -> str:
    """Validate raw input against value_type; return canonical storage string."""
    vt = value_type.upper()

    if vt == SettingValueType.STRING:
        return value

    if vt == SettingValueType.INTEGER:
        cleaned = value.strip()
        try:
            int(cleaned)
        except ValueError as exc:
            raise ValidationAppError(
                m("config.value_integer"),
                details={"value": value},
            ) from exc
        return cleaned

    if vt == SettingValueType.BOOLEAN:
        return _normalize_bool_storage(value)

    if vt == SettingValueType.JSON:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValidationAppError(
                m("config.value_json"),
                details={"value": value, "error": str(exc)},
            ) from exc
        return json.dumps(parsed, separators=(",", ":"), ensure_ascii=False)

    if vt == SettingValueType.URL:
        cleaned = value.strip()
        if cleaned == "":
            return ""
        parsed = urlparse(cleaned)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValidationAppError(
                m("config.value_http_url"),
                details={"value": value},
            )
        return cleaned

    if vt == SettingValueType.EMAIL:
        cleaned = value.strip()
        if cleaned == "":
            return ""
        if not _EMAIL_RE.match(cleaned):
            raise ValidationAppError(
                m("config.value_email"),
                details={"value": value},
            )
        return cleaned

    raise ValidationAppError(
        f"value_type tidak didukung: {value_type}",
        details={"valueType": value_type},
    )


def _to_response(row: Setting) -> SettingResponse:
    return SettingResponse.model_validate(row)


class SettingsService:
    """Sole configuration read/write path for application settings."""

    def __init__(self, repository: SettingsRepository) -> None:
        self._repo = repository

    def list_all(self) -> list[SettingResponse]:
        return [_to_response(row) for row in self._repo.list_all()]

    def list_public(self) -> list[SettingResponse]:
        return [_to_response(row) for row in self._repo.list_public()]

    def get(self, key: str | SettingsKey) -> SettingResponse:
        row = self._require(key)
        return _to_response(row)

    def get_string(self, key: str | SettingsKey, *, default: str | None = None) -> str:
        row = self._repo.get_by_key(str(key))
        if row is None:
            if default is not None:
                return default
            raise NotFoundError(f"Pengaturan tidak ditemukan: {key}")
        return row.value

    def get_int(self, key: str | SettingsKey, *, default: int | None = None) -> int:
        row = self._repo.get_by_key(str(key))
        if row is None:
            if default is not None:
                return default
            raise NotFoundError(f"Pengaturan tidak ditemukan: {key}")
        try:
            return int(row.value.strip())
        except ValueError as exc:
            raise ValidationAppError(
                f"pengaturan {key} bukan bilangan bulat",
                details={"key": str(key), "value": row.value},
            ) from exc

    def get_bool(self, key: str | SettingsKey, *, default: bool | None = None) -> bool:
        row = self._repo.get_by_key(str(key))
        if row is None:
            if default is not None:
                return default
            raise NotFoundError(f"Pengaturan tidak ditemukan: {key}")
        token = row.value.strip().lower()
        if token in _TRUE_VALUES:
            return True
        if token in _FALSE_VALUES:
            return False
        raise ValidationAppError(
            f"pengaturan {key} bukan boolean",
            details={"key": str(key), "value": row.value},
        )

    def get_json(
        self, key: str | SettingsKey, *, default: Any | None = None
    ) -> Any:
        row = self._repo.get_by_key(str(key))
        if row is None:
            if default is not None:
                return default
            raise NotFoundError(f"Pengaturan tidak ditemukan: {key}")
        try:
            return json.loads(row.value)
        except json.JSONDecodeError as exc:
            raise ValidationAppError(
                f"pengaturan {key} bukan JSON valid",
                details={"key": str(key), "value": row.value},
            ) from exc

    def set(self, key: str | SettingsKey, value: str) -> SettingResponse:
        row = self._require(key)
        normalized = _validate_and_normalize(value, row.value_type)
        updated = self._repo.update_value(row, value=normalized)
        self._repo.commit()
        return _to_response(updated)

    def update(self, key: str, payload: SettingUpdateRequest) -> SettingResponse:
        return self.set(key, payload.value)

    def _require(self, key: str | SettingsKey) -> Setting:
        row = self._repo.get_by_key(str(key))
        if row is None:
            raise NotFoundError(f"Pengaturan tidak ditemukan: {key}")
        return row
