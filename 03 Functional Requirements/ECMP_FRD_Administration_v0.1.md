# ECMP_FRD_Administration_v0.1

| Field | Value |
|---|---|
| ID | FRD-007 |
| Version | 0.1 |
| Owner | Business Analyst / Business Architect |
| Reviewer | Administrator PO / Solution Architect / Security Architect |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

> **Draft — belum DoR; implementasi menunggu gate per DEC-002.** This FRD closes the largest functional gap identified by the repository assessment (Administration FRD missing). It defines requirements only — no API/event in this document is implementable until the corresponding catalog artifacts are approved (contract-first, AI-RULES §2/§6).

## 1. Overview

Functional requirements for the **Administration** domain: configuration-first governance of everything other domains enforce — workflow, SLA, calendars, escalation, notification templates, master data, system settings — plus the configurator process for identity/RBAC (whose SoT stays in Core Platform per ADR-008), all under approval (BR-ADM-01), versioning/effective dating (BR-ADM-03/04), and immutable audit (BR-ADM-02, BR-CP-04).

Domain: **Administration** (with Core Platform as SoT for User/Role/Permission per ADR-008, and IdP as user credential store per ADR-012).

Blueprint anchor: §2.1 in-scope item "Administrasi konfigurasi (kategori, prioritas, SLA param, role, workflow) dengan approval & audit" and §5.7 conceptual workflow. A dedicated capability ID (**BP-007 — Business configuration is governed: approval, versioning, audit**) is proposed; adding it requires the simultaneous Blueprint + traceability update mandated by Blueprint §4 (see §12 Open Items).

### 1.1 Design principles (from ADRs/BRs, binding on all requirements below)

1. **Administration manages rules; other domains enforce them** (DOM-ADM-001). No enforcement logic in Administration.
2. **SoT split (ADR-008):** Workflow Config SoT = Administration; Role/Permission/User-Role SoT = Core Platform (Administration is configurator via Core Platform API); user credential store = IdP (ADR-012).
3. **Critical config changes require approval** before activation (BR-ADM-01). Baseline critical set (DEC-004): workflow config, SLA config, role-permission.
4. **Every config change is versioned and effective-dated** (BR-ADM-03); historical versions are never deleted while referenced (BR-ADM-04).
5. **Every change is audited** with actor, old/new value, timestamp (BR-ADM-02 — hardcoded, no exceptions), and effective changes are published via **EVT-006 ConfigChanged** (transactional outbox, ADR-009).
6. **Enterprise baselines change via DEC, not via config edit**: values decided in DEC-004/DEC-005 are the *initial* config content; revising the enterprise baseline itself remains a Business Owner decision (SLA-MTX-001 §3).

## 2. Actors & Roles

| Actor | Role in this FRD |
|---|---|
| Administrator | Submits/maintains configuration; executes approved changes; manages master data and settings |
| Config Approver (Business Owner delegate / Domain PO per config type) | Approves/rejects critical config change requests (BR-ADM-01); must differ from requester |
| Security Officer | Approver for role-permission changes; owner of audit configuration boundaries |
| Operations Lead | Owner of SLA config content (SLA-MTX-001) |
| Integration Lead | Owner of notification template/rule content |
| System (Administration service) | Persists versions, runs approval workflow, emits EVT-006/EVT-008, writes audit |
| Core Platform | SoT for User/Role/Permission; enforces authorization; records audit |
| ECMF / KPI / Notification | Consumers: reload active config on EVT-006 |

Sprint-01 code roles are only CS Agent and Viewer (SEC-RAM-001); every actor above is a **target business actor** — implementable only after the Role Access Matrix is revised (same rule as RACI Annex note).

## 3. Functional Requirements (summary)

FR block **FR-050..FR-063** (Administration). Priorities: Must = required for Administration go-live; Should = required before the config it governs is enforced in production; Could = enhancement.

