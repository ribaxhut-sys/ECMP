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
    HQ_SCHEDULE_START = "hq.schedule.start"
    HQ_SCHEDULE_END = "hq.schedule.end"
    HQ_SCHEDULE_SLOT_MINUTES = "hq.schedule.slot_minutes"
    HQ_SCHEDULE_CAPACITY_PER_SLOT = "hq.schedule.capacity_per_slot"
    HQ_SCHEDULE_WORKDAYS = "hq.schedule.workdays"
    HQ_SCHEDULE_BREAK_START = "hq.schedule.break_start"
    HQ_SCHEDULE_BREAK_END = "hq.schedule.break_end"
    INTERNAL_COMPLAINT_CANCEL_REASON_PRESETS = "internal_complaint.cancel_reason_presets"
    INTERNAL_COMPLAINT_TRANSFER_REASON_PRESETS = "internal_complaint.transfer_reason_presets"
    INTERNAL_COMPLAINT_REQUEST_TRANSFER_REASON_PRESETS = (
        "internal_complaint.request_transfer_reason_presets"
    )
    INTERNAL_COMPLAINT_TRANSFER_DECISION_REASON_PRESETS = (
        "internal_complaint.transfer_decision_reason_presets"
    )
    INTERNAL_COMPLAINT_COMPLETION_RETURN_REASON_PRESETS = (
        "internal_complaint.completion_return_reason_presets"
    )
    INTERNAL_COMPLAINT_RESEND_TO_PUSAT_NOTE_PRESETS = (
        "internal_complaint.resend_to_pusat_note_presets"
    )


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
    SettingDefinition(
        key=SettingsKey.HQ_SCHEDULE_START,
        value="08:00",
        value_type=SettingValueType.STRING,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description="HQ arrival schedule opening time (HH:MM)",
    ),
    SettingDefinition(
        key=SettingsKey.HQ_SCHEDULE_END,
        value="16:00",
        value_type=SettingValueType.STRING,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description="HQ arrival schedule closing time (HH:MM)",
    ),
    SettingDefinition(
        key=SettingsKey.HQ_SCHEDULE_SLOT_MINUTES,
        value="60",
        value_type=SettingValueType.INTEGER,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description="HQ arrival schedule slot length in minutes",
    ),
    SettingDefinition(
        key=SettingsKey.HQ_SCHEDULE_CAPACITY_PER_SLOT,
        value="2",
        value_type=SettingValueType.INTEGER,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description="Max taxpayer arrivals accommodated per HQ schedule slot",
    ),
    SettingDefinition(
        key=SettingsKey.HQ_SCHEDULE_WORKDAYS,
        value="1,2,3,4,5",
        value_type=SettingValueType.STRING,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description="ISO weekdays (1=Mon..7=Sun) HQ accepts arrivals, comma-separated",
    ),
    SettingDefinition(
        key=SettingsKey.HQ_SCHEDULE_BREAK_START,
        value="12:00",
        value_type=SettingValueType.STRING,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description="HQ arrival schedule lunch break start (HH:MM)",
    ),
    SettingDefinition(
        key=SettingsKey.HQ_SCHEDULE_BREAK_END,
        value="13:00",
        value_type=SettingValueType.STRING,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description="HQ arrival schedule lunch break end (HH:MM)",
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_CANCEL_REASON_PRESETS,
        value='["Duplikat","Input salah","Pembatalan wajib pajak"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill reason presets shown in the internal complaint cancel dialog",
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_TRANSFER_REASON_PRESETS,
        value='["Salah unit","Perlu keahlian khusus","Beban kerja unit tujuan lebih sesuai"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill reason presets shown in the internal complaint transfer dialog",
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_REQUEST_TRANSFER_REASON_PRESETS,
        value='["Di luar kewenangan unit","Perlu koordinasi lintas unit"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill reason presets for requesting an internal complaint transfer"
        ),
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_TRANSFER_DECISION_REASON_PRESETS,
        value='["Alasan tidak jelas","Dokumen pendukung kurang"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill reason presets for approving/rejecting an internal complaint "
            "transfer request"
        ),
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_COMPLETION_RETURN_REASON_PRESETS,
        value='["Dokumen kurang","Perlu verifikasi ulang","Data tidak sesuai"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill reason presets for returning an internal complaint for completion"
        ),
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_RESEND_TO_PUSAT_NOTE_PRESETS,
        value='["Dokumen sudah dilengkapi","Sudah diverifikasi ulang","Data sudah disesuaikan"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill note presets shown when a branch resends an internal complaint to HQ"
        ),
    ),
)
