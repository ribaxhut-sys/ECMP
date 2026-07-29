# ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.0

| Field | Value |
|---|---|
| ID | ADR-014 |
| Version | 1.1 |
| Owner | CTO |
| Reviewer | Architecture Board |
| Approver | Architecture Board |
| Status | 🟡 Proposed |
| Last Review | 2026-07-29 |
| Next Review | 2027-01-29 |

- ADR Status: Proposed
- Date: 2026-07-29
- Decision Owners: CTO
- Related Domains: Core Platform, ECMF (Complaint Management), Notification, Dashboard & Analytics, KPI & Performance

## Context

ECMP was originally designed as a standalone application with its own authentication, user management, authorization, and complaint management.

The enterprise roadmap has changed.

ECMP will become one business module within a larger Enterprise Application Platform.

The Enterprise Platform will provide shared capabilities for multiple business modules including:

- Portal
- Authentication
- Single Sign-On (SSO)
- User Directory
- Organization Structure
- Navigation
- Global Notification
- Session Management

ECMP will focus exclusively on Complaint Management.

## Problem Statement

If ECMP continues to own enterprise authentication, several issues arise:

- Multiple login pages
- Duplicate user databases
- Duplicate password management
- Separate password reset processes
- Inconsistent logout behavior
- Fragmented identity auditing
- Difficult enterprise integration

These issues increase operational complexity as additional enterprise modules are introduced.

## Decision

Authentication ownership shall be transferred to the Enterprise Platform.

ECMP shall no longer act as an Identity Provider.

ECMP shall operate as an Enterprise Business Module.

Authentication and Authorization shall become separate responsibilities.

### Decision Summary

- Enterprise Platform is the owner of Enterprise Identity.
- ECMP is the owner of Complaint Management.
- Authentication is external.
- Authorization remains internal.

This boundary shall guide future architectural decisions.

### Enterprise Mode Local Auth Prohibition

When Enterprise Mode is enabled:

- Local Login is disabled
- Forgot Password is disabled
- Reset Password is disabled
- Change Password is disabled
- Local Password Storage is prohibited

## Architecture Boundary

### Enterprise Platform

The Enterprise Platform owns:

- Authentication
- Single Sign-On
- User Directory
- Password Management
- Multi-Factor Authentication
- Session Management
- Organization
- Branch
- Department
- Enterprise Navigation
- Identity Audit

### ECMP

ECMP owns:

- Complaint Management
- Assignment
- Escalation
- Resolution
- SLA
- Timeline
- Complaint KPI
- Complaint Authorization
- Complaint Roles
- Complaint Preferences

## Authentication Ownership

Authentication is performed only by the Enterprise Platform.

User flow:

```
User
  ↓
Enterprise Login
  ↓
Enterprise SSO
  ↓
Access Token
  ↓
ECMP
  ↓
Token Validation
  ↓
Enterprise Entitlement Gate
  ↓
Complaint Module
```

ECMP never requests enterprise credentials.

Enterprise authentication alone must never grant ECMP access.

## Authorization Ownership

Authorization remains inside ECMP.

Identity received from Enterprise Platform shall be mapped into ECMP-specific roles only after the Enterprise Entitlement Gate has been satisfied.

Example flow:

```
Enterprise Identity
  ↓
external_user_id
  ↓
Enterprise Entitlement Gate
  ↓
ECMP Role
  ↓
Permission
  ↓
Complaint Business Rules
```

Enterprise roles shall not automatically become ECMP roles.

Role mapping remains under ECMP ownership.

### Enterprise Entitlement Gate

Access to ECMP requires an explicit enterprise entitlement for the Complaint module.

Enterprise authentication alone must never grant ECMP access.

Absence of entitlement shall result in denial of access. No default ECMP role shall be assigned solely because authentication succeeded.

## Enterprise Identity

The Enterprise Platform is the Source of Truth for identity.

### external_user_id

`external_user_id` is the only enterprise identity key used by ECMP.

It shall be:

- immutable
- opaque
- unique
- enterprise-owned
- non-reassignable

Email must never be used as an identity key.

### Minimum Identity Payload

Minimum identity payload required by ECMP:

- `external_user_id`
- `display_name`
- `email`
- `organization_id`
- `branch_id`
- `department_id`
- `employment_status`

Additional claims may be introduced without changing ECMP business logic.

## User Model

ECMP stores only module-specific information.

Example attributes:

- `external_user_id`
- notification preferences
- dashboard preferences
- favorite views
- last access
- local status