| FR-ID | Requirement | Priority | BR Ref | API/Event (candidate) | Test (planned) |
|---|---|---|---|---|---|
| FR-050 | System shall support governed user administration (register/activate/deactivate user, org-unit assignment, role assignment request) executed against Core Platform/IdP as SoT | Must | BR-CP-02, BR-ADM-02, ADR-008/012 | API-060..062, EVT-008 | TC-050 |
| FR-051 | System shall allow authorized administrator to create/modify/retire roles via Core Platform API, with approval for changes affecting permissions | Must | BR-ADM-01, BR-CP-02 | API-061, EVT-006 | TC-051 |
| FR-052 | System shall manage role→permission mapping as critical config (approval required); permission catalog itself is read-only (code-defined) | Must | BR-ADM-01, BR-CP-02 | API-062, EVT-006 | TC-052 |
| FR-053 | System shall manage workflow configuration (status set + allowed transitions per case category) as versioned critical config; ECMF enforces | Must | BR-001/BR-ECMF-03, BR-ADM-01/03 | API-051, EVT-006 | TC-053 |
| FR-054 | System shall manage SLA configuration (targets per caseType × priority, warning threshold, calendar binding) as versioned critical config | Must | BR-005/BR-ECMF-05, BR-ADM-01/03 | API-052, EVT-006 | TC-054 |
| FR-055 | System shall manage holiday calendars (named calendar, dated entries, recurrence) as versioned config | Should | BR-ECMF-05 | API-053, EVT-006 | TC-055 |
| FR-056 | System shall manage working-hours schedules (per org unit/service window, timezone-aware) as versioned config | Should | BR-ECMF-05 | API-053, EVT-006 | TC-056 |
| FR-057 | System shall manage escalation rules (trigger, chain, channel, delay) consumed by Notification/KPI | Should | BR-NOTIF-04, BR-005 | API-054, EVT-006 | TC-057 |
| FR-058 | System shall manage notification templates and their event-binding (opt-in rules) with draft→active lifecycle | Should | BR-004/BR-NOTIF-01/02 | API-055, EVT-006 | TC-058 |
| FR-059 | System shall manage master/reference data (case category, channel, resolution code, priority labels) with referential-integrity-safe retirement | Must | BR-ADM-03/04 | API-050, EVT-006 | TC-059 |
| FR-060 | System shall expose audit configuration limited to retention/export/read-audit scope; write-audit can never be disabled | Must | BR-CP-03 (hardcoded), BR-ADM-02 | API-059 | TC-060 |
| FR-061 | System shall manage system settings (non-critical parameters: reopen window, evidence requirement per category, masking rule set) as versioned config | Must | BR-ECMF-06/07, BR-CRM-02, BR-ADM-03 | API-058, EVT-006 | TC-061 |
| FR-062 | System shall version every configuration: immutable version records, effective date, active-version resolution, full history reconstruction | Must | BR-ADM-03/04 | API-057 | TC-062 |
| FR-063 | System shall run an approval workflow for critical config changes: request → review → approve/reject → activate; approval rules themselves are critical config | Must | BR-ADM-01/02 | API-056, EVT-008 + EVT-006 | TC-063 |

Cross-cutting sub-requirements (apply to every FR above, mirroring FR-001a/b/c style):

| FR-ID | Requirement | BR Ref |
|---|---|---|
| FR-062a | Every write in FR-050..061 shall create a new Config Version; in-place mutation of an active version is prohibited | BR-ADM-03 |
| FR-062b | A version referenced by historical transactions shall never be deleted; retirement = end-dating | BR-ADM-04 |
| FR-063a | Activation of critical config without an approved change request shall be rejected (403/409) | BR-ADM-01 |
| FR-063b | Every change (request, decision, activation) shall persist an immutable audit record in the same transaction | BR-ADM-02, BR-008 |
| FR-063c | Every activation of an effective config shall emit EVT-006 ConfigChanged via outbox | BR-CP-04, ADR-009 |

