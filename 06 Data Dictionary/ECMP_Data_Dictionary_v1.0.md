# ECMP Data Dictionary v1.0

| Field | Value |
|---|---|
| ID | DD-001 |
| Version | 1.1 |
| Owner | Data Architect / BA Lead |
| Reviewer | Solution Architect, Domain POs, Compliance |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Kamus data awal ECMP, disusun dari daftar "Data Konseptual" per domain di `01 Business Blueprint`. Level saat ini adalah **entity list by domain** (checklist item pertama). Detail atribut lengkap per entity akan diisi bertahap saat FRD (`03`) tiap domain dikerjakan — entity yang sudah punya skema fisik Sprint-01 (Case Header, Audit Log, Outbox) plus Customer Reference dan sketsa Config Version terdokumentasi di bagian 2. ERD Sprint-01 tersedia di [`ECMP_ERD_Sprint01_v0.1.md`](./ECMP_ERD_Sprint01_v0.1.md).

Catatan format: disimpan sebagai Markdown (bukan `.xlsx`) mengikuti Format Policy README utama (maintainable source diutamakan). Bila dibutuhkan untuk distribusi stakeholder formal, konversi ke `ECMP_Data_Dictionary_v1.0.xlsx` sesuai naming convention.

## 1. Entity List by Domain

> **Makna kolom Owner:** *business steward* (penanggung jawab kualitas/kebijakan data), bukan domain SoT teknis. Kepemilikan domain (SoT) mengikuti tabel Data Ownership di `20 Domain Architecture/<domain>/README.md` — mis. Audit Log di-steward Security Officer tetapi SoT domainnya Core Platform; Customer Reference di-steward CRM PO tetapi SoR-nya Customer Master eksternal (ADR-002).

