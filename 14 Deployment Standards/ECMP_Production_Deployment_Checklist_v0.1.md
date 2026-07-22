# ECMP Production Deployment Checklist

| Field | Value |
|---|---|
| ID | DEP-CHK-001 |
| Version | 0.1 |
| Owner | DevOps Lead |
| Reviewer | Security / SRE |
| Approver | Architecture Board |
| Status | 🟡 Draft (checklist — no production deploy in Sprint-08) |
| Last Review | 2026-07-22 |
| Related | DEP-001, ADR-010, ADR-007, TS-001 §7 |

Documentation only (Sprint-08 P1). **Do not** treat this as authorization to build a
Dockerfile, production Compose file, or shared-environment deploy. Those remain
prohibited until ADR-010's SIT/UAT activation trigger fires (ADR-007 target auth live).

## 1. Activation trigger (hard gate)

SIT/UAT baseline may be activated **only when**:

1. ADR-007 **target** authentication (JWT/OIDC) is live — static `ECMP_DEV_*` tokens
   prohibited in shared environments.
2. Architecture Board confirms ADR-010 § activation checklist can proceed.

Until then: DEV + CI only (DEP-001 §1).

## 2. Ordered build list (execute *after* trigger — not now)

1. Application Dockerfile (TS-001 §7) + image tagging standard.
2. Container registry wiring + GitHub Actions deploy workflow for SIT.
3. Production-class Compose (or equivalent) for the single-VM SIT/UAT baseline.
4. Secret manager / vault path for `ECMP_*` credentials (SEC-STD-001 §7 TBD → decided).
5. Set real `ECMP_ALLOWED_ORIGINS` for the frontend origin(s).
6. `ECMP_ENV=sit|uat`, `ECMP_ENABLE_DEV_ENDPOINTS` unset/false, non-default tokens.
7. PostgreSQL backup automation (`pg_dump` + WAL) — see Backup Strategy.
8. First restore drill — see Restore Verification Procedure (required before UAT).

## 3. Pre-merge / pre-release checklist (applies today)

| # | Check | Evidence |
|---|---|---|
| 1 | Backend CI green (`backend-ci.yml`) | PR checks |
| 2 | Frontend CI green incl. `npm audit --audit-level=high` | PR checks |
| 3 | OpenAPI catalog matches runtime (`test_contract_conformance`) | pytest |
| 4 | Liveness `GET /health` → 200 | smoke |
| 5 | Readiness `GET /health/ready` → 200 with DB up | smoke |
| 6 | Security headers present on responses | Sprint-08 tests |
| 7 | Structured JSON logs; no PII (`subject`/`description`/tokens) | log review |
| 8 | `X-Request-ID` / `X-Correlation-ID` echoed | smoke |
| 9 | CORS fail-closed when `ECMP_ALLOWED_ORIGINS` empty | config review |

## 4. Secret-leakage review (Sprint-08)

| Check | Result (2026-07-22) |
|---|---|
| `.env` gitignored | Confirmed via `.gitignore` (`**/.env`, `.env`) |
| `.env` never committed | `git log --all --full-history -- "**/.env"` — no commits of secrets expected; local `.env` must remain untracked |
| `.env.example` | Non-secret placeholders only (`dev-token`, local DB password labeled `ecmp_local_only`) |
| Error responses | Envelope `{code,message,details?}` — no stack traces (TS-001) |
| Structured logs | Access logs use method/path/status/ids only — no case subject/description |

Findings: **no production secrets in tree**. Local docker-compose Postgres password is a
documented local-only default, not a shared-env credential.

## 5. Backend startup baseline (measured Sprint-08)

| Metric | Approximate (local SQLite / warm disk) | Notes |
|---|---|---|
| Cold start to accept HTTP | &lt; 2 s typical | `uvicorn app.main:app` — no heavy init beyond config + engine |
| First `GET /health` | &lt; 50 ms after listen | Liveness, no DB |
| First `GET /health/ready` | depends on DB | Includes `SELECT 1` |

No speculative pool tuning (SQLAlchemy defaults) until shared-env load data exists.

## Related

- `./ECMP_Deployment_Standards_v0.1.md` (DEP-001)
- `../15 Operations Runbook/ECMP_Backup_Strategy_v0.1.md`
- `../15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md`
- `../05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`
