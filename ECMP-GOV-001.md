# GOV-001 — ECMP Delivery Governance Categories

| Field | Value |
|---|---|
| Decision ID | GOV-001 |
| Status | 🔒 LOCKED |
| Date | 2026-08-03 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 |

## Decision

Setiap diskusi/delivery baru harus masuk **satu** kategori:

| Category | Purpose | Examples | Cadence |
|---|---|---|---|
| **A — Constitution** | Aturan permanen | Golden Rules, boundary, ADR, Mode B | Sangat jarang |
| **B — Specification** | Bagaimana sesuatu harus bekerja | CWX-M1…M4, Queue Spec | Paling sering |
| **C — Implementation** | Baru setelah Spec + DoR | React, FastAPI, tests | Setelah B |

## Larangan (tanpa Board/ADR)

Tidak mengusulkan secara spontan: ECOS baru, Workspace baru, Engine baru, Layer platform baru, Capability OOS, redesign menyeluruh.

## Workflow

```
Board / ADR → CWX Spec → Design Review → Implementation → Verification → Architecture Review
```

## Definition of Ready / Done

- **DoR:** tujuan jelas · tidak bentrok Board/ADR/CONSTITUTION · UX Contract · AC · Out of Scope jelas.
- **DoD:** AC + Golden Rules + CWX-R + Dual-SoT intact + no Mode B + no SoR baru + Functional/Cognitive/Consistency.
