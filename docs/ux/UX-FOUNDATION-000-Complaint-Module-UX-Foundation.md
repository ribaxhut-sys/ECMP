# UX-FOUNDATION-000 — Complaint Module UX Foundation

| Field | Value |
|---|---|
| Document ID | UX-FOUNDATION-000 |
| Title | Complaint Module UX Foundation |
| Status | Draft — revisi mengikuti merge persona PDS-001; paket wajib Review ulang sebelum READY FOR APPROVAL |
| Version | 1.2 |
| Date | 2026-08-05 |
| Parent | ECMP-CONSTITUTION-001 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → **UX-FOUNDATION-000** → (baseline) PDS-001 · PWDM-001 · IA-001 · NAV-001 → **UX-DISC-001** → WF-001 → UI-001 → Prototype → Implementation |
| Revision note | Rujukan PDS-000 diperbarui ke **PDS-001** mengikuti merge persona Customer Service + Resolver/Handler → Complaint Officer (UX-001 Documentation Update, 2026-08-05). PDS-000 dipertahankan sebagai baseline historis, tidak lagi menjadi rujukan aktif. **G0.2D / BO-004 (2026-08-05):** status §2 PWDM-001 & IA-001 disinkronkan ke Draft agar selaras §6 (bukan READY FOR APPROVAL). **UX-001 Complete Discovery (2026-08-05):** fase Discovery ditutup oleh `UX-DISC-001`; §4 diperbarui agar urutan pasca-baseline mencerminkan Discovery → Wireframe. |

## 1. Purpose

UX Foundation adalah titik masuk resmi bagi seluruh pekerjaan UX Complaint Management Module.

Dokumen ini menetapkan baseline yang mengikat: persona, workflow & decision, dan information architecture. Ia tidak mendesain ulang artefak tersebut, tidak menambah konsep UX baru, dan tidak membahas implementasi. Tujuannya adalah memastikan setiap turunan UX berikutnya berangkat dari fondasi yang sama, sehingga domain pengalaman pengguna tetap stabil ketika mekanisme integrasi Enterprise berubah.

---

## 2. Baseline Documents

Paket baseline UX Foundation terdiri dari tiga dokumen berikut.

### PDS-001 — Persona Design Specification

| Field | Value |
|---|---|
| Document ID | PDS-001 (menggantikan PDS-000) |
| Title | Persona Design Specification |
| Status | Draft — menunggu Review/Approval setelah merge persona |
| Version | 1.0 |
| Scope | Mendefinisikan siapa pengguna Complaint Management Module dan apa yang membentuk pekerjaan mereka. Closed set tiga persona operasional: Complaint Officer (gabungan Customer Service + Resolver/Case Handler) · Supervisor · Manager. Bukan Business Rules, API, Domain Model, Authorization, Workflow Engine, UI, atau Wireframe. |

### PWDM-001 — Persona Workflow & Decision Model

| Field | Value |
|---|---|
| Document ID | PWDM-001 |
| Title | Persona Workflow & Decision Model |
| Status | Draft — menunggu Review/Approval setelah merge persona |
| Version | 1.0 |
| Scope | Mendeskripsikan bagaimana setiap persona bekerja sepanjang hari operasional — urutan kerja, keputusan, dan friksi. Bukan layar, komponen, atau interaksi UI. Tidak mendefinisikan ulang persona (PDS-000). |

### IA-001 — Information Architecture

| Field | Value |
|---|---|
| Document ID | IA-001 |
| Title | Information Architecture |
| Status | Draft — menunggu Review/Approval setelah merge persona |
| Version | 1.0 |
| Scope | Menentukan informasi yang dibutuhkan tiap persona, kapan, di mana berada, bagaimana dikelompokkan, dan bagaimana navigasi mengalir — di atas kerja yang sudah dipetakan PWDM-001. Bukan layar, komponen, atau visual. Tidak mendefinisikan ulang persona atau workflow. |

---

## 3. Relationship

Ketiga dokumen membentuk satu rantai desain berkesinambungan:

```
PDS-001
  Siapa pengguna & apa yang membentuk pekerjaan mereka
        ↓
PWDM-001
  Bagaimana mereka bekerja sehari-hari — urutan, keputusan, friksi
        ↓
IA-001
  Informasi apa yang dibutuhkan, kapan, di mana, dan bagaimana navigasi mengalir
```

- **PDS-001** menetapkan identitas persona, tujuan kerja, JTBD, prioritas informasi, dan tanggung jawab workspace.
- **PWDM-001** menurunkan persona itu menjadi alur kerja harian dan model keputusan — tanpa mengubah siapa persona-nya.
- **IA-001** menurunkan alur & keputusan itu menjadi inventori informasi, ownership, hierarki, zona workspace, dan arsitektur navigasi — tanpa mengubah persona atau workflow.

Setiap lapisan hanya boleh merujuk ke atas; tidak boleh mendefinisikan ulang lapisan di atasnya.

---

## 4. UX Roadmap

Urutan turunan resmi setelah baseline persona/workflow/IA:

| ID / Tahap | Nama | Status Discovery |
|---|---|---|
| NAV-001 | Navigation Architecture | Ada — Draft (reuse) |
| WF-000 · WF-PLAN-001 | Wireframe constitution + backlog | Ada — Draft (reuse) |
| **UX-DISC-001** | **Complete UX Discovery (one-pass)** | **Lengkap — Draft, siap Review** |
| WF-001 | Low Fidelity Wireframes | **R1 package:** `WF-001-R1` (Draft complete) · R2/R3 belum |
| UI-001 | High Fidelity Design | Future |
| — | Prototype | Future (rencana di UX-DISC-001 §10) |
| — | Implementation | Future (roadmap batch di UX-DISC-001 §11) |

**UX-DISC-001** merangkum discovery (summary, journey, screen/workspace inventory, gap analysis, readiness) tanpa menduplikasi PDS/PWDM/IA/NAV. Setelah Discovery, pekerjaan desain berikutnya adalah **wireframing (WF-001)**, bukan dokumen discovery tambahan.

Isi tiap tahap pasca-Discovery ditentukan pada penugasan masing-masing.

---

## 5. Governance Rules

1. **PDS-001** adalah sumber otoritatif untuk Personas.
2. **PWDM-001** adalah sumber otoritatif untuk Workflows & Decision Models.
3. **IA-001** adalah sumber otoritatif untuk Information Architecture.
4. Setiap artefak UX di masa depan **wajib** diturunkan dari ketiga dokumen baseline ini.
5. Tidak ada artefak masa depan yang boleh mendefinisikan ulang Personas, Workflows, atau Information Architecture tanpa formal governance (revisi baseline yang disetujui).

---

## 6. Approval Status

| Field | Value |
|---|---|
| Package | UX Foundation (PDS-001 · PWDM-001 · IA-001) |
| Status | **DRAFT — REVISI MERGE PERSONA, BUKAN READY FOR APPROVAL** |
| Approved | Tidak — status READY FOR APPROVAL sebelumnya dicabut karena PDS-001/PWDM-001/IA-001 direvisi mengikuti UX-001 Documentation Update (merge Customer Service + Resolver/Handler → Complaint Officer); paket wajib melalui Review ulang sebelum kembali READY FOR APPROVAL. |

Status APPROVED hanya boleh dicatat setelah formal approval diberikan. Dokumen ini tidak mengklaim APPROVED.

---

## Related

- `docs/ux/WF-001-R1-Wireframe-Package.md` — WF-001 Release 1 LF package
- `docs/ux/UX-DISC-001-Complete-UX-Discovery.md` — paket Complete UX Discovery (UX-001)
- `docs/ux/PDS-001-Persona-Design-Specification.md`
- `docs/ux/PDS-000-Persona-Design-Specification.md` (superseded — baseline historis)
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`
- `docs/ux/WF-PLAN-001-Wireframe-Roadmap-Backlog.md`
- `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`
