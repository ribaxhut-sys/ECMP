# ECMP Observability Standard

| Field | Value |
|---|---|
| ID | TS-OBS-001 |
| Version | 0.1 |
| Owner | Tech Lead Backend |
| Reviewer | Solution Architect / DevOps Lead |
| Approver | Architecture Board |
| Status | 🟡 Draft (full standard) — **Mode A floor §1–§3 Accepted via DEC-021 (2026-08-01)** |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Standar observability yang **diaktifkan di gate G1** (backlog TS-001 §6, DEP-001 §5, TST-001). Dokumen ini menetapkan kontrak lebih dulu agar implementasi G1 tidak berdebat format — **tidak ada dependensi kode yang dipasang sekarang** (anti gold-plating, TS-001 §6).

## 1. Structured Logging (aktif di G1)

- Format: **JSON satu baris per record** ke stdout — tanpa multi-line, tanpa format teks bebas.
- Field wajib:

| Field | Isi |
|---|---|
| `timestamp` | UTC, ISO-8601 (`2026-07-21T09:00:00.000Z`) |
| `level` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `service` | Nama service (`ecmp-case-service`) |
| `correlation_id` | Dari §2; wajib pada log dalam konteks request |
| `message` | Ringkas, bebas PII |
| `extra` | Objek opsional untuk konteks terstruktur (mis. `caseId`, durasi) — bukan string gabungan |

- Contoh:

```json
{"timestamp": "2026-07-21T09:00:00.000Z", "level": "INFO", "service": "ecmp-case-service", "correlation_id": "a1b2c3d4", "message": "case created", "extra": {"caseId": "CASE-1A2B3C4D5E"}}
```

## 2. Correlation ID (aktif di G1)

- Header: **`X-Request-ID`**.
- Aturan: bila client mengirim header → pakai nilainya; bila absen → **generate** (UUID) di middleware.
- Nilai di-**echo** kembali di response header `X-Request-ID`, disertakan di setiap log record request tersebut, dan **boleh** disertakan di `details` error envelope (field `details` memang opsional — TS-001 §2.2) untuk korelasi support.
- Propagasi lintas service (header diteruskan pada call keluar) berlaku begitu ada call lintas service — sekarang belum ada (ADR-009).

## 3. Larangan PII di Log (berlaku SEKARANG)

Satu-satunya bagian standar ini yang sudah mengikat sebelum G1 (identik TS-001 §6, selaras klasifikasi PII `ai/05_database.md`):

- Dilarang menulis PII ke log: `description`, `subject`, nama/kontak pelanggan, payload pelanggan.
- Log hanya boleh memuat ID (`caseId`; `customerId` hanya bila perlu untuk trace) dan metadata teknis.
- Dilarang log token/credential dalam bentuk apa pun.

## 4. Metrik Minimum (Planned — saat platform target ADR-010 ada)

Diaktifkan saat baseline SIT/UAT ADR-010 berjalan; dilarang memasang stack metrics spekulatif sebelum itu (DEP-001 §5):

- **Request rate, latency (p50/p95), error rate** per endpoint (`/v1/cases`, `/v1/cases/{caseId}`, `/health`).
- **Outbox backlog gauge**: jumlah baris `outbox` dengan `published_at IS NULL` + umur baris tertua (selaras playbook P3 OPS-RB-001).
- Pemilihan tooling (Prometheus/managed) = bagian aktivasi platform, bukan keputusan dokumen ini.

## 5. Tracing (ditunda)

Distributed tracing **ditunda sampai ada lebih dari satu service/consumer nyata** (trigger mengikuti ADR-009 broker / ADR-010 platform). Sampai saat itu, correlation-id (§2) adalah mekanisme korelasi resmi satu-satunya.

## 6. Mapping ke pytest/CI saat ini

- **Belum enforced** — tidak ada tes/CI step yang memverifikasi format log hari ini; enforcement masuk exit criteria implementasi G1.
- Saat G1: tambahkan tes pytest yang memverifikasi (a) log record JSON valid dengan field wajib §1, (b) `X-Request-ID` di-echo di response, (c) tidak ada `subject`/`description` bocor ke log pada jalur create.
- Larangan PII §3 sudah bisa dijaga lewat code review (DoD ENG-003) tanpa menunggu G1.

## Related
- `./ECMP_Technical_Standards_v0.1.md` (TS-001 §6)
- `../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` (DEP-001 §5)
- `../13 Test Strategy/ECMP_Test_Strategy_v0.1.md` (TST-001)
- `../05 Architecture Decision Records/ECMP_ADR_009_Message_Broker_Deferral_v1.0.md`, `ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md`
- `../ai/05_database.md` — klasifikasi PII
