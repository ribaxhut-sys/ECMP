"""Complaint Management Batch 1 (FRD-CM-001) — FR-001…FR-004.

Namespace: /api/v1/cm/* (+ shared CAP-011 attachment routes for API-507…512)
Aggregate persistence: Alembic 0040
Duplicate detection: Alembic 0041 — API-505 / API-506
Attachments (D-06): Alembic 0042 — orchestration over CAP-011
Foundation (Audit+Timeline+Outbox): Alembic 0043 — persist-only outbox
Master Customer: ``CustomerProvider`` via ``app.integrations.customer``
(ADR-002 read-only; not SoR; default stub, swappable via CUSTOMER_PROVIDER).
"""

from __future__ import annotations
