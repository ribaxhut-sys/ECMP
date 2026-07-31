# PROGRAM-DOC-001 — Documentation Sync Record

| Field | Value |
|---|---|
| Document ID | GOV-DOC-001 |
| Program | PROGRAM-DOC-001 |
| Version | 1.0 |
| Date | 2026-07-30 |
| Prepared by | ECMP Documentation Administrator / Documentation Architect |
| Audience | PMO / Architecture Board / Traceability owners |
| Status | 🟢 **Recorded** |
| Scope | Catalog / FRD / RTM / OpenAPI **metadata sync** under DEC-020 — no architecture redesign |

---

## 1. Purpose

Standalone record for **PROGRAM-DOC-001**, cited by FRD-CM-001, RTM Batch 1, API Catalog README, and DEC-020, previously without a dedicated governance file (audit K-6 / BLK-07).

---

## 2. Authorized scope

| In scope | Out of scope |
|---|---|
| Path/method metadata sync to `/api/v1/cm` (API-500…512) | Changing FR/BR semantics |
| Closing documentation OQ markers when a Decision exists (e.g. OQ-CM-B1-001 via DEC-020) | Accepting ADR-014/015/016… |
| Dual-SoT narrative alignment with DEC-020 | Mode B / Batch-2 unlock |
| README / catalog honesty notes | Inventing OpenAPI enterprise `securitySchemes` |

---

## 3. Executed syncs (evidence)

| Date | Surface | Change |
|---|---|---|
| 2026-07-30 | FRD-CM-001 v1.1 | OQ-CM-B1-001 Closed (DEC-020); dual-SoT narrative; Aggregate path refs → `/api/v1/cm` |
| 2026-07-30 | RTM Batch 1 | §7 path+method → `/api/v1/cm` (API-500…512); OQ Closed via DEC-020 |
| 2026-07-30 | `07 API Catalog/README.md` | Dual SoT ownership metadata note |
| 2026-07-30 | FRD LOCKED release notes | OQ Closed pointer |

---

## 4. Binding rules

1. Documentation sync **must not** silently upgrade Draft Business Rules or Accept ADRs.
2. When DEC-020 (or future Retirement DEC) changes SoT ownership, PROGRAM-DOC-001 may update catalogs **only** to match the Decision.
3. Mode B / enterprise customer / Batch-2 remain gated by Architecture Board (C-7).

---

## 5. Explicit Non-Authority

- Does not Accept ADRs
- Does not authorize implementation beyond existing DEC / FRD LOCK gates
- Does not close OPS recovery drill (K-4) or invent Security Officer sign-off

## 6. Related

- `27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md`
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md`
- `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0.md`
- `07 API Catalog/README.md`

| Rev | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | Audit K-6 — documentation sync program record |
