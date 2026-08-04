# CWX-M3 — Working Surface

| Field | Value |
|---|---|
| Document ID | CWX-M3 |
| Status | 🔒 LOCKED (specification) |
| Epic | EPIC-CW-001 |
| Parent | CWX-M2 / CWX-M1 / CWX-000 |
| Category | GOV-001 Category B — Specification |
| Date | 2026-08-03 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → GOV-001 → CWX-000 → CWX-M1 → CWX-M2 → **CWX-M3** |
| Implementation | DELIVERED (READY) — Evidence Surface · Working Actions Area composed Dual-SoT. Conversation · Internal Notes · Decision Notes remain **BLOCKED** (not implemented). |

## Objective

Menyediakan **Working Surface** Case Workspace: area kerja utama di bawah konteks (CWX-M1/M2) untuk **bukti** dan **aksi kerja yang boleh dilakukan sekarang** — dengan **reuse capability existing** saja.

Primary questions:

- Evidence Surface → *"What evidence supports this Case?"*
- Working Actions Area → *"What work can I perform right now?"*

CWX-M3 **extend** CWX-M1 dan CWX-M2. Bukan redesign Workspace. Bukan milestone terpisah M3A/M3B.

## Business Purpose

Setelah petugas memahami *apa kasusnya* (M1) dan *apa yang sedang terjadi* (M2), mereka membutuhkan permukaan kerja untuk:

1. melihat bukti pendukung yang sudah ada, dan  
2. menjalankan aksi operasional yang legal saat ini,

tanpa menduplikasi Context Header / Decision Bar, tanpa API baru, dan tanpa mengubah domain bisnis.

## Scope

CWX-M3 mendefinisikan **komposisi presentasi** di slot `main` Context-Aware Layout (CWX-M1), di Dual-SoT Mode A (Foundation `/api/v1/complaints` · Aggregate `/api/v1/cm`), hanya untuk capability berstatus **READY**.

Capability berstatus **BLOCKED** didokumentasikan di dokumen ini agar tidak diimplementasikan diam-diam; implementasi PANEL BLOCKED dilarang sampai keputusan governance membuka DoR.

## In Scope

- Evidence Surface (READY) — compose ulang kartu/panel attachment existing  
- Working Actions Area (READY) — compose ulang kartu/dialog aksi operasional existing  
- UX Contract untuk kedua surface di atas  
- Acceptance Criteria, Definition of Ready, Definition of Done  
- Dokumentasi capability BLOCKED (Conversation · Internal Notes · Decision Notes) sebagai **larangan implementasi** di M3  

## Out Of Scope

- Implementasi Conversation / Internal Notes / Decision Notes  
- Evidence **redesign** (storage, klasifikasi domain baru, API baru)  
- Redefinisi Context Header (CWX-M1)  
- Redefinisi Decision Bar (CWX-M1)  
- Duplikasi field konteks M1/M2  
- Timeline redesign · Activity Feed · Audit · Decision History  
- Notification · AI · Search/Queue redesign  
- Regional / Enterprise Workspace  
- Backend / API / DB / Auth changes  
- Mode B / SSO / Identity Adapter  
- State machines · Workflow engine  
- Silent Dual-SoT merge / retirement Foundation  

## Capability Matrix

| Capability | Business Rule | API | Entity | Component | Status | Ready | Blocked |
|---|---|---|---|---|---|---|---|
| Evidence Surface | BR-012 Attachment Management; FR-004 (Batch-1) | Foundation API-323–326, API-386–387; Batch-1 API-507–512 | `attachments` (CAP-011); `cm_batch1_attachments` / staging / history | `ComplaintAttachmentsCard`, `StagingAttachmentsPanel`, `CmBatch1BoundAttachmentsCard`, `features/attachments/*` | READY | Ya | Tidak |
| Working Actions Area | BR-005 Assignment; BR-007 Escalation; BR-008 Resolution; BR-009 Closure (+ CAP Foundation/Aggregate terkait) | Foundation assign/status/resolution/escalation/appointment/close (katalog existing); Aggregate CAP-008 status/resolve/close | Assignments, resolutions, escalations, appointments, `cm_cases` / resolutions | `AssignmentCard`, `ResolutionCard`, `EscalationCard`, `AppointmentCard`, close cards; Aggregate dialog via Decision Bar entry | READY | Ya | Tidak |
| Conversation | BR-011 Communication History | **NONE** di Foundation / Aggregate / case-service untuk thread komunikasi | **NONE** | **NONE** di `frontend/` | BLOCKED | Tidak | Ya |
| Internal Notes | BR-013 Comment (Internal Note); FR-007 (case-service only) | API-007 / API-008 **hanya** case-service; **NONE** di Foundation/Aggregate CWX | `case_notes` **hanya** `implementation/backend/`; **NONE** di `backend/` Mode A CWX | `NotesPanel` **hanya** `implementation/frontend/`; **NONE** di `frontend/` CWX | BLOCKED | Tidak | Ya |
| Decision Notes | **Tidak ada** FR/BR/ADR yang mendefinisikan “Decision Notes” sebagai entitas CWX | **NONE** (bukan API-506 duplicate; bukan resolve `comment`; bukan escalation `reviewNotes`) | **NONE** (`DecisionNote` / `decision_notes`) | **NONE** (`CwxDecisionBar` ≠ Decision Notes) | BLOCKED | Tidak | Ya |

