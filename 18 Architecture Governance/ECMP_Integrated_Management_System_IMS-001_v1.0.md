# ECMP Integrated Management System (IMS)
Document ID: **IMS-001**  
Version: 1.0  
Date: 2026-07-31  
Role: ECMP Management System Architect  
Status: **Proposed — Master Index**  

| Field | Value |
|---|---|
| Nature | Index & mapping only — does **not** rewrite, replace, or redefine approved documents |
| Governance phases | Unchanged (0–4.5 closed; Phase 5 runbook PRE-APPROVED; RAB NO-GO) |
| Philosophy | Complaint Module first; integration mechanism may change; domain stable |
| Scale path | Lab → Production → Multi-module → Platform **without new governance phases** |

---

# Executive Summary

IMS-001 is the **master index** that connects existing ECMP policies, standards, procedures, runbooks, checklists, and evidence into one management system.

It does **not** create new governance phases, does **not** alter RAB decisions, and does **not** replace SEC-BASE-001, SEC-STD-001, ADR, or Phase 0–5 artefacts.

**Scaling rule:** the same hierarchy (Policy → Standard → Procedure → Runbook → Checklist → Evidence) applies from Lab to Enterprise. What changes is **maturity and ownership** (module vs platform), not the philosophy.

| Stage | Focus | Ownership |
|---|---|---|
| 1 Lab | Current | ECMP module |
| 2 Production | Module production-bound | ECMP + ops |
| 3 Multi-module / Platform | Shared services | **Future Work — Platform** |
| 4 Enterprise | Corporate IdP/SIEM/org | **Future Work — Enterprise Platform** |

---

# IMS Architecture

```text
Level A  Policies          (why / non-negotiables)
Level B  Standards         (what “good” means)
Level C  Procedures        (how work is organized)
Level D  Runbooks          (how operators execute)
Level E  Checklists        (verify steps)
Level F  Evidence          (proof / audit trail)
         ↑
    IMS-001 master index + lifecycle + dashboards
```

Traceability spine:

`Requirements / FR / BR → Standards (B) → Procedures (C) → Runbooks/Checklists (D/E) → Evidence (F) → Approval`

---

# SECTION 1 — Document Hierarchy

| Level | Class | Role | Examples (existing — not rewritten) |
|---|---|---|---|
| **A** | Policies | Binding intent | CLAUDE.md / ECMP Constitution · DEC-* · ADR decisions (as policy outcomes) |
| **B** | Standards | Normative baseline | SEC-STD-001 · SEC-BASE-001 · ADR-007/012/014/015 · coding/deploy standards in `08`/`14`/`21`/`22` |
| **C** | Procedures | Managed work methods | Execution Readiness Program · Delivery Plan · AuthN migration plan · Architecture review process (`18`) |
| **D** | Runbooks | Step execution | Phase 5 Release Execution Runbook (PRE-APPROVED) · deploy README cutover/rollback · DR steps in SEC-BASE §9–10 |
| **E** | Checklists | Gate verification | Host/Domain Migration · Security/Deploy sign-off templates · Server provisioning lists in SEC-BASE §13 · RC checklists in `16` |
| **F** | Evidence | Auditable artefacts | `deploy/evidence/*` Phase 0–4.5 · forensics · restore-drill · approval sheets · posture |

---

# SECTION 2 — Document Registry

Lifecycle codes: D=Draft · R=Review · A=Approved · P=Published · V=Revised · X=Deprecated · Z=Archived  

Review: M=Monthly · Q=Quarterly · S=Semiannual · Y=Annual · E=Event-driven  

