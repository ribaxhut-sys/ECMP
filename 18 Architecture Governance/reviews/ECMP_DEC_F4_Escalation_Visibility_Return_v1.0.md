# DEC-F4 — Escalation Visibility, Return & Result Audience

| Field | Value |
|---|---|
| Document ID | GOV-DEC-F4 |
| Decision ID | DEC-F4 |
| Version | 1.0 |
| Date | 2026-07-29 |
| Owner | Business Owner / Domain PO ECMF |
| Reviewer | Solution Architect, Operations Lead |
| Approver | Business Owner (pending Architecture Board countersign) |
| Status | 🟡 Proposed — business decisions locked in workshop; awaiting formal DEC approval |
| Related | BR-007, BR-008 (BR-CM-CAT-001), ADR-014, ADR-015, INT-001 |

---

## 1. Context

ECMP will operate as an Enterprise Business Module (ADR-014). Workshop decisions are required for:

- Head Office (Pusat) visibility of escalated work vs monitoring
- Presence/absence of Regional tier on the complaint escalation path
- Post-resolve result visibility to branches
- Head Office ability to return incomplete escalations
- Control of who may see resolved results

FRD-CM-001 Batch 1 remains **LOCKED** and **unchanged** by this DEC (escalation/resolution execution remains outside Batch 1 SoT). This DEC amends **BR-CM-CAT-001 Draft** (BR-007 / BR-008) as the target business specification for later FRD batches / remapping DEC.

---

## 2. Locked Decisions

| ID | Decision | Status |
|---|---|---|
| **F4** | Visibility model **B**: Pusat handlers work only cases escalated/assigned to Pusat; analyst/viewer roles may have cross-branch KPI/monitoring without default detail access to non-escalated branch cases | Locked |
| **F4.1** | **No Regional** on the complaint escalation path — path is **Cabang → Pusat** only | Locked |
| **F4.2** | After Pusat **resolve**, the **originating branch always** may read the result | Locked |
| **F4.3** | Pusat selects result audience: `ORIGIN_BRANCH` or `ALL_BRANCHES` | Locked |
| **F4.3a** | `result_visibility` is set at **Resolve** and **may be changed later** (audit required) | Locked |
| **F4.4** | Pusat may **return** an escalation to the originating branch when information/package is incomplete | Locked |
| **F4.5** | Return requires **mandatory reason code** + **mandatory free-text note** | Locked |
| **F4-OQ-01** | `return_note` minimum length = **10** (trim then count) | Closed |
| **F4-OQ-02** | Originating branch **read-only** while Pusat owns Case; write after Return | Closed |

### Defaults

| Parameter | Default |
|---|---|
| `result_visibility` at Resolve | `ORIGIN_BRANCH` |
| Return target | Originating branch only (`returned_to_branch_id` = escalate-from branch) |

---

## 3. Visibility Model

### 3.1 Organization path (complaint escalation)

```
Cabang → Pusat
```

Regional is **out of scope** for this DEC’s escalation path. Enterprise Platform may still own Regional org units for other modules; ECMP complaint escalate/return UI and APIs under this DEC must not offer Regional as a target.

### 3.2 Work queues

| Actor | Non-escalated case at another branch | Case escalated to Pusat | After Resolve |
|---|---|---|---|
| Originating branch agent/supervisor | N/A (own branch: RW per role) | Read per policy while owned by Pusat | Read result (always) |
| Other branch | No | No | Only if `result_visibility = ALL_BRANCHES` (read-only) |
| Pusat handler | No (not in work queue) | RW + full Escalation Package history | Read |
| Pusat analyst / viewer | KPI/monitoring only; detail of non-escalated cases only with explicit permission | Per permission | Per permission |

### 3.3 `result_visibility`

| Value | Meaning |
|---|---|
| `ORIGIN_BRANCH` | Originating branch + Pusat may read resolved result/history; other branches must not find the case in search/list/detail |
| `ALL_BRANCHES` | All branches (authorized complaint roles) may **read-only** the resolved result and permitted history |

- Set **at Resolve** (UI should require explicit selection; system default if omitted = `ORIGIN_BRANCH`).
- May be changed **after Resolve** by authorized Pusat actors.
- Every change records audit: `from`, `to`, `changed_by`, `changed_at`, optional `change_note`.
- **Return must not** set or imply `result_visibility`.

---

## 4. Return / De-escalation (F4.4 / F4.5)

Aligned with BR-007 A4 / E1; sharpened by this DEC:

1. Allowed only while case is owned by Pusat (escalated to Pusat).
2. Target is always the **originating branch**.
3. Required fields:
   - `return_reason_code` (controlled enum)
   - `return_note` (free text; minimum length configurable, recommended ≥ 10 characters)
4. Escalation History is append-only: prior Pusat work and return reason remain visible.
5. Ownership returns to originating branch; Pusat drops the case from handler work queue until re-escalated.
6. Notifications to originating branch and related assignees.
7. Re-escalation after completion is allowed; package remains cumulative (No Information Lost).

