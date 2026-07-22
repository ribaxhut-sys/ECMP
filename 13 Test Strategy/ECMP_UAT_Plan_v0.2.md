# ECMP UAT Plan

| Field | Value |
|---|---|
| ID | UAT-001 |
| Version | 0.2 |
| Owner | QA Lead |
| Reviewer | BA / Business Owner delegate |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-21 |

## Purpose
Rencana User Acceptance Testing (UAT) ECMP. Dokumen ini **jujur ter-gate**: UAT belum bisa dieksekusi di shared environment hari ini karena environment SIT/UAT dan fase target autentikasi belum aktif — rencana ini mendefinisikan prasyarat, peserta, skenario (termasuk **Close** dan **Reject**), dan kriteria agar UAT siap jalan begitu gate terpenuhi.

**Changelog v0.2 (Sprint-09)**
- Explicit scenarios **UAT-S7 Close** and **UAT-S8 Reject** (J-4 / FR-004).
- Traceability table: UAT scenario → TC → automated pytest (and frontend permission checks where noted).
- Gelombang 2 expanded to cover Close/Reject after lifecycle TC-004 coverage.
- Cross-links updated to this filename (`ECMP_UAT_Plan_v0.2.md`).

## 1. Prasyarat (gate — wajib terpenuhi sebelum UAT dimulai)

| # | Prasyarat | Status | Owner | Target | Rujukan |
|---|---|---|---|---|---|
| 1 | Environment SIT/UAT tersedia | ⏳ Belum — baseline platform SIT/UAT sudah diputuskan (ADR-010: compose + VM managed, aktif hanya setelah fase target ADR-007); provisioning belum dilakukan | Solution Architect | Sebelum entry UAT gelombang 1 (aktivasi mengikuti fase target ADR-007) | `14 Deployment Standards`; ADR-010 |
| 2 | Fase target autentikasi aktif (JWT/OIDC) — token statis slice **dilarang** untuk shared UAT | ⏳ Belum — arah sudah diputuskan | Security Lead | Sebelum shared UAT dimulai (prasyarat ADR-007) | ADR-007 (fase target sebelum shared UAT) |
| 3 | Scope UAT ter-baseline: FRD terkait berstatus Approved dan TC-nya Implemented + hijau di CI | Sebagian (FRD-001 Approved; FRD-002/003 Draft) | Business Owner | Gelombang 1: terpenuhi (FRD-001); gelombang 2: gate G1 — sebelum Sprint-02 selesai | `03 Functional Requirements`, `ECMP_Test_Strategy_v0.1.md` §3 |
| 4 | Data uji sintetis disiapkan di environment UAT (dilarang data pelanggan nyata) | ⏳ Menunggu environment | QA Lead | Setelah prasyarat #1 terpenuhi, sebelum entry gelombang 1 | Test Strategy §5 |
| 5 | Mode Customer Master ditetapkan untuk UAT (stub vs sandbox real) | ⏳ Stub tersedia; sandbox = open item INT-001A | Integration Lead | Sebelum gelombang 2 (keputusan bersama closure INT-001A) | INT-001, INT-001A |
| 6 | Restore drill documented (OPS-RST-001) before shared UAT entry | ✅ Sprint-09 DEV scratch drill recorded; shared-env drill still required at ADR-010 activation | Operations Lead | Before shared UAT | `15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md` |

## 2. Peserta per Persona
Persona dari `../12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md`. **UI deferred** as primary UAT surface for early waves (non-goal DEC-002): gelombang 1–2 dieksekusi **via API** (koleksi request terkurasi, mis. Postman/Bruno). Close/Reject boleh diverifikasi juga lewat Case Detail actions bila UI tersedia (J-4), tanpa mengubah AC API.

| Persona | Peran di UAT | Skenario yang diuji |
|---|---|---|
| P-01 CS Agent | Peserta utama slice | Create case, get case (TC-001, TC-002); Customer 360 saat tersedia (TC-010) |
| P-02 Supervisor | Peserta Sprint-02+ | Assign/reassign (TC-003); **Approve & Close** / **Reject** (UAT-S7 / UAT-S8, J-4) |
| P-04 Handler | Peserta Sprint-02+ | Transisi status penanganan (TC-004); submit for review menuju `PENDING_REVIEW` |
| P-03 Administrator | Observer fase awal | Verifikasi audit trail (TC-005) bersama QA; config-driven flow menyusul |
| P-05 Manager / Executive | Belum dilibatkan | Dashboard/KPI (Sprint-03) — di luar scope UAT v0.2 gelombang 1–2 |
| QA Lead | Fasilitator | Menyiapkan skrip API, mencatat hasil & defect |
| BA | Pendamping | Memetakan hasil ke AC FRD |

