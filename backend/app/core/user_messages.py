"""Pesan user-facing Bahasa Indonesia untuk envelope error API ECMP.

Hanya berisi teks yang ditampilkan ke pengguna/operator. Untuk pesan generik
berbasis kode error, utamakan ``code_message(code)`` dari ``CODE_DEFAULTS``.
Pesan bisnis, auth, dan validasi spesifik domain gunakan ``m(key)``.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

CODE_DEFAULTS: dict[str, str] = {
    "UNAUTHENTICATED": "Autentikasi diperlukan.",
    "FORBIDDEN": "Anda tidak memiliki izin untuk tindakan ini.",
    "DATA_SCOPE_DENIED": "Akses data ditolak karena di luar cakupan wewenang Anda.",
    "ORG_SCOPE_DENIED": "Akses ditolak karena di luar cakupan organisasi Anda.",
    "NOT_FOUND": "Sumber daya tidak ditemukan.",
    "VALIDATION_ERROR": "Validasi permintaan gagal.",
    "INVALID_STATE": "Tindakan tidak diizinkan pada status sumber daya saat ini.",
    "CONFLICT": "Terjadi konflik data.",
    "RATE_LIMITED": "Terlalu banyak percobaan. Coba lagi nanti.",
    "INTERNAL_ERROR": "Terjadi kesalahan pada server.",
    "METHOD_NOT_ALLOWED": "Metode HTTP tidak diizinkan.",
    "HTTP_ERROR": "Permintaan gagal.",
    "PASSWORD_CHANGE_REQUIRED": "Anda harus mengubah kata sandi sebelum mengakses aplikasi.",
}

MESSAGES: dict[str, str] = {
    # --- Auth ---
    "auth.authentication_required": "Autentikasi diperlukan.",
    "auth.bearer_required": "Token Bearer diperlukan.",
    "auth.current_password_incorrect": "Kata sandi saat ini tidak benar.",
    "auth.invalid_credentials": "Nama pengguna atau kata sandi tidak valid.",
    "auth.invalid_refresh": "Token refresh tidak valid atau sudah kedaluwarsa.",
    "auth.invalid_reset_token": "Token reset tidak valid atau sudah kedaluwarsa.",
    "auth.invalid_token": "Token tidak valid atau sudah kedaluwarsa.",
    "auth.local_disabled": "Autentikasi kredensial lokal dinonaktifkan.",
    "auth.password_blank": "Kata sandi tidak boleh kosong.",
    "auth.password_change_required": ("Anda harus mengubah kata sandi sebelum mengakses aplikasi."),
    "auth.password_changed": "Kata sandi berhasil diubah.",
    "auth.password_must_differ": "Kata sandi baru harus berbeda dari kata sandi saat ini.",
    "auth.password_reset_ok": "Kata sandi berhasil direset.",
    "auth.password_whitespace": "Kata sandi tidak boleh diawali atau diakhiri spasi.",
    "auth.rate_limited_login": "Terlalu banyak percobaan masuk. Coba lagi nanti.",
    "auth.refresh_required": "Token refresh diperlukan.",
    "auth.token_missing_subject": "Token tidak memiliki subjek.",
    "auth.token_subject_must_be_uuid": "Subjek token harus berupa UUID.",
    "auth.unauthenticated": "Autentikasi diperlukan.",
    # --- Common / HTTP ---
    "common.forbidden": "Anda tidak memiliki izin untuk tindakan ini.",
    "common.data_scope_denied": "Akses data ditolak karena di luar cakupan wewenang Anda.",
    "common.idempotency_key_required": "Request Id (Idempotency-Key) diperlukan.",
    "common.internal_error": "Terjadi kesalahan pada server.",
    "common.invalid_status_transition": "Transisi status tidak valid.",
    "common.not_found": "Sumber daya tidak ditemukan.",
    "common.org_scope_denied": "Akses ditolak karena di luar cakupan organisasi Anda.",
    "common.rate_limited": "Terlalu banyak percobaan. Coba lagi nanti.",
    "common.request_failed": "Permintaan gagal.",
    "common.unsupported_source_type": "sourceType tidak didukung.",
    "common.unsupported_target_type": "targetType tidak didukung.",
    "common.validation_failed": "Validasi permintaan gagal.",
    # --- Organization scope ---
    "org.scope_missing_org_unit_claim": (
        "Akses ditolak karena di luar cakupan organisasi Anda: klaim orgUnitId tidak ditemukan."
    ),
    "org.scope_resource_no_org_unit": (
        "Akses ditolak karena di luar cakupan organisasi Anda: "
        "sumber daya tidak memiliki unit organisasi."
    ),
    # --- User ---
    "user.email_exists": "Alamat email sudah digunakan.",
    "user.not_found": "Pengguna tidak ditemukan.",
    "user.username_exists": "Nama pengguna sudah digunakan.",
    "user.branch_required_for_role": (
        "Cabang wajib diisi untuk peran operasional cabang "
        "(agen, petugas cabang, supervisor, atau manager cabang)."
    ),
    "user.branch_forbidden_for_role": (
        "Cabang tidak boleh diisi untuk peran kantor pusat."
    ),
    "user.only_head_office_admin_status": (
        "Hanya Admin Pusat yang dapat mengaktifkan atau menonaktifkan pengguna."
    ),
    # --- Branch ---
    "branch.not_found": "Cabang tidak ditemukan.",
    "branch.not_found_or_inactive": "Cabang tidak ditemukan atau tidak aktif.",
    # --- IAM ---
    "iam.cannot_assign_role": "Anda tidak diizinkan menetapkan peran ini.",
    "iam.data_scope_exists": "Cakupan data sudah ada untuk peran ini.",
    "iam.data_scope_not_found": "Cakupan data tidak ditemukan.",
    "iam.permission_already_assigned": "Izin sudah ditetapkan ke peran.",
    "iam.permission_not_found": "Izin tidak ditemukan.",
    "iam.permissions_not_found": "Satu atau lebih izin tidak ditemukan.",
    "iam.role_already_assigned": "Peran sudah ditetapkan ke pengguna.",
    "iam.role_not_found": "Peran tidak ditemukan.",
    "iam.role_not_found_or_inactive": "Peran tidak ditemukan atau tidak aktif.",
    "iam.role_permission_not_found": "Tautan peran-izin tidak ditemukan.",
    "iam.roles_not_found": "Satu atau lebih peran tidak ditemukan.",
    "iam.system_permission_cannot_delete": "Izin sistem tidak dapat dihapus.",
    "iam.system_role_cannot_delete": "Peran sistem tidak dapat dihapus.",
    "iam.user_role_not_found": "Tautan pengguna-peran tidak ditemukan.",
    # --- Customer ---
    "customer.exactly_one_key_type": "Tepat satu tipe kunci pelanggan harus disediakan.",
    "customer.search_key_empty": "Masukkan kunci pencarian.",
    "customer.search_name_too_short": "Nama terlalu pendek — minimal 3 karakter.",
    "customer.search_id_too_short": "ID terlalu pendek — minimal 8 digit.",
    "customer.search_phone_too_short": "Nomor telepon terlalu pendek — minimal 10 digit.",
    "customer.id_must_be_confirmed": (
        "CustomerId harus dikonfirmasi/dikunci untuk aktor ini sebelum pembuatan."
    ),
    "customer.master_unavailable_create_rejected": (
        "Master Customer tidak tersedia (mode Strict) — pembuatan ditolak."
    ),
    "customer.master_unavailable_strict": "Master Customer tidak tersedia (mode Strict).",
    "customer.master_writeback_forbidden": (
        "Write-back ke Customer Master dilarang (ADR-002 / BR-002)."
    ),
    "customer.not_found": "Pelanggan tidak ditemukan.",
    "customer.not_in_master": "Pelanggan tidak ditemukan di Master Customer.",
    "customer.search_blocked_enumeration": (
        "Pencarian pelanggan sementara diblokir oleh perlindungan enumerasi."
    ),
    # --- Complaint ---
    "complaint.already_closed": "Pengaduan sudah berstatus CLOSED.",
    "complaint.already_has_escalation": "Pengaduan sudah memiliki eskalasi aktif.",
    "complaint.already_has_sla": "Pengaduan sudah memiliki catatan SLA.",
    "complaint.cannot_assign_status": "Pengaduan tidak dapat ditugaskan pada status saat ini.",
    "complaint.cannot_delete_with_sla": (
        "Pengaduan tidak dapat dihapus selama catatan SLA masih ada."
    ),
    "complaint.cannot_escalate_status": "Pengaduan tidak dapat dieskalasi pada status saat ini.",
    "complaint.closer_not_found": "Penutup pengaduan tidak ditemukan atau tidak aktif.",
    "complaint.final_resolution_required_close": (
        "Resolusi Akhir harus ada sebelum menutup pengaduan."
    ),
    "complaint.has_resolution_cannot_escalate": (
        "Pengaduan sudah memiliki resolusi dan tidak dapat dieskalasi."
    ),
    "complaint.invalid_route": "Rute pengaduan tidak valid.",
    "complaint.must_be_in_progress_close": (
        "Pengaduan harus berstatus IN_PROGRESS sebelum ditutup."
    ),
    "complaint.must_be_in_progress_escalation": (
        "Pengaduan harus berstatus IN_PROGRESS sebelum meminta eskalasi."
    ),
    "complaint.must_be_in_progress_final": (
        "Pengaduan harus berstatus IN_PROGRESS sebelum mengirim Resolusi Akhir."
    ),
    "complaint.must_be_in_progress_resolve": (
        "Pengaduan harus berstatus IN_PROGRESS sebelum diselesaikan."
    ),
    "complaint.not_found": "Pengaduan tidak ditemukan.",
    "complaint.only_supervisor_admin_close": (
        "Hanya Supervisor, Manager, atau Head Office Admin yang dapat menutup pengaduan."
    ),
    "complaint.only_supervisor_assign": (
        "Hanya Supervisor atau Manager yang dapat menugaskan pengaduan."
    ),
    "complaint.only_supervisor_escalate": (
        "Hanya Supervisor atau Manager yang dapat mengeskalasi pengaduan."
    ),
    "complaint.submitter_not_found": "Pengirim pengaduan tidak ditemukan atau tidak aktif.",
    "complaint.unsupported_source_type": "Pengaduan memiliki sourceType yang tidak didukung.",
    "complaint.unsupported_status": "Pengaduan memiliki status yang tidak didukung.",
    "complaint.unsupported_target_type": "Pengaduan memiliki targetType yang tidak didukung.",
    # --- CAP-008 Case F4 acceptance ---
    "case.acceptance_role_denied": (
        "Hanya Supervisor atau Manager yang berwenang yang dapat memberikan "
        "persetujuan penutupan Case."
    ),
    "case.acceptance_owner_unit_mismatch": (
        "Persetujuan Owner hanya boleh dilakukan oleh Supervisor/Manager "
        "pada unit Owner Case."
    ),
    "case.acceptance_handling_unit_mismatch": (
        "Persetujuan Handling Unit hanya boleh dilakukan oleh Supervisor/Manager "
        "pada unit penanganan Case saat ini."
    ),
    "case.acceptance_creator_conflict": (
        "Pembuat pengaduan tidak boleh menjadi satu-satunya pemberi persetujuan "
        "untuk pengaduan yang sama (pemisahan tugas)."
    ),
    "case.acceptance_party_invalid": "Pihak persetujuan Case tidak valid.",
    "case.resolve_accept_role_denied": (
        "Agent tidak boleh memberikan penerimaan Handling Unit final. "
        "Gunakan pengajuan resolusi (PROPOSE), lalu Supervisor/Manager yang "
        "berwenang memberikan ACCEPT."
    ),
    # --- Escalation ---
    "escalation.already_closed": "Eskalasi sudah berstatus CLOSED.",
    "escalation.already_reviewed": "Eskalasi sudah ditinjau.",
    "escalation.final_resolution_required_close": (
        "Resolusi Akhir harus ada sebelum menutup eskalasi."
    ),
    "escalation.has_active_appointment": "Eskalasi sudah memiliki janji temu aktif.",
    "escalation.must_be_approved_for_booking": (
        "Eskalasi harus berstatus APPROVED sebelum memesan janji temu."
    ),
    "escalation.must_exist_before_close_complaint": (
        "Eskalasi harus ada sebelum menutup pengaduan."
    ),
    "escalation.not_found": "Eskalasi tidak ditemukan.",
    "escalation.only_admin_close": "Hanya Head Office Admin yang dapat menutup eskalasi.",
    "escalation.only_requested_review": "Hanya eskalasi berstatus REQUESTED yang dapat ditinjau.",
    "escalation.only_scheduler_admin_review": (
        "Hanya Head Office Scheduler atau Admin yang dapat meninjau eskalasi."
    ),
    "escalation.related_complaint_must_be_closed": (
        "Pengaduan terkait harus berstatus CLOSED sebelum menutup eskalasi."
    ),
    "escalation.source_user_not_found": (
        "Pengguna sumber eskalasi tidak ditemukan atau tidak aktif."
    ),
    "escalation.target_role_not_found": ("Peran target eskalasi tidak ditemukan atau tidak aktif."),
    "escalation.target_user_not_found": (
        "Pengguna target eskalasi tidak ditemukan atau tidak aktif."
    ),
    # --- Appointment ---
    "appointment.already_checked_in": "Janji temu sudah check-in.",
    "appointment.already_completed": "Janji temu sudah selesai.",
    "appointment.already_no_show": "Janji temu sudah ditandai sebagai no-show.",
    "appointment.engineer_not_found": "Teknisi yang ditugaskan tidak ditemukan atau tidak aktif.",
    "appointment.must_be_completed_for_final_resolution": (
        "Janji temu harus berstatus COMPLETED sebelum mengirim Resolusi Akhir."
    ),
    "appointment.no_show_already_checked_in": (
        "Tidak dapat menandai no-show: janji temu sudah check-in."
    ),
    "appointment.no_show_already_completed": (
        "Tidak dapat menandai no-show: janji temu sudah selesai."
    ),
    "appointment.not_found": "Janji temu tidak ditemukan.",
    "appointment.only_booked_check_in": "Hanya janji temu berstatus BOOKED yang dapat check-in.",
    "appointment.only_booked_no_show": (
        "Hanya janji temu berstatus BOOKED yang dapat ditandai no-show."
    ),
    "appointment.only_checked_in_complete": (
        "Hanya janji temu berstatus CHECKED_IN yang dapat diselesaikan."
    ),
    "appointment.only_engineer_admin_complete": (
        "Hanya Teknisi Kantor Pusat atau Admin yang dapat menyelesaikan janji temu."
    ),
    "appointment.overlap_booking": (
        "Janji temu bertumpang tindih dengan booking yang sudah ada untuk teknisi ini."
    ),
    "appointment.required_before_final_resolution": (
        "Janji temu diperlukan sebelum mengirim Resolusi Akhir."
    ),
    # --- Resolution ---
    "resolution.already_submitted": "Resolusi Akhir sudah dikirim.",
    "resolution.not_allowed_no_show": (
        "Resolusi Akhir tidak diizinkan ketika janji temu berstatus NO_SHOW."
    ),
    "resolution.not_found": "Resolusi Akhir tidak ditemukan.",
    "resolution.only_engineer_admin_submit": (
        "Hanya Teknisi Kantor Pusat atau Admin yang dapat mengirim Resolusi Akhir."
    ),
    "resolution.resolver_not_found": "Resolver tidak ditemukan atau tidak aktif.",
    "resolution.generic_not_found": "Resolusi tidak ditemukan.",
    "resolution.cannot_change_after_closed": (
        "Resolusi tidak dapat diubah setelah pengaduan berstatus CLOSED."
    ),
    "resolution.only_when_resolved_or_closed": (
        "Resolusi hanya diizinkan ketika status RESOLVED atau CLOSED."
    ),
    "resolution.resolved_by_must_match_user": (
        "resolvedBy harus sesuai dengan pengguna terautentikasi."
    ),
    # --- Assignment ---
    "assignment.active_cannot_have_released_at": (
        "Penugasan aktif tidak boleh memiliki released_at."
    ),
    "assignment.active_not_belong_complaint": ("Penugasan aktif tidak termasuk pengaduan ini."),
    "assignment.already_has_active": (
        "Pengaduan sudah memiliki penugasan aktif; gunakan penugasan ulang."
    ),
    "assignment.already_inactive": "Penugasan sudah tidak aktif.",
    "assignment.assignee_not_found": "Penerima tugas tidak ditemukan atau tidak aktif.",
    "assignment.inactive_requires_released_at": "Penugasan tidak aktif memerlukan released_at.",
    "assignment.no_active_to_reassign": (
        "Pengaduan tidak memiliki penugasan aktif untuk penugasan ulang."
    ),
    "assignment.no_active_to_unassign": "Pengaduan tidak memiliki penugasan aktif untuk unassign.",
    "assignment.reason_required_reassignment": "Alasan wajib diisi untuk penugasan ulang.",
    # --- SLA ---
    "sla.active_cannot_have_completed_at": "SLA aktif tidak boleh memiliki completed_at.",
    "sla.active_not_belong_complaint": "SLA aktif tidak termasuk pengaduan ini.",
    "sla.already_has_active": "Pengaduan sudah memiliki SLA aktif.",
    "sla.already_inactive": "SLA sudah tidak aktif.",
    "sla.breached_requires_breached_at": "SLA breached memerlukan breached_at.",
    "sla.cannot_start_on_closed": "Tidak dapat memulai SLA pada pengaduan berstatus CLOSED.",
    "sla.inactive_requires_completed_at": "SLA tidak aktif memerlukan completed_at.",
    "sla.no_active_to_complete": "Pengaduan tidak memiliki SLA aktif untuk diselesaikan.",
    "sla.non_breached_cannot_have_breached_at": (
        "SLA non-breached tidak boleh memiliki breached_at."
    ),
    "sla.no_default_policy": "Tidak ada kebijakan SLA default yang dikonfigurasi.",
    "sla.policy_not_found": "Kebijakan SLA tidak ditemukan.",
    "sla.policy_required_before_complaint": (
        "Kebijakan SLA aktif diperlukan sebelum membuat pengaduan."
    ),
    "sla.record_not_found": "Catatan SLA tidak ditemukan.",
    "sla.target_minutes_positive": "target_minutes harus bilangan bulat positif.",
    # --- Escalation (domain state) ---
    "escalation.already_historical": "Eskalasi sudah bersifat historis.",
    "escalation.current_cannot_have_released_at": (
        "Eskalasi saat ini tidak boleh memiliki released_at."
    ),
    "escalation.current_not_belong_complaint": "Eskalasi saat ini tidak termasuk pengaduan ini.",
    "escalation.historical_requires_released_at": "Eskalasi historis memerlukan released_at.",
    "escalation.not_current": "Eskalasi yang disediakan bukan eskalasi saat ini.",
    # --- Duplicate detection ---
    "duplicate.hard_block_create": (
        "Hard Block: kebijakan duplikat mencegah pembuatan Pengaduan baru."
    ),
    "duplicate.invalid_decision": "Keputusan duplikat tidak valid.",
    "duplicate.override_justification_required": (
        "Duplicate Warning: justifikasi override diperlukan."
    ),
    "duplicate.override_justification_reason_required": (
        "Justifikasi override diperlukan (Alasan wajib diisi)."
    ),
    "duplicate.surviving_complaint_not_found": "Pengaduan surviving tidak ditemukan.",
    "duplicate.surviving_id_required_link": (
        "survivingComplaintId diperlukan untuk link_existing."
    ),
    # --- Attachment ---
    "attachment.already_void": "Lampiran sudah void.",
    "attachment.cannot_supersede_void": (
        "Tidak dapat supersede lampiran void atau yang sudah di-supersede."
    ),
    "attachment.case_id_not_supported": ("CaseId tidak didukung pada unggahan lampiran Batch 1."),
    "attachment.duplicate_checksum": "Checksum lampiran duplikat.",
    "attachment.file_not_in_storage": "Berkas lampiran tidak ditemukan di storage.",
    "attachment.metadata_bind_failed": (
        "Pengikatan metadata lampiran gagal; lampiran platform dikompensasi."
    ),
    "attachment.not_found": "Lampiran tidak ditemukan.",
    "attachment.security_scan_rejected": "Lampiran ditolak oleh pemindaian keamanan.",
    "attachment.superseded_not_found": "Lampiran superseded tidak ditemukan.",
    "attachment.unsupported_checksum_algorithm": "Algoritma checksum tidak didukung.",
    "attachment.deleted_cannot_become_available": (
        "Lampiran terhapus tidak dapat menjadi AVAILABLE."
    ),
    "attachment.deleted_cannot_become_failed": ("Lampiran terhapus tidak dapat menjadi FAILED."),
    "attachment.void_reason_required": "Alasan pembatalan wajib diisi.",
    "attachment.void_forbidden": (
        "Hanya pengunggah, pembuat pengaduan, atau admin yang dapat menghapus lampiran."
    ),
    # --- Storage / upload ---
    "storage.aggregate_type_id_required": (
        "aggregateType dan aggregateId diperlukan untuk unggahan platform."
    ),
    "storage.allowed_mime_empty_strings": ("Entri storage.allowed.mime harus string non-kosong."),
    "storage.allowed_mime_non_empty_array": ("storage.allowed.mime harus array JSON non-kosong."),
    "storage.checksum_sha256_format": "checksum_sha256 harus digest hex 64 karakter.",
    "storage.file_empty": "Berkas tidak boleh kosong.",
    "storage.file_exceeds_max_size": "Berkas melebihi ukuran unggahan maksimum.",
    "storage.file_extension_mismatch": "Ekstensi berkas tidak sesuai dengan tipe MIME.",
    "storage.file_extension_too_long": "Ekstensi berkas terlalu panjang.",
    "storage.file_name_required": "file_name diperlukan.",
    "storage.filename_invalid_sanitized": "Nama berkas tidak valid setelah sanitasi.",
    "storage.filename_required": "filename diperlukan.",
    "storage.max_upload_mb_min": "storage.max.upload.mb harus >= 1.",
    "storage.mime_not_allowed": "Tipe MIME tidak diizinkan.",
    "storage.mime_type_required": "mime_type diperlukan.",
    "storage.original_name_required": "original_name diperlukan.",
    "storage.path_escapes_root": "Path storage keluar dari root storage.",
    "storage.path_required": "Path storage diperlukan.",
    "storage.path_must_be_relative": "Path storage harus relatif.",
    "storage.path_no_traversal": "Path storage tidak boleh mengandung path traversal.",
    "storage.root_path_not_empty": "storage.root.path tidak boleh kosong.",
    "storage.storage_path_required": "storage_path diperlukan.",
    "storage.storage_provider_required": "storage_provider diperlukan.",
    "storage.size_bytes_min": "size_bytes harus >= 1.",
    "storage.max_bytes_min": "max_bytes harus >= 1.",
    # --- Queue ---
    "queue.cancelled_cannot_be_called": "Tiket dibatalkan tidak dapat dipanggil.",
    "queue.closed_cannot_pause": "Antrian CLOSED tidak dapat dijeda; buka terlebih dahulu.",
    "queue.closed_calling_rejected": "Antrian CLOSED; pemanggilan ditolak.",
    "queue.closed_new_tickets_rejected": "Antrian CLOSED; tiket baru ditolak.",
    "queue.completed_cannot_be_called": "Tiket selesai tidak dapat dipanggil.",
    "queue.completed_cannot_be_cancelled": "Tiket selesai tidak dapat dibatalkan.",
    "queue.completed_cannot_return_waiting": "Tiket selesai tidak dapat kembali ke WAITING.",
    "queue.paused_calling_rejected": "Antrian PAUSED; pemanggilan ditolak.",
    "queue.paused_new_tickets_rejected": "Antrian PAUSED; tiket baru ditolak.",
    "queue.skipped_cannot_be_called": "Tiket dilewati tidak dapat dipanggil.",
    "queue.ticket_id_required": "queue_ticket_id diperlukan.",
    "queue.tickets_issued_waiting_no_reentry": (
        "Tiket diterbitkan sebagai WAITING; masuk kembali ke WAITING dilarang."
    ),
    # --- Notification ---
    "notification.disabled": "Notifikasi dinonaktifkan.",
    "notification.max_retry_min": "notification.max.retry harus >= 0.",
    "notification.only_failed_pending_retry": (
        "Hanya notifikasi FAILED atau PENDING yang dapat dicoba ulang."
    ),
    "notification.only_pending_cancel": "Hanya notifikasi PENDING yang dapat dibatalkan.",
    "notification.only_pending_failed_enter_sending": (
        "Hanya notifikasi PENDING atau FAILED yang dapat masuk Sending."
    ),
    "notification.only_pending_processing_failed": (
        "Hanya notifikasi PENDING atau PROCESSING yang dapat ditandai Failed."
    ),
    "notification.only_pending_processing_sent": (
        "Hanya notifikasi PENDING atau PROCESSING yang dapat ditandai Sent."
    ),
    "notification.queue_item_not_found": "Item antrian notifikasi tidak ditemukan.",
    "notification.retry_limit_exceeded": "Batas percobaan ulang notifikasi terlampaui.",
    "notification.template_not_found": "Template notifikasi tidak ditemukan.",
    # --- Staging token ---
    "staging.token_closed": "Token staging sudah ditutup.",
    "staging.token_expired": "Token staging sudah kedaluwarsa.",
    "staging.token_not_found": "Token staging tidak ditemukan.",
    "staging.token_not_open": "Token staging tidak terbuka.",
    # --- Audit / timeline ---
    "audit.not_found": "Log audit tidak ditemukan.",
    "timeline.not_found": "Entri timeline tidak ditemukan.",
    # --- Complaint create / state ---
    "complaint.new_must_start_open": "Pengaduan baru harus dimulai dengan status OPEN.",
    "complaint.customer_id_required": "customerId diperlukan.",
    "complaint.customer_id_required_blocked": "customerId diperlukan untuk blocked.",
    "complaint.customer_id_required_override": "customerId diperlukan untuk override.",
    "complaint.customer_id_required_recommend_only": "customerId diperlukan untuk recommend_only.",
    "complaint.customer_id_verified_master": (
        "customerId harus berupa id Master Customer terverifikasi."
    ),
    "complaint.target_id_required": "targetId diperlukan untuk rute ini.",
    "complaint.classification_not_allowed": "Klasifikasi tidak diizinkan.",
    "complaint.principal_key_required_confirm_lock": (
        "Kunci principal diperlukan untuk menerapkan kunci konfirmasi pelanggan."
    ),
    # --- Config / settings validation ---
    "config.at_least_one_field": "Setidaknya satu field diperlukan.",
    "config.code_module_prefix_match": "Awalan modul code harus sesuai dengan field module.",
    "config.code_uppercase_format": ("code harus huruf kapital, digit, dan underscore."),
    "config.code_module_action_format": "code harus sesuai format module:action.",
    "config.date_from_lte_date_to": "dateFrom harus <= dateTo.",
    "config.date_from_lte_date_to_snake": "date_from harus <= date_to.",
    "config.entity_type_required": "entity_type diperlukan.",
    "config.entity_type_max_length": "Panjang maksimum entity_type adalah 100.",
    "config.event_type_required": "event_type diperlukan.",
    "config.event_type_max_length": "Panjang maksimum event_type adalah 100.",
    "config.module_lowercase_format": ("module harus huruf kecil, digit, dan underscore."),
    "config.page_min": "page harus >= 1.",
    "config.page_size_range": "pageSize harus antara 1 dan 100.",
    "config.permission_ids_no_duplicates": "permissionIds tidak boleh mengandung duplikat.",
    "config.preferred_language_values": "preferredLanguage harus salah satu dari: id, en.",
    "config.role_ids_no_duplicates": "roleIds tidak boleh mengandung duplikat.",
    "config.scopes_no_duplicates": "scopes tidak boleh mengandung duplikat.",
    "config.template_code_format": (
        "Kode template harus diawali huruf dan menggunakan format yang valid."
    ),
    "config.title_required": "title diperlukan.",
    "config.value_boolean": "value harus boolean (true/false).",
    "config.value_email": "value harus alamat email valid.",
    "config.value_http_url": "value harus URL http(s).",
    "config.value_integer": "value harus bilangan bulat.",
    "config.value_json": "value harus JSON valid.",
    "config.work_item_status_values": "workItemStatus harus OPEN, CLOSED, atau ALL.",
    "escalation.rejected_new": "Pengaduan berstatus NEW tidak dapat dieskalasikan.",
    "escalation.rejected_resolved": "Pengaduan berstatus RESOLVED tidak dapat dieskalasikan.",
    "escalation.rejected_closed": "Pengaduan berstatus CLOSED tidak dapat dieskalasikan.",
    "validation.must_not_blank": "Tidak boleh kosong.",
    "validation.invalid_email": "Format email tidak valid.",
    "validation.no_edge_whitespace": "Tidak boleh diawali atau diakhiri spasi.",
    "validation.at_least_one_field": "Minimal satu bidang wajib diisi.",
    "validation.password_confirm_mismatch": ("Kata sandi dan konfirmasi kata sandi harus sama."),
    "validation.new_password_confirm_mismatch": ("Kata sandi baru dan konfirmasi harus sama."),
    "validation.name_required": "Nama wajib diisi.",
    "validation.time_hhmm": "Harus berformat HH:MM.",
    "validation.end_after_start": "endTime harus setelah startTime.",
    "escalation.target_required": ("escalatedToUserId atau escalatedToRoleId wajib diisi."),
    "complaint.route_fields_all_required": (
        "sourceType, sourceId, targetType, dan targetId wajib diisi jika salah satu diisi."
    ),
    "complaint.customer_source_mismatch": (
        "customerId harus sama dengan sourceId jika sourceType adalah CUSTOMER."
    ),
    "complaint.branch_target_mismatch": (
        "branchId harus sama dengan targetId jika targetType adalah BRANCH."
    ),
    "complaint.customer_required_when_route_omitted": (
        "customerId wajib diisi jika bidang source/target dihilangkan."
    ),
    "validation.value_required": "Nilai wajib diisi.",
    # --- Framework / Pydantic / Starlette (L10-03) ---
    # Required (missing field) — canonical wording for this condition.
    "framework.field_required": "Wajib diisi.",
    "framework.value_invalid": "Nilai tidak valid.",
    "framework.string_type": "Input harus berupa teks.",
    "framework.bool_type": "Input harus berupa boolean.",
    "framework.int_type": "Input harus berupa bilangan bulat.",
    "framework.float_type": "Input harus berupa angka.",
    "framework.list_type": "Input harus berupa daftar.",
    "framework.dict_type": "Input harus berupa objek.",
    "framework.uuid_invalid": "UUID tidak valid.",
    "framework.date_invalid": "Tanggal tidak valid.",
    "framework.datetime_invalid": "Tanggal dan waktu tidak valid.",
    "framework.json_invalid": "JSON tidak valid.",
    "framework.string_too_short": "Teks minimal {min_length} karakter.",
    "framework.string_too_long": "Teks maksimal {max_length} karakter.",
    "framework.list_too_short": "Daftar minimal {min_length} item.",
    "framework.list_too_long": "Daftar maksimal {max_length} item.",
    "framework.greater_than": "Nilai harus lebih besar dari {gt}.",
    "framework.greater_than_equal": "Nilai harus lebih besar atau sama dengan {ge}.",
    "framework.less_than": "Nilai harus lebih kecil dari {lt}.",
    "framework.less_than_equal": "Nilai harus lebih kecil atau sama dengan {le}.",
    "framework.unexpected_value": "Nilai tidak terduga; diharapkan {expected}.",
    "framework.bool_parsing": "Input harus berupa boolean yang valid.",
    "framework.int_parsing": "Input harus berupa bilangan bulat yang valid.",
    "framework.float_parsing": "Input harus berupa angka yang valid.",
    "framework.decimal_parsing": "Input harus berupa angka desimal yang valid.",
    "framework.string_pattern": "Format teks tidak sesuai pola yang diharapkan.",
    "http.not_found": "Sumber daya tidak ditemukan.",
    "http.method_not_allowed": "Metode HTTP tidak diizinkan.",
    "http.forbidden": "Anda tidak memiliki izin untuk tindakan ini.",
    "http.unauthorized": "Autentikasi diperlukan.",
    "http.internal_server_error": "Terjadi kesalahan pada server.",
}

LEGACY_EN_TO_KEY: dict[str, str] = {
    "An active SLA policy is required before creating a complaint.": (
        "sla.policy_required_before_complaint"
    ),
    "An appointment is required before submitting final resolution.": (
        "appointment.required_before_final_resolution"
    ),
    "Appointment has already been checked in.": "appointment.already_checked_in",
    "Appointment has already been completed.": "appointment.already_completed",
    "Appointment has already been marked as no-show.": "appointment.already_no_show",
    "Appointment must be COMPLETED before submitting final resolution.": (
        "appointment.must_be_completed_for_final_resolution"
    ),
    "Appointment not found": "appointment.not_found",
    "Appointment overlaps an existing booking for this engineer.": "appointment.overlap_booking",
    "Assigned engineer not found or inactive.": "appointment.engineer_not_found",
    "Assignee not found or inactive": "assignment.assignee_not_found",
    "Attachment already void": "attachment.already_void",
    "Attachment file not found in storage": "attachment.file_not_in_storage",
    "Attachment metadata bind failed; platform attachment compensated": (
        "attachment.metadata_bind_failed"
    ),
    "Attachment not found": "attachment.not_found",
    "Attachment rejected by security scan": "attachment.security_scan_rejected",
    "Audit log not found": "audit.not_found",
    "Authentication required": "auth.authentication_required",
    "Bearer token required": "auth.bearer_required",
    "Branch not found": "branch.not_found",
    "Branch not found or inactive": "branch.not_found_or_inactive",
    "CLOSED queue cannot be paused; open it first": "queue.closed_cannot_pause",
    "Cannot mark no-show: appointment is already checked in.": (
        "appointment.no_show_already_checked_in"
    ),
    "Cannot mark no-show: appointment is already completed.": (
        "appointment.no_show_already_completed"
    ),
    "Cannot supersede void or already superseded attachment": "attachment.cannot_supersede_void",
    "CaseId is not supported in Batch 1 attachment upload": "attachment.case_id_not_supported",
    "Closer not found or inactive": "complaint.closer_not_found",
    "Complaint already has a resolution and cannot be escalated.": (
        "complaint.has_resolution_cannot_escalate"
    ),
    "Complaint already has an SLA record.": "complaint.already_has_sla",
    "Complaint already has an active escalation.": "complaint.already_has_escalation",
    "Complaint cannot be assigned in its current status": "complaint.cannot_assign_status",
    "Complaint cannot be deleted while an SLA record exists.": ("complaint.cannot_delete_with_sla"),
    "Complaint cannot be escalated in its current status": "complaint.cannot_escalate_status",
    "Complaint has an unsupported sourceType": "complaint.unsupported_source_type",
    "Complaint has an unsupported status": "complaint.unsupported_status",
    "Complaint has an unsupported targetType": "complaint.unsupported_target_type",
    "Complaint is already CLOSED.": "complaint.already_closed",
    "Complaint must be IN_PROGRESS before closing.": "complaint.must_be_in_progress_close",
    "Complaint must be IN_PROGRESS before requesting escalation.": (
        "complaint.must_be_in_progress_escalation"
    ),
    "Complaint must be IN_PROGRESS before resolving.": "complaint.must_be_in_progress_resolve",
    "Complaint must be IN_PROGRESS before submitting final resolution.": (
        "complaint.must_be_in_progress_final"
    ),
    "Complaint not found": "complaint.not_found",
    "Current password is incorrect": "auth.current_password_incorrect",
    "Customer Master write-back is forbidden (ADR-002 / BR-002)": (
        "customer.master_writeback_forbidden"
    ),
    "Customer not found": "customer.not_found",
    "Customer not found in Master Customer": "customer.not_in_master",
    "Customer search temporarily blocked by enumeration protection": (
        "customer.search_blocked_enumeration"
    ),
    "CustomerId must be confirmed/locked for this actor before create": (
        "customer.id_must_be_confirmed"
    ),
    "Data scope already exists for role": "iam.data_scope_exists",
    "Data scope denied": "common.data_scope_denied",
    "Data scope not found": "iam.data_scope_not_found",
    "Duplicate Warning: override justification is required": (
        "duplicate.override_justification_required"
    ),
    "Duplicate attachment checksum": "attachment.duplicate_checksum",
    "Email already exists": "user.email_exists",
    "Escalation already has an active appointment.": "escalation.has_active_appointment",
    "Escalation has already been reviewed.": "escalation.already_reviewed",
    "Escalation is already CLOSED.": "escalation.already_closed",
    "Escalation must be APPROVED before booking an appointment.": (
        "escalation.must_be_approved_for_booking"
    ),
    "Escalation must exist before closing the complaint.": (
        "escalation.must_exist_before_close_complaint"
    ),
    "Escalation not found": "escalation.not_found",
    "Escalation source user not found or inactive": "escalation.source_user_not_found",
    "Escalation target role not found or inactive": "escalation.target_role_not_found",
    "Escalation target user not found or inactive": "escalation.target_user_not_found",
    "Exactly one customer key type must be supplied": "customer.exactly_one_key_type",
    "Final Resolution must exist before closing the complaint.": (
        "complaint.final_resolution_required_close"
    ),
    "Final Resolution must exist before closing the escalation.": (
        "escalation.final_resolution_required_close"
    ),
    "Final resolution has already been submitted.": "resolution.already_submitted",
    "Final resolution is not allowed when appointment is NO_SHOW.": (
        "resolution.not_allowed_no_show"
    ),
    "Final resolution not found": "resolution.not_found",
    "Hard Block: duplicate policy prevents new Complaint create": "duplicate.hard_block_create",
    "Internal server error": "common.internal_error",
    "Invalid complaint route.": "complaint.invalid_route",
    "Invalid duplicate decision": "duplicate.invalid_decision",
    "Invalid or expired refresh token": "auth.invalid_refresh",
    "Invalid or expired reset token": "auth.invalid_reset_token",
    "Invalid or expired token": "auth.invalid_token",
    "Invalid status transition.": "common.invalid_status_transition",
    "Invalid username or password": "auth.invalid_credentials",
    "Local credential authentication is disabled": "auth.local_disabled",
    "Master Customer unavailable (Strict mode)": "customer.master_unavailable_strict",
    "Master Customer unavailable (Strict mode) — create rejected": (
        "customer.master_unavailable_create_rejected"
    ),
    "New password must be different from the current password": "auth.password_must_differ",
    "Not allowed to assign this role": "iam.cannot_assign_role",
    "Notification queue item not found": "notification.queue_item_not_found",
    "Notification template not found": "notification.template_not_found",
    "One or more permissions not found": "iam.permissions_not_found",
    "One or more roles not found": "iam.roles_not_found",
    "Only BOOKED appointments can be checked in.": "appointment.only_booked_check_in",
    "Only BOOKED appointments can be marked as no-show.": "appointment.only_booked_no_show",
    "Only Branch Supervisor or Head Office Admin can close complaints": (
        "complaint.only_supervisor_admin_close"
    ),
    "Only CHECKED_IN appointments can be completed.": "appointment.only_checked_in_complete",
    "Only Head Office Admin can close escalations": "escalation.only_admin_close",
    "Only Head Office Engineer or Admin can complete appointments": (
        "appointment.only_engineer_admin_complete"
    ),
    "Only Head Office Engineer or Admin can submit final resolution": (
        "resolution.only_engineer_admin_submit"
    ),
    "Only Head Office Scheduler or Admin can review escalations": (
        "escalation.only_scheduler_admin_review"
    ),
    "Only REQUESTED escalations can be reviewed.": "escalation.only_requested_review",
    "Only Supervisor can assign complaints": "complaint.only_supervisor_assign",
    "Only Supervisor can escalate complaints": "complaint.only_supervisor_escalate",
    "Organization scope denied": "common.org_scope_denied",
    "Organization scope denied: missing orgUnitId claim": "org.scope_missing_org_unit_claim",
    "Organization scope denied: resource has no organization unit": (
        "org.scope_resource_no_org_unit"
    ),
    "Override justification is required (Reason Required)": (
        "duplicate.override_justification_reason_required"
    ),
    "Password change required before accessing the application": "auth.password_change_required",
    "Password changed successfully.": "auth.password_changed",
    "Password has been reset successfully.": "auth.password_reset_ok",
    "Password must not be blank": "auth.password_blank",
    "Password must not have leading or trailing whitespace": "auth.password_whitespace",
    "Permission already assigned to role": "iam.permission_already_assigned",
    "Permission denied": "common.forbidden",
    "Permission not found": "iam.permission_not_found",
    "Refresh token required": "auth.refresh_required",
    "Related Complaint must be CLOSED before closing the escalation.": (
        "escalation.related_complaint_must_be_closed"
    ),
    "Request Id (Idempotency-Key) is required": "common.idempotency_key_required",
    "Request failed": "common.request_failed",
    "Request validation failed": "common.validation_failed",
    "Resolution not found": "resolution.generic_not_found",
    "Resolver not found or inactive": "resolution.resolver_not_found",
    "Resource not found": "common.not_found",
    "Role already assigned to user": "iam.role_already_assigned",
    "Role not found": "iam.role_not_found",
    "Role not found or inactive": "iam.role_not_found_or_inactive",
    "Role permission link not found": "iam.role_permission_not_found",
    "SLA is already inactive": "sla.already_inactive",
    "SLA policy not found": "sla.policy_not_found",
    "SLA record not found": "sla.record_not_found",
    "Staging token has expired": "staging.token_expired",
    "Staging token is closed": "staging.token_closed",
    "Staging token is not open": "staging.token_not_open",
    "Staging token not found": "staging.token_not_found",
    "Submitter not found or inactive": "complaint.submitter_not_found",
    "Superseded attachment not found": "attachment.superseded_not_found",
    "Surviving Complaint not found": "duplicate.surviving_complaint_not_found",
    "System permission cannot be deleted": "iam.system_permission_cannot_delete",
    "System role cannot be deleted": "iam.system_role_cannot_delete",
    "Timeline entry not found": "timeline.not_found",
    "Token missing subject": "auth.token_missing_subject",
    "Token subject must be a UUID": "auth.token_subject_must_be_uuid",
    "Too many attempts; try again later": "common.rate_limited",
    "Too many login attempts. Try again later.": "auth.rate_limited_login",
    "Too many login attempts; try again later": "auth.rate_limited_login",
    "Unauthenticated": "auth.unauthenticated",
    "Unsupported checksum algorithm": "attachment.unsupported_checksum_algorithm",
    "Unsupported sourceType": "common.unsupported_source_type",
    "Unsupported targetType": "common.unsupported_target_type",
    "User not found": "user.not_found",
    "User role link not found": "iam.user_role_not_found",
    "Username already exists": "user.username_exists",
    "Branch is required for this role": "user.branch_required_for_role",
    "Branch is not allowed for this role": "user.branch_forbidden_for_role",
    "active SLA cannot have completed_at set": "sla.active_cannot_have_completed_at",
    "active SLA does not belong to this complaint": "sla.active_not_belong_complaint",
    "active assignment cannot have released_at set": "assignment.active_cannot_have_released_at",
    "active assignment does not belong to this complaint": "assignment.active_not_belong_complaint",
    "aggregateType and aggregateId are required for platform upload": (
        "storage.aggregate_type_id_required"
    ),
    "assignment is already inactive": "assignment.already_inactive",
    "at least one field is required": "config.at_least_one_field",
    "breached SLA requires breached_at": "sla.breached_requires_breached_at",
    "cancelled ticket cannot be called": "queue.cancelled_cannot_be_called",
    "cannot start SLA on a CLOSED complaint": "sla.cannot_start_on_closed",
    "checksum_sha256 must be a 64-char hex digest": "storage.checksum_sha256_format",
    "classification is not allowed": "complaint.classification_not_allowed",
    "code module prefix must match module field": "config.code_module_prefix_match",
    "code must be uppercase letters, digits, and underscores ": "config.code_uppercase_format",
    "code must match module:action ": "config.code_module_action_format",
    "complaint already has an active SLA": "sla.already_has_active",
    "complaint already has an active assignment; use reassign": "assignment.already_has_active",
    "complaint has no active SLA to complete": "sla.no_active_to_complete",
    "complaint has no active assignment to reassign": "assignment.no_active_to_reassign",
    "complaint has no active assignment to unassign": "assignment.no_active_to_unassign",
    "completed ticket cannot be called": "queue.completed_cannot_be_called",
    "completed ticket cannot be cancelled": "queue.completed_cannot_be_cancelled",
    "completed ticket cannot return to WAITING": "queue.completed_cannot_return_waiting",
    "current escalation cannot have released_at set": "escalation.current_cannot_have_released_at",
    "current escalation does not belong to this complaint": (
        "escalation.current_not_belong_complaint"
    ),
    "customerId is required": "complaint.customer_id_required",
    "customerId is required for blocked": "complaint.customer_id_required_blocked",
    "customerId is required for override": "complaint.customer_id_required_override",
    "customerId is required for recommend_only": "complaint.customer_id_required_recommend_only",
    "customerId must be a verified Master Customer id": "complaint.customer_id_verified_master",
    "dateFrom must be less than or equal to dateTo": "config.date_from_lte_date_to",
    "date_from must be <= date_to": "config.date_from_lte_date_to_snake",
    "deleted attachments cannot become AVAILABLE": "attachment.deleted_cannot_become_available",
    "deleted attachments cannot become FAILED": "attachment.deleted_cannot_become_failed",
    "entity_type is required": "config.entity_type_required",
    "entity_type max length is 100": "config.entity_type_max_length",
    "escalation is already historical": "escalation.already_historical",
    "event_type is required": "config.event_type_required",
    "event_type max length is 100": "config.event_type_max_length",
    "file exceeds maximum upload size": "storage.file_exceeds_max_size",
    "file extension does not match mime type": "storage.file_extension_mismatch",
    "file extension is too long": "storage.file_extension_too_long",
    "file must not be empty": "storage.file_empty",
    "file_name is required": "storage.file_name_required",
    "filename is invalid after sanitization": "storage.filename_invalid_sanitized",
    "filename is required": "storage.filename_required",
    "historical escalation requires released_at": "escalation.historical_requires_released_at",
    "inactive SLA requires completed_at": "sla.inactive_requires_completed_at",
    "inactive assignment requires released_at": "assignment.inactive_requires_released_at",
    "max_bytes must be >= 1": "storage.max_bytes_min",
    "mime type is not allowed": "storage.mime_not_allowed",
    "mime_type is required": "storage.mime_type_required",
    "module must be lowercase letters, digits, and underscores ": "config.module_lowercase_format",
    "new complaints must start in OPEN status": "complaint.new_must_start_open",
    "no default SLA policy configured": "sla.no_default_policy",
    "non-breached SLA cannot have breached_at set": "sla.non_breached_cannot_have_breached_at",
    "notification retry limit exceeded": "notification.retry_limit_exceeded",
    "notification.max.retry must be >= 0": "notification.max_retry_min",
    "notifications are disabled": "notification.disabled",
    "only FAILED or PENDING notifications can be retried": "notification.only_failed_pending_retry",
    "only PENDING notifications can be cancelled": "notification.only_pending_cancel",
    "only PENDING or FAILED notifications can enter Sending": (
        "notification.only_pending_failed_enter_sending"
    ),
    "only PENDING or PROCESSING notifications can be marked Failed": (
        "notification.only_pending_processing_failed"
    ),
    "only PENDING or PROCESSING notifications can be marked Sent": (
        "notification.only_pending_processing_sent"
    ),
    "original_name is required": "storage.original_name_required",
    "page must be >= 1": "config.page_min",
    "pageSize must be between 1 and 100": "config.page_size_range",
    "permissionIds must not contain duplicates": "config.permission_ids_no_duplicates",
    "preferredLanguage must be one of: id, en": "config.preferred_language_values",
    "principal key is required to enforce customer confirm lock": (
        "complaint.principal_key_required_confirm_lock"
    ),
    "provided escalation is not current": "escalation.not_current",
    "queue is CLOSED; calling is rejected": "queue.closed_calling_rejected",
    "queue is CLOSED; new tickets are rejected": "queue.closed_new_tickets_rejected",
    "queue is PAUSED; calling is rejected": "queue.paused_calling_rejected",
    "queue is PAUSED; new tickets are rejected": "queue.paused_new_tickets_rejected",
    "queue_ticket_id is required": "queue.ticket_id_required",
    "reason is required for reassignment": "assignment.reason_required_reassignment",
    "resolution cannot be changed after complaint is CLOSED": (
        "resolution.cannot_change_after_closed"
    ),
    "resolution is only allowed when status is RESOLVED or CLOSED": (
        "resolution.only_when_resolved_or_closed"
    ),
    "resolvedBy must match the authenticated user": "resolution.resolved_by_must_match_user",
    "roleIds must not contain duplicates": "config.role_ids_no_duplicates",
    "scopes must not contain duplicates": "config.scopes_no_duplicates",
    "size_bytes must be >= 1": "storage.size_bytes_min",
    "skipped ticket cannot be called": "queue.skipped_cannot_be_called",
    "storage path escapes storage root": "storage.path_escapes_root",
    "storage path is required": "storage.path_required",
    "storage path must be relative": "storage.path_must_be_relative",
    "storage path must not contain path traversal": "storage.path_no_traversal",
    "storage.allowed.mime entries must be non-empty strings": "storage.allowed_mime_empty_strings",
    "storage.allowed.mime must be a non-empty JSON array": "storage.allowed_mime_non_empty_array",
    "storage.max.upload.mb must be >= 1": "storage.max_upload_mb_min",
    "storage.root.path must not be empty": "storage.root_path_not_empty",
    "storage_path is required": "storage.storage_path_required",
    "storage_provider is required": "storage.storage_provider_required",
    "survivingComplaintId is required for link_existing": "duplicate.surviving_id_required_link",
    "targetId is required for this route.": "complaint.target_id_required",
    "target_minutes must be a positive integer": "sla.target_minutes_positive",
    "template code must start with a letter and use ": "config.template_code_format",
    "tickets are issued as WAITING; re-entry to WAITING is forbidden": (
        "queue.tickets_issued_waiting_no_reentry"
    ),
    "title is required": "config.title_required",
    "value must be a boolean (true/false)": "config.value_boolean",
    "value must be a valid email address": "config.value_email",
    "value must be an http(s) URL": "config.value_http_url",
    "value must be an integer": "config.value_integer",
    "value must be valid JSON": "config.value_json",
    "void reason is required (void-with-reason)": "attachment.void_reason_required",
    "attachment void forbidden": "attachment.void_forbidden",
    "workItemStatus must be OPEN, CLOSED, or ALL": "config.work_item_status_values",
    "NEW complaints cannot be escalated": "escalation.rejected_new",
    "RESOLVED complaints cannot be escalated": "escalation.rejected_resolved",
    "CLOSED complaints cannot be escalated": "escalation.rejected_closed",
    "must not be blank": "validation.must_not_blank",
    "invalid email format": "validation.invalid_email",
    "must not have leading or trailing whitespace": "validation.no_edge_whitespace",
    "at least one field must be provided": "validation.at_least_one_field",
    "password and confirmPassword must match": "validation.password_confirm_mismatch",
    "newPassword and confirmPassword must match": "validation.new_password_confirm_mismatch",
    "name is required": "validation.name_required",
    "must be HH:MM": "validation.time_hhmm",
    "endTime must be after startTime": "validation.end_after_start",
    "escalatedToUserId or escalatedToRoleId is required": "escalation.target_required",
    "sourceType, sourceId, targetType, and targetId are all required when any is provided": (
        "complaint.route_fields_all_required"
    ),
    "customerId must match sourceId when sourceType is CUSTOMER": (
        "complaint.customer_source_mismatch"
    ),
    "branchId must match targetId when targetType is BRANCH": "complaint.branch_target_mismatch",
    "customerId is required when source/target fields are omitted": (
        "complaint.customer_required_when_route_omitted"
    ),
    "value is required": "validation.value_required",
    "Not Found": "http.not_found",
    "Method Not Allowed": "http.method_not_allowed",
    "Forbidden": "http.forbidden",
    "Unauthorized": "http.unauthorized",
    "Internal Server Error": "http.internal_server_error",
    "Field required": "framework.field_required",
    "Input should be a valid string": "framework.string_type",
    "Input should be a valid boolean": "framework.bool_type",
    "Input should be a valid integer": "framework.int_type",
    "Input should be a valid number": "framework.float_type",
    "Input should be a valid list": "framework.list_type",
    "Input should be a valid dictionary": "framework.dict_type",
    "JSON decode error": "framework.json_invalid",
    "Value is not a valid UUID": "framework.uuid_invalid",
    "value is not a valid uuid": "framework.uuid_invalid",
    "Invalid UUID": "framework.uuid_invalid",
    "invalid datetime format": "framework.datetime_invalid",
    "invalid date format": "framework.date_invalid",
}


# Pydantic / FastAPI error ``type`` → static catalog key (no ctx formatting).
_FRAMEWORK_TYPE_STATIC: dict[str, str] = {
    "missing": "framework.field_required",
    "string_type": "framework.string_type",
    "bool_type": "framework.bool_type",
    "int_type": "framework.int_type",
    "float_type": "framework.float_type",
    "list_type": "framework.list_type",
    "dict_type": "framework.dict_type",
    "uuid_type": "framework.uuid_invalid",
    "uuid_parsing": "framework.uuid_invalid",
    "uuid_version": "framework.uuid_invalid",
    "date_type": "framework.date_invalid",
    "date_parsing": "framework.date_invalid",
    "date_from_datetime_parsing": "framework.date_invalid",
    "datetime_type": "framework.datetime_invalid",
    "datetime_parsing": "framework.datetime_invalid",
    "datetime_from_date_parsing": "framework.datetime_invalid",
    "time_parsing": "framework.datetime_invalid",
    "json_invalid": "framework.json_invalid",
    "json_type": "framework.json_invalid",
    "bool_parsing": "framework.bool_parsing",
    "int_parsing": "framework.int_parsing",
    "int_from_float": "framework.int_type",
    "float_parsing": "framework.float_parsing",
    "decimal_parsing": "framework.decimal_parsing",
    "string_pattern_mismatch": "framework.string_pattern",
    "value_error": "framework.value_invalid",
}

# Pydantic error ``type`` → (catalog key, ctx keys used in ``str.format``).
_FRAMEWORK_TYPE_TEMPLATES: dict[str, tuple[str, tuple[str, ...]]] = {
    "string_too_short": ("framework.string_too_short", ("min_length",)),
    "string_too_long": ("framework.string_too_long", ("max_length",)),
    "too_short": ("framework.list_too_short", ("min_length",)),
    "too_long": ("framework.list_too_long", ("max_length",)),
    "greater_than": ("framework.greater_than", ("gt",)),
    "greater_than_equal": ("framework.greater_than_equal", ("ge",)),
    "less_than": ("framework.less_than", ("lt",)),
    "less_than_equal": ("framework.less_than_equal", ("le",)),
}

_VALUE_ERROR_PREFIXES: tuple[str, ...] = (
    "Value error, ",
    "Assertion failed, ",
)


def code_message(code: str) -> str:
    """Return default Bahasa Indonesia message for an API error code."""
    return CODE_DEFAULTS.get(code, CODE_DEFAULTS["INTERNAL_ERROR"])


def m(key: str) -> str:
    """Return localized message for a semantic business/validation key."""
    return MESSAGES[key]


def localize_legacy(text: str | None, *, fallback_code: str | None = None) -> str:
    """Map a legacy English (or already-ID) string to the catalog message.

    Unknown strings are returned unchanged so framework details are not dropped.
    When ``text`` is empty, use ``code_message(fallback_code)`` if provided.
    Strips Pydantic ``Value error, `` / ``Assertion failed, `` prefixes so custom
    validator messages (already Indonesian via ``m()``) surface cleanly.
    """
    if not text:
        if fallback_code:
            return code_message(fallback_code)
        return code_message("INTERNAL_ERROR")
    cleaned = text
    for prefix in _VALUE_ERROR_PREFIXES:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            break
    key = LEGACY_EN_TO_KEY.get(cleaned)
    if key is not None:
        return m(key)
    # Exact original (pre-strip) legacy match — rare Starlette phrases.
    key = LEGACY_EN_TO_KEY.get(text)
    if key is not None:
        return m(key)
    return cleaned


def localize_framework_validation_error(err: Mapping[str, Any]) -> str:
    """Localize one Pydantic / FastAPI ``RequestValidationError`` item for users.

    Prefer error ``type`` (+ ``ctx``) over raw English ``msg``. Custom
    ``value_error`` messages that are already Indonesian are preserved after
    stripping the framework prefix. Envelope shape is unchanged.
    """
    typ = str(err.get("type") or "")
    msg = err.get("msg")
    msg_text = msg if isinstance(msg, str) else (str(msg) if msg is not None else "")
    ctx_raw = err.get("ctx")
    ctx: dict[str, Any] = ctx_raw if isinstance(ctx_raw, dict) else {}

    # Custom validators: "Value error, <already-localized>" → strip + catalog.
    if typ in {"value_error", "assertion_error"} or any(
        msg_text.startswith(p) for p in _VALUE_ERROR_PREFIXES
    ):
        return localize_legacy(msg_text, fallback_code="VALIDATION_ERROR")

    template = _FRAMEWORK_TYPE_TEMPLATES.get(typ)
    if template is not None:
        key, ctx_keys = template
        values = {k: ctx[k] for k in ctx_keys if k in ctx}
        if len(values) == len(ctx_keys):
            return m(key).format(**values)
        return m(key).format(**{k: ctx.get(k, "?") for k in ctx_keys})

    if typ in {"literal_error", "enum"} and "expected" in ctx:
        expected = str(ctx["expected"]).replace(" or ", " atau ")
        return m("framework.unexpected_value").format(expected=expected)

    static_key = _FRAMEWORK_TYPE_STATIC.get(typ)
    if static_key is not None:
        return m(static_key)

    localized = localize_legacy(msg_text, fallback_code="VALIDATION_ERROR")
    if localized != msg_text and localized != code_message("VALIDATION_ERROR"):
        return localized
    # Unknown framework phrasing — never leak English to the client.
    if msg_text and localized == msg_text and _looks_english_framework_msg(msg_text):
        return m("framework.value_invalid")
    return localized if localized else m("framework.value_invalid")


def _looks_english_framework_msg(text: str) -> bool:
    lower = text.lower()
    markers = (
        "input should",
        "field required",
        "string should",
        "value is not",
        "invalid ",
        "unable to",
        "json decode",
        "assertion failed",
        "value error",
        "unexpected",
    )
    return any(marker in lower for marker in markers)


def field_errors_from_validation(
    errors: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    """Build ``details`` map for VALIDATION_ERROR from framework error items."""
    field_errors: dict[str, str] = {}
    for err in errors:
        loc = err.get("loc", ())
        if not isinstance(loc, (list, tuple)):
            loc = ()
        key = ".".join(str(part) for part in loc if part != "body")
        field_errors[key or "body"] = localize_framework_validation_error(err)
    return field_errors
