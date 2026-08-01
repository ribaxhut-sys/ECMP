# ECMP FRD-CM-001 (Batch 1) — Independent Architecture Review

| Field | Value |
|---|---|
| ID | GOV-REV-FRD-CM-001 |
| Version | 1.0 |
| Subject | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.0.md` (FRD-CM-001 Draft v1.0) |
| Subject Status at Review | Draft v1.0 |
| Review Type | Independent architecture review — review only, no redesign |
| Reviewer Role | Principal Enterprise Architect |
| Owner | Architecture Board Chair |
| Approver | Architecture Board |
| Status | 🟢 Complete |
| Review Date | 2026-07-29 |
| Next Review | On FRD-CM-001 v1.1 resubmission |

## Evidence Base

- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.0.md` (subject)
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001, 🟡 Draft)
- `05 Architecture Decision Records/` — ADR-002 (Accepted), ADR-003, ADR-008, ADR-009, ADR-014 (🟡 Proposed), ADR-015 (🟡 Proposed)
- `07 API Catalog/API_CATALOG.generated.md`
- `18 Architecture Governance/README.md` — ADR lifecycle, quality gates G0/G1/G2
- `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`, `17 Compliance`, `13 Test Strategy` (checked for linkage)

Finding IDs: `C-nn` critical, `M-nn` major, `m-nn` minor.

---

## 1. Executive Summary

FRD-CM-001 is a **well-constructed document**. Its FR structure is consistent across all four requirements, its BR traceability is genuine rather than decorative, and it holds the locked Aggregate discipline firmly — Assignment and SLA are kept off the Complaint level in every place where a weaker document would have leaked them. The §1.1 namespace clarification, which openly declares that `FR-001` and `BR-001` mean different things in two live documents, is unusually honest and is the kind of disclosure most FRDs omit until it causes an incident. The RTM (DM → BR → FR) is complete for Batch 1.

Against that, the review found **six critical and seventeen major findings**. They cluster into four themes:

