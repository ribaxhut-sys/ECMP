# Domain — Notification

| Field | Value |
|---|---|
| ID | EAR-PORTAL-DOM-NOTIF |
| Version | 0.2 |
| Owner | Notification PO |
| Reviewer | Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The Notification domain sends event-driven notifications with templates, routing rules, delivery logs and retries.

- **Scope**: subscribe to domain events, resolve recipients, deliver (in-app/email first), track delivery status.
- **Key flow**: Event → Match Rule/Template → Recipients → Deliver → Log → Retry if failed.
- **Rules**: notifications only for configured events/recipients (BR-004/BR-NOTIF-01); delivery log is mandatory (BR-NOTIF-03).
- **Consumes**: case lifecycle events (EVT-001, EVT-002, EVT-003, EVT-005, EVT-007) and SLA breaches (EVT-004).

Canonical AI context: `ai/domain/notification.md`  
Detailed architecture: `20 Domain Architecture/Notification/`
