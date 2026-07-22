# ECMP Test Case Catalog

| Field | Value |
|---|---|
| ID | TC-CAT-001 |
| Version | 0.2 |
| Owner | QA Lead |
| Reviewer | BA / Tech Lead |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Spesifikasi formal per Test Case (TC) yang terdaftar di `26 Traceability/traceability.yaml` (TRC-DATA-001). Dokumen ini **tidak** menambah TC baru di luar traceability; ia merinci precondition, langkah, expected result, dan data uji untuk setiap TC, plus status implementasi terhadap tes pytest nyata di `implementation/backend/tests/test_cases.py`.

Aturan status:
- **✅ Implemented** — TC ter-cover oleh fungsi pytest nyata yang disebut per TC (lulus di CI: `backend-ci.yml`).
- **🕓 Planned** — TC belum diimplementasikan; langkah di bawah adalah **draf** yang diturunkan dari AC Gherkin FRD terkait dan **dibekukan saat gate G1/DoR** FRD-nya (lihat `ECMP_Test_Strategy_v0.1.md` §3). Endpoint/payload Planned mengikuti traceability + FRD; kontrak final menunggu OpenAPI merged (contract-first).

Konvensi umum:
- Semua path API berprefix `/v1/` (ADR-006). Semua error mengikuti Error envelope `{code, message, details?}`.
- AuthN slice: Bearer token statis dari environment (ADR-007); 401 = `UNAUTHENTICATED`, 403 = `FORBIDDEN`.
- Data uji sintetis (`CUST-10001`); dilarang data pelanggan nyata (Test Strategy §5).

## Ringkasan

| TC | Judul (traceability.yaml) | Sprint | Status |
|---|---|---|---|
| TC-001 | Create complaint with valid customer succeeds | Sprint-01 | ✅ Implemented |
| TC-002 | Get case by id returns case | Sprint-01 | ✅ Implemented |
| TC-003 | Assign case updates assignee and emits event | Sprint-02 | ✅ Implemented |
| TC-004 | Invalid status transition rejected | Sprint-02 | ✅ Implemented |
| TC-005 | Audit record persisted on create (same transaction) | Sprint-01 | ✅ Implemented |
| TC-006 | List cases paginated and filtered | Sprint-03B | ✅ Implemented |
| TC-010 | Customer 360 retrieval succeeds | Sprint-02 | 🕓 Deferred (CTO decision, ACR-002) |
| TC-020 | Notification stub handles CaseAssigned | Sprint-02 | ✅ Implemented |
| TC-030 | SLA breach event emitted when overdue | Sprint-03 | 🕓 Planned (DoR FRD-005) |
| TC-040 | Dashboard queue view scoped by role/org | Sprint-03 | 🕓 Planned (DoR FRD-006) |

### Pengecualian mapping TC (operational endpoint)
Fungsi pytest yang memverifikasi **endpoint operasional** dikecualikan dari mapping TC → traceability karena bukan functional requirement (tidak ada FR/BR yang ditelusuri). Daftar eksplisit pengecualian:

| Tes pytest | Endpoint | Alasan exempt |
|---|---|---|
| `test_health` | `GET /health` (tanpa auth, di luar prefix `/v1`) | Health check operasional (ADR-006); bukan FR — tidak dibuatkan TC |

Tes operasional lain yang muncul kemudian harus ditambahkan ke tabel ini secara eksplisit, bukan dibiarkan tak terpetakan.

---

## TC-001 — Create complaint with valid customer succeeds

| Field | Value |
|---|---|
| FR | FR-001, FR-001a, FR-001b |
| BR | BR-001, BR-003, BR-007 |
| API | API-001 `POST /v1/cases` |
| EVT | EVT-001 CaseCreated |
| Trace link | TRC-L-001 (Sprint-01, Approved) |

**Precondition**
- Service berjalan dengan skema DB bersih (fixture `fresh_db`).
- Principal terautentikasi dengan permission `cases:create` (Bearer `dev-token` slice, ADR-007).
- Customer Master mode stub aktif (INT-001) — `customerId` non-empty diterima, `customerVerified=false`.

**Langkah**
1. Kirim `POST /v1/cases` dengan header `Authorization: Bearer <token cases:create>` dan payload (contoh dari OpenAPI `examples.complaint`):

```json
{
  "customerId": "CUST-10001",
  "caseType": "COMPLAINT",
  "priority": "HIGH",
  "subject": "Billing discrepancy",
  "description": "Incorrect charge on invoice",
  "channel": "CALL"
}
```

