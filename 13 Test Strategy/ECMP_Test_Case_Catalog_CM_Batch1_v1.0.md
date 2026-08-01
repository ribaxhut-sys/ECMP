# ECMP Test Case Catalog — Complaint Management Batch 1

| Field | Value |
|---|---|
| ID | TC-CAT-CM-B1-001 |
| Version | 1.0.1 |
| Owner | QA Lead |
| Reviewer | BA / Solution Architect |
| Approver | Architecture Board / CTO |
| Status | 🟢 Execution sync (TASK-006-01) — mapping only; no new tests authored |
| Date | 2026-07-29 |
| Last sync | 2026-08-01 (TASK-006-01 @ tip `1608245`) |
| FRD | FRD-CM-001 v1.1 LOCKED |
| RTM | RTM-CM-B1-001 LOCKED |
| Namespace | TC-CM-* (not Sprint TC-001…) |

## Purpose

Formal Planned Test Cases for Batch 1 (FR-001…FR-004). Mapped 1:1 from RTM Acceptance Criteria. **Do not** create Case in any positive path (CTO D-02).

TASK-006-01 updates **traceability only**: link each TC-CM-* to an existing pytest/vitest symbol **or** mark Manual / Pending. Does **not** add tests or change runtime behavior.

## Summary

| FR | AC count | TC IDs | Automated executed | Pending / Manual | Status |
|---|---|---|---|---|---|
| FR-001 | 12 | TC-CM-FR001-01…12 | 9 | 3 Pending | 🟡 Partial |
| FR-002 | 9 | TC-CM-FR002-01…09 | 9 | 0 | 🟢 Mapped |
| FR-003 | 8 | TC-CM-FR003-01…08 | 8 | 0 | 🟢 Mapped |
| FR-004 | 9 | TC-CM-FR004-01…09 | 9 | 0 | 🟢 Mapped |
| **Total** | **38** | | **35** | **3 Pending** | **~92% automated executed** |

Supporting suites (not separate TC-CM-* IDs): API-513 supervisor visibility (`test_api_513_*`), ops hygiene (`test_cm_batch1_ops_hygiene.py`), confirm-lock harden (`test_tc_cm_fr001_confirm_lock_required_on_create` / TD-CM-001).

---

## FR-001 — Complaint Registration

| TC | Title | AC | API | EVT | Priority | Exec | Primary automated evidence |
|---|---|---|---|---|---|---|---|
| TC-CM-FR001-01 | Authorized create → REGISTERED, unique number, **no Case** | AC-CM-FR001-01 | API-500 | EVT-CM-001 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr001_01_create_registered_no_case` |
| TC-CM-FR001-02 | Stores CustomerId only (not Master SoR attributes) | AC-CM-FR001-02 | API-500 | EVT-CM-001 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr001_02_customer_id_only` |
| TC-CM-FR001-03 | Immutable audit + Timeline “Complaint Created” | AC-CM-FR001-03 | API-500 | EVT-CM-001 | Must | **Automated** | `backend/tests/test_cm_batch1_foundation.py::test_create_commits_audit_timeline_outbox` (+ `test_factory_create_maps_evt_cm_001`) |
| TC-CM-FR001-04 | Missing mandatory attributes → field validation reject | AC-CM-FR001-04 | API-500 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr001_04_missing_fields` |
| TC-CM-FR001-05 | Unauthorized → reject + security audit | AC-CM-FR001-05 | API-500 | — | Must | **Pending** | No dedicated automated deny/authz test under `test_cm_batch1*.py` (do not invent) |
| TC-CM-FR001-06 | Duplicate override with/without justification | AC-CM-FR001-06 | API-500 / API-506 | EVT-CM-021 | Must | **Automated** | `test_tc_cm_fr003_03_override_without_reason_rejected` + `test_tc_cm_fr003_04_override_with_justification` |
| TC-CM-FR001-07 | Redirect transfers staged evidence (no discard) | AC-CM-FR001-07 | API-500 / API-508 | EVT-CM-003, EVT-CM-033 | Must | **Automated** | `backend/tests/test_cm_batch1_attachments.py::test_tc_cm_fr004_08_transfer_d06_no_discard` (+ `test_bind_on_create_and_link_transfer_api`) |
| TC-CM-FR001-08 | Strict mode + Master Customer down → reject | AC-CM-FR001-08 | API-500 | — | Must | **Pending** | Search-path strict/unavailable exists (`test_tc_cm_fr002_05_*`); **no** API-500 create reject dedicated to this AC |
| TC-CM-FR001-09 | Notification down → Complaint remains; outbox records failure | AC-CM-FR001-09 | API-500 | EVT-CM-005 | Must | **Pending** | No automated EVT-CM-005 / notification-down path under Batch-1 suite |
| TC-CM-FR001-10 | Repeated Request Id → no new Aggregate | AC-CM-FR001-10 | API-500 | EVT-CM-002 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr001_10_request_id_replay` (+ foundation `test_idempotent_replay_emits_evt_cm_002_once`) |
| TC-CM-FR001-11 | Repeated Channel Message Id → no new Aggregate | AC-CM-FR001-11 | API-500 | EVT-CM-002 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr001_11_channel_message_replay` |
| TC-CM-FR001-12 | Confirm presents Batch 1 Customer 360 minimum | AC-CM-FR001-12 | API-504 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr001_12_360_after_create` |

