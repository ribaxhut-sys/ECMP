# ADR-CAP006-002 — ARB Decision Package (CAP006-BLK-001)

| Field | Value |
|---|---|
| ID | GOV-AR-CAP006-002 |
| Review ID | AR-20260823-01 |
| Version | 1.0 |
| Subject | [`05 Architecture Decision Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md`](../../05%20Architecture%20Decision%20Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md) v0.2 |
| Subject Status at Review | 🟡 **Proposed** — ARB Accept **not** granted |
| Review Type | Architecture Board decision on a submitted ADR (RACI: A = Architecture Board, R = Solution Architect) |
| Requester | Solution Architect |
| Reviewers | Architecture Review Board · Security (consulted — §5) · Performance Owner (CAP-006) · PMO (informed) |
| Owner | Architecture Board Chair |
| Approver | Architecture Review Board |
| Status | 🟢 **COMPLETE** — Accepted with Conditions (2026-08-23); **CAP006-BLK-001 lifted**; FR-030 eng **NOT authorized** |
| Prepared | 2026-08-23 |
| Blocker in scope | **CAP006-BLK-001** (frozen by B2-24, GOV-B2-24-GOV-001) |

> **Decision recorded 2026-08-23.** Outcome **B — Accepted with Conditions** (exactly one §8
> box). Signatory **rbxhut**. Evidence: `../../deploy/evidence/B2-25_CAP-006_ADR-CAP006-002_Accept_With_Conditions_20260823.md`.
> **CAP006-BLK-001 is lifted.** ADR-CAP006-002 is **Accepted with Conditions** (v0.3.1).
> DEC-031 §7b is signed with the Reachability Limit. Follow-up same day: **C-3 = 1h**,
> **C-4 = outbox drain**, **C-6 = in-app H-7/H-3/H-1**. **FR-030 engineering remains NOT
> authorized** until Implementation Gate 1–4 (C-1 heartbeat owner/mechanism still open).

---

## 1. Decision Requested

> **Does the Board Accept [`ADR-CAP006-002`](../../05%20Architecture%20Decision%20Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md) v0.2 — *Time Source Fulfillment Pattern: Scheduled Command Invocation* — as the architecture artifact that satisfies the condition B2-24 placed on CAP006-BLK-001, thereby lifting that blocker?**

B2-24 §3 states the condition verbatim:

> *"CAP-006 engine delivery remains Planned / Stay Deferred until a **future** architecture artifact **Accepts** a fulfillment pattern from **non-invent** repository evidence, **or** Board explicitly invent-authorizes."*

ADR-CAP006-002 is submitted on the **first** branch of that sentence — non-invent repository
evidence. **No invent authorization is requested.** B2-24 is not amended, reinterpreted, or
reopened by this package; its condition is taken exactly as written and answered on its own terms.

B2-17E set the evidentiary bar when it refused "Job": the Board rejected it because *"only the
word 'job' [appears] in FRD §8; no job/scheduler design in repo; Accepting would require
**inventing** scheduler/poll/store."* The question before the Board today is narrow: **has that
gap been closed by artifacts that already exist in the repository, or not?**

## 2. What an Accept does — and what it does not do

| Accept **does** | Accept **does not** |
|---|---|
| Name the Time Source fulfillment pattern (Scheduled Command Invocation) | Authorize FR-030 engineering — ADR §Non-scope 6; a separate sprint gate is required |
| Lift **CAP006-BLK-001** | Deliver DEC-031 Fase 2 |
| Give the ADR-009 outbox debt a sanctioned execution shape | Open **CAP-005** — the notification delivery channel stays Stay Deferred |
| Permit the four-gate Implementation Gate to be worked | Change any Business Rule, Event Catalog entry, FRD, or API surface |
| Sign DEC-031 §7b (a separate signature, on the same evidence) | Make an off-screen officer reachable — see §6 |

**Blocker opening ≠ feature completion.** These are different acts with different gates.
The Board is asked for the first only.

## 3. Evidence — the pattern is already executing in this repository

All rows re-verified in the working tree on **2026-08-23** for this package (the ADR carries the
full ten-row table; the four rows below are the load-bearing ones B2-17E asked for).

### E-1 — A committed CLI application command already exists

[`backend/scripts/cm_batch1_ops_hygiene.py`](../../backend/scripts/cm_batch1_ops_hygiene.py) —
`argparse` CLI, `_configure()` loading `get_settings()` + `configure_logging`, sub-commands that
open `get_session_factory()()`, delegate to an application service, print a structured line, close
the session in `finally`, and return an exit code (`0` OK / `2` failed), ending at
`raise SystemExit(main())` (line 103). Unit-tested by `backend/tests/test_cm_batch1_ops_hygiene.py`.