2. Baca response body.

**Expected Result**
- Status code **201**.
- Assertion kunci: `status == "REGISTERED"` (FR-001a), `caseId` berformat `CASE-<10-hex>` (assert prefix `CASE-`), `customerId == "CUST-10001"`, `customerVerified == false` (mode stub INT-001).
- EVT-001 CaseCreated tercatat di outbox (diverifikasi TC-005 dan `test_dev_events_endpoint_gated_and_working`).

**Jalur negatif (bagian TC-001, per AC FRD-001 §10)**
| Kondisi | Expected | Tes nyata |
|---|---|---|
| `caseType` bukan enum valid | 400, envelope `code=VALIDATION_ERROR`, `details` memuat `caseType` | `test_create_invalid_enum_400_with_details` |
| Field wajib hilang (mis. `customerId`) | 400, `code=VALIDATION_ERROR` | `test_create_missing_mandatory_field_400` |
| `subject` > 200 karakter (plus boundary lain: subject/customerId kosong, description > 5000, customerId > 64, channel > 32) | 400, `code=VALIDATION_ERROR` | `test_create_boundary_violations_400` |
| Tanpa token / token salah | 401, `code=UNAUTHENTICATED` | `test_create_missing_token_401_with_error_envelope`, `test_create_invalid_token_401` |
| Token sah tanpa `cases:create` | 403, `code=FORBIDDEN`, message menyebut `cases:create` | `test_create_without_permission_403` |

**Data uji**: payload `VALID_PAYLOAD` di `tests/test_cases.py` (customerId sintetis `CUST-10001`); variasi negatif diturunkan dari payload yang sama.

**Status**: ✅ **Implemented** — jalur create sukses: `test_create_and_get_case`; negatif seperti tabel di atas.

---

## TC-002 — Get case by id returns case

| Field | Value |
|---|---|
| FR | FR-002 |
| BR | BR-007 |
| API | API-002 `GET /v1/cases/{caseId}` |
| EVT | — |
| Trace link | TRC-L-002 (Sprint-01, Approved) |

**Precondition**
- Case sudah ada (dibuat via API-001 pada langkah setup).
- Principal terautentikasi dengan permission `cases:read`.

**Langkah**
1. Setup: `POST /v1/cases` dengan payload valid TC-001 → simpan `caseId` dari response 201.
2. Kirim `GET /v1/cases/{caseId}` dengan header Authorization valid.
3. Baca response body.

**Expected Result**
- Status code **200**.
- Assertion kunci: `caseId` response == `caseId` yang dibuat; field lengkap sesuai skema `Case` OpenAPI (status, createdAt/updatedAt UTC, createdBy, customerVerified); kolom DB `updated_by` **tidak** muncul di response (kebijakan kontrak, FRD-001 §7).

**Jalur negatif/pelengkap (bagian TC-002)**
| Kondisi | Expected | Tes nyata |
|---|---|---|
| `caseId` tidak dikenal (`CASE-NOT-FOUND`) | 404, envelope `code=NOT_FOUND` | `test_get_not_found_404_with_error_envelope` |
| Principal read-only (`cases:read` saja) melakukan GET | 200 | `test_readonly_principal_can_read` |
| Engine + connection pool di-reset terhadap DB sama (persistensi dari disk, bukan state proses) | 200, case tetap terbaca | `test_case_survives_engine_reset` |

**Data uji**: case hasil create payload TC-001; `caseId` fiktif `CASE-NOT-FOUND` untuk jalur 404.

**Status**: ✅ **Implemented** — jalur get: `test_create_and_get_case`; pelengkap seperti tabel di atas.

---

## TC-003 — Assign case updates assignee and emits event

| Field | Value |
|---|---|
| FR | FR-003 |
| BR | BR-002, BR-008 |
| API | API-003 `POST /v1/cases/{caseId}/assign` |
| EVT | EVT-002 CaseAssigned, EVT-003 StatusChanged |
| Trace link | TRC-L-003 (Sprint-02, Approved) |

> **Implemented (Sprint-02B; katalog disinkronkan Sprint-03A).** Langkah diturunkan dari AC Gherkin FRD-002 §6 (FR-003, v0.2); kontrak normatif: [`07 API Catalog/openapi/case-service.v1.yaml`](../07%20API%20Catalog/openapi/case-service.v1.yaml) v1.4.0 (API-003, `AssignRequest` — konsolidasi dari eks-`case-actions.v1.yaml` per DEC-006 D6/U-6); payload EVT-002/EVT-003 beku di `events.yaml` (status Implemented). Entry G1 (Test Strategy §3) terpenuhi; lihat `tests/test_lifecycle.py::test_tc003_*`.

