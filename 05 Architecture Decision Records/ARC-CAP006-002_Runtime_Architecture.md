# ARC-CAP006-002 — Runtime Architecture (CAP-006 / FR-030)

| Field | Value |
|---|---|
| Document ID | ARC-CAP006-002 |
| Title | Runtime Architecture |
| Document Type | Architecture Concept (formal) — **conceptual runtime only** |
| Version | 1.0 |
| Owner | Solution Architect / Performance Owner |
| Reviewer | Architecture Review Board |
| Approver | Architecture Board |
| Status | 🟢 **Accepted** — conceptual Runtime Architecture (B2-21); **not** an implementation authorization |
| Last Review | 2026-08-01 |
| Next Review | 2026-10-01 |
| Capability | CAP-006 (SLA Measurement & Breach Detection) |
| FR | FR-030 |
| Trace | TRC-L-007 |
| Governing ADR | ADR-CAP006-001 **Accepted** (B2-20) — mechanism class **Hybrid** |
| Related Concept | ARC-CAP006-001 Time Source **Accepted** (B2-19) |
| Persist sprint | B2-21 — `../deploy/evidence/B2-21_CAP-006_Runtime_Architecture_Specification_20260801.md` |

> **ONE official CAP-006 Runtime Architecture** for this repository.  
> Specifies **conceptual** stages, responsibilities, boundaries, and ownership only.  
> Does **not** select scheduler, cron, polling, queue, worker, retry, SQL, persistence, thread, timer implementation, or algorithms.

## 1. Official name

**Runtime Architecture** (CAP-006) — nama resmi dokumen konsep: **ARC-CAP006-002**.

## 2. Purpose

1. Menjadikan repository memiliki **satu** spesifikasi runtime **konseptual** resmi untuk CAP-006 setelah mechanism class **Hybrid** diterima (ADR-CAP006-001).
2. Memisahkan tegas: **kelas mekanisme** (Accepted) · **arsitektur runtime konseptual** (Accepted di sini) · **desain teknis konkret / engine** (tetap Deferred).
3. Mengikat ownership dan boundary agar engineering kelak tidak menginvent domain, event, API, atau tanggung jawab silang di luar katalog.

## 3. Classification

| Question | Board decision |
|---|---|
| Domain baru? | **Tidak** |
| Service produk baru? | **Tidak** |
| Runtime concern? | **Ya** — runtime evaluasi CAP-006 di dalam **KPI & Performance** |
| Implementation authorization? | **Tidak** — Accept konsep ≠ izin FR-030 engine |
| Relasi ke ARCH-EXEC-RT-001 (`20 Domain Architecture/Execution/EXECUTION_RUNTIME_ARCHITECTURE.md`) | **Bukan SoT CAP-006**; tidak diadopsi sebagai Runtime Architecture CAP-006 pada B2-21 |

## 4. Governing constraints (repository SoT)

| Artifact | Binding constraint |
|---|---|
| ADR-CAP006-001 | Mechanism class = **Hybrid** (lifecycle events **and** Time Source — both mandatory) |
| ARC-CAP006-001 | Time Source = stimulus evaluasi berbasis waktu; milik concern KPI; bukan domain |
| FRD-005 LOCKED | Event flow + AC: *waktu berjalan melewati dueAt* → EVT-004 |
| DEC-CAP006-BQ-001 | Start EVT-001; stop EVT-005; reopen EVT-007; warning 80% Notification; ownership separation |
| ADR-001 | Integrasi antar-domain = event-driven async; near-real-time breach = goal |
| ADR-009 | Emit durable via transactional outbox; broker deferred; no generic publisher retry/DLQ pre-broker |
| Data Dictionary | SLA Clock → ECMF; SLA Config → Administration; Breach Event / evaluation → KPI |
| Event Catalog | EVT-004 producer KPI; no enterprise time-tick event |

---

## 5. Runtime stages (conceptual)

Stages are **logical**. Order is lifecycle-significant, not a technology pipeline.

