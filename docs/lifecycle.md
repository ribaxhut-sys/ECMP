# ECMP Delivery Lifecycle

| Field | Value |
|---|---|
| ID | EAR-PORTAL-006 |
| Version | 1.1 |
| Owner | Enterprise Architecture / PMO |
| Reviewer | Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## End-to-End Flow

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
(ai/sprint, ai/domain, ai-platform policies, 00–10 context)
      │
      ▼
Cursor + Claude → Implementation
      │
      ▼
Testing (13) → Release (16) → Deployment (14)
      │
      ▼
Operations (15)
      │
      ▼
Feedback / Continuous Improvement
      │
      ├──► Blueprint / Rules / FRD
      ├──► ADR / Architecture
      └──► API / Event / Runbook / AI Context
```

## Quality Gates

| Gate | Requirement |
|---|---|
| Scope Gate | Blueprint In/Out of Scope confirmed |
| Architecture Gate | SA + Domain (+ ADR if needed) |
| Spec Gate | FRD + API/Event catalog readiness |
| AI Gate | `ai-platform/policies/ai-rules.md` + active sprint loaded |
| Quality Gate | Tests + `ear_repo_check` |
| Ops Gate | Runbook/monitoring readiness |

## Key Principles
- AI Context is a **living sync layer**, not a one-time stage.
- Feedback is **multi-target**, not Blueprint-only.
- FRD follows architecture clarity; limited parallel iteration is allowed.
