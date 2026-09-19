# ECMP Capability Register v0.1

| Field | Value |
|---|---|
| ID | BP-CAP-001 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | Domain Product Owners / Solution Architect |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-08-01 |
| Next Review | 2027-01-21 |

## Purpose
Register kapabilitas bisnis ECMP dengan ID stabil `CAP-0xx`, dipetakan ke capability statement Blueprint (`BP-0xx`), FR, dan status delivery. Status mengikuti `26 Traceability/traceability.yaml`; register ini tidak boleh menambah kapabilitas di luar Blueprint v2.1 (DEC-001).

## Capability Register

| CAP ID | Nama Kapabilitas | Domain | BP Ref | FR Ref | Status | Owner (PO) |
|---|---|---|---|---|---|---|
| CAP-001 | Case Registration & Retrieval (complaint/inquiry create + get, write-audit) | ECMF / Core Platform | BP-001 | FR-001, FR-001a/b/c, FR-002 | Implemented (Sprint-01 slice, Approved) | Domain PO ECMF |
| CAP-002 | Case Assignment (assign/reassign ke handler/unit) | ECMF | BP-002 | FR-003 | Implemented (Sprint-02B slice, Approved) — TRC-L-003; tree `implementation/backend/` | Domain PO ECMF |
| CAP-003 | Workflow Status Transition (transisi tervalidasi sesuai konfigurasi) | ECMF | BP-002 | FR-004 | Implemented (Sprint-02B slice, Approved) — TRC-L-004; tree `implementation/backend/` | Domain PO ECMF |
| CAP-004 | Customer 360 View (search/view profil read-only + masking) | CRM | BP-003 | FR-010 | Planned (Sprint-02; TRC-L-005 Planned; API-010 draft deferred ACR-002) | Domain PO CRM |
| CAP-005 | Event-driven Notification (notifikasi assignee/supervisor atas event case) | Notification | BP-004 | FR-020 | Implemented stub (Sprint-02B, Approved) — TRC-L-006; `implementation/backend/` notification stub | Notification PO / Integration Lead |
| CAP-006 | SLA Measurement & Breach Detection (kalkulasi otomatis + EVT-004) | KPI | BP-005 | FR-030; FRD-005 (`ECMP_FRD_KPI_SLA_v0.1.md`) 🔒 **LOCKED** v0.2 (DEC-CAP006-BQ-001) | Planned / **pattern Accepted with Conditions** — TRC-L-007 Planned; FRD LOCKED B2-16; blocker **CAP006-BLK-001 lifted B2-25**; **FR-030 eng AUTHORIZED WITH SCOPE** (B2-26 / IG-20260823-01); engine not built yet | Performance Owner |
| CAP-007 | Operational Queue Dashboard (monitoring antrian oleh supervisor) | Dashboard | BP-006 | FR-040 | Implemented (B2-14) — TRC-L-008 Approved; API-040 in `implementation/backend/` + Queue Dashboard FE | Dashboard PO |
| CAP-008 | Case Management (Batch-2 Mode A) — Create/Add/View/Update/Resolve/Close Case under Complaint Aggregate | ECMF | BP-001 / BR-004 (Batch-2) | FRD-CM-B2-001 (`ECMP_FRD_Case_Management_Batch2_v1.0.md`) 🔒 LOCKED; FR-CM-B2-001…006 | **Program CLOSED** (lab) — Implemented; BCS LOCKED; Residual BQ ZERO; FRD LOCKED; OpenAPI API-530…535; REL-RC-001 PASS; tag `v1.2.0-rc.1`; GOV-CAP008-CLOSE-010 | Domain PO ECMF |

## Portfolio Disposition (B2-08 — 2026-08-01)

Governance-only rationalization after CAP-008 Program Closure. Evidence: `../deploy/evidence/B2-08_Capability_Portfolio_Rationalization_20260801.md`. No capability redesign; no BR/FRD/OpenAPI/code changes.