| Document ID | Title | Owner | Purpose | Lifecycle | Review | Approval | Supersedes | Dependencies |
|---|---|---|---|---|---|---|---|---|
| IMS-001 | Integrated Management System | Mgmt System Architect | Master index | P (proposed) | Y | Architecture Board | — | All below |
| CONST-001 | ECMP Constitution / CLAUDE.md | Program Owner | North Star & scope filters | A | Y | Board | — | — |
| GOV-000 | Architecture Governance README | Arch Board Chair | Arch governance entry | R/A | S | Board | — | ADR process |
| ADR-* | Architecture Decision Records | Architects | Binding design decisions | A/P | E | Board | prior ADR ver | GOV-000 |
| DEC-* | Project Decisions (`27`) | PO / Board | Scoped decisions | A/P | E | Board | — | FR/BR |
| SEC-STD-001 | Security Standards v0.1 | Security Architect | App AuthN/Z, audit, secrets | A | Q | Board | — | ADR-007/008 |
| SEC-BASE-001 | Security Baseline Standard v1.0 | Security Architect | Portable host/domain/DR/release security | P (proposed) | Q | Board | extends SEC-STD-001 | Lab posture, migration |
| SEC-AUTH-001 | Target Auth Architecture | Security Architect | Mode B target design | P | S | Board | — | ADR-012 |
| SEC-MIG-001 | AuthN Migration Rollout | Security Architect | Auth migration procedure | P | S | Board | — | SEC-AUTH-001 |
| REL-GOV-P0 | Git Forensics Phase 0 | Release Mgr | Evidence collection | A (evidence) | E | RM | — | Git |
| REL-GOV-REC | Repository Reconciliation | Release Mgr | SoT binding | A | E | Board | — | Remote refs |
| REL-GOV-P1 | Phase 1 Decision Matrix | Release Board | Commit actions | A | E | Board | — | Phase 0 |
| REL-GOV-P2 | Phase 2 Governance Gate | Gov Board | Prep gate | A | E | Board | — | P1 |
| REL-GOV-P3 | Phase 3 Release Prep Plan | Release Mgr | Prep plan | A | E | Board | — | P2 |
| REL-GOV-P4 | Phase 4 RAB | RAB | Go/No-Go | A (NO-GO) | E | RAB | — | P3 |
| REL-GOV-P45 | Phase 4.5 Closure | Gov Office | Cycle close | A | E | Gov Office | — | P4 |
| REL-RUN-P5 | Phase 5 Execution Runbook | Release Mgr | Execute promote | P PRE-APPROVED | E | RAB GO required | — | P4 GO |
| REL-PROG-ERP | Execution Readiness Program | Release Mgr | WP-01…08 to exit NO-GO | A | E | Program Mgr | — | P4.5 |
| REL-PROG-DEL | Delivery Plan / Execution Manual | Program Mgr | Operationalize WPs | A | E | Program Mgr | — | ERP |
| OPS-MIG-001 | Host/Domain Migration Checklist | Deploy Lead | Safe FQDN/host move | D→R | E | Deploy+RM | — | SEC-BASE §10 |
| OPS-SEC-LAB | Lab Security Posture | Sec Reviewer | L1 dispositions | D→R | E | Sec+Deploy+RM | — | Phase 0 §7 |
| OPS-SEC-SO | Security Review Sign-off | Sec Reviewer | S-01…S-09 | D unsigned | E | Sec | — | OPS-SEC-LAB |
| OPS-DEP-SO | Deployment Review Sign-off | Deploy Lead | D-01…D-08 | D unsigned | E | Deploy | — | OPS-MIG-001 |
| OPS-RBK-001 | Rollback Pack | Deploy+RM | Release rollback | D unsigned | E | Deploy+RM | — | REL-RUN-P5 |
| EAR-00…27 | Numbered knowledge set | Domain owners | Blueprint→ops knowledge | A/P mix | S/Y | Board | — | Traceability `26` |
| AI-POL | ai-platform policies | AI Platform | Agent rules | A | Q | AI owner | — | ai-rules |

*IDs in REL-\* / OPS-\* are **registry aliases** for IMS indexing; they do not rename files on disk.*

---

# SECTION 3 — Lifecycle

```text
Draft → Review → Approved → Published → Revised ⇄ Approved
                              ↓
                         Deprecated → Archived
```

| State | Meaning | Rule |
|---|---|---|
| Draft | Work in progress | Not binding for RAB PASS |
| Review | Peer/owner review | Comments only |
| Approved | Binding for its scope | Signatures recorded |
| Published | Discoverable via IMS | Linked from IMS-001 |
| Revised | New version in flight | Prior remains until Approved |
| Deprecated | Do not use for new work | Pointer to successor |
| Archived | Retained for audit | No active links except history |