### Baseline reason codes (catalog may extend via Administrator)

| Code | Meaning |
|---|---|
| `MISSING_ATTACHMENT` | Required attachment/evidence missing |
| `INCOMPLETE_CHRONOLOGY` | Chronology/timeline incomplete |
| `UNCLEAR_CUSTOMER_DATA` | Customer/reference data unclear or inconsistent |
| `WRONG_CATEGORY_OR_ROUTING` | Wrong category or should not have been escalated on this path |
| `ADDITIONAL_EVIDENCE_REQUIRED` | Additional evidence requested by Pusat |
| `OTHER` | Other — `return_note` must explain |

---

## 5. Field Contract (implementation-facing)

### Return

| Field | Required | Owner |
|---|---|---|
| `return_reason_code` | Yes | Actor (Pusat) |
| `return_note` | Yes | Actor (Pusat) |
| `returned_to_branch_id` | System | Originating branch |
| `returned_by` / `returned_at` | System | Identity + clock |

### Resolve visibility

| Field | Required | Owner |
|---|---|---|
| `result_visibility` | Yes at Resolve (or default `ORIGIN_BRANCH`) | Actor (Pusat) |
| Visibility change after Resolve | Allowed | Authorized Pusat + Audit |

---

## 6. Acceptance Criteria

1. Escalation path offers **Pusat** only (no Regional target) under this DEC.
2. Pusat handler work queue contains only cases escalated/assigned to Pusat.
3. Pusat can **Return** with mandatory `return_reason_code` + `return_note`; missing either → reject.
4. After Return, originating branch regains operational ownership; history intact.
5. After Pusat Resolve, originating branch can always read the result.
6. Resolve sets `result_visibility`; default `ORIGIN_BRANCH`.
7. `ORIGIN_BRANCH`: other branches cannot access the case.
8. `ALL_BRANCHES`: other branches have read-only access to resolved result/permitted history.
9. Pusat may change `result_visibility` after Resolve; audit mandatory.
10. Return does not set `result_visibility`.

### UAT references

`UAT-F4-01` … `UAT-F4-11` (workshop pack; to be formalized in Test Strategy when escalation/resolution FRD batch is opened).

---

## 7. Document Impact

| Artifact | Action |
|---|---|
| `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` | Amended BR-007 / BR-008 (Draft v1.1 content) |
| `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` | **No change** (LOCKED Batch 1) |
| `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md` | **FRD-CM-002 Draft** |
| `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_Outline_v0.1.md` | Outline retained; FR content superseded by FRD-CM-002 Draft |
| `07 API Catalog/openapi/complaint-management-esc-res.v1.yaml` | Planned API-520…526 |
| `08 Event Catalog/events/events.yaml` | Planned EVT-CM-040…044 |
| `13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md` | Formal UAT-F4-01…11 |
| `18 Architecture Governance/reviews/ECMP_DEC_F4_Architecture_Board_Countersign_Pack_v1.0.md` | Board countersign pack |
| `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md` | Authoritative impact (EOS auto BR-007 collides Sprint ID) |
| Future FRD LOCK | Requires Architecture Board countersign of DEC-F4 |
| ADR-014 / ADR-015 | Unchanged; F4.1 is complaint-path policy, not removal of org tiers from Enterprise Platform |

---

## 8. Open Follow-ups

| ID | Topic | Owner | Status |
|---|---|---|---|
| F4-OQ-01 | Exact minimum length / i18n for `return_note` | BA | **Closed** — minimum **10** characters after trim |
| F4-OQ-02 | Whether branch may write while case is at Pusat | BA / Operations | **Closed** — originating branch **read-only** while Pusat owns Case; write restored after Return |
| F4-OQ-03 | Formal Architecture Board countersign | Solution Architect | Pack ready (`GOV-CS-DEC-F4`) — awaiting signatures |
| F4-OQ-04 | Map UAT-F4-* into Test Strategy | QA Lead | **Closed** — `TC-CAT-CM-F4-001` |

---

## 9. Approval

| Role | Name | Date | Sign-off |
|---|---|---|---|
| Business Owner | | | ☐ |
| Domain PO ECMF | | | ☐ |
| Solution Architect | | | ☐ |
| Architecture Board | | | ☐ |

---

## Related

- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-007, BR-008)
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md` (FRD-CM-002 Draft)
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_Outline_v0.1.md`
- `05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.0.md`
- `05 Architecture Decision Records/ECMP_ADR_015_Enterprise_Identity_Contract_v1.0.md`
- `07 API Catalog/openapi/complaint-management-esc-res.v1.yaml`
- `09 Integration Catalog/ECMP_INT_001_Customer_Master_Read_v0.1.md`
- `13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md`
- `18 Architecture Governance/reviews/ECMP_DEC_F4_Architecture_Board_Countersign_Pack_v1.0.md`
- `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md`
