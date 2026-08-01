# ADR-009 Addendum — G2 In-Process Outbox Extension (Mode A)

| Field | Value |
|---|---|
| ID | ADR-009-ADD-G2 |
| Parent | ADR-009 v1.0 |
| Version | 1.0 |
| Status | 🟢 Accepted (Mode A; does not revoke parent deferral) |
| Date | 2026-08-01 |
| Related | DEC-021 |

## Trigger

ADR-009 §3: evaluate broker when (a) first cross-service consumer or (b) gate **G2** starts. G2 started 2026-08-01 for Mode A path.

## Decision (G2 evaluation result)

1. **Continue deferral of physical broker** for Mode A SIT/UAT wave-1.  
2. **Extend** in-process outbox drain as the Mode A transport (Notification stub FR-020 already consumes via drain in `implementation/backend`).  
3. Next mandatory re-evaluation: when a **separate process** must consume outbox for KPI/SLA (FR-030 event clock) or multi-instance deploy requires shared relay.  
4. Parent ADR-009 Decision items 1–4 remain binding; this addendum only records the G2 evaluation outcome.

## Consequences

- No RabbitMQ/Kafka/cloud pub-sub introduction under this addendum.  
- No generic publisher framework.  
- Mode A regression must include outbox drain path (`REGRESSION_PACK_G2.md`).
