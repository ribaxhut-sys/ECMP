# ECMP_FRD_ECMF_v0.1

> Nama file `..._v0.1.md` sengaja dipertahankan agar tautan lintas-dokumen stabil; **versi konten otoritatif = field `Version` di header** (saat ini 0.3).

| Field | Value |
|---|---|
| ID | FRD-001 |
| Version | 0.3 |
| Owner | Business Analyst |
| Reviewer | ECMF PO / Solution Architect |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## 1. Overview
FRD minimum untuk Sprint-01: registrasi complaint/inquiry (create case) dan pengambilan detail case (get case), tertaut customer reference dari master (read-only).

Domain: **ECMF** (dengan dukungan konteks CRM untuk customer reference).

## 2. Actors & Roles
| Actor | Role |
|---|---|
| Customer Service (CS) | Membuat dan melihat case (`cases:create`, `cases:read`) |
| Viewer | Melihat case read-only (`cases:read` saja; lihat SEC-RAM-001) |
| System | Emit event CaseCreated; enforce validation |
| Customer Master (external) | Sumber customerId (di luar ownership ECMP) |

## 3. Use Cases / User Stories
1. Sebagai CS, saya ingin membuat case complaint/inquiry yang tertaut customerId agar penanganan tercatat.
2. Sebagai CS, saya ingin melihat detail case by id agar dapat melanjutkan penanganan.

## 4. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-001 | System shall allow authorized CS to create a case with customerId, caseType, priority, subject, description | Must | BR-003, BR-007 | API-001, EVT-001 | TC-001 |
| FR-002 | System shall allow authorized user to retrieve case details by caseId | Must | BR-007 | API-002 | TC-002 |
| FR-001a | On successful create, system shall set initial status `REGISTERED` and generate caseId | Must | BR-001 | API-001 | TC-001 |
| FR-001b | On successful create, system shall emit `CaseCreated` (EVT-001) | Must | BR-004 | EVT-001 | TC-001 |
| FR-001c | On successful create, system shall persist an immutable audit record (actor, action, entity, timestamp) in the same transaction | Must | BR-008 | API-001 | TC-005 |

## 5. Business Rules Reference
- **BR-001** Status transitions follow configured workflow (initial status fixed to REGISTERED in this slice)
- **BR-003** Customer master is read-only reference in ECMP
- **BR-004** Notifications/events only for configured event types
- **BR-007** Case access requires authenticated user with case read/create permission
- **BR-008** Every significant write (create) must produce an immutable audit trail entry (per DEC-003 mapping to BR-CP-03/BR-ECMF-01)

## 6. UI/UX Reference
Out of Sprint-01 UI polish. API-first slice. Future screen refs in `12 UI UX Spec`.

## 7. Data Requirements
### Case (create request)
| Field | Type | Mandatory | Notes |
|---|---|---|---|
| customerId | string | Yes | Reference to external customer master; 1..64 chars |
| caseType | enum | Yes | `COMPLAINT` \| `INQUIRY` |
| priority | enum | Yes | `LOW` \| `MEDIUM` \| `HIGH` \| `CRITICAL` |
| subject | string | Yes | max 200 chars |
| description | string | Yes | max 5000 chars |
| channel | string | No | e.g. CALL, EMAIL, BRANCH |

### Case (response)
| Field | Type | Notes |
|---|---|---|
| caseId | string | System generated |
| customerId | string | |
| caseType | string | |
| priority | string | |
| subject | string | |
| description | string | |
| status | string | Initial `REGISTERED` |
| channel | string \| null | |
| createdAt | datetime | ISO-8601 UTC |
| createdBy | string | user id |
| updatedAt | datetime | ISO-8601 UTC |
| customerVerified | boolean | `false` when Customer Master stub mode (see §8) |

> **Catatan:** kolom DB `updated_by` **sengaja tidak diekspos** di response API (kebijakan kontrak — lihat `21 Technical Standards` §4); `createdBy` diekspos karena dibutuhkan untuk konteks penanganan.

### Identifier & time rules
- `caseId` format: `CASE-<10-hex>` (system generated, current implementation standard)
- All timestamps ISO-8601 **UTC**
- Bearer claims shape (slice): `{userId, permissions[]}`

## 8. Integration Requirements
- Customer Master: validate existence of `customerId` if integration available; if stub mode, accept non-empty customerId and mark `customerVerified=false`.
- Event bus: publish EVT-001 CaseCreated after persistent create succeeds.

## 9. Non-Functional (high-level)
- AuthN required (Bearer token / gateway header)
- AuthZ: role with `cases:create` / `cases:read`
- **Audit (decided per DEC-002, 2026-07-21):** write-audit **required** — every successful create persists an immutable audit record in the same transaction (FR-001c). **Read-audit is deferred** (storage/latency cost not justified for the slice); revisit when multi-principal access exists.
- **Idempotency (decided per DEC-002):** `Idempotency-Key` is **out of scope** for Sprint-01 AC. Revisit when a real multi-client integration exists.

## 10. Acceptance Criteria
### FR-001 Create Case
- Given valid payload and authorized user, when POST `/v1/cases`, then 201 with caseId and status=REGISTERED
- Given missing customerId/subject, then 400 validation error
- Given unauthorized user, then 401/403
- Given successful create, then EVT-001 is produced with the full payload per `events/events.yaml`: caseId, customerId, caseType, priority, subject, status, createdAt, createdBy
- Given successful create, then an audit record exists with actor, action=`case.create`, entity ref, and UTC timestamp (FR-001c)
- Given validation error, then response body follows Error envelope `{code, message, details?}`

### FR-002 Get Case
- Given existing caseId, when GET `/v1/cases/{caseId}`, then 200 with full case fields
- Given unknown caseId, then 404
- Given unauthorized user, then 401/403

## 11. Out of Scope (this FRD version)
- Assignment, status transition matrix penuh, SLA clocks, approval, reopen
- Customer master write-back
- List/search cases (may exist in OpenAPI as future, not required for Sprint-01 DoD)