**IMS rule:** Evidence (Level F) is **Approved as record** even when decision is NO-GO (e.g. Phase 4).

---

# SECTION 4 — Governance Mapping

| Phase | Supporting documents (existing) | Level |
|---|---|---|
| Reconciliation | Repository Reconciliation | F/C |
| Phase 0 | Git Forensics | F |
| Phase 1 | Decision Matrix | F/C |
| Phase 2 | Governance Gate | F/C |
| Phase 3 | Release Preparation Plan · split/base drafts · sign-off templates | C/E/F |
| Phase 4 | RAB NO-GO record | F |
| Phase 4.5 | Governance Closure | F |
| Prep to re-RAB | Execution Readiness · Delivery Plan · WP artefacts | C |
| Phase 5 (blocked) | Release Execution Runbook PRE-APPROVED | D |
| Standing | ADR · DEC · GOV-000 · CONST-001 · IMS-001 | A/B |

No new phases introduced.

---

# SECTION 5 — Operations Mapping

| Operational activity | Procedure (C) | Runbook (D) | Checklist (E) | Evidence (F) |
|---|---|---|---|---|
| Exit RAB NO-GO | ERP · Delivery Plan | — | WP DoD · Approval Matrix | Signed sheets |
| Domain / subdomain change | SEC-BASE §10 | deploy cutover notes | OPS-MIG-001 §A | A-09 pack |
| VPS / cloud move | SEC-BASE §10 | DR/host steps | OPS-MIG-001 §B · SEC-BASE §13.1/13.4 | B-11 pack |
| Security review | WP-04 | — | Security Sign-off | Lab posture + signed S-* |
| Deployment review | WP-05 | — | Deploy Sign-off | Signed D-* |
| Rollback | Rollback Pack | Phase 5 §5 (when authorized) | Emergency rollback checklist | Rollback logs |
| Backup / restore drill | SEC-BASE §9 | restore procedure | DR checklist | restore-drill / backup-verify |
| Release promote | — | Phase 5 Runbook | CP-1…CP-5 | SHA register · PR · merge |

---

# SECTION 6 — Security Mapping

| Control theme | Security Baseline | Deployment Review | Migration Checklist | Evidence |
|---|---|---|---|---|
| Secrets / env | SEC-BASE §3 | D-01/env | Rotate on move | S-01/S-02 sheets · forensics §7 |
| Edge / TLS / docs | §4 §6 | D-02 | DNS+cert validation | S-04 · Caddy evidence |
| Auth / JWT / Mode | SEC-STD · SEC-BASE §2 §6 · DEC-020 | — | Reopen S-03 on move | Lab posture · S-03/S-05 |
| Rate limit / XFF | §6 | — | Post-move verify | S-05 |
| IAM / Users UI | §2 §6 | — | Lab-only reopen S-07 | S-06/S-07 |
| Host hardening | §4 | D-06 UFW OOG | §B provision | hardening evidence |
| Backup/DR | §9 | D-03/D-04 | B-02/B-06 | backup-verify · restore-drill |
| Release gate | §11 | Full D-* | — | R4 Security Sign-off |

---

# SECTION 7 — Architecture Mapping

| Layer | Primary standards / ADRs | Ops artefacts |
|---|---|---|
| Infrastructure | ADR-010 · SEC-BASE §4 · `14 Deployment` | VPS README · firewall · MIG checklist |
| Containers | SEC-BASE §5 · compose prod overlay | Deploy sign-off D-01 |
| Application | ADR-004/005/013 · SEC-STD · `21`/`22` | OpenAPI · RBAC docs |
| Database | `05`/`06` · SEC-BASE §7 | backup scripts · restore drill |
| Network / Edge | Caddy · ECMP_DOMAIN · SEC-BASE §6 HTTPS | MIG §A/B · D-02 |
| Storage | Volumes · backup media controls | backup evidence |
| Configuration | Config-first · env templates · SEC-BASE §3 | `.env.example` / `.env.prod.example` placeholders |

