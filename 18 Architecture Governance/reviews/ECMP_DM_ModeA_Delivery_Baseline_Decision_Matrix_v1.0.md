# Mode A Delivery Baseline — Decision Matrix (CAP-008)

| Field | Value |
|---|---|
| Document ID | DM-MODEA-B2-001 |
| Version | 1.1 |
| Date | 2026-08-01 (BQ-004 format amended 2026-08-22) |
| Status | **LOCKED** |
| Governing DEC | DEC-MODEA-B2-001 |
| Capability | CAP-008 |

| BQ | Topic | Decision (FINAL) | Status |
|---|---|---|---|
| BQ-001 | Case state machine SoT | DEC-BQ001 O3 — Aggregate = BR-CM-CAT Definition B | LOCKED |
| BQ-002 | Mandatory Case / aging | MAY register without Case; MUST ≥1 Case within 1 business day after REGISTERED; Supervisor Queue shows exceedances | LOCKED |
| BQ-003 | Max Case per Complaint | Default max **5**; override outside Mode A | LOCKED |
| BQ-004 | Case Number | Independent; Case `UNIT-YYMM-NNNN` / Complaint `CM{UNIT}-YYMM-NNNN` (DEC-028) | LOCKED |
| BQ-005 | SLA binding | Bind SLA Policy Version; countdown NOT activated | LOCKED |
| BQ-006 | Assignment | Unit level only; Assigned User outside Mode A | LOCKED |
| BQ-007 | Close vs Complaint Closure | Close Case ≠ auto Close Complaint | LOCKED |
| BQ-008 | Resolve / Close | IN_PROGRESS → RESOLVED → Supervisor Approval → CLOSED | LOCKED |
| BQ-009 | PENDING / ESCALATED | Defined in Aggregate matrix; Mode A Delivery does NOT expose | LOCKED |
| BQ-010 | Comment / Attachment | Resolve requires Comment; Attachment optional; Complaint Attachment may be reused | LOCKED |
| BQ-011 | D-02 / wajib Case awal | D-02 retained; no Case-at-intake; timing = BQ-002 | LOCKED |
| BQ-012 | Capability ID | **CAP-008** (CAP-002 unchanged) | LOCKED |
| BQ-013 | BR-CM-CAT lock | BR-CM-CAT-001 Locked | LOCKED |
| BQ-014 | CANCELLED | Included in Mode A; reasons: Duplicate, Wrong Input, Customer Cancellation | LOCKED |

**Residual BQ: ZERO**

Pack: `ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md`
