# B2-25 — CAP-006 ADR-CAP006-002 Accept with Conditions (blocker lift)

| Field | Value |
|---|---|
| Document ID | GOV-B2-25-ARB-001 |
| Sprint | B2-25 |
| Date | 2026-08-23 |
| Authority | Architecture Review Board (decision recorded by the Board member who holds the Accept) |
| Review ID | AR-20260823-01 |
| Subject | [`ADR-CAP006-002`](../../05%20Architecture%20Decision%20Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md) v0.2 → v0.3 |
| Verdict | **ACCEPTED WITH CONDITIONS** · **CAP006-BLK-001 LIFTED** · **FR-030 engineering NOT authorized** |
| Package | [`../../18 Architecture Governance/reviews/ECMP_ADR_CAP006_002_ARB_Decision_Package_v1.0.md`](../../18%20Architecture%20Governance/reviews/ECMP_ADR_CAP006_002_ARB_Decision_Package_v1.0.md) |
| Does not amend | B2-24 (GOV-B2-24-GOV-001) — that freeze stands as history; its *condition* is discharged on the non-invent branch |

## 1. Purpose

Record the Architecture Review Board outcome on ADR-CAP006-002: the Time Source fulfillment pattern **Scheduled Command Invocation** is Accepted with binding conditions. This lifts **CAP006-BLK-001**. It does **not** start FR-030 coding, open CAP-005, or install a crontab.

## 2. Decision

On 2026-08-23 the Architecture Review Board (signatory **rbxhut**) chose outcome **B — Accepted with Conditions** against package AR-20260823-01.

B2-24 §3 required a future architecture artifact to **Accept** a fulfillment pattern from **non-invent** repository evidence (or an explicit invent-authorization). ADR-CAP006-002 is Accepted on the **first** branch. No invent-authorization is granted. No new scheduler, worker, broker, library, container, or port is authorized.

## 3. Binding conditions (C-1…C-6)

| ID | Condition | State |
|---|---|---|
| C-1 | Positive heartbeat mandatory (named owner + mechanism) before FR-030 engineering (Gate 1 / G1.4) | **Closed** IG-20260823-01 — Operations Lead; marker files + JSON log; stale > 2h |
| C-2 | Reachability Limit in writing: trigger ≠ channel; CAP-005 remains stubbed | Binding; recorded in DEC-031 §7b |
| C-3 | Detection-lag tolerance = **1 hour**; starting cadence hourly | **Closed** 2026-08-23 (follow-up to Accept message `b`) |
| C-4 | `EVT-004` path = **outbox drainer under the same pattern** (write-only rejected) | **Closed** 2026-08-23; drainer **not built** in this cut |
| C-5 | Failed backup schedule repaired **independently** of CAP-006 | Binding; ops ticket, not an FR-030 prerequisite |
| C-6 | In-app alerts once each at remaining **7 / 3 / 1** calendar days + breach at `due_at`; no email/SMS/push | **Closed** 2026-08-23; engine **not built** |

### 3a. Follow-up recorded 2026-08-23 (same Board signatory)

Exact board message: *«C-3 1 jam, C-4 outbox dikuras, peringatan H-7 H-3 H-1 dalam aplikasi saja»*.

## 4. What this decision does not do

- Does not authorize FR-030 / EVT-004 **engineering**. Implementation Gate 1–4 must still pass (C-1 owner/mechanism open; Gates are process, not only C-3/C-4).
- Does not deliver DEC-031 Fase 2 off-screen notification (C-6 is in-app only).
- Does not open CAP-005 (no SMTP / Twilio / FCM).
- Does not add a host crontab, lock file, or log path in this sprint.
- Does not rewrite B2-17E, B2-22, B2-23, or B2-24.

## 5. Repository impact

| Artifact | Action |
|---|---|
| This evidence | **Created** |
| ADR-CAP006-002 | v0.3 **Accepted with Conditions** |
| ARB package AR-20260823-01 | Outcome B recorded; §11 signed |
| Capability Register CAP-006 | Blocker **lifted**; engine still not an engineering ticket |
| TRC-L-007 | Pattern Accepted; FR-030 still Planned / not authorized |
| DEC-031 §7b | ARB signature recorded with Reachability Limit |
| ADR index / 05 README / 18 README | Status rows updated (hand-edit; generator drops CAP-006 ids) |
| 04 / 14 / 15 | Pointers to runtime shape — **no crontab installed** |
| OpenAPI / Event Catalog / FRD body / BR / application code / DB | **Unchanged** |

## 6. Sign-off

- Architecture Review Board (Approver): **rbxhut** — 2026-08-23
- Architecture Board Chair: **rbxhut** — 2026-08-23
- Solution Architect (Requester): recorded in ADR-CAP006-002 v0.2 submission
- Outcome: **Accepted with Conditions** (exactly one §8 box)

---

*End of GOV-B2-25-ARB-001. CAP006-BLK-001 lifted. C-3/C-4/C-6 closed 2026-08-23. FR-030 engineering remains closed until Implementation Gate 1–4 (C-1 owner/mechanism still required).*