| Entity | Domain | Description | Source System | Owner | PII/Sensitive | Notes |
|---|---|---|---|---|---|---|
| User | Core Platform | Akun pengguna internal ECMP | ECMP (native) | Core Platform PO | Y (nama, email, org) | Terkait Role via mapping |
| Role | Core Platform | Definisi peran dan kumpulan permission | ECMP (native) | Core Platform PO | N | Configurable, lihat BR-CP-02 |
| Permission | Core Platform | Hak akses granular ke fungsi/data | ECMP (native) | Core Platform PO | N | Dipetakan ke Role |
| Organization Unit | Core Platform | Struktur unit/organisasi pengguna | ECMP (native) atau sinkron HR system [TBD] | Core Platform PO | N | Menentukan scope otorisasi (BR-CP-02) |
| Config Parameter | Core Platform | Parameter sistem yang configurable | ECMP (native) | Administrator | N | Wajib versioned (BR-ADM-03) |
| Audit Log | Core Platform | Jejak aktivitas immutable seluruh modul | ECMP (native) | Security Officer | Y (jejak aktivitas user) | Tidak dapat dihapus (BR-CP-03) |
| Customer Reference | CRM | Referensi/cache read-only data pelanggan dari Customer Master | Customer Master (eksternal, read-only) | CRM Domain PO | Y (data pribadi pelanggan) | Bukan SoR — lihat ADR-002 |
| Contact Channel | CRM | Kanal kontak pelanggan (telepon, email, dll) | Customer Master (sync) | CRM Domain PO | Y | Bagian dari Customer Reference |
| Interaction History | CRM | Catatan interaksi dengan pelanggan | ECMP (native) | CRM Domain PO | Y (konten interaksi bisa sensitif) | Tertaut ke Customer ID (BR-CRM-03) |
| Related Cases | CRM | Daftar case yang terkait dengan pelanggan | ECMP (native, dari ECMF) | CRM Domain PO | Y | Referensi ke Case Header |
| Customer Notes | CRM | Catatan konteks tambahan untuk layanan | ECMP (native) | CRM Domain PO | Y | Perlu retention policy [TBD] |
| Case Header | ECMF | Data inti complaint/inquiry (case_type, prioritas, status, subject) | ECMP (native) | ECMF Domain PO | Y (terhubung ke Customer) | Entity transaksional utama; detail atribut di bagian 2 |
| Case Activity | ECMF | Log aktivitas per case | ECMP (native) | ECMF Domain PO | Y | Bagian dari audit trail case |
| Attachment | ECMF | Berkas bukti/dokumen pendukung case | ECMP (native, storage terpisah) | ECMF Domain PO | Y (bisa memuat data sensitif) | Perlu kebijakan retensi & scanning |
| Comment | ECMF | Komentar internal/eksternal pada case | ECMP (native) | ECMF Domain PO | Y | Perlu klasifikasi internal vs customer-facing |
| Status History | ECMF | Riwayat perubahan status case | ECMP (native) | ECMF Domain PO | N | Basis perhitungan SLA Clock |
| SLA Clock | ECMF | Timer SLA berjalan per case/tahapan | ECMP (native) | ECMF Domain PO | N | Nilai berjalan milik ECMF; formula/aturan di `11 SLA and KPI Matrix` (steward kebijakan: Operations Lead) |
| Root Cause | ECMF | Penyebab utama masalah pada closure | ECMP (native) | ECMF Domain PO | N | Wajib untuk kategori tertentu [TBD] |
| Resolution | ECMF | Hasil penanganan yang menutup case | ECMP (native) | ECMF Domain PO | Y (bisa memuat detail pelanggan) | Wajib saat closure (BR-ECMF-06) |
| Metric Definition | KPI & Performance | Definisi metrik, formula, owner, periode | ECMP (native) | Performance Analyst | N | Governance-controlled (BR-KPI-02) |
| Target | KPI & Performance | Target nilai KPI per periode/unit | ECMP (native) | Performance Analyst | N | — |
| SLA Rule | KPI & Performance | Aturan SLA per kategori/prioritas | ECMP (native) | Administrator | N | Entitas yang sama dengan SLA Config (SoT: Administration, ADR-008); KPI hanya membaca nilai aktif via EVT-006 |
| Performance Fact | KPI & Performance | Hasil perhitungan KPI (fact table) | ECMP (native, derived dari event) | Performance Analyst | N | Harus traceable ke transaksi sumber (BR-KPI-04) |
| Breach Event | KPI & Performance | Kejadian pelanggaran SLA | ECMP (native, dari event SLABreached) | Performance Analyst | N | Trigger Notification |
| Dashboard Widget Config | Dashboard & Analytics | Konfigurasi tampilan widget per persona | ECMP (native) | Dashboard Domain PO | N | — |
| Aggregated Metrics | Dashboard & Analytics | Data agregat untuk dashboard | ECMP (native, derived) | Dashboard Domain PO | N | Harus reconcile ke sumber (BR-DASH-02) |
| Saved Filter | Dashboard & Analytics | Filter tersimpan milik user | ECMP (native) | Dashboard Domain PO | N | — |
| Report Snapshot | Dashboard & Analytics | Snapshot laporan pada titik waktu tertentu | ECMP (native) | Dashboard Domain PO | Y (bila memuat data pelanggan) | Perlu retention policy [TBD] |
| Event Type | Notification | Definisi jenis domain event yang bisa memicu notifikasi | ECMP (native) | Integration Lead | N | Selaras `08 Event Catalog` |
| Notification Rule | Notification | Aturan routing event ke penerima | ECMP (native) | Integration Lead | N | Configurable (BR-NOTIF-01) |
| Template | Notification | Template pesan notifikasi | ECMP (native) | Integration Lead | N | — |
| Delivery Log | Notification | Riwayat pengiriman & status | ECMP (native) | Integration Lead | Y (bisa memuat kontak penerima) | Wajib disimpan (BR-NOTIF-03) |
| Recipient | Notification | Penerima notifikasi (user/role/eksternal) | ECMP (native) | Integration Lead | Y (kontak) | Resolusi dinamis dari role/assignment |
| Reference Data | Administration | Data referensi/lookup (kategori, status, dll) | ECMP (native) | Administrator | N | — |
| SLA Config | Administration | Parameter SLA & kalender kerja | ECMP (native) | Administrator | N | Sumber BR-ECMF-05 |
| Workflow Config | Administration | Definisi transisi status yang diizinkan | ECMP (native) | Administrator | N | Sumber BR-ECMF-03 |
| Role-Permission Matrix | Administration | Pemetaan role ke permission | ECMP Core Platform (SoT — ADR-008) | Administrator | N | Config view, non-SoT — Administration hanya konfigurator; SoT = Core Platform Role/Permission (ADR-008) |
| Config Version | Administration | Riwayat versi konfigurasi | ECMP (native) | Administrator | N | Mendukung BR-ADM-03; sketsa atribut di bagian 2 (Planned) |

