# ECMP Repository Handover Manifest

| Field | Value |
|---|---|
| ID | MANIFEST-01 |
| Document | ECMP Repository Handover Manifest |
| Version | 1.0 |
| Sprint | MANIFEST-01 |
| Type | Repository Manifest (master table of contents) |
| Mode | Read-only inventory |
| Date | 2026-08-01 |
| Candidate tag | `v1.2.0-rc.1` @ `6890f50` |
| Status | 🟢 Authoritative navigation document |
| Owner | Enterprise Architecture / PMO |
| Scope | Inventory of what exists — not an audit, dashboard, executive report, or closure report |

> This document is the **master table of contents** for the ECMP repository.  
> It lists existing artifacts only. It does not re-audit, recommend, roadmap, or invent.

---

## Repository Files Audited (read set)

| Area | Path / artifact |
|---|---|
| Root identity | `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `mkdocs.yml` |
| Capability Register | `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` |
| Blueprint | `01 Business Blueprint/` |
| Business Rules | `02 Business Rules/` |
| FRD | `03 Functional Requirements/` |
| ADR | `05 Architecture Decision Records/` |
| Data Dictionary | `06 Data Dictionary/` |
| API Catalog | `07 API Catalog/` (+ `openapi/`) |
| Event Catalog | `08 Event Catalog/` (+ `events/events.yaml`) |
| Traceability | `26 Traceability/` |
| Test Strategy | `13 Test Strategy/` |
| Release Management | `16 Release Management/` |
| Operations Runbook | `15 Operations Runbook/` |
| Evidence | `deploy/evidence/` |
| Governance / closure packs | `18 Architecture Governance/` |
| Session audit packages | PMO-01 · PMO-02 · RRO-01 · EXEC-01 · OPS-01 · KB-01 · CLS-01 (Cursor canvases) |

---

## 1. Repository Identity

| Item | Value |
|---|---|
| Full name | Enterprise Complaint Management Platform (ECMP) |
| Repository role | Enterprise Knowledge Repository (EKR) + application foundation stack |
| EAR index ID | EAR-IDX-000 (root `README.md`) · EAR-IDX-001 (`00 Repository Guide/REPOSITORY_INDEX.md`) |
| Business SoT | Blueprint v2.1 (DEC-001) |
| Architecture position | Complaint Management **business module** inside Enterprise Application (ADR-014 / ADR-015) |
| Not | Customer Master system of record (BR-003 / ADR-002) |
| Application stack SoT | Root `backend/` · `frontend/` · `database/` · Compose |
| Historical / optional packs | `implementation/` |
| Canonical AI layer | `ai-platform/` |
| Compatibility AI pack | `ai/` (sprint briefs under `ai/sprint/`) |
| Release line (CHANGELOG) | Keep a Changelog + SemVer; latest tagged candidate `v1.2.0-rc.1` |
| Constitution | `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md` · `CLAUDE.md` |

---

## 2. Repository Structure

### Numbered EAR folders (`00`–`27`)

| # | Folder | Role |
|---|---|---|
| 00 | Repository Guide | Indexes, standards, ownership, this manifest |
| 01 | Business Blueprint | Blueprint, Capability Register, RACI annex |
| 02 | Business Rules | BR catalogs |
| 03 | Functional Requirements | FRD set + use cases |
| 04 | Solution Architecture | SA + NFR |
| 05 | Architecture Decision Records | ADR-001…018 + CAP-006 architecture concepts |
| 06 | Data Dictionary | DD + ERD Sprint-01 |
| 07 | API Catalog | OpenAPI SoT + generated catalog |
| 08 | Event Catalog | `events.yaml` SoT + generated catalog |
| 09 | Integration Catalog | Customer Master / email gateway |
| 10 | Security and Access Standards | AuthN, RBAC, OIDC/entitlement/org profiles |
| 11 | SLA and KPI Matrix | SLA/KPI matrices |
| 12 | UI UX Spec | UX specifications |
| 13 | Test Strategy | Test strategy, TC catalogs, UAT plans |
| 14 | Deployment Standards | Deploy standards + production checklist |
| 15 | Operations Runbook | Ops, security ops, backup/restore, IdP runbook |
| 16 | Release Management | REL entry point, security gate, approval, evidence templates |
| 17 | Compliance | Compliance pack |
| 18 | Architecture Governance | Board resolutions, CAP-008 closure pack, reviews/ |
| 19 | Reference Architecture | Patterns + CAP-008 Mode A RA |
| 20 | Domain Architecture | ECMF, CRM, Notification, KPI, Queue, Dashboard, Execution, … |
| 21 | Technical Standards | Technical + observability standards |
| 22 | Engineering Handbook | DoD, PR/review, git convention |
| 23 | Assets | Shared assets |
| 24 | Templates | Document / ADR templates |
| 25 | Glossary | `GLOSSARY.md` |
| 26 | Traceability | `traceability.yaml` (machine SoT) + RTM/DTM |
| 27 | Project Decisions | DEC-xxx · OPEN_QUESTIONS |

### Non-numbered hubs

| Hub | Path |
|---|---|
| MkDocs portal | `docs/` |
| Deploy & evidence | `deploy/` · `deploy/evidence/` · `deploy/proxy/` |
| Application | `backend/` · `frontend/` · `database/` |
| Scripts / tools | `scripts/` · `tools/` |
| AI platform | `ai-platform/` · `ai/` |
| Metrics | `metrics/` |
| Compose | `docker-compose.yml` · `docker-compose.prod.yml` · `docker-compose.prod.nginx.yml` |

Folder ownership: `00 Repository Guide/OWNERSHIP_MATRIX.md`.

---

## 3. Business Documents

| Artifact | Path |
|---|---|
| Blueprint v2.1 (official) | `01 Business Blueprint/ECMP_Business_Blueprint_v2.1.docx` |
| Blueprint MD extract | `01 Business Blueprint/ECMP_Business_Blueprint_v2.1_MD_Extract.md` |
| Capability Register (BP-CAP-001) | `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` |
| RACI annex | `01 Business Blueprint/ECMP_RACI_Role_Matrix_Annex_v0.1.md` |
| Business Rules (module) | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` |
| Business Rules v1.0 | `02 Business Rules/ECMP_Business_Rules_v1.0.md` |
| Business Rules Sprint-01 | `02 Business Rules/ECMP_Business_Rules_Sprint01_v0.1.md` |
| FRD Batch-1 v1.0 / v1.1 | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.*.md` |
| FRD Case Management Batch-2 (CAP-008) | `03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md` |
| FRD Escalation/Resolution | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md` |
| FRD KPI/SLA | `03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` |
| FRD Notification / CRM / Dashboard / ECMF / Admin | `03 Functional Requirements/ECMP_FRD_*.md` |
| Use cases ECMF | `03 Functional Requirements/ECMP_Use_Cases_ECMF_v0.1.md` |
| CAP-008 BCS | `docs/product/CAP-008_Case_Management_Business_Capability_Specification_v1.0.md` |
| Glossary | `25 Glossary/GLOSSARY.md` |
| Project decisions | `27 Project Decisions/DEC-*.md` · `OPEN_QUESTIONS.md` |