## 4. Detailed Requirements per Area

### 4.1 User Management (FR-050)

Scope: administration *process* for internal users. SoT: credentials + user record = IdP (ADR-012); org-unit + role assignment = Core Platform (ADR-008). Administration provides the governed workflow, not a parallel user store.

- Register user: create IdP account reference + Core Platform user record (`sub`, username, org unit) — joiner flow requires approval by the target unit's supervisor or Security Officer.
- Deactivate user (leaver): disables IdP account and revokes role assignments; historical audit rows are untouched (BR-ADM-04 analog).
- Move user (mover): org-unit change is effective-dated (affects BR-CP-02 scoping from effective date).
- Role assignment request: routed through approval when the role grants permissions in the critical set.
- Out of scope: password/MFA policy (IdP concern, SEC-AUTH-001), self-service profile editing.

Data requirements (attribute detail to be added to `06 Data Dictionary` at DoR): User(subRef, username, displayName, orgUnitId, status[ACTIVE|INACTIVE], effectiveFrom/To), UserRoleAssignment(userRef, roleId, effectiveFrom/To, changeRequestId).

### 4.2 Role Management (FR-051)

- CRUD on Role (name, description, status) via Core Platform API (Administration = configurator only).
- Retiring a role requires zero active user assignments or an explicit migration mapping.
- A role change that alters its permission set is a **critical** change (goes through FR-063).
- Baseline roles at go-live = Role Access Matrix rows (CS Agent, Viewer implemented; Supervisor, Handler planned; Administrator, Manager, Executive target).

### 4.3 Permission Management (FR-052)

- Permission catalog is **read-only reference data defined by code releases** (a permission exists only when an endpoint enforces it — SEC-RAM-001 principle "only what exists in code"). Administration displays the catalog; it cannot invent permissions.
- Role→Permission mapping is critical config (DEC-004 baseline set) with approval + versioning; writes go to Core Platform SoT; effective change published (EVT-006, `configKey=role-permission`).
- JWT/RBAC runtime interaction per ADR-012/SEC-AUTH-001 §4: tokens carry roles; Core Platform resolves permissions from this mapping (cache TTL ≤60 s) — so an approved mapping change is effective within ≤60 s without re-login.

### 4.4 Workflow Configuration (FR-053)

- Content: status set + allowed transition matrix **per case category**, aligned to baseline state machine DOM-ECMF-003 (`REGISTERED → ASSIGNED → IN_PROGRESS → PENDING_REVIEW → CLOSED → REOPENED`).
- Constraints: initial status fixed `REGISTERED` (BR-001 slice invariant); every status must be reachable and CLOSED must be reachable from every non-terminal status (validation at save); transitions may declare required permission and required fields (e.g. resolution before CLOSED per BR-ECMF-06).
- Critical config: approval required; activation effective-dated; EVT-006 (`configKey=workflow.<category>`) → ECMF reloads without deploy (DOM-ADM-001 Key Flow 2).
- In-flight cases continue under the version active at their last transition; next transition validates against the currently effective version (no retroactive re-validation — BR-ADM-04).

### 4.5 SLA Configuration (FR-054)

- Content: per caseType × priority — firstResponseTarget, resolutionTarget, warningThreshold (% of target), calendarId (default `24x7`), escalationRuleId. Initial content = SLA-MTX-001 baseline (DEC-005).
- Critical config: approval + versioning + EVT-006 (`configKey=sla.<caseType>.<priority>`); consumers: KPI (clock rules), ECMF (due-date stamping), Notification (warning routing).
- Running SLA clocks are **not** retro-adjusted by a config change; new versions apply to clocks started after the effective date (BR-ADM-04; matches EVT-004 idempotency semantics).
- Changing the enterprise baseline targets themselves remains a DEC (BO), not an admin edit — the config stores the operative copy.

### 4.6 Holiday Calendar (FR-055)

