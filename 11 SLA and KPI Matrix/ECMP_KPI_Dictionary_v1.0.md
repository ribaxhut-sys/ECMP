# ECMP KPI Dictionary v1.0

| Field | Value |
|---|---|
| ID | SLA-001 |
| Version | 1.0 |
| Owner | Operations Lead / Performance Owner |
| Reviewer | Business Owner, BA Lead, Domain POs |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Kompilasi KPI per domain dari `01 Business Blueprint` (bagian 7.1–7.7) menjadi KPI dictionary formal. Formula dan target numerik yang belum ada di Blueprint ditandai `[TBD]` — harus dikonfirmasi Business Owner sebelum Accepted.

## 1. KPI Dictionary

| Metric ID | Metric Name | Domain | Type | Definition | Formula | Target | Unit | Window | Data Source | Owner | Dashboard Consumer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KPI-CP-01 | Login success rate | Core Platform | KPI | Persentase percobaan login yang berhasil | successful_logins / total_login_attempts | [TBD] | % | Harian | Audit Log | Security Officer | Executive |
| KPI-CP-02 | Unauthorized access attempts | Core Platform | KPI | Jumlah percobaan akses yang ditolak otorisasi | count(denied_access_events) | [TBD] threshold alert | Count | Harian | Audit Log | Security Officer | Executive |
| KPI-CP-03 | Config change count | Core Platform | KPI | Jumlah perubahan konfigurasi dalam periode | count(ConfigChanged events) | Informational (no target) | Count | Mingguan | ConfigChanged event | Administrator | Supervisor |
| KPI-CP-04 | Audit completeness | Core Platform | KPI | Persentase aktivitas wajib-audit yang tercatat | audited_actions / total_actions_requiring_audit | 100% | % | Bulanan | Audit Log | Security Officer | Executive |
| KPI-CRM-01 | Profile retrieval success | CRM | KPI | Persentase pencarian profil pelanggan yang berhasil menampilkan data | successful_lookups / total_lookups | [TBD] | % | Harian | CRM access log | CRM Domain PO | Operational |
| KPI-CRM-02 | Context completeness saat handling | CRM | KPI | Persentase case yang dibuka dengan konteks pelanggan lengkap tersedia | cases_with_full_context / total_cases_opened | [TBD] | % | Mingguan | CRM + ECMF | CRM Domain PO | Supervisor |
| KPI-CRM-03 | Repeat contact rate | CRM | KPI | Persentase pelanggan yang menghubungi kembali untuk masalah sama dalam periode [TBD hari] | repeat_contacts / total_contacts | [TBD] | % | Bulanan | Interaction History | CRM Domain PO | Executive |
| KPI-ECMF-01 | Jumlah transaksi/case | ECMF | KPI | Total case dibuat dalam periode | count(CaseCreated events) | Informational | Count | Harian/Bulanan | CaseCreated event | ECMF Domain PO | Semua persona |
| KPI-ECMF-02 | Lead time | ECMF | KPI | Rata-rata waktu dari CaseCreated sampai CaseClosed | avg(closed_at - created_at) | [TBD] | Jam/Hari | Mingguan | CaseCreated + CaseClosed event | ECMF Domain PO | Supervisor, Executive |
| KPI-ECMF-03 | SLA achievement | ECMF/SLA | SLA | Persentase case yang selesai sebelum SLA due | cases_closed_within_sla / total_cases_closed | [TBD] | % | Mingguan | SLA Clock + CaseClosed | Operations Lead | Semua persona |
| KPI-ECMF-04 | Overdue rate | ECMF/SLA | SLA | Persentase case aktif yang sudah melewati SLA due | count(open_cases_past_due) / count(open_cases) | [TBD] threshold alert | % | Real-time/Harian | SLA Clock | Operations Lead | Operational, Supervisor |
| KPI-ECMF-05 | Reopen rate | ECMF | KPI | Persentase case closed yang di-reopen | count(reopened_cases) / count(closed_cases) | [TBD] | % | Bulanan | Status History | ECMF Domain PO | Supervisor |
| KPI-ECMF-06 | First Contact Resolution | ECMF | KPI | Persentase case selesai pada kontak pertama (bila berlaku) | fcr_cases / total_applicable_cases | [TBD] | % | Bulanan | Case Activity | ECMF Domain PO | Executive |
| KPI-KPI-01 | % metrik ter-publish on-time | KPI & Performance | KPI | Persentase metrik yang dipublikasikan sesuai jadwal | on_time_publications / total_scheduled_publications | [TBD] | % | Mingguan | Metric Definition + Performance Fact | Performance Analyst | Supervisor |
| KPI-KPI-02 | Data freshness | KPI & Performance | KPI | Selisih waktu antara event terjadi dan data tersedia di Performance Fact | avg(fact_available_at - event_occurred_at) | [TBD] | Menit | Real-time | Performance Fact | Performance Analyst | Operational |
| KPI-KPI-03 | SLA calculation accuracy | KPI & Performance | KPI | Persentase perhitungan SLA yang tervalidasi benar (audit sampling) | correct_calculations / sampled_calculations | [TBD] | % | Bulanan | SLA Clock audit | Performance Analyst | Executive |
| KPI-KPI-04 | Unit/agent performance index | KPI & Performance | KPI | Indeks komposit performa unit/agent (formula gabungan KPI lain) | [TBD - perlu definisi bobot komposit] | [TBD] | Index | Bulanan | Performance Fact | Performance Analyst | Supervisor, Executive |
| KPI-DASH-01 | Dashboard adoption | Dashboard & Analytics | KPI | Persentase user target yang aktif menggunakan dashboard | active_dashboard_users / total_target_users | [TBD] | % | Bulanan | Access log | Dashboard Domain PO | Executive |
| KPI-DASH-02 | Time-to-insight | Dashboard & Analytics | KPI | Rata-rata waktu load dashboard/report hingga tampil | avg(render_completed_at - request_at) | [TBD] | Detik | Harian | Application log | Dashboard Domain PO | Operational |
| KPI-DASH-03 | Report generation time | Dashboard & Analytics | KPI | Rata-rata waktu generate report snapshot | avg(generation_completed_at - requested_at) | [TBD] | Detik/Menit | Harian | Application log | Dashboard Domain PO | Operational |
| KPI-NOTIF-01 | Delivery success rate | Notification | KPI | Persentase notifikasi terkirim berhasil tanpa retry gagal permanen | successful_deliveries / total_notifications | [TBD] | % | Harian | Delivery Log | Integration Lead | Operational |
| KPI-NOTIF-02 | Average notification latency | Notification | KPI | Rata-rata waktu dari event terjadi sampai notifikasi terkirim | avg(delivered_at - event_occurred_at) | [TBD] | Detik | Harian | Delivery Log | Integration Lead | Operational |
| KPI-NOTIF-03 | SLA-breach alert lead time | Notification/SLA | SLA | Waktu dari SLABreached event sampai alert diterima penerima | avg(alert_delivered_at - breach_occurred_at) | [TBD] target ketat, mis. < 5 menit | Detik/Menit | Real-time | SLABreached + Delivery Log | Integration Lead | Supervisor |
| KPI-ADM-01 | % perubahan via konfigurasi (vs code change) | Administration | KPI | Persentase perubahan proses bisnis yang dilakukan via config, bukan rilis kode | config_changes / (config_changes + code_changes_for_business_rule) | [TBD] | % | Kuartalan | ConfigChanged event + release log | Administrator | Executive |
| KPI-ADM-02 | Config error rate | Administration | KPI | Persentase perubahan konfigurasi yang menyebabkan insiden/rollback | config_incidents / total_config_changes | [TBD] | % | Bulanan | Config Version + incident log | Administrator | Supervisor |
| KPI-ADM-03 | Time-to-apply change | Administration | KPI | Rata-rata waktu dari request perubahan konfigurasi sampai diterapkan | avg(applied_at - requested_at) | [TBD] | Jam | Bulanan | Config Version | Administrator | Supervisor |

