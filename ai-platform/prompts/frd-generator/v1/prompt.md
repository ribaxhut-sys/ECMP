# Prompt — FRD Generator

| Field | Value |
|---|---|
| ID | AI-PROMPT-FRD_GENERATOR |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Engineering Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Use in ChatGPT.

```text
Draft an FRD for ECMP domain: <DOMAIN>.

Use:
- ai/01_business.md
- ai/domain/<domain>.md
- 24 Templates/FRD_TEMPLATE.md structure
- enterprise IDs (FRD/FR/BR)

Constraints:
- Respect In/Out of Scope
- Link business rules as BR-xxx (create placeholders if missing)
- Include acceptance criteria
- Call out API/Event needs as API-xxx / EVT-xxx

Return markdown ready to store in 03 Functional Requirements.
```
