# Open Questions

| Field | Value |
|---|---|
| ID | OQ-000 |
| Version | 0.2 |
| Owner | PMO |
| Reviewer | Product Owner |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-08-01 |
| Next Review | 2026-10-21 |

| ID | Question | Raised By | Date | Status | Owner | Target Decision Date |
|---|---|---|---|---|---|---|
| OQ-001 | Apakah Channel app masuk fase 1 atau hanya integration boundary? | Architecture | 2026-07-21 | Open | Business Owner | TBD |
| OQ-002 | Stack frontend/backend final untuk standar teknis? | Engineering | 2026-07-21 | Resolved (backend) | Tech Lead | 2026-07-21 |
| OQ-003 | Apakah CQRS diadopsi sekarang atau ditunda? | Architecture | 2026-07-21 | Resolved | Solution Architect | 2026-07-21 |
| OQ-004 | Baseline bisnis: Blueprint/FRD vs brief discovery (branch/HO/scheduling)? | ARB | 2026-07-21 | Resolved | Business Owner | 2026-07-21 |
| OQ-005 | Otorisasi build: Sprint-01 GO vs gate G0? | ARB | 2026-07-21 | Resolved | Engineering Manager | 2026-07-21 |
| OQ-006 | Skema ID Business Rule ganda (BR-0xx vs BR-Domain-NN)? | ARB | 2026-07-21 | Resolved | BA Lead | 2026-07-21 |
| OQ-007 | Audit-on-read: wajib atau ditunda? | ARB | 2026-07-21 | Resolved | Business Owner | 2026-07-21 |
| OQ-008 | Target numerik SLA (respon/resolusi per prioritas) dan NFR (availability/latency/RTO-RPO)? | Operations | 2026-07-21 | Resolved | Business Owner | 2026-07-21 |
| OQ-CM-B1-001 | DEC remapping: when does BR-CM-CAT-001 / Complaint Aggregate replace Sprint delivery SoT for implementation? | Architecture / FRD-CM-001 | 2026-07-29 | Closed | Architecture Board | 2026-07-30 |
| OQ-CM-B1-004 | Production policy for when Batch 2 Case create becomes mandatory after REGISTERED | Architecture / FRD-CM-001 | 2026-07-29 | **CLOSED** | Domain PO ECMF / Product Owner | 2026-08-01 |
| BQ-001 | Case State Machine SoT for Batch-2 Mode A: DOM-ECMF-003 vs BR-CM-CAT Definition B? | Architecture / CAP-008 | 2026-08-01 | **CLOSED** | Architecture Board / Business Owner | 2026-08-01 |
| BQ-002 … BQ-014 | Mode A Delivery Baseline residual BQs (Case Management Batch-2) | Product Owner Session | 2026-08-01 | **CLOSED** (all LOCKED) | Product Owner | 2026-08-01 |
| BQ-CAP006-01 … 15 | CAP-006 SLA Engine residual BQs (calendar, clock, pause, EVT-004, ownership, …) | ARB / B2-15 | 2026-08-01 | **CLOSED** (DEFERRED items explicit) | Business Owner / Performance Owner | 2026-08-01 |
| OQ-ORG-001 | Descendant org scope for AuthZ (ADR-018 O-06)? | Architecture | 2026-07-31 | Open — Proposed DEC-021 (exact-ref interim) | Solution Architect / BO | TBD |
| OQ-ORG-002 | Upstream org restructure / orphan remediation (ADR-018 O-07)? | Architecture | 2026-07-31 | Open — Proposed DEC-022 (retain + fail-closed interim) | Solution Architect / BO | TBD |
| OQ-IAM-001 | Namespace permission per bounded context: apakah `complaints:*` dipecah jadi `cm:*` / `bc:*` / `case:*` / `internal:*`, dan siapa pemegang `queue:manage` / `customers:update` sebenarnya? | Engineering (temuan permission split) | 2026-08-13 | **CLOSED** (owner decision 2026-08-22, lihat Resolutions) | Architecture Board / Business Owner | 2026-08-22 |
| OQ-INT-001 | Pengaduan Internal: gerbang Agent atas transfer Handling ke unit lawan (Cabang↔Pusat) — bentuk gerbang, izin putusan, skema nomor, saluran notifikasi | Product Owner Session | 2026-08-14 | **CLOSED** (owner decision, lihat Resolutions) | Product Owner | 2026-08-14 |

