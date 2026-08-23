# ADR-CAP006-002 — Time Source Fulfillment Pattern

| Field | Value |
|---|---|
| ID | ADR-CAP006-002 |
| Version | 0.3.2 |
| Owner | Solution Architect |
| Reviewer | Architecture Review Board |
| Approver | Architecture Review Board |
| Status | 🟢 **Accepted with Conditions** (AR-20260823-01) — **CAP006-BLK-001 lifted**; FR-030 engineering **NOT authorized** until Implementation Gate 1–4 |
| Last Review | 2026-08-23 |
| Next Review | 2026-10-01 |
| Capability | CAP-006 (SLA Measurement & Breach Detection) |
| FR | FR-030 |
| Trace | TRC-L-007 |

- ADR Status: **Accepted with Conditions**
- Date: 2026-08-23 (Accept recorded)
- Decision Owners: Solution Architect · Architecture Review Board (Approver: rbxhut)
- Related Domains: KPI & Performance · Core Platform (outbox) · Notification
- Answers: **CAP006-BLK-001** (B2-24) — *"Time Source fulfillment pattern is NOT SPECIFIED"*
- Governed by: ARC-CAP006-001 (Time Source, Accepted) · ADR-CAP006-001 (Hybrid, Accepted) · ARC-CAP006-002 (Runtime Architecture, Accepted)

> **ARB decision (AR-20260823-01, 2026-08-23).** Architecture Review Board **Accepted with
> Conditions** this ADR v0.2 as the Time Source fulfillment pattern. Evidence:
> `../deploy/evidence/B2-25_CAP-006_ADR-CAP006-002_Accept_With_Conditions_20260823.md`.
> **CAP006-BLK-001 is lifted.** B2-24 is not amended; its condition is discharged on the
> non-invent branch. FR-030 engineering remains **not authorized** until Implementation
> Gate 1–4 pass, including the binding conditions below. CAP-005 stays stubbed.

## Binding Conditions (ARB 2026-08-23)

| ID | Condition | When it binds |
|---|---|---|
| C-1 | Positive heartbeat (§Decision 8) is mandatory: named owner + named mechanism before FR-030 engineering opens (Gate 1 / G1.4). Silence must not look like compliance. **Closed IG-20260823-01:** Owner = Operations Lead; mechanism = JSON log + marker files `/var/log/ecmp/cm-sla-sweep.last_ok` and `cm-outbox-drain.last_ok`; stale if age > 2h. | Gate 1 — **closed** |
| C-2 | Business notified in writing of the Reachability Limit before DEC-031 §7b is treated as Fase-2 delivery (Gate 2 / G2.3). Accept supplies the **trigger**, not SMTP/Twilio/FCM. | Gate 2 — recorded in DEC-031 §7b |
| C-3 | Detection-lag tolerance = **1 hour** (Gate 2 / G2.4). Cadence starting value: hourly host schedule (ADR §Decision 4). Recorded 2026-08-23 by ARB signatory. | Gate 2 — **closed** |
| C-4 | `EVT-004` publication path = **schedule an outbox drainer under this same pattern** (Gate 4 / G4.2). Write-only rejected. Recorded 2026-08-23 by ARB signatory. | Gate 4 — **closed** (path chosen; drainer not yet built) |
| C-5 | Failed backup schedule (20-byte dumps since 2026-08-02) is repaired **independently** of CAP-006. Operations defect; must not be bundled into this ADR or wait on FR-030. | Independent ops ticket |
| C-6 | In-app alert eligibility (Gate 3 / G3.3): fire **once per threshold per complaint** at remaining **7**, **3**, and **1** calendar days before `due_at`, plus breach at `due_at`. **In-application surface only** — no SMTP/Twilio/FCM (CAP-005 stays stubbed). DEC-031 Fase 1 read-time 80% badge threshold is unchanged until a later DEC. Recorded 2026-08-23. | Gate 2/3 — **closed** (eligibility named; engine not built) |

---

## Context

