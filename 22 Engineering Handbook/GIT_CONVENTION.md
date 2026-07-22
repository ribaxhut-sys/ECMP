# Git Convention (Starter)


| Field | Value |
|---|---|
| ID | ENG-001 |
| Version | 0.2 |
| Owner | Engineering Manager |
| Reviewer | Tech Lead |
| Approver | Engineering Manager |
| Status | 🟢 Approved |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-22 |

## Branch Naming
- `feature/<id>-short-name`
- `fix/<id>-short-name`
- `chore/<short-name>`
- `docs/<short-name>`

## Commit Message
```text
<type>(<scope>): <summary>

<body optional>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

Example: `feat(ecmf): add case assignment transition guard`

## Release tags

Annotated SemVer tags for the repository/application release line:

- Format: `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-rc.N`
- Normative docs: `../16 Release Management/ECMP_Git_Tag_Convention_v0.1.md`
  and `ECMP_Repository_Versioning_Policy_v0.1.md`
- Always update root `CHANGELOG.md` before tagging
