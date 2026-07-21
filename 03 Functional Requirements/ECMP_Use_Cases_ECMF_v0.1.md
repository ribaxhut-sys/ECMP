# ECMP_Use_Cases_ECMF_v0.1

| Field | Value |
|---|---|
| ID | UC-DOC-001 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | ECMF PO / QA Lead |
| Approver | Business Owner |
| Status | 🟢 Approved (selaras FRD-001, versi terkini per metadata dokumen) |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## Purpose
Use case naratif untuk slice Sprint-01 (FRD-001): Create Case dan Get Case, sebagai jembatan FRD → Test Strategy (TC-001/002/005).

---

## UC-001 — Create Case

| Field | Value |
|---|---|
| Actor | CS Agent (permission `cases:create`) |
| Goal | Meregistrasi complaint/inquiry tertaut customerId |
| FR | FR-001, FR-001a, FR-001b, FR-001c |
| API | API-001 `POST /v1/cases` |

### Precondition
- User terautentikasi (Bearer token valid) dengan permission `cases:create`.
- `customerId` tersedia dari Customer Master (atau stub mode aktif).

### Main Flow
1. CS mengirim `POST /v1/cases` dengan payload: customerId, caseType (`COMPLAINT`/`INQUIRY`), priority, subject, description, channel (opsional).
2. Sistem memvalidasi payload dan otorisasi.
3. Sistem memvalidasi customerId ke Customer Master; bila stub mode, terima non-kosong dan set `customerVerified=false`.
4. Sistem membuat case: generate `caseId` format `CASE-<10-hex>`, status awal `REGISTERED`, timestamp ISO-8601 UTC.
5. Dalam **transaksi yang sama**: persist case + audit record immutable (actor, action=`case.create`, entity ref, UTC timestamp) + outbox entry.
6. Sistem mengembalikan **201** dengan representasi case penuh.
7. Event **EVT-001 CaseCreated** dipublikasikan setelah persist sukses.

### Alternate / Exception Flows
| ID | Kondisi | Hasil |
|---|---|---|
| A1 | Customer Master stub mode | Case tetap dibuat; `customerVerified=false` di respons |
| E1 | Token hilang/invalid | **401** `UNAUTHENTICATED`, Error envelope `{code, message, details?}` |
| E2 | Token sah tanpa `cases:create` | **403** `FORBIDDEN`, Error envelope |
| E3 | Validasi gagal (customerId/subject kosong, enum salah, melebihi max length) | **400**, Error envelope; tidak ada case, audit create, maupun event |

### Postcondition
- Case tersimpan dengan status `REGISTERED`; audit record immutable ada dalam transaksi yang sama; EVT-001 terpublikasi.

### Test Mapping
- TC-001 (create sukses), TC-005 (audit record dalam transaksi yang sama).

---

## UC-002 — Get Case

| Field | Value |
|---|---|
| Actor | CS Agent / Viewer (permission `cases:read`) |
| Goal | Melihat detail case by id untuk melanjutkan penanganan |
| FR | FR-002 |
| API | API-002 `GET /v1/cases/{caseId}` |

### Precondition
- User terautentikasi dengan permission `cases:read`.
- Case dengan `caseId` dimaksud sudah ada.

### Main Flow
1. User mengirim `GET /v1/cases/{caseId}`.
2. Sistem memvalidasi token dan permission.
3. Sistem mengembalikan **200** dengan seluruh field case (termasuk status, createdAt/updatedAt UTC, customerVerified).

### Alternate / Exception Flows
| ID | Kondisi | Hasil |
|---|---|---|
| E1 | Token hilang/invalid | **401** `UNAUTHENTICATED`, Error envelope |
| E2 | Token sah tanpa `cases:read` | **403** `FORBIDDEN`, Error envelope |
| E3 | `caseId` tidak ditemukan | **404**, Error envelope |

### Postcondition
- Tidak ada perubahan state; read-audit **tidak** dicatat (deferred per FRD-001 §9 / DEC-002).

### Test Mapping
- TC-002 (get by id sukses).

---

## Related
- `ECMP_FRD_ECMF_v0.1.md` (FRD-001, Approved)
- `../10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md`
- `../13 Test Strategy` (TC-001, TC-002, TC-005)
