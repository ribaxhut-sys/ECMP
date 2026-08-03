# CWX-M1 — Experience Foundation

| Field | Value |
|---|---|
| Document ID | CWX-M1 |
| Status | 🔒 LOCKED (specification) |
| Epic | EPIC-CW-001 |
| Parent | CWX-000 |
| Date | 2026-08-03 |
| Implementation | DELIVERED (FE Mode A) — Header · Decision Bar · Layout. Portal: `docs/governance/ECMP-CWX-M1.md` |

## Objective

Kerangka pengalaman Case yang terasa produk baru — **bukan** seluruh Case Workspace.

## In scope

- Context Header  
- Decision Bar  
- Context-Aware Layout (kerangka + slot placeholders)  
- UX Contract / Acceptance Criteria  

## Out of scope

Conversation · Evidence redesign · Timeline redesign · Activity Feed · Notes · Audit · Decision History · Customer History implementation · Notification · AI · Search redesign · Regional/Enterprise Workspace · Backend/API/DB/Auth changes  

## Components

### Context Header

- Purpose: orientasi ≤5 detik  
- Always: Complaint ID, Customer, Title, Priority, Current Work, Owner, SLA  
- Never: Timeline, History, Statistics, Charts, Decision History, Audit  
- Sticky · ≤2 visual rows · responsive · Zero Duplicate Context  

### Decision Bar

- Visibility: Role ∧ Permission ∧ State ∧ Business Rule  
- Max 3 primary · secondary in overflow  
- Never illegal actions · never disabled-without-explanation (prefer hide)  

### Context-Aware Layout

| Level | Context | Slots |
|---|---|---|
| 1 | Normal | Header · Main placeholder · Decision Bar |
| 2 | Repeat | + Customer History slot (placeholder M1) |
| 3 | Escalated | + Decision Status slot (placeholder M1) |
| 4 | Critical | + SLA Alert slot (placeholder M1) |

Layout level derived from **existing** status/priority/SLA signals only. No invented repeat engine in M1.

## Success dimensions

Functional · Cognitive · Consistency (CWX-R)
