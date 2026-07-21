# Document Metadata Standard

| Field | Value |
|---|---|
| ID | EAR-STD-001 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | PMO / Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Standar metadata wajib di awal setiap dokumen EAR (kecuali file murni aset biner).

## Required Metadata Block

```markdown
| Field | Value |
|---|---|
| ID | SA-001 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Solution Architect |
| Approver | CIO / Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-08-01 |
| Next Review | 2027-02-01 |
```

## Field Rules

| Field | Rule |
|---|---|
| ID | Wajib, unik, mengikuti Enterprise Numbering |
| Version | Semantic document version `Major.Minor` |
| Owner | Role/person accountable for content |
| Reviewer | Peer/technical reviewer |
| Approver | Authority for baseline approval |
| Status | Draft / Under Review / Approved / Deprecated (+ badge) |
| Last Review | Tanggal review terakhir (YYYY-MM-DD) |
| Next Review | Tanggal review berikutnya sesuai Review Schedule |

## Where Required
- Semua dokumen `.md` substansial (bukan sekadar folder stub mini)
- FRD, SA, ADR, Standards, Runbook, Matrices explanatory docs
- OpenAPI/YAML: metadata di `info.x-ear` atau file sidecar README

## Template
Lihat `../24 Templates/DOCUMENT_HEADER_TEMPLATE.md`
