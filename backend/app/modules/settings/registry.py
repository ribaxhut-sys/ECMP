"""Settings key registry and default seed definitions (TASK-028)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.core.enums import SettingValueType, SettingVisibility


class SettingsKey(StrEnum):
    """Canonical setting keys (dot-notation)."""

    COMPANY_NAME = "company.name"
    COMPANY_LOGO = "company.logo"
    APP_LANGUAGE = "app.language.default"
    APP_TIMEZONE = "app.timezone"
    DASHBOARD_RECENT_LIMIT = "dashboard.recent.limit"
    COMPLAINT_NUMBER_PREFIX = "complaint.number.prefix"


@dataclass(frozen=True, slots=True)
class SettingDefinition:
    key: SettingsKey
    value: str
    value_type: SettingValueType
    category: str
    visibility: SettingVisibility
    description: str | None = None


DEFAULT_SETTINGS: tuple[SettingDefinition, ...] = (
    SettingDefinition(
        key=SettingsKey.COMPANY_NAME,
        value="ECMP",
        value_type=SettingValueType.STRING,
        category="company",
        visibility=SettingVisibility.PUBLIC,
        description="Company / product display name",
    ),
    SettingDefinition(
        key=SettingsKey.COMPANY_LOGO,
        value="",
        value_type=SettingValueType.URL,
        category="company",
        visibility=SettingVisibility.PUBLIC,
        description="Company logo URL (empty until configured)",
    ),
    SettingDefinition(
        key=SettingsKey.APP_LANGUAGE,
        value="id",
        value_type=SettingValueType.STRING,
        category="app",
        visibility=SettingVisibility.PUBLIC,
        description="Default application language code",
    ),
    SettingDefinition(
        key=SettingsKey.APP_TIMEZONE,
        value="Asia/Jakarta",
        value_type=SettingValueType.STRING,
        category="app",
        visibility=SettingVisibility.PUBLIC,
        description="Default application timezone (IANA)",
    ),
    SettingDefinition(
        key=SettingsKey.DASHBOARD_RECENT_LIMIT,
        value="10",
        value_type=SettingValueType.INTEGER,
        category="dashboard",
        visibility=SettingVisibility.PROTECTED,
        description="Max recent activity items on dashboard summary",
    ),
    SettingDefinition(
        key=SettingsKey.COMPLAINT_NUMBER_PREFIX,
        value="CMP",
        value_type=SettingValueType.STRING,
        category="complaint",
        visibility=SettingVisibility.PROTECTED,
        description="Prefix for generated complaint numbers",
    ),
)
