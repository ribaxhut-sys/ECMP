# ECMP — CM Batch-1 SLA Sweep & Outbox Drain (Mode A ops)

| Field | Value |
|---|---|
| Document ID | OPS-CM-B1-SLA-001 |
| Version | 0.1 |
| Date | 2026-08-23 |
| Status | 🟢 Active (Mode A) — **commands shipped** (IG-20260823-01); crontab **not** installed until lab smoke + ops provision |
| Related | ADR-CAP006-002 v0.3.1; DEC-031; FR-030; C-3=1h; C-4=drain; C-6=H-7/H-3/H-1 in-app; B2-26 |
| Mode B | **CLOSED** |

---

## Purpose

1. **SLA sweep** — detect H-7 / H-3 / H-1 / BREACH for Aggregate complaints; write durable Audit + Timeline + Outbox; refresh in-app alert facts.
2. **Outbox drain** — publish `UNPUBLISHED` rows (including `EVT-004`) under the same scheduled-command pattern.
3. **Heartbeat** — make absence of successful runs detectable (C-1).

Does not send email/SMS/push (CAP-005 stub).

---

## Prerequisites

- Backend image with `scripts/` (same as OPS-CM-B1-STG-001)
- `flock` (`util-linux` in image and on host)
- Settings: `COMPLAINT_RESOLUTION_TARGET_DAYS` (default 30), `COMPLAINT_SLA_SWEEP_BATCH_LIMIT` (default 100)
- Marker directory writable: `/var/log/ecmp/`
- Lock directory: `/var/lock/`

---

## Commands

```bash
# Inside backend container working dir /app (or host equivalent)
flock -n /var/lock/ecmp-cm-sla-sweep.lock \
  python scripts/cm_batch1_ops_hygiene.py sweep-sla-thresholds

flock -n /var/lock/ecmp-cm-outbox-drain.lock \
  python scripts/cm_batch1_ops_hygiene.py drain-outbox
```

Exit codes (aligned with OPS-CM-B1-STG-001): `0` OK or lock-held skip; `2` operational failure.

On success only: update `/var/log/ecmp/cm-sla-sweep.last_ok` or `cm-outbox-drain.last_ok` with UTC ISO-8601.

The script also takes an **internal** non-blocking flock on the same paths, so a double schedule without host `flock` still skips safely (G3.7).

---

## Cadence

| Environment | Cadence | Rationale |
|---|---|---|
| Lab / SIT / shared | **Hourly** | C-3 detection lag = 1 hour |
| Production | Hourly only after REL-SEC + this runbook countersigned | Not authorized by Accept alone |

Example host crontab (install **after** commands exist and lab smoke passes):

```cron
5 * * * * flock -n /var/lock/ecmp-cm-sla-sweep.lock docker compose -f /opt/ECMP/docker-compose.prod.yml exec -T -w /app backend python scripts/cm_batch1_ops_hygiene.py sweep-sla-thresholds >> /var/log/ecmp/cm-sla-sweep.log 2>&1
10 * * * * flock -n /var/lock/ecmp-cm-outbox-drain.lock docker compose -f /opt/ECMP/docker-compose.prod.yml exec -T -w /app backend python scripts/cm_batch1_ops_hygiene.py drain-outbox >> /var/log/ecmp/cm-outbox-drain.log 2>&1
```

Exact compose project/name may differ per host; do not embed secrets in the crontab line.

---

## Heartbeat check (Operations Lead)

```bash
# Fail if marker missing or older than 2 hours
python - <<'PY'
from pathlib import Path
from datetime import datetime, timezone, timedelta
for name in ("cm-sla-sweep.last_ok", "cm-outbox-drain.last_ok"):
    p = Path("/var/log/ecmp") / name
    if not p.exists():
        raise SystemExit(f"MISSING {p}")
    age = datetime.now(timezone.utc) - datetime.fromisoformat(p.read_text().strip().replace("Z", "+00:00"))
    if age > timedelta(hours=2):
        raise SystemExit(f"STALE {p} age={age}")
print("ok")
PY
```

---

## Explicitly out of scope

| Item | Why |
|---|---|
| CAP-005 email/SMS/push | Stay Deferred; C-6 in-app only |
| New worker container | ADR-CAP006-002 Decision 2 |
| Repair of backup 20-byte dumps | C-5 — separate ops defect |

---

## Related

- Gate pack: `18 Architecture Governance/reviews/ECMP_ADR_CAP006_002_Implementation_Gate_Pack_v1.0.md`
- Sibling pattern: `ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md` (OPS-CM-B1-STG-001)
- ADR: `05 Architecture Decision Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md`
