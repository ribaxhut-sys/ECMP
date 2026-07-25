# Sprint F2 — Complaint Module

**Status:** Complete  
**Scope:** Complaint List, Detail, Create, Edit against frozen backend APIs.  
**Out of scope:** Queue module, Assignment workflows (existing Assignment UI on detail left untouched; no new Queue work).

## 1. Folder structure

```
frontend/src/
  app/(app)/complaints/
    page.tsx                 # List (API-388)
    new/page.tsx             # Create
    [id]/page.tsx            # Detail
    [id]/edit/page.tsx       # Edit (API-204)
  features/complaints/
    ComplaintListView.tsx
    complaintListFilters.ts
    ComplaintDetailView.tsx
    CreateComplaintView.tsx
    createComplaintForm.ts
    EditComplaintView.tsx
    editComplaintForm.ts
    ComplaintAttachmentsCard.tsx
    TimelineCard.tsx / SlaCard.tsx / …
  lib/api/
    complaints.ts            # search + update + existing CRUD
    attachments.ts           # list by complaint + upload
    types.ts                 # ComplaintSearch*, ComplaintUpdate*, Attachment
```

## 2. Screens implemented

| Screen | Route | Notes |
|---|---|---|
| Complaint List | `/complaints` | Keyword, status, priority, category, branch, sort, order, page size; server pagination; loading / empty / error |
| Complaint Detail | `/complaints/[id]` | Info, current status, SLA, attachments (+ upload), timeline |
| Create Complaint | `/complaints/new` | Validation, optional multi-file upload after create, redirect to detail |
| Edit Complaint | `/complaints/[id]/edit` | Mutable fields only (API-204); requires `complaints:update` |

## 3. Backend APIs consumed

| ID | Endpoint | Use |
|---|---|---|
| API-388 | `GET /api/v1/complaints/search` | List + filter + sort + pagination |
| API-201 | `POST /api/v1/complaints` | Create |
| API-203 | `GET /api/v1/complaints/{id}` | Detail / edit load |
| API-204 | `PUT /api/v1/complaints/{id}` | Edit save |
| API-209 | `GET /api/v1/complaints/{id}/timeline` | Detail timeline |
| API-314 | `GET /api/v1/complaints/{id}/sla` | Detail SLA |
| API-387 | `GET /api/v1/complaints/{id}/attachments` | Detail attachments |
| API-323 | `POST /api/v1/attachments` | Create/detail upload |
| API-324/325 | attachment get/download | Preview / download |
| — | `GET /api/v1/customers`, `/branches` | Create/edit lookups |

No mocked APIs. No backend changes.

## 4. Validation

- **Create:** client checks required customer, subject ≤200, description ≤5000, priority, branch UUID, optional channel/category/reportedAt (aligned with API-201).
- **Edit:** subject, description, priority required; channel/category length; branch UUID when set (aligned with API-204). Status / customer / number not editable here.
- Server `VALIDATION_ERROR` / HTTP errors surfaced as form alerts.

## 5. Known limitations

- List uses search envelope (`items`/`pagination`), not the simpler `GET /complaints` list.
- Attachment upload on create is best-effort after complaint insert; failures can be retried on detail.
- Customer cannot be changed on edit (not in API-204).
- Status changes remain on dedicated workflow APIs (not part of Edit form).
- Queue screens and new Assignment UX were not implemented in F2.

## 6. Commit

See git commit hash for this sprint.
