# G1 Exit Verification — 2026-08-01

| Field | Value |
|---|---|
| Gate | G1 (Lifecycle Contract Freeze) |
| Verdict | **EXITED** — tidak perlu re-freeze |
| SoT tip | `feature/cm-batch1-s2-persistence` @ `a5391d6` (post PR #3) |
| Authority | `27 Project Decisions/DEC-006_Contract_Freeze_G1_Sprint02A_v1.0.md` (Accepted) |

## Prompt context

Setelah merge PR #3, pekerjaan “mulai G1” dijalankan sebagai **audit exit**, bukan penulisan ulang kontrak.

## Checklist verifikasi

| Item G1 | Bukti | Status |
|---|---|---|
| Keputusan 400 vs 409 | DEC-006 **D1 → 409** (`INVALID_STATE` / `INVALID_TRANSITION`); 400 = `VALIDATION_ERROR` | ✅ |
| Permission final | `cases:assign`, `cases:status` (D2/D3); SEC-RAM | ✅ |
| API-003 / API-004 normatif | Di `case-service.v1.yaml` (v1.7.0 tip); `case-actions.v1.yaml` = superseded stub | ✅ |
| EVT-002 / EVT-003 frozen | `events.yaml` + DEC-006 D4; ACR-003 Implemented | ✅ |
| Matriks transisi | DOM-ECMF-003 / `CASE_STATE_MACHINE.md` | ✅ |
| U-6 konsolidasi spec | Closed Sprint-03A (`ACR_SPRINT02B.md` ACR-001) | ✅ |

## Sisa non-blocker (bukan G1 re-open)

| ID | Isi | Catatan |
|---|---|---|
| U-5 | Sign-off manusia G0 + DoR FRD-002 | Proses Board/BO — tidak mengubah kontrak |
| U-1 | Subset transisi Sprint-02B (reopen dll.) | Config / planning |
| ACR-002 | Customer 360 | Deferred sampai INT-001A — di luar G1 |

## Konsekuensi

- **Jangan** membuat ADR/DEC kompetitor untuk 400/409.  
- **Sprint-02B implementation MAY proceed / already landed** pada jalur `implementation/backend` (assign/status + list per ACR).  
- Pekerjaan berikutnya untuk “selesai modul”: **G2 mini-gate** + gap Sprint-03 (SLA/dashboard) / SIT Mode A — **bukan** Mode B (C-7 CLOSED).

## Related

- PR #3 merged: hardening post-P5  
- Roadmap: `ai/sprint/IMPLEMENTATION_ROADMAP_v0.1.md` §G1