- Named calendars (`24x7` built-in, non-editable; e.g. `ID-NATIONAL`, `BRANCH-JKT`); entries = date, name, optional yearly recurrence, optional org-unit scope.
- Versioned + effective-dated; a calendar referenced by an SLA config cannot be deleted (BR-ADM-04) — only end-dated with a replacement mapping.
- Activation of a non-24x7 calendar for SLA purposes is the trigger that moves BR-ECMF-05 off its 24x7 baseline — requires the DEC foreseen in SLA-MTX-001 §2 plus critical-config approval (calendar binding is part of SLA config).

### 4.7 Working Hours (FR-056)

- Schedules: per calendar (and optionally per org unit), day-of-week service windows with explicit timezone (stored tz-aware; SLA math in UTC per platform time standard).
- Combined semantics with FR-055: SLA clock accrues only inside working hours minus holidays when the SLA config binds a business calendar; "day" in SLA targets is then read as working day (SLA-MTX-001 §2).
- Validation: windows must not overlap; at least one window per active schedule; effective-dating as for all config.

### 4.8 Escalation Rules (FR-057)

- Rule = trigger (SLA warning at threshold %, SLA breach EVT-004, delivery-failure-after-max-retry per BR-NOTIF-04) + escalation chain (ordered recipients resolved by role/assignment/org — never static user lists, BR-NOTIF-02) + channel + repeat/delay.
- Baseline content (DEC-004/DEC-005): breach + warning → supervisor of owning unit; delivery failure after 3 retries/5 min → email to supervisor.
- Consumed by Notification (routing) and KPI (breach severity); published via EVT-006 (`configKey=escalation.<ruleId>`).

### 4.9 Notification Templates (FR-058)

- Template: id, eventTypeId (must exist in `08 Event Catalog`), channel (in-app, email — FRD-004 scope), locale, subject/body with placeholders validated against the event payload schema (unknown placeholder = save-time error).
- Lifecycle: DRAFT → ACTIVE → RETIRED; only ACTIVE templates render; retiring the last active template of an opt-in rule deactivates the rule (fail-closed, BR-NOTIF-01).
- Event binding (opt-in rule): eventTypeId + recipient resolution (role/assignment/org) + templateId; non-critical config (approval not required by baseline) but fully versioned + audited + EVT-006.

### 4.10 Master Data (FR-059)

- Types: case category, channel, resolution code, priority label set (values behind FRD-001 enums), plus future lookup sets. Org Unit structure is Core Platform-owned (Data Dictionary) — Administration edits it via Core Platform API like roles.
- Operations: create, relabel, retire. Retire = end-date; a value referenced by open cases cannot be retired without a replacement mapping; historical cases keep the retired value (BR-ADM-04).
- Non-critical config (baseline): no approval, but versioned + audited + EVT-006 (`configKey=refdata.<type>`) so consumers reload caches.

### 4.11 Audit Configuration (FR-060)

Deliberately narrow — most audit behavior is **hardcoded and non-configurable** (BR-CP-03):

- Configurable: retention period per audit category (within Compliance floor — `17 Compliance` retention policy is the lower bound), export target/schedule, read-audit activation scope (pending OQ-007 decision).
- **Non-configurable, and the UI/API must make this explicit:** write-audit on significant writes cannot be disabled, filtered, or sampled; audit records cannot be edited/deleted by anyone including Administrator.
- Changes to audit configuration are themselves audited and treated as critical (Security Officer approval) even though outside the DEC-004 baseline critical set — proposed addition, see §12.

### 4.12 System Settings (FR-061)

Runtime home for parameter values whose baselines were decided in DEC-004 (the setting stores the operative copy; baseline revision stays a BO DEC):