**Shared asserts (all FR-001 positives):** `caseCreated == false` OR no Case resource created.

**Supporting (not a TC-CM-* row):** `test_tc_cm_fr001_confirm_lock_required_on_create` — TD-CM-001 / EX-D confirm lock on create.

---

## FR-002 — Customer Search

| TC | Title | AC | API | EVT | Priority | Exec | Primary automated evidence |
|---|---|---|---|---|---|---|---|
| TC-CM-FR002-01 | Unique Customer Number → lock CustomerId + 360 minimum | AC-CM-FR002-01 | API-502 / API-504 | EVT-CM-010 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_01_unique_customer_number` |
| TC-CM-FR002-02 | Multiple matches → no lock until selection | AC-CM-FR002-02 | API-502 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_02_ambiguous_no_lock` |
| TC-CM-FR002-03 | No match → normal create rejected (unless UNVERIFIED policy) | AC-CM-FR002-03 | API-502 / API-500 | EVT-CM-011 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_03_not_found` |
| TC-CM-FR002-04 | Master Customer write-back rejected | AC-CM-FR002-04 | — | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_04_write_back_rejected` |
| TC-CM-FR002-05 | Strict unavailable → degraded; no invented customer | AC-CM-FR002-05 | API-502 | EVT-CM-011 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_05_strict_unavailable` |
| TC-CM-FR002-06 | Frontend calls Backend only (integration/contract) | AC-CM-FR002-06 | API-502 | — | Must | **Automated** | `frontend/src/lib/api/cmBatch1.test.ts` — `cmBatch1Paths` anchors `customerSearch` / 360 under `/api/v1/cm` (FE contract; not browser E2E) |
| TC-CM-FR002-07 | Two key types in one request → reject | AC-CM-FR002-07 | API-502 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_07_two_keys_rejected` |
| TC-CM-FR002-08 | Enumeration threshold → delay/block + audit + alert | AC-CM-FR002-08 | API-502 | EVT-CM-011 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_08_enumeration_blocks` |
| TC-CM-FR002-09 | Profile `asOf` freshness shown | AC-CM-FR002-09 | API-504 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr002_09_as_of_present` |

---

## FR-003 — Duplicate Detection

