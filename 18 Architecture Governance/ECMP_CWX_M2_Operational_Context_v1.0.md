# CWX-M2 — Operational Context

| Field | Value |
|---|---|
| Document ID | CWX-M2 |
| Status | 🔒 LOCKED (specification) |
| Epic | EPIC-CW-001 |
| Parent | CWX-M1 / CWX-000 |
| Date | 2026-08-03 |
| Implementation | DELIVERED (FE Mode A). Portal: `docs/governance/ECMP-CWX-M2.md` |

## Objective

Memperbaiki pemahaman operasional Case dalam ≤15 detik — **extend** CWX-M1, bukan redesign.

Primary question: *"What is happening with this Case?"*

## In scope

- Operational Context Panel  
- Current Work Panel  
- Case Summary Card  
- Context Badges  
- Customer Summary (reference only)  

## Out of scope

Conversation · Timeline redesign · Activity Feed · Notes · Decision Notes · Evidence redesign · Audit · Decision History · Notification · AI · Search/Queue redesign · Regional/Enterprise Workspace · Backend/API/DB · State machines · Workflow engine  

## Zero Duplicate Context

Context Header tetap kanonik untuk: Complaint ID · Customer · Priority · Owner · Current Work · SLA.  
Operational Context **tidak** mengulang field tersebut.

## Data rules

- Hanya data existing; field kosong → omit  
- Tidak invent repeat complaint / customer profile / API / business rules  
- Next Expected Action = map presentasi dari status existing saja  
- Badges max 4 visible + overflow; no Repeat Complaint badge  

## Success dimensions

Functional · Cognitive · Consistency (CWX-R)
