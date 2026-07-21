# ECMP Glossary (Starter)

| Field | Value |
|---|---|
| ID | GLS-001 |
| Version | 0.3 |
| Owner | Business Analyst |
| Reviewer | Domain PO / Architecture |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

| Term | Definition | Notes |
|---|---|---|
| ECMP | **Enterprise Complaint Management Platform** — platform pengelolaan complaint & inquiry pelanggan end-to-end (ekspansi resmi per Blueprint v2.1 §1, SoT bisnis per DEC-001) | Bukan Customer Master SoR (BR-003 / BR-CRM-01); ekspansi lama yang memakai kata "Customer" adalah keliru |
| Case | Unit kerja penanganan di ECMP yang merepresentasikan inquiry atau complaint | Generic transactional unit |
| Complaint | Case yang menyatakan ketidakpuasan/masalah terhadap produk/layanan | Subtype of Case |
| Inquiry | Case berupa permintaan informasi/klarifikasi tanpa klaim ketidakpuasan | Subtype of Case |
| Customer | Individu/entitas pelanggan yang direferensikan dari sistem master | ECMP is not SoR |
| Assignment | Penunjukan Case ke petugas/unit penanganan | Can be reassigned |
| Escalation | Kenaikan penanganan ke level/role lebih tinggi karena rule/SLA/severityitas | May be auto or manual |
| Priority | Tingkat urgensi penanganan Case | Biasanya memengaruhi SLA |
| Severity | Tingkat dampak bisnis/teknis dari isu | Jangan disamakan otomatis dengan Priority |
| SLA | Batas waktu layanan yang disepakati untuk tahapan/penyelesaian Case | Dihitung otomatis |
| KPI | Indikator kinerja layanan/organisasi yang diukur dari data operasional | E.g. overdue rate |
| Interaction | Catatan kontak/interaksi dengan pelanggan | Ditautkan ke Customer/Case |
| Channel | Media masuk/interaksi (email, call, app, dll.) | App channel generally out of core scope |
| Root Cause | Penyebab utama masalah yang diidentifikasi saat/setelah resolusi | Required on certain closures |
| Resolution | Hasil penanganan yang menutup Case | Evidence may be required |
| Reopen | Membuka kembali Case yang sudah closed sesuai aturan role | Restricted action |
| Audit Trail | Jejak perubahan/aktivitas yang tidak dapat dihapus | Core Platform concern |
| Configuration First | Prinsip mengubah proses via konfigurasi sebelum ubah kode | Architecture principle |
| REGISTERED | Status awal Case setelah create sukses (FR-001a) | Status set baseline — `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` |
| ASSIGNED | Status Case setelah di-assign ke handler/unit (FR-003) | Status set baseline |
| IN_PROGRESS | Status Case sedang dikerjakan oleh assignee | Status set baseline |
| PENDING_REVIEW | Status Case menunggu review/approval sebelum closure | Status set baseline |
| CLOSED | Status Case selesai dengan resolusi (dan evidence bila dipersyaratkan) | Status set baseline; emit EVT-005 |
| REOPENED | Status Case yang dibuka kembali setelah closed, dalam window 30 hari (BR-ECMF-07 baseline) | Status set baseline; emit EVT-007 |
| Case Type | Klasifikasi Case: `COMPLAINT` \| `INQUIRY` | Enum tertutup (FRD-001 §7) |
| Priority (enum) | Nilai prioritas Case: `LOW` \| `MEDIUM` \| `HIGH` \| `CRITICAL` | Enum tertutup (FRD-001 §7); memengaruhi SLA |
| Business Action | Aksi bermakna bisnis terhadap Case (create, assign, status change, close, reopen) yang wajib diaudit dan dapat memicu event | Lihat BR-008, BR-ECMF-01 |
| Transactional Outbox | Pola menulis event ke tabel `outbox` dalam transaksi yang sama dengan perubahan data, lalu dipublikasikan asinkron | G0 deliverable (DEC-002); menjamin konsistensi event |
| Write-Audit | Audit record immutable yang dipersist dalam transaksi yang sama dengan write signifikan | Wajib per FR-001c/BR-008; read-audit ditunda (DEC-002) |
| Error Envelope | Format respons error standar `{code, message, details?}` | Selaras OpenAPI; berlaku 400/401/403/404 |
| CaseCreated (EVT-001) | Event saat case teregistrasi | Producer ECMF; SoT `08 Event Catalog/events/events.yaml` |
| CaseAssigned (EVT-002) | Event saat case di-assign/reassign | Producer ECMF |
| StatusChanged (EVT-003) | Event saat transisi status valid terjadi | Producer ECMF |
| SLABreached (EVT-004) | Event saat ambang SLA terlampaui | Producer KPI |
| CaseClosed (EVT-005) | Event saat case ditutup | Producer ECMF |
| ConfigChanged (EVT-006) | Event saat konfigurasi efektif berubah | Producer Administration |
| CaseReopened (EVT-007) | Event saat case closed dibuka kembali | Producer ECMF; status Proposed |
| Bounded Context | Batas model domain di mana istilah/aturan berlaku konsisten (per domain ECMP: Core Platform, CRM, ECMF, KPI, Dashboard, Notification, Administration) | DDD term; lihat `20 Domain Architecture` |
| Aggregate | Klaster entitas dengan satu root (mis. Case sebagai aggregate root atas activity/status history) yang menjadi unit konsistensi transaksi | DDD term |
| Branch / Head Office / Work Order / Schedule Slot | **Out of scope per DEC-001** — konsep dari brief discovery yang tidak ada di Blueprint v2.1; dilarang dimodelkan (schema, endpoint, event) sampai revisi Blueprint di-approve | Lihat `27 Project Decisions/DEC-001` |
