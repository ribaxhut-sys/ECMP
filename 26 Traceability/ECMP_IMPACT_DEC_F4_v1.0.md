# Impact Analysis — DEC-F4 (Escalation Visibility, Return & Result Audience)

| Field | Value |
|---|---|
| Document ID | GOV-IMPACT-DEC-F4 |
| Subject | DEC-F4 / BR-CM-CAT-001 BR-007 & BR-008 (Draft v1.1) |
| Version | 1.0 |
| Date | 2026-07-29 |
| Owner | Solution Architect |
| Reviewer | BA Lead / QA Lead / PMO |
| Approver | Architecture Board (pending) |
| Status | 🟡 Draft — manual analysis (EOS auto-impact collides Sprint `BR-007` namespace) |
| Related | `GOV-DEC-F4`, BR-CM-CAT-001 v1.1 |

> **Note:** `python tools/eos.py impact --id BR-007` resolves the **Sprint delivery** BR-007 (auth/permission), not CM Escalation. Per **DEC-020** dual SoT (OQ-CM-B1-001 Closed), namespaces remain qualified — use **this document** for DEC-F4 impact.

---

## 1. Decision summary

DEC-F4 locks Cabang→Pusat escalation path, HQ return (reason code + note), F4-B work-queue visibility, and post-resolve `result_visibility` (`ORIGIN_BRANCH` \| `ALL_BRANCHES`) set at Resolve and changeable later with audit.

---

## 2. Impact chain

```text
DEC-F4
   │
   ├─ BR: BR-007 (Escalation), BR-008 (Resolution) — BR-CM-CAT-001 Draft v1.1
   ├─ FRD: FRD-CM-001 Batch 1 LOCKED — NO CHANGE
   │       Future FRD Batch (Escalation/Resolution) — MUST consume DEC-F4
   ├─ API: Planned (escalate, return, resolve+visibility, change visibility)
   ├─ Event: Planned (Escalated, Returned, Resolved, ResultVisibilityChanged)
   ├─ Data: Escalation History fields; Case.result_visibility (+ history)
   ├─ Security/AuthZ: org scope + result_visibility enforcement
   ├─ Test: UAT-F4-01…11 / TC-CM-F4-* (catalog below)
   ├─ ADR-014/015: No change (F4.1 is complaint-path policy)
   └─ INT-001: No direct change (customer lookup independent)
```

---

## 3. Artifact impact matrix

| Artifact | Impact | Action required |
|---|---|---|
| `GOV-DEC-F4` | Source decision | Countersign Architecture Board (`GOV-CS-DEC-F4`) |
| BR-CM-CAT-001 BR-007 / BR-008 | **Amended** (Draft v1.1) | Keep Draft; dual SoT per DEC-020 (no wholesale remapping) |
| FRD-CM-001 v1.1 LOCKED | None | Do not edit |
| FRD-CM-002 Draft | **Authored** | Board countersign → refine → LOCK path |
| OpenAPI `complaint-management-esc-res.v1.yaml` | **Planned** API-520…526 | Implement after FRD LOCK / sprint plan |
| Event Catalog EVT-CM-040…044 | **Planned** | Implement with producers |
| RTM-CM-F4-001 | Draft | Expand when FRD LOCKED |
| Test Strategy TC-CAT-CM-F4-001 | Planned UAT | Execute when APIs ready |
| Implementation / Batch 1 code | None now | Out of Batch 1 execution scope |
| Enterprise Org (Regional) | Clarification | Regional may exist in platform; **not** on CM escalate path |

---

## 4. Planned API capabilities (logical — IDs TBD at FRD)

| Capability | Notes |
|---|---|
| Escalate Case to Pusat | Target Pusat only under DEC-F4 |
| Return Escalation | Require `return_reason_code` + `return_note` |
| Resolve Case (Pusat) | Require/default `result_visibility` |
| Change `result_visibility` | Post-resolve; audit mandatory |
| Search/List/Get Case | Enforce origin branch vs `ALL_BRANCHES` |

---

## 5. Planned events (logical — IDs TBD)

| Event (logical) | Trigger |
|---|---|
| CaseEscalated | Successful escalate Cabang→Pusat |
| CaseEscalationReturned | Successful return with code+note |
| CaseResolved | Resolve (includes visibility if Pusat) |
| ResultVisibilityChanged | Post-resolve visibility change |

---

## 6. Security / authorization impact

| Rule | Enforcement point |
|---|---|
| F4-B handler queue | List/work APIs for Pusat handlers |
| Origin branch always reads after Resolve | Get/detail after Resolve |
| `ORIGIN_BRANCH` hides from other branches | Search, list, get, export |
| `ALL_BRANCHES` read-only for other branches | Same surfaces; deny write |
| Return only to originating branch | Return API validation |

---

## 7. Risk & collision

| Risk | Mitigation |
|---|---|
| ID collision Sprint `BR-007` vs CM Escalation `BR-007` | Use BR-CM-CAT-001 + DEC-F4 IDs in reviews; dual SoT per **DEC-020** (OQ-CM-B1-001 Closed) |
| Accidental edit to LOCKED FRD Batch 1 | Explicit non-impact in DEC-F4 §7 |
| Premature API without FRD | Keep API/Event **Planned** until Escalation FRD batch |
| Regional UI regressing into path | AC: no Regional target under DEC-F4 config |

---

## 8. Recommended next gates

1. Architecture Board countersign on `GOV-DEC-F4`
2. Close or schedule F4-OQ-01…04
3. Author FRD Escalation/Resolution batch (outline → Draft)
4. Catalog API/Event IDs when FRD Draft exists
5. Execute UAT-F4 when environment + APIs ready

---

## Related

- `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (v1.1)
- `13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md`
- `26 Traceability/IMPACT_ANALYSIS.generated.md` (EOS auto — Sprint namespace; not authoritative for DEC-F4)