**Precondition (draf)**
- Case berstatus `REGISTERED`.
- Principal dengan permission `cases:assign` pada unit terkait (permission baru — revisi SEC-RAM-001, prasyarat G1).

**Langkah (draf)**
1. Setup: buat case via `POST /v1/cases` (payload TC-001) → `caseId`, status `REGISTERED`.
2. Kirim `POST /v1/cases/{caseId}/assign` dengan `assigneeId` dan `unitId` valid.
3. Kirim `GET /v1/cases/{caseId}` untuk verifikasi state.
4. Periksa outbox/audit (pola TC-005).

**Expected Result (draf)**
- Status code **200**; assignee ter-update; status menjadi `ASSIGNED`.
- EVT-002 CaseAssigned dipublikasikan (caseId, assigneeId, unitId, assignedBy, assignedAt) **dan** EVT-003 StatusChanged (`REGISTERED→ASSIGNED`) — setiap transisi valid memicu EVT-003 per DOM-ECMF-003.
- Audit record tercatat dalam transaksi yang sama (BR-008).
- Negatif: assignment lintas unit oleh non-supervisor → **403** `FORBIDDEN` dengan Error envelope `{code, message}`.
- Negatif: assign pada status non-assignable (mis. `IN_PROGRESS`) → **409** `INVALID_STATE`; state tidak berubah, tanpa event (DEC-006).

**Data uji (draf)**: case dari payload TC-001; `assigneeId`/`unitId` sintetis mengikuti fixture Role Access Matrix revisi Sprint-02.

**Status**: ✅ **Implemented** — `tests/test_lifecycle.py::test_tc003_*`. Exit gate G1 terpenuhi, termasuk authz permission baru dan audit/outbox pola create.

---

## TC-004 — Invalid status transition rejected

| Field | Value |
|---|---|
| FR | FR-004 |
| BR | BR-001, BR-008 |
| API | API-004 `POST /v1/cases/{caseId}/status` |
| EVT | EVT-003 StatusChanged (hanya pada transisi valid) |
| Trace link | TRC-L-004 (Sprint-02, Approved) |

> **Implemented (Sprint-02B; katalog disinkronkan Sprint-03A).** Langkah diturunkan dari AC Gherkin FRD-002 §6 (FR-004, v0.2); matriks transisi mengikuti DOM-ECMF-003. Kontrak normatif: [`07 API Catalog/openapi/case-service.v1.yaml`](../07%20API%20Catalog/openapi/case-service.v1.yaml) v1.4.0 (API-004, `StatusChangeRequest` — `toStatus`, `resolutionCode` wajib untuk →CLOSED, `reason` — konsolidasi dari eks-`case-actions.v1.yaml` per DEC-006 D6/U-6). **Rekonsiliasi 400-vs-409 selesai:** transisi ilegal = **409** `INVALID_TRANSITION`; 400 khusus validasi payload. Permission final: `cases:status` (DEC-006). Lihat `tests/test_lifecycle.py::test_tc004_*`.

**Precondition (draf)**
- Case berstatus `REGISTERED` (untuk jalur invalid) atau `ASSIGNED` (untuk jalur valid pembanding).
- Principal dengan permission transisi status (`cases:status` — nama beku per DEC-006, SEC-RAM-001 v0.3).

**Langkah (draf)**
1. Setup: buat case via `POST /v1/cases` → status `REGISTERED`.
2. Jalur invalid: kirim `POST /v1/cases/{caseId}/status` dengan `toStatus=CLOSED` (transisi `REGISTERED→CLOSED` tidak ada di matriks).
3. Kirim `GET /v1/cases/{caseId}` — verifikasi status tidak berubah.
4. Periksa outbox — verifikasi tidak ada event baru.
5. Jalur valid pembanding: dari `ASSIGNED`, kirim `toStatus=IN_PROGRESS` → verifikasi 200 + EVT-003.

**Expected Result (draf)**
- Jalur invalid: status code **409** dengan Error envelope (`code=INVALID_TRANSITION`, DEC-006); status case **tidak berubah**; **tidak ada event** yang diemit (AC FRD-002 v0.2).
- Jalur validasi payload (mis. `toStatus` bukan enum): **400** `VALIDATION_ERROR`.
- Jalur valid: **200**, status berubah, EVT-003 StatusChanged (fromStatus, toStatus, changedBy, changedAt), audit record dalam transaksi yang sama.