| CAP ID | Portfolio disposition | Next action class |
|---|---|---|
| CAP-001 | **Remain** | Keep-green / dual-SoT coexistence (DEC-020); merge only via Retirement DEC |
| CAP-002 | **Remain** | Keep-green Sprint slice; soft overlap with CAP-008 unit assignment — do not retire |
| CAP-003 | **Remain** | Keep-green Sprint slice; soft overlap with CAP-008 status path — do not retire |
| CAP-004 | **Stay Deferred** | Blocked on ACR-002 + FRD DoR + API-010; external CRM (BR-003) |
| CAP-005 | **Remain (stub) · Stay Deferred (prod engine)** | Stub Approved; production notification deferred pending catalog/engine gate |
| CAP-006 | **Pattern Accepted with Conditions** (engine still not an eng ticket) · **FRD LOCKED** · **blocker lifted (B2-25)** | FRD-005 LOCKED; Hybrid Accepted; ARC-CAP006-001/002 Accepted; B2-22 ADDITIONAL ARCHITECTURE REQUIRED; B2-23 **FULFILLMENT PATTERN NOT SPECIFIED** (historical); **B2-24** froze **CAP006-BLK-001**; **B2-25 / AR-20260823-01 Accepted with Conditions** ADR-CAP006-002 (Scheduled Command Invocation) — blocker **lifted**; **FR-030 eng NOT authorized** Implementation Gate PASS (B2-26); eng authorized with scope; engine not built |
| CAP-007 | **Remain (Implemented)** | B2-14 engineering against `dashboard-queues.v1.yaml` 1.0.0. Evidence: `../deploy/evidence/B2-14_CAP-007_Engineering_Implementation_20260801.md` |
| CAP-008 | **Remain (CLOSED)** | No delivery reopen — Program Closure GOV-CAP008-CLOSE-010 |

**Ranked posture (post-B2-25):** CAP-001/002/003/007 = maintenance only. CAP-006 engine = **pattern Accepted; Implementation Gate PASS — scoped eng ticket open** (B2-26). Deferred portfolio when DoR opens: CAP-004 → CAP-005 (prod engine).