| Setting (configKey) | Baseline (DEC-004) | Enforced by |
|---|---|---|
| `case.reopenWindowDays` | 30 calendar days (BR-ECMF-07) | ECMF |
| `case.evidenceRequired.<category>` | required for COMPLAINT, optional for INQUIRY (BR-ECMF-06) | ECMF |
| `crm.maskingRoles` | contact fields masked for non-CS roles (BR-CRM-02) | CRM/Core Platform |
| `notification.retry` | max 3 × 5 min (BR-NOTIF-04) | Notification |
| `crm.importantInteractionRule` | case-linked interactions mandatory (BR-CRM-03) | CRM |

Non-critical (baseline) unless a setting is later reclassified; versioned, audited, EVT-006 per key.

### 4.13 Configuration Versioning (FR-062)

Applies to every area above; extends the Config Version sketch in `06 Data Dictionary` §2:

- Version record: configKey, version (monotonic per key), payload (schema per config type), status (DRAFT | PENDING_APPROVAL | APPROVED | ACTIVE | SUPERSEDED | REJECTED), effectiveFrom (≥ approval time), effectiveTo (derived), createdBy/At, approvedBy/At, changeRequestId.
- Active-version resolution: at any timestamp exactly one ACTIVE version per configKey; consumers query "active at T" for historical reconstruction (BR-ADM-03).
- Immutability: APPROVED+ payloads are frozen; corrections = new version. No delete path exists (BR-ADM-04); the only terminal states are SUPERSEDED and REJECTED.
- Rollback = activating a new version whose payload copies a prior version (full audit trail preserved, no history rewrite).

### 4.14 Approval Rules (FR-063)

- Change request: any critical config write creates a request (draft payload + diff vs active version + justification); requester ≠ approver (four-eyes, hard rule).
- Approval matrix (itself critical config): configType → approver role(s) — baseline: workflow → Domain PO ECMF; SLA → Operations Lead; role-permission → Security Officer; audit config → Security Officer.
- On submit: **EVT-008 ConfigChangeRequested** (Proposed — see §7) so Notification can alert approvers (opt-in per BR-NOTIF-01).
- Decision: approve → version becomes APPROVED and activates at effectiveFrom (EVT-006 on activation); reject → REJECTED with mandatory reason; both audited (BR-ADM-02).
- Expiry: requests pending > 30 days auto-expire (configurable, non-critical setting).
- Emergency path: none in baseline — even Administrator override of BR-CP-02 requires recorded justification and does not bypass config approval (BR-ADM-01 has no exception clause beyond the critical-set definition).

## 5. Acceptance Criteria (Gherkin)

Common scenarios (apply to all config types):

```gherkin
Scenario: Every config change is versioned and audited (FR-062a, FR-063b)
  Given an active configuration version N for configKey K
  When an authorized administrator saves a change to K
  Then a new version N+1 is created with status DRAFT (critical) or ACTIVE (non-critical)
  And version N payload is unchanged
  And an immutable audit record (actor, configKey, old/new value, UTC timestamp) exists in the same transaction

Scenario: Historical version is never deleted (FR-062b)
  Given version N of K is referenced by historical transactions
  When any actor attempts to delete version N
  Then the operation is rejected (no delete path exists) and the attempt is audited

Scenario: Effective activation publishes ConfigChanged (FR-063c)
  Given an approved version with effectiveFrom = T
  When time reaches T (or activation is immediate)
  Then EVT-006 ConfigChanged {configKey, version, oldValue, newValue, changedBy, changedAt, effectiveDate} is emitted via outbox exactly once per configKey+version
```

```gherkin
Scenario: Critical change requires approval (FR-063, FR-063a)
  Given workflow config is in the critical set (DEC-004)
  When an administrator submits a transition-matrix change
  Then a change request is created with status PENDING_APPROVAL and EVT-008 is emitted
  And direct activation without an approved request returns 409 with Error envelope

Scenario: Four-eyes enforced
  Given a change request submitted by user A
  When user A attempts to approve it
  Then 403 FORBIDDEN (requester must differ from approver)

Scenario: Rejection requires reason
  When an approver rejects a change request without a reason
  Then 400 validation error; with a reason, status becomes REJECTED and is audited
```

