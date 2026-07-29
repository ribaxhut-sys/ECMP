# Architecture Board Countersign Pack — DEC-F4

| Field | Value |
|---|---|
| Document ID | GOV-CS-DEC-F4 |
| Subject | DEC-F4 Escalation Visibility, Return & Result Audience |
| Version | 1.0 |
| Date | 2026-07-29 |
| Prepared by | Solution Architect / Domain PO ECMF |
| Audience | Architecture Board / Business Owner |
| Status | 🟡 Ready for countersign |
| Decision pack | `ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md` |
| Impact | `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md` |

---

## One-page decision

**Ask:** Countersign DEC-F4 so Draft FRD Escalation/Resolution, Planned OpenAPI, and Planned Events may proceed under governance.

### Locked decisions (F4…F4.5 + OQ closures)

| ID | Decision |
|---|---|
| F4 | Pusat **handlers** work only escalated cases; analysts may KPI-monitor (model B) |
| F4.1 | Escalation path **Cabang → Pusat** only (**no Regional**) |
| F4.2 | After Pusat resolve, **originating branch always** may read the result |
| F4.3 | Pusat sets audience: `ORIGIN_BRANCH` \| `ALL_BRANCHES` |
| F4.3a | Visibility set at Resolve; **may change later** + audit |
| F4.4 | Pusat may **return** incomplete escalations to originating branch |
| F4.5 | Return = **reason code + free-text note** (both mandatory) |
| **F4-OQ-01** | `return_note` minimum length = **10** characters (Unicode; trim before count) |
| **F4-OQ-02** | While Case owned by Pusat, originating branch is **read-only** (no operational write). After Return, originating branch regains write. Exception: none in v1 (comments/attachments to fulfill return happen **after** Return ownership is restored) |

### Default

`result_visibility` default at Resolve = **`ORIGIN_BRANCH`**.

### Explicit non-impacts

- FRD-CM-001 Batch 1 **LOCKED** — unchanged  
- ADR-014 / ADR-015 — unchanged (Regional may exist in Enterprise Org; not on CM escalate path)  
- Customer Master remains read-only (INT-001)

---

## Artifact set for Board

| Artifact | Role |
|---|---|
| GOV-DEC-F4 | Decision SoT |
| GOV-IMPACT-DEC-F4 | Impact (authoritative; ignore EOS Sprint BR-007 collision) |
| BR-CM-CAT-001 v1.1 | BR-007 / BR-008 amended (Draft) |
| FRD-CM-002 Draft | Escalation & Resolution FRD |
| OpenAPI `complaint-management-esc-res.v1.yaml` | Planned API-520…526 |
| Events EVT-CM-040…044 | Planned |
| TC-CAT-CM-F4-001 | UAT-F4-01…11 |

---

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Business Owner | | | ☐ Approve / ☐ Reject / ☐ Approve with conditions |
| Domain PO ECMF | | | ☐ |
| Solution Architect | | | ☐ |
| Security Architect | | | ☐ |
| Architecture Board Chair | | | ☐ |

**Conditions (if any):** _________________________________

---

## Related paths

- `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md`
- `07 API Catalog/openapi/complaint-management-esc-res.v1.yaml`
- `08 Event Catalog/events/events.yaml` (EVT-CM-040…)
- `13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md`
