# ECMP AuthN Limitations Register v0.1

| Field | Value |
|---|---|
| ID | SEC-LIM-001 |
| Version | 0.1 |
| Owner | Security Officer |
| Reviewer | Tech Lead |
| Approver | Security Architect |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## Purpose
Mendaftarkan batasan keamanan yang **diketahui dan diterima sementara** pada fase slice (ADR-007), beserta gate yang mewajibkan penutupannya. Register ini mencegah batasan dev diperlakukan sebagai "auth selesai".

## Registered Limitations

| # | Batasan | Risiko | Diterima untuk | Wajib ditutup sebelum | Penutupan |
|---|---|---|---|---|---|
| L-1 | Token Bearer statis dari env (`ECMP_DEV_TOKEN`), tanpa expiry/issuer | Token bocor = akses penuh CS Agent | DEV lokal + CI | Shared UAT | ADR-007 fase target (JWT/OIDC) |
| L-2 | Principal tetap (`cs.agent.1`, `viewer.1`), tanpa user store | Tidak ada identitas individual | DEV lokal + CI | Shared UAT | User store / IdP claims |
| L-3 | Tanpa org-unit scoping (BR-CP-02 belum ditegakkan) | Akses lintas unit tak terkontrol | Sprint-01 (single unit) | Gate G1 (assign/status) | Claims `orgUnitId` + enforcement |
| L-4 | Read-audit ditunda (FRD §9 / OQ-007) | Jejak baca tidak ada | Sampai multi-principal nyata | Review saat UAT | Keputusan BO ulang |
| L-5 | Secrets via `.env` lokal (belum ada vault) | Salah commit = bocor | DEV lokal | PROD | Vault/CI secret store (lihat `14 Deployment Standards`) |

## Kontrol yang SUDAH aktif
- `.env` di-ignore git; `.env.example` tanpa secret nyata
- Tidak ada token hardcoded di source (env-based)
- Write-audit append-only aktif (BR-008 / FR-001c)
- 401/403 semantik benar + Error envelope

## Related
- ADR-007, `ECMP_Role_Access_Matrix_v0.1.md`, `14 Deployment Standards`