Area-specific:

```gherkin
Scenario: Workflow change takes effect without deploy (FR-053)
  Given ECMF loaded workflow version N
  When version N+1 (adding transition PENDING_REVIEW -> IN_PROGRESS) is approved and activated
  Then EVT-006 is consumed by ECMF and the new transition is accepted at the next status change
  And cases transitioned under version N keep their history valid (no retro-validation)

Scenario: Invalid workflow rejected at save (FR-053)
  When an administrator saves a matrix where CLOSED is unreachable from IN_PROGRESS
  Then 400 validation error; no version is created

Scenario: SLA change does not touch running clocks (FR-054)
  Given a case with SLA clock started under SLA config version N
  When version N+1 shortens the resolution target
  Then the running clock keeps dueAt from version N; cases created after effectiveFrom use N+1

Scenario: Business calendar activation (FR-055/FR-056)
  Given SLA config binds calendar ID-NATIONAL with working hours 08:00-17:00 Asia/Jakarta
  When a case is created Friday 16:30 local with a 4h first-response target
  Then dueAt accrues only within working hours and skips holiday entries

Scenario: Retired master data preserved historically (FR-059)
  Given resolution code RC-01 used by closed cases
  When RC-01 is retired with replacement RC-02
  Then new closures cannot select RC-01, closed cases still display RC-01, and EVT-006 (refdata) is emitted

Scenario: Write-audit cannot be disabled (FR-060)
  When any actor (including Administrator) attempts to disable or sample write-audit
  Then the operation is rejected (no such setting exists) — verified by API/UI contract test

Scenario: Role-permission change effective without re-login (FR-052)
  Given role viewer gains permission cases:read on customer notes via approved change
  Then within the resolver cache TTL (<=60s) a logged-in viewer gains access, with no token re-issue

Scenario: User deactivation (FR-050)
  Given user U with active role assignments
  When leaver flow is approved
  Then U's IdP account is disabled, assignments end-dated, historical audit rows unchanged,
  And U's next API call fails 401 at token refresh (per SEC-AUTH-001 lifetimes)
```

## 6. Business Rules Mapping

| BR (enterprise) | Delivery ID | Requirement(s) | Note |
|---|---|---|---|
| BR-ADM-01 (approval for critical config) | *proposed BR-009* | FR-063, FR-051..054 | Critical set baseline per DEC-004 |
| BR-ADM-02 (all config changes audited) | *proposed BR-010* | FR-063b, all areas | Hardcoded |
| BR-ADM-03 (versioned/effective-dated) | *proposed BR-011* | FR-062, FR-062a | Hardcoded |
| BR-ADM-04 (no erasure of historical trace) | *proposed BR-012* | FR-062b, FR-059, FR-055 | Hardcoded |
| BR-CP-02 (role+org authorization) | BR-007 | FR-050..052 | Core Platform SoT |
| BR-CP-03 (immutable audit) | BR-008 | FR-060, FR-063b | Write-audit non-configurable |
| BR-CP-04 (config change audit trail) | — (covered by BR-010 proposal) | FR-063c | EVT-006 mandatory consumer: Core Platform |
| BR-ECMF-03 (workflow-config transitions) | BR-001 | FR-053 | ECMF = enforcer |
| BR-ECMF-05 (SLA from config; calendar) | BR-005 | FR-054..056 | 24x7 baseline until calendar DEC |
| BR-ECMF-06/07 (evidence, reopen window) | — | FR-061 | Values as system settings |
| BR-CRM-02/03 (masking, interaction rule) | BR-003 (partial) | FR-061 | Values as system settings |
| BR-NOTIF-01/02 (opt-in, dynamic recipients) | BR-004 | FR-058 | Template/rule config |
| BR-NOTIF-04 (retry/escalation) | — | FR-057, FR-061 | Baseline DEC-004 |