**Data uji (draf)**: case payload TC-001; pasangan transisi invalid `REGISTERED→CLOSED` dan valid `ASSIGNED→IN_PROGRESS` dari DOM-ECMF-003.

**Status**: ✅ **Implemented** — `tests/test_lifecycle.py::test_tc004_*`, termasuk tes transisi ilegal 409 dengan state tidak berubah.

---

## TC-005 — Audit record persisted on create (same transaction)

| Field | Value |
|---|---|
| FR | FR-001c |
| BR | BR-008 |
| API | API-001 `POST /v1/cases` |
| EVT | EVT-001 CaseCreated (via outbox, ADR-009) |
| Trace link | TRC-L-009 (Sprint-01, Approved) |

**Precondition**
- Skema DB bersih (fixture `fresh_db`); principal dengan `cases:create`.

**Langkah**
1. Kirim `POST /v1/cases` dengan payload valid TC-001 → 201, simpan `caseId`.
2. Buka session DB langsung (SQLAlchemy) terhadap engine yang sama.
3. Query tabel `audit_log` dan `outbox`.

**Expected Result**
- Status code **201** pada create.
- Assertion kunci pada `audit_log`: tepat **1** record; `action == "case.create"`; `entity_id == caseId`; `actor_user_id == "cs.agent.1"` (principal slice).
- Assertion kunci pada `outbox`: tepat **1** record; `event_id == "EVT-001"`; `event_name == "CaseCreated"`; `payload.caseId == caseId`.
- Kedua record berada dalam **transaksi yang sama** dengan insert case (pola transactional outbox, ADR-009; BR-008).

**Data uji**: payload `VALID_PAYLOAD` (TC-001).

**Status**: ✅ **Implemented** — `test_create_persists_audit_and_outbox_in_one_transaction`.

---

## TC-006 — List cases paginated and filtered

| Field | Value |
|---|---|
| FR | FR-005 |
| BR | BR-007 |
| API | API-005 `GET /v1/cases` |
| EVT | — |
| Trace link | TRC-L-010 (Sprint-03B, Approved) |

> **Implemented (Sprint-03B).** Diturunkan dari FRD-001 v0.4 §10 FR-005 AC. Kontrak normatif: `07 API Catalog/openapi/case-service.v1.yaml` v1.5.0 (API-005, `CasePage`). Sort dikunci `createdAt` descending (keputusan CTO, design review Sprint-03B) — parameter sort tidak tersedia di kontrak ini.

**Precondition**
- Beberapa case tersedia dengan kombinasi `status`/`priority`/`caseType`/`assigneeId` berbeda (fixture setup via `POST /v1/cases` + `assign`/`status` sesuai kebutuhan skenario).
- Principal dengan `cases:read`.

**Langkah**
1. `GET /v1/cases` tanpa query param → verifikasi `page=1`, `pageSize=20` default, `items` terurut `createdAt` descending.
2. `GET /v1/cases?status=ASSIGNED` → verifikasi hanya case berstatus `ASSIGNED` yang kembali.
3. `GET /v1/cases?priority=HIGH&caseType=COMPLAINT` → verifikasi kombinasi filter AND.
4. `GET /v1/cases?assigneeId=USR-2001` → verifikasi filter assignee.
5. `GET /v1/cases?pageSize=101` → verifikasi 400 `VALIDATION_ERROR`.
6. `GET /v1/cases?page=999` → verifikasi 200 dengan `items=[]` dan `totalItems` benar.
7. Tanpa token / tanpa permission → verifikasi 401/403.

**Expected Result**
- Response mengikuti `CasePage{items,page,pageSize,totalItems}`.
- Filter tidak cocok → `items=[]`, bukan error.
- `pageSize>100` → 400 dengan Error envelope.
- Auth mengikuti pola endpoint lain (401 token hilang/salah, 403 tanpa `cases:read`).

**Data uji**: case sintetis dari payload TC-001, di-assign/status-ubah sesuai kebutuhan skenario filter.

**Status**: ✅ **Implemented** — `tests/test_case_list.py`.

---

## TC-010 — Customer 360 retrieval succeeds

| Field | Value |
|---|---|
| FR | FR-010 |
| BR | BR-003 (BR-CRM-01/04), BR-CRM-02 (masking) |
| API | API-010 `GET /v1/customers/{customerId}` |
| EVT | — |
| Trace link | TRC-L-005 (Sprint-02, Planned) |

