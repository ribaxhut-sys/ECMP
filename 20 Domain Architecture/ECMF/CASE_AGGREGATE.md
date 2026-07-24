# ECMF — Case Aggregate

| Field | Value |
|---|---|
| ID | DOM-ECMF-002 |
| Version | 1.0 |
| Owner | ECMF PO / Solution Architect |
| Reviewer | Tech Leads |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Mendefinisikan **Case sebagai Aggregate Root** domain ECMF: invariants, value objects, entitas anggota aggregate, dan katalog Business Actions yang menjadi satu-satunya jalur mutasi state.

## Aggregate Root: Complaint (Case)

Complaint is the single aggregate for all complaint origins and destinations
(DEC-018 / TASK-042). There is **one** `complaints` table — no
`BranchComplaint` / `CustomerComplaint` / `HeadOfficeComplaint` subtypes.

### Multi-source / multi-target (DEC-018)

| Dimension | Values | Storage |
|---|---|---|
| `source_type` | CUSTOMER, BRANCH, HEAD_OFFICE, SYSTEM | VARCHAR (extensible without migration) |
| `source_id` | UUID of originator | UUID (no typed FK — entity depends on type) |
| `target_type` | BRANCH, HEAD_OFFICE | VARCHAR (extensible without migration) |
| `target_id` | UUID of destination | UUID nullable for legacy null-branch rows |

Legacy columns `customer_id` / `branch_id` remain as derived projections:

- `source_type=CUSTOMER` → `customer_id = source_id`
- `target_type=BRANCH` → `branch_id = target_id` (initial assignment context)
- `target_type=HEAD_OFFICE` → `branch_id` cleared

Lifecycle, Assignment engine, Timeline, Resolution, Appointment, Escalation,
and Authorization are **unchanged**.

Initial organizational destination is resolved by **Complaint Routing Foundation**
(TASK-043 / `COMPLAINT_ROUTING.md`): `ComplaintRoutingService` → immutable
`ComplaintRoute` (`receiver_type`, `receiver_id`, `assignment_context`,
`routing_reason`). Complaint Service applies `assignment_context` to
`branch_id` when the receiver is BRANCH; Assignment Engine remains
user-assignment only (no routing matrix inside Assignment).

**Complaint Context Foundation** (TASK-044 / `COMPLAINT_CONTEXT.md`) is a
read-only assembled view (`ComplaintContext`) over Complaint + current
Assignment + SLA + Routing. It is **not** part of the aggregate boundary and
is **not** persisted.

### Invariants
| # | Invariant | Sumber |
|---|---|---|
| INV-1 | Status hanya berubah melalui transisi valid sesuai Workflow Config aktif (lihat `CASE_STATE_MACHINE.md`, DOM-ECMF-003) | BR-001 / BR-ECMF-03, ADR-008 |
| INV-2 | `source_type` / `source_id` immutable after create; when CUSTOMER, `customerId` matches `source_id` and remains immutable | ADR-002, FRD-001, DEC-018 |
| INV-3 | Setiap write (create/assign/status change/close/reopen) menghasilkan audit record immutable dalam transaksi yang sama | BR-008 (delivery), BR-ECMF-01, FR-001c |
| INV-4 | Case closed wajib memiliki Resolution (evidence sesuai kategori bila dipersyaratkan) | BR-ECMF-06 |
| INV-5 | Event emit terjadi dalam transaksi yang sama via outbox (tidak ada event tanpa write yang tersimpan) | ADR-001, ADR-009 |
| INV-6 | One Complaint aggregate only — no parallel complaint tables by source/target | DEC-018 |
| INV-7 | Initial destination must resolve via ComplaintRoutingService default matrix only | TASK-043 |
| INV-8 | Operational consumers should prefer ComplaintContext over ad-hoc joins across aggregates | TASK-044 |

