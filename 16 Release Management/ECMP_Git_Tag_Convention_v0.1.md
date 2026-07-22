# ECMP Git Tag Convention

| Field | Value |
|---|---|
| ID | REL-TAG-001 |
| Version | 0.1 |
| Owner | Release Manager |
| Reviewer | Tech Lead / Engineering Manager |
| Approver | PMO |
| Status | 🟢 Approved (Sprint-10 RC1) |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-22 |

## 1. Tag format

```text
v<MAJOR>.<MINOR>.<PATCH>[-<pre-release>]
```

Examples:

| Tag | Meaning |
|---|---|
| `v0.8.0-rc.1` | First RC for the 0.8 line (internal / DEV validation) |
| `v0.8.0-rc.2` | Second RC after fixes |
| `v0.8.0` | Final 0.8 release (when shared-env Go criteria met — future) |
| `v1.0.0` | First production-oriented major (future) |

Rules:

- Always prefix with `v`.
- Pre-release segment uses dot-separated identifiers (`rc.1`, not `rc1`).
- No floating tags (`latest`, `stable`) — consumers pin exact SemVer tags.
- Lightweight tags are **not** used for releases; releases are **annotated**.

## 2. Creating an annotated release tag

```bash
# Working tree clean; CHANGELOG section exists; checklist complete
git checkout main
git pull --ff-only
git tag -a v0.8.0-rc.1 -m "ECMP v0.8.0-rc.1 — RC1 internal DEV validation"
git push origin v0.8.0-rc.1
```

Optional GitHub release:

```bash
gh release create v0.8.0-rc.1 --title "v0.8.0-rc.1" --notes-file CHANGELOG.md
```

## 3. What may be tagged

- Only commits on the default branch (`main` / `master`) that have:
  - Green required CI for paths touched by the release,
  - Updated `CHANGELOG.md` section for that version,
  - Completed RC checklist (for `-rc.N`) or full Go/No-Go (for final releases).

## 4. What must not be tagged

- Dirty / uncommitted trees.
- Feature-branch tips (cherry-pick or merge to main first).
- Re-use of an existing tag name (never move a published tag).

## 5. Rollback communication

Tag remains immutable. Operational rollback follows
`../14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` DEP-001 §4.
Communicate the prior known-good tag in the incident/rollback note.

## Related

- `ECMP_Repository_Versioning_Policy_v0.1.md`
- `ECMP_RC_Release_Checklist_v0.1.md`
- `../22 Engineering Handbook/GIT_CONVENTION.md` (ENG-001)
- `../CHANGELOG.md`
