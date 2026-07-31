# Restore Drill Evidence — Foundation Compose (2026-07-30)

| Field | Value |
|---|---|
| ID | OPS-RST-EVID-20260730 |
| Procedure | OPS-RST-001 + OPS-RCV-001 checklist (as applicable) |
| Date (UTC) | 2026-07-30 |
| Operator | ECMP Documentation / Operations executor (lab) |
| Environment class | **Lab foundation Compose** (`ecmp-postgres` / `ecmp-backend`) — **NOT** shared SIT/UAT/staging/production |
| Result (procedure proof) | **PASS** (dump → scratch restore → dual audit tables → `/live` `/ready` + Mode A login smoke) |
| Result vs RR-1 / audit **K-4** | **DOES NOT CLOSE** — shared-env drill still **OPEN** (ADR-010 shared env not provisioned; Security Officer sign-off deferred) |

---

## 1. Honesty statement (mandatory)

This pack **upgrades** the 2026-07-22 DEV scratch proof to current Alembic head (`0044_admin_rbac_repair`) and current dual-table audit model, and adds foundation HTTP probes.

It does **not** satisfy:

| Gate | Why unmet |
|---|---|
| Shared-env restore drill (OPS-DR-001 / REL-SEC-001 §3.6) | No shared SIT/UAT host; local Docker only |
| Staging/production `ECMP_AUTH_MODE=jwt` smoke | Lab runs Mode A `ECMP_AUTH_MODE=dev` (intentional) |
| Security Officer sign-off on `audit_logs` | Synthetic/lab data — **PENDING** named SO (not invented) |
| DEC-005 RTO ≤ 4h claim | Lab wall-clock only; **N/A** vs shared target |
| WAL/PITR RPO = 15m | Not implemented — RPO = time since this logical dump |

**Audit K-4 / RR-1 CRITICAL therefore remains OPEN** until a true shared-env drill + SO sign-off exists.

---

## 2. Artifacts

| Artifact | Path / value |
|---|---|
| Logical dump (`pg_dump -Fc`) | `./ecmp_foundation_k4.dump` |
| SHA-256 | `F81F1C2F2CE7A8EE7162BF48912CFC04F9DEF1DEBA901D89D4F93C465F11EE66` |
| Source | Live Compose service `ecmp-postgres` DB `ecmp` |
| Target | Scratch container `ecmp-restore-k4-dst` DB `ecmp_restored` (destroyed after verify) |
| Pre/post watermarks | `pre_dump_watermarks.txt` / `post_restore_watermarks.txt` |
| HTTP smoke | `http_smoke.txt` |
| Config validator (lab `.env`) | `config_validator.txt` |
| Timestamps | `timestamps.txt` |

---

## 3. Steps executed

1. Recorded T0 = `2026-07-30T13:25:07Z`.
2. Captured SRC watermarks: Alembic `0044_admin_rbac_repair`; `audit_logs` n=589; `audit_logs_legacy` n=886.
3. Binary-safe dump: `pg_dump -Fc` inside container → `docker cp` → SHA-256 file.
4. Provisioned scratch Postgres 16; `pg_restore --clean --if-exists` (exit 0).
5. Compared DST watermarks — **match SRC** for Alembic + both audit tables.
6. HTTP against **live** foundation backend (non-destructive; DB cutover of live not performed): `GET /live` 200; `GET /ready` 200; login `golive_admin` OK; `/auth/me` OK.
7. Ran `python scripts/validate-production-config.py --env-file .env` (lab — not `--require-production`).
8. Recorded T1 = `2026-07-30T13:25:33Z`; removed scratch container.

---

## 4. Verification results

| Check | Result |
|---|---|
| SHA-256 verified | PASS |
| `pg_restore` exit 0 | PASS |
| Alembic SRC = DST | PASS (`0044_admin_rbac_repair`) |
| `audit_logs` count + `max(created_at)` SRC = DST | PASS (`589`) |
| `audit_logs_legacy` count + `max(occurred_at)` SRC = DST | PASS (`886`) |
| Append-only integrity | PASS — restore only; no UPDATE/DELETE tooling |
| `GET /live` | PASS (live foundation) |
| `GET /ready` | PASS (live foundation) |
| Auth smoke (Mode A login) | PASS (`golive_admin`) |
| Measured RTO (lab wall-clock) | ≈ **26 s** (T0→T1) — **not** comparable to 4h shared target |
| Measured RPO honesty | = age of this logical dump vs any future incident — **not** 15m WAL claim |
| Security Officer sign-off | **PENDING** (deferred; not invented) |
| Shared-env classification | **FAIL / N/A** — lab only |

---

## 5. Sign-off

| Role | Status |
|---|---|
| Operations / drill executor | Signed — procedure PASS 2026-07-30 (lab) |
| Approver (Operations Lead) | Pending human countersign for release packaging |
| Security Officer (audit tables / shared env) | **Not signed** — required before K-4 / RR-1 CLOSE |

---

## 6. Follow-up to close audit K-4

1. Provision shared SIT/UAT Postgres per ADR-010 activation path.
2. Repeat OPS-RST-001 against that environment with writers stopped (OPS-SHDN-001).
3. Require `ECMP_AUTH_MODE=jwt` + OIDC smoke on shared/staging profile.
4. Obtain **named** Security Officer sign-off on `audit_logs` (+ legacy if in scope).
5. File measured RTO/RPO against DEC-005 with honesty statements.
6. Only then update REL-SEC-001 / SEC-MIG certification C1 and audit addendum K-4 → SATISFIED.

## Related

- `../../ECMP_Restore_Verification_Procedure_v0.1.md` (OPS-RST-001)
- `../../ECMP_Recovery_Validation_Checklist_v1.0.md` (OPS-RCV-001)
- `../restore-drill-20260722/README.md` (historical DEV scratch)
- `../../../18 Architecture Governance/ECMP_AUDIT_ADDENDUM_Independent_Program_Audit_20260730_Fase0_v1.0.md`