| Stage ID | Stage | Stimulus | Outcome (conceptual) |
|---|---|---|---|
| RS-01 | **Config awareness** | EVT-006 (ConfigChanged) — when SLA-relevant config effective | KPI aware of active SLA Config parameters (targets / binding context) |
| RS-02 | **Clock arming** | EVT-001 (CaseCreated) | Active SLA clock cycle becomes evaluable for the case (attributes SoT remain ECMF) |
| RS-03 | **Clock status sync** | EVT-003 (StatusChanged) | Evaluation view reflects operational status history basis for fulfillment/clock behaviour per FRD |
| RS-04 | **Time-threshold observation** | **Time Source** (ARC-CAP006-001) | Wall-clock progress vs `dueAt` can be observed **including silent periods** (no lifecycle event at threshold) |
| RS-05 | **Warning evaluation** | Time Source observation + active clock + config | At 80% target elapsed → Notification path (DEC-005); **not** a new enterprise event |
| RS-06 | **Breach evaluation & emit** | Time Source observation + active clock without fulfillment | Once per `caseId`+`slaId` per breach cycle → produce **EVT-004**; durable emit path per ADR-009 |
| RS-07 | **Clock stop / finalize** | EVT-005 (CaseClosed) | No further breach for closed cycle; performance fact finalized conceptually |
| RS-08 | **Reopen restart** | EVT-007 (CaseReopened) — catalog status **Proposed** | New/restarted clock cycle; re-breach after reopen **allowed** (EVT-004 idempotency rule) |

**Hybrid binding:** RS-02/03/07/08 require **lifecycle events**; RS-04/05/06 require **Time Source**. Neither set alone is the Accepted runtime.

---

## 6. Runtime responsibilities

| Party | Responsibility inside CAP-006 runtime concept |
|---|---|
| **KPI & Performance** | Owns **runtime evaluation**, warning evaluation, breach detection, **EVT-004 emission**, and use of Time Source stimulus |
| **ECMF** | Owns **SLA clock attributes** / status-history basis; produces EVT-001/003/005/007 that supply/update clock **state** for KPI |
| **Administration** | Owns **SLA Config** SoT; produces EVT-006 when effective config changes; KPI reads active values |
| **Notification** | Consumes evaluation **outcomes** (warning alert path; EVT-004 for breach escalation) — does **not** evaluate SLA |
| **Dashboard & Analytics** | Consumes breach/operational facts for display (EVT-004 consumer; aggregated metrics) — does **not** evaluate or emit EVT-004 |
| **Core Platform (outbox)** | Durable emit path for domain events including EVT-004 after KPI decision — **not** Time Source and **not** evaluator |

---

## 7. Runtime boundaries

### In boundary (CAP-006 conceptual runtime)

1. Hybrid evaluation loop: lifecycle **state inputs** + Time Source **time stimulus** + KPI **decision**.
2. Warning (80%) and breach (`dueAt` exceeded without fulfillment) as defined by FRD-005 / DEC-005 / DEC-CAP006-BQ-001.
3. Emission of catalogued **EVT-004** by KPI.
4. Calendar context **24x7** baseline (DEC-004 / DEC-005) as “waktu berjalan” v1.

### Out of boundary

1. Scheduler / cron / polling / worker / queue / retry / SQL / persistence schema / timer **implementation**.
2. New enterprise events (e.g. TimeTick / DueReached) or new OpenAPI for FR-030.
3. Ownership of SLA clock **attributes** (ECMF) or SLA **Config** (Administration).
4. Notification delivery engine / BR-NOTIF-04 retry as CAP-006 evaluation mechanism.
5. Dashboard widget / queue UI (CAP-007) as breach detector.
6. Pause/Resume clock; working-day calendar activation; COMPLAINT vs INQUIRY target differentiation (DEFERRED / OOS per FRD-005 §9).
7. DEC-012/013/014 complaint-stage SLA as CAP-006 fulfillment.
8. Adoption of **ARCH-EXEC-RT-001** Execution Runtime as CAP-006 engine (not decided here).
9. FR-030 engineering start (requires separate gate; this ARC does not authorize).

---

## 8. State ownership

