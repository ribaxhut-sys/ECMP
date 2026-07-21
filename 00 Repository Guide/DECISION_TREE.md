# Repository Decision Tree

| Field | Value |
|---|---|
| ID | EAR-IDX-003 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Membantu anggota tim baru menentukan folder yang tepat.

## Tree

```text
Apa yang Anda butuhkan?
│
├─ Istilah bisnis/teknis?
│  └─ 25 Glossary
│
├─ Kebutuhan bisnis / scope?
│  ├─ Konteks & domain → 01 Business Blueprint
│  ├─ Aturan proses/SLA logic → 02 Business Rules
│  └─ Spesifikasi fungsi → 03 Functional Requirements
│
├─ Arsitektur?
│  ├─ Desain end-to-end → 04 Solution Architecture
│  ├─ Pola standar bersama → 19 Reference Architecture
│  ├─ Detail per domain → 20 Domain Architecture
│  └─ Keputusan arsitektur → 05 ADR
│
├─ Kontrak teknis?
│  ├─ API → 07 API Catalog
│  ├─ Event → 08 Event Catalog
│  ├─ Integrasi sistem → 09 Integration Catalog
│  └─ Data/atribut → 06 Data Dictionary
│
├─ Standar teknis & cara kerja?
│  ├─ Stack standard (Python/React/Docker/...) → 21 Technical Standards
│  ├─ Git/PR/review harian → 22 Engineering Handbook
│  └─ Template dokumen → 24 Templates
│
├─ Keamanan / kepatuhan / tatakelola?
│  ├─ Security & access → 10
│  ├─ Compliance → 17
│  ├─ Governance & architecture review → 18
│  └─ Decision non-ADR / open question → 27
│
├─ Operasional & delivery?
│  ├─ SLA/KPI → 11
│  ├─ UI/UX → 12
│  ├─ Test strategy → 13
│  ├─ Deployment → 14
│  ├─ Runbook → 15
│  └─ Release → 16
│
├─ Diagram source / logo / icon?
│  └─ 23 Assets
│
└─ Mapping requirement → test?
   └─ 26 Traceability
```

## One-liner Shortcuts
- Need API? → `07`
- Need Business? → `01/02/03`
- Need Architecture? → `04/19/20/05`
- Need Deployment? → `14`
- Need Ops? → `15`