### Capability Register snapshot (IDs only — status as recorded in register)

| CAP ID | Name |
|---|---|
| CAP-001 | Case Registration & Retrieval |
| CAP-002 | Case Assignment |
| CAP-003 | Workflow Status Transition |
| CAP-004 | Customer 360 View |
| CAP-005 | Event-driven Notification |
| CAP-006 | SLA Measurement & Breach Detection |
| CAP-007 | Operational Queue Dashboard |
| CAP-008 | Case Management (Batch-2 Mode A) |

Portfolio disposition table: same file, section “Portfolio Disposition (B2-08)”.

---

## 4. Architecture Documents

| Artifact | Path |
|---|---|
| Solution Architecture | `04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md` |
| NFR Specification | `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md` |
| ADR index (generated) | `05 Architecture Decision Records/ADR_INDEX.generated.md` |
| ADR-001…018 | `05 Architecture Decision Records/ECMP_ADR_*.md` |
| ADR-CAP006-001 | `05 Architecture Decision Records/ADR-CAP006-001_Evaluation_Mechanism.md` |
| ARC-CAP006-001 Time Source | `05 Architecture Decision Records/ARC-CAP006-001_Time_Source.md` |
| ARC-CAP006-002 Runtime Architecture | `05 Architecture Decision Records/ARC-CAP006-002_Runtime_Architecture.md` |
| Domain Architecture hub | `20 Domain Architecture/README.md` |
| Domain packs | `20 Domain Architecture/{ECMF,CRM,Notification,KPI,Queue,Dashboard,Execution,Workflow,Channel,Delivery,Administration,Core Platform}/` |
| Reference Architecture | `19 Reference Architecture/` |
| Security / Auth profiles | `10 Security and Access Standards/` |
| Constitution | `18 Architecture Governance/ECMP_CONSTITUTION_001_*.md` |
| Program board resolutions | `18 Architecture Governance/ECMP_PROGRAM_BOARD_*.md` |
| CAP-008 Mode A RA | `19 Reference Architecture/ECMP_RA_CAP008_Mode_A_v1.0.md` |

