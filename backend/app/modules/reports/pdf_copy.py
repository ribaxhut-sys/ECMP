"""Operator-facing PDF copy for API-546 (id / en)."""

from __future__ import annotations

from app.modules.reports.schemas import ReportPrintCategory


def normalize_report_lang(value: str | None) -> str:
    raw = (value or "id").strip().lower().replace("_", "-")
    if raw == "en" or raw.startswith("en-"):
        return "en"
    return "id"


_ID: dict[str, str] = {
    "internal": "DOKUMEN INTERNAL",
    "title": "Laporan Pengaduan",
    "identity": "Identitas",
    "summary": "Ringkasan",
    "status_now": "Status saat ini",
    "cycle_time": "Umur penyelesaian",
    "category": "Kategori",
    "period": "Periode",
    "date_range": "Rentang tanggal",
    "unit": "Unit",
    "downloaded": "Diunduh",
    "status": "Status",
    "count": "Jumlah",
    "all_units": "Semua unit",
    "unbounded": "Tidak dibatasi",
    "page": "Halaman",
    "footer_title": "Laporan Pengaduan",
    "unit_complaint": "pengaduan",
    "unit_case": "kasus",
    "unit_day": "hari",
    "kpi_created": "Total dibuat",
    "kpi_resolved": "Diselesaikan",
    "kpi_escalated": "Dieskalasi ke Pusat",
    "kpi_in_progress": "Masih diproses",
    "kpi_created_long": "Total pengaduan dibuat",
    "kpi_resolved_long": "Total pengaduan diselesaikan",
    "kpi_escalated_long": "Total pengaduan dieskalasi ke Pusat",
    "note_all": (
        "Masih diproses termasuk dikembalikan ke cabang — pengaduan "
        "masih berjalan. Dieskalasi hanya yang masih di jalur Pusat. "
        "Diselesaikan memakai tanggal penutupan; yang lain memakai "
        "tanggal pengaduan dibuat."
    ),
    "note_resolved": "Dihitung dari tanggal penutupan, bukan tanggal pengaduan dibuat.",
    "note_escalated": (
        "Hanya pengaduan yang masih di jalur Pusat "
        "(menunggu persetujuan, disetujui, atau terjadwal kunjungan)."
    ),
    "note_other": (
        "Kategori ini menunggu definisi status baru dan belum memiliki "
        "data. Laporan akan terisi begitu status tersebut ditambahkan "
        "ke domain pengaduan."
    ),
    "cycle_closed": "Kasus ditutup pada periode ini",
    "cycle_average": "Rata-rata waktu penyelesaian",
    "cycle_median": "Median waktu penyelesaian",
    "cycle_p90": "Persentil 90",
    "cycle_fastest": "Tercepat",
    "cycle_slowest": "Terlama",
    "cycle_empty": "Tidak ada kasus ditutup pada rentang tanggal ini.",
    "cycle_note": (
        "Diukur dari kasus dibuat sampai ditutup, dalam hari, pada jendela "
        "tanggal penutupan."
    ),
    "status_in_progress": "Diproses",
    "status_closed": "Ditutup",
    "band_same_day": "Sampai 1 hari",
    "band_up_to_3": "Lebih dari 1 sampai 3 hari",
    "band_up_to_7": "Lebih dari 3 sampai 7 hari",
    "band_over_7": "Lebih dari 7 hari",
    "cat_all": "Semua Pengaduan",
    "cat_created": "Pengaduan Dibuat",
    "cat_resolved": "Pengaduan Diselesaikan",
    "cat_escalated": "Pengaduan Dieskalasi",
    "cat_other": "Lainnya",
    "briefing": (
        "{closed} diselesaikan dari {total} pengaduan. "
        "{open} masih diproses."
    ),
    "briefing_escalated": " {escalated} di jalur Pusat.",
    "briefing_empty": "Belum ada pengaduan pada periode ini.",
    "vs_previous": "Vs periode sebelumnya",
    "cases_share": "{count} kasus ({share}%)",
    "user_activity": "Aktivitas petugas",
    "user_activity_name": "Petugas",
    "user_activity_unit": "Unit",
    "user_activity_created": "Dibuat",
    "user_activity_decided": "Diputus",
    "user_activity_closed": "Ditutup",
    "user_activity_events": "Aktivitas",
    "user_activity_empty": "Belum ada aktivitas petugas pada periode ini.",
    "user_activity_truncated": "Menampilkan {shown} dari {total} petugas dengan aktivitas.",
    "user_activity_note": (
        "Dibuat = pengaduan didaftarkan. Diputus = keputusan eskalasi. "
        "Ditutup = kasus ditutup. Aktivitas = peristiwa riwayat pada pengaduan."
    ),
}

