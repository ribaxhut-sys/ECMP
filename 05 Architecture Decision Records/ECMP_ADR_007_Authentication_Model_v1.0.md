# ECMP_ADR_007_Authentication_Model_v1.0

| Field | Value |
|---|---|
| ID | ADR-007 |
| Version | 1.0 |
| Owner | Security Architect |
| Reviewer | Tech Lead / Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

- ADR Status: Accepted
- Date: 2026-07-21
- Decision Owners: Security Architect, Tech Lead
- Related Domains: Core Platform

## Context
Runtime slice memakai token statis `dev-token` hardcoded dengan principal tetap. OpenAPI mengklaim `bearerFormat: JWT`. Tidak ada standar AuthN atau register batasan.

## Decision
### Fase slice (Sprint-01 / lokal — berlaku sekarang)
1. AuthN = Bearer token statis **dari environment** (`ECMP_DEV_TOKEN`), bukan hardcoded literal di source.
2. Principal slice: `{userId, permissions[]}`; permission = `cases:create`, `cases:read` (selaras Role Matrix `10 Security`).
3. **Batasan terdaftar (known limitation):** tanpa expiry, tanpa user store, tanpa multi-principal. Hanya untuk DEV lokal/CI. Dilarang untuk shared UAT/PROD.
4. Semantik status: token hilang/salah → **401** (`UNAUTHENTICATED`); token sah tanpa permission → **403** (`FORBIDDEN`).

### Fase target (sebelum shared UAT)
5. JWT ditandatangani IdP (OIDC): validasi signature, `exp`, `iss`, `aud`; claims `{sub, roles[], permissions[], orgUnitId}`.
6. Pemilihan IdP/SSO = keputusan lanjutan (Blueprint: Future Enhancement); bukan blocker G0/G1.

> **Elaborasi fase target (2026-07-21):** desain lengkap fase target diputuskan di **ADR-012** (`ECMP_ADR_012_Target_Authentication_Architecture_v1.0.md`) dengan arsitektur normatif di `10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001). Catatan penyempurnaan butir 5: token membawa `{sub, roles[], orgUnitId}`; `permissions[]` **tidak** dimuat di token melainkan diresolusi Core Platform dari Role-Permission matrix (menjaga SoT tunggal per ADR-008). Fase slice (butir 1–4) tetap berlaku tanpa perubahan untuk DEV lokal/CI.

## Consequences
- OpenAPI `bearerFormat: JWT` menjadi target-akurat; deskripsi slice mencantumkan mode dev-token.
- Gate rilis: tidak ada environment bersama tanpa fase target diaktifkan.
