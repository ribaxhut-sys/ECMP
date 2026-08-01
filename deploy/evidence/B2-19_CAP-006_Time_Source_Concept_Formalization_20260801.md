# B2-19 — CAP-006 Time Source Architecture Concept Formalization

| Field | Value |
|---|---|
| Document ID | GOV-B2-19-ARC-001 |
| Sprint | B2-19 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Solution Architect / Repository Governance |
| Scope | Formalize **Time Source** as official Architecture Concept; sync ADR-CAP006-001 v1.1 + metadata |
| Non-goals | No Backend / Frontend / DB / OpenAPI / Event Catalog / FRD body / BR / scheduler / polling / retry / invent domain |
| Prerequisite | ADR-CAP006-001 Proposed (B2-17D/E); FRD-005 LOCKED; DEC-CAP006-BQ-001; Workshop B2-18 |
| Verdict | **ARCHITECTURE CONCEPT FORMALIZED** |

## 1. Repository files audited

| Artifact | Role |
|---|---|
| `05 Architecture Decision Records/ADR-CAP006-001_Evaluation_Mechanism.md` | Evaluation mechanism ADR (updated → v1.1) |
| `03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` | FRD-005 LOCKED — time-based AC |
| `deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md` | DEC-CAP006-BQ-001 |
| `deploy/evidence/B2-17E_CAP-006_ADR-CAP006-001_Decision_Closure_20260801.md` | Mechanism Accept DEFERRED |
| `05 Architecture Decision Records/ECMP_ADR_001_Event_Driven_Domain_Integration_v1.0.md` | Inter-domain event-driven |
| `05 Architecture Decision Records/ECMP_ADR_009_Message_Broker_Deferral_v1.0.md` | Outbox; broker deferred |
| `08 Event Catalog/events/events.yaml` | EVT-004 Planned; no time-tick event |
| `06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` | SLA Clock → ECMF; Breach → KPI |
| Workshop B2-18 | Draft Decision: Time Source required; event-only rejected; hybrid class |

## 2. Architecture Concept

| ID | Official name | Status |
|---|---|---|
| **ARC-CAP006-001** | **Time Source** | 🟢 **Accepted** (concept only) |

Path: `05 Architecture Decision Records/ARC-CAP006-001_Time_Source.md`

## 3. Board definitions (summary)

| # | Topic | Decision |
|---|---|---|
| 1 | Definition | Stimulus evaluasi berbasis waktu agar KPI dapat bandingkan “now” vs `dueAt` tanpa menunggu EVT lifecycle di ambang |
| 2 | Purpose | Menutup celah event-only; dukung near-real-time breach secara konsep; SoT tanpa invent runtime |
| 3 | Boundary | Requirement + ownership separation + kompatibel ADR-001/009 + kalender 24x7 |
| 4 | Non-scope | Bukan domain/service baru; bukan scheduler/poll/retry/DB/OpenAPI/Event baru; bukan ubah BR |
| 5 | Relationships | KPI owns; ECMF = clock attributes; Admin = SLA Config; Notification = consumer akibat |
| 6 | ADR-001 / ADR-009 | Tidak direvisi; klarifikasi boundary saja |
| 7 | Classification | **Infrastructure / runtime concern** KPI (Architecture Concept) — bukan domain |
| 8 | Business Rules | **Tidak berubah** |
| 9 | OpenAPI | **Tidak diperlukan** |
| 10 | Event Catalog | **Tidak menambah** event |

## 4. What was persisted

| Artifact | Action |
|---|---|
| `ARC-CAP006-001_Time_Source.md` | **Created** — Accepted Architecture Concept |
| `ADR-CAP006-001_Evaluation_Mechanism.md` | **Updated** → v1.1 (event-only rejected; Time Source required; hybrid class; job NOT SPECIFIED) |
| This evidence file | Created |

## 5. Metadata sync

- `05 Architecture Decision Records/README.md`
- `05 Architecture Decision Records/ADR_INDEX.generated.md`
- `CHANGELOG.md` [Unreleased]
- Capability Register — reference note only; CAP-006 status **unchanged** (Planned / Stay Deferred)
- `26 Traceability/traceability.yaml` + `TRACEABILITY_MATRIX.md` — reference ARC-CAP006-001
- `18 Architecture Governance/README.md` — Related pointer

## 6. Explicit non-changes

CAP-006 engine status · FRD-005 body · Event Catalog · OpenAPI · Business Rules · application code · database · scheduler implementation.

## 7. ADR Update Plan (follow-up)

| Step | Intent |
|---|---|
| **Done (B2-19)** | Formalize ARC-CAP006-001; ADR-CAP006-001 v1.1 records direction |
| **Next (recommended B2-20)** | ARB Decision Closure: **Accept** evaluation mechanism **class** = hybrid (lifecycle events + Time Source), still **without** inventing job/scheduler detail; or keep Proposed until runtime design exists in-repo without invent |
| **Later** | Runtime design ADR/addendum only when repository has non-invent basis (patterns already present) + engineering gate |

## 8. Recommended next sprint

**B2-20 — ADR-CAP006-001 Mechanism Class Decision Closure** (governance-only): Accept/reject hybrid class citing ARC-CAP006-001; concrete job remains Deferred; no engineering.

---

*End of GOV-B2-19-ARC-001.*
