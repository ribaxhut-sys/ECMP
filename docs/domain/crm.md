# Domain — CRM

| Field | Value |
|---|---|
| ID | EAR-PORTAL-DOM-CRM |
| Version | 0.2 |
| Owner | CRM PO |
| Reviewer | Architect |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The CRM domain provides a Customer 360 view built on the existing customer master plus ECMP's own interaction and case context.

- **Scope**: search/verify customer, profile view, interaction history, related cases, customer notes.
- **Out of scope**: owning or editing the customer master — ECMP is not the System of Record (ADR-002); customer data is a read-only reference.
- **Key flow**: Search → Verify → View 360 → Open/Link Case → Add Interaction Note.
- **Integrations**: Customer Master (read-only), ECMF, Dashboard, Notification.

Canonical AI context: `ai/domain/crm.md`  
Detailed architecture: `20 Domain Architecture/CRM/`
