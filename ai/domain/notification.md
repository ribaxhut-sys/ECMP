# Domain Context — Notification

| Field | Value |
|---|---|
| ID | AI-DOM-NOTIF |
| Version | 0.1 |
| Owner | Notification PO / Integration Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Event-driven notifications with templates, routing, delivery logs, retries.

## In Scope
Subscribe to domain events, resolve recipients, deliver (in-app/email first), track status.

## Key Flow
Event → Match Rule/Template → Recipients → Deliver → Log → Retry if failed

## Detailed Docs
`20 Domain Architecture/Notification/`
