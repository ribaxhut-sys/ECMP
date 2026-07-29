# UAT / Test Catalog — DEC-F4 Escalation Visibility, Return & Result Audience

| Field | Value |
|---|---|
| ID | TC-CAT-CM-F4-001 |
| Version | 1.0 |
| Owner | QA Lead |
| Reviewer | BA / Solution Architect |
| Approver | Architecture Board (with DEC-F4) |
| Status | 🟡 Planned (authored; not executed) |
| Date | 2026-07-29 |
| Decision | GOV-DEC-F4 |
| Business Rules | BR-CM-CAT-001 BR-007, BR-008 (Draft v1.1) |
| FRD | Future Escalation/Resolution batch (not FRD-CM-001 Batch 1) |
| Namespace | `UAT-F4-*` / `TC-CM-F4-*` |

## Purpose

Formalize workshop UAT scenarios for DEC-F4. **Out of Batch 1 execution scope.** Execute when Escalation/Resolution FRD + APIs exist.

## Preconditions (environment)

- Enterprise Mode / org claims available (`branch_id`, etc.) or test doubles
- Two branches: **Cabang A** (origin), **Cabang B** (other)
- Roles: Agent Cabang A, Agent Cabang B, Handler Pusat, Analyst Pusat (optional)
- Case can be created and escalated in the target FRD batch (not Batch 1-only stack)

---

## Summary

| Area | IDs | Priority |
|---|---|---|
| Visibility B + path | UAT-F4-01, 04 | Must |
| Resolve audience | UAT-F4-01, 02, 10, 11 | Must |
| Return | UAT-F4-05, 06, 07, 08, 09 | Must |
| No Regional | UAT-F4-04 | Must |
| **Total** | **11** | |

---

## Catalog

| ID | Title | Expected | BR / DEC |
|---|---|---|---|
| UAT-F4-01 | Resolve `ORIGIN_BRANCH` | After Pusat resolve with `ORIGIN_BRANCH`, Cabang A reads result; Cabang B cannot find case | F4.2, F4.3, BR-008 |
| UAT-F4-02 | Resolve `ALL_BRANCHES` | After resolve with `ALL_BRANCHES`, Cabang B read-only can open result/permitted history | F4.3, BR-008 |
| UAT-F4-03 | Handler queue scoped | Pusat handler work queue shows only escalated/assigned-to-Pusat cases; non-escalated Cabang A case absent | F4, BR-007 |
| UAT-F4-04 | No Regional target | Escalate UI/API offers Pusat only; selecting Regional rejected/unavailable | F4.1, BR-007 |
| UAT-F4-05 | Return incomplete package | Pusat returns with reason; Cabang A notified; ownership back; history keeps Pusat work + return | F4.4, BR-007 A4 |
| UAT-F4-06 | Return without reason | Missing `return_reason_code` or `return_note` → reject | F4.5, BR-007 E6 |
| UAT-F4-07 | Return is not Resolve | After return, `result_visibility` unset; Cabang B still cannot see case | F4.4, BR-007/008 |
| UAT-F4-08 | Return valid fields | Kode + catatan both present → success; timeline shows both | F4.5 |
| UAT-F4-09 | Return invalid partial | Only code or only note → reject | F4.5 |
| UAT-F4-10 | Change visibility later | `ORIGIN_BRANCH` → `ALL_BRANCHES` after resolve → Cabang B gains read; audit `from`/`to` | F4.3a, BR-008 A4 |
| UAT-F4-11 | Revert visibility | `ALL_BRANCHES` → `ORIGIN_BRANCH` → Cabang B loses access again; audit recorded | F4.3a |

---

## Detailed scripts (Must)

### UAT-F4-01 — ORIGIN_BRANCH

1. Cabang A: create/handle case → escalate to Pusat (package complete).  
2. Pusat: resolve; set `result_visibility = ORIGIN_BRANCH`.  
3. Cabang A: open case → **see** resolution + history.  
4. Cabang B: search/list/direct id → **no access** (empty or 403).  

### UAT-F4-02 — ALL_BRANCHES

1. Repeat escalate path (or use another case).  
2. Pusat resolve with `ALL_BRANCHES`.  
3. Cabang B: **read-only** open succeeds; write/update denied.  

### UAT-F4-05 — Return

1. Cabang A escalate.  
2. Pusat Return: `return_reason_code = MISSING_ATTACHMENT`, `return_note` filled.  
3. Cabang A receives notification; can edit/upload; can re-escalate.  
4. Timeline: Escalated → Returned (code+note) → branch activity.  

### UAT-F4-10 — Change after Resolve

1. Resolve as `ORIGIN_BRANCH` (UAT-F4-01 state).  
2. Pusat changes to `ALL_BRANCHES` with optional change note.  
3. Cabang B can read; Audit shows previous→new, actor, time.  

---

## Traceability (logical)

| DEC | BR | UAT |
|---|---|---|
| F4 | BR-007 | UAT-F4-03 |
| F4.1 | BR-007 | UAT-F4-04 |
| F4.2 | BR-008 | UAT-F4-01 |
| F4.3 | BR-008 | UAT-F4-01, 02 |
| F4.3a | BR-008 | UAT-F4-10, 11 |
| F4.4 | BR-007 | UAT-F4-05, 07 |
| F4.5 | BR-007 | UAT-F4-06, 08, 09 |

API / Event / TC-CM-F4-* implementation IDs: mapped in FRD-CM-002 / RTM-CM-F4-001 (API-520…526, EVT-CM-040…044). Execution still blocked until APIs implemented.

### OQ closures affecting UAT

- F4-OQ-01: `return_note` min length 10 — assert in UAT-F4-06/08/09  
- F4-OQ-02: branch read-only at Pusat — assert write denied before Return; write allowed after Return (extend UAT-F4-05)


---

## Related

- `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`
- `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md`
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md`
