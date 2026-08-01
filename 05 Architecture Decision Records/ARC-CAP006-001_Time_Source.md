# ARC-CAP006-001 — Time Source (Architecture Concept)

| Field | Value |
|---|---|
| Document ID | ARC-CAP006-001 |
| Title | Time Source |
| Document Type | Architecture Concept (formal) |
| Version | 1.0 |
| Owner | Solution Architect / Performance Owner |
| Reviewer | Architecture Review Board |
| Approver | Architecture Board |
| Status | 🟢 **Accepted** — concept formalized (B2-19); **not** an implementation authorization |
| Last Review | 2026-08-01 |
| Next Review | 2026-10-01 |
| Capability | CAP-006 (SLA Measurement & Breach Detection) |
| FR | FR-030 |
| Trace | TRC-L-007 |
| Governing ADR | ADR-CAP006-001 **Accepted** (B2-20) — mechanism class **Hybrid**; conceptual runtime ARC-CAP006-002 Accepted (B2-21); concrete runtime still Deferred |
| Workshop source | B2-18 Architecture Design Workshop (Evaluation Mechanism) |
| Persist sprint | B2-19 — `../deploy/evidence/B2-19_CAP-006_Time_Source_Concept_Formalization_20260801.md` |

## 1. Official name

**Time Source** (nama resmi; tidak diganti di B2-19).

## 2. Definition

**Time Source** adalah konsep arsitektur yang menyatakan adanya **stimulus evaluasi berbasis waktu** yang menjamin domain **KPI & Performance** dapat membandingkan waktu berjalan terhadap `dueAt` pada SLA clock aktif, **tanpa bergantung** pada kedatangan event lifecycle ECMF tepat pada ambang `dueAt`.

Time Source memasok kemampuan untuk mengamati kondisi FRD-005 / FR-030:

> *When waktu berjalan melewati dueAt tanpa status pemenuhan → emit EVT-004.*

Time Source **bukan** definisi ulang breach, **bukan** pemilik atribut clock, dan **bukan** event enterprise baru.

## 3. Purpose

1. Menutup celah event-only: lifecycle EVT-001/003/005/007 tidak menjamin evaluasi pada saat wall-clock melewati `dueAt` (periode sunyi).
2. Memungkinkan tujuan near-real-time SLA breach (ADR-001 decision driver) secara prinsip, tanpa mengubah pola integrasi antar-domain.
3. Memberi SoT repository untuk requirement arsitektur yang sudah disimpulkan B2-17E/B2-18, tanpa menginvent scheduler, polling, retry, database, OpenAPI, atau Event Catalog baru.

## 4. Classification

| Question | Board decision |
|---|---|
| Domain baru? | **Tidak** |
| Service produk baru? | **Tidak** |
| Runtime concern? | **Ya** — bagian runtime evaluasi KPI (CAP-006) |
| Infrastructure concern? | **Ya** — concern infrastruktur/runtime yang memasok stimulus waktu |
| Lainnya | **Architecture concept** yang mengikat requirement evaluasi berbasis waktu |

**Ringkas:** Time Source = **infrastructure / runtime concern** milik **KPI**, terdokumentasi sebagai Architecture Concept; **bukan** domain bisnis.

## 5. Scope (boundary)

Termasuk dalam konsep:

1. Requirement bahwa evaluasi CAP-006 **harus** dapat dipicu oleh berjalannya waktu terhadap `dueAt` aktif.
2. Pemisahan tanggung jawab: **stimulus waktu** (Time Source) vs **state clock** (atribut milik ECMF) vs **keputusan breach + emit EVT-004** (KPI).
3. Konsistensi dengan kalender baseline **24x7** (DEC-004 / DEC-005) sebagai konteks “waktu berjalan” v1.
4. Kompatibilitas dengan konsumsi event lifecycle sebagai **input state** (bukan sebagai satu-satunya stimulus ambang).
5. Kompatibilitas dengan jalur durable emit EVT-004 via **transactional outbox** (ADR-009).

## 6. Non-scope (apa yang BUKAN Time Source)

Time Source **bukan**:

1. Domain bisnis baru atau Capability Register entry baru.
2. Scheduler / cron / worker / polling **implementation** (detail tetap Deferred di ADR-CAP006-001).
3. Framework retry / DLQ publisher generik (dilarang ADR-009 hingga broker dipilih).
4. Event Catalog baru (mis. `TimeTick`, `DueReached`) — **ditolak** sebagai invent.
5. OpenAPI / HTTP business API untuk “time” atau “force evaluate” sebagai produk.
6. Perubahan Business Rule (BR-005 / DEC-004 / DEC-005 / definisi breach).
7. Pemilik SLA Config (tetap Administration) atau pemilik atribut SLA Clock (tetap ECMF).
8. Pemenuhan CAP-006 via DEC-012/013/014 complaint-stage SLA (tetap OOS per FRD-005 §9).
9. Otorisasi engineering FR-030 engine (Accept kelas Hybrid ≠ izin implementasi; tetap menunggu runtime design non-invent + gate).