| TC | Title | AC | API | EVT | Priority | Exec | Primary automated evidence |
|---|---|---|---|---|---|---|---|
| TC-CM-FR003-01 | Open candidate in window → warning | AC-CM-FR003-01 | API-505 | EVT-CM-020 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_01_warning_in_window` |
| TC-CM-FR003-02 | Open/link existing → no new Aggregate, **no Case** | AC-CM-FR003-02 | API-506 | EVT-CM-022 / 023 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_02_link_existing_no_case` |
| TC-CM-FR003-03 | Continue without required justification → reject | AC-CM-FR003-03 | API-506 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_03_override_without_reason_rejected` |
| TC-CM-FR003-04 | Override with justification → create + linkage + audit | AC-CM-FR003-04 | API-506 / API-500 | EVT-CM-021 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_04_override_with_justification` |
| TC-CM-FR003-05 | Hard-block category → reject create | AC-CM-FR003-05 | API-505 / API-500 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_05_hard_block_rejects_create` |
| TC-CM-FR003-06 | Index unavailable → degraded + later-review work item | AC-CM-FR003-06 | API-505 | EVT-CM-025 / 026 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_06_degraded_later_review` |
| TC-CM-FR003-07 | Out-of-scope candidates → uniform empty | AC-CM-FR003-07 | API-505 | — | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_07_out_of_scope_uniform_empty` |
| TC-CM-FR003-08 | Any Batch 1 duplicate flow → **no Case created** | AC-CM-FR003-08 | API-505 / API-506 | EVT-CM-024 | Must | **Automated** | `backend/tests/test_cm_batch1.py::test_tc_cm_fr003_08_no_case_from_duplicate_flow` |

---

## FR-004 — Attachment Upload

| TC | Title | AC | API | EVT | Priority | Exec | Primary automated evidence |
|---|---|---|---|---|---|---|---|
| TC-CM-FR004-01 | Allowlisted upload → ACTIVE + hash + history/audit | AC-CM-FR004-01 | API-507 | EVT-CM-030 | Must | **Automated** | `backend/tests/test_cm_batch1_attachments.py::test_tc_cm_fr004_01_upload_active_with_hash` |
| TC-CM-FR004-02 | Illegal type/size → reject; no ACTIVE | AC-CM-FR004-02 | API-507 | — | Must | **Automated** | `test_tc_cm_fr004_02_reject_illegal_type` + `test_tc_cm_fr004_02b_reject_oversize` |
| TC-CM-FR004-03 | Malware failure → reject + security audit | AC-CM-FR004-03 | API-507 | — | Must | **Automated** | `backend/tests/test_cm_batch1_attachments.py::test_tc_cm_fr004_03_malware_reject` |
| TC-CM-FR004-04 | Physical delete rejected; void-with-reason only | AC-CM-FR004-04 | API-512 | EVT-CM-032 | Must | **Automated** | `backend/tests/test_cm_batch1_attachments.py::test_tc_cm_fr004_04_void_with_reason` (+ FE void via `cmBatch1.upload.test.ts`) |
| TC-CM-FR004-05 | Supersede → prior SUPERSEDED and retrievable | AC-CM-FR004-05 | API-507 | EVT-CM-031 | Must | **Automated** | `backend/tests/test_cm_batch1_attachments.py::test_tc_cm_fr004_05_supersede` |
| TC-CM-FR004-06 | Later escalation visibility (No Information Lost) | AC-CM-FR004-06 | API-509 | — | Must | **Automated** | `test_repo_history_and_list` (list-by-complaint) + FE `cmBatch1.upload.test.ts` API-509 list + `CmBatch1BoundAttachmentsCard.test.tsx` |
| TC-CM-FR004-07 | Frontend uses Backend attachment APIs only | AC-CM-FR004-07 | API-507…512 | — | Must | **Automated** | `frontend/src/lib/api/cmBatch1.upload.test.ts` (multipart `/api/v1/attachments`, void API-512, list API-509) |
| TC-CM-FR004-08 | Duplicate redirect transfer → survivor + audit; no discard | AC-CM-FR004-08 | API-508 | EVT-CM-033 | Must | **Automated** | `backend/tests/test_cm_batch1_attachments.py::test_tc_cm_fr004_08_transfer_d06_no_discard` |
| TC-CM-FR004-09 | CaseId not belonging to Complaint → reject | AC-CM-FR004-09 | API-507 | — | Must | **Automated** | `backend/tests/test_cm_batch1_attachments.py::test_tc_cm_fr004_09_case_id_rejected` |

---

## TC ↔ automated evidence matrix (TASK-006-01)

Primary node only (no duplicate primary ownership). Secondary symbols listed in FR tables where useful.

| TC ID | Exec | Primary node |
|---|---|---|
| TC-CM-FR001-01 | Automated | `test_cm_batch1.py::test_tc_cm_fr001_01_create_registered_no_case` |
| TC-CM-FR001-02 | Automated | `test_cm_batch1.py::test_tc_cm_fr001_02_customer_id_only` |
| TC-CM-FR001-03 | Automated | `test_cm_batch1_foundation.py::test_create_commits_audit_timeline_outbox` |
| TC-CM-FR001-04 | Automated | `test_cm_batch1.py::test_tc_cm_fr001_04_missing_fields` |
| TC-CM-FR001-05 | Pending | — |
| TC-CM-FR001-06 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_03_override_without_reason_rejected` |
| TC-CM-FR001-07 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_08_transfer_d06_no_discard` |
| TC-CM-FR001-08 | Pending | — |
| TC-CM-FR001-09 | Pending | — |
| TC-CM-FR001-10 | Automated | `test_cm_batch1.py::test_tc_cm_fr001_10_request_id_replay` |
| TC-CM-FR001-11 | Automated | `test_cm_batch1.py::test_tc_cm_fr001_11_channel_message_replay` |
| TC-CM-FR001-12 | Automated | `test_cm_batch1.py::test_tc_cm_fr001_12_360_after_create` |
| TC-CM-FR002-01 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_01_unique_customer_number` |
| TC-CM-FR002-02 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_02_ambiguous_no_lock` |
| TC-CM-FR002-03 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_03_not_found` |
| TC-CM-FR002-04 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_04_write_back_rejected` |
| TC-CM-FR002-05 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_05_strict_unavailable` |
| TC-CM-FR002-06 | Automated | `frontend/src/lib/api/cmBatch1.test.ts` (`cmBatch1Paths`) |
| TC-CM-FR002-07 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_07_two_keys_rejected` |
| TC-CM-FR002-08 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_08_enumeration_blocks` |
| TC-CM-FR002-09 | Automated | `test_cm_batch1.py::test_tc_cm_fr002_09_as_of_present` |
| TC-CM-FR003-01 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_01_warning_in_window` |
| TC-CM-FR003-02 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_02_link_existing_no_case` |
| TC-CM-FR003-03 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_03_override_without_reason_rejected` |
| TC-CM-FR003-04 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_04_override_with_justification` |
| TC-CM-FR003-05 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_05_hard_block_rejects_create` |
| TC-CM-FR003-06 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_06_degraded_later_review` |
| TC-CM-FR003-07 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_07_out_of_scope_uniform_empty` |
| TC-CM-FR003-08 | Automated | `test_cm_batch1.py::test_tc_cm_fr003_08_no_case_from_duplicate_flow` |
| TC-CM-FR004-01 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_01_upload_active_with_hash` |
| TC-CM-FR004-02 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_02_reject_illegal_type` |
| TC-CM-FR004-03 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_03_malware_reject` |
| TC-CM-FR004-04 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_04_void_with_reason` |
| TC-CM-FR004-05 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_05_supersede` |
| TC-CM-FR004-06 | Automated | `test_cm_batch1_attachments.py::test_repo_history_and_list` |
| TC-CM-FR004-07 | Automated | `frontend/src/lib/api/cmBatch1.upload.test.ts` |
| TC-CM-FR004-08 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_08_transfer_d06_no_discard` |
| TC-CM-FR004-09 | Automated | `test_cm_batch1_attachments.py::test_tc_cm_fr004_09_case_id_rejected` |

### Mapping notes

- **Shared evidence:** `test_tc_cm_fr003_03_*` is primary for TC-CM-FR003-03 and also satisfies TC-CM-FR001-06 “without justification”; `test_tc_cm_fr003_04_*` completes FR001-06 “with justification”. `test_tc_cm_fr004_08_*` is primary for TC-CM-FR004-08 and satisfies TC-CM-FR001-07 transfer.
- **Not Manual:** no TC in this catalog is designated Manual for Batch-1 lab; gaps are **Pending** (automation absent).
- **Out of 38-TC denominator:** API-513 / M3b–M3d supervisor tests, foundation outbox/migration probes, ops hygiene — evidence for Mode A keep-green, not additional TC-CM-* rows.

## Authoring notes

- Prefix paths under `/api/v1/cm/...` for Aggregate Batch 1 (see OpenAPI).
- Synthetic customers only; never real PII.
- Security suite must include enumeration, idempotency replay, authz deny.
- Closing remaining **Pending** Must TCs (FR001-05/08/09) requires a **separate** testing task (e.g. TASK-006-02) — out of scope for TASK-006-01.

## Document History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-29 | Initial 38 Planned TCs from RTM-CM-B1-001 (S0) |
| 1.0.1 | 2026-08-01 | TASK-006-01 — map existing pytest/vitest → TC-CM-*; Exec column; 35 Automated / 3 Pending; no new tests |

---

*End of TC-CAT-CM-B1-001.*
