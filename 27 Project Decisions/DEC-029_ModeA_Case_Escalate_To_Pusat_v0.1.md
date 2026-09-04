# DEC-029 — Eskalasi ke Pusat dari Case (bukan pengaduan induk)

| Field | Value |
|---|---|
| ID | DEC-029 |
| Version | 0.2 |
| Owner | Product Owner |
| Status | 🟢 Accepted with Conditions (product authorization 2026-08-22; amend jadwal 2026-08-27) |
| Date | 2026-08-22 (amend 2026-08-27) |
| Basis | `18 Architecture Governance/board-drafts/BOARD-DRAFT_ModeA_Case_Escalate_To_Pusat_API520_v0.1.md` vote **ACCEPT WITH CONDITIONS** |
| Related | BR-007 · API-520 · BQ-009 · DEC-021 (butir 5, amend sempit) · DEC-028 · CAP-008 |
| Type | Project Decision (Mode A lab) — **bukan** Mode B unlock · **bukan** EPIC-CM-F4 utuh |

---

## 1. Intent

Eskalasi Cabang → Pusat diajukan dari **Case** yang tidak bisa diselesaikan di cabang. Pengaduan induk tidak dipakai sebagai jalur ajuan (satu induk boleh banyak Case).

## 2. Decision

1. Unlock lab **API-520**: `POST /api/v1/cm/cases/{caseId}/escalate-to-pusat`.
2. CTA **Ajukan eskalasi ke Pusat** di halaman Case. Eskalasi **bukan** aksi resolve (`ACCEPT` / `PROPOSE`).
3. **Cabut CTA eskalasi di pengaduan induk** dalam slice yang sama, setelah jalur Case hidup: form daftar eskalasi, ajuan ulang di konfirmasi, deep-link `?action=escalate` ke induk.
4. Hanya Case yang diajukan yang ke Pusat. Sibling **tidak** di-eskalasi. Induk **boleh** `intakeDisposition=ESCALATE_APPROVED` sebagai **pintu jadwal Pusat** (Terima & jadwalkan) — bukan klaim sibling, bukan status `ESCALATED`.
5. **BQ-009 tetap:** Mode A tidak menampilkan status `ESCALATED`. Case tetap status ter-expose (`IN_PROGRESS` bila perlu naik dari CREATED/ASSIGNED). Ownership Pusat = flag `escalatedToPusat` / `owningUnit=PUSAT`, **bukan** menimpa `owning_unit_id` cabang (DEC-028).
6. Alasan eskalasi wajib (minimum 20 karakter, selaras ajuan cabang yang sudah ada).
7. **Amend 2026-08-23:** putusan intake per Case (`/complaints/new/escalate`) boleh memanggil API-520 segera setelah Case dibuat. CTA/deep-link eskalasi di **pengaduan induk** tetap dicabut (butir 3). Sibling Case tidak ikut.
8. **Amend 2026-08-27:** makna ajuan Cabang→Pusat = **minta jadwal agar pengaduan diselesaikan di Pusat**. CTA Pusat yang benar: **Terima & jadwalkan**, bukan klaim penanganan (`HANDLE_CLAIM`). Usulan slot cabang (`proposedArrivalDate` / `proposedArrivalTime`) **opsional**; Pusat yang mengunci CRO. GET Case menyembuhkan pintu induk bila Case masih di Pusat tetapi induk sudah `RETURNED_TO_BRANCH`.

## 3. Conditions

- Dual-SoT DEC-020 tidak berubah.
- Mode B / Identity Adapter CLOSED.
- API-521…526 (return, antrian Pusat, `result_visibility`) **tidak** di-unlock.
- DEC-021 butir 1–4 dan 6 tetap. Butir 5 (UI eskalasi → induk) **disupersede**: tempat ajuan = Case.

## 4. Acceptance

1. Dari halaman Case terbuka **atau** putusan intake per Case, petugas cabang dapat mengajukan eskalasi ke Pusat dengan alasan (usulan slot opsional).
2. Sibling Case pada induk yang sama tetap di cabang.
3. Form/tombol eskalasi di induk tidak lagi menawarkan ajuan baru.
4. Response/UI Mode A tidak memakai label status `ESCALATED`.
5. Setelah ajuan, Pusat melihat **Terima & jadwalkan** pada Case/induk (`ESCALATE_APPROVED`); klaim penanganan bukan CTA utama.
