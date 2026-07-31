# PROGRAM-BOARD-008 — EA-TARGET-CM-001 + EA-PLATFORM-001 Draft Pack

| Field | Value |
|---|---|
| Document ID | GOV-BR-BOARD-008 |
| Program | PROGRAM-BOARD-008 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Prepared by | Chief Enterprise Architect / Documentation Administrator |
| Status | 🟡 **DRAFT** — Architecture Board intake pack (BR-002 lifecycle) |
| Authority requested | Board **review** of drafts; **not** Mode B unlock; **not** implementation authorization |
| Mode B | **CLOSED** (BOARD-004 C-7 · BOARD-006 C-B6-1) — pack does not open coding |

---

## 1. Purpose

Mendaftarkan dua artefak arsitektur sebagai **Draft for Architecture Board**, dengan framing eksplisit:

1. **Bukan tiket implementasi** — body target-state / platform contract tidak boleh dipecah menjadi backlog coding Mode B.
2. **HOST-first** — seluruh asumsi sisi Enterprise Application (HOST) harus Closed / waiver sebelum implementasi yang bergantung kontrak tersebut.
3. **Indeks keputusan** — DTM-001 menghubungkan ADR, prinsip, desain, alasan, dan bukti.

---

## 2. Artifacts in this pack

| ID | File | Lifecycle | Peran |
|---|---|---|---|
| **EA-TARGET-CM-001** | [`../04 Solution Architecture/board-drafts/EA-TARGET-CM-001_Complaint_Management_Module_Target_Architecture_v1.0.md`](../04%20Solution%20Architecture/board-drafts/EA-TARGET-CM-001_Complaint_Management_Module_Target_Architecture_v1.0.md) | DRAFT | Target architecture *guest* = Complaint Management Module |
| **EA-PLATFORM-001** | [`../04 Solution Architecture/board-drafts/EA-PLATFORM-001_Enterprise_Module_Platform_v1.0.md`](../04%20Solution%20Architecture/board-drafts/EA-PLATFORM-001_Enterprise_Module_Platform_v1.0.md) | DRAFT | Kontrak modularitas HOST↔GUEST (bilateral EP) |
| **DTM-001** | [`../26 Traceability/ECMP_DTM_001_Decision_Traceability_Matrix_v0.1.md`](../26%20Traceability/ECMP_DTM_001_Decision_Traceability_Matrix_v0.1.md) | DRAFT | Decision Traceability Matrix (indeks keputusan) |

**Hubungan:** EA-PLATFORM-001 = standar bersama (masih usulan). EA-TARGET-CM-001 = penerapan desain untuk modul keluhan. DTM-001 = indeks lintas keduanya + ADR Accepted.

Dokumen ini **melengkapi** ADR-014…018 (Accepted with Conditions). Ia **tidak** mensupersede ADR dan **tidak** mengubah Board Resolution sebelumnya.

---

## 3. What the Board is asked to do (this session / next)

| # | Request | Outcome yang diinginkan |
|---:|---|---|
| R1 | Terima pack sebagai **DRAFT under review** (BR-002 → boleh naik ke REVIEW) | Status tercatat; bukan BASELINE |
| R2 | Tegaskan: roadmap Sprint/rilis di kedua EA **bukan** authorization coding | Anti-skip Mode B |
| R3 | Adopsi prinsip induk *Enterprise owns Capability, Module owns Meaning* sebagai **klarifikasi** ADR-014 (bukan revisi teks ADR kecuali Board memutuskan amend) | Arah kepemilikan jelas |
| R4 | Setujui **HOST Gate** (§4) sebagai prasyarat implementasi bergantung kontrak | Binding untuk Tech Lead / PMO |
| R5 | Arahkan EP Owner ke sesi bilateral untuk menutup H*/K*/F* (lihat §4) | Masukan ke org-gap / profiles track |
| R6 | **Jangan** buka C-7 / C-B6-1 dalam resolusi pack ini kecuali evidence bar terpenuhi | Mode B tetap CLOSED |

**Out of scope untuk pack ini:** Identity Adapter coding, OpenAPI enterprise `securitySchemes`, SSO browser bridge (OD-FE-002), force-merge DEC-020, menghapus Mode A credential routes.

---

## 4. HOST Gate (binding recommendation)

**Aturan:** implementasi yang bergantung pada kontrak HOST/enterprise **dilarang dimulai** sampai item terkait berstatus **Closed** atau **Waived (Board + EP Owner, bertanggal, dengan residual risk)**.

### 4.1 Register (canonical list)

