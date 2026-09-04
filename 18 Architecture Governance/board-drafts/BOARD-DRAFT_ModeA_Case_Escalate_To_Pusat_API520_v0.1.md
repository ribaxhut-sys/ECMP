# BOARD-DRAFT — Mode A: eskalasi ke Pusat dari Case (bukan pengaduan induk)

**Status:** ACCEPTED WITH CONDITIONS (product authorization 2026-08-22 → **DEC-029**)  
**Date:** 2026-08-22  
**Scope:** CAP-008 Mode A lab — ajuan eskalasi Cabang → Pusat pada **Case** (`API-520`)  
**Out of scope:** Mode B · Identity Adapter · DEC-F4 penuh (return, antrian Pusat, `result_visibility`) · auto-close pengaduan induk (BQ-007)

---

## 1. Request (one sentence)

Izinkan petugas **mengajukan eskalasi ke Pusat dari halaman Case**, dan **hapus jalur eskalasi di pengaduan induk**, tanpa menampilkan status `ESCALATED` di Mode A (BQ-009) dan tanpa menjadikan eskalasi sebagai aksi resolve Case.

---

## 2. Business intent

Satu pengaduan boleh punya beberapa Case. Jika satu Case tidak bisa diselesaikan di cabang, **hanya Case itu** yang ke Pusat. Sibling Case di induk yang sama tetap dikerjakan di cabang.

Pengaduan induk adalah jejak agregat, bukan objek eskalasi. Unit kerja yang di-assign, diukur SLA, dieskalasikan, dan diselesaikan adalah **Case** (BR-007).

---

## 3. What is already LOCKED (do not reopen)

| ID | Rule | Stay |
|----|------|------|
| **BQ-009** | Mode A **tidak menampilkan** `PENDING` / `ESCALATED` | **Tetap** — wire/UI Mode A tidak memakai label `ESCALATED` |
| **BQ-007** | Tutup Case ≠ tutup pengaduan induk | **Tetap** |
| **DEC-021** butir 1–4, 6 | Tutup Case = comment (+ lampiran opsional); eskalasi **bukan** `ACCEPT`/`PROPOSE` | **Tetap** |
| **DEC-F4** path | Cabang → Pusat (tanpa Regional) | **Tetap** — detail return / visibilitas / `result_visibility` tetap OOS sampai countersign |
| Dual-SoT **DEC-020** | Coexistence catalog | **Tetap** |
| Mode B / C-B6-1 | CLOSED | **Tetap CLOSED** |

---

## 4. What Board must decide (SoT change)

### Option recommended — **Unlock lab API-520 + retire eskalasi di induk**

| Layer | Today | Proposed |
|-------|--------|----------|
| UX Case | **Selesaikan → Eskalasi** hanya mengarah ke induk (`?focus=penanganan&action=escalate`) | Tombol **Ajukan eskalasi ke Pusat** di halaman Case; alasan wajib; **bukan** aksi resolve |
| UX induk | Form daftar eskalasi, ajuan ulang (`API-518`), `allowEscalate` di tabel Case | **Cabut CTA eskalasi di induk** dalam slice yang sama setelah API-520 lab hidup — jangan cabut lebih dulu |
| OpenAPI | `complaint-management-esc-res.v1.yaml` API-520 **Planned** | Unlock **lab Mode A API-520 saja** (`POST /api/v1/cm/cases/{caseId}/escalate-to-pusat`) |
| Domain Case | `ESCALATED` tidak di-expose (BQ-009); transisi ditolak | Ownership **per Case** ke Pusat (`owningUnit=PUSAT` atau field setara). Status wire Mode A tetap ter-expose (`IN_PROGRESS` atau setara). Matrix Aggregate boleh tetap mendefinisikan `ESCALATED` tanpa diekspos delivery |
| Pengaduan induk | `intakeDisposition` menarik **seluruh** pengaduan ke jalur Pusat | Induk **tidak** menarik sibling Case ke Pusat hanya karena satu Case dieskalasikan |
| DEC-021 butir 5 | “Eskalasi UI → pengaduan induk” | **Supersede sempit:** eskalasi tetap bukan resolve; **tempat ajuan = Case** |

### Explicitly **reject** (unless separate Board item)

- Menjadikan eskalasi sebagai `action` pada API-534 (`ACCEPT` / `PROPOSE` / `REJECT`)
- Mengekspos label/status `ESCALATED` di Mode A (melanggar BQ-009)
- Unlock API-521…526 (return, antrian Pusat, `result_visibility`) dalam vote ini
- Coding Mode B / Identity Adapter / enterprise `securitySchemes`
- Menghapus CTA induk **sebelum** jalur Case hidup (lab kehilangan satu-satunya ajuan)

---

## 5. Delivery sequence (after Accept)

Satu slice, urutan wajib:

1. Implementasi lab API-520 + CTA di halaman Case  
2. Baru cabut jalur eskalasi di induk (form `/complaints/new/escalate`, ajuan ulang di konfirmasi, deep-link `action=escalate` ke induk)

---

## 6. Impact checklist (after Board Accept)

- [x] `07 API Catalog/openapi/complaint-management-esc-res.v1.yaml` — API-520 lab (bukan 521…526)
- [x] OpenAPI/catalog Mode A Case bila perlu field ownership tanpa label `ESCALATED`
- [x] `backend` Case domain + tes (BQ-009 tetap)
- [x] `frontend/src/features/cases/CaseDetailView.tsx` — CTA ajuan eskalasi
- [x] Cabut CTA/API pemakaian eskalasi di induk (`EscalateIntakeView`, `requestCmBatch1IntakeEscalation` di konfirmasi, `allowEscalate` di tabel)
- [x] DEC-021 butir 5 — amend sempit setelah vote
- [x] Traceability / tes sinkron  

**Not changed by this draft:** Dual-SoT DEC-020 · Mode B CLOSED · Identity Adapter · return Pusat · antrian Pusat  

---

## 7. Decision options for Board

| Vote | Meaning |
|------|---------|
| **ACCEPT WITH CONDITIONS** | Unlock lab API-520; eskalasi hanya dari Case; cabut jalur induk dalam slice yang sama; BQ-009 tetap; F4 penuh tetap OOS |
| **DEFER** | Biarkan hedge induk sampai EPIC-CM-F4 di-unlock utuh |
| **REJECT** | Eskalasi tetap di pengaduan induk |

---

## 8. Ask

Board: **Accept with Conditions** agar engineering boleh mengimplementasikan ajuan eskalasi ke Pusat **dari Case** dan menghapus jalur eskalasi di induk, tanpa membuka mesin DEC-F4 penuh dan tanpa menampilkan `ESCALATED` di Mode A?

---

*Draft only — bukan Board Resolution. Jangan dianggap unlock Mode B atau EPIC-CM-F4 utuh (API-521…526).*