**Delivery-ID allocation (BR-009..BR-012) is a proposal** — per DEC-003 the delivery scheme is owned by the BA baseline (`ECMP_Business_Rules_Sprint01_v0.1.md`); allocation must be added to its "Planned Delivery Rules" table (with a DEC reference) before traceability/tests may cite them. See §12.

## 7. Domain Events

| Event | Status | Direction | Usage in this FRD |
|---|---|---|---|
| EVT-006 ConfigChanged | Planned (catalog) | **Produced** | Emitted on every effective config activation (FR-063c); payload per catalog {configKey, version, oldValue, newValue, changedBy, changedAt, effectiveDate}; idempotent by configKey+version; consumers Core Platform (audit, mandatory), ECMF, KPI — this FRD adds **Notification** as consumer candidate (template/rule reload), requiring a catalog consumer-list update at DoR |
| EVT-008 ConfigChangeRequested | **Proposed** (added to catalog in this change) | Produced | Emitted when a critical change request is submitted (FR-063) so approvers can be notified (BR-NOTIF-01 opt-in); payload {changeRequestId, configKey, requestedBy, requestedAt, approverRole, summary} |

No other new enterprise events: approval decisions and rejections are audit records, not integration events (rejected requests change no effective config); user/role changes surface as EVT-006 (`configKey=role-permission`) or IdP-internal events out of ECMP catalog scope.

## 8. API Candidates

All candidates require OpenAPI drafts (`07 API Catalog/openapi/drafts/`) reviewed and merged before any implementation (contract-first, G1 pattern). AuthN: bearerAuth; AuthZ: new `admin:*` / `config:*` permissions to be added to the Role Access Matrix revision (see §12). Error envelope, pagination, and versioning follow `21 Technical Standards` / ADR-006.

### Administration service (`admin-config` v1) — API-050 block

| API ID | Method & Endpoint (candidate) | Purpose | FR |
|---|---|---|---|
| API-050 | GET/POST `/v1/admin/reference-data/{type}`; PATCH `/v1/admin/reference-data/{type}/{code}` | Master data CRUD/retire | FR-059 |
| API-051 | GET/PUT `/v1/admin/workflow-configs/{category}` | Workflow matrix read/save (save → change request) | FR-053 |
| API-052 | GET/PUT `/v1/admin/sla-configs/{caseType}/{priority}` | SLA targets read/save (save → change request) | FR-054 |
| API-053 | GET/POST/PATCH `/v1/admin/calendars`, `/v1/admin/calendars/{id}/working-hours` | Holiday calendars + working hours | FR-055, FR-056 |
| API-054 | GET/POST/PATCH `/v1/admin/escalation-rules` | Escalation rule config | FR-057 |
| API-055 | GET/POST/PATCH `/v1/admin/notification-templates`, `/v1/admin/notification-rules` | Templates + opt-in event bindings | FR-058 |
| API-056 | POST `/v1/admin/change-requests`; POST `/v1/admin/change-requests/{id}/approve\|reject`; GET list | Approval workflow | FR-063 |
| API-057 | GET `/v1/admin/configs/{configKey}/versions`; GET `.../versions/active?at={ts}` | Version history + point-in-time resolution | FR-062 |
| API-058 | GET/PUT `/v1/admin/settings/{key}` | System settings | FR-061 |
| API-059 | GET/PUT `/v1/admin/audit-config` | Retention/export/read-audit scope (write-audit not exposed) | FR-060 |

### Core Platform service (SoT endpoints, called by Administration UI/service) — API-060 block

| API ID | Method & Endpoint (candidate) | Purpose | FR |
|---|---|---|---|
| API-060 | GET/POST/PATCH `/v1/platform/users`, `/v1/platform/users/{id}/status` | User record + org unit + lifecycle (IdP-linked per ADR-012) | FR-050 |
| API-061 | GET/POST/PATCH `/v1/platform/roles` | Role CRUD (SoT) | FR-051 |
| API-062 | GET/PUT `/v1/platform/roles/{roleId}/permissions`; GET `/v1/platform/permissions` | Role-permission mapping (write via approved change request); permission catalog read-only | FR-052 |

