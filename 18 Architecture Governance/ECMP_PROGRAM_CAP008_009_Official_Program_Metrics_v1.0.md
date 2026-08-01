# CAP-008 Official Program Metrics

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-009 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 Official (repository-counted) |
| Authority | Architecture Review Board |
| Method | Counts and statuses from repository evidence only — no estimates |

## 1. Scope metrics

| Metric | Value | Evidence |
|---|---|---|
| Capability | CAP-008 | Capability Register |
| FR (document-local) | 6 (FR-001…FR-006) | FRD-CM-B2-001 LOCKED |
| Trace FR IDs | 6 (FR-CM-B2-001…006) | `traceability.yaml` |
| OpenAPI operations | 6 (API-530…535) | API Catalog README |
| TRC links | 6 (TRC-L-011…016) | `traceability.yaml` v0.11 |
| Residual BQ | **0** | DEC-MODEA-B2-001 |

## 2. Quality / RC metrics

| Metric | Value | Evidence |
|---|---|---|
| REL-RC-001 verdict | PASS (lab) | `REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md` |
| CAP-008 pytest (assessment) | 12 passed | REL-RC-001 §2 |
| Batch-1 + CAP-008 regression (assessment) | 46 passed | REL-RC-001 §2 |
| Test module lines | 472 | `backend/tests/test_cm_case_mode_a.py` |
| Annotated RC tag | `v1.2.0-rc.1` | `git tag` |
| RC tip SHA | `6890f50d8243ba30589a3d88f0c0efcef791ce01` | `git rev-parse v1.2.0-rc.1^{}` |
| Alembic | `0046_cm_case_management` | REL-RC-001 / CHANGELOG |

## 3. Governance metrics

| Metric | Value | Evidence |
|---|---|---|
| FRD status | LOCKED | FRD-CM-B2-001 |
| OpenAPI status | Implemented (lab) | `cm-case-management.v1.yaml` v1.0.0 |
| Register status | Implemented (lab) | BP-CAP-001 |
| SoT Closure | COMPLETE | GOV-SOT-CAP008-001 |
| Production `v1.2.0` | NOT authorized | REL-SEC-001 NO-GO |
| Mode B | CLOSED | C-7 / C-B6-1 |

## 4. Explicit zeros / not claimed

| Metric | Value |
|---|---|
| EVT Aggregate catalog IDs specified | 0 (NOT SPECIFIED) |
| Formal TC-catalog IDs | 0 (deferred; lab suite only) |
| Production AuthN GO | 0 |
| Mode B unlock resolutions | 0 |

## 5. Program completion declaration

Engineering Mode A CAP-008 delivery metrics above are **complete for lab RC + SoT**.  
Production and Mode B metrics are **out of program** and do not reopen CAP-008.

---

*End of GOV-CAP008-CLOSE-009.*
