# 00 — Project Context

| Field | Value |
|---|---|
| ID | AI-CTX-000 |
| Version | 1.1 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## Product
**ECMP** — Enterprise Complaint Management Platform (official expansion per Blueprint v2.1 / DEC-001; ECMP is not a Customer Master SoR).

## Platform Positioning
This repository is the **Enterprise Knowledge Repository (EKR)** / EAR for ECMP, plus an **AI Development Platform** context pack.

Future split:
- **EKR** = business, architecture, standards, governance, AI context, templates
- **ECMP Implementation** = backend, frontend, infra, tests, deployment (`implementation/`)

## Mission
Orchestrate customer service processes using centralized customer master data — not rebuild master data.

## Primary Domains
Core Platform, CRM, ECMF, KPI, Dashboard, Notification, Administration.

## Tooling Roles
| Tool | Role |
|---|---|
| ChatGPT | Chief Enterprise Architect |
| Claude (Cursor) | Senior Software Engineer |
| Cursor | Development workspace |

## Source of Truth
- Detailed docs: folders `00`–`27`
- AI compact context: `ai/`
- Portal entry: MkDocs (`docs/` + `mkdocs.yml`)