Three layers of CAP-006 are Accepted: the **concept** (ARC-CAP006-001 Time Source), the **mechanism class** (ADR-CAP006-001 Hybrid — time stimulus *and* lifecycle events), and the **conceptual runtime** (ARC-CAP006-002). One layer is missing, and it blocks everything below it:

> **CAP006-BLK-001** — Time Source **fulfillment pattern** is **NOT SPECIFIED** (B2-23). CAP-006 delivery stays Deferred *"until a future architecture artifact **Accepts** a fulfillment pattern from **non-invent** repository evidence, **or** Board explicitly invent-authorizes."*

B2-17E set the bar precisely: the Board rejected "Job" not because a job is wrong, but because *"only the word 'job' [appears] in FRD §8; no job/scheduler design in repo; Accepting would require **inventing** scheduler/poll/store."*

This ADR does not ask for an invention licence. It argues that the pattern is **already committed, already documented as an Active operating procedure, and already executing in the target environment**, and asks the Board to name it.

### What triggered the submission

DEC-031 set a 30 calendar-day resolution target and delivered its Fase 1 — measurement and in-app alerts computed at read time, no scheduler involved. Fase 1 covers the officer who opens ECMP. It cannot cover the one who does not: nothing reaches a person at the moment a threshold is crossed. Business asked for exactly that (DEC-031 §3 Fase 2). Fase 2 needs a time trigger, and a time trigger needs this ADR.

## Decision Drivers

1. **Non-invent is the binding constraint.** Any pattern that cannot be sourced to something already in the repository fails the B2-22 gate on arrival.
2. **The gap is not CAP-006's alone.** ADR-009 mandates a transactional outbox for durable event emission. The outbox exists (`cm_batch1_outbox`) and **nothing in the root stack drains it** — 262 rows sit `UNPUBLISHED`, occurred 2026-08-17 … 2026-08-22 (verified on the lab database 2026-08-23). A drainer needs a time trigger too. The missing pattern is therefore an **existing architectural debt**, not a new CAP-006 requirement.
3. **ADR-009 must not be reopened.** No broker, no generic retry/DLQ publisher.
4. **ADR-003 configuration-first.** Cadence must be configuration, never compiled in.
5. **Smallest thing that discharges the requirement.** ARC-CAP006-001 §6 keeps scheduler *implementation* out of the concept; this ADR must specify a pattern without becoming a framework.

## Options Considered

### Option A — In-process background thread / asyncio task in the API container

- Pros: no new deployment unit; nothing to install.
- Cons: fires once per replica, so N replicas evaluate N times — needs locking the repo has no pattern for; dies silently with the worker; unobservable; not sourced to anything in the repository. **This is the invention B2-17E refused.**

### Option B — Dedicated worker container (celery / rq / dramatiq / arq)

- Pros: the conventional answer; mature libraries.
- Cons: none of those libraries is a dependency ([`requirements.txt`](../backend/requirements.txt) has no scheduler of any kind); a worker service would be a new deployment unit in `docker-compose.prod.yml`; brokers of this class edge into ADR-009 territory. **Pure invent — fails B2-22.**

### Option C — Scheduled Command Invocation (host scheduler → committed CLI command → existing application service) ✅

An operating-system scheduler invokes a **plain command already shipped in the backend image**. The command opens a session, calls the existing application service, prints a structured line, and exits with a code. No daemon, no library, no broker, no new container, no new deployment unit.

- Pros: **already the committed, documented and executing pattern in this repository** (see Evidence); one process per firing so no replica fan-out; the command is testable by calling it directly; cadence is configuration; identical shape serves the outbox drainer that ADR-009 already implies.
- Cons: cadence granularity bounds detection latency; the schedule lives in host configuration rather than in the repository; requires the host to have a scheduler (it does); **the pattern's real-world failure mode in this very repository is silent death — see Counter-Evidence.**

## Evidence that Option C is non-invent

All rows verified on the lab/VPS host and the running `ecmp-prod` stack on **2026-08-23**.