| Code | Pertanyaan / deliverable | Sumber | Blocks |
|---|---|---|---|
| **H1** | Apakah EP sudah punya model modul/ekstensi? | EA-PLATFORM Lampiran A | Seluruh platform draft alignment |
| **H2** | Stack & versi framework host (FE) | EA-PLATFORM H2 / TARGET F2 | FE ACL / rewrite risk |
| **H3** | Apakah Module Registry akan dibangun (roadmap EP)? | EA-PLATFORM H3 | Lifecycle registrasi |
| **H4** | Teknologi event bus & kontrak DLQ | EA-PLATFORM H4 / TARGET K6 | Outbox adapter |
| **H5** | Metode embed UI (federation / iframe / mount / package) | EA-PLATFORM H5 / TARGET F1 | FE Sprint 5 |
| **H6** | Mekanisme entitlement | EA-PLATFORM H6 / TARGET K3 | Entitlement Gate |
| **H7** | Model & API organisasi | EA-PLATFORM H7 / TARGET K4 | Org scope / ADR-018 |
| **H8** | Sink observability | EA-PLATFORM H8 / TARGET K9 | Metrics/logging sink |
| **H9** | Contoh payload nyata per kapabilitas (token sample, dll.) | EA-PLATFORM H9 / TARGET K1–K2 | Identity Adapter |
| **H10** | Modul kedua sebagai validator platform v1.0 | EA-PLATFORM H10 | Deklarasi platform v1.0 |
| **K5** | (subset) Framework host — sama H2 | TARGET K5 | FE reuse |
| **K7** | API File Service | TARGET K7 | Attachment port |
| **K8** | Kontrak Notification | TARGET K8 | Notification port |
| **K10** | Format module manifest | TARGET K10 / F4 | Registrasi guest |
| **K11** | Bentuk deployment (out-of-process vs in-process) | TARGET §13.1 | BAB 6/7/13 lock |
| **F3** | Kontrak design system / shared UI | TARGET F3 | `platform/ui.ts` |
| **C-B6-3** | Org-gap evidence bar | BOARD-006 / org-gap plan | Mode B unlock path |

Status operasional tiap baris: kolom *HOST status* di **DTM-001** dan register di bawah (awalnya semua **Open**).

| Code | Status 2026-07-31 | Evidence / waiver |
|---|---|---|
| H1…H10, K*, F*, C-B6-3 | **Open** | — |

### 4.2 Allowed without G-HOST

| Allowed now | Why |
|---|---|
| Board review / komentar / amend draft | Governance |
| EP bilateral sessions (profiles, H*/K*/F* gathering) | Menutup gate |
| Mode A delivery per `GOV-MODEA-NEXT-001` | AUTHORIZED WITH CONDITIONS; no enterprise SoR |
| Capability Ownership Matrix *discussion* (not production cutover) | Menutup BLK-C1 secara keputusan, belum coding adapter |

### 4.3 Forbidden until G-HOST ∩ (G-C7 for Mode B runtime)

Identity Adapter produksi · Entitlement Gate enterprise · Org sync produk · Hapus `/api/v1/auth` Mode A hedge · Embed portal EP · OpenAPI enterprise `securitySchemes` · “Platform registry” di dalam repo ECMP seolah HOST.

---

## 5. Relationship to prior Board decisions

| Prior | Binding remains |
|---|---|
| BOARD-004 | ADR-014/015 Accepted with Conditions; Mode B CLOSED (C-7) |
| BOARD-006 | ADR-016/017/018 Accepted with Conditions; C-B6-1…7; Mode B CLOSED |
| BR-008 | Mode A AUTHORIZED WITH CONDITIONS |
| BR-007 | ADR-013 remain active — jangan supersede lewat dokumen FE/EA saja |
| SAFE-NEXT P1–P4 | Org-gap, EP bilateral, O-06/O-07, Mode A — parallel track |

---

## 6. Proposed Board minute (draft text)

> Architecture Board menerima **PROGRAM-BOARD-008** sebagai *Draft Pack*: EA-TARGET-CM-001, EA-PLATFORM-001, dan DTM-001 berstatus **DRAFT**. Roadmap di dalamnya **bukan** authorization implementasi. Board mengadopsi rekomendasi **HOST Gate** (§4): asumsi HOST harus Closed/Waived sebelum coding yang bergantung kontrak. Mode B tetap **CLOSED** (C-B6-1 / C-7). Tidak ada perubahan pada ADR Accepted kecuali melalui amend ADR terpisah.

---

## 7. Next work (governance only)

1. Jadwalkan Board REVIEW (form `reviews/ARCHITECTURE_REVIEW_FORM.md`).
2. EP Owner session — isi register §4.1; update DTM-001.
3. Lanjutkan P1 org-gap / P2 bilateral profiles (tidak digantikan pack ini).
4. Engineering: tetap Mode A queue — **jangan** buka Sprint 2–5 EA-TARGET sebagai ticket.

---

## 8. Revision

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Initial draft pack; frames Claude EA drafts as Board intake + HOST Gate + DTM-001 |