Enterprise module ADRs of record: **ADR-014** (module position) · **ADR-015** (identity contract) · **ADR-016** (protocol binding) · **ADR-017** (entitlement) · **ADR-018** (org sync).

---

## 5. Engineering Documents

| Artifact | Path |
|---|---|
| Technical Standards | `21 Technical Standards/ECMP_Technical_Standards_v1.0.md` (and observability) |
| Engineering Handbook | `22 Engineering Handbook/` (DoD, PR, code review, git) |
| Backend README | `backend/README.md` |
| Frontend README | `frontend/README.md` |
| Frontend architecture docs | `docs/frontend/` |
| Implementation packs (historical/optional) | `implementation/README.md` |
| AI rules | `ai-platform/policies/ai-rules.md` |
| AI workflow | `ai/09_workflow.md` · `docs/lifecycle.md` |
| Sprint briefs | `ai/sprint/` |
| DX launcher | `tools/eos.py` |
| Contributing / repo standards | `00 Repository Guide/CONTRIBUTING.md` · `REPOSITORY_STANDARDS.md` |

---

## 6. Contracts (API · Events · Data Dictionary)

### API Catalog

| Item | Path |
|---|---|
| Catalog README | `07 API Catalog/README.md` |
| Generated catalog | `07 API Catalog/API_CATALOG.generated.md` |
| OpenAPI (normative files) | `07 API Catalog/openapi/` |
| | `case-actions.v1.yaml` |
| | `case-service.v1.yaml` |
| | `cm-case-management.v1.yaml` |
| | `complaint-domain-service.v1.yaml` |
| | `complaint-management-batch1.v1.yaml` |
| | `complaint-management-esc-res.v1.yaml` |
| | `complaint-service.v1.yaml` |
| | `dashboard-queues.v1.yaml` |
| | `queue-service.v1.yaml` |
| | `openapi/drafts/` |

### Event Catalog

| Item | Path |
|---|---|
| Event SoT | `08 Event Catalog/events/events.yaml` (EVT-CAT-001) |
| Generated catalog | `08 Event Catalog/EVENT_CATALOG.generated.md` |

### Data Dictionary

| Item | Path |
|---|---|
| Data Dictionary v1.0 | `06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` |
| ERD Sprint-01 | `06 Data Dictionary/ECMP_ERD_Sprint01_v0.1.md` |

### Integration contracts (related)

| Item | Path |
|---|---|
| Customer Master read | `09 Integration Catalog/ECMP_INT_001_*.md` |
| Email gateway | `09 Integration Catalog/ECMP_INT_002_*.md` |
| OIDC binding profile | `10 Security and Access Standards/ECMP_BINDING_PROFILE_OIDC_ECMP_v0.1.md` |
| Entitlement profile | `10 Security and Access Standards/ECMP_ENTITLEMENT_REPRESENTATION_PROFILE_v0.1.md` |
| Org sync profile | `10 Security and Access Standards/ECMP_ORG_SYNC_INTEGRATION_PROFILE_v0.1.md` |
| EP handover package | `deploy/evidence/EP_HANDOVER_PACKAGE_v1.2.0_20260801.md` |

---

## 7. Governance Documents