## 3. Skenario UAT
Skenario UAT = **subset** dari `ECMP_Test_Case_Catalog_v0.1.md` (TC-CAT-001), dijalankan oleh persona bisnis (bukan pytest) terhadap environment UAT. Mapping ke tes otomatis ada di **§3.1**.

### Gelombang 1 — slice Sprint-01 (siap begitu prasyarat §1 terpenuhi)
| Skenario | TC | Persona | Ringkas |
|---|---|---|---|
| UAT-S1 | TC-001 | P-01 | Registrasi complaint via `POST /v1/cases` → 201, status `REGISTERED`; coba juga jalur gagal 400/401/403 |
| UAT-S2 | TC-002 | P-01 | Ambil detail case via `GET /v1/cases/{caseId}` → 200 field lengkap; 404 untuk id salah |
| UAT-S3 | TC-005 | P-03 + QA | Verifikasi audit record `case.create` + outbox EVT-001 tercipta satu transaksi dengan create |

### Gelombang 2 — lifecycle (TC Implemented per gate G1 / Sprint-02B+)
| Skenario | TC | Persona | Ringkas |
|---|---|---|---|
| UAT-S4 | TC-003 | P-02 | Assign case → status `ASSIGNED`, EVT-002 + EVT-003 |
| UAT-S5 | TC-004 | P-04 | Transisi valid diterima; transisi ilegal ditolak **409** `INVALID_TRANSITION` tanpa perubahan state |
| UAT-S6 | TC-010 | P-01 + role non-CS | Customer 360 read-only; masking kontak untuk non-CS (BR-CRM-02) — **deferred** sampai ACR-002/INT-001 ditutup |
| UAT-S7 | TC-004 | P-02 | **Close (Approve & Close):** dari `PENDING_REVIEW` → `CLOSED` dengan `resolutionCode` wajib; EVT-005 CaseClosed + EVT-003 |
| UAT-S8 | TC-004 | P-02 | **Reject:** dari `PENDING_REVIEW` → `IN_PROGRESS` (optional `reason`); EVT-003; case kembali ke antrian handler |

#### UAT-S7 — Close (explicit)
1. Setup: case melewati `REGISTERED` → `ASSIGNED` → `IN_PROGRESS` → `PENDING_REVIEW` (handler path).
2. Sebagai reviewer/supervisor dengan `cases:status`: `POST /v1/cases/{caseId}/status` body `{ "toStatus": "CLOSED", "resolutionCode": "RESOLVED_REFUND" }` (atau kode resolusi valid lain per kontrak).
3. Negatif: `toStatus=CLOSED` tanpa `resolutionCode` → **400** `VALIDATION_ERROR`; status tetap `PENDING_REVIEW`.
4. Positif: **200**, `status=CLOSED`; outbox memuat EVT-005 (`resolutionCode` terisi) dan EVT-003; audit `case.status_change` ada.
5. Case terminal untuk scope ini (reopen out of scope — FRD-002 §8).

#### UAT-S8 — Reject (explicit)
1. Setup: case berstatus `PENDING_REVIEW` (sama seperti UAT-S7 step 1).
2. Sebagai reviewer/supervisor: `POST /v1/cases/{caseId}/status` body `{ "toStatus": "IN_PROGRESS", "reason": "Need more evidence" }` (`reason` opsional per BR untuk jalur non-override).
3. Expected: **200**, `status=IN_PROGRESS`; EVT-003 StatusChanged (`fromStatus=PENDING_REVIEW`, `toStatus=IN_PROGRESS`); **tidak** ada EVT-005.
4. Handler dapat melanjutkan penanganan (J-3/J-4).

TC-020/TC-030 (Notification, SLA breach) menyusul di gelombang berikutnya sesuai sprint traceability; tidak dijadwalkan di plan v0.2.

### 3.1 Traceability — UAT scenario ↔ automated tests

