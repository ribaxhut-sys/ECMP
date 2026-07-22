# Changelog

All notable changes to the ECMP application/repository release line are documented here.
API contract versioning remains governed by ADR-006 and OpenAPI `info.version`
(see `16 Release Management/ECMP_Release_Management_v0.1.md` §1).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Repository versioning follows [SemVer](https://semver.org/) as defined in
`16 Release Management/ECMP_Repository_Versioning_Policy_v0.1.md`.

## [Unreleased]

### Added

- Sprint-10 RC1 (internal / DEV validation): frontend Vitest coverage gate in CI;
  response-body OpenAPI contract tests; RC exit criteria in Test Strategy;
  repository versioning policy + git tag convention; RC release checklist;
  bundle-size budget and axe-core a11y checks in frontend CI (warning mode).

## [0.8.0-rc.1] - 2026-07-22

### Added

- First Release Candidate tag line for internal / DEV validation (RC1).
- Scope inherits Sprint-09 closed baseline (UAT plan v0.2, operational readiness
  runbooks) plus Sprint-10 quality/release gates above.

### Notes

- Shared SIT/UAT/PROD deployment remains **out of scope** until JWT/OIDC
  (ADR-012 Phase 3) is accepted and active (ADR-010 / DEP-CHK-001).
- This RC is for internal DEV/CI validation only.

[Unreleased]: https://github.com/nandeshut/ECMP/compare/v0.8.0-rc.1...HEAD
[0.8.0-rc.1]: https://github.com/nandeshut/ECMP/releases/tag/v0.8.0-rc.1
