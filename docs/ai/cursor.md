# Cursor Integration

| Field | Value |
|---|---|
| ID | EAR-PORTAL-AI-005 |
| Version | 1.1 |
| Owner | Engineering Manager |
| Reviewer | Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Always-on rule
`.cursor/rules/ecmp-ai-platform.mdc`

## Feature implementation pattern
1. Read domain docs (`ai/domain/...`)
2. Read engineering standards (`ai/08_standards.md`)
3. Read API/Event context if relevant
4. Implement in `implementation/`
5. Run checks
6. Update documentation when design changes

## Recommended prompt
Use `ai-platform/prompts/implement-feature/v1/prompt.md` with `@ai-platform/policies/ai-rules.md` and sprint/domain files attached.