**Establishes:** the *shape* ADR-CAP006-002 proposes is written, committed, and tested. Nothing
about it is invented for CAP-006.

### E-2 — A time-threshold sweep is already executed by that command

`void-abandoned-staging` → `CmBatch1AttachmentService.void_abandoned_staging`
([`attachment_service.py:687`](../../backend/app/modules/cm_batch1/attachment_service.py)) →
`CmBatch1AttachmentRepository.list_expired_open_staging(now=…)`
([`attachment_repository.py:108`](../../backend/app/modules/cm_batch1/attachment_repository.py)),
whose SQL predicate is:

```
status == "OPEN"  AND  expires_at < now
```

**Establishes:** *"find the rows whose deadline passed while nobody was looking"* — the exact
computational act CAP-006 needs — is already performed by a scheduled command in this repository.
CAP-006 differs only in **which** deadline column is read (`due_at` derived from
`created_at + COMPLAINT_RESOLUTION_TARGET_DAYS`, not `expires_at`).

### E-3 — That sweep already writes durable side effects through the ADR-009 outbox

The same loop calls `self._side_effects.record(...)` → `CmBatch1SideEffectRecorder` → **Audit +
Timeline + Outbox in one session**, then `self._repo.commit()`
([`attachment_service.py:713–724`](../../backend/app/modules/cm_batch1/attachment_service.py)).
`OutboxRepository.enqueue` refuses a row whose `idempotency_key` already exists and returns `None`
([`outbox_repository.py:43–56`](../../backend/app/modules/cm_batch1/outbox_repository.py)).

**Establishes:** a non-HTTP, command-invoked caller already emits durable domain events **and** the
duplicate-suppression primitive CAP-006 needs already exists. Neither is a new capability.

### E-4 — Scheduling an ECMP command on a cadence is already an Active operating procedure

[`15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md`](../../15%20Operations%20Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md)
— **OPS-CM-B1-STG-001, Status 🟢 Active (Mode A)** — carries a Cadence table, documented exit
codes, and JSON log fields. Written before this ADR, for a different capability. On the target
host, the root crontab already invokes an ECMP repository command
(`15 2 * * * /opt/ECMP/deploy/backup-postgres.sh`), and `flock` is present both on the host and
inside the backend image ([`backend/Dockerfile:49`](../../backend/Dockerfile) installs `util-linux`).

**Establishes:** the host scheduler exists, already owns an ECMP workload, and the anti-overlap
primitive is already installed. **The composite chain — scheduled execution → application service
→ time-threshold evaluation → durable side effects → exit code — is complete in the repository
today.** No link of it is proposed for invention.

### Negative evidence (what is *absent*, verified 2026-08-23)

| Checked | Result |
|---|---|
| `backend/requirements.txt` for celery / apscheduler / rq / arq / dramatiq | **none** |
| `.github/workflows/*.yml` for `schedule:` triggers | **none** (5 workflows, all event-driven) |
| ECMP systemd unit / timer | **none** |
| `docker-compose.prod.yml` services | 4 (caddy, postgres, backend, frontend) — no worker |

Option C is therefore not chosen over a scheduler the repository already has; it is chosen because
it is the **only** execution mechanism the repository has. Options A (in-process thread) and B
(worker container + broker library) are both **invent** and fail the B2-22 gate on arrival.

## 4. Constraints the Board is asked to hold the decision to

An Accept binds the pattern to these limits. §Decision 1–11 of the ADR states them normatively;
they are restated here so the Board decides on them explicitly.

- **No new scheduler** — the operating system's is used.
- **No new worker architecture** — no daemon, no long-running process.
- **No new broker** — ADR-009 is not reopened; no generic retry/DLQ publisher.
- **No new container / no new deployment unit** — the command ships in the existing backend image.
- **No new orchestration mechanism**, no new port, no new HTTP surface, no new queue table.
- **No new library** in `requirements.txt`.
- **No modification of historical governance** — B2-17E, B2-20…B2-24 stand unamended; this package
  adds a decision, it does not rewrite one.
- **Reuse of the existing execution pattern** — the CAP-006 command must not diverge from
  `cm_batch1_ops_hygiene.py`, and must not carry a second SLA implementation
  (`backend/app/modules/cm_batch1/sla.py` `resolve_complaint_sla` is the single source of truth).
- **Cadence is configuration** (ADR-003), not compiled in. Hourly is the recommended starting value,
  not a fixed property of the design.

