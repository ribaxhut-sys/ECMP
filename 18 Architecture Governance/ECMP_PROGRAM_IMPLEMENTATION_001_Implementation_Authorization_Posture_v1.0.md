# PROGRAM-IMPLEMENTATION-001 — Implementation Authorization Posture

| Field | Value |
|---|---|
| Document ID | GOV-IMPL-001 |
| Program | PROGRAM-IMPLEMENTATION-001 |
| Version | 1.0 |
| Date | 2026-07-30 |
| Prepared by | ECMP Documentation Administrator |
| Audience | Tech Lead / Solution Architect / PMO / Architecture Board |
| Status | 🟢 **Recorded** |
| Scope | Capture implementation posture cited by DEC-020 / BMR — **does not** invent new Board Accept |

---

## 1. Purpose

Standalone record for **PROGRAM-IMPLEMENTATION-001**, referenced by DEC-020 as prior approved policy for controlled coexistence of complaint implementations, previously without a dedicated file (audit K-6 / BLK-07).

Board-level FE Implementation Authorization remains PROGRAM-ADR-002 **BR-008** (**AUTHORIZED WITH CONDITIONS**). This program record states the **engineering coexistence posture** for complaint stacks under Mode A delivery.

---

## 2. Binding posture (as cited by DEC-020)

| Rule | Meaning |
|---|---|
| No forced merge | Do not force-merge legacy `complaints`, `complaint_cases*`, and `cm_batch1` into one implementation without a Decision |
| Controlled coexistence | Dual/triple SoT may coexist under explicit ownership tables |
| Cutover only by Decision | Namespace retirement / router mount changes require a future Retirement DEC (or equivalent Board/Decision record) |
| Governance gates remain active | Mode B, Batch-2, real-customer production, and exception packs EX-A…H stay gated |

---

## 3. Relationship to Board resolutions

| Authority | Effect |
|---|---|
| PROGRAM-ADR-002 **BR-008** | FE Implementation Authorization: AUTHORIZED WITH CONDITIONS |
| PROGRAM-BOARD-004 **C-7** | Mode B / Batch-2 / enterprise customer **CLOSED** |
| DEC-020 | Closes OQ-CM-B1-001; dual SoT; does **not** Accept ADR-014/015 by itself (Accept is BOARD-004) |

---

## 4. What this program does **not** authorize

- Mode B AuthN / Identity Adapter implementation
- OpenAPI enterprise `securitySchemes`
- Batch-2 / EPIC-CM-F4 code unlock without Board
- Production cutover while REL-SEC-001 / P6-006 conditions (including shared-env recovery drill) remain open
- Silent retirement of `/api/v1/complaints` or mounting of unmounted complaint routers

---

## 5. Related

- `27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md`
- `18 Architecture Governance/BACKEND_MASTER_ROADMAP.md` (BMR-001)
- `ECMP_PROGRAM_ADR_002_Board_Resolutions_v1.0.md` (BR-008)
- `ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md` (C-7)

| Rev | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | Audit K-6 — implementation posture record |
