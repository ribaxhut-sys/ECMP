# BOARD MEETING AGENDA — Mode A Batch-1

| Field | Value |
|---|---|
| Document ID | BOARD-AG-MA-B1-001 |
| Proposed date | External record `EXT-HD-RC-MA-B1-20260801` (2026-08-01) |
| Duration (suggested) | 60–90 minutes |
| Chair | Architecture Board / PMO |
| SoT tip for discussion | `1608245` on `feature/cm-batch1-s2-persistence` |
| Pre-read (mandatory) | `BOARD_DECISION_PACKAGE.md`, `BOARD_DECISION_MATRIX.md`, `RC_GATE_REPORT.md`, `DEC_ID_Collision_Register_20260801.md`, `MISSING_APPROVALS.md`, `EXECUTIVE_STATUS.md` |
| Approvals recorded in this file | **None** |

---

## Attendees (roles)

| Role | Required |
|---|---|
| Architecture Board / PMO | Yes |
| Release Manager | Yes |
| Tech Lead | Yes |
| Solution Architect | Yes |
| QA Lead | Yes |
| Business Owner / Product Owner | Yes |
| Security Reviewer | Recommended (W-S03 / delta) |
| Governance Coordinator (prep only) | Optional |

---

## Agenda

### 1. Project Status (10 min)

- Confirm SoT: SHA `1608245`, branch `feature/cm-batch1-s2-persistence`
- Phase: Release Governance — RC documentation preparation
- Mode: Mode A Batch-1; Mode B CLOSED
- Dashboard: `EXECUTIVE_STATUS.md`
- Claim control: meeting target = Board decisions, **not** Production Ready

### 2. Engineering Completion (10 min)

- G2 Mini Gate Mode A = EXITED
- Regression pack = PASS (103 recorded)
- Phase 4 RAB = GO WITH WAIVERS (limited Phase 5)
- Phase 5 limited + post-P5 = DONE under waivers
- FR-030 / FR-040 = DEFER for Mode A DoD
- Explicit: engineering complete ≠ READY FOR RC

### 3. Open Decisions (25 min)

| ID | Decision | Materials | Outcome needed |
|---|---|---|---|
| B-1 | DEC ID Collision | Collision register; matrix row B-1 | Written choice A / B / C |
| B-2 | Release Tag Strategy | REL-TAG-001; matrix comparison A vs B | Written choice merge-to-main **or** lab waiver |
| B-3 | Mode B remains CLOSED | `Mode_B_Blocked_*` | Affirmation |
| B-4 | SemVer (or delegate to RM) | REL-VER-001 | Choice or formal delegation |

**Rule:** Do not renumber DEC files or cut tags during the meeting unless Board record explicitly authorizes immediate execution owners.

### 4. Risks (10 min)

- W-SOD-1, W-S03 OPEN, W-D07, dual-tree, RTM executed-TC gap, IMS/SEC Baseline gap on tip, security sheet drift, dirty working tree
- Confirm residual risks remain accepted for lab scope (no rewrite of signed Residual sheet)

### 5. Vote (15 min)

| Motion | Options | Quorum / record |
|---|---|---|
| Motion B-1 | **A** | **APPROVED** (`EXT-HD-RC-MA-B1-20260801`) |
| Motion B-2 | **B** (lab waiver→tag) | **APPROVED** (`EXT-HD-RC-MA-B1-20260801`) |
| Motion B-3 | Affirm Mode B CLOSED | **PENDING HUMAN DECISION** |
| Motion B-5 | Authorize post-meeting Action Register sequence | **PENDING HUMAN DECISION** |

B-1 and B-2 recorded from `EXT-HD-RC-MA-B1-20260801`. B-3/B-5 not in external COMPLETE set — left unchanged.

### 6. Action Items (10 min)

- Walk `BOARD_ACTION_REGISTER.md`
- Assign owners / due dates (humans fill dates)
- Confirm STOP: no READY FOR RC claim until U-5 + REL-RC-001 + tag path complete
- Next gate: re-run `RC_GATE_REPORT.md` only after P0 human items close

---

## Meeting outputs (expected artefacts — after humans)

1. Written Board minutes with B-1 / B-2 / B-3 results  
2. Updated Action Register statuses  
3. Handoff to Release Manager for SemVer + freeze (if authorized)  
4. **Not** an automatic RC tag

---

## Explicit out of scope for this meeting

- Software development / feature work  
- Mode B / OIDC enablement  
- API, database, Approved ADR/DEC substance changes  
- Inventing signatures on U-5 or REL-RC-001  

---

*Agenda only — no decisions recorded herein.*
