# ECMP Compliance Control Matrix v0.1

| Field | Value |
|---|---|
| ID | CMP-001 |
| Version | 0.1 |
| Owner | Compliance Officer |
| Reviewer | Security Architect / Legal |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## 1. Compliance Scope
Pemetaan requirement kepatuhan terhadap kontrol nyata ECMP untuk scope Sprint-01 slice (case-service: create/get case, audit, outbox) plus baseline dokumen yang sudah disepakati. Dokumen ini **memetakan** kontrol — **bukan** pernyataan/klaim kepatuhan; klaim kepatuhan memerlukan asesmen formal setelah konfirmasi Legal atas daftar regulasi yang berlaku.

Out of scope: sertifikasi eksternal, DPIA, asesmen regulasi sektor spesifik (belum ada konfirmasi Legal bahwa itu berlaku).

## 2. Applicable Requirements
Baseline kandidat — **menunggu konfirmasi Legal**; jangan diperlakukan sebagai daftar final:

| Req-ID | Requirement | Jenis | Status konfirmasi |
|---|---|---|---|
| REQ-INT-01 | Kebijakan internal keamanan data (AuthN/AuthZ wajib, need-to-know, audit trail, pengelolaan secret) — dioperasionalkan via `10 Security and Access Standards` | Kebijakan internal | Berlaku (baseline internal) |
| REQ-REG-01 | UU Pelindungan Data Pribadi (UU PDP) Indonesia — kandidat regulasi relevan karena ECMP memproses PII pelanggan (Customer Reference, konten case) | Regulasi | **Kandidat — menunggu konfirmasi Legal** (cakupan pasal/kewajiban belum diases) |

Regulasi lain (sektor, internal group policy tambahan) belum didaftarkan — ditambahkan hanya setelah konfirmasi Legal.

## 3. Control Mapping
Hanya kontrol yang benar-benar ada di kode/dokumen ECMP:

| Req-ID | Aspek | Kontrol ECMP | Status kontrol |
|---|---|---|---|
| REQ-INT-01 / REQ-REG-01 | Akuntabilitas & jejak audit | Audit trail immutable: `audit_log` append-only, tanpa jalur update/delete aplikasi (BR-008 / BR-CP-03 / FR-001c), ditulis satu transaksi dengan write bisnis | Implemented (Sprint-01) |
| REQ-INT-01 | Kontrol akses | RBAC dengan SoT Core Platform (ADR-008); permission enforced per endpoint (SEC-RAM-001); 401/403 semantik ADR-007 | Implemented (slice: 2 role, 2 permission); role Sprint-02 Planned |
| REQ-REG-01 | Need-to-know / pembatasan akses PII | Masking kontak pelanggan untuk role non-CS (BR-CRM-02 baseline DEC-004, FRD-003) | **Planned** — belum ada endpoint customer di kode |
| REQ-INT-01 | Pengelolaan secret | `.env` git-ignored (`.env.example` non-secret); CI memakai GitHub Actions secrets; tidak ada secret di source | Implemented |
| REQ-REG-01 | Minimalisasi data / bukan master PII | ECMP bukan SoR pelanggan (ADR-002); Customer Reference = cache read-only, tanpa write-back (INT-001); stub dilarang mengarang data pelanggan | Implemented (by design) |
| REQ-REG-01 | Retensi & penghapusan data | Baseline retensi di `ECMP_Data_Retention_Policy_v0.1.md` (CMP-002) | **Baseline dokumen — mekanisme purging belum diimplementasikan** |

## 4. Evidence Repository
Lokasi bukti audit di repo/sistem:

| Bukti | Lokasi | Catatan |
|---|---|---|
| Jejak write per transaksi | Tabel `audit_log` (skema: `06 Data Dictionary` §2; migrasi Alembic `implementation/backend/`) | Append-only (BR-CP-03) |
| Jejak event integrasi | Tabel `outbox` (`published_at` sebagai bukti publikasi) | ADR-009 |
| Bukti quality gate rilis | CI logs GitHub Actions (`.github/workflows/backend-ci.yml`) — lint, OpenAPI validate, migrate, pytest | Wajib hijau sebelum merge |
| Keputusan arsitektur & baseline | `05 Architecture Decision Records/` (ADR), `27 Project Decisions/` (DEC) | Lifecycle di badan dokumen |
| Batasan keamanan yang diterima | `10 Security and Access Standards/ECMP_AuthN_Limitations_Register_v0.1.md` | L-1..L-5 + gate penutupan |

## 5. Gaps & Remediation
| Gap | Dampak | Remediasi | Target |
|---|---|---|---|
| AuthN dev-token statis (tanpa expiry/user store) | Tidak layak untuk environment bersama | Fase target ADR-007: JWT/OIDC | Sebelum shared UAT |
| Retention policy baru baseline dokumen, job purging belum ada | Data tumbuh tanpa batas; kewajiban penghapusan belum bisa dipenuhi | Implementasi job purging per `ECMP_Data_Retention_Policy_v0.1.md`; konfirmasi Legal via DEC | Fase berikut (pasca Sprint-02) |
| DPIA belum ada | Risiko privasi belum diases formal | DPIA setelah konfirmasi Legal daftar regulasi (REQ-REG-01) | Menunggu Legal |
| Masking BR-CRM-02 belum di kode | Kontrol need-to-know PII kontak belum enforced | Implementasi bersama FRD-003 / API-010 (SEC-RAM-001 v0.2 Planned) | Sprint-02 (menunggu DoR) |
| Daftar regulasi belum dikonfirmasi | Scope kepatuhan belum final | Sesi konfirmasi Legal → catat via DEC | Menunggu Legal |

## 6. Audit Calendar
Placeholder — belum ada jadwal audit disepakati:

| Aktivitas | Frekuensi (usulan) | Status |
|---|---|---|
| Review register batasan keamanan (SEC-LIM-001) | Per gate (G0/G1/UAT) | Berjalan via Next Review dokumen |
| Review compliance matrix ini | Kuartalan | Placeholder |
| Audit internal / eksternal | TBD | Menunggu konfirmasi Legal/Compliance |

## 7. Ownership
| Peran | Tanggung jawab |
|---|---|
| Compliance Officer | Pemilik dokumen; koordinasi konfirmasi Legal; update mapping |
| Security Architect | Kontrol keamanan teknis (10 Security); threat model SEC-TM-001 |
| Legal | Konfirmasi daftar regulasi berlaku (REQ-REG-01 dst.) |
| Data Architect | Klasifikasi PII di Data Dictionary (DD-001 Open Items) |
| Business Owner | Persetujuan baseline retensi via DEC |

## Related
- `ECMP_Data_Retention_Policy_v0.1.md` (CMP-002)
- `../10 Security and Access Standards/` (SEC-STD-001, SEC-RAM-001, SEC-LIM-001, SEC-TM-001)
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`
- `../05 Architecture Decision Records/` (ADR-002, ADR-007, ADR-008)
- `../18 Architecture Governance/reviews/EXCEPTION_REQUEST.md`
