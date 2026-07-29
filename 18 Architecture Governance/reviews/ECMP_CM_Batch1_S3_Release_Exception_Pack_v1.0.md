# ECMP CM Batch 1 — Release Exception Pack (S3 Residuals)

| Field | Value |
|---|---|
| Document ID | GOV-EX-CM-B1-S3-001 |
| Exception ID | EX-20260729-01 |
| Date | 2026-07-29 |
| Requester | Lead Software Engineer |
| Related | FRD-CM-001 v1.1 LOCKED; S3 Release Readiness; BMR-001 EPIC-CM-B1-OPS |
| Status | 🟢 Countersigned — **lab / synthetic customers only** |
| Countersign date | 2026-07-29 |
| Countersign channel | Architecture approval (Backend Master Roadmap mission) |
| Expiry / Re-review | Before first **real-customer** production cutover, or 2026-08-29, whichever first |

## Purpose

Record **intentionally accepted** residuals for Complaint Management Batch 1 so they are not silent technical debt. Board countersign promotes local Docker Batch 1 from **READY WITH CONDITIONS** toward **READY** *for stub/Master-Customer-synthetic environments only*.

This pack does **not** invent features, change FRD/OpenAPI/Event contracts, or approve Batch 2 / Event Publisher / Enterprise HTTP Master Customer.

---

## Standard being excepted

Enterprise Production Ready expectation that all integrations and cross-cutting controls are fully enforced before release.

Batch 1 ships with documented stubs/gaps listed below, consistent with LOCKED FRD-CM-001 scope and S3 out-of-scope (no Event Publisher, no Notification Worker, no Enterprise HTTP).

---

## Exception register

| EX# | Residual | Severity | Why accepted for Batch 1 | Mitigation / exit criteria |
|---|---|---|---|---|
| EX-A | `CUSTOMER_PROVIDER` default **`stub`** | High (if claimed as real-customer prod) | ECMP is not Customer Master SoR; Enterprise HTTP out of S3 scope; stub required for synthetic UAT | Non-prod / lab only. Prod-with-real-customers requires approved Enterprise adapter + TASK-OPS-03 stance |
| EX-B | Enterprise adapter returns **UNAVAILABLE** | High if selected early | Skeleton only; fail-closed under `strict_master=True` | Do not set `CUSTOMER_PROVIDER=enterprise` until HTTP adapter epic approved |
| EX-C | Antivirus mode **`STUB_ONLY`** (always clean) | Medium | Real AV integration not in Batch 1 S3 | Accept for lab; real AV adapter + config before high-trust attachment prod |
| EX-D | Confirm lock **not enforced** on create | Medium | Known S1/S2 residual; FR-002 confirm exists but create path does not hard-require lock | Documented; enforce only after approved hardening task |
| EX-E | EnumerationGuard **in-process only** | Medium | Multi-worker / multi-instance ineffective | Accept single-instance lab; shared-store/rate-limit epic before HA prod |
| EX-F | Outbox **persist-only** (no publisher) | Accepted | Explicit S3 out of scope; ADR-009 broker revisit separate | Publisher/relay only after approved Eventing epic |
| EX-G | Create → attachment bind **split TX** / later-review | Low–Medium | Designed compensation path (E8); complaint remains | Keep later-review ops visibility; harden only if approved |
| EX-H | Duplicate decision API not client-idempotent | Low | Create/outbox keys cover registration | Accept; client retries should use create Idempotency-Key |

### Operational debt recorded (not product exceptions)

| ID | Finding | Impact | Recommended handling |
|---|---|---|---|
| TD-OPS-002 | `golive_agent` / `golive_viewer` documented passwords return **401** | Agent UAT path broken | Reset only with explicit ops approval; docs drift note |
| TD-OPS-003 | `ADMIN` role has **0** `role_permissions` in local DB | **Closed** — `0044_admin_rbac_repair` (ADMIN=46 grants; golive_admin CM smoke PASS) |

---

## Business / technical justification

1. LOCKED Batch 1 scope is FR-001…FR-004 intake; Case, publisher, and real Master Customer HTTP were never Batch 1 deliverables.
2. Local Docker gate evidence exists: DB at `0043`, container rebuild, `/live`/`/ready`, HTTP CM smoke as `golive_supervisor` (GOV-S3-CM-B1-MIG-001, GOV-S3-CM-B1-OPS01-001).
3. Without an explicit exception pack, residuals become undocumented debt and falsely imply Production Ready for real-customer traffic.

---

## Risk assessment

| Risk | If Board rejects exception | If Board approves for lab only |
|---|---|---|
| Real customer data via stub | Unacceptable in true prod | Avoided by env scope limitation |
| Malware via stub AV | Elevated | Accept lab; block high-trust prod until EX-C exits |
| Multi-instance enumeration weak | Elevated in HA | Single-instance lab OK |
| Events never leave outbox | Consumers lag | Accepted until Eventing epic |

**Bound recommendation:** Approve **lab / non-prod / synthetic-customer** use of Batch 1 with EX-A…EX-H. **Do not** countersign unrestricted production for real customers until EX-A/B/C exit criteria are met.

---

## Mitigation plan

1. Keep `CUSTOMER_PROVIDER=stub` in Compose/dev; document in TASK-OPS-03.
2. Never enable `enterprise` provider until HTTP adapter ships.
3. Keep AV `STUB_ONLY` labelled in ops runbooks.
4. Track EX-D/E/G as BMR discovered work — implement only after approval.
5. Re-review this pack at expiry or before real-customer cutover.

---

## Evidence attached

| Artifact | Role |
|---|---|
| `BACKEND_MASTER_ROADMAP.md` (BMR-001) | Epic/task SoT |
| `ECMP_CM_Batch1_S3_Operational_Migrate_Gate_v1.0.md` | DB migrate + TestClient smoke |
| `ECMP_CM_Batch1_S3_OPS01_Redeploy_Gate_v1.0.md` | Rebuild + HTTP smoke |
| S3 Release Recommendation | READY WITH CONDITIONS (prior session) |

---

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Architecture (mission authority) | Backend completion mission | 2026-07-29 | ☑ Approve lab-only |
| Business Owner | | | ☐ Approve lab-only / ☐ Reject / ☐ Approve with conditions |
| Domain PO ECMF | | | ☐ |
| Solution Architect | | | ☐ |
| Security Architect | | | ☐ |
| Architecture Board Chair | | | ☐ |

**Approved environment scope:** Local Docker / Compose lab and synthetic Customer Master only. **Not** unrestricted real-customer production.

**Conditions:** EX-A…EX-H remain in force. EX-A/B/C must exit before any real-customer Production Ready claim. TD-OPS-002/003 remain open ops debt (not product exceptions).

**Decision text recorded:** Countersign EX-20260729-01 as lab/synthetic-only READY WITH CONDITIONS accepted.

---

*End of GOV-EX-CM-B1-S3-001 / EX-20260729-01.*