## Ready Capabilities

Kedua capability di bawah adalah **presentation compositions** yang dibangun dengan **reuse capability yang sudah ada**.

### Evidence Surface

| Item | Nilai |
|---|---|
| Status | READY |
| Pertanyaan UX | *What evidence supports this Case?* |
| Sifat | Compose / presentasi ulang panel attachment existing di Working Surface |
| Canonical source | BR-012; FR-004; CAPABILITY-011 |
| API | Existing only — tidak menambah operasi |
| Entity / storage | Existing only — tidak mengubah storage |
| Komponen reuse | Kartu/panel attachment yang sudah ada di Foundation; Aggregate mengikuti kartu yang sudah ada tanpa invent CRUD Case attachment baru |

**Larangan READY Evidence:**

- Tidak ada API baru  
- Tidak ada perubahan backend  
- Tidak ada perubahan storage  
- Tidak ada domain “Evidence” terpisah di luar Attachment yang sudah ada  
- Tidak redesign Timeline sebagai “bukti”  

### Working Actions Area

| Item | Nilai |
|---|---|
| Status | READY |
| Pertanyaan UX | *What work can I perform right now?* |
| Sifat | Compose / presentasi ulang kartu & dialog aksi operasional existing di area kerja `main` |
| Canonical source | BR & CAP aksi operasional yang sudah diimplementasikan; filter legalitas tetap Role ∧ Permission ∧ State ∧ Business Rule |
| API | Existing only |
| Entity | Existing only |
| Komponen reuse | Kartu aksi Foundation (`AssignmentCard`, `ResolutionCard`, `EscalationCard`, `AppointmentCard`, close cards, dsb.) dan dialog Aggregate yang sudah dipicu dari Decision Bar |

**Hubungan dengan Decision Bar (CWX-M1 — tidak diubah):**

- Decision Bar = **entry / gate** aksi primer (max 3 + overflow)  
- Working Actions Area = **form / permukaan kerja** untuk menyelesaikan aksi  
- Jangan menggabungkan, mengganti, atau menduplikasi kontrak Decision Bar  

**Larangan READY Working Actions:**

- Tidak ada API baru  
- Tidak ada perubahan backend  
- Tidak ada engine workflow baru  
- Tidak menampilkan aksi ilegal  

## Blocked Capabilities

Implementasi UI untuk capability berikut **dilarang** di CWX-M3 sampai DoR terpenuhi dan keputusan governance membuka status READY.

### Conversation

| Dimensi | Isi |
|---|---|
| Business reference | BR-011 Communication History |
| Current canonical source | Business rule ada; FR Batch-1 menandai Communication History **later / out of Batch 1**. Tidak ada living CWX contract runtime untuk Conversation. |
| Existing API | **NONE** (`/conversations`, `/messages`, `/communications` tidak ada di Foundation, Aggregate, atau case-service) |
| Existing entity | **NONE** (bukan `channel_message_id` intake; bukan notification stub) |
| Current blocker | Tidak ada kontrak API, entity, komponen React, atau DB thread komunikasi yang bisa di-reuse tanpa invent |
| Required governance decision | FR + OpenAPI + Dual-SoT ownership untuk Communication History **sebelum** panel Conversation di CWX; Timeline **bukan** pengganti Conversation |

### Internal Notes