| Artifact | Path |
|---|---|
| Architecture Governance hub | `18 Architecture Governance/README.md` |
| Review forms / checklists | `18 Architecture Governance/reviews/` |
| CAP-008 Program Closure Index | `18 Architecture Governance/ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md` |
| CAP-008 Closure Report … Final Decision | `ECMP_PROGRAM_CAP008_001` … `010` (same folder) |
| Board packages (evidence) | `deploy/evidence/BOARD_*.md` |
| Ownership matrix | `00 Repository Guide/OWNERSHIP_MATRIX.md` |
| Repository index | `00 Repository Guide/REPOSITORY_INDEX.md` |
| Decision tree | `00 Repository Guide/DECISION_TREE.md` |
| Enterprise numbering | `00 Repository Guide/ENTERPRISE_NUMBERING.md` |
| Portal governance mirrors | `docs/governance/` |
| Master prompt (module assistant) | `18 Architecture Governance/ECMP_MASTER_PROMPT_001_*.md` |

---

## 8. Operations Documents

| Artifact | Path |
|---|---|
| Operations Runbook hub | `15 Operations Runbook/README.md` |
| Security Operations Runbook | `15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md` |
| Backup Strategy / Operations / Restore / Recovery | `15 Operations Runbook/ECMP_Backup_*.md` · `ECMP_Restore_*.md` · `ECMP_Recovery_*.md` |
| Secret Operations | `15 Operations Runbook/ECMP_Secret_Operations_Guide_v1.0.md` |
| Audit investigation / log inspection | `15 Operations Runbook/ECMP_Audit_*.md` · `ECMP_Log_*.md` |
| IdP Administrator Runbook | `15 Operations Runbook/ECMP_IdP_Administrator_Runbook_v1.0.md` |
| DR/BCP | `15 Operations Runbook/ECMP_DR_BCP_Plan_v0.1.md` |
| Deployment hub | `docs/deployment/README.md` |
| Deployment checklist | `docs/deployment-checklist.md` |
| Startup checklist | `docs/deployment/STARTUP_CHECKLIST.md` |
| Production deployment guide | `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md` |
| TLS / reverse proxy | `docs/deployment/TLS_REVERSE_PROXY.md` |
| Env variable reference | `docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md` |
| Deploy scripts | `deploy/backup-postgres.sh` · `deploy/smoke-lab.sh` · `deploy/proxy/` |
| Compose | `docker-compose.yml` · `docker-compose.prod.yml` |
| OPS evidence | `deploy/evidence/OPS_*.md` · `Observability_Minimum_20260801.md` |

Operator chain (as documented): **REL-SEC → DEP-CHK → START-CHK → OPS → Rollback**.

---

## 9. Release Documents

| Artifact | Path |
|---|---|
| Release Management hub | `16 Release Management/README.md` |
| Release Management policy | `16 Release Management/ECMP_Release_Management_v0.1.md` |
| Release Security Gate | `16 Release Management/ECMP_Release_Security_Gate_v1.0.md` |
| Approval Matrix | `16 Release Management/ECMP_Release_Approval_Matrix_v1.0.md` |
| Evidence template | `16 Release Management/ECMP_Release_Evidence_Template_v1.0.md` |
| RC checklist | `16 Release Management/ECMP_RC_Release_Checklist_v0.1.md` |
| Versioning / git tag policy | `16 Release Management/ECMP_Repository_Versioning_Policy_v0.1.md` · `ECMP_Git_Tag_Convention_v0.1.md` |
| Provenance | `16 Release Management/ECMP_R6-01_Release_Artifact_Provenance_v1.0.md` |
| CHANGELOG | `CHANGELOG.md` |
| Release notes (portal) | `docs/releases/` (`v1.0.0.md`, `v1.2.0.md`, RC notes, rollback, UAT packs) |
| Release prep / inventory / manifest (evidence) | `deploy/evidence/README_Release_Preparation_Pack_20260731.md` · `RELEASE_INVENTORY.md` · `RELEASE_MANIFEST.md` · `RELEASE_TRACEABILITY.md` |
| Final release review | `deploy/evidence/FINAL_RELEASE_REVIEW_v1.2.0_20260801.md` |
| REL assessments | `deploy/evidence/REL_SEC_001_*` · `REL_RC_001_*` · `REL_EVID_001_*` · `REL_APR_OPS_EVID_*` |
| Platform readiness | `deploy/evidence/PLATFORM_READINESS_REVIEW_v1.2.0_PE_20260801.md` |
| Prod config closure | `deploy/evidence/PROD_CFG_CLOSURE_v1.2.0_20260801.md` |
| Mode B blocked note | `deploy/evidence/Mode_B_Blocked_Pending_IdP_Contract_20260801.md` |