## 2. Contoh Detail Atribut (starting point untuk FRD)

### Entity: Case Header (ECMF) — selaras skema fisik Sprint-01 (tabel `cases`) + FRD-001 v0.2
| Attribute | Description | Data Type | Mandatory | Source System | PII | Sample Value | Notes |
|---|---|---|---|---|---|---|---|
| case_id | Identifier unik case | String(32) | Y | ECMP | N | CASE-A1B2C3D4E5 | Primary key; format `CASE-<10-hex>` uppercase, pattern `^CASE-[0-9A-F]{10}$` (FRD-001) |
| customer_id | Referensi ke Customer Reference | String(64) | Y | ECMP (link ke CRM) | Y | CUST-88213 | FK logis ke domain CRM; indexed |
| case_type | Jenis case (COMPLAINT/INQUIRY) | String(32) | Y | ECMP | N | COMPLAINT | Sebelumnya bernama `category`; distandarkan `case_type` mengikuti skema fisik & FRD |
| priority | Prioritas penanganan | String(16) | Y | ECMP | N | HIGH | LOW/MEDIUM/HIGH/CRITICAL; memengaruhi SLA Clock |
| subject | Ringkasan singkat case | String(200) | Y | ECMP | Y (bisa memuat konteks pelanggan) | "Billing discrepancy" | — |
| description | Uraian lengkap case | Text | Y | ECMP | Y (bisa memuat konteks pelanggan) | — | Max 5000 char di API |
| status | Status case saat ini | String(32) | Y | ECMP | N | REGISTERED | Sprint-01 hanya status awal; transisi mengikuti Workflow Config (enum SoT: `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md`) |
| channel | Kanal masuknya case | String(32) | N | ECMP | N | CALL | Nullable |
| customer_verified | Hasil verifikasi ke Customer Master | Boolean | Y | ECMP | N | false | Default `false`; selalu `false` selama mode stub (INT-001, FRD §8) |
| created_at | Waktu case dibuat | Timestamp (UTC) | Y | ECMP | N | 2026-07-21T09:00:00Z | Immutable; lihat Standar Kolom Audit |
| created_by | User pembuat case | String(64) | Y | ECMP | Y | USR-4471 | Lihat Standar Kolom Audit |
| updated_at | Waktu perubahan terakhir | Timestamp (UTC) | Y | ECMP | N | 2026-07-21T09:00:00Z | Lihat Standar Kolom Audit |
| updated_by | User pengubah terakhir | String(64) | Y | ECMP | Y | USR-4471 | Lihat Standar Kolom Audit |

Catatan penyimpangan dari versi sebelumnya:
- `category` → diganti `case_type` (mengikuti skema fisik dan FRD-001).
- Sample `case_id` lama (`CASE-2026-000123`) menyimpang dari format resmi `CASE-<10-hex>` — sudah diperbaiki.
- `assignee_id` belum ada di skema fisik Sprint-01 — masuk fase assignment (Sprint-02, API-003).
- `sla_due_at` dipindah ke fase SLA (belum ada di skema fisik Sprint-01; dihitung dari SLA Config saat fase SLA dikerjakan).