## Resolutions
- **OQ-002 (partial):** Backend stack dikunci di `ADR-004` (Python/FastAPI/PostgreSQL). Frontend tetap deferred.
- **OQ-003:** CQRS **ditunda** — tidak relevan untuk slice 2-endpoint; revisit saat ada kebutuhan read-model nyata (ADR-005 layering mencatat deferral).
- **OQ-004:** Blueprint v2.1 + FRD-001 = SoT; model branch/HO/scheduling di luar lingkup. Lihat `DEC-001`.
- **OQ-005:** GO = slice + G0 floor; Build-1 menunggu G0 exit. Lihat `DEC-002`.
- **OQ-006:** SoT delivery = `BR-0xx`; katalog enterprise jadi referensi dengan tabel pemetaan. Lihat `DEC-003`.
- **OQ-007:** Write-audit wajib (BR-008/FR-001c); read-audit ditunda; idempotency key di luar AC Sprint-01. Lihat FRD-001 §9 + `DEC-002`.
- **OQ-008:** Ditutup dengan nilai baseline konservatif (SLA per prioritas, warning 80%, NFR availability/latency/throughput/kapasitas/RTO-RPO) — reversible BO via DEC. Lihat `DEC-005`.
- **OQ-CM-B1-001:** **Closed — remapped by dual SoT (DEC-020), retired by DEC-026**. M-026-1…3 executed (FE redirect + HTTP unmount + DROP migration 0072). Mode A complaint SoT = `/api/v1/cm` + Case. CA BC out of retire set. Lihat `DEC-020`, `DEC-025`, `DEC-026`.
- **OQ-CM-B1-004 / BQ-002:** **CLOSED** — Complaint MAY register without Case; MUST have ≥1 Case within **1 business day** after REGISTERED; Supervisor Queue MUST display exceedances. Lihat `DEC-MODEA-B2-001`.
- **BQ-001:** **CLOSED — Option O3 APPROVED** (DEC-BQ001). Sprint / case-centric Case SoT = DOM-ECMF-003; Aggregate Case SoT = BR-CM-CAT Definition B. Lihat `ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md`.
- **BQ-002 … BQ-014 (Mode A Delivery Baseline):** **ALL LOCKED** — Product Owner Decision Session 2026-08-01. Capability ID final **CAP-008**. Residual BQ for Batch-2 Mode A Case Management = **ZERO**. Lihat `18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md`.
- **BQ-CAP006-01 … 15:** **CLOSED** (with explicit DEFERRED: pause/resume v1, Working Day activation, case-type target split) — DEC-CAP006-BQ-001. FRD-005 **LOCKED** B2-16. Lihat `deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md` dan `deploy/evidence/B2-16_CAP-006_FRD_Lock_Governance_Closure_20260801.md`.
- **OQ-ORG-001:** Dilacak di **DEC-021** (Proposed) — interim: no descendant expansion; Recommend Option A exact-ref.
- **OQ-ORG-002:** Dilacak di **DEC-022** (Proposed) — interim: retain historical refs + fail-closed for new scoped actions.
- **OQ-IAM-001:** Dibuka 2026-08-13 dari temuan bahwa `complaints:create` menggerbangi **7** hal — 4 memang membuat pengaduan (`/api/v1/cm/complaints`, `cm_case`, `internal_complaint`, CA BC ticket-nested), 3 **tidak** (buat antrean, buat loket API-370, ubah telepon pelanggan). String itu jadi penampung *de facto* "petugas front-office boleh berbuat". **Sudah ditutup (migrasi 0073):** gerbang tulis queue → `queue:manage`, customers → `customers:update`; keduanya diberikan otomatis ke 9 peran pemegang `complaints:create` agar tidak ada petugas kehilangan akses. **Owner 2026-08-13:** Admin boleh semua *kecuali* membuat pengaduan (WP dan internal) — grant `complaints:create` dicabut dari ADMIN/ADMINISTRATOR/SUPER_ADMIN (migrasi 0074); wildcard `*` tidak mengizinkan kode itu. **Belum diputuskan:** (a) namespace per bounded context untuk CM ↔ CA BC ↔ internal ↔ case; (b) 19 gerbang baca/ubah yang masih menumpang `complaints:read`/`complaints:update` — queue `tickets` 9 + `queues` 6 + `counters` 3, plus `customers` list 1; (c) penyempitan sebenarnya — siapa yang *seharusnya* memegang `queue:manage`/`customers:update`, karena 0073 memisahkan kosakata tanpa mempersempit wewenang siapa pun.
- **OQ-IAM-001 (lanjutan) — CLOSED 2026-08-22 (Business Owner):** Sisa (a)/(b)/(c) ditutup **tanpa perubahan kode**, atas dua temuan verifikasi:
  1. **18 dari 19 gerbang sisa menjaga pintu tanpa ruangan.** Modul antrean loket (`/api/v1/queues`, `/api/v1/tickets`, `/api/v1/counters` — 9 tickets + 6 queues + 3 counters) ter-mount di `app/api/router.py`, tetapi **tidak ada satu pun pemanggil di `frontend/src`** dan tidak ada folder fitur antrean. Peninggalan Foundation, satu kategori dengan yang dipensiunkan DEC-026. Tidak ada petugas yang terpengaruh karena tidak ada layar yang menuju ke sana.
  2. **Gerbang ke-19 diputuskan memang melekat.** Owner: mengubah nomor telepon pelanggan (`/api/v1/customers/{id}`) **boleh** dilakukan siapa pun yang boleh mengubah pengaduan — tidak perlu izin terpisah.
  Konsekuensi: (a) namespace per bounded context **tidak dikerjakan** — kerapian arsitektur murni, gagal filter 1 CLAUDE.md; (b)/(c) tidak ada penyempitan wewenang. Reversibel lewat DEC baru bila muncul tuntutan audit atau bila modul antrean loket kelak diberi UI.