Environmental delta of an Accept, in full: **one crontab entry, one lock path, one log
destination.** Database: none. Image: none. Compose: none.

## 5. Risks the Board must weigh

### R1 (HIGH) — Silent death of a scheduled job. **Realized in this repository today.**

The ADR's own Counter-Evidence records it: the cited backup schedule
(`deploy/backup-postgres.sh`, root crontab) has **failed on every firing since 2026-08-02** — 21
consecutive days. Each `backups/ecmp_*.sql.gz` since then is **20 bytes** (gzip of empty input);
the last good dump is `ecmp_20260801T021501Z.sql.gz`. Root cause is configuration drift
(`--env-file .env.prod` aborting on a missing variable), not the pattern — `set -euo pipefail`
behaved correctly and wrote the failure to `/var/log/ecmp-backup.log` on every firing.

**Nobody read that log for three weeks.** Two consequences the Board should treat as load-bearing:

1. **"The failure is visible in the job log" is not observability.** A log nobody reads is
   indistinguishable from silence. ADR v0.1 listed log-visibility as a Pro; v0.2 **withdraws** that
   claim.
2. **This failure mode is uniquely dangerous for SLA notification.** A dead backup job is
   discovered at restore time. A dead SLA job produces *no alerts* — which is byte-for-byte what a
   compliant month looks like. Absence of runs must be **positively detectable**.

Therefore **§Decision 8 (positive heartbeat) is a non-optional condition of the Accept**, not a
recommendation: the last-successful-run timestamp must be observable by operations rather than
inferred from silence, with a named owner and a named mechanism recorded at Gate 1 (G1.4).

The counter-evidence is presented deliberately. The pattern is proposed **with** its known failure
mode disclosed, and the mitigation is written into the decision.

### Remaining risks (ADR §Risks R2–R7, summarized)

| # | Risk | Sev | Mitigation |
|---|---|---|---|
| R2 | Schedule lives in host config; a host rebuild loses it silently | MED | Provisioning step recorded in `14 Deployment Standards` + `15 Operations Runbook` on Accept |
| R3 | Overlapping firings double-emit | MED | `flock` **and** outbox `idempotency_key` — the second is authoritative |
| R4 | Config drift breaks the command as it broke the backup | MED | The command reads settings via `get_settings()` **inside** the image, not via host compose interpolation — the drift class that killed the backup does not apply |
| R5 | Aggressive cadence turns a sweep into a poll | LOW | Batch limit in configuration; cadence is a config change |
| R6 | `EVT-004` accumulates unpublished (262-row precedent) | MED | Drainer scheduled under the same pattern, **or** write-only emission explicitly accepted (G4.2) |
| R7 | Business reads "blocker cleared" as "notifications delivered" | MED | §6 below; DEC-031 §7b note; G2.3 written notice |

### Security (consulted)

The command runs as the existing container user with existing credentials from the existing
environment; opens no port, adds no HTTP surface, accepts no network input. Two obligations carried
into the command contract (§Decision 9): no secret to stdout or file, and **file modes set before
content is written, not after** — the backup failure left a would-be partial dump world-readable
at mode `0644` precisely because `chmod 600` came last.

## 6. Reachability Limit — CAP-005 remains a separate gate

Verified 2026-08-23. Accepting this ADR supplies **the trigger only**. The path from trigger to a
human is cut in two further places:

| Link | State | Consequence |
|---|---|---|
| Trigger (this ADR) | Proposed | Supplied on Accept |
| Breach detection + `EVT-004` write | Write path exists and works (E-3) | Available |
| `EVT-004` **publication** | Nothing drains `cm_batch1_outbox` in the root stack; **262 rows `UNPUBLISHED`** (2026-08-17 … 2026-08-22) | `EVT-004` would be **written but never published** |
| Notification **channel** | `StubNotificationProvider` only (`backend/app/modules/notification/infrastructure/providers.py:36` — *"No SMTP / Twilio / FCM / webhook HTTP. Stub only."*); `notification_queue` holds **0 rows**; CAP-005 production engine **Stay Deferred** (B2-24) | Email / SMS / push **cannot** be sent |
| In-app surface | DEC-031 Fase 1 delivered `SlaAlertsPanel`, computed at read time; **no notification inbox** exists in `frontend/src/features/` | An off-screen officer is still not reached |

