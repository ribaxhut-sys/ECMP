# ECMP_FRD_ECMF_Lifecycle_v0.1

| Field | Value |
|---|---|
| ID | FRD-002 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | ECMF PO / Solution Architect |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

> **Draft — belum DoR; implementasi menunggu gate per DEC-002** (Build-1 hanya setelah G0 exit ditandatangani Tech Lead + Solution Architect).

## 1. Overview
Lanjutan FRD-001: assignment (FR-003) dan status transition tervalidasi (FR-004) untuk lifecycle case ECMF. Melengkapi kapabilitas BP-002 (Assignment and status follow configured workflow).

Domain: **ECMF**.

## 2. Actors & Roles
| Actor | Role |
|---|---|
| Supervisor | Assign/reassign case ke handler/unit di unitnya |
| CS Agent / Handler | Menjalankan transisi status pada case yang di-assign padanya |
| System | Validasi transisi terhadap workflow config; emit event; audit |

## 3. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-003 | System shall allow authorized supervisor to assign/reassign a case to a handler/unit | Must | BR-002 | API-003, EVT-002 + EVT-003 | TC-003 |
| FR-004 | System shall allow authorized user to change case status only via allowed transitions per workflow configuration | Must | BR-001 | API-004, EVT-003 | TC-004 |

## 4. State Machine Reference
Status set dan matriks transisi mengikuti baseline `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (**DOM-ECMF-003**):
`REGISTERED → ASSIGNED → IN_PROGRESS → PENDING_REVIEW → CLOSED → REOPENED`.
FRD ini tidak mendefinisikan transisi sendiri; setiap perubahan matriks dilakukan di DOM-ECMF-003.

## 5. Business Rules Reference
- **BR-001** (BR-ECMF-03): transisi status hanya sesuai workflow configuration; override Administrator wajib justifikasi tercatat
- **BR-002** (BR-ECMF-02): assignment memerlukan role/unit berwenang; lintas unit hanya supervisor unit induk, lainnya read-only (baseline DEC-004)
- **BR-008**: setiap write signifikan (assign, status change) menghasilkan audit record immutable dalam transaksi yang sama

## 6. Acceptance Criteria (ringkas, Gherkin)
### FR-003 Assign Case
```gherkin
Scenario: Supervisor assigns a registered case
  Given case berstatus REGISTERED dan user memiliki permission cases:assign pada unit terkait
  When POST /v1/cases/{caseId}/assign dengan assigneeId dan unitId valid
  Then 200, assignee ter-update, status menjadi ASSIGNED
  And EVT-002 CaseAssigned dipublikasikan (caseId, assigneeId, unitId, assignedBy, assignedAt)
  And EVT-003 StatusChanged dipublikasikan (REGISTERED→ASSIGNED) — setiap transisi valid memicu EVT-003 per DOM-ECMF-003
  And audit record tercatat dalam transaksi yang sama (BR-008)

Scenario: Assignment lintas unit oleh non-supervisor ditolak
  Given user bukan supervisor unit induk case
  When POST /v1/cases/{caseId}/assign
  Then 403 FORBIDDEN dengan Error envelope {code, message}
```

### FR-004 Status Transition
```gherkin
Scenario: Valid transition
  Given case berstatus ASSIGNED dan user berwenang
  When POST /v1/cases/{caseId}/status dengan toStatus=IN_PROGRESS
  Then 200, status berubah, EVT-003 StatusChanged (fromStatus, toStatus, changedBy, changedAt)
  And audit record tercatat dalam transaksi yang sama

Scenario: Invalid transition ditolak
  Given case berstatus REGISTERED
  When POST /v1/cases/{caseId}/status dengan toStatus=CLOSED
  Then 400 dengan Error envelope; status tidak berubah; tidak ada event (TC-004)
```

## 7. Dependencies
- **G0 exit** ditandatangani (DEC-002) — prasyarat Build-1
- **G1**: workflow configuration persisten + permission `cases:assign`/`cases:transition` di Role Access Matrix (revisi SEC-RAM-001)
- Traceability: TRC-L-003, TRC-L-004 (Sprint-02, Planned)

## 8. Out of Scope (versi ini)
- SLA clocks & escalation (FR-030, FRD-005), approval berjenjang, reopen flow penuh, bulk assignment.
- Branch/HO escalation, Schedule Slot, Work Order — out of scope per DEC-001.
