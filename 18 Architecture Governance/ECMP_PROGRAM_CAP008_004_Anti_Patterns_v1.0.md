# CAP-008 Anti-Patterns

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-004 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 Recorded |
| Authority | Architecture Review Board |

## Anti-patterns observed or explicitly forbidden

| ID | Anti-pattern | Why forbidden / observed |
|---|---|---|
| AP-01 | Implement Aggregate Case while FRD still Draft and catalog says “not implemented” without SoT Closure | Creates dual truth; fixed by GOV-SOT-CAP008-001 |
| AP-02 | Map Sprint `API-001…` / `EVT-001…` onto Aggregate CAP-008 | DEC-BQ001 O3 / DEC-020 collision |
| AP-03 | Invent production `OIDC_*` to pass REL-SEC-001 | Forbidden; Mode_B_Blocked evidence |
| AP-04 | Treat Mode B CLOSED as incomplete CAP-008 | Board C-7 — Follow-up NONE |
| AP-05 | Auto-close Complaint Aggregate on Case close | BQ-007 locked opposite |
| AP-06 | Expose PENDING/ESCALATED on Mode A delivery path | BQ-009 |
| AP-07 | Assignment-to-User in Mode A CAP-008 | BQ-006 Unit only |
| AP-08 | Reopen program by editing LOCKED FRD without new CR/Board | Violates SoT lock |
| AP-09 | Claim Production Ready from lab RC alone | REL-SEC-001 NO-GO |
| AP-10 | Expand into Enterprise Platform / SDK / multi-module framework during CAP delivery | Constitution North Star |
| AP-11 | Leave Capability Register “Planned” after RC PASS | Audit understates completion |
| AP-12 | Invent EVT / TC catalog IDs when SoT says NOT SPECIFIED | FRD Appendix E discipline |

---

*End of GOV-CAP008-CLOSE-004.*
