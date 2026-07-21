# ECMP Integration: Customer Master Read (INT-001)

| Field | Value |
|---|---|
| ID | INT-001 |
| Version | 0.1 |
| Owner | Integration Lead |
| Reviewer | Solution Architect, CRM Domain PO, Security |
| Approver | Architecture Board |
| Status | 🟢 Approved (untuk mode stub Sprint-01) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Mendefinisikan integrasi read-only ECMP ke sistem eksternal **Customer Master** untuk validasi/referensi data pelanggan. ECMP **bukan** SoR pelanggan (ADR-002); data pelanggan di ECMP hanyalah cache/reference read-only.

## Integration Summary

| Field | Value |
|---|---|
| Integration ID | INT-001 |
| Source System | Customer Master (eksternal) |
| Target System | ECMP (case-service) |
| Business Purpose | Validasi existence `customerId` saat create case; referensi data pelanggan di CRM domain |
| Pattern | Synchronous API read + cache read-only (ADR-002) |
| Direction | Inbound read-only ke ECMP (ECMP tidak pernah write-back) |
| Data Entities | Customer Reference (lihat `../06 Data Dictionary`) |
| Frequency / Trigger | On-demand saat `POST /v1/cases` (API-001); planned: `GET /v1/customers/{customerId}` (API-010) |
| SLA | Timeout 3s per call (mode real) |
| Security controls | Read-only credential; tidak menyimpan PII melebihi kebutuhan cache (lihat `../10 Security and Access Standards`) |
| Owner | Integration Lead |
| Status | Stub mode aktif (Sprint-01); real mode planned |

## MODE STUB (aktif Sprint-01)
- Tidak ada panggilan ke sistem eksternal sama sekali.
- `customerId` non-empty apa pun **diterima**.
- `customerVerified=false` selalu (lihat FRD-001 §8).
- **Dilarang mengarang data pelanggan** — stub tidak boleh mengembalikan nama/kontak/atribut pelanggan fiktif; hanya keputusan accept + flag unverified.

## MODE REAL (target)
- Validasi existence pelanggan by `customerId` ke Customer Master.
- Timeout: **3 detik** per panggilan.
- Fallback saat Customer Master tidak tersedia / timeout: **perlakukan seperti stub** — terima `customerId` non-empty, set `customerVerified=false` (flag unverified), dan **lanjutkan create case**. Prinsip: availability > verification (FRD-001 §8).
- Hasil verifikasi sukses: `customerVerified=true` pada Case.

## Error Handling & Retry
- Mode stub: tidak berlaku (tidak ada panggilan eksternal).
- Mode real: tanpa retry synchronous pada jalur create (fallback langsung ke perilaku stub agar create tidak terblokir); detail retry/circuit breaker ditentukan saat akses sistem eksternal tersedia.

## Open Items
- Endpoint, auth scheme, dan kontrak nyata Customer Master **menunggu akses sistem eksternal**.
- Kebijakan cache TTL / `last_synced_at` untuk Customer Reference (CRM) menyusul bersama API-010.

## Related
- `../05 Architecture Decision Records/ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0.md`
- `../03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` (§8 Integration Requirements)
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` (Customer Reference)
- `../07 API Catalog/openapi/case-service.v1.yaml`
