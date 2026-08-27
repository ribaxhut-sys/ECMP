# ECMP — Mode A Module Lab COMPLETE Evidence Pack (M3c)

| Field | Value |
|---|---|
| Document ID | GOV-MODEA-M3C-001 |
| Program | PROGRAM-MODE-A-NEXT-001 / EPIC-CM-B1 |
| Version | 1.0 |
| Date | 2026-07-31 |
| Prepared by | Tech Lead / Engineering Assistant (Mode A delivery) |
| Status | 🟢 **Evidence recorded** — Mode A Batch-1 **lab COMPLETE** (synthetic / stub) |
| Authorization | PROGRAM-ADR-002 **BR-008** AUTHORIZED WITH CONDITIONS; DEC-019/020 |
| Companion | `ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md`; EX pack `GOV-EX-CM-B1-S3-001`; EX-C re-review `GOV-EX-CM-B1-EXC-RR-001` (pending countersign) |
| Mode B / Batch-2 / real-customer prod | **NOT claimed** — remain CLOSED / excepted |

---

## 1. Purpose

Record **objective evidence** that the ECMP Complaint Management Module (Batch 1 Aggregate) is **COMPLETE for Mode A lab delivery** under existing Implementation Authorization:

- FRD-CM-001 v1.1 LOCKED — FR-001…FR-004 intake capability
- Supervisor later-review / no-Case aging **visibility** (API-513)
- Dual SoT coexistence (DEC-020) without foundation cutover
- Supporting Mode A tracks M1 / M2 / M5 / M6 keep-green

This pack **does not**:

- Unlock Mode B (C-7 / C-B6-1)
- Approve Batch-2 Case create or M4 assign/status/notification
- Exit EX-A / EX-B / EX-C for real-customer production
- Invent APIs outside OpenAPI catalog
- Retire `/api/v1/complaints` (needs Retirement DEC)

---

## 2. Claim (precise)

| Claim | Scope |
|---|---|
| **Mode A Batch-1 Module lab COMPLETE** | Synthetic / stub Master Customer; single-instance lab; AV stub; outbox persist-only |
| Environment class | Non-prod / local Docker / CI lab — **not** unrestricted Production Ready for real customers |
| Product surface | Aggregate `/api/v1/cm` (API-500…513) + Mode A FE intake + supervisor queue + FR-004 shared attachment CAP alignments |

**Board / PMO language:** *lab COMPLETE* ≡ features + tests + catalog + Mode A UI for FR-001…004 + supervisor visibility delivered under BR-008. It is **not** an Accept of Mode B or real-customer prod cutover.

---

## 3. Delivery map (Mode A tracks)

| Track | Status | Evidence anchor |
|---|---|---|
| **M1** credential-route guards | HARDENED | FE `check:auth-routes*`; BE `ECMP_LOCAL_CREDENTIAL_AUTH` / enterprise fail-fast |
| **M2** DEC-020 dual-SoT hygiene | DONE | Mount coexistence tests; OWNERSHIP / catalog / RTM sync |
| **M3** Aggregate intake UI | CLOSED | SCR-CM-001…006 + FR-004 staging/void/confirm attachments |
| **M3 residual AC** | HARDENED | TD-CM-001 / EX-D closed (confirm lock); FR-004 AC3 lab malware-reject |
| **M3b** supervisor visibility | HARDENED | API-513 + FE `/complaints/cm/supervisor` + round-trip/edge tests |
| **M3c** this pack | DONE | GOV-MODEA-M3C-001 |
| **M4** assign/status/notification | DEFERRED | Catalog / PMO gate |
| **M5** FE quality incremental | HARDENED | Vitest coverage helpers + component smoke |
| **M6** ops hygiene | HYGIENE DONE | Staging TTL script/runbook; shared cron deferred |
| **Mode B** | BLOCKED | C-B6-1 |

---

## 4. Capability ↔ contract evidence

### 4.1 OpenAPI / logical APIs

Catalog: `07 API Catalog/openapi/complaint-management-batch1.v1.yaml`  
Inventory: `07 API Catalog/README.md` (API-500…513)

| Catalog | Logical | Capability | Mode A FE / notes |
|---|---|---|---|
| API-500 | API-CM-B1-001 | Create Complaint (no Case) | `/complaints/new` → Aggregate |
| API-501 | API-CM-B1-002 | Get Complaint | `/complaints/cm/[id]` |
| API-502…504 | API-CM-B1-003…005 | Customer search / confirm / 360 | SCR-CM-002/006 |
| API-505…506 | API-CM-B1-006…007 | Duplicate check / decision | SCR-CM-003 |
| API-507…512 | API-CM-B1-008…013 | Attachments (shared CAP + transfer/void) | SCR-CM-004 + confirmation card |
| API-513 | API-CM-B1-014 | Supervisor later-review + no-Case aging | `/complaints/cm/supervisor` |

RTM: `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0.md` (includes API-CM-B1-014).

### 4.2 Screens (FRD SCR)

