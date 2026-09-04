# ADR-CAP006-002 — Implementation Gate Pack (FR-030 eng authorization)

| Field | Value |
|---|---|
| ID | GOV-AR-CAP006-002-IGATE |
| Review ID | IG-20260823-01 |
| Version | 1.0 |
| Subject | [`ADR-CAP006-002`](../../05%20Architecture%20Decision%20Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md) v0.3.1 |
| Parent Accept | AR-20260823-01 / B2-25 (Accepted with Conditions) |
| Authority | Architecture Review Board · Tech Lead · Solution Architect (gate exit per DEC-002 pattern) |
| Status | 🟢 **PASS** — FR-030 engineering **AUTHORIZED WITH SCOPE** (2026-08-23) |
| Signatory | rbxhut |
| Evidence | [`../../deploy/evidence/B2-26_CAP-006_Implementation_Gate_Pass_20260823.md`](../../deploy/evidence/B2-26_CAP-006_Implementation_Gate_Pass_20260823.md) |

> This pack records Implementation Gate 1–4. It **authorizes coding** of the scoped
> FR-030 / DEC-031 Fase 2 slice below. It does **not** install crontab, open CAP-005,
> or claim off-screen notification delivery.

---

## Authorized engineering scope

| In scope | Out of scope |
|---|---|
| CLI sweep (shape of `cm_batch1_ops_hygiene.py`) using `resolve_complaint_sla` only | Second SLA calculator |
| Predicates for H-7 / H-3 / H-1 + breach; once per threshold per complaint | SMTP / Twilio / FCM / CAP-005 |
| Durable Audit + Timeline + Outbox via `CmBatch1SideEffectRecorder` | New broker / worker / library / container / port |
| In-app alert surface (extend existing dashboard/list feed) | Off-screen push to officers who never open the app |
| Outbox **drainer** CLI under the same pattern (C-4) | Generic retry/DLQ publisher (ADR-009) |
| Hourly cadence config + `flock` + positive heartbeat markers (C-1/C-3) | Invent-authorize alternate Time Source |
| Unit tests mapped toward TC-030 | Changing FRD-005 LOCKED body without DEC |

---

## Gate 1 — Architecture

| ID | Criterion | Verdict | Evidence |
|---|---|---|---|
| G1.1 | Pattern Evidence #1–#8 still in repo | **PASS** | `backend/scripts/cm_batch1_ops_hygiene.py` (103 lines) + unit test; `list_expired_open_staging`; side-effect recorder path; OPS-CM-B1-STG-001 Active; `util-linux` in `backend/Dockerfile:49`; no celery/apscheduler/rq/arq/dramatiq in `requirements.txt` |
| G1.2 | No new scheduler/worker/broker/library/container/port | **PASS** | Design constraint restated; compose remains 4 services |
| G1.3 | ADR Accepted; index updated | **PASS** | ADR v0.3.1 Accepted with Conditions; `ADR_INDEX.generated.md` + `05/README.md` hand-edited (generator drops CAP-006 ids) |
| G1.4 | Positive heartbeat — named owner + mechanism | **PASS** | See §Heartbeat below (closes C-1) |
| G1.5 | Register / TRC / Accept evidence | **PASS** | B2-25; Capability Register; TRC-L-007; B2-24 unamended |

### Heartbeat (C-1 / G1.4) — binding

| Field | Value |
|---|---|
| Owner | **Operations Lead** (accountable). Performance Owner consulted for CAP-006. |
| Mechanism | Each successful firing of the SLA sweep **and** the outbox drainer (1) emits one structured JSON log line via existing `configure_logging`, and (2) writes ISO-8601 UTC timestamp to a host-visible marker file. |
| Marker paths | `/var/log/ecmp/cm-sla-sweep.last_ok` · `/var/log/ecmp/cm-outbox-drain.last_ok` |
| Alert rule | Marker age **> 2 hours** (2× hourly cadence / C-3) = silent-death incident — same severity class as missing backup dumps. Log-only without marker is **not** sufficient (Counter-Evidence on backup). |
| Skip / fail | Lock-held skip (`exit 0`) does **not** refresh the marker. Non-zero exit does **not** refresh the marker. |

---

## Gate 2 — Business

| ID | Criterion | Verdict | Evidence |
|---|---|---|---|
| G2.1 | DEC-031 §7a signed | **PASS** | rbxhut 2026-08-23 |
| G2.2 | DEC-031 §7b signed | **PASS** | Accepted with Conditions; AR-20260823-01 |
| G2.3 | Reachability Limit in writing | **PASS** | DEC-031 §7b + C-2 + C-6 (in-app only) |
| G2.4 | Detection-lag number | **PASS** | **C-3 = 1 hour** |

