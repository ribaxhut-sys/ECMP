# ECMP-CONSTITUTION-001 — Complaint Management Module Constitution v1.1

| Field | Value |
|---|---|
| Document ID | ECMP-CONSTITUTION-001 |
| Title | Complaint Management Module Constitution |
| Version | 1.1 |
| Date | 2026-07-31 |
| Status | 🔒 **LOCKED** (Operating Constitution / Delivery Binding Filter) |
| Authority | Project Owner / Architecture program operating filter |
| Subordination | **Subordinate to** Board Resolution → ADR → EA Documents |
| Does not | Override Board decisions; invent Target Architecture; unlock Mode B |
| Runtime companion | `ECMP_MASTER_PROMPT_001_…_v1.1.md` |
| Portal mirror | `docs/governance/ECMP-CONSTITUTION-001.md` |
| Mode B | **CLOSED** (C-7 / C-B6-1) — this document does not unlock |

---

## Project Mission

ECMP bukan proyek untuk membangun Enterprise Platform.

ECMP bukan proyek untuk membangun Enterprise Operating System.

ECMP bukan proyek untuk membangun Generic Module Framework.

Misi ECMP hanya satu:

> **Menyelesaikan Complaint Management Module dengan arsitektur yang benar, sehingga ketika pintu Enterprise Application terbuka, yang berubah hanyalah mekanisme integrasinya—bukan domain bisnisnya.**

Seluruh keputusan teknis, arsitektur, implementasi, review, dan dokumentasi harus dapat dibuktikan membantu misi tersebut.

Jika tidak dapat dibuktikan, maka keputusan tersebut berada di luar ruang lingkup proyek.

---

## 1. North Star (Absolute)

Kalimat misi di atas adalah hukum tertinggi proyek untuk perilaku delivery, desain, dan review.

Semua keputusan memiliki prioritas lebih rendah daripada North Star **kecuali** keputusan Architecture Board / ADR yang sudah berlaku — yang mana CONSTITUTION ini **wajib hormati**, bukan ganti.

Jika terdapat konflik antar artefak operasional:

1. Board Resolution  
2. ADR  
3. EA Documents  
4. **ECMP-CONSTITUTION-001** (dokumen ini)  
5. ECMP MASTER PROMPT  

---

## 2. Project Objective

Produk yang sedang dibangun adalah:

**Complaint Management Module**

BUKAN:

- Enterprise Platform  
- Enterprise Operating System  
- Enterprise Engineering Framework  
- Generic SDK  
- Marketplace  
- Framework Multi Module  
- Enterprise Portal  
- Enterprise Runtime  
- Enterprise Module Registry  

Jika diskusi mulai mengarah ke sana, hentikan dan kembali ke Complaint Module, atau tandai:

> Future Work — Di luar ruang lingkup Complaint Management Module.

---

## 3. Target Architecture

Target akhir: Complaint Management Module hidup sebagai **Business Module** di dalam Enterprise Application.

**Enterprise Application menyediakan:** Login, SSO, Identity, Organization, Entitlement, Notification, Shared Services, Shared Infrastructure.

**Complaint Management Module menyediakan:** Complaint Domain, Ticket, Workflow, SLA, Escalation, Assignment, Timeline, Business Rules, Complaint API.

**Complaint Management Module bukan pemilik:** User Master, Password, Login, Identity Master, Organization Master, Enterprise Permission, Enterprise SSO.

Ketika Enterprise siap, yang berubah hanyalah:

- Identity Adapter  
- Authentication Provider  
- Organization Provider  
- Notification Provider / Adapter  
- Shared Service Adapter  

Bukan Domain Complaint.

---

## 4. Mode A dan Mode B

Mode A dan Mode B bukan dua produk dan bukan dua arsitektur. Target Architecture selalu **SATU**.

| Mode | Arti |
|---|---|
| **Mode A** | Authorized Delivery Strategy (hedge delivery agar modul selesai tanpa menunggu Enterprise) |
| **Mode B** | Enterprise Integration Strategy (target akhir ketika Enterprise siap) |

Mode B coding / implementasi produksi tetap mengikuti keputusan Board. Selama Mode B **CLOSED**, dilarang implementasi produksi untuk:

- Identity Adapter Enterprise (runtime)  
- Enterprise SSO / Embed UI / Portal  
- Enterprise OpenAPI `securitySchemes`  
- Enterprise Organization Sync / Entitlement engine sebagai produk Mode B  
- Enterprise Notification Integration produksi  

Yang boleh: menjelaskan status, mendokumentasikan kontrak, **mendesain interface/kontrak**, migration plan — **bukan** coding produksi Mode B.

---

## 5. Governance

Hormati Architecture Board, Board Resolution, ADR, DTM, EA Documents, Architecture Review.

Dilarang: membuat governance tandingan; membuat Target Architecture baru; mengubah keputusan Board; mengabaikan ADR; mengusulkan implementasi yang bertentangan dengan Board.

Jika diperlukan perubahan yang bertentangan dengan keputusan yang berlaku:

> Perlu Board Review.

Perubahan tersebut **tidak** otomatis disetujui.

---

## 6. Stability Guard

Jangan redesign bagian sistem yang telah **accepted / stable / green / production-ready**, kecuali:

1. Regression Bug  
2. Security Issue  
3. Architecture Defect  
4. Business Requirement Baru  
5. Architecture Board Decision  

Prinsip: **Don't redesign a stable solution.**

Khusus Mode A: jangan ulang pekerjaan yang sudah hijau tanpa gap regresi baru (lihat `.cursor/rules/ecmp-module-boundary.mdc` — M1–M5 hygiene).

---

## 7. Domain Protection

Domain Complaint adalah aset utama. Business Rule, Aggregate, dan Workflow harus stabil.

Perubahan Enterprise tidak boleh memaksa perubahan Domain Complaint. Yang boleh berubah: Adapter, Integration Layer, Infrastructure Layer, Authentication / Organization / Notification Provider.

---

## 8. Decision Filter

Sebelum rekomendasi / desain / implementasi:

1. Apakah ini membuat Complaint Module lebih dekat ke **COMPLETE**? Jika tidak → tolak.  
2. Apakah ini mengubah Domain Complaint? Jika ya → hanya jika dibutuhkan Business Requirement.  
3. Apakah ini hanya mengubah mekanisme integrasi? Jika ya → diperbolehkan (dalam batas Board).  
4. Apakah ini bertentangan dengan Board? Jika ya → tolak / “Perlu Board Review.”  

---

## 9. Completion Criteria

Complaint Module dianggap **COMPLETE** apabila Domain, Business Rule, UI (Mode A, tanpa silent foundation cutover / forced dual-SoT merge), API, Test, Architecture boundary, dan Observability selesai sesuai katalog & otorisasi yang berlaku.

**Enterprise Integration bukan syarat COMPLETE.** Enterprise Integration adalah milestone berikutnya.

Keberhasilan diukur dari modul selesai dengan boundary benar — bukan dari jumlah dokumen governance, framework, atau modul enterprise.

---

## 10. Forbidden Behavior

- Memperbesar ruang lingkup menjadi Platform / SDK / Marketplace / OS / Runtime  
- Mengusulkan governance baru tanpa permintaan eksplisit pengguna / Board pathway  
- Redesign besar tanpa evidence  
- Menganggap Accept ADR-016/017/018 = Mode B unlocked  
- Force-merge / retire dual-SoT tanpa Retirement DEC  

---

## Related

- Runtime: [`ECMP_MASTER_PROMPT_001_Complaint_Management_Module_Engineering_Assistant_v1.1.md`](./ECMP_MASTER_PROMPT_001_Complaint_Management_Module_Engineering_Assistant_v1.1.md)  
- Mode A priority: [`ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md`](./ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md)  
- Implementation posture: [`ECMP_PROGRAM_IMPLEMENTATION_001_Implementation_Authorization_Posture_v1.0.md`](./ECMP_PROGRAM_IMPLEMENTATION_001_Implementation_Authorization_Posture_v1.0.md)  
- ADR-014 / Board-004 / Board-006 (Mode B CLOSED)  
- Cursor: `.cursor/rules/ecmp-master-constitution.mdc`, `ecmp-module-boundary.mdc`, `ecmp-anti-skip-phases.mdc`  

---

## Document control

| Version | Date | Notes |
|---|---|---|
| 1.1 | 2026-07-31 | LOCKED operating constitution; Project Mission; Mode B contract-only; dual-SoT / anti-redo notes; subordination hierarchy |
