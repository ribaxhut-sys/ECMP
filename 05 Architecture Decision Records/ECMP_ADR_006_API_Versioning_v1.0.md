# ECMP_ADR_006_API_Versioning_v1.0

| Field | Value |
|---|---|
| ID | ADR-006 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Leads / Integration Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- ADR Status: Accepted
- Date: 2026-07-21
- Decision Owners: Solution Architect
- Related Domains: All (API contracts)

## Context
Versi API saat ini hanya tersirat dari nama file (`case-service.v1.yaml`) dan `info.version`. Tidak ada strategi URL/header maupun kebijakan deprecation.

## Options Considered
- **A — URL prefix `/v1`** (dipilih): eksplisit, mudah di-route gateway, terlihat di log.
- **B — Header versioning:** rapi tapi mudah terlewat oleh klien internal.
- **C — Tanpa versi:** menutup jalan breaking change.

## Decision
1. Semua path API produk diprefix **`/v1`** (mis. `POST /v1/cases`). `/health` tetap tanpa versi (operasional).
2. **MAJOR** version naik hanya untuk breaking change; bidang baru opsional = MINOR (tanpa perubahan prefix).
3. **Deprecation policy:** versi lama minimal hidup 2 minor release setelah pengumuman; respons versi deprecated menyertakan header `Deprecation: true` + `Sunset: <date>`.
4. Penamaan file katalog: `<service>.v<major>.yaml` di `07 API Catalog/openapi/` (pola existing dipertahankan sebagai standar; konvensi `ECMP_API_...` di README disesuaikan).
5. `info.version` = semver penuh kontrak (mis. `1.1.0`).

## Consequences
- Breaking change punya jalur komunikasi konsumen yang jelas.
- Perubahan sekali jalan pada slice: path `/cases` → `/v1/cases` (dilakukan di G0 sebelum ada konsumen eksternal).
