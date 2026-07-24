# Complaint Processing Developer Guide (CAPABILITY-005)

| Field | Value |
|---|---|
| ID | DEV-COMPLAINT-005 |
| Version | 1.0 |
| Owner | Backend Lead |
| Status | 🟢 Implemented |

## Architecture

```text
HTTP
 ↓
Controller (thin)
 ↓
ComplaintProcessingApplicationService (orchestration)
 ↓
ComplaintDomainService → Complaint aggregate methods
 ↓
ComplaintRepository (port)
 ↓
SqlAlchemyComplaintRepository
 ↓
PostgreSQL (complaint_cases)
```

## Use cases

| Method | Domain |
|---|---|
| `start_processing` | `complaint.start_processing()` |
| `resolve` | `complaint.resolve(summary, resolved_by)` |
| `close` | `complaint.close()` |
| `reopen` | `complaint.reopen(reason?)` |

Application service loads via repository, calls domain, persists via `update`.
No business rules in Application or Repository.

## Persistence

Nullable columns (migration `0029_complaint_processing`):

- `resolution_summary`
- `resolution_resolved_by`
- `resolution_resolved_at`

Backward compatible with CAPABILITY-004 rows.

## Out of scope

Timeline · Escalation · SLA · Notification · Audit · Auth · AI
