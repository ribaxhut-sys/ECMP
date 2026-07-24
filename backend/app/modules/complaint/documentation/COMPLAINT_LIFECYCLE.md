# Complaint Lifecycle (CAPABILITY-004 / CAPABILITY-005)

## Happy path

```text
OPEN → IN_PROGRESS → RESOLVED → CLOSED
```

## Reopen

```text
RESOLVED → IN_PROGRESS
```

## Rules

| From | Allowed next |
|---|---|
| OPEN | IN_PROGRESS |
| IN_PROGRESS | RESOLVED |
| RESOLVED | CLOSED, IN_PROGRESS (reopen) |
| CLOSED | (terminal) |

## Forbidden examples

- `OPEN → CLOSED`
- `OPEN → RESOLVED`
- `IN_PROGRESS → CLOSED`
- `CLOSED → OPEN`
- `CLOSED → IN_PROGRESS`

Invalid transitions raise `ComplaintDomainError` (`INVALID_COMPLAINT_TRANSITION`).

## Processing endpoints

Prefer dedicated operations over generic PUT status:

| Operation | Endpoint |
|---|---|
| Start | `POST .../start` |
| Resolve | `POST .../resolve` |
| Close | `POST .../close` |
| Reopen | `POST .../reopen` |

Validation lives in `domain/lifecycle.py` and aggregate methods
(`start_processing` / `resolve` / `close` / `reopen`), enforced via
`ComplaintDomainService` and `ComplaintProcessingApplicationService`.