| Dimensi | Isi |
|---|---|
| Business reference | BR-013 Comment Management (Internal Note) |
| Current canonical source | FR-007 append-only notes pada **case-service** saja — bukan SoT Mode A Dual-SoT (`frontend/` Foundation + Aggregate) |
| Existing API | API-007 `GET /v1/cases/{caseId}/notes`, API-008 `POST /v1/cases/{caseId}/notes` (**case-service only**). **NONE** di `/api/v1/complaints` atau `/api/v1/cm` |
| Existing entity | `CaseNote` / `case_notes` di `implementation/backend/` saja. **NONE** di `backend/` Mode A CWX |
| Current blocker | Capability Notes tidak tersedia pada permukaan CWX Dual-SoT; wiring ke case-service tanpa keputusan SoT = tebak Dual-SoT. Field `notes` pada assign/close/escalation **bukan** Internal Notes thread. |
| Required governance decision | Keputusan Dual-SoT: apakah Notes CWX memakai case-service FR-007, atau menunggu API Notes pada Foundation/Aggregate. Tanpa itu → tetap BLOCKED. Port ke Mode A tanpa API = dilarang. |

### Decision Notes

| Dimensi | Isi |
|---|---|
| Business reference | **Tidak ada** BR/FR yang menetapkan “Decision Notes” sebagai artefak domain CWX |
| Current canonical source | **NONE.** CWX-M1/M2 menandai Decision Notes / Decision History **out of scope**. Jangan disamakan dengan Decision Bar. |
| Existing API | **NONE** untuk Decision Notes. Bukan padanan: API-506 duplicate decisions; CAP-008 resolve `comment`; escalation `reviewNotes`. |
| Existing entity | **NONE** (`DecisionNote`, `decision_notes`). `cm_batch1_duplicate_decisions` = FR-003 linkage, bukan Decision Notes CWX. |
| Current blocker | Konsep pengalaman tanpa SoT data; mengisi field lain sebagai “Decision Notes” = asumsi terlarang |
| Required governance decision | Spek Category B + penunjukan SoT eksplisit ke field/API existing **atau** (jika butuh artefak baru) keluar dari “no API / no backend” — perlu jalur governance terpisah. |

## UX Contract

### Evidence Surface

| Aturan | Isi |
|---|---|
| Question answered | *What evidence supports this Case?* |
| Placement | Slot `main` Context-Aware Layout; di bawah Operational Context (M2); tidak di Context Header |
| Content | Daftar / status attachment existing (staging, bound, voidable per aturan existing) |
| Never | Mengulang Complaint ID · Customer · Priority · Owner · Current Work · SLA dari Context Header |
| Never | Menjadi Timeline, Audit, atau Communication History |
| Empty state | Tidak ada bukti → empty state jujur; bukan error; bukan invent data |

### Working Actions Area

| Aturan | Isi |
|---|---|
| Question answered | *What work can I perform right now?* |
| Placement | Slot `main`; area kerja untuk form/kartu aksi; Decision Bar tetap entry primer |
| Visibility | Hanya aksi yang lulus Role ∧ Permission ∧ State ∧ Business Rule (sama prinsip M1) |
| Never | Redefinisi Context Header |
| Never | Redefinisi Decision Bar (max 3 primary, sticky, overflow, filter legalitas) |
| Never | Duplikasi Context (Zero Duplicate Context — CWX-000 Golden Rule 4) |
| Never | Menampilkan aksi ilegal sebagai disabled tanpa penjelasan (prefer hide, konsisten M1) |

### Batas dengan M1 / M2

| Artefak | Pemilik | CWX-M3 |
|---|---|---|
| Context Header | CWX-M1 | Reference only — tidak diubah |
| Decision Bar | CWX-M1 | Reference only — tidak diubah |
| Operational Context / Current Work / Badges / Summaries | CWX-M2 | Reference only — tidak diulang di Evidence / Working Actions |

## Acceptance Criteria

Dokumentasi AC saja — **bukan** perintah implementasi di dokumen ini.

1. Evidence Surface menjawab *What evidence supports this Case?* memakai data attachment existing saja.  
2. Working Actions Area menjawab *What work can I perform right now?* memakai aksi/kartu existing saja.  
3. Tidak ada endpoint OpenAPI baru.  
4. Tidak ada perubahan backend, skema DB, atau storage.  
5. Context Header tidak diubah dan tidak diduplikasi.  
6. Decision Bar tidak diubah dan tidak digantikan oleh Working Actions Area.  
7. Conversation, Internal Notes, dan Decision Notes **tidak** muncul sebagai panel kerja M3.  
8. Dual-SoT tetap coexistence (DEC-020); tidak ada silent merge / retirement Foundation.  
9. Mode B / SSO / enterprise `securitySchemes` tidak disentuh.  
10. CWX-R checklist relevan tetap dapat dievaluasi pada surface READY.  

## Definition of Ready

Implementasi suatu capability di CWX-M3 **boleh dimulai HANYA JIKA** semua berikut benar:

