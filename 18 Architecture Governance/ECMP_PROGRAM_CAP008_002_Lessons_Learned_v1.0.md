# CAP-008 Lessons Learned

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-002 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 Recorded |
| Authority | Architecture Review Board |

## Lessons (evidence-based)

1. **Lock business questions before FRD.** Residual BQ ZERO (DEC-MODEA-B2-001) prevented FR churn during implementation.
2. **Dual SoT must be named early.** DEC-020 / DEC-BQ001 O3 avoided silent overwrite of Sprint `API-001…` vs Aggregate `API-530…`.
3. **RC without catalog sync creates false “not implemented”.** Lab RC PASS while OpenAPI README still said “contract only” — fixed only by SoT Closure, not by more features.
4. **Document-local FR-001…006 collide with Sprint IDs.** Trace IDs `FR-CM-B2-001…006` were required in `traceability.yaml`.
5. **Annotated tag tip ≠ source freeze commit.** Tag `v1.2.0-rc.1` → `6890f50`; freeze ancestor `b7d8e2c`. Provenance docs must cite the tag tip.
6. **External AuthN cannot be “fixed” in-module.** Inventing OIDC is forbidden; Production NO-GO is correct when IdP contract is absent.
7. **Mode B CLOSED is a feature, not a defect.** C-7 / C-B6-1 kept scope on Complaint Module completion.
8. **Capability Register can lag delivery.** Status fields must be updated in the same closure as RC, or audits will understate completion.
9. **NOT SPECIFIED must stay NOT SPECIFIED.** EVT Aggregate IDs and formal TC-catalog IDs were left unset rather than invented.
10. **Constitution North Star filters gold-plating.** Portal/vector-DB/enterprise OS work is not CAP-008 exit criteria.

---

*End of GOV-CAP008-CLOSE-002.*