- **OQ-INT-001:** Dibuka 2026-08-14 dari GAP Pengaduan Internal: create dengan `handlingUnitId` men-transfer Handling langsung untuk **siapa pun** yang memegang `complaints:create`, termasuk Agent — Agent bisa mengeskalasi ke unit lawan tanpa `complaints:assign` maupun putusan atasan. **CLOSED (keputusan Product Owner 2026-08-14):**
  (a) **Bentuk gerbang** — kolom permintaan pada `internal_complaints` (`transfer_request_status` PENDING/APPROVED/REJECTED + snapshot tujuan/alasan/aktor), **bukan** status baru pada `InternalStatus`; status tetap `CREATED` selama menunggu. State machine lama (CREATED→ASSIGNED→IN_PROGRESS→RESOLVED→CLOSED) tidak dirombak.
  (b) **Izin putusan** — permission baru `internal:escalate-decide` (migrasi 0075), digrant ke SUPERVISOR/BRANCH_SUPERVISOR/MANAGER/ADMIN/ADMINISTRATOR/SUPER_ADMIN, **bukan** ke AGENT. Terpisah dari `complaints:escalate` (WP intake-escalation, CAP-008) dan dari `complaints:assign` (transfer langsung SPV/Manager, tidak berubah).
  (c) **Skema nomor** — format baru `PI-{UNIT}-{YYMM}-{NNN}` (mis. `PI-TAB-2608-001`), counter per unit per bulan di tabel baru `internal_complaint_unit_counters` (migrasi 0077); lebar seq melebar otomatis di atas 999. Format lama `PI-YYYY-NNNNNN` (counter global per tahun) **tidak** diremap — baris lab lama tetap terbaca lewat `InternalComplaintNumber` yang menerima dua pola.
  (d) **Saluran notifikasi** — dalam modul: badge hitung + antrean, bukan kanal baru. Foundation `notification` module (channel EMAIL/WHATSAPP/SMS/PUSH, provider stub) **tidak** disentuh — tidak ada `IN_APP` baru di sana, karena itu akan tumpang tindih dengan Global Notification milik Enterprise Platform (bagian 2 CLAUDE.md). Endpoint `GET /transfer-requests/pending-count` dipakai untuk badge sidebar, visibilitas sama dengan list (DEC-024 UNIT/PUSAT/ALL).
  Lihat migrasi `0075_internal_escalate_decide`, `0076_internal_transfer_request`, `0077_internal_unit_counters`; endpoint `POST /{id}/transfer-request` (ajukan/ajukan ulang) dan `POST /{id}/transfer-request/decision` (putus).
