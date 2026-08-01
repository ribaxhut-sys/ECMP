# ECMP Repository Baseline Freeze

| Field | Value |
|---|---|
| ID | BASELINE-01 |
| Document | ECMP Repository Baseline Freeze |
| Version | 1.0 |
| Sprint | BASELINE-01 |
| Type | Repository Governance — Baseline Declaration |
| Mode | Read-only |
| Date | 2026-08-01 |
| Status | 🟢 Official baseline frozen |
| Owner | Enterprise Architecture / PMO |
| Prerequisite chain | PMO-01 · PMO-02 · RRO-01 · EXEC-01 · OPS-01 · KB-01 · CLS-01 · MANIFEST-01 |
| Scope | Declare the repository documentation baseline as frozen. No new requirement. No reopen. No code evaluation. |

> This document **declares** the baseline.  
> It does **not** audit, recommend, roadmap, reopen deferred items, or replace companion documents.

---

## Repository Files Audited (read set)

| Source | Path / locus |
|---|---|
| README | `README.md` |
| Capability Register | `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` (BP-CAP-001) |
| CHANGELOG | `CHANGELOG.md` |
| MANIFEST-01 | `00 Repository Guide/ECMP_Repository_Handover_Manifest_MANIFEST-01_v1.0.md` |
| CLS-01 | session canvas `cls-01-project-closure.canvas.tsx` |
| KB-01 | session canvas `kb-01-project-knowledge-base.canvas.tsx` |
| PMO-01 | session canvas `ecmp-master-capability-status.canvas.tsx` |
| PMO-02 | session canvas `ecmp-implementation-backlog-audit.canvas.tsx` |
| RRO-01 | session canvas `rro-01-release-readiness.canvas.tsx` |
| EXEC-01 | session canvas `exec-01-executive-project-report.canvas.tsx` |
| OPS-01 | session canvas `ops-01-operations-handover.canvas.tsx` |
| Evidence | `deploy/evidence/` |

---

## 1. Repository Baseline Identity

| Item | Baseline value |
|---|---|
| Product | Enterprise Complaint Management Platform (ECMP) |
| Role | Complaint Management business module (ADR-014 / ADR-015) |
| Repository | Enterprise Knowledge Repository (EKR) + application foundation stack |
| EAR index | EAR-IDX-000 (`README.md`) · EAR-IDX-001 (`00 Repository Guide/REPOSITORY_INDEX.md`) |
| Business SoT | Blueprint v2.1 (DEC-001) |
| Capability SoT | Capability Register BP-CAP-001 |
| Navigation SoT | MANIFEST-01 |
| Not | Customer Master system of record (BR-003 / ADR-002) |
| Constitution | `ECMP_CONSTITUTION_001` · `CLAUDE.md` |

---

## 2. Repository Version

| Item | Baseline value |
|---|---|
| Annotated candidate tag | `v1.2.0-rc.1` |
| Commit (tag) | `6890f50` (`6890f50d8243ba30589a3d88f0c0efcef791ce01`) |
| Tag subject | finalize CAP-008 Mode A REL-RC-001 PASS for v1.2.0-rc.1 |
| CHANGELOG form | Keep a Changelog · SemVer (REL versioning policy) |
| Other annotated RC tags present | `v1.0.0-rc4` · `v1.1.0-rc.1` |
| Application stack SoT paths | root `backend/` · `frontend/` · `database/` · Compose |
| Historical / optional packs | `implementation/` |

This freeze records the **documentation / evidence baseline** associated with the above version identity. It does not authorize a new release tag.

---

## 3. Repository Scope

| In baseline scope | Recorded as |
|---|---|
| EAR folders `00`–`27` | Knowledge / governance SoT |
| Contracts | API Catalog · Event Catalog · Data Dictionary |
| Application foundation | Mode A delivery artifacts under root stack |
| Release & ops docs | `16` · `15` · `docs/deployment/` · `deploy/evidence/` |
| AI layers | `ai-platform/` (canonical) · `ai/` (compatibility) |
| Session audit / handover chain | PMO → RRO → EXEC → OPS → KB → CLS → MANIFEST |

| Explicitly outside this freeze | Recorded locus |
|---|---|
| New requirements | Forbidden by BASELINE-01 rules |
| Reopening Stay Deferred capabilities | Forbidden; Register remains SoT |
| Enterprise Platform–owned surfaces | Authentication, SSO, directory, org, portal, global notification, identity audit (README / ADR-014) |
| Blueprint Out of Scope items | DEC-001 / Register notes |

---

## 4. Repository State

State declaration only — sourced from companion packages and Register. No re-evaluation.

| Layer | Baseline state (as recorded) |
|---|---|
| **Business** | Blueprint Approved · Capability Register Active · BR/FRD set present |
| **Architecture** | ADR set present · Mode B Accepted with Conditions · Mode B implementation Deferred / CLOSED (C-7) |
| **Engineering** | Foundation + Mode A lab delivered (as recorded in Register / CLS-01 / MANIFEST-01) — this freeze does not evaluate code |
| **Testing** | Test Strategy Active · lab RC evidence present · shared/prod UAT authorization gated (as recorded in CLS-01 / RRO-01) |
| **Release** | Lab RC `v1.2.0-rc.1` tagged · FINAL_RELEASE_REVIEW records production **NOT READY FOR RELEASE** |
| **Operations** | Runbooks present · bak/rcv evidence present · OPS-01 handover indexed |
| **Governance** | CAP-008 Program CLOSED · PMO/RRO/EXEC/OPS/KB/CLS/MANIFEST chain complete |
| **Knowledge** | EAR `00`–`27` · KB-01 · MANIFEST-01 master TOC |

