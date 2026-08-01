# PROGRAM-ENTERPRISE-PROFILES-001 — Subordinate Profiles Draft Pack

| Field | Value |
|---|---|
| Document ID | GOV-ENT-PROFILES-001 |
| Program | PROGRAM-ENTERPRISE-PROFILES-001 |
| Version | 0.1 |
| Date | 2026-07-30 |
| Prepared by | Architecture Board Secretary / Documentation Administrator |
| Authority | Project Owner instruction — draft subordinate profiles (binding / entitlement / org-sync); no Mode B coding |
| Status | 🟡 **Draft pack published** |
| Parent Resolutions | PROGRAM-BOARD-006 (BR-011/012/013; C-B6-1…C-B6-7); ADR-016 §9.3 subordination |

---

## 1. Purpose

Publish the first coordinated **Draft** pack of Mode B subordinate profiles required after Accept of ADR-016/017/018 — without unlocking Mode B or authorizing Identity Adapter / OpenAPI / schema coding.

---

## 2. Artifacts

| Profile | Path | Parent ADR | Deferred IDs addressed |
|---|---|---|---|
| Binding (OIDC) | `10 Security and Access Standards/ECMP_BINDING_PROFILE_OIDC_ECMP_v0.1.md` | ADR-016 | D-02 (provisional) |
| Entitlement representation | `10 Security and Access Standards/ECMP_ENTITLEMENT_REPRESENTATION_PROFILE_v0.1.md` | ADR-017 | E-01 / D-04 (working draft) |
| Org sync integration | `10 Security and Access Standards/ECMP_ORG_SYNC_INTEGRATION_PROFILE_v0.1.md` | ADR-018 | O-01…O-05, O-08 (architecture) |

Sequencing for **future** Mode B coding gates remains **016 → 017 → 018** (C-B6-5). Draft authoring may proceed in parallel.

---

## 3. Shared constraints

| Constraint | Source |
|---|---|
| Fail-closed; no profile-granted degraded allow | ADR-016 §9.3 / C-B6-2 |
| Mode B / Batch-2 / enterprise customer CLOSED | C-B6-1 / C-7 |
| Org-gap prerequisite unmet until evidence bar in org-sync profile §8 | C-B6-3 / K-7 |
| ADR-015 claim SoT preserved | BR-010 / C-3 Bilateral |
| Wire names provisional until Enterprise Platform bilateral confirm | All three profiles |

---

## 4. Explicit Non-Authority

This pack does **not**:

1. Accept profiles as BASELINE (status remains **Draft**)
2. Unlock Mode B or authorize coding
3. Edit OpenAPI enterprise `securitySchemes`
4. Authorize org schema migration
5. Close O-06 / O-07 / D-01 / D-08 / E-06 / E-07

---

## 5. Recommended next steps

1. Enterprise Platform bilateral review — **pack issued**: `ECMP_PROGRAM_EP_BILATERAL_PROFILE_REVIEW_PACK_v0.1.md` (awaiting EP countersign)
2. Org-gap delivery plan — **Draft published**: `ECMP_PROGRAM_ORG_GAP_DELIVERY_PLAN_v0.1.md` (Phase A done; B+ needs delivery authorization)
3. O-06 / O-07 — **DEC-021 / DEC-022 Proposed** (interim fail-closed rules)
4. Mode A delivery — see `ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md`
5. Mode B unlock **only** after org-gap evidence + explicit Board Resolution

---

## 6. Related

- `ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`
- `ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`
- `ECMP_PROGRAM_AUDIT_K5_FailClosed_Subordination_v1.0.md`

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-30 | Initial Draft pack — three subordinate profiles; Mode B CLOSED |

---

*End of GOV-ENT-PROFILES-001.*
