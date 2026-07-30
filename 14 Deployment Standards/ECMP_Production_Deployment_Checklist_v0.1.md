# ECMP Production Deployment Checklist (Historical)

| Field | Value |
|---|---|
| ID | DEP-CHK-001 |
| Version | 0.1 → Historical |
| Owner | DevOps Lead |
| Reviewer | Security / SRE |
| Approver | Architecture Board |
| Status | ⚫ **Historical** (Sprint-08 planning checklist) |
| Last Review | 2026-07-30 |
| Related | DEP-001, ADR-010, ADR-007, TS-001 §7 |
| Task note | SECMIG-P6-005 — superseded for foundation cutover |

> **Historical / not for foundation production cutover.**  
> Retained for Sprint-08 ADR-010 planning context and link stability.  
> **Canonical execution order** for shared/staging/UAT/production on the foundation stack:  
> **REL-SEC-001 → DEP-CHK-V1 → START-CHK-001**  
> See [`../docs/deployment/README.md`](../docs/deployment/README.md) and  
> [`../docs/deployment-checklist.md`](../docs/deployment-checklist.md) (DEP-CHK-V1).

Do **not** treat the body below as the live production cutover checklist.
Items about “do not build Dockerfile / prod Compose yet” reflect the Sprint-08
planning freeze; foundation release docs under `docs/deployment/` are the
operational reference for the current foundation line.

---

## Archived body (Sprint-08 P1 — planning only)

Documentation only (Sprint-08 P1). Original framing: do not treat as authorization
to build Dockerfile / production Compose / shared-environment deploy until
ADR-010 SIT/UAT activation trigger (ADR-007 target auth live).

### 1. Activation trigger (hard gate) — historical wording

SIT/UAT baseline may be activated **only when**:

1. ADR-007 **target** authentication (JWT/OIDC) is live — static `ECMP_DEV_*` tokens
   prohibited in shared environments.
2. Architecture Board confirms ADR-010 § activation checklist can proceed.

Until then (as of Sprint-08): DEV + CI only per then-current DEP-001 §1.

### 2. Ordered build list (post-trigger — historical)

1. Application Dockerfile (TS-001 §7) + image tagging standard.
2. Container registry wiring + GitHub Actions deploy workflow for SIT.
3. Production-class Compose (or equivalent) for the single-VM SIT/UAT baseline.
4. Secret manager / vault path for credentials.
5. Real frontend origin allowlists.
6. Shared-env flags; no default tokens; no dev endpoints.
7. PostgreSQL backup automation (`pg_dump` + WAL) — **still Future** (not P6-003). Use OPS-BAK-001 manual policy until authorized.
8. First **shared-env** restore drill — OPS-RST-001 + OPS-RCV-001 (still required before shared UAT). DEV scratch drill does not satisfy this gate.

### 3. Pre-merge checks (superseded by REL-SEC-001 + DEP-CHK-V1)

Historical smoke used foundation `/live` / `/ready`. Prefer current gates.

### 4–5. Secret-leakage review & startup baseline (2026-07-22)

Sprint-08 evidence snapshot only — not a live cutover record.

## Related (current)

- [`./ECMP_Deployment_Standards_v0.1.md`](./ECMP_Deployment_Standards_v0.1.md) (DEP-001 — Active standards)
- [`../docs/deployment-checklist.md`](../docs/deployment-checklist.md) (DEP-CHK-V1 — **use this**)
- [`../docs/deployment/STARTUP_CHECKLIST.md`](../docs/deployment/STARTUP_CHECKLIST.md) (START-CHK-001)
- [`../16 Release Management/ECMP_Release_Security_Gate_v1.0.md`](../16%20Release%20Management/ECMP_Release_Security_Gate_v1.0.md) (REL-SEC-001)
- [`../docs/deployment/README.md`](../docs/deployment/README.md) (DEP-HUB-001)