### Entity: Customer Reference (CRM)
| Attribute | Description | Data Type | Mandatory | Source System | PII | Sample Value | Notes |
|---|---|---|---|---|---|---|---|
| customer_id | Identifier pelanggan dari Customer Master | String | Y | Customer Master | Y | CUST-88213 | Read-only, tidak boleh write-back |
| full_name | Nama lengkap pelanggan | String | Y | Customer Master | Y | [TBD masking rule] | PII tinggi |
| contact_channel | Kanal kontak (email/phone) | Array | N | Customer Master | Y | — | Lihat entity Contact Channel |
| last_synced_at | Waktu terakhir sinkron dari master | Timestamp | Y | ECMP (derived) | N | 2026-07-21T06:00:00Z | Wajib ditampilkan ke user (ADR-002) |

### Entity: Audit Log (Core Platform) — selaras skema fisik Sprint-01 (tabel `audit_log`)
| Attribute | Description | Data Type | Mandatory | Source System | PII | Sample Value | Notes |
|---|---|---|---|---|---|---|---|
| log_id | Identifier unik entri log | String(36)/UUID | Y | ECMP | N | — | Primary key |
| actor_user_id | User yang melakukan aksi | String(64) | Y | ECMP | Y | USR-4471 | — |
| action | Jenis aksi | String(64) | Y | ECMP | N | case.create | Verb lowercase bertitik (lihat catatan konvensi di bawah) |
| entity_type | Tipe entity yang terdampak | String(64) | Y | ECMP | N | Case | PascalCase; indexed bersama `entity_id` |
| entity_id | Identifier entity yang terdampak | String(64) | Y | ECMP | N | CASE-A1B2C3D4E5 | — |
| new_value | Nilai sesudah aksi | JSON | Y | ECMP | Tergantung entity | — | Skema Sprint-01 hanya menyimpan `new_value`; `old_value` menyusul saat ada mutasi (update/status change) |
| occurred_at | Waktu kejadian | Timestamp (UTC) | Y | ECMP | N | — | Immutable, append-only (BR-CP-03) |

> **Konvensi nilai audit** (selaras implementasi `implementation/backend/app/service.py` dan `21 Technical Standards` §4):
> `action` memakai verb lowercase bertitik (`case.create`, `case.assign`, ...), dan `entity_type` memakai nama entity PascalCase (`Case`, `AuditLog`, ...).
> Gaya ini **sengaja berbeda** dari gaya enum UPPER_SNAKE (mis. `REGISTERED`, `COMPLAINT`) yang dipakai untuk nilai enum bisnis.

### Entity: Outbox (Core Platform) — selaras skema fisik Sprint-01 (tabel `outbox`)
Pola transactional outbox per ADR-009 (message broker ditunda); event ditulis satu transaksi dengan data bisnis, publikasi menyusul.

| Attribute | Description | Data Type | Mandatory | Source System | PII | Sample Value | Notes |
|---|---|---|---|---|---|---|---|
| outbox_id | Identifier unik record outbox | String(36)/UUID | Y | ECMP | N | — | Primary key |
| event_id | ID event dari Event Catalog | String(16) | Y | ECMP | N | EVT-001 | Lihat `../08 Event Catalog` |
| event_name | Nama event | String(64) | Y | ECMP | N | CaseCreated | — |
| payload | Isi event | JSON | Y | ECMP | Tergantung event | — | Skema payload di Event Catalog |
| created_at | Waktu record dibuat | Timestamp (UTC) | Y | ECMP | N | — | — |
| published_at | Waktu event dipublikasikan | Timestamp (UTC) | N | ECMP | N | — | Null = belum published; index komposit `(published_at, created_at)` untuk polling terurut |