> **Ditunda (CTO decision, Sprint-03B design review, 2026-07-22).** Draft kontrak dan FRD-003 AC mengasumsikan stub mengembalikan profil pelanggan nyata (fullName, contactChannels) — bertentangan dengan larangan fabrikasi data pelanggan di INT-001 untuk mode stub. Lihat `implementation/backend/ACR_SPRINT02B.md` ACR-002. Tidak dikerjakan sampai akses sandbox INT-001A tersedia atau kontrak stub didefinisikan ulang. Langkah di bawah **tetap draf**, belum berubah.

**Precondition (draf)**
- Principal terautentikasi; ada dua varian role: CS Agent dan non-CS (mis. Viewer).
- `customerId` valid tersedia (mode stub: reference lokal; mode real: sandbox Customer Master per INT-001A).

**Langkah (draf)**
1. Sebagai CS Agent: kirim `GET /v1/customers/{customerId}`.
2. Verifikasi body: profil 360 (data master + case/interaksi terkait), field kontak **tanpa masking**.
3. Sebagai role non-CS: kirim `GET /v1/customers/{customerId}`.
4. Verifikasi body: `phone`/`email` **dimask** sesuai BR-CRM-02 baseline.
5. Verifikasi tidak tersedia operasi write terhadap data master (read-only, BR-003) — tidak ada endpoint mutasi customer di kontrak.

**Expected Result (draf)**
- Status code **200** untuk kedua role; perbedaan hanya pada masking kontak.
- Error mengikuti envelope: 401/403 untuk auth, 404 untuk `customerId` tidak dikenal.

**Data uji (draf)**: `CUST-10001` (sintetis); role fixture CS vs non-CS per Role Access Matrix revisi.

**Status**: 🕓 **Deferred** — ditunda oleh keputusan CTO (Sprint-03B); menunggu akses INT-001A atau redefinisi kontrak stub.

---

## TC-020 — Notification stub handles CaseAssigned

| Field | Value |
|---|---|
| FR | FR-020 |
| BR | BR-004 (BR-NOTIF-01), BR-NOTIF-02/03/04 |
| API | — (konsumsi event) |
| EVT | EVT-001 CaseCreated, EVT-002 CaseAssigned (consume) |
| Trace link | TRC-L-006 (Sprint-02, Approved) |

> **Implemented (Sprint-02B; katalog disinkronkan Sprint-03A).** Langkah diturunkan dari AC Gherkin FRD-004 §6. Konsumen stub berjalan in-process terhadap outbox (ADR-009); lihat `app/notification.py`.

**Precondition (draf)**
- Rule notifikasi `CaseAssigned` aktif (opt-in per BR-004).
- Ada mekanisme konsumsi outbox (publisher in-process DEV per ADR-009 — broker belum dipilih).

**Langkah (draf)**
1. Setup: buat + assign case sehingga EVT-002 CaseAssigned masuk outbox (prasyarat TC-003).
2. Jalankan konsumen Notification (stub) terhadap event tersebut.
3. Verifikasi notifikasi terkirim ke assignee dan delivery log tercatat.
4. Idempotency: kirim EVT-002 yang sama dua kali (at-least-once, ADR-001) — verifikasi hanya **satu** notifikasi terkirim.

**Expected Result (draf)**
- Notifikasi ter-resolve ke penerima dari kombinasi role/assignment (BR-NOTIF-02), delivery log tersimpan (BR-NOTIF-03).
- Duplikat event tidak menggandakan notifikasi (idempotent consumer, dedup per caseId + event key).
- (Lanjutan, boleh dipisah TC turunan saat DoR) retry 3x interval 5 menit lalu eskalasi email supervisor (BR-NOTIF-04) — kebutuhan gateway di INT-002.

**Data uji (draf)**: event EVT-002 sintetis dari case payload TC-001; rule notifikasi fixture opt-in.

**Status**: ✅ **Implemented** — `tests/test_notification_unit.py`, `tests/test_lifecycle.py::test_fr020_notification_stub_on_drain`.

---

## TC-030 — SLA breach event emitted when overdue

| Field | Value |
|---|---|
| FR | FR-030 |
| BR | BR-005, BR-KPI-01/02/03/04 |
| API | — (konsumsi/produksi event) |
| EVT | EVT-004 SLABreached (produce); EVT-001, EVT-003, EVT-005, EVT-007 (consume) |
| Trace link | TRC-L-007 (Sprint-03, Planned) |

