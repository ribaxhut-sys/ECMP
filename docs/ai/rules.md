# AI Rules

| Field | Value |
|---|---|
| ID | EAR-PORTAL-AI-001 |
| Version | 1.1 |
| Owner | Enterprise Architecture |
| Reviewer | Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Canonical source: `ai-platform/policies/ai-rules.md` (`ai/rules.md` is a legacy compatibility pointer)

## Must Follow (summary)
- No Business Rule changes without ADR
- No API outside API Catalog / OpenAPI
- Follow Engineering Standards
- Every endpoint has OpenAPI
- Schema changes need migration plan
- Every event is in Event Catalog
- ECMP is not Customer Master SoR
- Keep docs synchronized with design/code changes
