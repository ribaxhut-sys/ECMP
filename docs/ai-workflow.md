# AI Workflow Overview

| Field | Value |
|---|---|
| ID | EAR-PORTAL-003 |
| Version | 0.3 |
| Owner | Enterprise Architecture |
| Reviewer | Engineering Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Canonical detail: `ai/09_workflow.md`

## Official Lifecycle

```text
Business Idea
      │
      ▼
Business Blueprint (01)
      │
      ▼
Business Rules (02)
      │
      ▼
Solution Architecture (04)
      │
      ├── Reference Architecture (19)
      └── Domain Architecture (20)
      │
      ▼
FRD (03) (+ Traceability 26)
      │
      ▼
Sprint Plan + AI Context sync
      │
      ▼
Cursor + Claude → Implementation
      │
      ▼
Testing → Release → Deployment
      │
      ▼
Operations
      │
      ▼
Feedback → Blueprint / Rules / FRD / ADR / Catalogs / AI Context
```

## Role Split

| Tool | Role |
|---|---|
| ChatGPT | Chief Enterprise Architect |
| Claude (Cursor) | Senior Software Engineer |
| Cursor | Development workspace |

## Shared Context
Semua tool wajib berpijak pada `ai/` pack (Single Source of Context).

Lihat:
- [AI Rules](ai/rules.md)
- [Context Pack](ai/context-pack.md)
- [Sprint Context](ai/sprint.md)
- [Prompt Library](ai/prompts.md)
- [Cursor Integration](ai/cursor.md)
