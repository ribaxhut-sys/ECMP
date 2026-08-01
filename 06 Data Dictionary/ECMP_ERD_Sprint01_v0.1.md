# ECMP ERD Sprint-01 (DD-ERD-001)

| Field | Value |
|---|---|
| ID | DD-ERD-001 |
| Version | 0.1 |
| Owner | Data Architect / BA Lead |
| Reviewer | Solution Architect, ECMF Domain PO |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline Sprint-01) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Diagram relasi entitas untuk skema fisik Sprint-01 (migration `0001_initial_cases_audit_outbox`): tabel `cases`, `audit_log`, `outbox`, plus diagram konseptual relasi antar entitas inti. Definisi atribut lengkap ada di [`ECMP_Data_Dictionary_v1.0.md`](./ECMP_Data_Dictionary_v1.0.md).

## 1. ERD Fisik Sprint-01

Catatan: relasi antar tabel bersifat **logis** (tidak ada FK constraint fisik di Sprint-01). `audit_log` menunjuk entity via `entity_type` + `entity_id`; `outbox` memuat referensi case di dalam `payload`.

```mermaid
erDiagram
    CASES {
        string_32 case_id PK "format CASE- diikuti 10 hex"
        string_64 customer_id "indexed, ref eksternal Customer Master"
        string_32 case_type "COMPLAINT | INQUIRY"
        string_16 priority "LOW | MEDIUM | HIGH | CRITICAL"
        string_200 subject
        text description
        string_32 status "Sprint-01: REGISTERED"
        string_32 channel "nullable"
        boolean customer_verified "default false (stub INT-001)"
        timestamptz created_at "UTC"
        string_64 created_by
        timestamptz updated_at "UTC"
        string_64 updated_by
    }

    AUDIT_LOG {
        string_36 log_id PK "UUID"
        string_64 actor_user_id
        string_64 action "mis. CASE_CREATED"
        string_64 entity_type "indexed dgn entity_id"
        string_64 entity_id
        json new_value
        timestamptz occurred_at "UTC, append-only"
    }

    OUTBOX {
        string_36 outbox_id PK "UUID"
        string_16 event_id "mis. EVT-001"
        string_64 event_name "mis. CaseCreated"
        json payload
        timestamptz created_at "UTC"
        timestamptz published_at "nullable; index komposit (published_at, created_at)"
    }

    CASES ||--o{ AUDIT_LOG : "logis: entity_type='case', entity_id=case_id"
    CASES ||--o{ OUTBOX : "logis: payload.caseId"
```

## 2. Diagram Konseptual Entitas Inti

```mermaid
flowchart LR
    CM["Customer Master<br/>(eksternal, SoR pelanggan)"]
    CR["Customer Reference<br/>(cache read-only, ADR-002)"]
    CASE["Case<br/>(ECMF, SoR di ECMP)"]
    AUDIT["Audit Log<br/>(append-only, BR-CP-03)"]
    OUTBOX["Outbox / Event<br/>(ADR-009, EVT-001 CaseCreated)"]

    CM -. "sync read-only (INT-001)" .-> CR
    CASE -- "customer_id (referensi eksternal)" --> CR
    CASE -- "setiap mutasi tercatat" --> AUDIT
    CASE -- "create → CaseCreated" --> OUTBOX
```

Ringkasan relasi:
- **Case — Customer Reference (eksternal)**: Case memegang `customer_id` sebagai referensi ke Customer Master; ECMP bukan SoR pelanggan (ADR-002), verifikasi via INT-001 (stub Sprint-01 → `customer_verified=false`).
- **Case — Audit**: setiap mutasi Case menghasilkan entri `audit_log` (append-only) via `entity_type`/`entity_id`.
- **Case — Outbox/Event**: create Case menulis record `outbox` (EVT-001 CaseCreated) dalam satu transaksi; publikasi ke broker ditunda (ADR-009).

## Related
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`
- `../05 Architecture Decision Records/ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0.md`
- `../05 Architecture Decision Records/ECMP_ADR_009_Message_Broker_Deferral_v1.0.md`
- `../09 Integration Catalog/ECMP_INT_001_Customer_Master_Read_v0.1.md`
- `../27 Project Decisions/DEC-018_Multi_Source_Multi_Target_Complaint_TASK042_v1.0.md`
- `implementation/backend/alembic/versions/0001_initial_cases_audit_outbox.py` (skema fisik sumber)

## 3. Complaint multi-source / multi-target (DEC-018 / TASK-042)

Physical table `complaints` (backend migration `0026_complaint_source_target`)
adds polymorphic origin/destination without subtype tables:

```mermaid
erDiagram
    COMPLAINTS {
        uuid id PK
        string complaint_number UK
        uuid customer_id FK "nullable when source != CUSTOMER"
        uuid branch_id FK "nullable; set when target = BRANCH"
        string source_type "CUSTOMER|BRANCH|HEAD_OFFICE|SYSTEM"
        uuid source_id "polymorphic originator"
        string target_type "BRANCH|HEAD_OFFICE"
        uuid target_id "polymorphic destination; nullable legacy"
        string status
        string priority
    }
    CUSTOMERS ||--o{ COMPLAINTS : "customer_id when CUSTOMER"
    BRANCHES ||--o{ COMPLAINTS : "branch_id when target BRANCH"
```

Enums are VARCHAR-backed so future values (VENDOR, REGIONAL, …) do not require
schema changes. Lifecycle and related aggregates (Assignment, Timeline,
Resolution, Appointment, Escalation) are unchanged.

## Addendum — Identity & Password Management (2026-07-28)

Foundation Alembic `0037_password_management` (live SoT under `backend/`):

```mermaid
erDiagram
    USERS {
        uuid id PK
        boolean force_password_change "default false"
        string password_hash "bcrypt; never API-exposed"
    }
    PASSWORD_RESET_TOKENS {
        uuid id PK
        uuid user_id FK
        string token_hash "SHA-256 only"
        timestamptz expires_at
        timestamptz used_at "nullable"
        timestamptz created_at
    }
    USERS ||--o{ PASSWORD_RESET_TOKENS : "user_id"
```

See `10 Security and Access Standards/ECMP_Identity_Password_Management_v1.0.md`.
