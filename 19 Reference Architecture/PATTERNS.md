# ECMP Reference Patterns

| Field | Value |
|---|---|
| ID | REF-001 |
| Version | 0.2 |
| Owner | Chief Architect |
| Reviewer | Tech Leads |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Pola arsitektur yang disetujui untuk ECMP. Pola yang sudah dipakai di kode merujuk implementasi aktual; pola yang belum dipakai diberi kondisi adopsi eksplisit — bukan menu bebas pilih.

## 1. Layered Architecture + aturan dependensi (ADR-005)

Prinsip: `Presentation → Application → Domain ← Infrastructure`. Untuk fase slice, ADR-005 memandatkan **minimal split** (bukan 4 package penuh):

```text
        main.py            (Presentation: routes + error handlers)
           │  memanggil                (error via errors.py → envelope)
           ▼
        service.py         (Application: business actions)
           │  memakai
           ▼
   models.py / db.py       (Domain-persistence / Infrastructure)

   pendukung: schemas.py (kontrak), auth.py (AuthN/Z), errors.py (ApiError), settings.py (env)

Aturan arah:
- main.py  → service.py → models.py/db.py   ✅
- service.py → main.py / FastAPI             ❌ (service bebas framework HTTP)
- models.py → service.py                     ❌
```

- Route handler dilarang memuat business rule; hanya validasi kontrak + delegasi.
- Full layering (package `domain/`, `application/`, repository interface) baru diadopsi saat service punya **>1 aggregate** — direview di gate G1. Mengadopsinya lebih awal = pelanggaran ADR-005 (over-engineering yang sudah ditolak sebagai Option A).

## 2. Business Action Pattern (command service, bukan CRUD generik)

Application layer mengekspos **aksi bisnis bernama**, bukan operasi CRUD generik:

- ✅ `register_case(...)`, `get_case(...)` (aktual di `service.py`); nanti `assign_case`, `transition_status`.
- ❌ `update_case(fields)` generik / repository `save()` yang menerima entitas bebas.

Alasan: setiap aksi bisnis membawa invariannya sendiri (status awal `REGISTERED`, audit BR-008, event EVT-xxx). CRUD generik membuat invarian itu opsional — sumber bug lifecycle. Endpoint HTTP boleh RESTful (`POST /v1/cases`), tetapi di belakangnya tetap command yang eksplisit.

## 3. Transactional Outbox (ADR-009) — DIPAKAI

**Kapan pakai:** setiap kali write bisnis harus menghasilkan event domain, dan broker belum ada / publish tidak boleh merusak konsistensi. Ini mekanisme resmi emisi event ECMP sampai broker dipilih.

**Cara:** event ditulis ke tabel `outbox` **dalam transaksi yang sama** dengan write bisnis + audit. Skema aktual (Alembic 0001):

| Kolom | Tipe | Catatan |
|---|---|---|
| `outbox_id` | String(36) PK | UUID |
| `event_id` | String(16) | ID enterprise, mis. `EVT-001` |
| `event_name` | String(64) | mis. `CaseCreated` |
| `payload` | JSON | camelCase, sesuai Event Catalog |
| `created_at` | DateTime (UTC) | waktu tulis |
| `published_at` | DateTime nullable | NULL = belum terkirim |

**Larangan gold-plating (ADR-009 aturan 4):** dilarang membangun publisher framework generik — retry backoff, DLQ, abstraksi multi-broker — sebelum broker nyata dipilih. Publisher in-process sederhana boleh menguras outbox di DEV. Trigger evaluasi broker: consumer lintas-service pertama, atau gate G2.

## 4. Anti-Corruption Layer — Customer Master (ADR-002 / INT-001)

ECMP **bukan** System of Record pelanggan (ADR-002). Semua akses data pelanggan lewat ACL di domain CRM:

- Model internal ECMP (Customer 360 view) dipisahkan dari model Customer Master; translasi terjadi di adapter integrasi (INT-001, `09 Integration Catalog`), bukan tersebar di service.
- Pola data: **local read-only cache** yang disinkronkan dari Customer Master (event atau scheduled pull); UI wajib menampilkan "data as of \<timestamp\>".
- **Dilarang:** write-back ke Customer Master di luar integrasi resmi; menyimpan field master sebagai data milik ECMP; memakai skema Customer Master mentah sebagai model internal (itulah korupsi yang dicegah ACL).

## 5. Hexagonal (Ports & Adapters)
Domain di tengah; adapter untuk API, DB, message bus, sistem eksternal. Gunakan untuk modul integration-heavy (adapter CRM/Customer Master, Notification). ACL §4 adalah kasus khusus pola ini.

## 6. Repository Pattern
Abstraksi persistence di belakang interface. **Belum dipakai** — dengan satu aggregate, `service.py` memakai session SQLAlchemy langsung (ADR-005). Diadopsi bersamaan full layering saat aggregate >1 (review G1).

## 7. Event Driven Pattern (ADR-001)
Publikasikan domain event untuk reaksi lintas modul. Baseline events: `CaseCreated`, `CaseAssigned`, `StatusChanged`, `SLABreached`, `CaseClosed`, `ConfigChanged` — SoT di `08 Event Catalog/events/events.yaml`. Mekanisme emisi saat ini = outbox (§3).

## 8. CQRS (Optional)
Pisahkan write model dan read model. **Ditunda secara eksplisit** (ADR-005, OQ-003 Resolved). Adopsi hanya bila kompleksitas read terbukti, lewat ADR baru.

## 9. When-to-use Matrix

| Pattern | Pakai saat | Jangan pakai saat | Status di ECMP |
|---|---|---|---|
| Minimal split (§1) | Selalu — baseline setiap service | — | ✅ Dipakai (`implementation/backend`) |
| Full layering + Repository (§1, §6) | Service punya >1 aggregate | Aggregate tunggal (ceremony > nilai) | 🕓 Review di G1 |
| Business action (§2) | Semua write dengan invarian/audit/event | — (CRUD generik dilarang untuk write) | ✅ Dipakai |
| Transactional outbox (§3) | Write bisnis harus emit event, broker belum ada | Data internal tanpa konsumen event | ✅ Dipakai |
| ACL (§4) | Konsumsi data dari sistem eksternal yang bukan milik ECMP | Data yang ECMP miliki sendiri | 🕓 Wajib saat CRM/Customer 360 dibangun |
| Hexagonal (§5) | Modul dengan banyak adapter eksternal | Service internal sederhana | 🕓 Notification/CRM |
| Event driven (§7) | Reaksi lintas modul/domain | Alur sinkron dalam satu transaksi | ✅ Via outbox |
| CQRS (§8) | Read complexity/skala terbukti + ADR | Default apa pun | ⛔ Ditunda |

## Adoption Rule
Deviasi dari pola di atas (atau adopsi pola berstatus 🕓/⛔ lebih awal) membutuhkan ADR + Architecture Review (`../18 Architecture Governance`).