> **Draf, dibekukan saat gate G1/DoR.** Langkah diturunkan dari AC Gherkin FRD-005 §6. Dependensi: FR-004 (StatusChanged), konfigurasi SLA `11 SLA and KPI Matrix`, event bus operasional.

**Precondition (draf)**
- Case dengan SLA aktif: kategori+prioritas terkonfigurasi, kalender baseline **24x7** (DEC-004).
- KPI service mengonsumsi EVT-001 (start clock), EVT-003, EVT-005, EVT-007.

**Langkah (draf)**
1. Setup: buat case (EVT-001) dengan konfigurasi SLA yang `dueAt`-nya dekat (clock injeksi/time-travel pada tes).
2. Majukan waktu melewati `dueAt` tanpa status pemenuhan.
3. Verifikasi outbox/bus KPI: EVT-004 SLABreached diemit dengan payload (caseId, slaId, breachedAt, dueAt, severity).
4. Ulangi evaluasi clock — verifikasi **tidak** ada EVT-004 kedua (idempoten per caseId + slaId).
5. Pembanding: case CLOSED sebelum `dueAt` (EVT-005) → tidak ada breach; performance fact difinalisasi.

**Expected Result (draf)**
- EVT-004 diemit **tepat satu kali** per caseId+slaId saat overdue; re-breach setelah reopen (EVT-007) diperbolehkan per `08 Event Catalog/events/events.yaml`.
- Tidak ada breach untuk case yang closed sebelum due.

**Data uji (draf)**: case payload TC-001 dengan konfigurasi SLA sintetis (kategori COMPLAINT × priority HIGH), clock ter-inject.

**Status**: 🕓 **Planned** — Sprint-03 (menunggu DoR FRD-005 dan trigger evaluasi broker ADR-009 bila lintas service).

---

## TC-040 — Dashboard queue view scoped by role/org

| Field | Value |
|---|---|
| FR | FR-040 |
| BR | BR-006 (BR-DASH-01/04), BR-DASH-02, BR-DASH-03 |
| API | API-040 `GET /v1/dashboard/queues` (draft: [`drafts/dashboard-queues.v1.draft.yaml`](../07%20API%20Catalog/openapi/drafts/dashboard-queues.v1.draft.yaml)) |
| EVT | — (read-only) |
| Trace link | TRC-L-008 (Sprint-03, Planned) |

> **Draf minimal, dibekukan saat DoR FRD-006.** Langkah diturunkan dari AC Gherkin FRD-006 §5; kontrak API-040 masih draft (non-normatif sampai merged di gate terkait Sprint-03).

**Precondition (draf)**
- Beberapa case tersebar di ≥2 unit dengan status beragam (setup via API-001/003/004).
- Dua principal: Supervisor unit U dan Supervisor/Manager unit lain (scope berbeda, revisi SEC-RAM-001 Sprint-03).

**Langkah (draf)**
1. Sebagai Supervisor unit U: kirim `GET /v1/dashboard/queues` → verifikasi hanya antrian unit U (BR-006) dan respons memuat timestamp `asOf` (BR-DASH-02).
2. Sebagai principal scope lain: kirim request yang sama → verifikasi data ter-scope berbeda; angka agregat reconcile dengan list case (`GET /v1/cases` API-005) pada filter setara.
3. Verifikasi tidak ada operasi mutasi yang tersedia dari kontrak dashboard (BR-DASH-03).

**Expected Result (draf)**
- Status code **200**; antrian ter-scope role+org; `asOf` ada; agregat konsisten dengan sumber; error auth mengikuti envelope (401/403).

**Data uji (draf)**: case sintetis payload TC-001, unit/assignee fixture per Role Access Matrix revisi Sprint-03.

**Status**: 🕓 **Planned** — Sprint-03 (gate: DoR FRD-006 per sprint traceability TRC-L-008).

---

## Related
- `ECMP_Test_Strategy_v0.1.md` (TST-001) — level tes, mapping TC → tes nyata, gate G0/G1
- `../26 Traceability/traceability.yaml` (TRC-DATA-001) — SoT definisi TC/FR/API/EVT
- `../03 Functional Requirements/` — FRD-001 (Approved), FRD-002..005 (Draft, AC Gherkin sumber draf TC Planned)
- `../implementation/backend/tests/test_cases.py` — tes pytest nyata
- `ECMP_UAT_Plan_v0.1.md` (UAT-001) — subset TC untuk UAT