Passwords shall never be stored when Enterprise Mode is enabled.

### User Provisioning

Enterprise Mode uses Just-In-Time Provisioning.

Provisioning is subject to the Enterprise Entitlement Gate. Enterprise authentication alone must never create ECMP access.

Lifecycle:

```
Identity received
  ↓
Lookup external_user_id
  ↓
Enterprise Entitlement Gate
  ↓
Create | Update | Deactivate | Reactivate
  ↓
Continue or Deny
```

Lifecycle operations:

- **Create** — create a local ECMP profile when an entitled identity is first seen
- **Update** — update local profile attributes from enterprise identity
- **Deactivate** — deactivate the local ECMP profile when entitlement or employment status requires it
- **Reactivate** — reactivate a previously deactivated local profile when entitlement is restored
- **Periodic Reconciliation** — reconcile local profiles against enterprise identity on a periodic basis

Future synchronization strategies may refine these lifecycle operations without changing this decision.

## Organization Ownership

Enterprise Platform owns:

- Organization
- Branch
- Department

ECMP stores references only.

ECMP shall not become the master source for organizational hierarchy.

## Architecture Dependency

### Organization Synchronization

Organization Synchronization is an Architecture Dependency of this ADR.

ECMP authorization depends on organization hierarchy (organization, branch, department). ECMP stores references only; therefore organization structure must be available from the Enterprise Platform for authorization to function correctly under Enterprise Mode.

Protocol, frequency, and transport for Organization Synchronization remain outside the scope of this ADR and require a future decision. The dependency itself is recorded here and is not an open question as to whether synchronization is required.

## Deployment Modes

### Mode A — Standalone

- Authentication: Local
- Recommended for customers deploying ECMP independently.

### Mode B — Enterprise

- Authentication: Enterprise SSO
- Recommended for enterprise platform deployments.

When Enterprise Mode is enabled:

- Local Login is disabled
- Forgot Password is disabled
- Reset Password is disabled
- Change Password is disabled
- Local Password Storage is prohibited

Complaint domain behavior shall remain identical across both modes.

## Architecture Principles

- Authentication and Authorization are separate concerns.
- Enterprise Platform owns Authentication.
- ECMP owns Authorization.
- Enterprise Platform owns Enterprise Identity.
- ECMP owns Complaint Business Rules.
- Business modules shall consume Enterprise Identity rather than implement Enterprise Authentication.
- Enterprise authentication alone must never grant ECMP access.

## Alternatives Considered

### Alternative 1 — ECMP continues to own authentication

Rejected.

Reason: Creates duplicate identity management.

### Alternative 2 — Enterprise Platform owns authentication

Accepted.

Reason: Provides clear responsibility separation and aligns with enterprise architecture.

## Risks

Dependency and integration risks introduced by this decision include:

- Dependency on Enterprise Identity availability
- Need for token validation infrastructure
- Role mapping layer required
- Additional integration testing
- Dependency on Organization Synchronization for authorization correctness
- Dependency on Enterprise Entitlement availability for access control

## Open Questions

The following topics remain outside the scope of this ADR and require future decisions:

- Identity protocol (OIDC, OAuth2, SAML, internal token)
- Token lifecycle
- Refresh token strategy
- Single Logout
- Enterprise role synchronization
- Identity caching
- High availability for Identity Provider
- Enterprise Entitlement representation and issuance

## ADR Relationship

| ADR | Relationship |
|---|---|
| ADR-007 | Relationship Pending |
| ADR-008 | Relationship Pending |
| ADR-012 | Relationship Pending |

No supersession is declared by this ADR.

## Consequences

### Positive

- Single Login Experience
- Centralized Identity Management
- Enterprise-ready architecture
- Reduced operational complexity
- Easier future module integration
- Cleaner security boundary
- Explicit entitlement prevents unintended access from enterprise authentication alone

### Negative / Trade-offs

- Dependency on Enterprise Identity availability
- Need for token validation infrastructure
- Role mapping layer required
- Additional integration testing
- Dependency on Organization Synchronization
- Dependency on Enterprise Entitlement Gate

### Follow-up Actions

- [ ] Architecture Board review → move Status to Accepted
- [ ] Resolve ADR Relationship for ADR-007, ADR-008, and ADR-012 (Relationship Pending)
- [ ] Define Organization Synchronization approach as a follow-on decision
- [ ] Update Solution Architecture when Enterprise Mode contracts are defined
- [ ] Communicate to impacted teams — Core Platform, ECMF, Security, Integration
