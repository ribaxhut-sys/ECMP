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
    HQ_SCHEDULE_BREAK_OVERRIDES = "hq.schedule.break_overrides"
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
    INTERNAL_COMPLAINT_WITHDRAW_DECISION_REASON_PRESETS = (
        "internal_complaint.withdraw_decision_reason_presets"
    )
    INTERNAL_COMPLAINT_REJECT_PROPOSAL_REASON_PRESETS = (
        "internal_complaint.reject_proposal_reason_presets"
    )
    INTERNAL_COMPLAINT_RESOLUTION_COMMENT_PRESETS = (
        "internal_complaint.resolution_comment_presets"
    )
    INTERNAL_COMPLAINT_ACCEPTANCE_NOTE_PRESETS = (
        "internal_complaint.acceptance_note_presets"
    )
    CASE_CLOSE_NOTE_PRESETS = "case.close_note_presets"
    CASE_CANCEL_REASON_PRESETS = "case.cancel_reason_presets"
    CASE_RESOLUTION_COMMENT_PRESETS = "case.resolution_comment_presets"
    CASE_REJECTION_REASON_PRESETS = "case.rejection_reason_presets"
    CM_B1_APPROVE_ESCALATION_NOTE_PRESETS = "cm_batch1.approve_escalation_note_presets"
    CM_B1_REJECT_ESCALATION_NOTE_PRESETS = "cm_batch1.reject_escalation_note_presets"
    CM_B1_CANCEL_ESCALATION_NOTE_PRESETS = "cm_batch1.cancel_escalation_note_presets"
    CM_B1_RERUN_ESCALATION_REASON_PRESETS = (
        "cm_batch1.rerequest_escalation_reason_presets"
    )
    CM_B1_HQ_ACCEPT_SCHEDULE_NOTE_PRESETS = "cm_batch1.hq_accept_schedule_note_presets"
    CM_B1_HQ_RETURN_NOTE_PRESETS = "cm_batch1.hq_return_note_presets"
    CM_B1_HQ_ARRIVAL_NOTE_PRESETS = "cm_batch1.hq_arrival_note_presets"
    CM_B1_HQ_COMPLETE_NOTE_PRESETS = "cm_batch1.hq_complete_note_presets"
    CM_B1_INTAKE_CASE_NOTE_PRESETS = "cm_batch1.intake_case_note_presets"


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
        key=SettingsKey.HQ_SCHEDULE_BREAK_OVERRIDES,
        value='{"5": {"start": "11:30", "end": "13:30"}}',
        value_type=SettingValueType.JSON,
        category="hq_schedule",
        visibility=SettingVisibility.PROTECTED,
        description=(
            "Per-weekday break windows overriding break_start/break_end "
            '(ISO weekday key, null = no break); Jumat defaults to 11:30-13:30'
        ),
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
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_WITHDRAW_DECISION_REASON_PRESETS,
        value='["Alasan penarikan tidak jelas","Pengaduan masih perlu ditindaklanjuti"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill reason presets for approving/rejecting an internal complaint "
            "withdraw request"
        ),
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_REJECT_PROPOSAL_REASON_PRESETS,
        value='["Penyelesaian belum sesuai","Bukti pendukung kurang","Perlu penjelasan tambahan"]',
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill reason presets for rejecting an internal complaint resolution proposal"
        ),
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_RESOLUTION_COMMENT_PRESETS,
        value=(
            '["Sudah ditindaklanjuti sesuai SOP","Sudah dikoordinasikan dengan unit terkait",'
            '"Selesai, tidak ada tindak lanjut tambahan"]'
        ),
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill comment presets for the internal complaint resolution dialog"
        ),
    ),
    SettingDefinition(
        key=SettingsKey.INTERNAL_COMPLAINT_ACCEPTANCE_NOTE_PRESETS,
        value=(
            '["Diterima untuk ditindaklanjuti","Bukan kewenangan unit ini",'
            '"Perlu dilengkapi terlebih dahulu"]'
        ),
        value_type=SettingValueType.JSON,
        category="internal_complaint",
        visibility=SettingVisibility.PUBLIC,
        description=(
            "Quick-fill note presets for accepting or returning an internal complaint"
        ),
    ),
    SettingDefinition(
        key=SettingsKey.CASE_CLOSE_NOTE_PRESETS,
        value=(
            '["Kasus selesai ditangani","Ditutup atas persetujuan pelapor",'
            '"Ditutup, tidak ada tindak lanjut tambahan"]'
        ),
        value_type=SettingValueType.JSON,
        category="case",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets shown in the case close dialog",
    ),
    SettingDefinition(
        key=SettingsKey.CASE_CANCEL_REASON_PRESETS,
        value='["Duplikat","Input salah","Permintaan dibatalkan pelapor"]',
        value_type=SettingValueType.JSON,
        category="case",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill reason presets shown when a case is cancelled",
    ),
    SettingDefinition(
        key=SettingsKey.CASE_RESOLUTION_COMMENT_PRESETS,
        value=(
            '["Sudah ditindaklanjuti sesuai SOP","Sudah dikoordinasikan dengan unit terkait",'
            '"Selesai, pelapor sudah diinformasikan"]'
        ),
        value_type=SettingValueType.JSON,
        category="case",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill comment presets shown in the case resolve dialog",
    ),
    SettingDefinition(
        key=SettingsKey.CASE_REJECTION_REASON_PRESETS,
        value=(
            '["Penyelesaian belum sesuai","Bukti pendukung kurang",'
            '"Perlu penjelasan tambahan"]'
        ),
        value_type=SettingValueType.JSON,
        category="case",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill reason presets shown when a case resolution is rejected",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_APPROVE_ESCALATION_NOTE_PRESETS,
        value=(
            '["Sesuai kewenangan Pusat","Perlu penanganan Pusat",'
            '"Eskalasi disetujui sesuai SOP"]'
        ),
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets for approving an intake escalation",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_REJECT_ESCALATION_NOTE_PRESETS,
        value=(
            '["Masih dapat ditangani cabang",'
            '"Alasan eskalasi kurang jelas","Dokumen pendukung belum lengkap"]'
        ),
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets for rejecting an intake escalation",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_CANCEL_ESCALATION_NOTE_PRESETS,
        value='["Diselesaikan di cabang","Eskalasi tidak jadi diperlukan","Diajukan keliru"]',
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets for cancelling an intake escalation",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_RERUN_ESCALATION_REASON_PRESETS,
        value=(
            '["Dokumen sudah dilengkapi","Ada informasi baru",'
            '"Kondisi berubah, tetap perlu Pusat"]'
        ),
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill reason presets for re-requesting an intake escalation",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_HQ_ACCEPT_SCHEDULE_NOTE_PRESETS,
        value='["Dijadwalkan sesuai ketersediaan","Wajib pajak diminta hadir sesuai jadwal"]',
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets when HQ accepts and schedules a visit",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_HQ_RETURN_NOTE_PRESETS,
        value='["Dokumen kurang","Perlu verifikasi ulang cabang","Bukan kewenangan Pusat"]',
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets when HQ returns a complaint to the branch",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_HQ_ARRIVAL_NOTE_PRESETS,
        value='["Wajib pajak dijadwalkan hadir","Perubahan jadwal atas permintaan wajib pajak"]',
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets for the HQ arrival schedule note",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_HQ_COMPLETE_NOTE_PRESETS,
        value=(
            '["Kunjungan selesai, tidak ada tindak lanjut",'
            '"Selesai, hasil sudah disampaikan","Selesai sesuai SOP"]'
        ),
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets when HQ completes a visit",
    ),
    SettingDefinition(
        key=SettingsKey.CM_B1_INTAKE_CASE_NOTE_PRESETS,
        value=(
            '["Perlu penanganan lanjutan unit","Sesuai kategori layanan",'
            '"Dilanjutkan sesuai SOP"]'
        ),
        value_type=SettingValueType.JSON,
        category="cm_batch1",
        visibility=SettingVisibility.PUBLIC,
        description="Quick-fill note presets for the per-case note on intake escalation",
    ),
)
