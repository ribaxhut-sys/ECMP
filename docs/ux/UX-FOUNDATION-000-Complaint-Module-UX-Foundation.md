# UX-FOUNDATION-000 — Complaint Module UX Foundation

| Field | Value |
|---|---|
| Document ID | UX-FOUNDATION-000 |
| Title | Complaint Module UX Foundation |
| Status | READY FOR APPROVAL |
| Version | 1.0 |
| Date | 2026-08-03 |
| Parent | ECMP-CONSTITUTION-001 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → **UX-FOUNDATION-000** → (baseline) PDS-000 · PWDM-001 · IA-001 → (future) NAV-001 → WF-001 → UI-001 → Prototype → Implementation |

## 1. Purpose

UX Foundation adalah titik masuk resmi bagi seluruh pekerjaan UX Complaint Management Module.

Dokumen ini menetapkan baseline yang mengikat: persona, workflow & decision, dan information architecture. Ia tidak mendesain ulang artefak tersebut, tidak menambah konsep UX baru, dan tidak membahas implementasi. Tujuannya adalah memastikan setiap turunan UX berikutnya berangkat dari fondasi yang sama, sehingga domain pengalaman pengguna tetap stabil ketika mekanisme integrasi Enterprise berubah.

---

## 2. Baseline Documents

Paket baseline UX Foundation terdiri dari tiga dokumen berikut.

### PDS-000 — Persona Design Specification

| Field | Value |
|---|---|
| Document ID | PDS-000 |
| Title | Persona Design Specification |
| Status | READY FOR APPROVAL |
| Version | 1.0 |
| Scope | Mendefinisikan siapa pengguna Complaint Management Module dan apa yang membentuk pekerjaan mereka. Closed set empat persona operasional: Customer Service · Resolver / Case Handler · Supervisor · Manager. Bukan Business Rules, API, Domain Model, Authorization, Workflow Engine, UI, atau Wireframe. |

### PWDM-001 — Persona Workflow & Decision Model

| Field | Value |
|---|---|
| Document ID | PWDM-001 |
| Title | Persona Workflow & Decision Model |
| Status | READY FOR APPROVAL |
| Version | 1.0 |
| Scope | Mendeskripsikan bagaimana setiap persona bekerja sepanjang hari operasional — urutan kerja, keputusan, dan friksi. Bukan layar, komponen, atau interaksi UI. Tidak mendefinisikan ulang persona (PDS-000). |

### IA-001 — Information Architecture

| Field | Value |
|---|---|
| Document ID | IA-001 |
| Title | Information Architecture |
| Status | READY FOR APPROVAL |
| Version | 1.0 |
| Scope | Menentukan informasi yang dibutuhkan tiap persona, kapan, di mana berada, bagaimana dikelompokkan, dan bagaimana navigasi mengalir — di atas kerja yang sudah dipetakan PWDM-001. Bukan layar, komponen, atau visual. Tidak mendefinisikan ulang persona atau workflow. |

---

## 3. Relationship

Ketiga dokumen membentuk satu rantai desain berkesinambungan:

```
PDS-000
  Siapa pengguna & apa yang membentuk pekerjaan mereka
        ↓
PWDM-001
  Bagaimana mereka bekerja sehari-hari — urutan, keputusan, friksi
        ↓
IA-001
  Informasi apa yang dibutuhkan, kapan, di mana, dan bagaimana navigasi mengalir
```

- **PDS-000** menetapkan identitas persona, tujuan kerja, JTBD, prioritas informasi, dan tanggung jawab workspace.
- **PWDM-001** menurunkan persona itu menjadi alur kerja harian dan model keputusan — tanpa mengubah siapa persona-nya.
- **IA-001** menurunkan alur & keputusan itu menjadi inventori informasi, ownership, hierarki, zona workspace, dan arsitektur navigasi — tanpa mengubah persona atau workflow.

Setiap lapisan hanya boleh merujuk ke atas; tidak boleh mendefinisikan ulang lapisan di atasnya.

---

## 4. Future UX Roadmap

Urutan turunan resmi setelah baseline ini:

| ID / Tahap | Nama |
|---|---|
| NAV-001 | Navigation Model |
| WF-001 | Low Fidelity Wireframes |
| UI-001 | High Fidelity Design |
| — | Prototype |
| — | Implementation |

Isi tiap tahap ditentukan pada penugasan masing-masing. Dokumen ini tidak mendefinisikan kontennya.

---

## 5. Governance Rules

1. **PDS-000** adalah sumber otoritatif untuk Personas.
2. **PWDM-001** adalah sumber otoritatif untuk Workflows & Decision Models.
3. **IA-001** adalah sumber otoritatif untuk Information Architecture.
4. Setiap artefak UX di masa depan **wajib** diturunkan dari ketiga dokumen baseline ini.
5. Tidak ada artefak masa depan yang boleh mendefinisikan ulang Personas, Workflows, atau Information Architecture tanpa formal governance (revisi baseline yang disetujui).

---

## 6. Approval Status

| Field | Value |
|---|---|
| Package | UX Foundation (PDS-000 · PWDM-001 · IA-001) |
| Status | **READY FOR APPROVAL** |
| Approved | Tidak — menunggu formal approval |

Status APPROVED hanya boleh dicatat setelah formal approval diberikan. Dokumen ini tidak mengklaim APPROVED.

---

## Related

- `docs/ux/PDS-000-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`
