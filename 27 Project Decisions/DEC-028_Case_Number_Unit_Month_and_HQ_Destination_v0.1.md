# DEC-028 — Format nomor Case/pengaduan (BQ-004 opsi C) dan unit tujuan eskalasi Pusat

| Field | Value |
|---|---|
| ID | DEC-028 |
| Version | 0.1 |
| Owner | Product Owner |
| Status | 🟢 Accepted (lab Mode A) — 2026-08-22 |
| Date | 2026-08-22 |
| Related | BQ-004 / DEC-MODEA-B2-001 (format string only); DEC-025 (overlay identitas CM); FRD-CM-B2-001; CAP-008; FR-CM-010 (origin keeps read) |
| Type | Project Decision (identitas + proses eskalasi Mode A) — **bukan** Mode B unlock · **bukan** Board Resolution · **bukan** reopen independensi nomor Case |

---

## 1. Intent

Mengunci dua keputusan Product Owner 2026-08-22:

1. **String format** nomor Case (BQ-004) — independensi dari nomor pengaduan **tetap**.
2. Saat Pusat menerima eskalasi: Pusat menetapkan jam final **dan** unit tujuan; Pusat yang menginformasikan ke wajib pajak.

## 2. Decision

### 2.1 BQ-004 — format saja (opsi C)

Independensi: nomor Case **MUST NOT** memakai counter/nomor pengaduan. Tetap LOCKED.

| Identitas | Format | Contoh | Counter |
|---|---|---|---|
| Pengaduan (CM Aggregate) | `CM{UNIT}-YYMM-NNNN` | `CMTAB-2608-0001` | `cn:UNIT:YYYYMM` |
| Case | `UNIT-YYMM-NNNN` | `TAB-2608-0001` | `cs:UNIT:YYYYMM` |

`NNNN` mulai 4 digit dan melebar otomatis setelah 9999. Prefiks `CM` pada pengaduan **wajib** — tanpa itu nomor Case dan pengaduan bisa terlihat sama.

**Ditolak:** `CASE-YYYY-NNNNNN` (kunci 2026-08-01, format string saja); `CASE-YYYY-NNNN` (`e1440d9`).

**Lab:** migrasi `0096` membuang baris counter Case lama. Data lab nomor `CASE-…` tidak dilestarikan. Produksi nanti wajib jalur data terpisah — bukan drop diam-diam.

**Overlay DEC-025 §15:** baris CM Aggregate = `CM{UNIT}-YYMM-NNNN`; CM Case = `UNIT-YYMM-NNNN`. Tubuh DEC-025 tidak di-rewrite.

### 2.2 Eskalasi ke Pusat — jam, unit tujuan, siapa mengabari

Saat Pusat menerima eskalasi pengaduan WP:

1. Pusat menetapkan **jam kedatangan final** dan **unit tujuan** di Pusat (CRO / Sekretariat / Suban).
2. Unit tujuan disimpan di kolom terpisah dari `owning_unit_id`. Unit asal cabang **tetap** pemilik visibilitas asal (FR-CM-010: origin keeps read). Menimpa `owning_unit_id` dengan sub-unit Pusat **dilarang**.
3. Yang menginformasikan jadwal dan unit tujuan ke wajib pajak: **Pusat**, bukan CRO cabang.

Konsekuensi otorisasi (bukan daftar enumerasi produk): kode `PUSAT`, `PUSAT-CRO`, `PUSAT-SUBAN-*`, dan akar setara (`HO` / `HEAD_OFFICE`) dihitung sebagai Pusat. Pemisah wajib (`-` / `.` / `/`). `PUSATAKA` **bukan** Pusat.

### 2.3 Di luar keputusan ini

| Topik | Status |
|---|---|
| Independensi nomor Case vs pengaduan | Tidak dibuka |
| Mode B / SSO / Identity Adapter | CLOSED |
| Force-merge Dual-SoT / retire path | Tidak |
| Batalkan Eskalasi dari halaman Case | Bukan keputusan baru — aksi tetap pada pengaduan induk |

## 3. Acceptance

1. Create Case menghasilkan `UNIT-YYMM-NNNN` unik, bukan `CASE-YYYY-*`.
2. Create pengaduan menghasilkan `CM{UNIT}-YYMM-NNNN`.
3. Terima eskalasi Pusat menolak tanpa unit tujuan; `owning_unit_id` cabang tidak ditimpa.
4. Copy operator: Pusat yang mengabari WP.

## 4. Catalog sync

Lock pack DEC-MODEA-B2-001 (BQ-004 format) · DM-MODEA-B2-001 · BR-CM-CAT Mode A notes · FRD-CM-B2-001 · OpenAPI `cm-case-management.v1.yaml` · CAP-008 · BC-9.9 / BR-CAS-001 / BW-000 WS-02 · DL-070.

UAT package `v1.2.0` tetap artefak historis (ekspektasi `CASE-YYYY-NNNNNN`).
