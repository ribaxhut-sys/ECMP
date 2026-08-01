# REL-RC-001 Assessment — CAP-008 Mode A (Batch-2)

| Field | Value |
|---|---|
| Template | `16 Release Management/ECMP_RC_Release_Checklist_v0.1.md` |
| Capability | CAP-008 Case Management (Mode A) |
| Branch | `feature/cm-batch1-s2-persistence` |
| Freeze tip | `6890f50d8243ba30589a3d88f0c0efcef791ce01` (`6890f50`) — annotated tag `v1.2.0-rc.1` tip |
| SemVer | `v1.2.0-rc.1` |
| Date assessed | 2026-08-01 |
| Assessor | Release Engineering (lab) |
| Alembic | `0046_cm_case_management` |
| Verdict | **PASS (lab)** — READY FOR RC |
| SoT Closure | `deploy/evidence/CAP-008_SoT_Closure_20260801.md` (FRD LOCK + OpenAPI normative; 2026-08-01) |

> Scope: Mode A lab RC for CAP-008 only. Mode B CLOSED.
> **Provenance note (SoT Closure):** Source freeze commit was `b7d8e2c` (ancestor). Annotated tag
> `v1.2.0-rc.1` points to finalize commit `6890f50` (authoritative RC tip). Assessment freeze tip
> aligned to tag tip.

## 0. Scope declaration

| Item | Result | Notes |
|---|---|---|
| RC purpose stated | **PASS** | CAP-008 Mode A internal/lab RC — `v1.2.0-rc.1` |
| Out of scope explicit | **PASS** | Mode B/OIDC, prod cutover, Notification/Assignment/SLA/Event engines |

## 1. Source integrity

| Item | Result | Notes |
|---|---|---|
| Authorized ref selected | **PASS (B-2 Option B)** | Feature-tip lab waiver (same pattern as `v1.1.0-rc.1`) |
| Working tree clean | **PASS** | Tag tip `6890f50` clean at cut; source freeze ancestor `b7d8e2c` |
| SHA in CHANGELOG | **PASS** | Section `[1.2.0-rc.1]` + this assessment |
| No secrets in tree | **PASS (spot)** | `.env*` gitignored |
| R6-01 build-rc / verify-artifact | **N/A (lab)** | Deferred for lab RC (Batch-1 posture) |

## 2. Quality gates

| Item | Result | Notes |
|---|---|---|
| CAP-008 pytest | **PASS** | `test_cm_case_mode_a.py` — 12 passed (incl. 401/403/`AuditTimelineSideEffects`) |
| Batch-1 + CAP-008 regression | **PASS** | 46 passed (foundation + migration pins + security headers + CAP-008) |
| CAP-008 401 / 403 | **PASS** | Automated + live lab: unauth → 401; missing `complaints:create` → 403 |
| `AuditTimelineSideEffects` | **PASS** | Unit assertion + `get_case_service` wires production side effects |
| Frontend CAP-008 | **PASS** | typecheck OK; 23 vitest passed; Mode A credential routes 5/5 PRESENT |

## 3. Deploy / migration / live verify

| Item | Result | Notes |
|---|---|---|
| Rebuild backend + frontend | **PASS** | Images `ecmp-backend:1.2.0-rc.1` / `ecmp-frontend:1.2.0-rc.1` |
| Lab Mode A posture | **PASS** | `ENVIRONMENT=development`; `/health` → `environment=development`, `version=1.2.0-rc.1` |
| Alembic → `0046_cm_case_management` | **PASS** | Tables `cm_cases`, `cm_case_resolutions`, `cm_case_number_counters` present |
| Live POST/GET/PATCH/resolve/close ≠ 404 | **PASS** | Full lifecycle 201/200/200/200/200; unauth POST → 401 (not 404) |

## 4. Documentation

| Item | Result | Notes |
|---|---|---|
| CHANGELOG `[1.2.0-rc.1]` | **PASS** | Present |
| B2-05 hardening evidence | **PASS** | Updated post-cut |
| Ops / Mode B | **OUT OF SCOPE** | Not claimed |

## 5. Sign-off (REL-RC-001)

| Role | Name | Date | Go / No-Go |
|---|---|---|---|
| Tech Lead | Release Engineering (lab) | 2026-08-01 | **Go** |
| QA Lead | Release Engineering (lab) | 2026-08-01 | **Go** |
| Release Manager | Release Engineering (lab) | 2026-08-01 | **Go** |

## 6. Tag & communicate

| Item | Result |
|---|---|
| Annotated RC tag | **CUT** | `v1.2.0-rc.1` on freeze tip |

## Blocking summary

**NONE** — READY FOR RC (lab / Mode A CAP-008).
