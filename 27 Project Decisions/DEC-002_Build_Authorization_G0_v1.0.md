# Decision Record — Build Authorization (Sprint-01 GO vs Gate G0)

| Field | Value |
|---|---|
| ID | DEC-002 |
| Version | 1.0 |
| Owner | Engineering Manager |
| Reviewer | Tech Lead / Solution Architect |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-21
- Owner: Engineering Manager
- Participants: Architecture Review Board, Tech Lead, PMO

## Context
`ai/sprint/Sprint-01.md` menyatakan "APPROVED — GO for development", sementara `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md` mensyaratkan gate **G0** (platform floor) sebelum Build-1. Dua sinyal otorisasi ini bertentangan.

## Options
- **A.** GO tanpa syarat (abaikan G0).
- **B.** GO Sprint-01 = otorisasi mengerjakan **slice create/get + platform floor G0**; fitur produk di luar slice menunggu G0 lulus.
- **C.** Tahan semua coding sampai seluruh EKR Approved.

## Decision
**Opsi B.** Interpretasi resmi:

1. **Sprint-01 GO** = otorisasi untuk: bootstrap backend, slice create/get (FR-001/FR-002), **dan seluruh deliverable G0** (PostgreSQL + Alembic rev0 `cases`/`audit_log`/`outbox`, docker-compose, backend CI hijau, error envelope OpenAPI, Role matrix minimal, write-audit pada create).
2. **Build-1 (fitur di luar slice: assign, status transition, SLA, notification, dashboard)** hanya boleh dimulai setelah **G0 exit criteria** terpenuhi dan ditandatangani Tech Lead + Solution Architect.
3. **Non-goals Sprint-0/G0** (dilarang dibangun): assign/status transition, Notification delivery, Schedule Slot/Appointment/Work Order, Branch/HO escalation, frontend produk, idempotency key, audit-on-read, pemilihan broker, integrasi SSO/IdP, framework audit generik, scaffold 4-layer penuh.

## Rationale
Menutup celah "GO" dipakai untuk mengkode fitur di atas stub in-memory, tanpa memblokir pekerjaan fondasi yang justru diwajibkan ADR-004.

## Impact
- `ai/sprint/Sprint-01.md` diperbarui untuk merujuk keputusan ini.
- CI backend menjadi gate wajib untuk PR `implementation/backend/**`.

## G0 Exit Criteria (checklist)
- [x] docker-compose PostgreSQL + `.env.example`
- [x] Alembic revision 0: `cases`, `audit_log`, `outbox`
- [x] Create case = 1 transaksi (case + audit + outbox)
- [x] Error envelope runtime = OpenAPI `Error{code,message}`
- [x] Backend CI (migrate → pytest) hijau
- [x] Role matrix minimal (`10 Security and Access Standards`)
- [ ] Sign-off Tech Lead + Solution Architect (manusia — di luar kendali repo)

## Follow-up
- [x] Update `ai/sprint/Sprint-01.md` status wording
- [x] Tambah OQ-005 Resolved di `OPEN_QUESTIONS.md`

## Links
- Related: `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md`, `DEC-001`
