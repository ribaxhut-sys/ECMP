# Decision Record — Dashboard API Scope (TASK-027)



| Field | Value |

|---|---|

| ID | DEC-016 |

| Version | 1.0 |

| Owner | Solution Architect |

| Reviewer | Tech Lead |

| Approver | Architecture Board (delegated via TASK-027) |

| Status | Approved |

| Last Review | 2026-07-23 |

| Next Review | 2026-10-23 |



- Type: Project Decision (non-ADR)

- Status: Accepted

- Date: 2026-07-23

- Related: DEC-015, TASK-027, API-319, API-318



## Context



KPI Foundation (API-318), Complaint, SLA, and Timeline modules already expose

operational facts. TASK-027 needs a single Dashboard Summary API that

aggregates those facts for the UI without becoming a second domain.



## Decision



**Create `app/modules/dashboard` as an orchestration layer only.**



- Owns **no** business logic

- Performs **no** KPI calculation

- Stores **no** data (no migration, no dashboard tables)

- Never queries the database directly — calls KPI Service, Timeline Service,

  and Complaint Service



API-319 `GET /api/v1/dashboard/summary` returns:



- **Header** — total / open / closed complaints (from KPI)

- **SLA Summary** — assignment, appointment, resolution, escalation, overall

  each with completed / breached (from KPI)

- **Recent Activity** — latest ≤10 timeline events with event type,

  complaint number, timestamp, actor (from Timeline + Complaint)



Permission: `dashboard:read`.



Frontend replaces multiple dashboard fetches with one API-319 request and

renders Header Cards, SLA Cards, and Recent Activity only.



Remains **out of scope**:



- Charts / graphs / analytics

- Realtime websocket

- Caching / Redis

- Notifications / scheduler / queue

- Export / reporting



## Rationale



Dashboard must stay a thin composition surface so metrics remain consistent

with KPI Foundation and timeline facts, without duplicated aggregation logic.



## Impact



- New module + OpenAPI API-319 + API Catalog

- RBAC adds `dashboard:read`

- Frontend dashboard uses single request



## Links



- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml` (API-319)


