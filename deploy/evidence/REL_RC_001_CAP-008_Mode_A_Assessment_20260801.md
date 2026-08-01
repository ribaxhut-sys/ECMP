# REL-RC-001 Assessment — CAP-008 Mode A (Batch-2)

| Field | Value |
|---|---|
| Template | `16 Release Management/ECMP_RC_Release_Checklist_v0.1.md` |
| Capability | CAP-008 Case Management (Mode A) |
| Branch | `feature/cm-batch1-s2-persistence` |
| SemVer | `v1.2.0-rc.1` |
| Date assessed | 2026-08-01 |
| Assessor | Release Engineering (lab) |
| Alembic | `0046_cm_case_management` |
| Verdict | **PENDING CUT** — filled after freeze / deploy / verify |

> Scope: Mode A lab RC for CAP-008 only. Mode B CLOSED. No FRD / OpenAPI / Business Rules
> edits in this release-engineering cut (engineering SoT frozen as-is).

## 0. Scope declaration

| Item | Result | Notes |
|---|---|---|
| RC purpose stated | **PASS** | CAP-008 Mode A internal/lab RC — `v1.2.0-rc.1` |
| Out of scope explicit | **PASS** | Mode B/OIDC, prod cutover, Notification/Assignment/SLA/Event engines |

## 1. Source integrity

| Item | Result | Notes |
|---|---|---|
| Authorized ref selected | **PASS (B-2 Option B)** | Feature-tip lab waiver (same pattern as `v1.1.0-rc.1`) |
| Working tree clean | **PENDING** | Required before annotated tag |
| SHA in CHANGELOG | **PASS** | Section `[1.2.0-rc.1]` |
| No secrets in tree | **PASS (spot)** | `.env*` gitignored |
| R6-01 build-rc / verify-artifact | **N/A (lab)** | Deferred for lab RC (Batch-1 posture) |

## 2. Quality gates

| Item | Result | Notes |
|---|---|---|
| CAP-008 pytest | **PENDING** | `tests/test_cm_case_mode_a.py` |
| Batch-1 + CAP-008 regression | **PENDING** | Batch-1 foundation + CAP-008 suite |
| CAP-008 401 / 403 | **PENDING** | Automated in `test_cm_case_mode_a.py` |
| `AuditTimelineSideEffects` | **PENDING** | Unit assertion + router wiring review |
| Frontend CAP-008 vitest / typecheck | **PENDING** | Lab attestation |

## 3. Deploy / migration / live verify

| Item | Result | Notes |
|---|---|---|
| Rebuild backend + frontend | **PENDING** | Mode A lab compose (`.env`, `ENVIRONMENT=development`) |
| Alembic → `0046_cm_case_management` | **PENDING** | From lab `0036_search_indexes` |
| Live POST/GET/PATCH/resolve/close ≠ 404 | **PENDING** | Must not return 404 |

## 4. Documentation

| Item | Result | Notes |
|---|---|---|
| CHANGELOG `[1.2.0-rc.1]` | **PASS** | Present |
| B2-05 hardening evidence | **PASS** | `B2-05_CAP-008_Mode_A_Integration_Hardening_20260801.md` |
| Ops / Mode B | **OUT OF SCOPE** | Not claimed |

## 5. Sign-off (REL-RC-001)

| Role | Name | Date | Go / No-Go |
|---|---|---|---|
| Tech Lead | Release Engineering (lab) | 2026-08-01 | **PENDING** |
| QA Lead | Release Engineering (lab) | 2026-08-01 | **PENDING** |
| Release Manager | Release Engineering (lab) | 2026-08-01 | **PENDING** |

## 6. Tag & communicate

| Item | Result |
|---|---|
| Annotated RC tag | **PENDING** | `v1.2.0-rc.1` |

## Blocking summary

Filled after execute steps 1–10 of CAP-008 Release Engineering mission.
