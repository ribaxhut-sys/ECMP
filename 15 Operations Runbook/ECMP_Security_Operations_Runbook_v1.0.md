# ECMP Security Operations Runbook

| Field | Value |
|---|---|
| ID | OPS-SEC-RB-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Owner | Operations Lead / Security Architect |
| Status | 🟢 Active (foundation stack) |
| Task | TASK-PLATFORM-SECMIG-P6-002 |
| Scope | Root foundation (`backend/`, `frontend/`, Compose) — **not** feature redesign |
| Related | SECMIG-P5-004/005, SECMIG-P6-001, OPS-RB-001, OPS-SEC-001 |

## 1. Purpose

Playbook operasional keamanan untuk **foundation ECMP** setelah SEC-MIG Phase 5 dan P6-001 Secure Configuration Baseline.

Tidak mengubah autentikasi, otorisasi, atau audit runtime — hanya prosedur respons.

## 2. Stack in scope

| Component | How to operate |
|---|---|
| Backend API | `backend/` — Compose service `backend` |
| Frontend | `frontend/` |
| Postgres | Compose service `postgres` |
| Production edge | `docker-compose.prod.yml` (Caddy) or `.prod.nginx.yml` |
| Local foundation | Root `docker-compose.yml` |

> **Historical:** Sprint-01 slice paths under `implementation/backend` and `implementation/infrastructure` remain for legacy drills / IdP baseline (OPS-IDP-001). Production and security ops use the **root** stack.

## 3. Escalation (security)

| Level | Role | When |
|---|---|---|
| L1 | On-duty operations / support | Triage; run this runbook; collect `X-Request-ID` |
| L2 | Backend Lead **or** DevOps Lead | Config/deploy/IdP connectivity; persistent auth failures |
| L2-SEC | Security Architect / Security Officer | Secret/key compromise; confirmed abuse; audit integrity |
| L3 | Solution Architect / Operations Lead | Cross-team outage; restore decisions; data retention |

Map platform security events (`security.*`) → start at L1; escalate to **L2-SEC** when compromise or mass abuse is suspected.

Companion guides:

- Secret rotation / emergency replace → [`ECMP_Secret_Operations_Guide_v1.0.md`](./ECMP_Secret_Operations_Guide_v1.0.md) (OPS-SEC-SEC-001)
- Audit investigation → [`ECMP_Audit_Investigation_Guide_v1.0.md`](./ECMP_Audit_Investigation_Guide_v1.0.md) (OPS-SEC-AUD-001)
- Deploy/smoke/rollback → [`../docs/deployment/`](../docs/deployment/)

---

## 4. Playbooks

### SEC-P1 — Authentication incident (login / token failures)

1. **Symptom:** Spikes of HTTP 401/403; users cannot log in; logs show token reject; IdP errors.
2. **Impact:** AuthN unavailable or partial; lockouts may cascade (SEC-P2).
3. **Detection:**
   - Access logs: `status=401` / `403` with `request_id=…`
   - Platform audit: `event_type` in `security.login_failed`, `security.token_rejected`, `security.permission_denied`
   - Backend env: `ECMP_AUTH_MODE`, `OIDC_*` (staging/production **must** be `jwt` — P6-001)
4. **Diagnosis:**
   - Confirm mode inside container: `ECMP_AUTH_MODE` should be `jwt` when `ENVIRONMENT` is staging/production.
   - Confirm OIDC issuer/audience/JWKS reachable from backend network.
   - Distinguish client misconfig (single user) vs systemic (all users / all paths).
   - Capture response `X-Request-ID`; investigate per OPS-SEC-AUD-001.
5. **Mitigation:**
   - Do **not** switch production to `ECMP_AUTH_MODE=dev` (startup refuse / policy P6-001).
   - If IdP down: communicate outage; keep edge rate limits; do not weaken CORS/hosts.
6. **Resolution:** Restore IdP/JWKS or correct OIDC env; re-validate with CLI; smoke login over HTTPS.
7. **Escalation:** L2 (IdP/config) → L2-SEC if credential stuffing suspected.
8. **Post-incident:** Update ticket with request ids + `event_type` counts; review edge limits.

### SEC-P2 — Lockout storm

1. **Symptom:** Many `security.lockout` rows; clients receive lockout with `retryAfterSeconds` / `Retry-After`; legitimate users blocked.
2. **Impact:** Availability for affected identities/IPs; audit write amplification (accepted P5-005 residual).
3. **Detection:** Query audit for `security.lockout` / `security.login_failed` in a time window (OPS-SEC-AUD-001). Login limiter is **in-memory per process** (not Redis).
4. **Diagnosis:**
   - Single IP vs distributed sources (`ip_address` on audit rows).
   - Confirm `TRUST_FORWARDED_CLIENT_IP` still `false` unless intentionally enabled; prefer Uvicorn `FORWARDED_ALLOW_IPS`.
   - Multi-replica: lockout state is **not** shared — attackers may rotate instances.
5. **Mitigation:**
   - Edge / reverse-proxy / WAF rate limits (primary per `OPERATIONAL_SECURITY.md`).
   - Do not disable `LOGIN_RATE_LIMIT_ENABLED` in production without L2-SEC approval.
   - Temporary IP block at edge if clear abuse source.