1. **Foundation is unratified.** The document declares thirteen decisions "LOCKED" and describes itself as *implementation-ready*, but every one of those decisions traces to a 🟡 Proposed ADR or a 🟡 Draft BR catalog, and the DEC that would make BR-CM-CAT-001 the implementation SoT does not exist (it is the FRD's own OQ-CM-B1-001). `C-01`
2. **A boundary inversion.** §4 lists **Authorization** as an external enterprise dependency consumed "via APIs only", directly contradicting ADR-014 ("Authorization remains internal") and ADR-008 (Role-Permission SoT = Core Platform). `C-02`
3. **Scope conflicts that make the primary business outcome undeliverable.** BR-014's stated purpose is to steer duplicates toward *a new Case on the existing Complaint*. FR-003 offers that outcome, defines an audit event for it, and maps a use case to it — but Create Case is explicitly out of Batch 1 scope. `C-03`
4. **Under-specified intake controls at exactly the points where volume and adversaries arrive.** Channel auto-register is in scope while its idempotency control is deferred to Future Enhancement (`C-05`); customer enumeration prevention is a `SHOULD` delegated to a dependency the FRD never declares (`C-06`); and the customer-key cardinality rule contradicts itself three times over (`C-04`).

None of these require redesign. All are corrections or completions within the existing structure. The architecture the FRD describes is sound; the specification of it is not yet safe to implement against.

**Compliance verification against the nine mandated checks:**

| Check | Verdict | Note |
|---|---|---|
| Complaint Aggregate Root | ✅ Compliant | Enforced consistently; identity non-reuse, no physical delete, no Case outside Aggregate |
| Multi Case | ✅ Compliant | 1..n Cases honoured; A4 no-Case path correct |
| Assignment on Case | ✅ Compliant | Explicitly excluded from Complaint level in §15.4 and validation table |
| Working Day SLA | ✅ Compliant | Correctly deferred; A4 states SLA MUST NOT start; Calendar correctly scoped as later dependency |
| CustomerId-only | ⚠️ Partial | Principle held, but UNVERIFIED path permits a Complaint with no CustomerId (`M-01`); ADR-002 staleness indicator omitted (`M-04`) |
| Customer 360 | ⚠️ Partial | Downgraded from BR imperative to `SHOULD`; depends on a capability out of Batch 1 scope (`M-08`) |
| API First | ✅ Compliant | Strong and repeated; catalog ID collisions are an inherited defect (`M-15`) |
| No Direct Database Access | ✅ Compliant | Stated normatively in §4, §13, and per-FR security sections |
| No Information Lost During Escalation | ⚠️ Partial | Held for committed evidence; staged-upload "discarded" permission breaches it pre-commit (`M-05`) |

---

## 2. Critical Findings

### C-01 — "LOCKED" decisions rest entirely on unratified documents, yet the FRD claims implementation-readiness

§3 presents thirteen decisions as **LOCKED and MUST NOT be changed**. Tracing them:

- Items 1–11 originate in **BR-CM-CAT-001**, which is 🟡 **Draft** and states of itself: *"menunggu DEC formal sebelum menggantikan SoT implementasi"* — awaiting a formal DEC before it replaces the implementation SoT.
- Items 12–13 originate in **ADR-014**, which is 🟡 **Proposed** and carries eight blocking items from its own independent review (GOV-REV-014).
- The related **ADR-015** is likewise 🟡 Proposed.
- The DEC that would resolve all of this is the FRD's own **OQ-CM-B1-001** — an open question inside the document that depends on it.

§2.1 nevertheless describes the deliverable as an *"**implementation-ready** Functional Requirements baseline"*. A document cannot be implementation-ready while its normative foundation is a draft catalog, two proposed ADRs, and an absent decision record. This also conflicts with the repository's own gate principle in `18 Architecture Governance` — *"gate = kontrak dibekukan **sebelum** kode"* — because nothing here is frozen.

*Impact:* teams may begin building against a model that the Business Owner has not ratified, and the existing Sprint delivery SoT (`BR-DOC-001` / `FRD-001`) still governs live code. §1.1's "MUST NOT silently overwrite" instruction mitigates ID collision but not the sequencing risk.

### C-02 — Authorization is listed as an external enterprise dependency, inverting the ADR-014 boundary

§4 opens: *"ECMP integrates with the following **external enterprise systems via APIs only**"* — and the table that follows contains:

> | Authorization | ECMP module authorization for complaint/customer/attachment actions |

ECMP's module authorization is **internal**. ADR-014 §Architecture Boundary assigns "Complaint Authorization" and "Complaint Roles" to ECMP; ADR-008 fixes Role-Permission SoT in Core Platform; ADR-015 §4 lists "ECMP roles and permissions" as ECMP-owned. Placing Authorization in a table of external systems accessed via API contradicts all three.

*Impact:* this is the single most likely finding in the document to be implemented literally. An implementer reading §4 as normative would build an outbound authorization call — reintroducing exactly the coupling ADR-014 was written to prevent. Identity, Authentication, and Organization belong in that table; Authorization does not.

### C-03 — FR-003's preferred business outcome is out of Batch 1 scope

BR-014's stated purpose is *"mendorong penambahan Case pada Complaint existing"* — steer duplicates into a new Case on the existing Complaint. The FRD carries this through:

- §9 FR-003 Normal Flow step 4, option 3: *"Add Case to existing Complaint (BR-004) instead of new Complaint"*
- §17 Audit Requirements defines the event `ResolvedAsCaseOnExisting`
- §11 Use Case Mapping defines UC-CM-007
- §4 FR-003 Business Objective names it explicitly

But §2.3 and §17 place **Case creation out of Batch 1 scope** ("Case creation as a standalone FR", "FR-005+ Case create standalone"). FR-001 A2 step 4 concedes it: *"Actor MAY add a new Case on the existing Complaint (BR-004) **outside this FR's create path**"* — outside the batch entirely.

*Impact:* Batch 1 ships duplicate detection that can warn and can block, but cannot deliver the resolution path the rule exists to promote. Agents are left with only two real options — abandon or override — which will drive the override rate up and corrupt the very KPI (`% Possible Duplicate Override`) meant to measure intake quality. An audit event is also defined for an outcome the system cannot produce.

### C-04 — Customer key cardinality: the FRD contradicts the BR and itself

BR-001 Business Validation is unambiguous: *"Kunci pelanggan | **Tepat satu** jenis kunci primer digunakan untuk lookup"* — **exactly one**.

The FRD states this four times, inconsistently:

| Location | Text | Reading |
|---|---|---|
| FR-001 §9 step 2 | "using **exactly one** primary key type" | exactly one |
| FR-001 §12 Validation | "**At least one** allowed key type MUST be supplied" | one or more |
| FR-001 §11 E1 | "require **at least one** allowed key" | one or more |
| FR-002 §12 Validation | "**At least one** allowed key MUST be provided" | one or more |

The normative validation tables — which is what implementers and testers read — say the opposite of both the BR and the FRD's own flow. FR-002 E5 ("Conflicting multiple keys supplied → MUST force manual resolution") only makes sense under the "at least one" reading, so the contradiction is structural, not typographical.

*Impact:* two defensible implementations exist, with different validation logic, different UI, and different test cases. This also violates the FRD's own §1.2 quality rule against deviating from BR-CM-CAT-001.

### C-05 — Channel auto-register is in scope while its idempotency control is deferred

FR-001 A5 step 2 permits: *"System auto-registers when channel auto-register policy is active and validations pass"* — an unattended create path, in Batch 1 scope.

Its control is not:

- §13 Input Data lists "Idempotency / channel message id" as **Conditional**, with no rule governing its use.
- §11 Exception Flow has **no case** for a repeated or replayed message-id.
- §21 Future Enhancement #2 defers *"Full omnichannel intake with per-message-id idempotency"* — the control is explicitly out of scope while the capability is in it.
- No idempotency exists for the **human** path either; a double submit is guarded only by duplicate detection, which is asynchronous-index-dependent (`M-02`) and score-threshold-dependent.

*Impact:* channel retries and double submits create duplicate Complaint Aggregates. Because §15.6 correctly forbids physical deletion, every such duplicate is **permanent** and must be resolved through linkage and audit forever after. The failure is silent, cumulative, and unrecoverable by cleanup.

### C-06 — Enumeration prevention is a `SHOULD` delegated to an undeclared dependency

FR-002 exposes lookup by **Identity Number** — a national identity number. The controls:

- §12: *"Rate control | Bulk enumeration patterns **SHOULD** be prevented via **enterprise security controls**"* — a `SHOULD`, delegated to a dependency that does not appear anywhere in §4's dependency table and therefore has no owner, no contract, and no availability assumption.
- §16.3: *"Enterprise anti-enumeration controls **SHOULD** apply."* — same weakening, repeated.
- §17 Audit: *"Key type used (not full identity number **when forbidden** — hash/mask allowed)"* — circular. It forbids logging the number when logging it is forbidden, without stating when that is.

*Impact:* FR-002 is a confirm-or-deny oracle over national identity numbers, reachable by any authenticated agent, with rate limiting as advisory and its masking rule self-referential. This is the one finding with direct regulatory exposure. Both controls should be `MUST`, the dependency should be declared in §4 with an owner, and the audit rule should read as an unconditional prohibition on cleartext identity numbers in audit records.

---

## 3. Major Findings

### M-01 — UNVERIFIED / degraded mode has no closure obligation, and permits a Complaint with no customer

BR-001 E3 requires reconciliation: *"wajib reconcile saat Master pulih"*. FR-001 E3 renders this as *"MAY create with `customerVerificationPending=true` without inventing Master attributes"* — the mandatory reconciliation obligation is dropped. Additionally:

- FR-001 §14 Output: *"CustomerId | Yes (**or UNVERIFIED pending flag**)"* — so a persisted Complaint may carry no `CustomerId` at all.
- FR-003 §13 requires *"CustomerId (**or pending key context**)"*. "Pending key context" is defined nowhere in the FRD, the BR catalog, or the RTM.
- No aging queue, maximum pending duration, or supervisor visibility is required. FR-002 §18 offers only an optional threshold notification (`MAY`).

*Impact:* duplicate detection is keyed on `CustomerId`. A Complaint without one is invisible to duplicate detection and to Customer 360 — it silently exits both the data-quality and the customer-context mechanisms, with no requirement that anyone ever notice.

### M-02 — Complaint search index is absent from Database Mapping, and its update semantics are unspecified

BR-001 Data Affected includes *"Indeks pencarian Complaint (BR-003)"*. §14 Database Mapping omits it entirely, despite FR-003 depending on it (E1: "Detection unavailable (index down)") and §15 listing BR-003 as FR-003's "substrate".

Nothing states whether indexing on create is **synchronous or asynchronous**. This is not a technical footnote: if asynchronous, two agents registering the same customer's complaint within the indexing lag will both pass duplicate detection cleanly. Combined with `C-05`, this is the mechanism by which permanent duplicates are actually produced.

### M-03 — Three obligations are created with no owning requirement

| Obligation | Source | Owner |
|---|---|---|
| "MUST require later review" after `duplicateCheckDegraded=true` | FR-003 E1 | none |
| Enrichment of a previously UNVERIFIED Complaint | FR-002 A4 | none |
| "Periodic/recheck after UNVERIFIED Complaint becomes verified" | FR-003 §8 Trigger | none |

Each states a mandatory downstream action with no FR, no actor, no queue, no schedule, and no entry in §17 Out of Scope or the FR-005+ deferral list. The third additionally implies a background scheduled process that appears nowhere in the architecture.

### M-04 — ADR-002's staleness indicator and cache retention policy are not carried forward

ADR-002 is **Accepted** and its Consequences require: *"Perlu UI yang menampilkan 'data as of [timestamp]'"*, plus *"kebijakan retensi dan PII untuk cache lokal"*. The FRD establishes the customer read-model (§14 DM/DB mapping, FR-002 §15.2) but requires **neither** the staleness indicator nor a retention/PII policy. FR-002 §15.2 acknowledges the cache "MAY become stale" without requiring the user ever be told.

### M-05 — Staged attachment "discard" permits physical destruction of customer-supplied evidence

FR-004 A4 step 3: *"If create is cancelled, staged uploads MUST be **discarded or voided** per policy without leaving orphan ACTIVE operational evidence."*

"Discarded" permits physical deletion, which conflicts with BR-012 E3 (*"Hapus fisik oleh user — Ditolak"*), BR-012 Business Constraints (*"history append-only"*), and the FRD's own §15.2 (*"void/supersede — not silent erase"*).

The realistic path makes it worse: an agent uploads the customer's photographs, duplicate detection fires (FR-003), the agent chooses **A2 — open existing Complaint**, and the create is cancelled. The evidence is discarded at precisely the moment it should have been carried to the surviving Complaint. Additionally, only *cancellation* is covered — an **abandoned** session (browser closed, timeout) has no defined behaviour at all.

### M-06 — Attachment anchor invariant is missing

FR-004 §12 requires *"Anchor | Complaint and/or Case reference MUST be valid"*. "Valid" is not the invariant. Nothing requires that the anchor Case **belongs to the anchor Complaint**. As written, an attachment may be bound to Complaint A and Case B where Case B belongs to Complaint C — a direct breach of the Aggregate boundary the document otherwise defends carefully.

### M-07 — "Add Case to existing Complaint" is offered without status qualification, conflicting with BR-004 E1

BR-004 E1 blocks Case creation on a **CLOSED** Complaint. FR-003 Normal Flow step 4 and FR-001 A2 offer "open existing / add Case" with no status precondition, and duplicate candidates are drawn from *"Complaint aktif/recent"* — recent explicitly includes closed ones. §9 FR-003 step 3 shows *"status and open Case indicators"* but no rule prevents selecting a closed candidate for an action that will be refused.

### M-08 — Customer 360 downgraded to `SHOULD`, and depends on an out-of-scope capability

BR-001 Normal Flow step 5 is imperative: *"Sistem menampilkan/menyediakan akses ke Customer 360 View (BR-010)"*. FR-001 step 4 renders it *"System **SHOULD** present or link Customer 360 context"*. Meanwhile §2.3 places *"Customer 360 full view"* out of Batch 1 scope.

The consequence is substantive, not editorial: BR-010 A3 — *"Multi-Complaint aktif — Sorot semua aktif untuk mencegah duplikat"* — is a **duplicate-prevention mechanism**, and it is the human-judgement complement to FR-003's scoring. Batch 1 keeps the algorithmic check and drops the human one, then downgrades what remains to `SHOULD`.

### M-09 — Evidence-integrity and sensitive-access controls are weakened relative to the BR catalog

| Control | BR-CM-CAT-001 | FRD | Effect |
|---|---|---|---|
| Sensitive attachment access audit | BR-012: `Accessed (untuk sensitif)` in the audit set | §16.5 `MAY require audited access`; §17 "when policy requires" | Downgraded to optional |
| Integrity hash | BR-012: *"hash/integritas"* in Attachment History | §14 Output: `Integrity hash | **SHOULD**` | Downgraded |

Attachments here are evidence in a regulated complaint process that may be escalated to Head Office and read by Compliance. An unhashed evidence artifact cannot be shown to be the one that was uploaded. Both should be `MUST`.

### M-10 — Anti-inference control on duplicate detection is a `SHOULD`

FR-003 E4: *"Candidate MUST NOT be leaked; uniform authorized-empty behavior **SHOULD** apply per security policy."* The `MUST` covers the payload; the `SHOULD` covers the observable difference. Since FR-003 returns **scores** and a warning flag, silently removing out-of-scope candidates while returning a different result shape is exactly the side channel that discloses the existence of another unit's complaints for a given customer. The uniformity requirement is the control and must be `MUST`.

### M-11 — Transaction boundary is undefined and, as implied, very large

FR-001 E6 requires audit/timeline failure to fail the business create. Step 10 requires the initial Case *"in the same business transaction"*. FR-004 A4 binds staged attachments *"on successful FR-001 commit"*. Taken together the implied unit of work spans: Complaint + Case + audit + timeline + history + duplicate linkage + attachment binding + search index — with the attachment **binary already committed to external enterprise storage** beforehand.

No compensation or saga semantics are stated, and no behaviour is defined for the specific case of a successful Complaint commit followed by a failed attachment binding. The FRD is right to demand atomicity for audit; it does not bound what else it has pulled inside that boundary.

### M-12 — Notification failure must be recorded in a log ECMP does not own

FR-001 §18: *"failure MUST be recorded in Notification delivery log."* Per §4 and BR-CM-CAT-001's scope table, Notification Platform ownership sits **outside** ECMP. If the platform is unavailable — the common failure — its delivery log is equally unavailable, so the mandatory record cannot be written. No ECMP-side outbox or delivery-status projection is required, despite **ADR-009** having already established the outbox pattern for precisely this class of problem.

### M-13 — No NFR linkage for a synchronous, unbounded pre-commit check

Duplicate detection runs synchronously before every create confirm, over a configurable time window, returning *"Score per candidate | Yes when candidates exist"*. There is no latency budget, no candidate result cap, no timeout, and no degradation trigger on slowness (only on unavailability, E1). FR-002 bounds Master Customer retries; FR-003 bounds nothing. `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md` is not referenced anywhere in the document.

For a high-volume customer with a long configured window, the candidate set is unbounded and sits directly on the intake critical path.

### M-14 — Audit retention is unspecified and `17 Compliance` is unreferenced

BR-016 Business Constraints require *"retensi panjang sesuai compliance"*. The FRD mandates audit content thoroughly across all four FRs but never states a retention period, an immutability enforcement mechanism, or a legal-hold interaction for audit (legal hold appears only for attachments, §15.3). The `17 Compliance` folder is not referenced.

### M-15 — Cited API catalog IDs are ambiguous in the generated catalog

§13 anchors traceability on `API-390` (Create Complaint) and `API-392` (Get Complaint). In `07 API Catalog/API_CATALOG.generated.md` both IDs are **assigned twice**:

- `API-390` → `POST /api/v1/complaints` **and** `GET /api/v1/dashboard/queue`
- `API-392` → `GET /api/v1/complaints/{complaintId}` **and** `GET /api/v1/dashboard/notifications`

The catalog defect is not the FRD's fault, but the FRD inherits it and presents these IDs as stable traceability anchors. Any automated traceability check will resolve them incorrectly.

### M-16 — KPI Impact and the supervisor-queue obligation are dropped in translation

BR-CM-CAT-001 defines **KPI Impact** for every rule; the FRD's 21-section FR template has no KPI section, so all of it is lost — including `Complaint tanpa Case (aging)`, `% Possible Duplicate Override`, and `Time to Register`. These are the measures by which the batch would be judged successful.

Relatedly, BR-001 A4 step 4 requires: *"Supervisor queue menandai Complaint tanpa Case sebagai item yang perlu ditindaklanjuti."* FR-001 A4 has three steps and omits it. The no-Case aging control is therefore absent in both its mechanism and its measure.

### M-17 — Upstream customer merge / retirement is not addressed

Master Customer systems merge and retire customer records. When two `CustomerId`s merge upstream, existing Complaints reference a retired identifier — breaking Customer 360 composition, duplicate detection correlation, and historical reporting. FR-002 A3 handles *inactive*; nothing handles *merged* or *superseded*. Given that ADR-002 fixes ECMP as a pure consumer with no write-back, ECMP cannot correct this itself and must define its reaction.

---

## 4. Minor Findings

- `m-01` — Document Status is "Draft v1.0" while §1.1 declares the document *"normative for Batch 1"*. Draft and normative are not compatible states under the `18 Architecture Governance` lifecycle.
- `m-02` — Recording unit is *"overridable if permitted"* (§13) with no rule for who may override, no audit requirement for the override, and no behaviour defined for an actor belonging to multiple org units.
- `m-03` — Complaint Number: uniqueness is required (§15.5) but format, sequencing, whether numbers must be gapless (frequently an audit requirement), per-year/per-unit reset, and generator-failure behaviour are all unspecified.
- `m-04` — FR-002 A3 requires *"a special flag MUST be recorded"* for an inactive customer. The flag is unnamed, absent from FR-001 §14 Output Data, and absent from §14 Database Mapping.
- `m-05` — Override justification *"Minimum length/content MUST apply"* (FR-003 §12) with no value specified and no corresponding Open Question, unlike the duplicate threshold and window which are properly captured in OQ-CM-B1-003.
- `m-06` — Two BR-016 provisions are not carried into any FR: E3 clock-skew detection (*"Tandai; jangan diam-diam menormalisasi"*) and the constraint that audit records contain no authentication secrets.
- `m-07` — Bulk upload enforces per-file max size and per-action count (FR-004 §12) but no aggregate payload size for the action.
- `m-08` — FR-001 §15.7 correctly requires effective-dated classification config. The same protection is not extended to attachment allowlists, size limits, or duplicate hard-block category lists, whose historical values matter equally when explaining a past decision.
- `m-09` — No linkage to `13 Test Strategy` or `26 Traceability`, despite the FRD carrying a full acceptance-criteria set and an RTM that those documents would consume.
- `m-10` — FR-002 §15.4 permits updating the customer reference *"with full audit trail"* but does not require before/after capture, which BR-018 makes the defining characteristic of History as distinct from Timeline.
- `m-11` — Concurrent create by two agents for the same customer is not addressed in any alternative or exception flow.
- `m-12` — Deceased, dormant, and merged customer states from Master Customer are not addressed; only *inactive* (FR-002 A3).
- `m-13` — Even with §1.1's disclosure, two live documents in one repository both defining `FR-001` and `BR-001` with different meanings is a durable hazard for ID-based tooling, generated indexes, and commit messages. §1.1 warns humans; it does not protect automation.

---

## 5. Recommendations

Ordered by whether they gate implementation.

### Gating — resolve before the FRD is used to plan or build

| # | Recommendation | Addresses | Why |
|---|---|---|---|
| R-01 | Change §2.1 from "implementation-ready" to "specification baseline, pending DEC", or obtain the DEC (OQ-CM-B1-001) and the ADR-014/ADR-015 acceptances first | `C-01` | The repository's own gate rule is *contract frozen before code*; nothing in the foundation is frozen |
| R-02 | Remove **Authorization** from the §4 external dependency table; state that complaint authorization is ECMP-internal per ADR-014 / ADR-008 | `C-02` | §4 is normative and will be read literally; leaving it invites the exact coupling ADR-014 removed |
| R-03 | Either bring minimal "add Case to existing Complaint" into Batch 1, or remove that option from FR-003 Normal Flow, UC-CM-007, and the `ResolvedAsCaseOnExisting` audit event, and record the limitation explicitly | `C-03` | Shipping a warning with no remedy inflates the override path and corrupts the KPI meant to measure intake quality |
| R-04 | Align all four key-cardinality statements to BR-001's **exactly one**, and re-derive FR-002 E5 from that premise | `C-04` | The validation tables are what implementers and testers read; they currently contradict the BR the FRD claims to follow |
| R-05 | Either move channel auto-register (A5) out of Batch 1, or promote per-message-id idempotency out of Future Enhancement into FR-001 with a replay exception flow; add a create-level idempotency key for the human path | `C-05` | Duplicates created this way are permanent by §15.6 and cannot be cleaned up afterwards |
| R-06 | Raise both enumeration controls to `MUST`, declare the enterprise rate-limiting dependency in §4 with an owner, and restate the audit rule as an unconditional prohibition on cleartext identity numbers | `C-06` | The only finding with direct regulatory exposure; the current masking rule is self-referential and unenforceable |

### High priority — resolve in v1.1

| # | Recommendation | Addresses |
|---|---|---|
| R-07 | Restore BR-001 E3's mandatory reconciliation; define "pending key context"; require an aging queue and maximum pending duration for UNVERIFIED Complaints; state explicitly whether a Complaint may persist with no `CustomerId` | `M-01` |
| R-08 | Add the Complaint search index to §14 Database Mapping and state whether indexing on create is synchronous or asynchronous | `M-02` |
| R-09 | Assign an owning requirement (or an explicit deferral entry) to each of the three orphan obligations | `M-03` |
| R-10 | Carry ADR-002's "data as of [timestamp]" indicator and cache retention/PII policy into FR-002 as requirements | `M-04` |
| R-11 | Remove "discarded" from FR-004 A4 — void-with-reason only; define abandoned-session behaviour; state whether staged evidence follows the actor to the surviving Complaint under FR-003 A2 | `M-05` |
| R-12 | State the attachment anchor invariant: anchor Case MUST belong to anchor Complaint | `M-06` |
| R-13 | Qualify "open existing / add Case" by Complaint status, consistent with BR-004 E1 | `M-07` |
| R-14 | Restore Customer 360 to the BR's imperative form and define the minimum 360 subset in Batch 1 scope — specifically BR-010 A3 active-complaint highlighting | `M-08` |
| R-15 | Raise sensitive-attachment access audit and integrity hash to `MUST` | `M-09` |
| R-16 | Raise FR-003 E4 uniform-empty behaviour to `MUST` | `M-10` |
| R-17 | State the transaction boundary explicitly and define behaviour for post-commit attachment binding failure | `M-11` |
| R-18 | Require an ECMP-side notification outbox/delivery-status projection per ADR-009, rather than mandating a record in an externally owned log | `M-12` |
| R-19 | Reference `ECMP_NFR_Specification_v0.1.md`; add a latency budget, candidate cap, and timeout for FR-003 | `M-13` |
| R-20 | Add audit retention, immutability enforcement, and legal-hold interaction; reference `17 Compliance` | `M-14` |
| R-21 | Resolve the `API-390` / `API-392` collisions in the API catalog before citing them as traceability anchors | `M-15` |
| R-22 | Add a KPI Impact section to the FR template and restore BR-001 A4's supervisor-queue flagging | `M-16` |
| R-23 | Add customer merge/retirement handling, or record it as an explicit Open Question with an owner | `M-17` |

### Housekeeping

`R-24` — Address `m-01` … `m-13` in v1.1; several (`m-03` Complaint Number policy, `m-05` justification minimum) are better handled as new Open Questions with named owners than as invented values.

---

## 6. Overall Score

**73 / 100**

| Dimension | Score | Basis |
|---|---|---|
| Architecture consistency | 70 | Locked decisions held throughout; undermined by `C-02` boundary inversion and `C-01` unratified foundation |
| Domain consistency | 85 | Aggregate, Multi-Case, Assignment-on-Case, SLA-on-Case handled correctly and without leakage |
| Business Rule compliance | 72 | Traceability genuine and complete; four normative downgrades from BR (`C-04`, `M-01`, `M-08`, `M-09`) |
| Requirement completeness | 65 | Orphan obligations (`M-03`), missing index mapping (`M-02`), KPI section dropped (`M-16`) |
| Requirement ambiguity | 62 | `C-04` cardinality, "pending key context", circular masking rule, unnamed inactive-customer flag |
| Requirement conflicts | 60 | `C-03` scope conflict, `C-04` self-contradiction, `M-07` closed-Complaint conflict |
| Missing edge cases | 65 | Concurrency, merge/retirement, abandoned session, post-commit binding failure |
| Security | 62 | `C-06` enumeration, `M-09` evidence integrity, `M-10` inference oracle — controls present but weakened to `SHOULD` |
| Audit | 80 | Genuinely strong; E6 atomicity discipline is exemplary; retention and clock-skew missing |
| Scalability | 63 | Synchronous unbounded pre-commit check, no NFR linkage, oversized implied transaction |
| Maintainability | 80 | Consistent template, configuration-first, honest §1.1 disclosure and Open Questions |

**Assessment.** This is a competent, disciplined FRD that is closer to ready than the finding count suggests. Its problems are concentrated in two places: a foundation that has not yet been ratified through the repository's own governance, and a pattern of softening BR imperatives into `SHOULD` at precisely the points where the control matters — enumeration, evidence integrity, inference, and Customer 360. The Aggregate discipline, the audit atomicity rule, the traceability matrix, and the namespace disclosure are all of a standard worth preserving as the template for later batches.

Six gating recommendations (`R-01` … `R-06`) stand between this document and safe implementation. None of them requires redesign.

---

## Related

- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.0.md` (subject)
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001)
- `18 Architecture Governance/reviews/ECMP_ADR_014_Architecture_Review_v1.0.md` (GOV-REV-014)
- `05 Architecture Decision Records/` — ADR-002, ADR-003, ADR-008, ADR-009, ADR-014, ADR-015
- `07 API Catalog/API_CATALOG.generated.md`
- `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`, `17 Compliance`, `13 Test Strategy`
