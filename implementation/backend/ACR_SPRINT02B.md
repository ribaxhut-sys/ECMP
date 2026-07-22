# Architecture Change Request (ACR) — blocked items outside Sprint-02B implementation rules
#
# Generated because implementation would require changing a frozen contract / draft catalog.
# Do NOT implement these until the ACR is accepted and contracts are re-frozen.

---

## ACR-001 — Consolidate case-actions into case-service (DEC-006 U-6)

| Field | Value |
|---|---|
| ID | ACR-001 |
| Date | 2026-07-22 |
| Raised by | Lead Backend Engineer (Sprint-02B) |
| Status | **Closed — resolved in Sprint-03A (governance sync, 2026-07-22)** |

### Resolution (Sprint-03A)
Merged into `case-service.v1.yaml` v1.4.0 exactly per the "Proposed change" below.
`case-actions.v1.yaml` rewritten to an empty, `x-status: superseded` stub (kept on
disk, not deleted, per repo file-retention constraint). `test_contract_conformance.py`
now reads only `case-service.v1.yaml`. No API behavior or event payload changed —
verified by full pytest run (62/62 passing, same assertions as before the merge).

### Problem
DEC-006 U-6 planned merge of `case-actions.v1.yaml` → `case-service.v1.yaml` v1.4.0 when
endpoints land, plus expanding `CaseStatus` / `Case.assigneeId`/`unitId` in case-service.
Sprint-02B implementation rules forbid modifying OpenAPI specs.

### Impact if deferred
- Two normative OpenAPI files must both be read by conformance (`test_contract_conformance.py`).
- `case-service.v1.yaml` CaseStatus remains `[REGISTERED]` while runtime exposes full enum
  (truthful vs lifecycle frozen spec `case-actions.v1.yaml`).

### Proposed change (requires Architecture / contract freeze decision)
1. Merge API-003/API-004 into `case-service.v1.yaml` v1.4.0.
2. Align Case / CaseStatus with case-actions.
3. Retire or mark `case-actions.v1.yaml` as superseded.
4. Keep conformance on a single catalog file.

### Workaround in Sprint-02B
Conformance suite unions both catalogs; runtime Case schema follows `case-actions.v1.yaml`.
No OpenAPI files modified.

---

## ACR-002 — Customer 360 read (FR-010 / S2-4) blocked on draft contract

| Field | Value |
|---|---|
| ID | ACR-002 |
| Date | 2026-07-22 |
| Raised by | Lead Backend Engineer (Sprint-02B) |
| Status | **Closed — deferred by CTO decision (Sprint-03B design review, 2026-07-22)** |

### Resolution (Sprint-03B design review)
Confirmed still blocked, and for a sharper reason than originally logged: `customer-read.v1.draft.yaml`
and FRD-003 AC both assume the stub returns a real profile (`fullName`, `contactChannels`), but
INT-001's stub principle explicitly forbids fabricating customer data ("stub tidak boleh
mengembalikan nama/kontak/atribut pelanggan fiktif"). CTO decision: **defer API-010 entirely**
until INT-001A sandbox access exists to answer this honestly — do not implement a stub that
would fabricate profile data. Sprint-03B ships API-005 (list cases) only. Revisit when
INT-001A access is available or a redefined stub contract (e.g. existence/verification-only,
no profile fields) is explicitly approved.

### Problem
`07 API Catalog/openapi/drafts/customer-read.v1.draft.yaml` is still a **draft**.
Implementing `GET /v1/customers/{customerId}` requires promoting the draft to a normative
spec (modifies OpenAPI catalog). Implementation rules forbid creating APIs outside the
normative catalog and forbid modifying OpenAPI.

### Proposed change
1. Freeze/promote `customer-read.v1.yaml` (G1-style decision).
2. Then implement INT-001 stub client + masking + TC-010 in a follow-up slice.

### Workaround in Sprint-02B
FR-010 / S2-4 **not implemented**. Sprint-02.md governing in-scope list (assign/status/events/
notification stub) is delivered without Customer 360.

---

## ACR-003 — Event catalog status Planned → Implemented (optional doc sync)

| Field | Value |
|---|---|
| ID | ACR-003 |
| Date | 2026-07-22 |
| Status | **Closed — resolved in Sprint-03A (governance sync, 2026-07-22)** |

### Resolution (Sprint-03A)
`08 Event Catalog/events/events.yaml`: EVT-002, EVT-003, EVT-005 status flipped
Planned → Implemented (version 0.4 → 0.5). Metadata-only change — payloads unchanged,
still frozen per DEC-006. EVT-004/EVT-006/EVT-007/EVT-008 left as Planned/Proposed
(genuinely not yet implemented). `EVENT_CATALOG.generated.md` regenerated.
