# ECMP_FRD_Notification_v0.1

| Field | Value |
|---|---|
| ID | FRD-004 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | Notification PO / Integration Lead |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

> **Draft — belum DoR; implementasi menunggu gate per DEC-002.**

## 1. Overview
Notifikasi event-driven untuk stakeholder case (BP-004): konsumsi event case dan pengiriman notifikasi ke penerima yang ditentukan konfigurasi.

Domain: **Notification**.

## 2. Actors & Roles
| Actor | Role |
|---|---|
| System (Notification service) | Konsumsi event, resolve penerima, deliver, log, retry |
| Assignee / Supervisor | Penerima notifikasi |
| Administrator | Konfigurasi rule notifikasi (opt-in) |

## 3. Functional Requirements
| FR-ID | Requirement | Priority | BR Ref | API/Event | Test |
|---|---|---|---|---|---|
| FR-020 | System shall send notification to resolved recipients on case creation/assignment | Must | BR-004 | konsumsi EVT-001, EVT-002 | TC-020 |

## 4. Event Consumption
- **EVT-001 CaseCreated** → notifikasi ke assignee pool / supervisor unit
- **EVT-002 CaseAssigned** → notifikasi ke assignee (dan previous assignee bila reassign)
- Delivery guarantee at-least-once (ADR-001): konsumen **wajib idempotent** (dedup per caseId + event key)

## 5. Business Rules Reference
- **BR-004** (BR-NOTIF-01): notifikasi hanya untuk event yang dikonfigurasi eksplisit (opt-in)
- **BR-NOTIF-02**: penerima dari kombinasi role/assignment/organisasi, bukan daftar statis
- **BR-NOTIF-03**: riwayat pengiriman (berhasil/gagal) wajib disimpan
- **BR-NOTIF-04 (baseline DEC-004)**: retry maksimal **3x interval 5 menit**; setelah max retry, eskalasi via **email ke supervisor** terkait

## 6. Acceptance Criteria (ringkas, Gherkin)
```gherkin
Scenario: Notifikasi saat case di-assign
  Given rule notifikasi CaseAssigned aktif (opt-in)
  When EVT-002 diterima
  Then notifikasi terkirim ke assignee dan delivery log tercatat (TC-020)

Scenario: Duplikat event tidak menggandakan notifikasi
  Given EVT-002 yang sama diterima dua kali (at-least-once)
  Then hanya satu notifikasi terkirim (idempotent consumer)

Scenario: Retry lalu eskalasi
  Given pengiriman gagal
  When retry 3x interval 5 menit tetap gagal
  Then eskalasi email ke supervisor terkait dan seluruh attempt tercatat (BR-NOTIF-03/04)
```

## 7. Dependencies
- Outbox/event bus operasional (G0: tabel `outbox`; broker belum dipilih — pemilihan broker adalah non-goal DEC-002, perlu ADR)
- Template & rule konfigurasi notifikasi (Administration)
- Traceability: TRC-L-006 (Sprint-02, Planned)

## 8. Out of Scope (versi ini)
- Channel selain in-app/email, preferensi notifikasi per user, digest/batching, push/SMS.