| State concern | Owner | Notes |
|---|---|---|
| SLA Clock **attributes** (running timer facts / status history basis) | **ECMF** | Data Dictionary entity SLA Clock → ECMF |
| SLA **Config** parameters (targets, calendar binding when activated) | **Administration** | Data Dictionary SLA Config; KPI reads active values (e.g. via EVT-006) |
| **Evaluation decision state** (whether warning/breach conditions hold for an active cycle; emission intent for EVT-004) | **KPI** | Derived runtime concern; not dual SoT of ECMF clock attributes |
| **Breach Event** fact (post-emit conceptual record) | **KPI** | Data Dictionary Breach Event → KPI |
| **Performance Fact** (finalize on close) | **KPI** | Derived from operational events; BR-KPI-04 traceability |

Separation of responsibility per FRD-005 §2a / DEC-CAP006-BQ-001 §11 — **not** competing dual SoT for the same function.

---

## 9. Evaluation ownership

| Evaluation concern | Owner |
|---|---|
| Compare elapsed / wall-clock progress to `dueAt` | **KPI** |
| Detect warning threshold (80%) | **KPI** |
| Detect breach (dueAt passed without fulfillment) | **KPI** |
| Decide emit EVT-004 (once per caseId+slaId per cycle; re-breach after reopen allowed) | **KPI** |
| Supply time-based evaluation **stimulus** | **Time Source** (concept owned as KPI runtime/infrastructure concern — ARC-CAP006-001) |
| Supply/update clock **state** via lifecycle events | **ECMF** (producer); **KPI** (consumer for evaluation) |

**Non-owners of evaluation:** Notification, Dashboard, Administration, Core Platform outbox, Execution Runtime (ARCH-EXEC-RT-001).

---

## 10. Event ownership

| Event | Producer | CAP-006 runtime role | Consumer relevance (CAP-006) |
|---|---|---|---|
| EVT-001 CaseCreated | ECMF | Clock arming (RS-02) | KPI |
| EVT-003 StatusChanged | ECMF | Clock status sync (RS-03) | KPI |
| EVT-005 CaseClosed | ECMF | Stop / finalize (RS-07) | KPI |
| EVT-007 CaseReopened | ECMF | Restart cycle (RS-08); status **Proposed** | KPI |
| EVT-006 ConfigChanged | Administration | Config awareness (RS-01) | KPI (reload SLA rules) |
| EVT-004 SLABreached | **KPI** | Breach outcome emit (RS-06); status **Planned** | Notification, Dashboard |

**Explicit non-events:** no TimeTick / DueReached / Warning enterprise event. Warning uses Notification domain path only.

**ADR-001 / ADR-009:** Inter-domain flow remains event-driven; EVT-004 follows transactional outbox until broker selection. Time Source is **intra-KPI** stimulus, not a replacement for ECMF→KPI events.

---

## 11. Configuration ownership

| Config concern | Owner | Runtime implication |
|---|---|---|
| SLA Config / rules parameters | **Administration** | SoT; changes via governance; effective change signalled by EVT-006 |
| Numeric targets / warning 80% / breach→EVT-004 policy baseline | **DEC-005 / SLA-MTX-001** (policy) | Not reinvented in runtime; KPI observes configured values |
| Calendar baseline 24x7 | **DEC-004 / DEC-005** | Working-day calendar = DEFERRED |
| Case-type target differentiation | **DEFERRED** | Uniform baseline until BO DEC |

KPI **reads** active configuration; KPI does **not** own SLA Config SoT.

---

## 12. Notification boundary

| In Notification boundary | Out of Notification boundary |
|---|---|
| Consume warning outcome (80%) as alert routing | Evaluate whether 80% elapsed |
| Consume EVT-004 for breach escalation to supervisor/manager | Decide breach or emit EVT-004 |
| Apply Notification rules / templates / delivery (incl. BR-NOTIF-04 baseline) | Own Time Source or SLA clock attributes |
| | Replace CAP-006 Hybrid evaluation |

Notification is a **downstream consequence consumer**, not part of the Hybrid evaluation mechanism class.

---

## 13. Dashboard boundary

