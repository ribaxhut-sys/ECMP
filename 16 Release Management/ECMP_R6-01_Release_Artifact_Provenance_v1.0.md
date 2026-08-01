# R6-01 — Release Artifact Provenance

| Field | Value |
|---|---|
| ID | REL-R6-01 |
| Version | 1.0 |
| Owner | Release Engineering |
| Status | Active |
| Last Review | 2026-07-28 |

## Problem

Host unit tests can pass against a dirty working tree while running Docker
containers serve an older (or differently composed) artifact. Without build
provenance there is no way to prove:

Git commit → Docker image → Running container → Release Candidate

are the same code.

## Controls

1. **Clean-tree RC gate** — `scripts/release/build-rc.ps1` refuses dirty trees
   unless `-AllowDirty` (non-RC diagnostic only).
2. **Build-time provenance** — Dockerfiles accept `GIT_COMMIT`, `GIT_BRANCH`,
   `BUILD_TIME`, `GIT_TREE_STATE`, `APP_VERSION` as ARG→ENV + OCI labels.
3. **Runtime probe** — `GET /version` returns those values (never hardcoded SHA).
4. **Verification** — `scripts/release/verify-artifact.ps1` asserts
   `HEAD == /version.git_commit` and tree is clean.

## Required RC flow

```powershell
# working tree MUST be clean
git status
.\scripts\release\build-rc.ps1
.\scripts\release\verify-artifact.ps1
```

## Anti-patterns (do not)

- `docker compose up` without rebuild after source changes
- Relying on host pytest as proof of what the container runs
- Binding host source into backend/frontend containers for RC
- Shipping images with `GIT_COMMIT=unknown` or `GIT_TREE_STATE=dirty`

## Related

- `ECMP_RC_Release_Checklist_v0.1.md` §1 Source integrity
- `docker-compose.yml` build args
- `backend/Dockerfile` / `frontend/Dockerfile` LABEL/ENV