**Therefore:** with this ADR Accepted and CAP-005 still stubbed, DEC-031 §3 Fase 2's sentence
*"memberi tahu petugas tanpa ada orang membuka halaman"* **remains unachievable**. That sentence
depends on CAP-005, not on this ADR. The Board is asked to Accept the ADR **on its own merits as
the Time Source pattern**, and Business must be told in writing (Gate 2 / G2.3) that the deliverable
scope available today is **detection + durable record + in-app alert**, not proactive off-screen
notification. No SMTP / Twilio / FCM provider may be introduced as a workaround; that is CAP-005's
gate, requiring its own decision.

## 7. Acceptance Criteria put to the Board

Board ticks in session; unticked = not yet assessed. Mirrors ADR §Acceptance Criteria AC-1…AC-8.

- [ ] **AC-1** Every Evidence row 1–10 is independently verifiable in the repository or on the target host; none rests on documentation alone.
- [ ] **AC-2** No new scheduler, library, worker, container, broker, port, or queue is introduced by §Decision.
- [ ] **AC-3** ADR-009 is not reopened: no generic retry/backoff/DLQ publisher is specified.
- [ ] **AC-4** ADR-003 is honoured: cadence and batch bounds are configuration.
- [ ] **AC-5** Duplicate suppression is sourced to the existing `idempotency_key` claim, not to a new mechanism.
- [ ] **AC-6** The Counter-Evidence failure mode is addressed by a stated, non-optional condition (§Decision 8 positive heartbeat).
- [ ] **AC-7** The Reachability Limit is understood and recorded, so that Accept is not mistaken for delivery of DEC-031 Fase 2.
- [ ] **AC-8** Non-scope §1–8 hold: no Business Rule, Event Catalog, FRD, or API surface change.

## 8. Review Outcome

*(Architecture Review Board — tick exactly one. Unticked = no decision taken.)*

- [ ] **Accepted** — ADR-CAP006-002 v0.2 satisfies the B2-24 condition; **CAP006-BLK-001 lifted**
- [x] **Accepted with conditions** — conditions recorded in §9 below and mirrored into the ADR
- [ ] **Rejected** — reason recorded in §9; ADR status → Rejected, retained for history; blocker stays frozen
- [ ] **Deferred** — what additional evidence or artifact is required, recorded in §9; blocker stays frozen

**Outcome as of 2026-08-23: Accepted with Conditions. CAP006-BLK-001 LIFTED. FR-030 engineering NOT authorized.**

## 9. Conditions / Actions

*(Completed by the Board at decision time.)*

Conditions carried in the proposal, should the Board Accept:

- **C-1** Positive heartbeat (§Decision 8) is mandatory, with a named owner and mechanism before FR-030 engineering opens (Gate 1 / G1.4).
- **C-2** Business notified in writing of the Reachability Limit before DEC-031 §7b is signed (Gate 2 / G2.3).
- **C-3** Detection-lag tolerance = **1 hour** (recorded 2026-08-23 follow-up). Starting cadence: hourly.
- **C-4** `EVT-004` publication path = **outbox drainer under the same pattern** (recorded 2026-08-23 follow-up). Write-only rejected.
- **C-5** The failed backup schedule is repaired **independently** of CAP-006; it is an operations defect and must not be bundled into this decision or wait on it.
- **C-6** In-app alert eligibility = remaining **7 / 3 / 1** calendar days (once each) + breach at `due_at`; CAP-005 not opened (recorded 2026-08-23 follow-up).

Board-added conditions:

> Follow-up 2026-08-23 (same signatory): *«C-3 1 jam, C-4 outbox dikuras, peringatan H-7 H-3 H-1 dalam aplikasi saja»*.
> C-3, C-4, and C-6 are **closed**. C-1 named owner/mechanism remains required before FR-030 code.

**Exception required?** **No.** This is an ADR decision on the ADR lifecycle path
(`18 Architecture Governance/README.md` §ADR Lifecycle), not a deviation from a standard. No
`EXCEPTION_REQUEST.md` is filed.

## 10. Repository synchronization — only after a recorded Accept

Executed **only** with the signed §11 as evidence, never on assumption. Each line cites the Accept.

