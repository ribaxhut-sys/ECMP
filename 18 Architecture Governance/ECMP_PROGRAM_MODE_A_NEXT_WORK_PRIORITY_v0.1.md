# PROGRAM — Mode A Next-Work Priority v0.1

| Field | Value |
|---|---|
| Document ID | GOV-MODEA-NEXT-001 |
| Program | PROGRAM-MODE-A-NEXT-001 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Prepared by | Documentation Administrator / Tech Lead (planning) |
| Status | 🟡 **Draft priority note** |
| Authorization | PROGRAM-ADR-002 **BR-008** AUTHORIZED WITH CONDITIONS; DEC-019/020 |
| Mode B / Batch-2 / enterprise customer | **CLOSED** — not in this queue |

---

## 1. Purpose

Rank **safe Mode A delivery** work so engineering continues under existing Implementation Authorization without drifting into Mode B / enterprise SSO / OpenAPI enterprise `securitySchemes`.

This note does **not** start a new sprint by itself; it prioritizes candidates for Tech Lead / PMO scheduling.

---

## 2. Priority within Mode A (recommended)

| Rank | Workstream | Why | Gate / note |
|---:|---|---|---|
| **M1** | Keep Mode A credential-route guards green (FE `check:auth-routes` + BE `ECMP_LOCAL_CREDENTIAL_AUTH`) | Audit K-3; prevents enterprise self-test regressions | CI must stay red if routes leak under enterprise posture |
| **M2** | Complaint dual-SoT hygiene (DEC-020) — docs/tests/ownership clarity; no forced merge | Prevents stack collision | Cutover only via future Retirement DEC |
| **M3** | FRD-CM / Batch-1 Aggregate intake UI (FR-001…004 screens) | Product delivery | Stay inside OpenAPI catalog; no Batch-2 unlock; **CLOSED for this intake slice** — see §6 / §7 |
| **M4** | Sprint-02 style assign/status/notification **only if** PMO activates Sprint-02 and events exist in catalog | Lifecycle value | **DEFERRED** — do not invent events outside `08 Event Catalog` |
| **M5** | FE quality (FE-CI-POL): lint/coverage/a11y already gated — extend tests incrementally | Hardening | No OD-FE-002 / Mode B UI bridge |
| **M6** | Ops hygiene supporting Complaint Module (staging TTL, storage probe, JSON logs) | Stability / FR-004 evidence durability | Shared-env re-drill C-K4-4 when ops capacity; **TD-OPS-002 password drift remains deferred** |

---

## 3. Explicitly out of Mode A queue

| Item | Why out |
|---|---|
| Identity Adapter / OIDC Mode B coding | C-B6-1 |
| Org schema Phase B without delivery authorization | Org-gap plan Phase B gate |
| OD-FE-002 browser bridge implementation | Gated |
| Batch-2 / EPIC unlock beyond governed drafts | C-7 / C-B6-1 |
| Supersede ADR-013 via FE docs | BR-007 |
| Foundation gaps without proven Complaint blocker | Only if they block Module COMPLETE |

---

## 4. Coordination with enterprise track

Enterprise P1–P3 (org-gap plan, EP bilateral, O-06/O-07) run **in parallel** as documentation/governance. Mode A coding should not wait for EP countersign, and must not implement Mode B “early.”

---

## 5. Suggested immediate engineering focus (if capacity = 1 stream)

1. **Keep-green** M1 / M3b / M3d / M5 / M6 (regression only)  
2. **M3c** evidence pack remains SoT for lab COMPLETE claim language  
3. **M4** remain **deferred** until PMO / catalog unlock  
4. Do **not** start Mode B adapter spikes; do **not** reopen M3 intake without regression gap  

---

## 6. Execution status (Mode A delivery — do not reorder §2)

| Rank | Status 2026-07-31 | Notes |
|---:|---|---|
| **M1** | **HARDENED** | FE guards + unit; BE gate endpoint/wiring; user create + update-password gated |
| **M2** | **HYGIENE DONE** | DEC-020 mount coexistence historically; **DEC-026 M-026-2** Foundation HTTP unmounted — tes coexistence diganti “unmounted” |
| **M3** | **CLOSED (intake slice)** | Aggregate intake lengkap; Foundation UI **retired** via DEC-026 (bukan silent cutover) |
| **M3 residual AC** | **HARDENED** | **TD-CM-001 / EX-D closed** — confirm lock enforced on API-500 create; FR-004 AC3 lab malware-reject proof added |
| **M3b supervisor visibility** | **HARDENED (Mode A)** | API-513 round-trip + edge cases (empty/limit/threshold/unknown reason); FE contract helpers; read-only; no Case create |
| **M3c lab COMPLETE evidence** | **DONE** | `ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md` (GOV-MODEA-M3C-001) — lab/synthetic claim only |
| **M3d EX-G complaintId** | **DONE (Mode A)** | API-513 `complaintId` nullable; bind-failure enqueue anchors Aggregate; FE link to `/complaints/cm/[id]` |
| **M4** | **DEFERRED** | Unchanged — PMO / catalog gates |
| **M5** | **HARDENED (helpers + FR-004 UI smoke)** | Coverage include `cmBatch1Attachments.ts`; staging/bound attachment component tests |
| **M6** | **HYGIENE SLICE DONE (cron deferred)** | Ops P0 + staging TTL script/runbook; **shared cron not started** (deployment / cross-env / Arch-DevOps only) |
| **Ops P0** | **DONE (Mode A)** | Attachment named volume; complaint BC AuthN floor (unmounted); JSON logging (`LOG_FORMAT`) |
| **IAM harden** | **DONE (Mode A)** | `RoleMapper` drops privileged IdP codes; not Entitlement Gate |
| **REC-01 pack** | **DRAFT** | BOARD-007 disposition brief — Board vote pending |

