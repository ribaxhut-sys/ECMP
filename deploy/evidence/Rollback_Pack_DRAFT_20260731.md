# Rollback Pack — DRAFT (R-01…R-06 / R6)

| Field | Value |
|---|---|
| Date | 2026-07-31 |
| Status | **DRAFT — awaiting Deploy Lead + Release Manager approval** |
| Constraint | No rewrite of VPS `main` history as rollback method |

## R-01 — Edge lab rollback (from `96f52eb` evidence)

- Stop/disable lab Caddy edge and/or compose overlay used for `pengaduan.layanankami.tech` per `deploy/README.md` lab runbook.
- Does **not** by itself roll back application cherry-picks on a release branch.

## R-02 — Release branch rollback

If cherry-picks are in progress or completed on `release/cm-batch1-vps-sync` (or agreed name):

1. **Abort mid-sequence:** stop further picks; leave branch tip at last known-good pick SHA; record abort in evidence.
2. **Revert completed picks:** revert in **reverse** pick order (newest pick first); or close PR without merge; or reset branch tip to locked base SHA **only on the release branch** (not on VPS `main`, not force-push to protected SoT).
3. **Do not** merge VPS `main` to “undo.”

## R-03 — Abort criteria (cherry-pick window)

Abort if any of:

- Unresolvable conflict on EXISTS paths without Tech Lead decision
- Security or Deploy sign-off withdrawn
- Seed/data risk on live lab DB without backup (R-04)
- Scope creep beyond approved split units

## R-04 — DB backup before seed

If `deploy/seed-lab-master-data.sql` is in the pick set: take Postgres backup **before** apply; retain path/timestamp in evidence.

## R-05 — On-call owner

| Window | Owner | Contact |
|---|---|---|
| Preparation cut (future Phase 5) | _pending Release Manager_ | |

## R-06 — Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Deploy Lead | _pending_ | | Approve / Reject |
| Release Manager | _pending_ | | Approve / Reject |