### Entity: Config Version (Administration) — sketsa, status Planned (BR-ADM-03)
| Attribute | Description | Data Type | Mandatory | Source System | PII | Sample Value | Notes |
|---|---|---|---|---|---|---|---|
| config_key | Kunci konfigurasi | String | Y | ECMP | N | sla.default_hours | — |
| version | Nomor versi konfigurasi | Integer | Y | ECMP | N | 3 | Monoton naik per config_key |
| effective_from | Mulai berlaku | Timestamp (UTC) | Y | ECMP | N | — | — |
| effective_to | Berakhir berlaku | Timestamp (UTC) | N | ECMP | N | — | Null = masih aktif |
| payload | Isi konfigurasi versi tersebut | JSON | Y | ECMP | N | — | — |
| created_by | User pembuat versi | String | Y | ECMP | Y | USR-4471 | — |
| created_at | Waktu versi dibuat | Timestamp (UTC) | Y | ECMP | N | — | — |
| updated_at | Waktu perubahan terakhir | Timestamp (UTC) | Y | ECMP | N | — | Diperlukan karena `effective_to` diisi saat versi digantikan (entitas mutable — Standar Kolom Audit §3) |
| updated_by | User pengubah terakhir | String | Y | ECMP | Y | — | Lihat Standar Kolom Audit §3 |

Status: **Planned** — belum ada di skema fisik Sprint-01; mendukung BR-ADM-03 (konfigurasi wajib versioned).

## 3. Standar Kolom Audit
Berlaku untuk semua **entitas mutable** (contoh: `cases`):
- `created_at` (Timestamp UTC, mandatory, immutable) — waktu record dibuat.
- `created_by` (String user id, mandatory, immutable) — pembuat record.
- `updated_at` (Timestamp UTC, mandatory) — waktu perubahan terakhir; saat create diisi sama dengan `created_at`.
- `updated_by` (String user id, mandatory) — pengubah terakhir.

Ketentuan:
- `audit_log` bersifat **append-only** (tidak boleh update/delete — BR-CP-03) sehingga hanya memakai `occurred_at`, tanpa kolom updated_*.
- Semua timestamp disimpan dan dipertukarkan dalam **UTC** (ISO-8601 di API, `DateTime(timezone=True)` di DB).

## 4. Naming Standard
- Database menggunakan **snake_case**; API dan event payload menggunakan **camelCase** (lihat `../21 Technical Standards`).
- Mapping bersifat mekanis 1:1 untuk field yang diekspos; field yang sengaja tidak diekspos ditandai. Contoh:

| DB (snake_case) | API/Event (camelCase) |
|---|---|
| case_id | caseId |
| customer_id | customerId |
| case_type | caseType |
| customer_verified | customerVerified |
| created_at | createdAt |
| created_by | createdBy |
| updated_at | updatedAt |
| updated_by | — (sengaja **tidak diekspos** di response API — kebijakan kontrak, lihat `21 Technical Standards` §4) |

## Open Items
- Attribute-level detail untuk entity selain yang sudah didetailkan di bagian 2 menyusul saat FRD per domain dikerjakan.
- PII classification di atas masih level indikatif (Y/N) — perlu review Compliance untuk menentukan tingkat sensitivitas dan masking rule (lihat `17 Compliance`, `10 Security and Access Standards`).
- ~~Role-Permission Matrix muncul di dua domain (Core Platform vs Administration) — perlu diputuskan satu source of truth.~~ **Resolved**: SoT = Core Platform, Administration = konfigurator (config view, non-SoT) — lihat ADR-008.
- Retention policy untuk Attachment, Customer Notes, Report Snapshot: baseline ditetapkan di [`../17 Compliance/ECMP_Data_Retention_Policy_v0.1.md`](../17%20Compliance/ECMP_Data_Retention_Policy_v0.1.md) (baseline menunggu konfirmasi Legal via DEC).

## Related
- `../01 Business Blueprint`
- `../03 Functional Requirements`
- `../09 Integration Catalog`
- `../10 Security and Access Standards`
- `../05 Architecture Decision Records/ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0.md`
