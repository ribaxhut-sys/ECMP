# Definition of Done (Engineering)

| Field | Value |
|---|---|
| ID | ENG-003 |
| Version | 0.1 |
| Owner | Engineering Manager |
| Reviewer | Tech Lead |
| Approver | Engineering Manager |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Sebuah perubahan `implementation/**` dianggap **Done** hanya jika SEMUA butir di bawah terpenuhi. Ini melengkapi (bukan menggantikan) acceptance criteria FRD dan exit criteria gate (DEC-002).

## Checklist

1. **Kode selesai sesuai kontrak** — perilaku runtime sama dengan OpenAPI (`07 API Catalog/openapi/`) dan Event SoT (`08 Event Catalog/events/events.yaml`). Tidak ada endpoint yang hidup di runtime tapi tidak ada di katalog, dan sebaliknya.
2. **Tes hijau di CI** — pipeline `backend-ci.yml` lulus penuh: ruff → OpenAPI validate → `alembic upgrade head` → pytest terhadap PostgreSQL service. Tes baru/terubah menyertai perubahan perilaku.
3. **Katalog & traceability sinkron** — jika kontrak API/event/skema berubah: `07 API Catalog`, `08 Event Catalog`, dan `26 Traceability/traceability.yaml` diperbarui dalam PR yang sama (atau contract-PR mendahului code-PR, sesuai aturan gate G1).
4. **Tidak ada endpoint di luar OpenAPI** — catalog-first bersifat mutlak; endpoint eksperimen pun harus di belakang flag dev (contoh existing: `/_dev/events` di-gate `ECMP_ENABLE_DEV_ENDPOINTS`).
5. **BR-0xx dirujuk di PR** — deskripsi PR mencantumkan ID business rule / FR / ADR yang menjadi dasar perubahan perilaku (contoh: BR-008 untuk jalur write-audit). Perubahan tanpa dasar ID = pertanda scope creep, tahan dan klarifikasi dulu.
6. **Migrasi disertakan** — perubahan skema DB selalu lewat Alembic revision baru; tidak pernah mengedit revision yang sudah ter-merge.
7. **Tanpa secret** — tidak ada token/credential/connection string di kode maupun test fixture; konfigurasi via env (`.env` di-gitignore).
8. **Dokumen terdampak diperbarui** — README/standar terkait disentuh bila perilaku yang didokumentasikan berubah.

## Yang BUKAN bagian dari Done
- Fitur di luar otorisasi build aktif (non-goals DEC-002) — mengerjakannya justru melanggar DoD.
- Gold-plating: framework generik, abstraksi "untuk nanti" (larangan eksplisit ADR-009 aturan 4, ADR-005 opsi A).

## Related
- `PR_CHECKLIST.md` (ENG-002) — checklist mekanis per PR
- `CODE_REVIEW_CHECKLIST.md` (ENG-004) — sudut pandang reviewer
- `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`