## 2. SLA Matrix by Category/Priority
Struktur tabel disiapkan; nilai target SLA per kategori/prioritas **belum ada di Blueprint** dan wajib diisi Business Owner sebelum BR-ECMF-05 bisa berstatus Accepted.

| Category | Priority | SLA Target (respond) | SLA Target (resolve) | Business Calendar | Escalation Threshold |
|---|---|---|---|---|---|
| [TBD] | Critical | [TBD] | [TBD] | [TBD] | [TBD] |
| [TBD] | High | [TBD] | [TBD] | [TBD] | [TBD] |
| [TBD] | Medium | [TBD] | [TBD] | [TBD] | [TBD] |
| [TBD] | Low | [TBD] | [TBD] | [TBD] | [TBD] |

## 3. Business Calendar / Working Hours
`[TBD]` — belum didefinisikan di Blueprint. Perlu ditentukan: jam kerja standar, hari libur nasional, apakah SLA berjalan 24/7 atau hanya jam kerja (memengaruhi perhitungan SLA Clock).

## Open Items
- Semua kolom Target bertanda `[TBD]` — prioritas tertinggi karena memblok BR-ECMF-05, KPI-ECMF-03, KPI-ECMF-04, dan desain Notification eskalasi.
- SLA Matrix by category/priority (bagian 2) kosong nilainya — wajib workshop dengan Business Owner.
- KPI-KPI-04 (performance index) perlu definisi bobot komposit sebelum dapat diimplementasikan.

## Related
- `../02 Business Rules`
- `../03 Functional Requirements`
- `../08 Event Catalog`
