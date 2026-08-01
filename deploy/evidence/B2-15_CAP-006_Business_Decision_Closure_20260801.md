# B2-15 — CAP-006 Business Decision Closure

| Field | Value |
|---|---|
| Document ID | GOV-B2-15-BQ-001 |
| Decision ID | **DEC-CAP006-BQ-001** |
| Sprint | B2-15 |
| Date | 2026-08-01 |
| Authority | ARB / Business Owner / Business Architect / Solution Architect / Repository Governance / Complaint SME |
| Scope | Close residual Business Questions blocking CAP-006 (SLA Engine / FR-030) — **decision package only** |
| Non-goals | No Backend / Frontend / OpenAPI / Event Catalog / BR body / DB / tests / invent SLA algorithm / invent scheduler / invent events or APIs |
| Prerequisite | CAP-006 Planned / Stay Deferred (B2-08); OQ-008 Resolved → DEC-005; DEC-004 calendar baseline |
| Verdict | **CAP-006 BUSINESS READY** |

## 1. Consolidated Business Decision Statement

**DEC-CAP006-BQ-001 (repository-evidenced):**

1. **CAP-006 SoT behaviour** = FRD-005 / FR-030 / SLA-MTX-001 / DEC-004 / DEC-005 / EVT-004 (producer KPI). **Not** BR-CM-006 Working Day Aggregate Case SLA. **Not** DEC-012/013/014 complaint-stage SLA foundation (EVT-004 deferred there).
2. **Calendar v1** = **24x7** (DEC-004 / DEC-005 / SLA-MTX §2). Working Day / business calendar activation = **DEFERRED** (fase berikut; BR-ECMF-05).
3. **Clock start** = CaseCreated (**EVT-001**). **Clock stop / finalize** = CaseClosed (**EVT-005**). **Reopen** = EVT-007 restart; re-breach after reopen allowed (Event Catalog EVT-004 idempotency).
4. **Pause / Resume** for CAP-006 v1 = **DEFERRED / OOS** (present in BR-CM-006 only; absent from FRD-005).
5. **Warning** = **80%** of target via Notification domain — **not** a new enterprise event (DEC-005 / SLA-MTX).
6. **Breach** = clock passes `dueAt` without fulfillment → emit **EVT-004** exactly once per `caseId`+`slaId` per breach cycle (FR-030 / DEC-005).
7. **Notification** on warning/breach uses Notification consumers + **BR-NOTIF-04** baseline retry/fallback (DEC-005).
8. **SLA Config** runtime owned by **Administration** (ADR-008 / BR-ADM-01); baseline numeric targets change only via DEC.
9. **Case-type target differentiation** (COMPLAINT vs INQUIRY) = **DEFERRED** (SLA-MTX Open Items; uniform baseline stands).
10. **Detection outcome** (must detect when `dueAt` exceeded) is in scope; **scheduler / evaluation mechanism** = engineering/ADR — **not** invented as business policy in B2-15.
11. **Ownership separation (not dual ownership):** ECMF owns **SLA clock attributes** on the case; KPI owns **runtime evaluation**, warning evaluation, breach detection, and **EVT-004 emission** (`06 Data Dictionary`; FRD-005 Actors; EVT-004 producer).

## 2. BQ dispositions

| BQ | Disposition | Decision |
|---|---|---|
| BQ-CAP006-01 SoT scope | **CLOSED** | Option A — FRD-005 / SLA-MTX / EVT-004 |
| BQ-CAP006-02 Calendar | **CLOSED** | 24x7 baseline; Working Day **DEFERRED** |
| BQ-CAP006-03 Clock ownership (runtime) | **CLOSED** | KPI service evaluates/emits; see §1.11 |
| BQ-CAP006-04 Clock start | **CLOSED** | EVT-001 |
| BQ-CAP006-05 Clock stop | **CLOSED** | EVT-005 |
| BQ-CAP006-06 Pause / Resume | **DEFERRED** | OOS CAP-006 v1 |
| BQ-CAP006-07 Reopen / re-breach | **CLOSED** | EVT-007 + re-breach allowed |
| BQ-CAP006-08 Scheduler mechanism | **CLOSED** (outcome) | Mechanism = engineering/ADR |
| BQ-CAP006-09 Warning 80% | **CLOSED** | DEC-005 |
| BQ-CAP006-10 Breach + EVT-004 | **CLOSED** | DEC-005 / FR-030 |
| BQ-CAP006-11 Notification | **CLOSED** | Notification + BR-NOTIF-04 |
| BQ-CAP006-12 Administration / Config | **CLOSED** | Administration owns SLA Config |
| BQ-CAP006-13 Runtime ownership | **CLOSED** | KPI runtime; Ops Lead governance |
| BQ-CAP006-14 Case-type differentiation | **DEFERRED** | Uniform until BO DEC |
| BQ-CAP006-15 Relation DEC-012/013 | **CLOSED** | Separate track ≠ CAP-006 fulfillment |

Numeric targets (First Response / Resolution per priority) remain as **DEC-005 / SLA-MTX-001** — not reopened (OQ-008 Resolved).

## 3. Exit criteria

- Business questions for CAP-006 direction = **CLOSED / DEFERRED** with evidence.
- Does **not** by itself LOCK FRD-005 (see B2-16) or authorize engineering start.
- FRD LOCK / metadata sync = B2-16.

## 4. Evidence anchors (read-only)

- `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` (CAP-006)
- `03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` (FRD-005)
- `11 SLA and KPI Matrix/ECMP_SLA_Matrix_v0.1.md` (SLA-MTX-001)
- `27 Project Decisions/DEC-004_*`, `DEC-005_*`, `DEC-012_*`, `DEC-013_*`, `DEC-014_*`
- `08 Event Catalog/events/events.yaml` (EVT-004 Planned)
- `06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` (SLA Clock / Breach Event)
- `26 Traceability/traceability.yaml` (TRC-L-007 Planned)
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-006 — separate track)

---

*End of GOV-B2-15-BQ-001.*