| UAT | TC (TC-CAT-001) | TRC link | Automated evidence (CI) |
|---|---|---|---|
| UAT-S1 | TC-001 | TRC-L-001 | `implementation/backend/tests/test_cases.py` (create paths) |
| UAT-S2 | TC-002 | TRC-L-002 | `implementation/backend/tests/test_cases.py` (get paths) |
| UAT-S3 | TC-005 | TRC-L-009 | `test_create_persists_audit_and_outbox_in_one_transaction` |
| UAT-S4 | TC-003 | TRC-L-003 | `tests/test_lifecycle.py::test_tc003_*` |
| UAT-S5 | TC-004 | TRC-L-004 | `tests/test_lifecycle.py::test_tc004_invalid_transition_rejected_state_unchanged` (+ valid transition siblings) |
| UAT-S6 | TC-010 | TRC-L-005 | 🕓 Deferred (ACR-002) — no CI pytest until CRM stub decision closes |
| UAT-S7 | TC-004 | TRC-L-004 | `tests/test_lifecycle.py::test_tc004_close_emits_evt005`, `test_tc004_closed_requires_resolution_code_400`; UI gate: `canApproveClose` in `permissions.test.ts` |
| UAT-S8 | TC-004 | TRC-L-004 | Workflow allows `PENDING_REVIEW→IN_PROGRESS` (`app/domain/workflow.py`); UI gate: `canReject` in `permissions.test.ts`; backend path covered by TC-004 status API suite (`test_tc004_*`) — reject transition is the configured inverse of close from review |

SoT IDs remain in `../26 Traceability/traceability.yaml`. UAT rows above are the **acceptance subset** mapping; they do not invent new TC ids.

## 4. Entry / Exit Criteria

**Entry criteria (per gelombang)**
1. Seluruh prasyarat §1 terpenuhi untuk gelombang tersebut.
2. Semua TC dalam gelombang berstatus ✅ Implemented di TC-CAT-001 dan hijau di CI (`backend-ci.yml`), kecuali yang secara eksplisit Deferred (UAT-S6).
3. Skrip/koleksi API UAT direview BA terhadap AC FRD.
4. Peserta persona terkonfirmasi dan mendapat kredensial UAT (bukan token dev).

**Exit criteria (per gelombang)**
1. 100% skenario gelombang yang **tidak** Deferred dieksekusi; hasil tercatat (pass/fail + evidence).
2. Tidak ada defect Severity 1/2 yang open (lihat §5).
3. Defect Severity 3/4 open memiliki disposisi tertulis (fix sekarang / defer) yang disetujui Business Owner.
4. Sign-off §6 ditandatangani.
5. Untuk gelombang 2: UAT-S7 dan UAT-S8 keduanya pass (Close dan Reject).

## 5. Defect Triage

| Severity | Definisi | Contoh | Keputusan disposisi oleh |
|---|---|---|---|
| Sev-1 | Fungsi inti gagal total / data korup / keamanan | Create case selalu gagal; audit tidak tercatat | Business Owner + Tech Lead (blokir exit) |
| Sev-2 | Fungsi inti salah perilaku tanpa workaround | Status awal bukan `REGISTERED`; Close tanpa resolution diterima; Reject tidak mengembalikan `IN_PROGRESS` | Business Owner + Tech Lead (blokir exit) |
| Sev-3 | Perilaku salah dengan workaround / kasus tepi | Pesan error kurang jelas; field opsional tidak tersimpan | QA Lead + BA (boleh defer dengan persetujuan Business Owner) |
| Sev-4 | Kosmetik / dokumentasi | Typo pesan, inkonsistensi label | QA Lead (defer default) |

Alur: penemu mencatat defect (skenario, langkah, expected vs actual, evidence) → QA Lead menetapkan severity awal → triage harian bersama BA + Tech Lead → disposisi per tabel di atas. Defect yang mengubah kontrak API/event wajib lewat jalur contract-first (bukan hotfix langsung).

## 6. Sign-off
- **Penandatangan:** Business Owner (approver), didampingi QA Lead (kelengkapan eksekusi) dan BA (kesesuaian AC).
- **Objek sign-off:** per gelombang — daftar skenario + hasil + daftar defect beserta disposisinya.
- Sign-off gelombang 1 menjadi salah satu masukan keputusan rilis (lihat `16 Release Management`).

## Related
- `ECMP_Test_Case_Catalog_v0.1.md` (TC-CAT-001) — sumber skenario
- `ECMP_Test_Strategy_v0.1.md` (TST-001) — gate G0/G1
- `../12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (UX-001) — persona
- `../12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` (UX-SCR-001) — J-4 Close/Reject
- `../05 Architecture Decision Records/ECMP_ADR_007_Authentication_Model_v1.0.md` — prasyarat auth fase target
- `../14 Deployment Standards` — environment; baseline platform SIT/UAT per `../05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`
- `../26 Traceability/traceability.yaml` — sprint per TC; UAT mapping §3.1
- `../15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md` — prasyarat restore drill
