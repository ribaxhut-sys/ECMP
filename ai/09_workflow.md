# 09 — AI + Human Delivery Workflow

| Field | Value |
|---|---|
| ID | AI-CTX-009 |
| Version | 1.1 |
| Owner | Enterprise Architecture / Eng Manager |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Official ECMP Lifecycle

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
(ai/sprint, ai/domain, ai/rules, 00–10 context)
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

## Notes on Sequencing
1. **FRD after architecture clarity** — Domain Architecture should be clear enough; FRD may iterate in parallel once boundaries are stable.
2. **AI Context is a living sync layer** — update `ai/` whenever Blueprint/Rules/Architecture/FRD/contracts change; it is not a one-time gate after FRD.
3. **Feedback is multi-target** — operations insights may update Blueprint, Rules, ADR, catalogs, tests, runbooks, and AI context — not only Blueprint.

## Quality Gates (do not skip)

| Gate | Requirement |
|---|---|
| Scope Gate | Blueprint In/Out of Scope confirmed |
| Architecture Gate | SA + Domain (+ ADR if trade-off/deviation) |
| Spec Gate | FRD + API/Event catalog readiness |
| AI Gate | `ai-platform/policies/ai-rules.md` + active sprint loaded |
| Quality Gate | Tests + `ear_repo_check` |
| Ops Gate | Runbook/monitoring readiness |

## Tool Roles in the Lifecycle

```text
ChatGPT: Blueprint / Rules / Architecture / FRD / Sprint Plan / Review
                 │
                 ▼
Cursor + Claude: Implement against approved specs
                 │
                 ▼
ChatGPT: Architecture / quality review
                 │
                 ▼
Cursor + Claude: Refactor / fix
                 │
                 ▼
Merge + sync EKR artifacts + AI Context
```

## Feature Implementation Pattern (Cursor)

1. Read domain context (`ai/domain/...`)
2. Read `ai-platform/policies/ai-rules.md` + `ai/08_standards.md`
3. Read API/Event context if relevant (`04_api`, `06_events`)
4. Read active sprint brief (`ai/sprint/Sprint-XX.md`)
5. Implement code in `implementation/`
6. Run checks (`ear_repo_check`, tests)
7. Update docs/catalogs/traceability/AI context if design changed

## Feedback Routing

| Feedback type | Update target |
|---|---|
| New capability / scope change | Business Blueprint (01) |
| Process / SLA rule change | Business Rules (02), SLA/KPI (11) |
| Technical trade-off | ADR (05), Architecture (04/19/20) |
| Contract change | API Catalog (07), Event Catalog (08) |
| Acceptance/regression | FRD (03), Test Strategy/cases (13) |
| Production incident | Operations Runbook (15), Security (10) |
| Recurring AI inconsistency | `ai-platform/policies/ai-rules.md`, domain/sprint context |

## Definition of Done (AI-assisted work)
- [ ] Spec references cited (FR/BR/ADR)
- [ ] Rules not violated
- [ ] Contracts updated
- [ ] Tests added/updated
- [ ] Docs + AI Context synced
- [ ] Traceability updated when relationships changed