---

# SECTION 8 — Evidence Mapping

| Artefact (path under `deploy/evidence/` unless noted) | Producer | Reviewer | Retention | Purpose |
|---|---|---|---|---|
| Git_Forensics_Phase0_* | Forensics collector | Release Board | ≥1 year / release+1 | P0 proof |
| Repository_Reconciliation_* | Reconciler | Board | ≥1 year | SoT binding |
| Phase1…Phase45_* | Boards / Gov Office | Board | ≥1 year | Gate history |
| Phase5_*_PREAPPROVED_* | Release Mgr | RAB | Until superseded +1y | Execution authority bound |
| Execution_Readiness_* · Delivery_Plan_* | RM / Program Mgr | Program Mgr | Until M7+1y | WP program |
| Split_Plans_* · Base_SHA_* · Path_Overlap_* | Tech Lead | TL/RM | Until promote+1y | Prep |
| Security/Deploy/Rollback/Approval/Residual_* | Owners | Gate owners | ≥1 year | Sign-off |
| Lab_Security_Posture_* | Sec Architect | Sec | Until L3 or superseded | L1 baseline |
| Host_Domain_Migration_* | Deploy | Deploy+RM | Each move +1y | Migration |
| backup-verify / restore-drill / hardening | Ops | Deploy | ≥1 year | Ops integrity |
| `10 Security…/SEC-BASE-001` | Sec Architect | Board | Standing | Standard (not Level F) |

Location convention today: **`deploy/evidence/`** for release/ops evidence; numbered EAR folders for standing standards. Target layout in §12 may migrate **without** changing document meaning.

---

# SECTION 9 — Traceability Matrix

| Requirements / intent | Standards (B) | Procedures (C) | Evidence (F) | Approval |
|---|---|---|---|---|
| Stable Complaint domain | CONST-001 · ADR-014/015 | — | — | Board |
| SoT Batch-1 vs lab VPS | — | Reconciliation | REL-GOV-REC · REC file | Board |
| Safe Git promote | Phase 1–3 decisions | ERP · Delivery | P1–P45 · split/base | RAB |
| Portable domain/host | SEC-BASE-001 | MIG procedure | MIG checklist + move evidence | Deploy+RM |
| AuthN/Z | SEC-STD · ADR-007/008/012 | SEC-MIG-001 | Auth tests / reviews | Sec/Board |
| Release auditable | SEC-BASE §11 · REL-RUN-P5 | WP-07/08 | Sign-offs · SHA register | RAB GO |
| DR | SEC-BASE §9 | Restore drill proc | restore-drill | Deploy |

Spine: **Requirements → Standards → Procedures → Evidence → Approval** (runbooks/checklists sit under Procedures for execution).

---

# SECTION 10 — Review Schedule

| Cadence | Scope |
|---|---|
| **Monthly** | Access & firewall (ops); backup success; cert expiry; open WP/issue register; doc draft aging |
| **Quarterly** | SEC-STD / SEC-BASE; Lab posture vs reality; restore drill; dependency window; IMS registry accuracy |
| **Semiannual** | GOV-000 · ADR index · Architecture review forms · Auth target docs |
| **Annual** | CONST-001 · IMS-001 · full maturity stage assessment (Lab vs Production) |
| **Event** | Domain/VPS move; RAB; incident; major ADR; staff leave (secret rotation) |

---

# SECTION 11 — Versioning Policy

| Change | Version | Example |
|---|---|---|
| Incompatible philosophy / structure | **Major** | IMS-001 → IMS-002 or v2.0 |
| New section / registry rows / mappings | **Minor** | v1.1 |
| Typos, links, metadata | **Patch** | v1.0.1 |

**Numbering:** `ID` stable (IMS-001); file may include `_v1.0`.  
**Change history:** table at document end (date, ver, summary, author).  
**Evidence files:** prefer dated suffix `YYYYMMDD` rather than semantic version.

---

# SECTION 12 — Repository Structure

**Recommend (logical). Physical migration is optional and must not break EAR numbered folders.**