## Value Objects
| Value Object | Nilai | Catatan |
|---|---|---|
| CaseType | `COMPLAINT`, `INQUIRY` | FRD-001 §7; enum tertutup baseline |
| Priority | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | FRD-001 §7; memengaruhi SLA (BR-005) |
| CaseStatus | `REGISTERED`, `ASSIGNED`, `IN_PROGRESS`, `PENDING_REVIEW`, `CLOSED`, `REOPENED` | Baseline — definisi transisi milik Workflow Config Administration (DOM-ECMF-003) |
| Channel | mis. `CALL`, `EMAIL`, `BRANCH` | Optional; atribut asal pencatatan, bukan referensi ke domain Channel aktif (OQ-001) |

## Entitas Anggota Aggregate (future)
Entitas berikut adalah **bagian dari aggregate Case** (bukan aggregate mandiri), belum diimplementasikan di Sprint-01:

| Entity | Peran | Catatan |
|---|---|---|
| Activity | Log aktivitas per case (BR-ECMF-04) | Append-only, visible ke pihak berwenang |
| Comment | Komentar internal/customer-facing | Perlu klasifikasi internal vs eksternal [TBD] |
| Attachment | Berkas bukti/dokumen | Storage terpisah; retensi & scanning [TBD] |
| Status History | Riwayat transisi status | Append-only; basis SLA Clock |
| Resolution / Root Cause | Hasil penanganan saat closure | Wajib saat close (INV-4) |

## Business Actions Catalog
Satu-satunya jalur mutasi Case. **Dilarang menyediakan generic PATCH/update yang melewati business action** — setiap mutasi harus lewat action bernama di bawah agar invariants, audit (INV-3), dan event emit (INV-5) selalu ditegakkan.

| Action | Status | API | Event | Audit action | Catatan |
|---|---|---|---|---|---|
| RegisterCase | ✅ Implemented (Sprint-01) | API-001 `POST /v1/cases` | EVT-001 CaseCreated | `case.create` | Status awal `REGISTERED` (FR-001a); audit + outbox satu transaksi (FR-001c) |
| GetCase | ✅ Implemented (Sprint-01) | API-002 `GET /v1/cases/{caseId}` | — | — (read-audit deferred, DEC-002) | FR-002 |
| AssignCase | 🕓 Planned (Sprint-02 / gate G1) | API-003 `POST /v1/cases/{caseId}/assign` | EVT-002 CaseAssigned + EVT-003 StatusChanged | `case.assign` | Termasuk reassign (previousAssigneeId) |
| TransitionStatus | 🕓 Planned (Sprint-02 / gate G1) | API-004 `POST /v1/cases/{caseId}/status` | EVT-003 StatusChanged | `case.status_change` | Guard per DOM-ECMF-003; reason wajib untuk override |
| CloseCase | 🕓 Planned (Sprint-02 / gate G1) | API-004 (transisi ke `CLOSED`) | EVT-005 CaseClosed + EVT-003 StatusChanged | `case.close` | Resolution wajib (INV-4, BR-ECMF-06) |
| ReopenCase | 🕓 Planned (Sprint-02 / gate G1) | API-004 (transisi `CLOSED`→`REOPENED`) | EVT-007 CaseReopened (Proposed) + EVT-003 StatusChanged | `case.reopen` | Role + window 30 hari kalender per BR-ECMF-07 (baseline DEC-004); reason wajib |

Catatan: API-003/API-004 tercatat di `../../26 Traceability/TRACEABILITY_MATRIX.md` (Sprint-02, Planned); OpenAPI harus merged sebelum kode (aturan `ai/04_api.md`).

## Anti-patterns (dilarang)
- Generic `PATCH /cases/{caseId}` atau `PUT` field bebas — melewati invariants dan audit.
- Update status langsung di repository/DB tanpa melalui TransitionStatus.
- Mengubah `customerId` setelah create (INV-2).
- Emit event di luar transaksi write (harus via outbox, ADR-009).

## Related
- `README.md` (DOM-ECMF-001) — konteks domain ECMF
- `CASE_STATE_MACHINE.md` (DOM-ECMF-003) — matriks transisi + guards
- `../../27 Project Decisions/DEC-018_Multi_Source_Multi_Target_Complaint_TASK042_v1.0.md`
- `COMPLAINT_ROUTING.md` (ARCH-ECMF-ROUTING-001) — Routing Foundation
- `../../08 Event Catalog/events/events.yaml` — SoT event
- `../../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` — atribut Case Header
