# ECMP RC Release Checklist

| Field | Value |
|---|---|
| ID | REL-RC-001 |
| Version | 0.1 |
| Owner | Release Manager |
| Reviewer | QA Lead / Tech Lead |
| Approver | PMO / Engineering Manager |
| Status | 🟢 Approved (Sprint-10 RC1) |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-22 |

Checklist for cutting an **internal / DEV validation** Release Candidate (`vX.Y.Z-rc.N`).
This does **not** authorize shared SIT/UAT/PROD deployment (blocked until ADR-012
Phase 3 per ADR-010 / DEP-CHK-001).

## 0. Scope declaration

- [ ] RC purpose stated (e.g. "RC1 — internal DEV/CI validation")
- [ ] Explicitly **out of scope** for this RC: shared-environment deploy, JWT/OIDC
      go-live, production cutover, new business features beyond the tagged commit

## 1. Source integrity

- [ ] Default branch tip selected; working tree clean on the cut machine
- [ ] Commit SHA recorded in CHANGELOG / release notes
- [ ] No secrets in tree (`.env` untracked; audit spot-check)
- [ ] R6-01: `.\scripts\release\build-rc.ps1` succeeds without `-AllowDirty`
- [ ] R6-01: `.\scripts\release\verify-artifact.ps1` RESULT=PASS
- [ ] R6-01: `GET /version` returns matching `git_commit` and `git_tree_state=clean`

## 2. Quality gates (CI)

- [ ] Backend CI green on candidate SHA: ruff, OpenAPI validate, Alembic upgrade,
      pytest vs PostgreSQL with **coverage ≥ 90%**
- [ ] Frontend CI green: typecheck, lint, **Vitest coverage thresholds**, production build
- [ ] Response-body contract tests green (`test_response_body_contract.py`)
- [ ] Bundle-size budget step reviewed (warning mode OK for RC1; note overruns)
- [ ] Accessibility warning step reviewed (axe smoke; note violations)

## 3. Test Strategy RC exit criteria

Confirm against `../13 Test Strategy/ECMP_Test_Strategy_v0.1.md` § RC Exit Criteria:

- [ ] Backend coverage floor met
- [ ] Frontend coverage floor met
- [ ] Contract tests (schema conformance + response-body) met
- [ ] Integration/E2E expectations for this RC acknowledged (see Test Strategy —
      full browser E2E still backlog; API integration via pytest TestClient required)

## 4. Documentation

- [ ] `CHANGELOG.md` section for this `vX.Y.Z-rc.N` populated
- [ ] Versioning policy followed (`ECMP_Repository_Versioning_Policy_v0.1.md`)
- [ ] Tag name matches convention (`ECMP_Git_Tag_Convention_v0.1.md`)
- [ ] Ops runbooks still accurate for DEV validation scenarios (shutdown, logs, restore)

## 5. Sign-off (RC1 / internal)

| Role | Name | Date | Go / No-Go |
|---|---|---|---|
| Tech Lead | | | |
| QA Lead | | | |
| Release Manager | | | |

No-Go → fix-forward; cut a new `rc.N+1`. Do not move tags.

## 6. Tag & communicate

- [ ] Annotated tag created and pushed
- [ ] Stakeholders notified: RC scope = internal DEV only; shared UAT still gated

## Related

- `ECMP_Repository_Versioning_Policy_v0.1.md`
- `ECMP_Git_Tag_Convention_v0.1.md`
- `ECMP_Release_Management_v0.1.md` (REL-001)
- `../13 Test Strategy/ECMP_Test_Strategy_v0.1.md`
- `../CHANGELOG.md`