_EN: dict[str, str] = {
    "internal": "INTERNAL DOCUMENT",
    "title": "Complaint Report",
    "identity": "Identity",
    "summary": "Summary",
    "status_now": "Current status",
    "cycle_time": "Cycle time",
    "category": "Category",
    "period": "Period",
    "date_range": "Date range",
    "unit": "Unit",
    "downloaded": "Downloaded",
    "status": "Status",
    "count": "Count",
    "all_units": "All units",
    "unbounded": "Not limited",
    "page": "Page",
    "footer_title": "Complaint Report",
    "unit_complaint": "complaints",
    "unit_case": "cases",
    "unit_day": "days",
    "kpi_created": "Total created",
    "kpi_resolved": "Resolved",
    "kpi_escalated": "Escalated to HQ",
    "kpi_in_progress": "Still in progress",
    "kpi_created_long": "Total complaints created",
    "kpi_resolved_long": "Total complaints resolved",
    "kpi_escalated_long": "Total complaints escalated to HQ",
    "note_all": (
        "Still in progress includes returned-to-branch — the complaint is "
        "still open. Escalated covers only the live HQ path. Resolved uses "
        "the closure date; other counts use the created date."
    ),
    "note_resolved": "Counted from the closure date, not the created date.",
    "note_escalated": (
        "Only complaints still on the HQ path "
        "(pending approval, approved, or scheduled for a visit)."
    ),
    "note_other": (
        "This category is waiting for a new status definition and has no "
        "data yet. The report will fill in once that status is added to "
        "the complaint domain."
    ),
    "cycle_closed": "Cases closed in this period",
    "cycle_average": "Average time to close",
    "cycle_median": "Median time to close",
    "cycle_p90": "90th percentile",
    "cycle_fastest": "Fastest",
    "cycle_slowest": "Slowest",
    "cycle_empty": "No cases were closed in this date range.",
    "cycle_note": (
        "Measured from case created to closed, in days, on the closure-date "
        "window."
    ),
    "status_in_progress": "In progress",
    "status_closed": "Closed",
    "band_same_day": "Up to 1 day",
    "band_up_to_3": "More than 1 up to 3 days",
    "band_up_to_7": "More than 3 up to 7 days",
    "band_over_7": "Over 7 days",
    "cat_all": "All Complaints",
    "cat_created": "Complaints Created",
    "cat_resolved": "Complaints Resolved",
    "cat_escalated": "Complaints Escalated",
    "cat_other": "Other",
    "briefing": "{closed} resolved out of {total} complaints. {open} still in progress.",
    "briefing_escalated": " {escalated} on the HQ path.",
    "briefing_empty": "No complaints in this period.",
    "vs_previous": "Vs previous period",
    "cases_share": "{count} cases ({share}%)",
    "user_activity": "Officer activity",
    "user_activity_name": "Officer",
    "user_activity_unit": "Unit",
    "user_activity_created": "Created",
    "user_activity_decided": "Decided",
    "user_activity_closed": "Closed",
    "user_activity_events": "Activity",
    "user_activity_empty": "No officer activity in this period.",
    "user_activity_truncated": "Showing {shown} of {total} officers with activity.",
    "user_activity_note": (
        "Created = complaints registered. Decided = escalation decisions. "
        "Closed = cases closed. Activity = complaint history events."
    ),
}

_COPY: dict[str, dict[str, str]] = {"id": _ID, "en": _EN}

_CATEGORY_KEY: dict[ReportPrintCategory, str] = {
    ReportPrintCategory.ALL: "cat_all",
    ReportPrintCategory.CREATED: "cat_created",
    ReportPrintCategory.RESOLVED: "cat_resolved",
    ReportPrintCategory.ESCALATED: "cat_escalated",
    ReportPrintCategory.OTHER: "cat_other",
}


def copy_for(lang: str | None) -> dict[str, str]:
    return _COPY[normalize_report_lang(lang)]


def category_title(category: ReportPrintCategory, lang: str | None) -> str:
    return copy_for(lang)[_CATEGORY_KEY[category]]
