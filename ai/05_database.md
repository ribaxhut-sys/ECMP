# 05 — Database / Data Context

| Field | Value |
|---|---|
| ID | AI-CTX-005 |
| Version | 1.0 |
| Owner | Data Architect |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Ownership
- Customer master attributes: **external SoR** (reference only in ECMP)
- Case/interaction/SLA/audit: **ECMP-owned**

## Rules
1. Every schema change needs an **Alembic revision** (`implementation/backend/alembic/`).
2. Do not duplicate customer master as authoritative copy.
3. PII handling follows Security standards (dilarang log `description`).
4. Important state changes must be auditable — write-audit dalam transaksi yang sama (BR-008).
5. Keep Data Dictionary (`06`) updated for new entities/attributes.
6. Naming: DB snake_case ↔ API/event camelCase (lihat `21 Technical Standards`).
7. Kolom audit standar entitas mutable: `created_at`, `created_by`, `updated_at`, `updated_by` (UTC).

## Physical Schema (revision 0001)
`cases`, `audit_log` (append-only), `outbox` — ERD: `06 Data Dictionary/ECMP_ERD_Sprint01_v0.1.md`

## Conceptual Case Data
Case Header, Activity, Attachment, Comment, Status History, SLA Clock, Root Cause, Resolution
