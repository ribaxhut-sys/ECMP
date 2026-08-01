# DEC ID Collision Register — 2026-08-01

| Field | Value |
|---|---|
| Status | **CLOSED — Board Option A** (`EXT-HD-RC-MA-B1-20260801`) |
| Severity | P0 governance (documentation integrity) |
| Action taken | Documented only — **no renumber, no content rewrite of DEC bodies** |

## Collisions found (repository SoT)

### DEC-020 (two Accepted files)

| File | Topic | Status in file |
|---|---|---|
| `27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md` | Dual SoT / namespace remapping | Approved / Accepted |
| `27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md` | Lab auth local JWT → SSO later | Accepted (ops) |

Canonical index historically listed only the SoT remapping DEC-020 (`27 Project Decisions/README.md`).

### DEC-021 (Proposed vs Accepted, different topics)

| File | Topic | Status in file |
|---|---|---|
| `27 Project Decisions/DEC-021_Organization_Hierarchy_Descendant_Scope_O06_v0.1.md` | O-06 descendant AuthZ | Proposed |
| `27 Project Decisions/DEC-021_G2_Mini_Gate_Mode_A_v1.0.md` | G2 mini-gate Mode A | Accepted (Mode A lab) |

G2 artefacts (`G2_Mini_Gate_Mode_A_20260801.md`, ADR-009 Addendum G2, regression pack) cite **DEC-021** for G2. Org-gap / OPEN_QUESTIONS cite **DEC-021** for O-06.

## Recommended Board options (pick one — do not invent)

| Option | Meaning |
|---|---|
| A | Keep O-06 as DEC-021; renumber G2 Mini-Gate → next free ID (e.g. DEC-023) + update citations |
| B | Keep G2 as DEC-021; renumber O-06 → next free ID + update OQ/ADR-018 citations |
| C | Keep both files; introduce explicit suffixes (`DEC-020-A` / `DEC-020-B`) via new numbering policy |

Until Board chooses: treat **file path + title** as disambiguator; do not claim a single DEC-021 meaning.

## Explicit non-actions

- No Mode B unlock  
- No change to ADR Approved bodies  
- No forged Accept of O-06  


## Board decision recorded

| Field | Value |
|---|---|
| Decision | B-1 |
| Option | **A** — Keep O-06 as DEC-021; renumber G2 Mini-Gate → next free ID (e.g. DEC-023) + update citations |
| Record | `EXT-HD-RC-MA-B1-20260801` |
| Date | 2026-08-01 |
| Execution of renumber | Separate (BA-03); not required to record this decision |

