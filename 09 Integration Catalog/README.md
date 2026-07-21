# 09 Integration Catalog


| Field | Value |
|---|---|
| ID | INT-000 |
| Version | 0.1 |
| Owner | Integration Lead |
| Reviewer | External System Owners |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Katalog integrasi ECMP dengan sistem eksternal/internal: arah data, pola, SLA, dan ownership.

## Owner
- Document Owner: Integration Lead
- Reviewers: Solution Architect, External System Owners, Security

## Status
Approved (baseline) — INT-001 approved untuk mode stub Sprint-01; INT-002 boundary draft.

## Integration Index

| ID | Nama | Sistem Eksternal | Direction | Pattern | Status |
|---|---|---|---|---|---|
| INT-001 | [Customer Master Read](./ECMP_INT_001_Customer_Master_Read_v0.1.md) | Customer Master | Inbound read-only ke ECMP | Sync API read + cache read-only (ADR-002) | 🟢 Approved (mode stub) |
| INT-001A | [Customer Master Real Mode — Requirements/RFI](./ECMP_INT_001A_Customer_Master_Real_Mode_Requirements_v0.1.md) | Customer Master | — (requirement sheet, bukan kontrak) | Input negosiasi mode real; hasilnya jadi INT-001 v0.2 | 🟡 Draft |
| INT-002 | [Email Gateway](./ECMP_INT_002_Email_Gateway_v0.1.md) | Email Gateway | Outbound dari ECMP | Async outbound (Notification G1+) | 🟡 Draft (boundary saja) |

## Minimum Contents (v1)
- [x] Customer Master integration (read) — INT-001
- [ ] Identity Provider / SSO (if any)
- [x] Email / notification gateway — INT-002 (boundary saja, detail menyusul)
- [ ] Downstream reporting (if any)
- [x] Interface ownership matrix — kolom Owner per integrasi di tiap dokumen INT
- [x] Error handling & retry policy — didefinisikan per integrasi (lihat INT-001 §Error Handling & Retry)

## Template Fields (per integration)
- Integration ID
- Source System
- Target System
- Business Purpose
- Pattern (sync API / async event / batch / file)
- Direction (inbound/outbound/bidirectional)
- Data Entities
- Frequency / Trigger
- SLA
- Security controls
- Owner
- Status

## Boundary Note
- Jangan duplikasi detail schema API/Event di sini; tautkan ke folder 07/08.
- Fokus pada system-to-system mapping dan operasional integrasi.

## Related
- `../06 Data Dictionary`
- `../07 API Catalog`
- `../08 Event Catalog`
- `../10 Security and Access Standards`
