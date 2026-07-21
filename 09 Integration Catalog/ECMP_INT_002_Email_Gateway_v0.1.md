# ECMP Integration: Email Gateway (INT-002)

| Field | Value |
|---|---|
| ID | INT-002 |
| Version | 0.1 |
| Owner | Integration Lead |
| Reviewer | Solution Architect, Security |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Placeholder boundary untuk integrasi outbound ke **Email Gateway** yang dipakai domain Notification pada fase **G1+**. Dokumen ini hanya menetapkan boundary; detail kontrak menyusul saat Notification FRD dikerjakan.

## Integration Summary

| Field | Value |
|---|---|
| Integration ID | INT-002 |
| Source System | ECMP (Notification) |
| Target System | Email Gateway (eksternal) |
| Business Purpose | Pengiriman notifikasi email (mis. SLA breach, case assignment) |
| Pattern | Asynchronous outbound (didorong dari outbox/event — ADR-009: broker ditunda) |
| Direction | Outbound dari ECMP |
| Data Entities | Delivery Log, Template, Recipient (lihat `../06 Data Dictionary`) |
| Frequency / Trigger | Event-driven (Notification Rule) |
| SLA | TBD |
| Security controls | TBD (kontak penerima = PII) |
| Owner | Integration Lead |
| Status | Draft — dipakai Notification fase G1+, boundary saja |

## Open Items
- Seluruh detail (provider, protokol, auth, retry, template) menunggu Notification FRD.

## Related
- `../08 Event Catalog`
- `../05 Architecture Decision Records/ECMP_ADR_009_Message_Broker_Deferral_v1.0.md`
