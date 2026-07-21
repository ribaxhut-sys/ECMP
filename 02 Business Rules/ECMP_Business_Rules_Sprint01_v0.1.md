# ECMP Business Rules — Sprint-01 Baseline

> Filename `..._v0.1.md` is frozen to keep cross-document links stable; the **authoritative content version is the `Version` field in the header** (currently 0.2).

| Field | Value |
|---|---|
| ID | BR-DOC-001 |
| Version | 0.2 |
| Owner | Business Analyst |
| Reviewer | ECMF PO / Ops |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

Scope: rules required for Sprint-01 create/get case slice.

## Rule Catalog

| Rule ID | Statement | Domain | Config vs Code | Severity |
|---|---|---|---|---|
| BR-001 | Status transitions must follow configured workflow. For Sprint-01, newly created cases MUST start at `REGISTERED`. Other transitions are out of slice. | ECMF | Config-first (later); fixed initial in code for v0.1 | High |
| BR-003 | ECMP treats customer master as read-only reference. System stores `customerId` only; no authoritative customer profile ownership. | CRM/ECMF | Hard rule | High |
| BR-004 | Only configured domain events may be emitted/consumed. Sprint-01 requires `CaseCreated` (EVT-001). | Notification/ECMF | Config-first | Medium |
| BR-007 | Create/read case requires authenticated principal with permission `cases:create` / `cases:read`. | Core/ECMF | Code + future config | High |
| BR-008 | Every significant write (Sprint-01: case create) MUST persist an immutable, append-only audit record (actor, action, entity, timestamp) in the same transaction. Read-audit deferred per FRD §9. | Core/ECMF | Hard rule | Critical |

## Planned Delivery Rules (reserved — belum aktif di Sprint-01)
ID berikut sudah dialokasikan (per mapping DEC-003) karena dikutip traceability dan FRD draft; rule menjadi aktif saat sprint terkait dimulai. Nilai baseline mengikuti DEC-004.

| Rule ID | Statement | Domain | Enterprise Ref | Target |
|---|---|---|---|---|
| BR-002 | Assignment/reassignment hanya oleh role/unit berwenang: aksi tulis oleh supervisor unit induk; unit lain read-only. | ECMF | BR-ECMF-02 | Sprint-02 (FR-003) |
| BR-005 | SLA dihitung otomatis berdasarkan konfigurasi kategori+prioritas; kalender baseline 24x7. | KPI/ECMF | BR-ECMF-05 | Sprint-03 (FR-030) |
| BR-006 | Tampilan dashboard mengikuti role dan organisasi user (read-only, otorisasi Core Platform). | Dashboard | BR-DASH-01 / BR-DASH-04 | Sprint-03 (FR-040) |

## Validation Rules (Create)
- `customerId` mandatory, non-empty
- `caseType` in {COMPLAINT, INQUIRY}
- `priority` in {LOW, MEDIUM, HIGH, CRITICAL}
- `subject` mandatory, 1..200 chars
- `description` mandatory, 1..5000 chars

## Exceptions
- If Customer Master integration unavailable, allow create with unverified customerId (flagged), do not invent customer data.
