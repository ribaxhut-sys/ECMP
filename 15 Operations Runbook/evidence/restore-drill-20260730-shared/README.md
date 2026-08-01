# Restore Drill Evidence — Shared-Profile (2026-07-30)

| Field | Value |
|---|---|
| ID | OPS-RST-EVID-20260730-SHARED |
| Procedure | OPS-RST-001 + OPS-RCV-001 |
| Date (UTC) | 2026-07-30 |
| Operator | ECMP Operations executor (lab) |
| Environment class | **Shared-profile** — `ECMP_ENV=shared` + `ECMP_AUTH_MODE=jwt` + Keycloak IdP (`ecmp-keycloak`) on foundation Compose host |
| Not claimed | Dedicated remote SIT/UAT VM (ADR-010 full activation) / production cutover Go |
| Result | **PASS** |
| Closes audit **K-4** / SEC-MIG **RR-1** (shared-profile class) | **YES** — with conditions in §6 |
| Related lab pack | `../restore-drill-20260730/` (Mode A foundation; not sufficient alone for K-4) |

---

## 1. Scope honesty

| Claim | Status |
|---|---|
| Writers stopped before dump | **Yes** (`ecmp-backend` stopped) |
| Binary-safe `-Fc` dump + SHA-256 | **Yes** |
| Restore to separate DB `ecmp_k4_shared_restore` | **Yes** |
| Dual audit tables SRC=DST | **Yes** |
| App started against restored DB with `auth_mode=jwt` `ecmp_env=shared` | **Yes** (`ecmp-backend-k4-shared:8001`) |
| `GET /live` + `GET /ready` | **PASS** |
| Local credential login disabled (`ECMP_LOCAL_CREDENTIAL_AUTH=false`) | **PASS** (`LOCAL_CREDENTIAL_AUTH_DISABLED`) |
| IdP AuthN smoke (Keycloak password grant → Bearer `/api/v1/auth/me`) | **PASS** (`idp_dev_cs_agent` / AGENT) |
| Config validator shared profile | **PASS** |
| Remote multi-host SIT/UAT | **Not provisioned** — this drill is shared-**profile** on lab host |
| Production cutover authorization | **Not granted** — REL-SEC-001 still required per release candidate |

---

## 2. Artifacts

| Artifact | Value |
|---|---|
| Dump | `./ecmp_shared_profile.dump` |
| SHA-256 | `EE804E34F223D857CDCF7E8C50D300FC2C3F1D354CDD0831AC698108377910C6` |
| Pre/post watermarks | `pre_dump_watermarks.txt` / `post_restore_watermarks.txt` |
| HTTP / AuthN smoke | `http_smoke.txt` |
| Shared profile env (redact secrets if publishing externally) | `shared_profile.env` |
| Config validator | `config_validator.txt` |
| IdP | `ecmp-keycloak` healthy; issuer `http://localhost:8180/realms/ecmp` |

---

## 3. Measured RTO / RPO (honesty)

| Field | Value |
|---|---|
| T0 (writers stopped / dump start) | `2026-07-30T13:32:04Z` |
| T1 (shared-profile smoke PASS) | `2026-07-30T13:34:20Z` |
| **Measured RTO** | ≈ **2 m 16 s** lab wall-clock |
| DEC-005 target RTO | 4 hours — **PASS vs target** (lab only; not a production SLA proof) |
| **Measured RPO** | Time since this logical dump — **not** DEC-005 15m (WAL/PITR still out of scope) |
| Alembic | `0044_admin_rbac_repair` |
| `audit_logs` | n=589 (SRC=DST) |
| `audit_logs_legacy` | n=887 (SRC=DST) |

---

## 4. AuthN notes (shared-profile)

1. Backend rebuilt so K-3 gate is present in image before final smoke.
2. Mode A `/api/v1/auth/login` returns **403** `LOCAL_CREDENTIAL_AUTH_DISABLED` under shared profile.
3. IdP user `dev.cs_agent` token (`aud=ecmp-api`, `roles=["cs_agent"]`, `orgUnitId=OU-DEV-01`) mapped to seeded local user `idp_dev_cs_agent` with `id` = Keycloak `sub` for `/auth/me` correlation (lab drill only — not Mode B Identity Adapter unlock).

---

## 5. Sign-off

| Role | Status |
|---|---|
| Operations / drill executor | **Signed — PASS** 2026-07-30 |
| Approver (Operations Lead) | **Accepted via Project Owner chat instruction** 2026-07-30 (complete K-4) |
| Security Officer (audit tables + shared-profile AuthN) | **Accepted via Project Owner chat instruction** 2026-07-30 as **lab shared-profile Security Officer delegate** — see §6 conditions |

Named individual wet-ink / enterprise SO countersign for **remote SIT/UAT or production** remains a follow-up when ADR-010 shared hosts exist.

---

## 6. Conditions of K-4 closure

| # | Condition |
|---|---|
| C-K4-1 | This PASS closes Independent Audit **K-4** / SEC-MIG **RR-1** for **shared-profile recovery evidence** on the foundation Compose + IdP baseline. |
| C-K4-2 | Does **not** authorize production cutover by itself — REL-SEC-001 + REL-APR-001 + REL-EVID-001 still gate each release candidate. |
| C-K4-3 | Does **not** unlock Mode B / Batch-2 / enterprise customer (PROGRAM-BOARD-004 **C-7**). |
| C-K4-4 | When a dedicated shared SIT/UAT or production host is provisioned, Operations **must** re-run OPS-RCV-001 there and obtain a **named** Security Officer sign-off for that host class. |
| C-K4-5 | RPO must not be advertised as 15 minutes until WAL/PITR exists. |

---

## 7. Cleanup after drill

- Ephemeral container `ecmp-backend-k4-shared` removed; Mode A `ecmp-backend` restored.
- DB `ecmp_k4_shared_restore` retained on `ecmp-postgres` for forensics (drop when ops confirm).
- Keycloak left running if already used by lab; stop via IdP runbook when idle.

## Related

- `../../ECMP_Restore_Verification_Procedure_v0.1.md` (OPS-RST-001)
- `../../ECMP_Recovery_Validation_Checklist_v1.0.md` (OPS-RCV-001)
- `../../ECMP_IdP_Administrator_Runbook_v1.0.md` (OPS-IDP-001)
- `../../../18 Architecture Governance/ECMP_AUDIT_ADDENDUM_Independent_Program_Audit_20260730_Fase0_v1.0.md`
- `../../../docs/releases/SEC_MIG_FINAL_CERTIFICATION_v1.0.md` (RR-1 / C1)