| # | Evidence | What it establishes |
|---|---|---|
| 1 | [`backend/scripts/cm_batch1_ops_hygiene.py`](../backend/scripts/cm_batch1_ops_hygiene.py) — committed `argparse` CLI; `_configure()` loads `get_settings()` + `configure_logging`; each sub-command opens `get_session_factory()()`, delegates to an existing application service, prints a structured line, closes the session, returns an exit code (`0` OK / `2` failed) | **The exact shape this ADR proposes is already written, committed and unit-tested** (`backend/tests/test_cm_batch1_ops_hygiene.py`). Nothing about the shape is invented. |
| 2 | `cm_batch1_ops_hygiene.py void-abandoned-staging` → `CmBatch1AttachmentService.void_abandoned_staging` → `CmBatch1AttachmentRepository.list_expired_open_staging(now=…)`, whose predicate is `status == "OPEN" AND expires_at < now` | **A time-threshold expiry sweep executed by a scheduled command already exists in this repository.** It is the same computational act CAP-006 needs — "find the rows whose deadline passed while nobody was looking" — differing only in which deadline is read. |
| 3 | The same sweep calls `self._side_effects.record(...)` → `CmBatch1SideEffectRecorder` → **Audit + Timeline + Outbox in one session** | **A command-invoked sweep already emits durable domain events through the ADR-009 outbox.** The emit half of RS-06 is not a new capability; it is exercised today by a non-HTTP caller. |
| 4 | [`15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md`](../15%20Operations%20Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md) — OPS-CM-B1-STG-001, **Status 🟢 Active (Mode A)**, with a **Cadence** table (*"Shared / SIT: Daily or via ops cron when host capacity allows"*) and documented exit codes and JSON log fields | **Scheduling an ECMP application command on a cadence is already an Active, governed operating procedure** — written before this ADR, for a different capability. |
| 5 | Live: `docker compose exec -T -w /app backend python scripts/cm_batch1_ops_hygiene.py probe-storage` → `storageProbe ok=True root=/app/storage/attachments exists=True writable=True detail=writable`, exit `0` (executed 2026-08-23 against the running `ecmp-backend` container) | **The pattern runs today**, in the deployed image, without any change to the stack. `/app/scripts/` is present in the image via the Dockerfile `COPY . .`. |
| 6 | [`deploy/backup-postgres.sh`](../deploy/backup-postgres.sh) — committed command, `set -euo pipefail`, reads `ECMP_BACKUP_DIR` / `ECMP_BACKUP_KEEP_DAYS` from environment; [`deploy/README.md`](../deploy/README.md) §Backup documents it | The "scheduled command reading its parameters from configuration" shape is **committed and documented** |
| 7 | Host **root crontab**: `15 2 * * * /opt/ECMP/deploy/backup-postgres.sh >> /var/log/ecmp-backup.log 2>&1`; `/etc/cron.d/` additionally carries `docker-builder-prune`, `monarx-update`, `sysstat`, `e2scrub_all`; 12 systemd timers active | **An ECMP repository command is already scheduled by the host scheduler in the target environment.** The scheduler is present, running, and already owns an ECMP workload. |
| 8 | `flock` present on the host (`/usr/bin/flock`) **and inside the backend image** (`util-linux` installed by [`backend/Dockerfile`](../backend/Dockerfile)) | The overlap-prevention primitive the pattern needs **is already installed**; no library, no lock table, no new dependency. |
| 9 | `cm_batch1_outbox`: 262 rows `UNPUBLISHED`, occurred 2026-08-17 … 2026-08-22; `outbox_repository.py` exposes `list_unpublished()` but **no non-test caller exists in `backend/`** (the only `drain_outbox` lives in `implementation/backend`, which is ⚫ Historical and drains via a DEV HTTP route, not a schedule) | A scheduled command is **already required** by Accepted ADR-009, independent of CAP-006 |
| 10 | ADR-003 Configuration-First | Cadence-as-configuration is **existing policy**, not a new principle |

Rows 1–5 supply the application-level mechanism and prove it executes. Rows 6–8 supply the host-level scheduling and mutual exclusion. Row 9 supplies a motive that predates CAP-006. Nothing above was written for this ADR.

## Counter-Evidence — what the same pattern actually does when it breaks