| SCR | Disposition |
|---|---|
| SCR-CM-001 Create | Done (Mode A Aggregate) |
| SCR-CM-002 Customer search | Done |
| SCR-CM-003 Duplicate panel | Done |
| SCR-CM-004 Attachment staging | Done |
| SCR-CM-005 Confirmation | Done (`/complaints/cm/[id]`) |
| SCR-CM-006 Customer 360 min | Done |
| Supervisor queue (FR-001 A4 / FR-003 E1 / FR-004 E8 visibility) | Done (API-513; not Case create) |

### 4.3 Persistence / ops

| Item | Evidence |
|---|---|
| Durable Aggregate tables | Alembic `0040`…`0043` (`cm_batch1_*`) |
| Staging TTL ops | `backend/scripts/cm_batch1_ops_hygiene.py`; runbook `15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md` |
| Shared cron | **Deferred** (deployment / Arch-DevOps only) |

---

## 5. Automated test evidence (captured 2026-07-31)

Commands (lab workstation):

```text
# Backend Batch-1 related
python -m pytest tests/test_cm_batch1.py tests/test_cm_batch1_attachments.py \
  tests/test_cm_batch1_foundation.py tests/test_cm_batch1_customer_provider.py -q
# → 83 passed

# Frontend Aggregate helpers / UI smoke (subset)
npx vitest run src/features/complaints/cmBatch1*.test.ts \
  src/features/complaints/StagingAttachmentsPanel.test.tsx \
  src/features/complaints/CmBatch1BoundAttachmentsCard.test.tsx \
  src/features/complaints/CmBatch1SupervisorQueueView.test.tsx \
  src/features/complaints/createComplaintForm.test.ts \
  src/lib/api/cmBatch1.test.ts
# → 33 passed (7 files)
```

Notable AC / harden tests:

| ID / theme | Location |
|---|---|
| Confirm lock (TD-CM-001 / EX-D) | `backend/tests/test_cm_batch1*.py` + `cm_batch1_helpers.confirmed_create` |
| Degraded duplicate → later-review | `test_tc_cm_fr003_06_degraded_later_review` |
| API-513 E2E + edge cases | `test_api_513_*` in `test_cm_batch1.py` |
| FR-004 AC3 malware reject (lab) | `test_tc_cm_fr004_03_malware_reject` |
| DEC-020 path helpers | `frontend/src/lib/api/cmBatch1.test.ts` |

---

## 6. Exception / residual posture (lab)

Source of truth: `18 Architecture Governance/reviews/ECMP_CM_Batch1_S3_Release_Exception_Pack_v1.0.md` (EX-20260729-01).

| EX# | Lab posture after Mode A M3…M3b |
|---|---|
| EX-A / EX-B | **Still in force** — stub / enterprise UNAVAILABLE; not real-customer prod |
| EX-C | **Still in force** — AV `STUB_ONLY`; calendar re-review GOV-EX-CM-B1-EXC-RR-001 (2026-08-26) pending countersign |
| EX-D | **Closed (Mode A lab)** — confirm lock enforced |
| EX-E | Accepted for single-instance lab |
| EX-F | Accepted — outbox persist-only |
| EX-G | Visibility delivered (API-513); split-TX design residual remains — harden only if approved (optional M3d) |
| EX-H | Accepted — create Idempotency-Key for retries |
| TD-OPS-002 | Deferred password drift |
| Shared cron staging TTL | Deferred |

---

## 7. Explicit non-claims (anti-skip)

| Non-claim | Correct next gate |
|---|---|
| Mode B SSO / Identity Adapter / enterprise `securitySchemes` | Board unlock C-B6-1 + org-gap C-B6-3 |
| Batch-2 Case create | Batch-2 / FRD unlock |
| M4 assign / status / notification | PMO + Event Catalog |
| Foundation UI cutover / merge SoTs | Retirement DEC |
| Real-customer Production Ready | Exit EX-A/B/C + ops readiness |
| “Accept ADR-016/017/018 = Mode B unlocked” | False — architecture ≠ coding unlock |

---

## 8. Recommended next work (after M3c)

| Priority | Item | Note |
|---:|---|---|
| Keep-green | M1 / M5 / M6 / M3b tests | Regression only |
| Optional product | **M3d** EX-G `complaintId` on later-review | **Done (2026-07-31)** — catalog + Alembic 0045 + BE/FE |
| Deferred | **M4** | Do not invent events |
| Parallel governance | Org-gap / EP bilateral / BOARD-007 | Docs only until unlock |
| Blocked | Mode B coding | C-B6-1 |

---

## 9. Sign-off record

| Role | Action | Date / note |
|---|---|---|
| Engineering (this pack) | Evidence compiled; lab COMPLETE claim as defined in §2 | 2026-07-31 |
| Tech Lead / PMO | Optional countersign of claim language | Pending if required by release process |
| Architecture Board | **Not required** for Mode A lab COMPLETE under BR-008; **required** before Mode B / real-customer prod claims | — |

---

## 10. Revision

| Rev | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-31 | Initial M3c Mode A Module Lab COMPLETE Evidence Pack |

---

*End of GOV-MODEA-M3C-001.*
