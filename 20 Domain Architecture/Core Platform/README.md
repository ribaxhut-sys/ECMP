# Domain Architecture — Core Platform

| Field | Value |
|---|---|
| ID | DOM-CP-001 |
| Version | 1.0 |
| Owner | Platform PO / Security |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Fondasi bersama seluruh domain ECMP: identity, access control, organisasi, konfigurasi platform, dan audit trail immutable. Semua domain lain bergantung pada Core Platform untuk AuthN/AuthZ dan pencatatan audit.

## Bounded Context
- **Konteks:** Identity & Access + Audit. Core Platform tidak mengetahui semantik bisnis case/customer — ia hanya tahu *siapa* (user, role, org unit), *boleh apa* (permission), dan *apa yang terjadi* (audit record).
- **SoT Role-Permission (per ADR-008):** Entitas Role, Permission, Role-Permission mapping, dan User-Role **dimiliki dan ditegakkan Core Platform**. Administration hanya bertindak sebagai konfigurator (UI/proses perubahan + approval BR-ADM-01) yang menulis melalui API Core Platform — tidak ada salinan otoritatif di domain lain.
- **Ubiquitous language:** User, Role, Permission, Organization Unit, Audit Log, Config Parameter.

## In Scope
- Authentication (Bearer token / gateway header per ADR-007)
- Authorization: kombinasi role + organization unit (BR-CP-01, BR-CP-02 → delivery BR-007)
- Struktur organization unit
- Config parameter platform (non-bisnis)
- **Central audit trail — append-only** (BR-CP-03 → delivery BR-008): audit record tidak dapat dihapus/diedit oleh siapapun termasuk Administrator; write-audit wajib pada setiap significant write (FR-001c)

## Out of Scope
- Konfigurasi bisnis (workflow, SLA, reference data) — milik Administration (ADR-008)
- Data pelanggan — ECMP bukan Customer Master SoR (ADR-002)

## Key Components
| Komponen | Tanggung jawab |
|---|---|
| Auth Service | Validasi JWT (`sub` + `roles`); permissions **tidak** di-embed di token |
| Permission Resolver (TASK-038) | Resolve `Set<permissionCode>` via User→UserRole→Role→RolePermission→Permission (+ IAM cache 5 menit) |
| Data Scope Resolver (TASK-039) | Resolve `EffectiveScope` via User→UserRole→Role→DataScope (+ IAM cache 5 menit); helpers opt-in |
| Authorization Middleware (TASK-040) | Satu pipeline: AuthN → Permission Resolver → Permission Check → (opsional) Data Scope Resolver/Check → Endpoint |
| IAM Cache (TASK-041) | `IamCacheService` in-memory: permissions / data_scopes / principals; invalidate_iam_user / invalidate_iam_all; metrics |
| RBAC Store | SoT Role/Permission/Role-Permission/User-Role/DataScope (ADR-008) |
| Org Registry | Organization unit hierarchy untuk scoping otorisasi |
| Audit Writer | Persist audit record append-only, satu transaksi dengan write bisnis (BR-008) |
| Audit Projection | Konsumsi domain events untuk proyeksi audit lintas domain |

## Key Flows
1. **AuthZ check (TASK-038/039/040):** Request → Authentication (JWT) → Permission Resolver → Permission Check → (opsional) Data Scope Resolver → Data Scope Check → Endpoint (BR-007). Helper publik: `require_permissions` / `require_roles` / `require_data_scope` / `resolve_effective_scope`. Filtering baris domain **belum** otomatis di semua endpoint.
2. **Write audit (BR-008):** Domain melakukan significant write → audit record (actor, action, entity ref, timestamp UTC, old/new value bila relevan) dipersist dalam transaksi yang sama.
3. **RBAC change:** Administration mengajukan perubahan role-permission / data-scope → approval (BR-ADM-01) → tulis via API Core Platform → `invalidate_iam_user` / `invalidate_iam_all` → audit (BR-ADM-02). Design: `10 Security and Access Standards/ECMP_IAM_Cache_Design_v1.0.md`.

## Data Ownership
| Entity | Ownership | Catatan |
|---|---|---|
| User, Role, Permission, User-Role | Core Platform (SoT) | ADR-008; Administration = config view, non-SoT |
| Organization Unit | Core Platform | Sinkron HR system masih [TBD] |
| Config Parameter (platform) | Core Platform | Parameter bisnis di Administration |
| Audit Log | Core Platform | Append-only, immutable (BR-CP-03 / BR-008) |

## Integrations
- **Events consumed** (per `../../08 Event Catalog/events/events.yaml`): EVT-001 CaseCreated, EVT-002 CaseAssigned, EVT-003 StatusChanged, EVT-005 CaseClosed, EVT-006 ConfigChanged, EVT-007 CaseReopened — semua untuk audit projection.
- **Events produced:** tidak ada (baseline). Perubahan RBAC diaudit langsung, bukan via event.
- **Konsumen layanan:** semua domain (AuthN/AuthZ, audit writer).
- Delivery guarantee at-least-once (ADR-001) via transactional outbox (ADR-009); consumer wajib idempotent.

## NFR Considerations
- Audit write tidak boleh gagal diam-diam — kegagalan audit = kegagalan transaksi bisnis (BR-008).
- Read-audit ditunda per DEC-002 (revisit saat multi-principal access ada).
- Layering minimal per ADR-005 (Presentation → Application → Domain ← Infrastructure ringan).

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Open Questions
- Sinkronisasi Organization Unit dengan HR system: native vs sync [TBD].
- Proses override manual otorisasi oleh Administrator (exception BR-CP-02) — **ditutup** baseline DEC-004: override hanya oleh Administrator dengan justifikasi tercatat + audit trail.