Honesty requires recording the failure this audit found, because it lands on the exact workload CAP-006 cares about most.

The scheduled backup in Evidence #6/#7 has **failed on every firing since 2026-08-02** — 21 consecutive days at the time of writing:

- `backups/ecmp_2026080[2-9]…` through `ecmp_20260823T021501Z.sql.gz` are each **20 bytes** (gzip of empty input). The last good cron dump is `ecmp_20260801T021501Z.sql.gz` (33 KB).
- Root cause is configuration drift, not the pattern: `docker compose … --env-file .env.prod` aborts with *"required variable PGADMIN_DEFAULT_PASSWORD is missing a value"*, so `pg_dump` never runs and `gzip` compresses nothing.
- The script behaved correctly: `set -euo pipefail` aborted the run. Proof — the failed files carry mode `0644` because the script exited **before** its `chmod 600`, and the retention prune never ran either.
- The failure was written to `/var/log/ecmp-backup.log` on every firing. **Nobody read it for three weeks.**

Two conclusions follow, and both are load-bearing for this decision:

1. **"Failure is visible in the host's job log" is not observability.** A log nobody reads is indistinguishable from silence. Version 0.1 of this ADR listed log-visibility as a Pro; that claim is withdrawn.
2. **This failure mode is uniquely dangerous for SLA notification.** A dead backup job is discovered at restore time. A dead SLA job produces *no alerts*, which is byte-for-byte what a compliant month looks like. The pattern cannot host CAP-006 without a positive-heartbeat requirement — an absence of runs must be detectable, not merely a failure of one run.
3. A secondary, security-relevant artifact: because the abort happens before `chmod 600`, a **partially** successful dump would be left world-readable at the default umask. The mitigation belongs in the command contract (§Decision 9), not in CAP-006.

## Decision

Adopt **Scheduled Command Invocation** as the Time Source fulfillment pattern, subject to the conditions below.

1. **Shape.** A host scheduler invokes a committed command inside the existing backend image on a configured cadence. The command opens a session, delegates to the existing application service, emits a structured line, and exits with a code. It is a **caller**, never a home for business logic — breach decision stays in KPI, clock attributes stay in ECMF, config stays in Administration (ARC-CAP006-001 §7 unchanged). The reference implementation of this shape is `backend/scripts/cm_batch1_ops_hygiene.py`; CAP-006's command must not diverge from it.
2. **No new runtime unit.** The command ships inside the existing backend image and is invoked through it (`docker compose exec` or the equivalent `run --rm`). **No worker service is added to `docker-compose.prod.yml`.**
3. **No library.** No celery / apscheduler / rq / dramatiq / arq enters `requirements.txt`. The scheduler is the operating system's.
4. **Execution frequency is configuration** (ADR-003), expressed in two independent places that must agree:
   - the **host schedule** (crontab entry) determines when the process starts;
   - an application setting bounds what one firing may do (batch limit).
   The cadence is **not** derived from the SLA target. Selection rule: the interval is the largest value that keeps worst-case detection lag within business tolerance, since detection lag ≤ one interval (§8). For DEC-031's 30-day target and a day-granular warning threshold, an **hourly** firing is sufficient and is the recommended starting value; it is a configuration change, not a code change, to move it.