```text
docs/
  ims/
    IMS-001_Integrated_Management_System_v1.0.md   # this index (or pointer)
  standards/          # mirrors / links to 05, 10, 14, 21…
  procedures/         # ERP, Delivery Plan, review process
  runbooks/           # Phase 5, deploy cutover, DR
  checklists/         # migration, provisioning, sign-off templates
  evidence/           # ← may alias deploy/evidence/
  templates/          # 24 Templates + sign-off blanks
  archive/            # deprecated/superseded
```

**Current ECMP reality (canonical knowledge):** folders `00`–`27`, `ai-platform/`, `deploy/evidence/`.  
IMS treats those as **authoritative locations**; `docs/` layout above is the **target catalog view** for Stage 2+ without forcing a big-bang move.

---

# SECTION 13 — Quality Management

| Process | Rule |
|---|---|
| Document Review | Owner completeness vs IMS level class |
| Peer Review | Second role (Sec/Deploy/Arch) before Approved |
| Approval Workflow | Per registry Approval Authority; signatures in evidence or doc header |
| Exception Process | Use `18 Architecture Governance/reviews/EXCEPTION_REQUEST.md` |
| Waiver Process | Written, time-bound, risk owner, linked to RAB “GO WITH WAIVERS” only when RAB convened — **no silent waivers** |

---

# SECTION 14 — Management Dashboard

### Governance Dashboard
| KPI | Source |
|---|---|
| RAB status | Phase 4 record |
| Open WP count | Delivery Plan |
| Unsigned gates | Approval Matrix |
| ADR freshness | ADR index |

### Security Dashboard
| KPI | Source |
|---|---|
| S-01…S-09 status | Sign-off / Lab posture |
| Lab acceptances open | OPS-SEC-LAB |
| Secret rotation on last move | MIG evidence |
| Cert days-to-expiry | Ops |

### Operations Dashboard
| KPI | Source |
|---|---|
| Backup / restore last drill | evidence |
| Firewall/SSH posture | hardening notes |
| Migration checklist completion | OPS-MIG-001 |

### Release Dashboard
| KPI | Source |
|---|---|
| Phase 5 authorized? | RAB |
| Base SHA locked? | Base SHA Lock |
| Split plans approved? | Split Plans |
| Evidence pack % | Pack README |

### Migration Dashboard
| KPI | Source |
|---|---|
| Domain moves YTD | MIG evidence |
| Host moves YTD | MIG evidence |
| Post-move reopen items closed | Lab posture |

### Documentation Dashboard
| KPI | Source |
|---|---|
| Registry rows Draft vs Approved | IMS §2 |
| Broken links / missing evidence | Quarterly IMS review |
| Deprecated not archived | §3 |

---

# SECTION 15 — Roadmap

| Stage | Name | IMS focus | Out of scope reminder |
|---|---|---|---|
| **1** | Lab | Operate L1; complete WP-01…08; keep evidence pack; portable env | Not production IdP |
| **2** | Production | L3 controls; RAB GO; Phase 5 when authorized; SEC-BASE §11 | Not multi-module platform |
| **3** | Platform | Shared identity/notification/org **contracts**; same IMS levels | **Future Work** — not Complaint domain rewrite |
| **4** | Enterprise | Corporate controls consumed by ECMP | **Future Work — Enterprise Platform** |

Philosophy unchanged at every stage: **complete Complaint Module; keep domain stable; ease integration.**

---

# Review Calendar (rollup)

See §10. Next concrete actions under Stage 1:

1. Adopt IMS-001 as index (Board).  
2. Keep weekly Delivery Plan status.  
3. Quarterly: SEC-BASE + IMS registry sync.  
4. Event: each migration runs OPS-MIG-001 under SEC-BASE §10.

---

# Formal Statement

**IMS-001 is the master index for ECMP documentation.**  
Approved documents remain authoritative in their own files.  
IMS connects them; it does not replace them.  
No new governance phases. No Phase 5 execution authority granted.

---

## Change History

| Date | Ver | Summary | Author |
|---|---|---|---|
| 2026-07-31 | 1.0 | Initial IMS master index | Management System Architect |

—*End of IMS-001 v1.0*
