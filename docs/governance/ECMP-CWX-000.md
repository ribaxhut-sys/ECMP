# CWX-000 — Case Workspace Experience Product Constitution

| Field | Value |
|---|---|
| Document ID | CWX-000 |
| Status | 🔒 LOCKED |
| Date | 2026-08-03 |
| Epic | EPIC-CW-001 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → **CWX-000** → CWX-M* → CWX-R → Implementation |

## Single responsibility

> Mendefinisikan **bagaimana pengguna bekerja di dalam Case Workspace**.

CWX **bukan** tempat mendefinisikan: Business Rules, API, Domain Model, Data Ownership, SoR, Workflow Engine, Architecture Pattern (hanya merujuk).

## Dual-SoT

```
Case Workspace Experience (CWX)
        │
   ┌────┴────┐
   ▼         ▼
Foundation  Aggregate
/api/v1/complaints   /api/v1/cm
```

No silent merge. No rewrite without Architecture Decision. Mode B not unlocked.

## Golden Rules

1. Business First  
2. Case is the Product (Queue = entry)  
3. Context Before Action  
4. Zero Duplicate Context  
5. Progressive Disclosure  
6. Context-Aware Experience  
7. Experience Above Implementation  
8. No Rewrite Without Decision  
9. Reference, Don't Redefine  

## Living artifacts (only)

CWX-000 · CWX-M1 · CWX-M2 · CWX-M3 · CWX-M4 · CWX-R  

No CWX-M5 / CWX-v2 / CWX-Architecture / CWX-Business Rules without Category A governance.