---

## 5. Capability Baseline

Source: **Capability Register only** (`BP-CAP-001`). Status and disposition copied as recorded. No capability review performed in BASELINE-01.

| CAP ID | Name | Register status | Portfolio disposition (B2-08) |
|---|---|---|---|
| CAP-001 | Case Registration & Retrieval | Implemented (Sprint-01 slice, Approved) | Remain |
| CAP-002 | Case Assignment | Implemented (Sprint-02B slice, Approved) | Remain |
| CAP-003 | Workflow Status Transition | Implemented (Sprint-02B slice, Approved) | Remain |
| CAP-004 | Customer 360 View | Planned | **Stay Deferred** |
| CAP-005 | Event-driven Notification | Implemented stub (Approved) | Remain (stub) · **Stay Deferred** (prod engine) |
| CAP-006 | SLA Measurement & Breach Detection | Planned · FRD LOCKED | **Stay Deferred** (engine) · FRD LOCKED |
| CAP-007 | Operational Queue Dashboard | Implemented (B2-14) | Remain (Implemented) |
| CAP-008 | Case Management (Batch-2 Mode A) | **Program CLOSED** (lab) — Implemented | Remain (CLOSED) |

---

## 6. Deferred Baseline

Official deferred items only (Register · README · ADR-014/015 · CLS-01 · evidence).

| Item | Official record |
|---|---|
| CAP-004 Customer 360 | Stay Deferred (Register / B2-08) |
| CAP-006 SLA engine (concrete) | Stay Deferred (Register / B2-08); Time Source fulfillment pattern NOT SPECIFIED (B2-23) |
| CAP-005 production notification engine | Stay Deferred (prod) · stub Remain (Register / B2-08) |
| Mode B — Enterprise SSO implementation | CLOSED (C-7) — architecture accepted, implementation deferred (README / ADR-014) |
| Production final release / tag `v1.2.0` | NOT READY FOR RELEASE (`FINAL_RELEASE_REVIEW_v1.2.0_*`) |
| Shared/prod UAT authorization | Gated (as recorded in CLS-01 / release evidence) |

No deferred item is reopened by this freeze.

---

## 7. External Dependencies

**Enterprise Platform only** (as recorded).

| Dependency | Recorded locus |
|---|---|
| IdP / OIDC production contracts (`iss`, `aud`, JWKS / discovery) | `deploy/evidence/EP_HANDOVER_PACKAGE_v1.2.0_20260801.md` · `Mode_B_Blocked_Pending_IdP_Contract_20260801.md` |
| Identity Contract of Record (ADR-015 claim set confirmation) | EP handover · ADR-015 |
| Entitlement signal contract | ADR-017 · SEC entitlement profile · EP handover |
| Organization reference / sync contract | ADR-018 · SEC org-sync profile · EP handover |
| Enterprise-owned identity / org / portal / global notification / identity audit | README Mode B ownership boundary |

ECMP does not invent Enterprise Platform production values in this baseline.

---

## 8. Repository Freeze Statement

The **ECMP repository documentation baseline** is hereby **frozen** as of BASELINE-01 (2026-08-01), anchored to candidate tag `v1.2.0-rc.1` @ `6890f50` and the companion package chain ending in MANIFEST-01.

Any future change to baseline identity, capability disposition, deferred set, contracts, release posture, or ownership boundaries requires **new repository evidence** (decision, ADR, Register update, release evidence, or equivalent governed artifact). This freeze does not itself authorize engineering, architecture invention, capability reopen, or release.

---

## 9. Integrity Statement

All companion documents remain **authoritative** in their original roles:

| Companion | Remains authoritative for |
|---|---|
| Capability Register (BP-CAP-001) | CAP-001…008 status and portfolio disposition |
| MANIFEST-01 | Master table of contents / navigation |
| CLS-01 | Project closure / deferred disposition report |
| KB-01 | Knowledge navigation index |
| PMO-01 / PMO-02 | Capability status and backlog/debt dashboards |
| RRO-01 | Release readiness audit |
| EXEC-01 | Executive project report |
| OPS-01 | Operations handover index |
| `deploy/evidence/*` | Dated evidence packs (release, OPS, EP, B2-*, CAP-008) |
| ADR-014 / ADR-015 (and subordinates) | Module position and enterprise identity architecture |
| CHANGELOG / `16 Release Management/` | Release line and release governance |

BASELINE-01 does **not** duplicate or supersede those documents. It only freezes the baseline that they collectively describe.

---

## 10. Baseline Declaration

As of 2026-08-01, after completion of PMO-01, PMO-02, RRO-01, EXEC-01, OPS-01, KB-01, CLS-01, and MANIFEST-01, the ECMP repository documentation baseline is officially frozen at candidate `v1.2.0-rc.1` @ `6890f50`, with Capability Register CAP-001…008 dispositions unchanged, Stay Deferred items (including CAP-004, CAP-006 engine, CAP-005 prod engine, and Mode B implementation) remaining deferred, and Enterprise Platform IdP/OIDC/org contracts remaining the sole external dependency class recorded for Mode B / production unlock—without introducing requirements, reopening capabilities, evaluating code, or replacing any companion source of truth.

---

## FINAL VERDICT

**ECMP REPOSITORY BASELINE FROZEN**
