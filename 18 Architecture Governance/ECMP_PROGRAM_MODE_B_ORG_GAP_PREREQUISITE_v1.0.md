# PROGRAM — Mode B Organization-Model Gap Prerequisite (Audit K-7)

| Field | Value |
|---|---|
| Document ID | GOV-MODEB-ORG-001 |
| Program | PROGRAM-MODE-B-ORG-GAP-001 |
| Version | 1.0 |
| Date | 2026-07-30 |
| Prepared by | ECMP Documentation Administrator / Solution Architect |
| Audience | Architecture Board / Security Architect / PMO / Tech Lead |
| Status | 🟢 **Recorded — Binding Mode B prerequisite** |
| Related audit | Independent Program Audit 2026-07-30 — **K-7** / BLK-05 |
| Non-goals | Does **not** unlock Mode B; does **not** Accept ADR-016/017/018; does **not** authorize schema migration |

---

## 1. Purpose

Record, in one verifiable place, that closing the **three-level organization model gap** is a **Mode B prerequisite**, elevating prior “post-Accept delivery concern” language so Mode B cannot be unlocked while AuthZ org references remain systematically unresolvable.

---

## 2. Gap statement (evidence)

| Item | Evidence |
|---|---|
| Required under Mode B | ADR-015 v1.0 contract: `organization_id`, `branch_id`, `department_id` — exactly one each |
| Current foundation | Local `branches` model; **no** first-class `organizations` / `departments` masters in Alembic corpus (audit BLK-05) |
| AuthZ consequence | ADR-018 §14: unresolvable Organization References → **deny** scope-dependent AuthZ |
| Prior wording | ADR-014 v1.4 called this a post-Accept delivery concern |

---

## 3. Binding rule (K-7)

**Architecture Board and implementers SHALL treat the following as a Mode B unlock prerequisite:**

1. ECMP must provide **resolvable** organizational context for the ADR-015 three-level reference set (organization / branch / department) consistent with ADR-018 (local non-authoritative projection and/or masters as designed under accepted sync architecture).
2. Until that prerequisite is met (or Architecture Board records an **explicit waiver Resolution** citing this document and ADR-014/018), PROGRAM-BOARD-004 **C-7** Mode B / Batch-2 / enterprise customer remain **CLOSED** for unlock purposes.
3. Accept of ADR-018 (PROGRAM-BOARD-006 **BR-013**) does **not** by itself waive this prerequisite — reaffirmed as Resolution condition **C-B6-3**.
4. Schema / projection delivery remains a future implementation program — gated by `ECMP_PROGRAM_ORG_GAP_DELIVERY_PLAN_v0.1.md` (Draft). This prerequisite record **gates unlock**; the plan does **not** authorize Mode B or schema by itself.

---

## 4. Cross-references updated

| Artifact | Change |
|---|---|
| ADR-014 v1.4 § Organizational model gap | Elevated to Mode B prerequisite (rev 1.4a) |
| ADR-018 §8 / §15 / O-03 | Mode B prerequisite language (rev 1.0a) |
| PROGRAM-BOARD-004 C-7 | Unchanged CLOSED; this record clarifies an unlock prerequisite |
| PROGRAM-BOARD-005 Review | Lists this prerequisite as Board input (RC-3 advisory for BOARD-006) |
| PROGRAM-BOARD-006 C-B6-3 | Prerequisite adopted as Resolution condition |
| Org-gap delivery plan | `ECMP_PROGRAM_ORG_GAP_DELIVERY_PLAN_v0.1.md` (Draft phases A–D) |

---

## 5. Explicit Non-Authority

- No Mode B AuthN / Identity Adapter implementation authorized
- No OpenAPI enterprise `securitySchemes`
- No invented Board Accept of ADR-016/017/018
- No waiver of fail-closed AuthZ (see audit K-5 / ADR-018 §14)

| Rev | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | Audit K-7 — Mode B org-gap prerequisite recorded |
| 1.0a | 2026-07-31 | Cross-ref org-gap delivery plan Draft; BOARD-006 C-B6-3; no Mode B unlock |
