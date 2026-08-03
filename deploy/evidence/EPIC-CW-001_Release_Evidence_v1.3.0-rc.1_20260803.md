# Release Evidence — EPIC-CW-001 / v1.3.0-rc.1

| Field | Value |
|---|---|
| ID | REL-EVID-EPIC-CW-001-v1.3.0-rc.1 |
| Date | 2026-08-03 |
| Epic | EPIC-CW-001 (Version 1.0) |
| Repo tag target | `v1.3.0-rc.1` |
| Release Manager | ECMP Release Manager |
| Architecture | CLOSED |
| Complaint Module | CLOSED |
| Security Review | CLOSED |
| Domain Review | CLOSED |
| Official Sign-Off | COMPLETED |
| Known Risk | ACCEPTED |

## Scope of this evidence pack

Repository release execution only: merge path, artifacts, annotated tag, GitHub Release.

## Delivery commits (pre-rebase reference)

| Role | SHA (pre-rebase) | Subject |
|---|---|---|
| PR-1 Foundation | `670183b6778d67c843119f966fb9dd3e718c2aa6` | feat(cwx): land CWX Foundation (CWX-000 / M1 / M2) for PR-1 |
| PR-2 Working Surface | `9d534fa430a95ac8b8ac23bfbfe164d2237b09ea` | feat(cwx): land CWX-M3 Working Surface for PR-2 |

Post-rebase SHAs are recorded at merge / tag time below.

## Artifacts

| Artifact | Path |
|---|---|
| CHANGELOG | `CHANGELOG.md` → `[1.3.0-rc.1]` |
| Release Notes | `docs/releases/v1.3.0-rc.1-EPIC-CW-001.md` |
| This evidence | `deploy/evidence/EPIC-CW-001_Release_Evidence_v1.3.0-rc.1_20260803.md` |

## Merge strategy

1. PR-1: `release/cwx-foundation` → `main` (squash or merge commit per repo default; preserve intent Foundation)
2. PR-2: `release/cwx-working-surface` → `main` (after PR-1 merged; includes M3 + release artifacts)
3. Annotated tag `v1.3.0-rc.1` on `main` tip
4. GitHub Release for `v1.3.0-rc.1`

## CI / gate record

| Gate | Result | Notes |
|---|---|---|
| PR-1 CI | _pending — fill on green_ | |
| PR-2 CI | _pending — fill on green_ | |
| Tag SHA | _pending_ | |

## Sign-off record

| Role | Status | Date |
|---|---|---|
| Official Sign-Off | COMPLETED | 2026-08-03 |
| Release Manager (execution) | EXECUTE | 2026-08-03 |