5. **Duplicate execution is prevented at two levels, and both are required.**
   - **Overlap (process level):** the command runs under `flock` on a fixed lock path (Evidence #8). A firing that finds the lock held exits `0` with a `skipped=lock_held` line. No lock table, no new dependency.
   - **Re-emission (data level):** duplicate suppression does **not** depend on the lock. `OutboxRepository.enqueue` already refuses a row whose `idempotency_key` exists, returning `None`, and `CmBatch1SideEffectRecorder.record` already claims that key **before** writing Audit/Timeline. CAP-006's `idempotency_key` must therefore be derived from `caseId` + `slaId` + threshold, so a repeated firing, a manual re-run, or a retried deploy cannot emit `EVT-004` twice. This restates FRD-005's existing idempotency requirement; it is not a new rule.
6. **Retry is by next firing, not by in-process backoff.** A failed run does not retry itself. It exits non-zero and leaves the work undone; the next scheduled firing re-evaluates from current state and picks it up, because the sweep is a *predicate over current data*, not a queue of pending items. This is deliberate: in-process retry/backoff is precisely the "generic publisher framework" ADR-009 §4 forbids. Consequence: recovery latency after a failure is one cadence interval.
7. **Failure is recorded, not merely logged.** Every firing writes one structured JSON line through `configure_logging` (the mechanism OPS-CM-B1-STG-001 already relies on) carrying at minimum: run id, start/end timestamps, evaluated count, emitted count, skipped-duplicate count, error count, and outcome. Non-zero exit codes follow the existing convention (`0` OK, `2` operational failure).
8. **Observability requires a positive heartbeat.** Given the Counter-Evidence, a Accept of this pattern for CAP-006 is conditional on the *absence* of successful runs being detectable — the last-successful-run timestamp must be observable by operations, not inferred from silence. The mechanism (a readable last-run record and its surfacing) is an operations deliverable specified in the Implementation Gate, not invented here.
9. **Security posture is inherited, not extended.** The command runs as the existing container user with the existing database credentials from the existing environment; it opens **no port**, adds **no HTTP surface**, and accepts **no network input**. It must not write secrets to stdout or to any file, and any file it creates must have its mode set before content is written, not after (the failure in the Counter-Evidence). Host-side, the schedule entry must not carry credentials inline.
10. **Detection granularity is bounded by cadence and is accepted.** "Near real-time" in ADR-001 is satisfied to within one scheduling interval. A breach is detected on the next firing after `dueAt`, not at the instant of `dueAt`. Business consequence: a warning or breach alert may lag the threshold by up to one interval.
11. **Same shape serves the outbox drainer.** One pattern, two callers. Adopting it gives the ADR-009 debt in Evidence #9 a sanctioned home.

## Non-scope (unchanged by this ADR)

1. **No message broker; no generic retry/DLQ publisher** — ADR-009 stands untouched.
2. **No new Event Catalog entry.** `TimeTick` / `DueReached` remain rejected as invent (ARC-CAP006-001 §6.4). `EVT-004` stays the only breach event.
3. **No business API for "time" or "force evaluate"** as a product surface.
4. **No Business Rule change.** BR-005 / DEC-004 / DEC-005 / the definition of breach are untouched. DEC-031 sets the *target value*; this ADR sets only *how time is observed*.
5. **No change of ownership.** Time Source remains a KPI runtime concern.
6. **Not an implementation authorization by itself.** Accepting this ADR specifies the pattern and closes CAP006-BLK-001. FR-030 engineering still needs its own sprint gate.
7. **Delivery transport stays deferred.** CAP-005 remains stubbed. This ADR supplies the *trigger*, not the *channel* — see the Reachability Limit below.
8. **No change to DEC-031's scope.** Fase 1 stays as delivered; this ADR adds no field, no status, and no target.

## Reachability Limit — what Fase 2 can and cannot do if this is Accepted

Version 0.1 claimed that Accepting this ADR makes DEC-031 Fase 2 "reachable". That overstates it, and the audit shows why. Accepting the pattern supplies **only the trigger**. The path from trigger to a human is still cut in two places:

| Link | State verified 2026-08-23 | Consequence |
|---|---|---|
| Trigger | This ADR (Proposed) | Supplied on Accept |
| Breach detection + `EVT-004` write | Outbox write path exists and works (Evidence #3) | Available |
| `EVT-004` **publication** | Nothing drains `cm_batch1_outbox` in the root stack; 262 rows `UNPUBLISHED` (Evidence #9) | `EVT-004` would be **written but never published** |
| Notification **channel** | `StubNotificationProvider` only — *"no SMTP / Twilio / FCM / webhook"*; `notification_queue` holds **0 rows**; CAP-005 production engine is **Stay Deferred** | Email / SMS / push **cannot** be sent |
| In-app surface | DEC-031 Fase 1 delivered `SlaAlertsPanel`, computed at read time; there is no notification inbox feature in `frontend/src/features/` | An off-screen officer is still not reached |

**Therefore:** with this ADR Accepted and CAP-005 still stubbed, a firing can compute breaches and write durable rows — but *"memberi tahu petugas tanpa ada orang membuka halaman"* (DEC-031 §3 Fase 2) **remains unachievable**. That sentence of DEC-031 depends on CAP-005, not on this ADR. The Board should Accept this ADR on its own merits as the Time Source pattern, and Business should be told plainly that Fase 2's proactive half needs the CAP-005 gate as well.

## Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Scheduled job dies silently; absence of alerts reads as compliance | **HIGH** — realized today on the backup job | §Decision 8 positive heartbeat; Gate 1 exit criterion |
| R2 | Schedule lives in host config, so a host rebuild loses it with no repository signal | MEDIUM | Provisioning step recorded in `14 Deployment Standards` + `15 Operations Runbook` on Accept |
| R3 | Overlapping firings double-emit | MEDIUM | `flock` (§5) **and** outbox idempotency key (§5); the second is authoritative |
| R4 | Config drift breaks the command exactly as it broke the backup | MEDIUM | Command reads settings through `get_settings()` inside the image, not through host compose interpolation — the drift class that killed the backup does not apply |
| R5 | Cadence chosen too aggressively turns a sweep into a poll under load | LOW | Batch limit in configuration (§4); cadence is a config change |
| R6 | `EVT-004` accumulates unpublished, repeating the ADR-009 debt at higher volume | MEDIUM | Drainer scheduled under the same pattern (§11); or Board accepts write-only emission explicitly |
| R7 | Business reads "blocker cleared" as "notifications delivered" | MEDIUM | §Reachability Limit; DEC-031 §7b note |

## Migration & Deployment Impact

- **Database:** none. No table, no column, no Alembic revision required by the pattern itself.
- **Image:** none. `scripts/` is already copied into the backend image; `flock` is already installed.
- **Compose:** none. No service added, no port opened, no volume added.
- **Host:** one crontab entry, one lock path, one log destination. This is the *only* environmental change, and it is the same class of change already made for `backup-postgres.sh`.
- **Rollback:** remove the crontab entry. The pattern has no residue — no daemon to stop, no queue to drain, no schema to revert. Detection simply stops and the system returns to DEC-031 Fase 1 read-time behaviour. A second, finer lever: the command's own enable/batch settings can be set to zero without touching the schedule. Emitted `EVT-004` rows already written are not withdrawn by rollback; they are durable domain facts.
- **Reversibility grade:** the deployment change is fully reversible; the data written by a firing is not, by design.

## Acceptance Criteria (for the ADR, not for the implementation)

This ADR may be Accepted when the Board is satisfied that:

- [ ] AC-1 — Every Evidence row 1–10 is independently verifiable in the repository or the target host; none rests on documentation alone.
- [ ] AC-2 — No new scheduler, library, worker, container, broker, port, or queue is introduced by §Decision.
- [ ] AC-3 — ADR-009 is not reopened: no generic retry/backoff/DLQ publisher is specified.
- [ ] AC-4 — ADR-003 is honoured: cadence and batch bounds are configuration.
- [ ] AC-5 — Duplicate suppression is sourced to the existing `idempotency_key` claim, not to a new mechanism.
- [ ] AC-6 — The Counter-Evidence failure mode is addressed by a stated, non-optional condition (§Decision 8).
- [ ] AC-7 — The Reachability Limit is understood and recorded, so that Accept is not mistaken for delivery of DEC-031 Fase 2.
- [ ] AC-8 — Non-scope §1–8 hold: no Business Rule, Event Catalog, FRD, or API surface changes.

## Implementation Gate (applies only after ARB Accept)

Accepting this ADR closes CAP006-BLK-001. It does **not** authorize FR-030 engineering (Non-scope §6). Engineering opens only when all four gates below are passed and recorded.

**Recorded PASS:** [`../18 Architecture Governance/reviews/ECMP_ADR_CAP006_002_Implementation_Gate_Pack_v1.0.md`](../18%20Architecture%20Governance/reviews/ECMP_ADR_CAP006_002_Implementation_Gate_Pack_v1.0.md) (IG-20260823-01) · evidence [`../deploy/evidence/B2-26_CAP-006_Implementation_Gate_Pass_20260823.md`](../deploy/evidence/B2-26_CAP-006_Implementation_Gate_Pass_20260823.md). FR-030 engineering is **AUTHORIZED WITH SCOPE** (in-app H-7/H-3/H-1 + breach + outbox drain; no CAP-005).

### Gate 1 — Architecture

- [x] G1.1 Existing execution pattern verified against Evidence #1–#8 at the time of the sprint (not assumed from this document).
- [x] G1.2 No new scheduler, worker, broker, library, container, or port introduced by the proposed change.
- [x] G1.3 ADR-CAP006-002 recorded **Accepted** by ARB per `18 Architecture Governance` ADR Lifecycle §3; ADR index regenerated.
- [x] G1.4 Positive-heartbeat requirement (§Decision 8) has a named owner and a named mechanism.
- [x] G1.5 Capability Register, TRC-L-007, and the B2-24 blocker record updated to reflect the Accept — with the Accept evidence cited.

### Gate 2 — Business

- [x] G2.1 DEC-031 §7a confirmed signed (Business Owner, 2026-08-23) — **already satisfied**.
- [x] G2.2 DEC-031 §7b signed by ARB, or explicitly recorded as not required for the scope actually being built.
- [x] G2.3 Business informed in writing of the Reachability Limit: with CAP-005 stubbed, Fase 2 delivers detection and durable records, **not** off-screen notification.
- [x] G2.4 Business tolerance for detection lag (§Decision 10) stated as a number, so the cadence in §Decision 4 can be justified rather than guessed.

### Gate 3 — Technical

- [x] G3.1 SLA calculation defined — reuse `backend/app/modules/cm_batch1/sla.py` (`resolve_complaint_sla`) unchanged; the command must not carry a second implementation of the rule.
- [x] G3.2 Expiry detection defined — a repository predicate over persisted columns in the shape of `list_expired_open_staging` (`status open AND due_at < now`), evaluated in SQL, bounded by the configured batch limit.
- [x] G3.3 Notification eligibility defined — which thresholds fire (warning at `COMPLAINT_SLA_WARNING_PERCENT`, breach at `due_at`), for whom, and once per threshold per complaint.
- [x] G3.4 Idempotency defined — `idempotency_key` composition fixed and written down before code; verified against `OutboxRepository.enqueue`'s existing uniqueness claim.
- [x] G3.5 Retry / failure handling defined per §Decision 6 — next-firing recovery, no in-process backoff; recovery latency stated.
- [x] G3.6 Auditability defined — the sweep writes through `CmBatch1SideEffectRecorder` so Audit + Timeline + Outbox stay in one transaction, as the existing sweep already does.
- [x] G3.7 Concurrency defined — `flock` path fixed; behaviour on lock-held is exit `0` with an explicit skip reason.

### Gate 4 — Delivery

- [x] G4.1 Delivery mechanism verified. **Currently FAILING:** `StubNotificationProvider` only; `notification_queue` empty; CAP-005 production engine Stay Deferred. Either CAP-005 opens, or the sprint scope is explicitly narrowed to in-app/durable-record only and G2.3 is signed.
- [x] G4.2 `EVT-004` publication path decided — either the outbox drainer is scheduled under the same pattern (§Decision 11), or write-only emission is explicitly accepted with the 262-row precedent acknowledged.
- [x] G4.3 Existing infrastructure reused: existing image, existing session factory, existing logging, existing outbox, existing SLA module. Any new component requires its own justification against B2-22.
- [x] G4.4 Tests defined — unit tests for the sweep predicate and eligibility; an idempotency test proving a second firing emits nothing; a lock-held test; a failure test asserting non-zero exit and a structured error line. Test IDs mapped to TC-030.
- [x] G4.5 Runbook + deployment standard updated with the provisioning step, in the shape of OPS-CM-B1-STG-001.

## Follow-up Actions (on Accept, not before)

- [ ] Record Accept as evidence; lift CAP006-BLK-001 in the Capability Register and TRC-L-007
- [ ] Update `04 Solution Architecture` with the runtime shape
- [ ] Update `14 Deployment Standards` + `15 Operations Runbook` with the provisioning step and the heartbeat check
- [ ] Open the FR-030 engineering gate as a separate sprint decision, gated on §Implementation Gate
- [ ] Schedule the outbox drainer under the same pattern (ADR-009 debt, Evidence #9)
- [ ] Revisit CAP-005 for delivery transport — trigger without channel reaches no one off-screen
- [ ] **Separately and independently of CAP-006:** repair the failed backup schedule (Counter-Evidence). It is an operations defect, not an architecture question, and it should not wait on this ADR.

## Related Documents

- `./ARC-CAP006-001_Time_Source.md` · `./ARC-CAP006-002_Runtime_Architecture.md` · `./ADR-CAP006-001_Evaluation_Mechanism.md`
- `./ECMP_ADR_003_Configuration_First_Principle_v1.0.md` · `./ECMP_ADR_009_Message_Broker_Deferral_v1.0.md` · `./ECMP_ADR_009_Addendum_G2_InProcess_Extension_v1.0.md`
- `../15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md` (OPS-CM-B1-STG-001, Active)
- `../deploy/evidence/B2-22_CAP-006_Concrete_Runtime_Non_Invent_Gate_20260801.md`
- `../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md`
- `../deploy/evidence/B2-24_CAP-006_Stay_Deferred_Confirmation_Blocker_Freeze_20260804.md`
- `../27 Project Decisions/DEC-031_SLA_Resolution_Target_30_Calendar_Days_v0.1.md`
- `../03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` (FRD-005 🔒 LOCKED)

## Document History

| Ver | Date | Change |
|---|---|---|
| 0.1 | 2026-08-23 | Proposed — Scheduled Command Invocation submitted against CAP006-BLK-001, sourced to committed backup script, documented lab cron, live host cron entries, and the undrained ADR-009 outbox |
| 0.2 | 2026-08-23 | Audit revision. Added Evidence #1–#5 and #8 (`cm_batch1_ops_hygiene.py` CLI, its time-threshold expiry sweep, its outbox emission, the Active OPS-CM-B1-STG-001 runbook cadence, live execution in the running container, `flock` availability) — the application-level half of the pattern, absent from v0.1. Corrected Evidence #7: the ECMP backup schedule is in the **root crontab**, not `/etc/cron.d/`. Added **Counter-Evidence**: the cited backup schedule has failed silently for 21 consecutive days; the v0.1 claim that log-visibility constitutes observability is **withdrawn**, and a positive-heartbeat condition added (§Decision 8). Specified execution frequency, duplicate prevention, retry, failure recording, security, and rollback. Added **Reachability Limit** replacing v0.1's overstated claim that Accept makes DEC-031 Fase 2 reachable. Added Risks, Migration & Deployment Impact, Acceptance Criteria, and the four-gate Implementation Gate. Status remains **Proposed**; ARB Accept **not** granted. |
| 0.3 | 2026-08-23 | ARB **Accepted with Conditions** (AR-20260823-01). CAP006-BLK-001 lifted. Binding C-1…C-5 recorded; C-3 number and C-4 publication path left **open** (required before Gate 2/4 and before FR-030 code). No engine code in this revision. |
| 0.3.1 | 2026-08-23 | Conditions addendum (same Accept): **C-3 = 1 hour**; **C-4 = outbox drainer under same pattern**; **C-6 = in-app alerts at H-7 / H-3 / H-1 + breach** (no CAP-005). C-1 owner/mechanism still open. No engine code. |
| 0.3.2 | 2026-08-23 | Implementation Gate **PASS** (IG-20260823-01 / B2-26). C-1 closed (Operations Lead + marker files). FR-030 engineering **AUTHORIZED WITH SCOPE**. No engine code in this revision. |

---

*ADR-CAP006-002 v0.3.2 — Accepted with Conditions; Implementation Gate PASS. FR-030 engineering authorized with scope (in-app + drain; no CAP-005).*
