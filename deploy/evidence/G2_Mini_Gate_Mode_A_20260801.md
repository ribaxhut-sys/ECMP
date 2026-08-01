# G2 Mini-Gate Exit — Mode A (2026-08-01)

| Field | Value |
|---|---|
| Verdict | **EXITED** (Mode A lab) |
| Authority | DEC-021 + ADR-009 Addendum G2 |
| Tip | `feature/cm-batch1-s2-persistence` |
| SoD | W-SOD-1 disclosed |

## Checklist

| Item | Result |
|---|---|
| G2-S1 broker | **Extend in-process** — no physical broker |
| G2-S2 CM / API-010 | **Deferred** (ACR-002 affirmed) |
| G2-S3 obs floor | **Accepted** for Mode A (JSON + X-Request-ID) |
| G2-S4 pack/runbook | **Adopted** — `REGRESSION_PACK_G2.md`, `DEV_RUNBOOK.md` |
| U-1 reopen | **Out of Mode A DoD** |
| Mode B | **CLOSED** (untouched) |

## Artefacts

- `27 Project Decisions/DEC-021_G2_Mini_Gate_Mode_A_v1.0.md`
- `05 Architecture Decision Records/ECMP_ADR_009_Addendum_G2_InProcess_Extension_v1.0.md`
- `deploy/evidence/Mode_A_SIT_SoT_Choice_20260801.md`
- `deploy/evidence/U5_Signoff_Checklist_20260801.md`
- `deploy/evidence/W-S03_Status_20260801.md`
- `deploy/evidence/Sprint03_Residual_Mode_A_DoD_20260801.md`

## Regression evidence (2026-08-01)

```
docker … pytest -q tests/  →  103 passed
```

Also aligned case-service probes to catalog: `/live`, `/ready`, `/version` (+ legacy `/health`); removed uncataloged `/health/ready`.