6. **Resolution:** Abuse stopped; lockouts expire (`LOGIN_LOCKOUT_SECONDS`, default 300); verify login for canary users.
7. **Escalation:** L2-SEC when coordinated attack or audit DB pressure.
8. **Post-incident:** Record whether edge controls were missing; no application sampling of audit (policy locked).

### SEC-P3 — Secret compromise

1. **Symptom:** Suspected leak of `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`, `.env`, or CI secrets; unexpected admin activity.
2. **Impact:** Token forgery risk (lab/`dev` HS256 path), DB exfiltration, lateral movement.
3. **Detection:** External report, git history, log scrub miss, anomalous DB access.
4. **Diagnosis:** Identify which secret class (see OPS-SEC-SEC-001 inventory). Note: staging/production AuthN is `jwt` — HS256 secret is dual-mode tooling / residual lab surface, still rotate if leaked.
5. **Mitigation / Resolution:** Follow **emergency replacement** in OPS-SEC-SEC-001 immediately (rotate → validate → restart → smoke → evidence). Escalate L2-SEC.
6. **Escalation:** L2-SEC + Operations Lead; consider session invalidation / IdP password resets for affected users.
7. **Post-incident:** Confirm old secret not in images/logs/tickets; rotate related credentials (DB, pgAdmin if used).

### SEC-P4 — Production configuration error

1. **Symptom:** Backend container exit loop; logs `Configuration validation failed`; compose `${VAR:?}` refuse; wrong AuthN mode attempt.
2. **Impact:** Outage or fail-closed start (preferred vs insecure start).
3. **Detection:** `docker compose … logs backend`; CLI validator FAIL; missing `application started … auth_mode=jwt`.
4. **Diagnosis:**
   ```powershell
   python scripts/validate-production-config.py --env-file .env --require-production
   docker compose -f docker-compose.prod.yml config
   ```
   - Check P6 vars: `ECMP_AUTH_MODE`, `ECMP_ENV`, `OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URL`.
5. **Mitigation:** Fix `.env` from `.env.production.example`; do not bypass fail-fast.
6. **Resolution:** Validator PASS; backend healthy; `/ready` 200; logs show expected `ENVIRONMENT` + `auth_mode=jwt`.
7. **Escalation:** L2 DevOps if compose/network; L2 Backend if Settings/validation semantics.
8. **Post-incident:** Update checklist if a new footgun appeared.

### SEC-P5 — Deployment failure

1. **Symptom:** Deploy/upgrade fails (build, migrate, healthcheck, TLS, frontend).
2. **Impact:** Partial or full outage.
3. **Detection:** Compose `ps` unhealthy; `/ready` 503; Caddy/ACME errors; Alembic errors in entrypoint.
4. **Diagnosis:** Separate layers — proxy TLS, backend config, DB migrate, frontend build-arg `NEXT_PUBLIC_API_BASE_URL`.
5. **Mitigation:** Prefer **forward-fix**; if go-live validation fails, execute [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md) with approval.
6. **Resolution:** Smoke checklist PASS (section 5 deployment docs); AuthN jwt smoke if staging/production.
7. **Escalation:** L2 DevOps (infra) / Backend (migrate); L3 if `audit_logs` / data restore.
8. **Post-incident:** Attach pre-upgrade dump id; note image tags.

### SEC-P6 — Security event escalation

1. **Symptom:** Confirmed or high-confidence security incident beyond single user error.
2. **Impact:** Confidentiality/integrity risk; regulatory/comms needs.
3. **Detection:** Investigator (OPS-SEC-AUD-001) finds patterned `security.*` events, compromise indicators, or SEC-P3 trigger.
4. **Actions:**
   - Declare incident commander (Operations Lead or L2-SEC).
   - Freeze unnecessary config changes; preserve logs + DB (no destructive restore without approval).
   - Collect evidence pack: time window, `requestId`s, `event_type` histogram, compose/image tags, config validator output (redact secrets).
   - Execute relevant playbook (SEC-P1…P5).
5. **Resolution criteria:** Threat contained; secrets rotated if needed; service validated; stakeholders notified.
6. **Post-incident:** Blameless notes; update this runbook / secret guide if gaps.

---

## 5. Quick reference — probes

```powershell
# Production (proxy published only)
curl.exe -fsS https://$env:ECMP_DOMAIN/live
curl.exe -fsS https://$env:ECMP_DOMAIN/ready

# Local foundation
curl.exe -fsS http://127.0.0.1:8000/live
curl.exe -fsS http://127.0.0.1:8000/ready
```

Capture `X-Request-ID` from failing responses for audit correlation.

## 6. Related

- [`../docs/deployment/OPERATIONAL_SECURITY.md`](../docs/deployment/OPERATIONAL_SECURITY.md) (OPS-SEC-001)
- [`../docs/deployment/STARTUP_CHECKLIST.md`](../docs/deployment/STARTUP_CHECKLIST.md)
- [`./ECMP_Runbook_Slice_v0.1.md`](./ECMP_Runbook_Slice_v0.1.md) (OPS-RB-001) — general service playbooks
- [`./ECMP_IdP_Administrator_Runbook_v1.0.md`](./ECMP_IdP_Administrator_Runbook_v1.0.md) (OPS-IDP-001) — local IdP only