## 7. Ownership & relationships

| Party | Relationship to Time Source |
|---|---|
| **KPI & Performance** | **Owner konsep & runtime evaluation** — memakai Time Source sebagai stimulus evaluasi; mendeteksi warning/breach; menghasilkan EVT-004 |
| **ECMF** | **Tidak memiliki Time Source** — tetap pemilik **SLA Clock attributes** / status history basis; memasok state via EVT-001/003/005/007 |
| **Administration** | **Tidak memiliki Time Source** — tetap SoT **SLA Config** (target, binding); KPI membaca nilai aktif (mis. via EVT-006) |
| **Notification** | **Consumer akibat evaluasi** — warning 80% dan breach memakai Notification (bukan event enterprise baru untuk warning; EVT-004 untuk breach) — **bukan** pemilik Time Source |
| **Core Platform (outbox)** | Jalur durable untuk EVT-004 setelah keputusan breach; **bukan** Time Source |

## 8. Impact on ADR-001

- **Tidak merevisi** keputusan ADR-001 (integrasi antar-domain = event-driven async).
- **Klarifikasi:** event-driven antar-domain **≠** evaluasi SLA harus event-only di dalam KPI.
- Time Source adalah stimulus **intra-capability KPI**, komplementer terhadap konsumsi event ECMF.
- Decision driver “SLA breach near real-time” menjadi **terdukung secara konsep**.

## 9. Impact on ADR-009

- **Tidak merevisi** deferral broker atau mandatory transactional outbox.
- Time Source **bukan** message broker dan **bukan** izin membangun retry/DLQ publisher generik.
- Evaluasi berbasis waktu dan jalur outbox→broker bersifat **orthogonal**.

## 10. Business Rules / OpenAPI / Event Catalog

| Concern | Impact |
|---|---|
| Business Rules | **Tidak berubah** — Time Source mengamati kondisi yang sudah didefinisikan |
| OpenAPI | **Tidak diperlukan** untuk konsep ini; TRC-L-007 tetap `api: []` |
| Event Catalog | **Tidak menambah** event; EVT-004 tetap satu-satunya breach event yang dikatalogkan |

## 11. Relationship to ADR-CAP006-001

| Layer | Status after B2-21 |
|---|---|
| ARC-CAP006-001 Time Source | **Accepted** (konsep) |
| ADR-CAP006-001 Evaluation Mechanism | **Accepted** (B2-20) — mechanism class = **Hybrid**; Time Source **wajib** + lifecycle events **wajib** |
| ARC-CAP006-002 Runtime Architecture | **Accepted** (B2-21) — conceptual stages/ownership/boundaries; **bukan** otorisasi implementasi |
| Concrete job/scheduler | **masih Deferred** |
| Technical Runtime Design unlock | **Blocked** — B2-22 **ADDITIONAL ARCHITECTURE REQUIRED**; B2-23 **FULFILLMENT PATTERN NOT SPECIFIED** |

B2-19 formalisasi konsep; B2-20 Accept kelas Hybrid; B2-21 Accept Runtime Architecture konseptual; B2-22 Non-Invent Gate; B2-23 menegaskan fulfillment pattern Time Source **belum** didefinisikan di repository. Implementasi job tetap Deferred.

## 12. Document History

| Ver | Date | Change |
|---|---|---|
| 1.0 | 2026-08-01 | B2-19 — formalisasi konsep dari Workshop B2-18; Accepted as Architecture Concept. B2-20 cross-ref: governing ADR-CAP006-001 Accepted (Hybrid class); definisi Time Source tidak berubah |
| 1.0a | 2026-08-01 | B2-22/B2-23 — Technical Runtime Design blocked; Time Source fulfillment pattern **NOT SPECIFIED** (requirement concept unchanged) |

## Related Documents

- `./ADR-CAP006-001_Evaluation_Mechanism.md`
- `./ARC-CAP006-002_Runtime_Architecture.md`
- `../deploy/evidence/B2-21_CAP-006_Runtime_Architecture_Specification_20260801.md`
- `../deploy/evidence/B2-22_CAP-006_Concrete_Runtime_Non_Invent_Gate_20260801.md`
- `../deploy/evidence/B2-23_CAP-006_Time_Source_Fulfillment_Pattern_Decision_20260801.md`
- `../03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` (FRD-005 LOCKED)
- `../deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md` (DEC-CAP006-BQ-001)
- `../deploy/evidence/B2-17E_CAP-006_ADR-CAP006-001_Decision_Closure_20260801.md`
- `../deploy/evidence/B2-19_CAP-006_Time_Source_Concept_Formalization_20260801.md`
- `./ECMP_ADR_001_Event_Driven_Domain_Integration_v1.0.md`
- `./ECMP_ADR_009_Message_Broker_Deferral_v1.0.md`
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`
- `../08 Event Catalog/events/events.yaml` (EVT-004)