Tagged candidates present in git: `v1.0.0-rc4` · `v1.1.0-rc.1` · `v1.2.0-rc.1`.

---

## 10. Evidence Packages

Location: **`deploy/evidence/`** (85 files as of inventory date).

### Classes present

| Class | Examples (filenames) |
|---|---|
| Release / RC | `FINAL_RELEASE_REVIEW_v1.2.0_*`, `REL_*`, `RC_*`, `RELEASE_*`, `Mode_A_Batch1_RC_Readiness_*` |
| Platform / EP | `PLATFORM_READINESS_*`, `EP_HANDOVER_PACKAGE_*`, `Mode_B_Blocked_*` |
| Operations | `OPS_BAK_EVID_*`, `OPS_RCV_EVID_*`, `OPS_DOC_VERIFICATION_*`, backup/restore drills |
| Board / gate | `BOARD_*`, `Phase4_RAB_*`, `Phase5_*`, `G1_Exit_*`, `G2_Mini_Gate_*` |
| Capability Batch-2 | `B2-05` … `B2-23`, `CAP-008_SoT_Closure_*` |
| CI / task evidence | `TASK_007_01_*`, `TASK_007_02_*` |
| Doc sync / signoff | `Doc_Sync_Audit_*`, `Approval_Matrix_Signoff_*`, `Security_Review_Signoff_*` |
| Pack status | `PACK_STATUS_20260801.md`, `EXECUTIVE_STATUS.md` |

Runbook-local evidence: `15 Operations Runbook/evidence/`.

---

## 11. Audit Packages (session handover chain)

These packages were produced as **read-only session canvases** (Cursor), indexing repository evidence. They are **not** duplicated into EAR numbered folders by this manifest. Paths are relative to the Cursor project canvases directory.

| ID | Title | Canvas artifact | Role |
|---|---|---|---|
| **PMO-01** | Master Capability Status | `ecmp-master-capability-status.canvas.tsx` | Capability portfolio status dashboard |
| **PMO-02** | Implementation Backlog & Debt | `ecmp-implementation-backlog-audit.canvas.tsx` | Backlog / debt inventory dashboard |
| **RRO-01** | Release Readiness Master Audit | `rro-01-release-readiness.canvas.tsx` | Release readiness audit dashboard |
| **EXEC-01** | Executive Project Completion Report | `exec-01-executive-project-report.canvas.tsx` | Executive synthesis report |
| **OPS-01** | Operations Handover Package | `ops-01-operations-handover.canvas.tsx` | Operations handover index |
| **KB-01** | Project Knowledge Base | `kb-01-project-knowledge-base.canvas.tsx` | Role-based knowledge navigation index |
| **CLS-01** | Project Closure Package | `cls-01-project-closure.canvas.tsx` | Closure / handover report |

Related (non-ID) session canvases also present: `arb-complete-project-audit`, `completion-simplification-report`, `governance-duplication-report`, `ecmp-production-readiness-audit`, `phase-45-governance-closure`.

**This MANIFEST-01 document does not replace or re-run those packages.** It only records that they exist and points to them.

---

## 12. Repository Completion Summary

Summary only — no re-audit.

| Layer | What exists |
|---|---|
| Business | Blueprint Approved · Capability Register Active (CAP-001…008) · BR/FRD set present |
| Architecture | ADR set present · Domain packs present · Mode B architecture Accepted with Conditions / implementation deferred |
| Contracts | OpenAPI catalog · Event catalog · Data Dictionary · Integration & security profiles |
| Engineering | Foundation stack (`backend/` / `frontend/`) · Mode A lab delivery artifacts · dual-SoT namespaces documented (DEC-020) |
| Traceability / Test | `traceability.yaml` + RTM/DTM · Test Strategy / TC / UAT catalogs |
| Release | REL hub · CHANGELOG · evidence packs · tag `v1.2.0-rc.1` |
| Operations | Runbooks · deploy docs · OPS evidence · Compose / Caddy |
| Governance | Board resolutions · CAP-008 program closure pack · constitution |
| Session audits | PMO → RRO → EXEC → OPS → KB → CLS chain complete as canvases |
| External dependency recorded | Enterprise Platform IdP/OIDC/org contracts (EP handover package) |

---

## 13. Repository Navigation

### Recommended reading order

