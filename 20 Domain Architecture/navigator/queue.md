# Domain Navigator — Queue

| Field | Value |
|---|---|
| ID | EOS-NAV-QUEUE |
| Version | 0.2 |
| Owner | Architecture |
| Reviewer | PMO / Enterprise Architecture |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-24 |
| Next Review | auto |

> Command concept: _Masuk ke domain Queue_

## Quick Pack

- Domain: `20 Domain Architecture/Queue/README.md`
- Domain Architecture: `QUEUE_DOMAIN_ARCHITECTURE.md`
- Application Architecture: `QUEUE_APPLICATION_ARCHITECTURE.md`
- Model: `QUEUE_MODEL.md`
- Commands: `QUEUE_COMMAND_GUIDE.md`
- Queries: `QUEUE_QUERY_GUIDE.md`
- Lifecycle: `QUEUE_TICKET_LIFECYCLE.md`
- Guides: `QUEUE_DEVELOPER_GUIDE.md`, `QUEUE_APPLICATION_DEVELOPER_GUIDE.md`

## API

- — (no HTTP in TASK-061 / TASK-062)

## Tests

- `backend/tests/test_queue_domain.py`
- `backend/tests/test_queue_application.py`

## Active / Related Sprints

- Sprint-17 (TASK-061 Domain Foundation, TASK-062 Application Foundation)

## Notes

Domain model + application CQRS foundation — no persistence, REST, display,
kiosk, or notification. STOP after TASK-062.