| In Dashboard boundary | Out of Dashboard boundary |
|---|---|
| Consume EVT-004 / operational projections for display | Detect SLA breach |
| Aggregated Metrics / widgets (Data Dictionary) with reconcile posture (BR-DASH-02) | Emit EVT-004 |
| CAP-007 queue monitoring (separate capability) | Own SLA Config or SLA clock attributes |
| | Act as Time Source |

Dashboard is a **read/consumer surface**, not the CAP-006 evaluator.

---

## 14. Runtime lifecycle (conceptual)

```text
[Administration] --EVT-006--> [KPI: config awareness]
[ECMF] --EVT-001/003--> [KPI: clock state view]
                              |
                              +-- Time Source (time stimulus) --> [KPI: warn / breach evaluate]
                              |                                      |
                              |                                      +-- warning --> [Notification]
                              |                                      +-- breach  --> [KPI emit EVT-004]
                              |                                                      via outbox (ADR-009)
                              |                                                            |
                              |                                                            +--> [Notification]
                              |                                                            +--> [Dashboard]
[ECMF] --EVT-005--> [KPI: stop / finalize]
[ECMF] --EVT-007--> [KPI: restart cycle]   (EVT-007 Proposed)
```

---

## 15. Deferred technical design (explicit)

Remains **Deferred** (not specified by this ARC):

- Scheduler / cron / worker / polling interval or strategy
- Queue technology for evaluation
- Retry of evaluation/emit (distinct from BR-NOTIF-04)
- SQL / physical persistence of SLA Clock projection / emission ledger
- Timer implementation
- Recovery / catch-up procedures
- Engine observability / metrics
- Fulfillment predicate detail, multi-clock model, `slaId` allocation beyond catalog
- Binding (if any) to ARCH-EXEC-RT-001 Execution Runtime
- FR-030 engineering implementation

## 16. Compatibility

| Concern | Impact of ARC-CAP006-002 |
|---|---|
| ADR-CAP006-001 | Unchanged class (**Hybrid**); this ARC fills **conceptual runtime** layer only |
| ARC-CAP006-001 | Unchanged; Time Source remains mandatory stimulus at RS-04/05/06 |
| ADR-001 / ADR-009 | Unchanged |
| FRD-005 / Business Rules / OpenAPI / Event Catalog | **Unchanged** |
| CAP-006 engine delivery status | **Unchanged** — Planned / Stay Deferred |
| Technical Runtime Design (B2-22) | **Not unlocked** — ADDITIONAL ARCHITECTURE REQUIRED (Time Source fulfillment) |
| Time Source fulfillment pattern (B2-23) | **NOT SPECIFIED** — repository defines requirement, not fulfillment pattern |

## 17. Document History

| Ver | Date | Change |
|---|---|---|
| 1.0 | 2026-08-01 | B2-21 — Official conceptual Runtime Architecture Accepted; no implementation |
| 1.0a | 2026-08-01 | B2-22 — Non-Invent Gate cross-ref; Technical Runtime Design blocked pending Time Source fulfillment architecture |
| 1.0b | 2026-08-01 | B2-23 — fulfillment pattern NOT SPECIFIED confirmed |

## Related Documents

- `./ADR-CAP006-001_Evaluation_Mechanism.md`
- `./ARC-CAP006-001_Time_Source.md`
- `../03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` (FRD-005 LOCKED)
- `../deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md` (DEC-CAP006-BQ-001)
- `../deploy/evidence/B2-20_CAP-006_ADR-CAP006-001_Mechanism_Class_Decision_Closure_20260801.md`
- `../deploy/evidence/B2-21_CAP-006_Runtime_Architecture_Specification_20260801.md`
- `../deploy/evidence/B2-22_CAP-006_Concrete_Runtime_Non_Invent_Gate_20260801.md`
- `../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md`
- `./ECMP_ADR_001_Event_Driven_Domain_Integration_v1.0.md`
- `./ECMP_ADR_009_Message_Broker_Deferral_v1.0.md`
- `../08 Event Catalog/events/events.yaml`
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`
- `../01 Business Blueprint/ECMP_Capability_Register_v0.1.md`
- `../26 Traceability/traceability.yaml` (TRC-L-007)