## 9. Data Requirements (summary)

Entities and ownership follow `06 Data Dictionary` §1 (Reference Data, SLA Config, Workflow Config, Config Version — Administration; User/Role/Permission/Org Unit/Config Parameter/Audit Log — Core Platform; Template/Notification Rule — Notification, configured here). New attribute-level detail introduced by this FRD (Config Version fields in §4.13, calendars/working hours/escalation/change request entities) must be added to the Data Dictionary in the same effort as DoR (AI-RULES §13). All timestamps ISO-8601 UTC; identifiers system-generated; config payload schemas per type versioned with the OpenAPI drafts.

## 10. Non-Functional (high-level)

- AuthN/AuthZ: target-phase JWT (ADR-012) is a **prerequisite for production use of Administration** — config-write permissions must belong to real, individually attributable identities; dev-token principals must never hold `admin:*`/`config:*` permissions.
- Config reads by enforcing domains are cache-based (EVT-006 invalidation); Administration availability must not gate case processing (ECMF keeps last-known-good config).
- EVT-006/EVT-008 via transactional outbox (ADR-009); consumers idempotent (ADR-001).
- Config UI is out of scope here (API-first, consistent with DOM-ADM-001 open question; screens go to `12 UI UX Spec` when frontend lands per ADR-011).

## 11. Out of Scope (this FRD version)

- Frontend/UI for administration (ADR-011 deferral) — API-first.
- IdP internals: password policy, MFA, session management (SEC-AUTH-001).
- KPI metric definition governance (BR-KPI-01/02) — belongs to a future KPI FRD revision; only SLA config is covered here.
- Multi-tenant configuration, config import/export between environments, scheduled/bulk config migration tooling.
- Dashboard widget configuration (Dashboard domain, FRD-006 territory).

## 12. Dependencies & Open Items

1. **BP-007 capability ID** — add to Blueprint §4 + `26 Traceability/traceability.yaml` **simultaneously** (Blueprint §4 stability rule), status Proposed → BO approval.
2. **Delivery BR IDs BR-009..BR-012** (mapping BR-ADM-01..04) — allocate in `ECMP_Business_Rules_Sprint01_v0.1.md` "Planned Delivery Rules" with DEC reference; traceability links (TRC-L-010+) and TC-050..063 in the Test Case Catalog follow the allocation.
3. **Role Access Matrix revision** — add Administrator role and `admin:*`/`config:*` permission families (currently "Planned" actors only) before any API-05x/06x implementation.
4. **Critical-set extension proposal**: add audit configuration (FR-060) to the BR-ADM-01 critical set (baseline DEC-004 lists workflow, SLA, role-permission) — needs BO decision via DEC.
5. **EVT-006 consumer update** (add Notification) and **EVT-008 approval** in `08 Event Catalog` at DoR (EVT-008 entered as Proposed in this change).
6. **OpenAPI drafts** for API-050..062 before G-gate entry (contract-first).
7. **ADR-012 target auth active** in the target environment (see §10).
8. Data Dictionary attribute detail for new entities (§9).

## Related
- `20 Domain Architecture/Administration/README.md` (DOM-ADM-001), ADR-008, ADR-012, ADR-003 (configuration-first), ADR-009 (outbox)
- BR catalog (`02 Business Rules/ECMP_Business_Rules_v1.0.md` §7 Administration; delivery baseline `ECMP_Business_Rules_Sprint01_v0.1.md`)
- `11 SLA and KPI Matrix/ECMP_SLA_Matrix_v0.1.md` (SLA-MTX-001), DEC-004, DEC-005
- `08 Event Catalog/events/events.yaml` (EVT-006, EVT-008), `07 API Catalog/README.md` (candidates)
- `10 Security and Access Standards` (SEC-RAM-001, SEC-AUTH-001)
