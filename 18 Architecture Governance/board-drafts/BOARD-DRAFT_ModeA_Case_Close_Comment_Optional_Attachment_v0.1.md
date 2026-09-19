# BOARD-DRAFT — Mode A Case Close: Comment (+ optional attachment) without resolutionCode/summary

**Status:** ACCEPTED WITH CONDITIONS (product authorization 2026-08-12 → **DEC-021**)  
**Implemented:** OpenAPI API-534 · domain sentinel `BRANCH_DONE` · FE form Tutup/Eskalasi/Tolak  
**Date:** 2026-08-12  
**Scope:** CAP-008 / FRD-CM-B2-001 Mode A Aggregate Case (`/api/v1/cm/cases`)  
**Out of scope:** Complaint Aggregate closure · Mode B · DEC-F4 Escalation Engine · foundation case-service

---

## 1. Request (one sentence)

Izinkan jalur **Tutup Case di cabang** dengan **Comment wajib** dan **Attachment opsional**, **tanpa** mewajibkan `resolutionCode` / `summary` pada Resolve ACCEPT (dan tanpa memindahkan Eskalasi Pusat ke API Case).

---

## 2. Business intent

Petugas cabang menutup pekerjaan Case dengan cepat: cukup menjelaskan hasil di komentar; boleh lampiran bukti; tidak mengisi katalog kode resolusi / ringkasan formal. Eskalasi ke Pusat tetap lewat **pengaduan induk**, bukan aksi resolve Case.

---

## 3. What is already LOCKED (do not reopen)

| ID | Rule | Stay |
|----|------|------|
| **BQ-010** | Resolve requires Comment; Attachment optional; Complaint Attachment may be reused | **Tetap** — selaras permintaan |
| **BQ-007** | Close Case ≠ close Complaint Aggregate | **Tetap** |
| Mode A | HQ Escalation full / DEC-F4 on Case | **Tetap OOS** — eskalasi UI → induk Aggregate |

---

## 4. What Board must decide (SoT change)

### Option recommended — **Amend Mode A Resolve ACCEPT (branch close path)**

| Layer | Today | Proposed |
|-------|--------|----------|
| OpenAPI `cm-case-management.v1.yaml` API-534 | ACCEPT requires `resolutionCode` + `summary` | ACCEPT: **Comment required**; `resolutionCode` / `summary` **optional** (nullable); `attachmentIds` optional |
| Domain `CaseAggregate.resolve(ACCEPT)` | Rejects if code/summary missing | Accept with comment only; store empty/`BRANCH_CLOSED` placeholder **only if** persistence column NOT NULL still requires a value — prefer nullable or documented sentinel **`BRANCH_DONE`** owned by Board |
| FRD-CM-B2-001 FR-005 / AC-12 | “complete Accepted resolution” implies code+summary in prose | Amend AC-12: Comment (+ optional attachment) sufficient for Mode A branch ACCEPT → `RESOLVED` |
| CAP-008 BR-CAP02-R13 wording “Kode resolusi valid” | Must / tied BQ-008 | Board: **narrow** — kode wajib **tidak** untuk jalur cabang Mode A Tutup; atau supersede R13 untuk Mode A only |
| Close API-536 | Separate step after RESOLVED | **Tetap terpisah** **atau** Board boleh izinkan FE/BE orkestrasi resolve+close dalam satu UX (kontrak tetap 2 call) |

### Explicitly **reject** (unless separate Board item)

- Menjadikan “Eskalasi Pusat” sebagai `action` pada API-534 Case resolve  
- Menghapus BQ-010 Comment requirement  
- Auto-close Complaint Aggregate saat Case CLOSED  

---

## 5. Persistence note

ORM `resolution_code` column is `nullable=False` today. Board must pick one:

1. **Sentinel** (no migration): ACCEPT tanpa input user → persist `BRANCH_DONE` (or similar) + summary = comment truncate; **katalog resolusi formal tidak dipakai**  
2. **Migration**: make `resolution_code` / summary nullable for Mode A records  

Recommendation for speed: **(1) Sentinel** with Board-named code, documented in OpenAPI description.

---

## 6. Impact checklist (after Board Accept)

- [ ] `07 API Catalog/openapi/cm-case-management.v1.yaml` (API-534 schema + examples)  
- [ ] `03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md` (FR-005 / AC-12)  
- [ ] CAP-008 BR-CAP02-R13 Mode A narrow (or DEC supersede)  
- [ ] `backend/app/modules/cm_case/domain/aggregate.py` + tests  
- [ ] `frontend` Resolve form: Tutup = comment (+ optional attachment); remove required code/summary  
- [ ] Traceability / Test catalog AC sync  
- [ ] Decision Matrix / DEC entry once Board resolves  

**Not changed by this draft:** Dual-SoT DEC-020 · Mode B CLOSED · Identity Adapter  

---

## 7. Decision options for Board

| Vote | Meaning |
|------|---------|
| **ACCEPT WITH CONDITIONS** | Mode A ACCEPT: comment (+ optional attachment) sufficient; sentinel code allowed; Escalation remains Aggregate-only |
| **ACCEPT WITH CONDITIONS (nullable columns)** | Same + Alembic nullable resolution fields |
| **REJECT** | Keep code+summary mandatory; UI may hide fields but SoT unchanged |
| **DEFER** | Ship UI orchestration only (hidden defaults) until next Board cycle |

---

## 8. Ask

Board: **Accept Option recommended (sentinel)** so engineering may update OpenAPI + domain + FE without inventing contract?

---

*Draft only — not an Accepted Board Resolution. Do not treat as unlock for Mode B or Escalation Engine.*
