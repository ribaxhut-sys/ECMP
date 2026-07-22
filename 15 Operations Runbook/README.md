# 15 Operations Runbook


| Field | Value |
|---|---|
| ID | OPS-000 |
| Version | 0.1 |
| Owner | SRE / Operations |
| Reviewer | DevOps |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Prosedur operasional harian dan penanganan insiden ECMP untuk tim operations/support.

## Owner
- Document Owner: Operations Lead
- Reviewers: DevOps, Domain Tech Leads, Support Lead

## Status
Draft — konten inti terisi (OPS-RB-001, OPS-DR-001); tetap 🟡 Draft konservatif karena sebagian prosedur masih Planned (menunggu shared env ADR-010) dan batch/job monitoring belum relevan.

## Documents
- [`ECMP_Runbook_Slice_v0.1.md`](./ECMP_Runbook_Slice_v0.1.md) (OPS-RB-001) — service inventory, health check, playbooks P1–P6, escalation matrix
- [`ECMP_DR_BCP_Plan_v0.1.md`](./ECMP_DR_BCP_Plan_v0.1.md) (OPS-DR-001) — RTO/RPO baseline, backup/restore, perlindungan audit_log, BCP
- [`ECMP_Backup_Strategy_v0.1.md`](./ECMP_Backup_Strategy_v0.1.md) (OPS-BAK-001) — Sprint-08 docs-only backup strategy
- [`ECMP_Restore_Verification_Procedure_v0.1.md`](./ECMP_Restore_Verification_Procedure_v0.1.md) (OPS-RST-001) — Sprint-08 restore drill checklist

## Minimum Contents (v1)
- [x] Service inventory & ownership (OPS-RB-001 §1)
- [x] Health check procedures (OPS-RB-001 §2)
- [x] Common incident playbooks (OPS-RB-001 §3 — P1–P4)
- [x] Escalation matrix (OPS-RB-001 §4)
- [ ] Batch/job monitoring (if any) — belum ada batch/job
- [x] Notification failure handling (OPS-RB-001 P6 — Planned, domain belum dibangun)
- [x] SLA breach operational response (OPS-RB-001 P5 — baseline manual)

## Template Sections (per playbook)
1. Symptom
2. Impact
3. Detection
4. Diagnosis steps
5. Mitigation / workaround
6. Resolution
7. Escalation
8. Post-incident actions

## Naming
`ECMP_Runbook_<Topic>_vX.Y.md`

## Related
- `../11 SLA and KPI Matrix`
- `../14 Deployment Standards`
- `../16 Release Management`
