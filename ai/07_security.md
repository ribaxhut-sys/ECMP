# 07 — Security Context

| Field | Value |
|---|---|
| ID | AI-CTX-007 |
| Version | 1.0 |
| Owner | Security Architect |
| Reviewer | Compliance |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## Rules
1. Authenticate every access.
2. Authorize by role + organization scope.
3. Apply need-to-know for customer data.
4. Audit trail cannot be deleted.
5. No secrets in repo/docs/prompts.
6. Security-relevant changes may require Security review.

## References
- `10 Security and Access Standards/ECMP_Security_Standards_v0.1.md`
- Role matrix: `10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md` (baselined 2026-07-21)
- Batasan slice: `10 Security and Access Standards/ECMP_AuthN_Limitations_Register_v0.1.md`
- AuthN model: ADR-007 · RBAC SoT: ADR-008
