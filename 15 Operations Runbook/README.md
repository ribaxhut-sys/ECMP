# 15 Operations Runbook

| Field | Value |
|---|---|
| ID | OPS-000 |
| Version | 0.5 |
| Owner | SRE / Operations |
| Reviewer | DevOps |
| Approver | Operations Lead |
| Status | 🟢 Active (security + backup-recovery; general Draft where noted) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |
| Task note | SECMIG-P6-005 navigation |

## Purpose

Prosedur operasional harian dan penanganan insiden ECMP untuk tim operations/support.

**Canonical application stack for production and SEC-MIG ops:** root `backend/`, `frontend/`, and Compose files at repo root. Paths under `implementation/` are **Historical / optional packs** (slice drills, local IdP baseline) unless a document explicitly says otherwise.

## Owner

- Document Owner: Operations Lead
- Reviewers: DevOps, Domain Tech Leads, Support Lead, Security Architect

## Status

General runbook content remains Draft-conservative where shared-env automation is still Planned (ADR-010). Security operations (P6-002) and Backup & Recovery Security documentation (P6-003) are **Active** for the foundation stack. WAL/PITR/schedulers remain **out of scope**.

## Operator navigation

Come here **after** Release + Deployment + Startup for day-2 / incident / recovery work:

```text
Release (REL-SEC-001)
  → Deployment (DEP-CHK-V1)
  → Startup (START-CHK-001)
  → Security Operations (this folder)
  → Backup / Restore / Recovery
  → Rollback (docs/releases)
```

Hub: [`../docs/deployment/README.md`](../docs/deployment/README.md).  
Release entry: [`../16 Release Management/README.md`](../16%20Release%20Management/README.md).

**Precedence for foundation cutover:** REL-SEC-001 → DEP-CHK-V1 → START-CHK-001.  
Historical DEP-CHK-001 is **not** used for foundation production cutover.

## Documents

### Security operations (SECMIG-P6-002) — Active

- [`ECMP_Security_Operations_Runbook_v1.0.md`](./ECMP_Security_Operations_Runbook_v1.0.md) (OPS-SEC-RB-001) — auth, lockout, secret compromise, config/deploy failure, escalation
- [`ECMP_Secret_Operations_Guide_v1.0.md`](./ECMP_Secret_Operations_Guide_v1.0.md) (OPS-SEC-SEC-001) — rotation, emergency replace, validation, rollback, evidence
- [`ECMP_Audit_Investigation_Guide_v1.0.md`](./ECMP_Audit_Investigation_Guide_v1.0.md) (OPS-SEC-AUD-001) — `security.*` events, requestId/correlationId, investigation workflow

### Backup & recovery (SECMIG-P6-003) — Active

- [`ECMP_Backup_Operations_Guide_v1.0.md`](./ECMP_Backup_Operations_Guide_v1.0.md) (OPS-BAK-001) — DB/config/secret backup policy, retention, encryption, current RPO, target RTO
- [`ECMP_Restore_Verification_Procedure_v0.1.md`](./ECMP_Restore_Verification_Procedure_v0.1.md) (OPS-RST-001) — DB/config/secret restore, validation, rollback, evidence
- [`ECMP_DR_BCP_Plan_v0.1.md`](./ECMP_DR_BCP_Plan_v0.1.md) (OPS-DR-001) — DR/BCP synchronized to foundation probes `/live` `/ready`
- [`ECMP_Recovery_Validation_Checklist_v1.0.md`](./ECMP_Recovery_Validation_Checklist_v1.0.md) (OPS-RCV-001) — restore/smoke/RPO/RTO/evidence checklist
- [`ECMP_Backup_Strategy_v0.1.md`](./ECMP_Backup_Strategy_v0.1.md) — **Superseded** stub → Backup Operations Guide
- [`evidence/restore-drill-20260722/README.md`](./evidence/restore-drill-20260722/README.md) — Sprint-09 DEV scratch restore drill evidence (PASS)
- [`evidence/restore-drill-20260730/README.md`](./evidence/restore-drill-20260730/README.md) — Foundation lab restore drill (PASS procedure; Mode A)
- [`evidence/restore-drill-20260730-shared/README.md`](./evidence/restore-drill-20260730-shared/README.md) — **Shared-profile** restore drill (PASS — closes audit K-4 / RR-1 with conditions)