| # | Artifact | Action on Accept |
|---|---|---|
| 1 | `05 …/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md` | Status 🟡 Proposed → 🟢 **Accepted**; version bump; Accept date + this Review ID recorded in Document History |
| 2 | This package | Status → 🟢 Complete; §8 outcome ticked; §11 signed |
| 3 | `deploy/evidence/` | New ARB decision evidence document created (successor cut to B2-24; B2-24 itself unchanged) |
| 4 | `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` | CAP-006 rows: blocker **CAP006-BLK-001 lifted**, citing the Accept; engine remains **not yet an eng ticket** until the Implementation Gate passes |
| 5 | `26 Traceability/traceability.yaml` TRC-L-007 | Description updated: pattern Accepted, blocker lifted, FR-030 gate now openable via Implementation Gate |
| 6 | `27 Project Decisions/DEC-031` §7b | ARB signature recorded **only if the Board also signs there**; §7a untouched |
| 7 | `05 …/README.md` + `ADR_INDEX.generated.md` | Status rows updated (hand-edit — see the note in §12) |
| 8 | `18 Architecture Governance/README.md` | CAP-006 pointer line updated |
| 9 | `04 Solution Architecture`, `14 Deployment Standards`, `15 Operations Runbook` | Runtime shape, provisioning step, heartbeat check (ADR Follow-up Actions) |

**Not done by any of the above:** starting FR-030 code. That needs the four-gate Implementation
Gate (ADR §Implementation Gate) recorded as passed, as a separate sprint decision.

## 11. Sign-off

*(No signature is valid unless §8 carries a ticked outcome.)*

- **Architecture Review Board (Approver):** rbxhut  Date: 2026-08-23
- **Architecture Board Chair:** rbxhut  Date: 2026-08-23
- **Solution Architect (Requester, R):** ADR-CAP006-002 v0.2 submitter  Date: 2026-08-23
- **Security (Consulted — §5):** consulted via package §5; no additional objection recorded  Date: 2026-08-23
- **Performance Owner (CAP-006):** informed via CAP-006 register sync  Date: 2026-08-23

**Status 2026-08-23: SIGNED — Accepted with Conditions.**

## 12. Verification log (2026-08-23)

Commands run against the working tree while preparing this package, so the Board can repeat them:

```bash
sed -n '1,103p' backend/scripts/cm_batch1_ops_hygiene.py
```

```bash
grep -n -A 15 "def list_expired_open_staging" backend/app/modules/cm_batch1/attachment_repository.py
```

```bash
grep -n -A 40 "def void_abandoned_staging" backend/app/modules/cm_batch1/attachment_service.py
```

```bash
grep -n -A 25 "def enqueue" backend/app/modules/cm_batch1/outbox_repository.py
```

```bash
grep -in "celery\|apscheduler\|rq\|arq\|dramatiq" backend/requirements.txt
```

```bash
grep -n "util-linux" backend/Dockerfile
```

**Toolchain note (defect, not a blocker):** `tools/ear_repo_check.py --write-adr-index` regenerates
`ADR_INDEX.generated.md` from the `ADR-NNN` filename pattern only. It **drops** every
`ADR-CAP006-*` / `ARC-CAP006-*` row (those are hand-maintained) and rewrites ADR-016…018 status
text. The index rows for CAP-006 artifacts must therefore be hand-edited; do **not** run the
generator as part of the §10 sync without reviewing its diff. Gate 1 / G1.3's "ADR index
regenerated" is satisfied by a reviewed hand-edit.

## Related Documents

- [`05 …/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md`](../../05%20Architecture%20Decision%20Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md) — the subject (v0.3, **Accepted with Conditions**)
- [`deploy/evidence/B2-25_CAP-006_ADR-CAP006-002_Accept_With_Conditions_20260823.md`](../../deploy/evidence/B2-25_CAP-006_ADR-CAP006-002_Accept_With_Conditions_20260823.md) — this decision
- [`deploy/evidence/B2-24_…_Blocker_Freeze_20260804.md`](../../deploy/evidence/B2-24_CAP-006_Stay_Deferred_Confirmation_Blocker_Freeze_20260804.md) — historical freeze (unamended; condition discharged)
- [`27 Project Decisions/DEC-031_…_v0.1.md`](../../27%20Project%20Decisions/DEC-031_SLA_Resolution_Target_30_Calendar_Days_v0.1.md) — §7a signed; §7b signed Accepted with Conditions
- [`03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md`](../../03%20Functional%20Requirements/ECMP_FRD_KPI_SLA_v0.1.md) (FRD-005 🔒 LOCKED)
- [`15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md`](../../15%20Operations%20Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md) (OPS-CM-B1-STG-001, Active)
- [`18 Architecture Governance/README.md`](../README.md) — RACI, ADR Lifecycle · [`reviews/ARCHITECTURE_REVIEW_FORM.md`](./ARCHITECTURE_REVIEW_FORM.md) (AR-001, form this package follows)

---

*End of GOV-AR-CAP006-002 — decided 2026-08-23. Accepted with Conditions. CAP006-BLK-001 lifted. FR-030 engineering remains closed until Implementation Gate 1–4.*
