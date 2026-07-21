# Domain Architecture — Administration

| Field | Value |
|---|---|
| ID | DOM-ADM-001 |
| Version | 1.0 |
| Owner | Administrator / Product Owner |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Configuration-first control: pengelolaan reference data, SLA Config, Workflow Config, dan proses perubahan role-permission — dengan approval, versioning, dan audit penuh.

## Bounded Context
- **Konteks:** Business Configuration. Administration mengelola *aturan* yang domain lain tegakkan.
- **SoT Workflow Config = Administration (ADR-008):** definisi status & transisi Case per kategori adalah konfigurasi bisnis (BR-001/BR-ECMF-03), diversion sesuai BR-ADM-03, dipublikasikan via EVT-006 ConfigChanged. **ECMF adalah enforcer** — memuat config aktif dan menolak transisi invalid.
- **Role-Permission: Administration hanya konfigurator (ADR-008):** SoT = Core Platform. Administration menyediakan UI/proses perubahan + approval, menulis melalui API Core Platform; tidak menyimpan salinan otoritatif (config view, non-SoT).
- **Ubiquitous language:** Reference Data, SLA Config, Workflow Config, Config Version, Effective Date, Approval.

## In Scope
- Reference Data (kategori, prioritas, dll.)
- SLA Config (parameter SLA + kalender kerja — sumber BR-ECMF-05)
- Workflow Config (definisi transisi status yang diizinkan — sumber BR-ECMF-03; SoT per ADR-008)
- Proses perubahan role-permission sebagai konfigurator Core Platform
- Approval perubahan konfigurasi kritikal (BR-ADM-01); baseline DEC-004: workflow config, SLA config, role-permission
- Versioning / effective dating tiap konfigurasi (BR-ADM-03)

## Out of Scope
- Menyimpan Role/Permission otoritatif (SoT = Core Platform, ADR-008)
- Enforcement transisi status (ECMF), perhitungan SLA (ECMF/KPI)

## Key Components
| Komponen | Tanggung jawab |
|---|---|
| Config Registry | Reference Data, SLA Config, Workflow Config + Config Version (BR-ADM-03) |
| Approval Workflow | Perubahan kritikal wajib approval sebelum diterapkan (BR-ADM-01) |
| Config Publisher | Emit EVT-006 ConfigChanged saat konfigurasi efektif berubah (BR-ADM-02) |
| RBAC Configurator | Proses perubahan role-permission via API Core Platform (ADR-008) |

## Key Flows
1. **Config change:** usulan perubahan → klasifikasi kritikal? → approval (BR-ADM-01) → simpan versi baru + effective date (BR-ADM-03) → audit lengkap (siapa, apa, kapan, nilai lama/baru — BR-ADM-02) → emit EVT-006.
2. **Workflow config publish:** perubahan matriks transisi → EVT-006 → ECMF reload config aktif → transisi baru berlaku tanpa deploy.
3. **RBAC change:** ajukan via Administration → approval → tulis ke Core Platform API → audit di Core Platform.

## Data Ownership
| Entity | Ownership | Catatan |
|---|---|---|
| Reference Data | Administration | — |
| SLA Config | Administration | Dipakai ECMF (clock) dan KPI (rules) |
| Workflow Config | Administration (SoT, ADR-008) | ECMF = enforcer |
| Config Version | Administration | BR-ADM-03; histori tidak boleh menghapus jejak transaksi lama (BR-ADM-04) |
| Role-Permission Matrix | **Core Platform** (SoT) | Administration = config view, non-SoT (ADR-008) |

## Integrations
- **Events produced** (per `../../08 Event Catalog/events/events.yaml`): EVT-006 ConfigChanged — consumers: Core Platform (audit wajib, BR-CP-04), ECMF (reload workflow/SLA config), KPI (reload SLA rules). Idempotent by configKey + version.
- **Events consumed:** tidak ada.
- **Core Platform API:** jalur tulis role-permission (ADR-008).

## NFR Considerations
- Setiap perubahan konfigurasi wajib audit trail immutable (BR-ADM-02, BR-008).
- Konfigurasi lama tidak boleh dihapus bila masih dirujuk transaksi historis (BR-ADM-04).
- Emit EVT-006 via transactional outbox (ADR-009).

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Open Questions
- Daftar konfigurasi yang tergolong kritikal (BR-ADM-01) — **ditutup** baseline DEC-004: workflow config, SLA config, role-permission.
- UI Administration belum di-scope Sprint-01 (API-first slice).
