# Reference Patterns

| Field | Value |
|---|---|
| ID | EAR-PORTAL-MIRROR |
| Version | 0.2 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The approved architecture patterns (REF-001, 🟢 Approved baseline) for ECMP — patterns already used in code reference the actual implementation; unused patterns carry explicit adoption conditions:

- **Layered architecture with minimal split** (ADR-005): `main.py` → `service.py` → `models.py`/`db.py`; route handlers hold no business rules; full 4-layer packaging only when a service has more than one aggregate.
- **Business Action pattern**: application layer exposes named business actions (`register_case`, `get_case`) instead of generic CRUD, so each action carries its own invariants (initial status, audit, event).
- **Transactional Outbox** (ADR-009, in use): events written to the `outbox` table in the same transaction as the business write and audit record.

**Canonical source:** `19 Reference Architecture/PATTERNS.md`.