1. `README.md` — repository identity and architecture position  
2. This manifest — `00 Repository Guide/ECMP_Repository_Handover_Manifest_MANIFEST-01_v1.0.md`  
3. `00 Repository Guide/REPOSITORY_INDEX.md` — EAR folder map  
4. `01 Business Blueprint/` — Blueprint + Capability Register  
5. `02 Business Rules/` → `03 Functional Requirements/`  
6. `05 Architecture Decision Records/` — especially ADR-014 / ADR-015  
7. `07 API Catalog/` → `08 Event Catalog/` → `06 Data Dictionary/`  
8. `26 Traceability/traceability.yaml`  
9. `13 Test Strategy/`  
10. `16 Release Management/` → `CHANGELOG.md` → `deploy/evidence/`  
11. `15 Operations Runbook/` → `docs/deployment/`  
12. `18 Architecture Governance/` (constitution + CAP-008 closure)  
13. Session packages as needed: PMO-01 → PMO-02 → RRO-01 → EXEC-01 → OPS-01 → KB-01 → CLS-01  

### Quick entry by role

| Role | Start here |
|---|---|
| Business / PO | Blueprint · Capability Register · FRD · Register disposition |
| Architect | ADR-014/015 · Solution Architecture · Domain Architecture · Security profiles |
| Backend / Frontend | OpenAPI · Event Catalog · `backend/` / `frontend/` README · Engineering Handbook |
| QA | Traceability · Test Strategy · UAT catalogs |
| Release Manager | `16 Release Management/` · CHANGELOG · `deploy/evidence/FINAL_RELEASE_REVIEW_*` |
| Operator | OPS-01 canvas · `15 Operations Runbook/` · `docs/deployment/` |
| Auditor / PMO | PMO-01/02 · RRO-01 · EXEC-01 · CLS-01 · CAP-008 closure pack |
| Enterprise Platform | `deploy/evidence/EP_HANDOVER_PACKAGE_v1.2.0_20260801.md` |

---

## 14. Repository Boundaries

### ECMP owns

- Complaint / case lifecycle (create, assign, status, escalate, resolve, close, timeline)
- Complaint authorization (roles & permissions applied after Enterprise entitlement gate)
- Complaint KPI / SLA **domain** artifacts (measurement engine status per Capability Register)
- Operational queue dashboard (CAP-007)
- ECMP business notification (stub / domain events as catalogued)
- Application code SoT: root `backend/` · `frontend/`
- EKR documentation `00`–`27`, contracts, evidence, release/ops docs for the module

### Enterprise Platform owns

- Authentication, SSO, User Directory  
- Password management, MFA, Session  
- Organization / Branch / Department directory  
- Enterprise navigation & portal  
- Enterprise global notification  
- Identity audit  

(As stated in root `README.md` / ADR-014 Mode B ownership boundary.)

### Remains deferred / external (as recorded in repository)

| Item | Recorded locus |
|---|---|
| Mode B implementation | ADR-014/015 · C-7 / C-B6-1 · `Mode_B_Blocked_Pending_IdP_Contract_*` |
| Production IdP/OIDC bilateral contracts | `EP_HANDOVER_PACKAGE_*` · PLATFORM_READINESS |
| CAP-004 Customer 360 | Capability Register — Stay Deferred |
| CAP-006 SLA engine (concrete runtime) | Capability Register — Stay Deferred; ARC/ADR CAP-006 present |
| CAP-005 production notification engine | Register — stub remain; prod engine deferred |
| Message broker | ADR-009 deferral |
| Out-of-scope Blueprint capabilities | DEC-001 / Blueprint Out of Scope (e.g. appointment/work order as noted in register) |

---

## 15. Repository Manifest Statement

This **ECMP Repository Handover Manifest (MANIFEST-01)** is the authoritative navigation document for the ECMP repository. It inventories identity, structure, business, architecture, engineering, contracts, governance, operations, release, evidence, and session audit packages that already exist. It is not an audit, not an executive report, not a closure decision, and not a roadmap. All detailed status, readiness, and closure judgments remain in their original source artifacts (Capability Register, ADRs, Release Management, `deploy/evidence/`, CAP-008 closure pack, and the PMO/RRO/EXEC/OPS/KB/CLS session packages). Readers should use this manifest solely as the master table of contents to locate those sources of truth.

---

## FINAL VERDICT

**ECMP REPOSITORY MANIFEST COMPLETE**