1. Capability status = **READY** (lihat Capability Matrix).  
2. Canonical Source ada (BR/FR/CAP yang dirujuk).  
3. API existing ada (tidak perlu API baru).  
4. Entity existing ada.  
5. Component existing ada untuk di-reuse/compose.  
6. Living artifact CWX-M3 ini LOCKED.  
7. CWX-M1 dan CWX-M2 sudah LOCKED + implemented (prasyarat anti-skip).  

Capability **BLOCKED** gagal DoR secara definisi — coding panel tersebut dilarang.

## Definition of Done

Implementasi CWX-M3 (surface READY) dianggap DONE hanya jika:

1. Tidak ada perubahan backend.  
2. Tidak ada perubahan API (katalog & runtime).  
3. Tidak ada arsitektur baru (tidak ada engine, SoR, atau bounded context baru).  
4. Tidak ada konteks terduplikasi (Zero Duplicate Context vs Header / M2).  
5. Tidak ada pelanggaran governance (Board / ADR / CONSTITUTION / GOV-001 / CWX-000 / M1 / M2).  
6. Panel BLOCKED tidak diimplementasikan.  
7. AC di atas terpenuhi untuk Evidence Surface dan Working Actions Area.  
8. Verifikasi Functional · Cognitive · Consistency (CWX-R) untuk surface yang diubah.  

## References

| Artefak | Path / ID |
|---|---|
| CWX-000 | `docs/governance/ECMP-CWX-000.md` |
| CWX-M1 | `docs/governance/ECMP-CWX-M1.md` |
| CWX-M2 | `docs/governance/ECMP-CWX-M2.md` |
| CWX-R | `docs/governance/ECMP-CWX-R.md` |
| GOV-001 | `docs/governance/ECMP-GOV-001.md` |
| ECMP-CONSTITUTION-001 | `docs/governance/ECMP-CONSTITUTION-001.md` |
| BR-011 / BR-012 / BR-013 | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` |
| FR-004 | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` |
| FR-007 / API-007 / API-008 | case-service OpenAPI + `26 Traceability` |
| Attachment APIs | `07 API Catalog/openapi/complaint-service.v1.yaml`; `complaint-management-batch1.v1.yaml` |
| DEC-020 Dual-SoT | Architecture Decision / Mode A coexistence |
| Mirror (Architecture Governance) | `18 Architecture Governance/ECMP_CWX_M3_Working_Surface_v1.0.md` |

## 10. Delivery Plan

Urutan delivery untuk surface **READY** saja. Capability **BLOCKED** (Conversation · Internal Notes · Decision Notes) tidak masuk fase implementasi.

### Phase 1 — Evidence Surface Composition

- Compose Evidence Surface dari komponen attachment existing (Foundation + kartu Aggregate yang sudah ada).
- Tidak menambah API, backend, atau storage.
- Menjawab: *What evidence supports this Case?*
- Tidak mengubah Context Header / Decision Bar / panel M2.

### Phase 2 — Working Actions Composition

- Compose Working Actions Area dari kartu/dialog aksi operasional existing.
- Decision Bar tetap entry/gate (CWX-M1); Area = permukaan kerja di `main`.
- Menjawab: *What work can I perform right now?*
- Hanya aksi legal: Role ∧ Permission ∧ State ∧ Business Rule.

### Phase 3 — Integration into ComplaintDetailView and CaseDetailView

- Wire komposisi Phase 1–2 ke Dual-SoT: `ComplaintDetailView` (Foundation) dan `CaseDetailView` (Aggregate).
- Zero Duplicate Context terhadap Header / M2.
- Tidak silent-merge Dual-SoT; tidak retire Foundation.

### Phase 4 — Product Review Checklist

- [ ] Evidence Surface menjawab pertanyaan UX yang ditetapkan.
- [ ] Working Actions Area menjawab pertanyaan UX yang ditetapkan.
- [ ] Context Header tidak diubah dan tidak diduplikasi.
- [ ] Decision Bar tidak diubah dan tidak digantikan.
- [ ] Panel BLOCKED tidak muncul.
- [ ] Terasa Workspace (CWX-R), bukan form admin baru.

### Phase 5 — Quality Gate Checklist

- [ ] No backend changes.
- [ ] No API changes.
- [ ] No new architecture.
- [ ] No duplicated context.
- [ ] No governance violations (Board → ADR → EA → CONSTITUTION → GOV-001 → CWX-000 → M1 → M2 → M3).
- [ ] Definition of Done (dokumen ini) terpenuhi untuk surface READY.
- [ ] Mode B / SSO tidak disentuh.