Mode B / Batch-2 / enterprise customer remain **CLOSED** (C-B6-1).

---

## 7. M3 close-out backlog (administrative)

| Item | Disposition |
|---|---|
| SCR-CM-001…006 Aggregate intake UI + FR-004 staging/void/confirm list | **Done** (Mode A) |
| Dual-SoT foundation list/detail coexistence | **Retired (runtime)** — DEC-026 M-026-1…3; CA BC ticket-nested tetap |
| Silent foundation → Aggregate cutover | **Out of this queue** — cutover = DEC-026 (executed); bukan silent |
| Confirm lock on create (TD-CM-001 / EX-D) | **Done** — enforced on new API-500 creates |
| Event catalog EVT-CM-030…034 production wiring beyond lab side-effects | **Not blocking**; track under observability/catalog when scheduled |
| Shared cron for staging TTL | **Deferred** — deployment / cross-env need / Arch-DevOps standard only |
| M3 reopen | Only for **regression**, security, architecture defect, new BR, or Board Decision |

---

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Initial Mode A priority note |
| 0.1a | 2026-07-31 | Execution status §6 after BOARD-006 Mode A delivery pass (priority table unchanged) |
| 0.1b | 2026-07-31 | M1 user password gate; M3 FE `cmBatch1` Aggregate client (no UI cutover) |
| 0.1c | 2026-07-31 | M5 dual-SoT FE helpers + coverage/test incremental |
| 0.1d | 2026-07-31 | Mode A ops P0: attachment volume, BC AuthN floor, JSON logging |
| 0.1e | 2026-07-31 | RoleMapper privileged drop; BOARD-007 REC-01 disposition brief Draft |
| 0.1f | 2026-07-31 | M3 Create UI → Aggregate API-500 + SCR-CM-005 confirmation route (DEC-020 coexistence) |
| 0.1g | 2026-07-31 | M3 SCR-CM-002/003/006 — customer search/confirm/360 + duplicate warning panel |
| 0.1h | 2026-07-31 | M3 SCR-CM-004 — StagingAttachmentsPanel + API-507 client; stagingToken on API-500 create and API-506 link_existing (D-06) |
| 0.1i | 2026-07-31 | M3 void + confirmation bound attachments (API-512/509); M5 coverage helper + component smoke |
| 0.1j | 2026-07-31 | **M3 CLOSED (admin)**; M4 explicit DEFERRED; M6 staging TTL ops hygiene + focus §5 retarget |
| 0.1k | 2026-07-31 | Verification pass: TD-CM-001 confirm-lock enforced; FR-004 AC3 lab reject test; shared cron stays deferred |
| 0.1l | 2026-07-31 | **M3b** later-review / no-Case aging visibility — API-513 + FE supervisor queue (read-only) |
| 0.1m | 2026-07-31 | **M3b HARDENED** — API-513 E2E round-trip, empty/limit/threshold/unknown-reason; FE contract helpers |
| 0.1n | 2026-07-31 | **M3c DONE** — Mode A Module Lab COMPLETE Evidence Pack (GOV-MODEA-M3C-001); focus §5 retarget |
| 0.1o | 2026-07-31 | **M3d DONE** — API-513 `complaintId` on later-review (EX-G); Alembic 0045; FE deep-link |
| 0.1p | 2026-07-31 | **Keep-green PASS** — Batch-1 BE 85; FE Aggregate 37; M1 auth-routes + unit; M6 ops script `--help` |
| 0.1q | 2026-08-01 | **CAP-008 Program CLOSED** — ARB pack GOV-CAP008-CLOSE-*; Roadmap Reset `ai/sprint/CAP008_ROADMAP_RESET_v1.0.md`. Batch-2 Mode A Case delivery no longer future work. Mode B remains CLOSED. |
| 0.1r | 2026-08-21 | Hygiene: M2/M3/§7 aligned to **DEC-026 executed**; remaining Mode A = BO/Board (Tutup Pengaduan, OQ-IAM-001, F4) — bukan Dual-SoT |

---

## 8. CAP-008 disposition (post Program Closure)

| Item | Disposition |
|---|---|
| CAP-008 Mode A Create/Add/View/Status/Resolve/Close | **PROGRAM CLOSED** — do not reopen under this queue |
| Roadmap | `../../ai/sprint/CAP008_ROADMAP_RESET_v1.0.md` |
| Closure index | `ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md` |

Mode B / enterprise customer remain **CLOSED** (C-B6-1).

---

## 9. Remaining Mode A after DEC-025/026/027 (2026-08-21)

Bukan antrian fitur baru. Coding Mode A hanya bila regresi, atau setelah keputusan di kolom Pemilik.

| Item | Status | Pemilik |
|---|---|---|
| Tutup Pengaduan / induk tetap buka jika semua Case `CANCELLED` | OOS DEC-025 §3.4 | Business Owner (DEC follow-up) |
| OQ-IAM-001 sisa 19 gerbang baca `complaints:read`/`update` | Open | Architecture Board / BO |
| DEC-F4 / FRD-CM-002 coding | Draft; **NOT APPROVED FOR CODE** | Architecture Board countersign |
| HQ schedule overdue visual hint | Mode A FE — slice ini | Tech Lead (keep-green) |
| Mode B / SSO / Identity Adapter | **CLOSED** (C-B6-1) | Board Unlock Resolution |
| CAP-006 FR-030 engine | Stay Deferred (CAP006-BLK-001) | Time Source pattern |

---

*End of GOV-MODEA-NEXT-001.*
