# DEC — Mode A Delivery Baseline BQ Lock Pack (Batch-2 Case Management)

| Field | Value |
|---|---|
| Document ID | GOV-DEC-MODEA-B2-BQLOCK |
| Decision ID | DEC-MODEA-B2-001 |
| Version | 1.1 |
| Date | 2026-08-01 (amended 2026-08-22) |
| Owner | Product Owner / Domain PO ECMF |
| Reviewer | Architecture Board, Operations Lead, BA |
| Approver | Business Owner / Product Owner |
| Status | **APPROVED** |
| Batch | Batch-2 Mode A |
| Capability ID (final) | **CAP-008** (formerly working ID `CAP-02`) |
| Related | DEC-BQ001 (O3); BR-CM-CAT-001 Locked; FRD-CM-001 Locked; BCS CAP-008; DEC-028 (BQ-004 format 2026-08-22) |

---

## 1. Purpose

Record **FINAL** Product Owner decisions that lock all residual Business Questions for Batch-2 Mode A Case Management delivery baseline. This pack **synchronizes** repository governance only. It does not author FRD Batch-2, OpenAPI, or implementation.

---

## 2. Capability Identifier (BQ-012)

| Field | Value |
|---|---|
| Former working ID | `CAP-02` (BCS working label — collided semantically with `CAP-002` Case Assignment) |
| Final ID | **CAP-008** |
| Naming convention | Capability Register `CAP-0xx` (three-digit) — next free after CAP-007 |
| Name | Case Management (Batch-2 Mode A) — Create / Add / View / Update Status / Resolve / Close Case under Complaint Aggregate |
| Must not overwrite | **CAP-002** Case Assignment (unchanged) |

---

## 3. Locked Decisions

### BQ-001 / BQ-013
Already **LOCKED** (DEC-BQ001 O3; BR-CM-CAT-001 Locked). Unchanged.

### BQ-002 — Create Case mandatory / aging
**LOCKED**

- Complaint **MAY** be registered without a Case.
- Every Complaint **MUST** have at least one Case within **1 business day** after `REGISTERED`.
- Supervisor Queue **MUST** display complaints that exceed this threshold.

Closes **OQ-CM-B1-004**.

### BQ-003 — Max Case per Complaint
**LOCKED**

- Default maximum: **5** Cases per Complaint.
- Future override policy is **outside Mode A**.

### BQ-004 — Case Number
**LOCKED** (format string amended 2026-08-22 — DEC-028 / DL-070)

- Case Number is **independent** from Complaint Number. Independensi **tidak** dibuka.
- Format Case: `UNIT-YYMM-NNNN` (e.g. `TAB-2608-0001`)
- Format pengaduan (pasangan, agar tidak tabrakan visual): `CM{UNIT}-YYMM-NNNN` (e.g. `CMTAB-2608-0001`)
- Counter Case: per unit per bulan (`cs:UNIT:YYYYMM`), bukan per tahun global
- Format lama `CASE-YYYY-NNNNNN` / `CASE-YYYY-NNNN` **retired** for new issues

### BQ-005 — SLA Binding
**LOCKED**

- Case **SHALL** bind an SLA Policy Version.
- SLA countdown is **NOT** activated in Mode A.
- (Equivalent to Mode A **bind-without-clock**.)

### BQ-006 — Assignment
**LOCKED**

- Assignment is performed at **Unit level only**.
- Assigned User is **outside Mode A**.

### BQ-007 — Close Case vs Complaint Closure
**LOCKED** (countersign LOCK READY)

- Close Case = Case → `CLOSED` only.
- Close Case **MUST NOT** automatically close the Complaint Aggregate (BR-009 remains separate).

### BQ-008 — Resolve / Close
**LOCKED**

Mode A workflow:

`IN_PROGRESS` → `RESOLVED` → Supervisor Approval → `CLOSED`

### BQ-009 — PENDING / ESCALATED
**LOCKED**

- States remain defined inside Aggregate State Machine (BR-CM-CAT-001).
- Mode A Delivery **does NOT expose** those states.

### BQ-010 — Comment / Attachment
**LOCKED**

- Resolve **requires** Comment.
- Attachment is **optional**.
- Complaint Attachment **may** be reused.

### BQ-011 — Wajib Case awal vs D-02
**LOCKED** (countersign LOCK READY)

- Batch-1 / CTO **D-02** remains: Complaint intake does **not** create Case at registration.
- “Wajib Case awal” at intake is **not** activated for Mode A CAP-008 delivery.
- Mandatory Case timing after `REGISTERED` is governed by **BQ-002** (1 business day), not Case-at-intake.

### BQ-012 — Capability Identifier
**LOCKED** — see §2 (**CAP-008**).

### BQ-014 — Cancel Case
**LOCKED**

- `CANCELLED` **is included** in Mode A.
- Reasons include: **Duplicate**, **Wrong Input**, **Customer Cancellation**.

---

## 4. Residual Business Questions

**ZERO** for CAP-008 / Batch-2 Mode A delivery baseline (BQ-001 … BQ-014 all LOCKED).

---

## 5. Gate Status After This Pack

| Gate | Status |
|---|---|
| Business Lock | READY |
| Board Unlock | READY |
| Residual BQ | ZERO |
| FRD Batch-2 authoring prerequisite (BQ lock) | **READY** |

This pack does **not** itself publish FRD Batch-2 text. It unlocks FRD authoring.

---

## 6. Repository Synchronization Targets

- `docs/product/` BCS (CAP-008)
- `01 Business Blueprint/ECMP_Capability_Register_v0.1.md`
- `27 Project Decisions/OPEN_QUESTIONS.md`
- `27 Project Decisions/README.md`
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (Mode A policy notes; Transition Matrix SoT unchanged)
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (OQ-CM-B1-004 closed)
- `18 Architecture Governance/reviews/README.md`
- `26 Traceability/README.md`
- `docs/product/README.md` (if present)

**Out of scope for this sync (v1.0):** OpenAPI, Event Catalog, application code, Mode B, Identity redesign, Transition Matrix rewrite.

---

## 7. Amendment 2026-08-22 (v1.1)

Product Owner: BQ-004 **format string only** → opsi C (`UNIT-YYMM-NNNN` / `CM{UNIT}-YYMM-NNNN`). Independensi tidak berubah. Record: `27 Project Decisions/DEC-028_Case_Number_Unit_Month_and_HQ_Destination_v0.1.md`. OpenAPI `cm-case-management.v1.yaml` **ikut** diseragamkan pada amandemen ini.
