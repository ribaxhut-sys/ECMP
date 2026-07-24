# Domain Navigator — Queue

| Field | Value |
|---|---|
| ID | EOS-NAV-QUEUE |
| Version | 0.5 |
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
- Persistence Architecture: `QUEUE_PERSISTENCE_ARCHITECTURE.md`
- REST API: `QUEUE_REST_API.md`
- Model: `QUEUE_MODEL.md`
- Commands: `QUEUE_COMMAND_GUIDE.md`
- Queries: `QUEUE_QUERY_GUIDE.md`
- Lifecycle: `QUEUE_TICKET_LIFECYCLE.md`
- Persistence guides: `QUEUE_REPOSITORY_PATTERN_GUIDE.md`, `QUEUE_MAPPER_GUIDE.md`,
  `QUEUE_ORM_GUIDE.md`, `QUEUE_MIGRATION_GUIDE.md`
- Guides: `QUEUE_DEVELOPER_GUIDE.md`, `QUEUE_APPLICATION_DEVELOPER_GUIDE.md`,
  `QUEUE_PERSISTENCE_DEVELOPER_GUIDE.md`

## API

- OpenAPI: `07 API Catalog/openapi/queue-service.v1.yaml` (API-360…381)
- Runtime: FastAPI `/docs` tags Queues / Queue Tickets / Queue Operations / Queue Counters
- Code: `backend/app/modules/queue/api/`
- Operations: `backend/app/modules/queue/application/services/operations_service.py`
- Ticket numbers: `backend/app/modules/queue/domain/ticket_number.py`
- Execution context: `backend/app/core/request_context/` (CAPABILITY-002)

## Tests

- `backend/tests/test_queue_domain.py`
- `backend/tests/test_queue_application.py`
- `backend/tests/test_queue_persistence.py`
- `backend/tests/test_queue_api.py`
- `backend/tests/test_queue_operations.py`
- `backend/tests/test_request_context.py`

## Active / Related Sprints

- Sprint-17 (TASK-061 Domain Foundation, TASK-062 Application Foundation)
- Sprint-18 (TASK-063 Queue Persistence Foundation)
- Sprint-19 (TASK-064 Queue REST API Foundation)
- CAPABILITY-003 (Queue Operations)

## Notes

Operational queue (open/close/issue/call-next/recall/complete/skip/cancel).
No Redis, display, kiosk, voice, complaint, auth, or dashboard. STOP after
CAPABILITY-003.