---

## Gate 3 — Technical (definitions before code)

| ID | Criterion | Verdict | Definition |
|---|---|---|---|
| G3.1 | Single SLA implementation | **PASS** | Call `resolve_complaint_sla` in `backend/app/modules/cm_batch1/sla.py` only. No duplicate formula in the CLI. |
| G3.2 | Expiry / threshold predicate | **PASS** | Persist/read `created_at`, `closed_at`, `status`. Derive `due_at = created_at + COMPLAINT_RESOLUTION_TARGET_DAYS`. Open rows only (`status != CLOSED`). Threshold instants: `due_at - 7d` (H7), `due_at - 3d` (H3), `due_at - 1d` (H1), `due_at` (BREACH). Select candidates with SQL bounded by `COMPLAINT_SLA_SWEEP_BATCH_LIMIT` (default **100**), ordered oldest `created_at` first. Shape mirrors `list_expired_open_staging`. |
| G3.3 | Eligibility | **PASS** | Fire **once per** `{complaintId, threshold}` for thresholds **H7, H3, H1, BREACH** when `now >= threshold_at` and not yet recorded (idempotency). Audience: durable Audit/Timeline/Outbox + existing in-app surfaces (`SlaAlertsPanel` / list badge consumers with `dashboard:read` / `complaints:read`). **No** external channel. |
| G3.4 | Idempotency key | **PASS** | Fixed before code: `cm-sla:{complaintId}:RESOLUTION:{threshold}` where `threshold ∈ {H7,H3,H1,BREACH}`. Relies on `OutboxRepository.enqueue` uniqueness (`exists_idempotency_key` → `None`). |
| G3.5 | Retry | **PASS** | No in-process backoff. Failed run exits non-zero; next hourly firing re-evaluates. Recovery latency ≤ **1 hour** (C-3). |
| G3.6 | Auditability | **PASS** | All emissions through `CmBatch1SideEffectRecorder` (Audit + Timeline + Outbox one transaction), same as staging void sweep. |
| G3.7 | Concurrency | **PASS** | `flock` on `/var/lock/ecmp-cm-sla-sweep.lock` (sweep) and `/var/lock/ecmp-cm-outbox-drain.lock` (drainer). Lock held → structured `skipped=lock_held`, **exit 0**, marker **not** refreshed. |

---

## Gate 4 — Delivery

| ID | Criterion | Verdict | Evidence |
|---|---|---|---|
| G4.1 | Delivery mechanism | **PASS (narrowed)** | CAP-005 remains stub. Scope explicitly **in-app + durable record** per C-6 / G2.3. |
| G4.2 | EVT-004 publication | **PASS (path chosen)** | **C-4:** schedule outbox drainer under same pattern. Drainer is **in authorized coding scope**; not yet implemented. |
| G4.3 | Reuse infrastructure | **PASS** | Existing image, session factory, logging, outbox, `sla.py`. |
| G4.4 | Tests defined | **PASS** | Required before merge: (1) predicate/eligibility unit tests for H7/H3/H1/BREACH; (2) second firing emits nothing (idempotency); (3) lock-held skip; (4) failure → non-zero + structured error line. Map to **TC-030** (breach) + new TC ids for H-thresholds in the same PR. |
| G4.5 | Runbook + deploy standard | **PASS** | [`../../15 Operations Runbook/ECMP_CM_Batch1_SLA_Sweep_v0.1.md`](../../15%20Operations%20Runbook/ECMP_CM_Batch1_SLA_Sweep_v0.1.md) (OPS-CM-B1-SLA-001); pointer in `14 Deployment Standards/README.md`. **Crontab not installed** until coding + ops provision. |

---

## Verdict

**ALL GATES PASS.** FR-030 / DEC-031 Fase 2 engineering is **AUTHORIZED WITH SCOPE** as listed above.

Next act (separate from this pack): implement CLI + tests + runbook provisioning; then ops installs hourly crontab under `flock` + heartbeat markers.

## Sign-off

- Architecture Review Board: **rbxhut** — 2026-08-23
- Solution Architect / Tech Lead (gate exit): recorded with this pack — 2026-08-23

---

*End of GOV-AR-CAP006-002-IGATE / IG-20260823-01.*