## Catatan
- **Implemented** = FR ber-status Approved di traceability dan sudah ada di kode. Sprint slice: `implementation/backend` (TRC-L-001/002/009; CAP-002/003/005 = TRC-L-003/004/006). CAP-008 Mode A: root `backend/app/modules/cm_case/` (TRC-L-011…016).
- **Planned** = FR ber-status Planned di traceability; implementasi menunggu gate per DEC-002 (berlaku CAP-004/006/007 di register ini).
- Kapabilitas Branch/HO escalation, Schedule Slot, Appointment, Work Order **tidak terdaftar** karena out of scope (DEC-001).
- **CAP-008** registered 2026-08-01 per DEC-MODEA-B2-001 / BQ-012. Former working ID `CAP-02` retired to avoid collision with **CAP-002** Case Assignment (unchanged). BCS: `../docs/product/CAP-008_Case_Management_Business_Capability_Specification_v1.0.md`. FRD: `../03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md` (FRD-CM-B2-001 🔒 LOCKED). SoT Closure: `../deploy/evidence/CAP-008_SoT_Closure_20260801.md`.
- **SoT Closure 2026-08-01 (CAP-008 only):** Register status CAP-008 → Implemented (lab). CAP-001…007 rows were **not** changed in that closure cut.
- **B2-07 Repository Alignment 2026-08-01:** CAP-002 / CAP-003 / CAP-005 status synchronized to match `traceability.yaml` Approved + repository code evidence (Sprint slice). CAP-004 / CAP-006 / CAP-007 remain Planned (evidence absent for FR-010 / FR-030 / API-040). Evidence: `../deploy/evidence/B2-07_Repository_Capability_Alignment_20260801.md`.
- **B2-25 CAP-006 ADR-CAP006-002 Accept with Conditions 2026-08-23:** ARB **Accepted with Conditions** (AR-20260823-01); **CAP006-BLK-001 lifted**; FR-030 eng **NOT authorized** until Implementation Gate 1–4; C-3/C-4/C-6 closed; C-1 closed at IG-20260823-01; eng AUTHORIZED WITH SCOPE (B2-26). Evidence: `../deploy/evidence/B2-25_CAP-006_ADR-CAP006-002_Accept_With_Conditions_20260823.md`. No BE/FE/OpenAPI/Event/FRD/BR/scheduler.
- **ADR-CAP006-002 v0.3 2026-08-23:** status 🟢 **Accepted with Conditions**. Engine coding still closed.
- **B2-24 CAP-006 Stay Deferred Confirmation & Blocker Freeze 2026-08-04:** Historical freeze. Condition discharged by B2-25 on the non-invent branch; B2-24 text **unamended**. Evidence: `../deploy/evidence/B2-24_CAP-006_Stay_Deferred_Confirmation_Blocker_Freeze_20260804.md`.
- **B2-23 CAP-006 Time Source Fulfillment Pattern Decision 2026-08-01:** ARB verdict **FULFILLMENT PATTERN NOT SPECIFIED** — repository defines Time Source requirement only; Accepting a pattern would invent. Engine status unchanged. Evidence: `../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md`. No BE/FE/OpenAPI/Event/FRD/BR/scheduler.
- **B2-22 CAP-006 Concrete Runtime Non-Invent Gate 2026-08-01:** ARB verdict **ADDITIONAL ARCHITECTURE REQUIRED** — Time Source fulfillment pattern absent; lifecycle/outbox patterns insufficient alone. Engine status unchanged. Evidence: `../deploy/evidence/B2-22_CAP-006_Concrete_Runtime_Non_Invent_Gate_20260801.md`. No BE/FE/OpenAPI/Event/FRD/BR/scheduler.
- **B2-21 CAP-006 Runtime Architecture Specification 2026-08-01:** ARC-CAP006-002 **Runtime Architecture** Accepted (conceptual only; ONE official CAP-006 runtime SoT). Engine status unchanged. Evidence: `../deploy/evidence/B2-21_CAP-006_Runtime_Architecture_Specification_20260801.md`. No BE/FE/OpenAPI/Event/FRD/BR/scheduler.
- **B2-20 CAP-006 ADR-CAP006-001 Mechanism Class Decision Closure 2026-08-01:** ADR-CAP006-001 **ACCEPTED** (v2.0) — class **Hybrid**; concrete runtime Deferred; engine status unchanged. Evidence: `../deploy/evidence/B2-20_CAP-006_ADR-CAP006-001_Mechanism_Class_Decision_Closure_20260801.md`. No BE/FE/OpenAPI/Event/FRD/BR/scheduler.
- **B2-19 CAP-006 Time Source Concept Formalization 2026-08-01:** ARC-CAP006-001 **Time Source** Accepted (concept); ADR-CAP006-001 → v1.1. Engine status unchanged. Evidence: `../deploy/evidence/B2-19_CAP-006_Time_Source_Concept_Formalization_20260801.md`. No BE/FE/OpenAPI/Event/FRD/BR/scheduler.
- **B2-17E CAP-006 ADR-CAP006-001 Decision Closure 2026-08-01:** ARB verdict **DEFERRED** — cannot Accept event-only or job without invent / AC gap. ADR remains Proposed. Evidence: `../deploy/evidence/B2-17E_CAP-006_ADR-CAP006-001_Decision_Closure_20260801.md`. No BE/FE/OpenAPI/Event/FRD/BR.
- **B2-17D CAP-006 ADR-CAP006-001 Repository Persist 2026-08-01:** Created `../05 Architecture Decision Records/ADR-CAP006-001_Evaluation_Mechanism.md` (Proposed; mechanism **NOT SPECIFIED**). CAP-006 status unchanged. Evidence: `../deploy/evidence/B2-17D_CAP-006_ADR-CAP006-001_Repository_Persist_20260801.md`. No BE/FE/OpenAPI/Event Catalog/FRD/BR.
- **B2-16 CAP-006 FRD Lock & Governance Closure 2026-08-01:** FRD-005 → **LOCKED** v0.2; DEC-CAP006-BQ-001 applied. Engine remains Planned / Stay Deferred. Evidence: `../deploy/evidence/B2-16_CAP-006_FRD_Lock_Governance_Closure_20260801.md`. No BE/FE/OpenAPI/Event Catalog/BR.
- **B2-15 CAP-006 Business Decision Closure 2026-08-01:** DEC-CAP006-BQ-001 **BUSINESS READY** — BQ-CAP006-01…15 CLOSED/DEFERRED from repository evidence. Evidence: `../deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md`. No OpenAPI/BR/FE/BE/FRD LOCK in that cut (LOCK = B2-16).
- **B2-14 CAP-007 Engineering Implementation 2026-08-01:** API-040 Implemented (`implementation/backend` + FE Queue Dashboard); TRC-L-008 Approved; TC-040 executed (API). Evidence: `../deploy/evidence/B2-14_CAP-007_Engineering_Implementation_20260801.md`. OpenAPI unchanged.
- **B2-13 API-040 Normative Closure 2026-08-01:** API-040 → `dashboard-queues.v1.yaml` **1.0.0** NORMATIVE; draft superseded. Evidence: `../deploy/evidence/B2-13_API-040_Normative_Closure_20260801.md`. No BE/FE.
- **B2-12 CAP-007 FRD Lock & Governance Closure 2026-08-01:** FRD-006 → **LOCKED**; DEC-CAP007-BQ-001 applied. Verdict eng **NOT READY** (API-040 draft). Evidence: `../deploy/evidence/B2-12_CAP-007_FRD_Lock_Governance_Closure_20260801.md`.
- **B2-11 CAP-007 Business Decision Closure 2026-08-01:** DEC-CAP007-BQ-001 **READY** — BQ-01…05 closed from repository evidence. Evidence: `../deploy/evidence/B2-11_CAP-007_Business_Decision_Closure_20260801.md`. No OpenAPI/BR/FE/BE/FRD content edits in this cut (update plan post-approval).
- **B2-10 CAP-007 Definition of Ready 2026-08-01:** Verdict **NOT READY** — Continue Draft. Evidence: `../deploy/evidence/B2-10_CAP-007_Definition_of_Ready_20260801.md`. No OpenAPI/BR/FE/BE/FRD content edits.
- **B2-09 Queue Architecture Rationalization 2026-08-01:** ONE architecture = three lanes (CAP-007/API-040 target · Visit Queue KEEP · API-513 Aggregate KEEP). API-390 ≠ FR-040. Evidence: `../deploy/evidence/B2-09_Queue_Architecture_Rationalization_20260801.md`. No OpenAPI/BR/FE/BE edits.
- **B2-08 Portfolio Rationalization 2026-08-01:** Dispositions Remain / Stay Deferred / Merge candidate recorded above. Roadmap B2-09…B2-13 in evidence pack. CAP-008 delivery follow-up = **NONE**.
- **Program Closure 2026-08-01:** CAP-008 Mode A delivery program **CLOSED** — `../18 Architecture Governance/ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md` · Decision `…_010_Final_Closure_Decision_v1.0.md`. Follow-up on CAP-008 Mode A delivery = **NONE**. Production / Mode B remain separate gates.

## Related
- `ECMP_Business_Blueprint_v2.1_MD_Extract.md` (BP-EXT-001) §4 Capability Map
- `../26 Traceability/traceability.yaml`
- `../03 Functional Requirements/README.md`
- `../deploy/evidence/B2-08_Capability_Portfolio_Rationalization_20260801.md`