### Core operations

- [`ECMP_Runbook_Slice_v0.1.md`](./ECMP_Runbook_Slice_v0.1.md) (OPS-RB-001) — service inventory, health, playbooks P1–P6, escalation matrix (foundation-updated)
- [`ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md`](./ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md) (OPS-CM-B1-STG-001) — Mode A FR-004 staging TTL void + attachment storage probe (script; no Mode B). Same command shape is the **Accepted** Time Source pattern for CAP-006 (ADR-CAP006-002 / B2-25); an SLA sweep crontab is **not** installed until Implementation Gate 1–4 (heartbeat C-1 mandatory).
- [`ECMP_CM_Batch1_SLA_Sweep_v0.1.md`](./ECMP_CM_Batch1_SLA_Sweep_v0.1.md) (OPS-CM-B1-SLA-001) — Mode A SLA H-7/H-3/H-1 + breach sweep + outbox drain + heartbeat markers (IG-20260823-01 authorized; crontab after commands ship)
- [`ECMP_IdP_Administrator_Runbook_v1.0.md`](./ECMP_IdP_Administrator_Runbook_v1.0.md) (OPS-IDP-001) — local DEV Keycloak baseline (**Historical pack path** `implementation/infrastructure` — marked in-doc)
- [`ECMP_Shutdown_Procedure_v0.1.md`](./ECMP_Shutdown_Procedure_v0.1.md) (OPS-SHDN-001) — orderly shutdown
- [`ECMP_Log_Inspection_Procedure_v0.1.md`](./ECMP_Log_Inspection_Procedure_v0.1.md) (OPS-LOG-001) — request id lookup (foundation + historical JSON note)

### Deployment & release (companions)

- [`../docs/deployment/`](../docs/deployment/) — hub, startup checklist, production guide, TLS, upgrade, operational security, secure config
- [`../16 Release Management/`](../16%20Release%20Management/) — **canonical release entry** (REL-SEC-001 security gate, approvals, evidence)
- [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md) — foundation rollback package

## Minimum Contents (v1)

- [x] Service inventory & ownership (OPS-RB-001 §1)
- [x] Health check procedures (OPS-RB-001 §2) — foundation `/live` `/ready`
- [x] Common incident playbooks (OPS-RB-001 §3 — P1–P4)
- [x] Escalation matrix (OPS-RB-001 §4)
- [x] Shutdown procedure (OPS-SHDN-001)
- [x] Structured log inspection / id lookup (OPS-LOG-001)
- [x] Security operations runbook + secret + audit investigation (P6-002)
- [x] Backup operations + restore + DR sync + recovery validation checklist (P6-003)
- [x] Restore drill executed (DEV scratch 2026-07-22; foundation lab 2026-07-30; **shared-profile** 2026-07-30 — OPS-RST-EVID-20260730-SHARED). Dedicated remote SIT/UAT re-drill remains Planned when ADR-010 hosts exist.
- [x] Batch/job monitoring (if any) — Mode A CM Batch-1 staging TTL cleanup via `scripts/cm_batch1_ops_hygiene.py` (OPS-CM-B1-STG-001); generic batch platform still Planned
- [x] Notification failure handling (OPS-RB-001 P6 — Planned, domain belum dibangun)
- [x] SLA breach operational response (OPS-RB-001 P5 — baseline manual)

## Naming

`ECMP_Runbook_<Topic>_vX.Y.md` / `ECMP_<Topic>_Guide_vX.Y.md`

## Related

- `../14 Deployment Standards`
- `../16 Release Management`
- `../docs/deployment/`
