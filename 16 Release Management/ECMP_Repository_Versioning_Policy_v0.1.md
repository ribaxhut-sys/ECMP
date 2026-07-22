# ECMP Repository Versioning Policy

| Field | Value |
|---|---|
| ID | REL-VER-001 |
| Version | 0.1 |
| Owner | Release Manager |
| Reviewer | Tech Lead / Engineering Manager |
| Approver | PMO |
| Status | 🟢 Approved (Sprint-10 RC1) |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-22 |

## 1. Purpose

Define SemVer for the **ECMP repository / application release line**, distinct from
API contract SemVer (ADR-006 / OpenAPI `info.version`).

## 2. Version identity

| Artifact | Scheme | Source of truth |
|---|---|---|
| Repository / app release | SemVer `MAJOR.MINOR.PATCH` (+ optional pre-release) | Git annotated tag + `CHANGELOG.md` |
| Frontend package | Align `implementation/frontend/package.json` `version` on release tags | Same SemVer as tag (without leading `v`) |
| Backend Python package | No separate PyPI package today; track via repo tag | Git tag |
| API contract | SemVer in OpenAPI `info.version` + path prefix `/vN` | `07 API Catalog/openapi/*.yaml` (ADR-006) |

## 3. SemVer rules (app/repo)

- **MAJOR** — incompatible operational or product breaking change for consumers of the
  deployed slice (e.g. removing a supported workflow, incompatible data migration
  requiring coordinated cutover).
- **MINOR** — backward-compatible feature or capability addition (new screens,
  additive APIs already versioned under `/v1`, new ops procedures).
- **PATCH** — backward-compatible fixes, docs, CI/quality gates, runbook clarifications.

Pre-release labels (see tag convention):

- `rc.N` — Release Candidate for internal / DEV validation (Sprint-10+).
- `alpha.N` / `beta.N` — optional earlier preview lines (not used for RC1).

## 4. Relationship to API versioning

- Bumping the **repo** version does **not** require bumping OpenAPI `info.version`.
- Bumping OpenAPI **MAJOR** (new `/v2`) **does** require a repo MINOR or MAJOR bump
  and an explicit CHANGELOG entry under "Changed" / "Removed".
- Contract-only clarifications (OpenAPI PATCH) may ship under a repo PATCH.

## 5. When to bump

| Event | Typical bump |
|---|---|
| Internal RC for DEV/CI validation | Pre-release (`X.Y.Z-rc.N`) |
| Gate/slice close without shared-env deploy | MINOR or PATCH as appropriate |
| First shared-environment release (future) | Drop `-rc` → `X.Y.Z` after Go criteria |
| Hotfix on a released line | PATCH |

## 6. Process

1. Update `CHANGELOG.md` under `[Unreleased]` as work merges.
2. On RC/release cut: move Unreleased notes into a dated section; set tag per
   `ECMP_Git_Tag_Convention_v0.1.md`.
3. Complete `ECMP_RC_Release_Checklist_v0.1.md` before publishing the tag.
4. Do **not** retag an existing SemVer; fix-forward with a new PATCH or new `rc.N`.

## Related

- `ECMP_Git_Tag_Convention_v0.1.md`
- `ECMP_RC_Release_Checklist_v0.1.md`
- `ECMP_Release_Management_v0.1.md` (REL-001)
- `../05 Architecture Decision Records/ECMP_ADR_006_API_Versioning_v1.0.md`
- `../CHANGELOG.md`
