# DTM-001 — Decision Traceability Matrix

| Field | Value |
|---|---|
| Document ID | **DTM-001** |
| Full ID | TRC-DTM-001 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Status | 🟡 **DRAFT** |
| Owner | Chief Enterprise Architect / Solution Architect |
| Reviewer | Architecture Board · Enterprise Application Owner · Security Architect |
| Approver | Architecture Board (when pack BOARD-008 enters REVIEW/BASELINE) |
| Pack | [`../18 Architecture Governance/ECMP_PROGRAM_BOARD_008_EA_TARGET_PLATFORM_Draft_Pack_v0.1.md`](../18%20Architecture%20Governance/ECMP_PROGRAM_BOARD_008_EA_TARGET_PLATFORM_Draft_Pack_v0.1.md) |
| Purpose | Indeks keputusan yang menghubungkan **ADR**, **prinsip platform**, **keputusan desain (EA)**, **alasan**, **bukti**, dan **ketergantungan HOST** |

---

## 1. Cara pakai

| Kolom | Arti |
|---|---|
| **DTM-ID** | ID stabil baris keputusan (`DTM-D-xxx`) |
| **Statement** | Keputusan dalam satu kalimat |
| **Class** | `ADR` · `PRINCIPLE` · `DESIGN` · `GATE` · `DEC` |
| **Source** | Dokumen kanonik (ADR / EA / Board / DEC) |
| **Rationale** | Mengapa |
| **Evidence** | Bukti repo / resolusi / katalog |
| **HOST dep.** | Kode H*/K*/F*/C-B6-* yang harus Closed sebelum implementasi bergantung; `—` = tidak bergantung HOST |
| **Impl. posture** | `Board-only` · `Mode A OK` · `POST G-HOST` · `POST C-7` · `Blocked` |
| **Status** | `Proposed` · `Accepted` · `Accepted w/ Conditions` · `Draft` · `Superseded` |

**Aturan pemeliharaan:** setiap amend ADR Accepted, keputusan desain baru di EA-TARGET/PLATFORM, atau penutupan item HOST → **update baris DTM** di commit yang sama (atau sync record terpisah).

**Bukan pengganti:** RTM (FR→API→TC) di folder ini; DTM = *keputusan arsitektur*, RTM = *requirement delivery*.

---

## 2. Matrix — keputusan induk & Board

| DTM-ID | Statement | Class | Source | Rationale | Evidence | HOST dep. | Impl. posture | Status |
|---|---|---|---|---|---|---|---|---|
| DTM-D-001 | ECMP adalah Business Module tambahan Enterprise Platform, bukan aplikasi enterprise mandiri (target akhir) | ADR | ADR-014 v1.4 | Hindari login/user/org ganda | BOARD-004 Accept w/ Conditions | — | Board-only (identity) | Accepted w/ Conditions |
| DTM-D-002 | Mode B embed/SSO coding **CLOSED** sampai Board unlock | GATE | BOARD-004 C-7 · BOARD-006 C-B6-1 | Fail-closed subordination | Board resolutions | C-B6-3 + H* | Blocked | Binding |
| DTM-D-003 | Mode A delivery AUTHORIZED WITH CONDITIONS | GATE | PROGRAM-ADR-002 BR-008 | Hedge lab/ops tanpa unlock enterprise | Implementation Authorization posture | — | Mode A OK | Binding |
| DTM-D-004 | Enterprise identity contract (klaim, fail-closed, no privileged role from IdP) | ADR | ADR-015 v1.3 | AuthN enterprise ≠ AuthZ modul | BOARD-004; RoleMapper tests | H9, K1–K2 | POST C-7 (runtime) | Accepted w/ Conditions |
| DTM-D-005 | OIDC binding profile subordinate to ADR-015/016 | ADR | ADR-016 v1.0 | Binding teknis tanpa unlock coding | BOARD-006; Binding Profile draft | H9, K2 | POST C-7 | Accepted w/ Conditions |
| DTM-D-006 | Entitlement architecture: AuthN ≠ module access | ADR | ADR-017 v1.0 | Default deny ke modul | BOARD-006; Entitlement Profile draft | H6, K3 | POST C-7 | Accepted w/ Conditions |
| DTM-D-007 | Organization sync architecture (reference, not SoR di modul) | ADR | ADR-018 v1.0 | Org master milik EP | BOARD-006; Org Sync Profile; org-gap plan | H7, K4, C-B6-3 | POST C-7 | Accepted w/ Conditions |
| DTM-D-008 | ADR-013 frontend stack remain active; jangan supersede lewat dokumen FE/EA saja | ADR | ADR-013 · BR-007 | Stabilitas stack Mode A | BOARD / FE docs | H2, F1–F3 | Mode A OK | Accepted |
| DTM-D-009 | Complaint dual-SoT (foundation + aggregate) coexistence; no forced merge | DEC | DEC-020 | Hindari silent cutover | Mount coexistence tests; DOC-001 | — | Mode A OK | Accepted (hygiene) |
| DTM-D-010 | Retire/force-merge dual-SoT hanya dengan Retirement DEC | GATE | DEC-020 · BOARD-008 | Anti silent foundation cutover | Program rules | — | Blocked until Retirement DEC | Binding |
| DTM-D-011 | ECMP bukan Customer Master SoR | ADR | ADR-002 | Customer via provider/API | Customer adapter stub | — | Mode A OK (adapter) | Accepted |
| DTM-D-012 | Message broker ditunda; outbox lokal | ADR | ADR-009 | Kurangi distributed complexity | Event catalog delivery_guarantee | H4, K6 | POST G-HOST (bus) | Accepted |

---

## 3. Matrix — prinsip platform (EA-PLATFORM-001 / EA-TARGET-CM-001)

| DTM-ID | Statement | Class | Source | Rationale | Evidence | HOST dep. | Impl. posture | Status |
|---|---|---|---|---|---|---|---|---|
| DTM-D-020 | **Enterprise owns Capability; Module owns Meaning** | PRINCIPLE | EA-TARGET §2.3 · EA-PLATFORM §24.3 | Melarutkan konflik brief vs ADR-014 tanpa revisi ADR paksa | Capability matrices BAB 4 (TARGET) / BAB 9 (PLATFORM) | — | Board-only (klarifikasi) | Draft (BOARD-008 R3) |
| DTM-D-021 | Modul tidak memanggil modul lain secara langsung; lewat EP (API/event terdaftar) | PRINCIPLE | EA-TARGET §2.2 | Hindari coupling lateral | Integration tables | H4 | POST G-HOST | Draft |
| DTM-D-022 | Kontrak wajib; SDK opsional | PRINCIPLE | EA-PLATFORM §24.3 #3 | Hindari platform bottleneck | SDK S1–S5 | H3 | POST G-HOST | Draft |
| DTM-D-023 | Penegakan di lapisan yang tidak dapat dilewati (repo scope, arch tests, contract tests) | PRINCIPLE | EA-PLATFORM §24.3 #2 | Pelajaran data-scope opsional = nol pakai | Audit findings | — | Mode A OK (tests) | Draft |
| DTM-D-024 | HOST side = permintaan kapabilitas bilateral, bukan perintah sepihak modul | PRINCIPLE | EA-PLATFORM BAB 0 | Tanpa EP co-owner = “enterprise palsu” | BAB 0 · BOARD-008 §4 | H1 | Board-only | Draft |
| DTM-D-025 | Platform v1.0 butuh validasi modul kedua berbeda karakter | GATE | EA-PLATFORM BAB 23 | Satu modul ≠ generalitas | H10 | H10 | Board-only | Draft |
| DTM-D-026 | Capability tanpa pemilik tidak boleh diimplementasikan siapa pun | PRINCIPLE | EA-PLATFORM ownership rules | Hindari orphan capability | Capability Registry usulan | H1 | Board-only | Draft |

---

## 4. Matrix — keputusan desain modul (EA-TARGET-CM-001)

| DTM-ID | Statement | Class | Source | Rationale | Evidence | HOST dep. | Impl. posture | Status |
|---|---|---|---|---|---|---|---|---|
| DTM-D-040 | Modular monolith + hexagonal ports/adapters; satu deployable | DESIGN | EA-TARGET BAB 6 | Tim kecil; konsistensi aggregate; ADR-009 | Struktur target `ports/`/`adapters/` | K11 | POST C-7 (enterprise adapters); Mode A boleh refine domain | Draft |
| DTM-D-041 | Divergensi Mode A/B hanya di `adapters` + `bootstrap` | DESIGN | EA-TARGET §6.3 D6 | Hedge tanpa mencemari domain | — | — | Mode A OK (struktur) | Draft |
| DTM-D-042 | Domain murni: tidak import framework/ORM/HTTP | DESIGN | EA-TARGET D1–D5 | Testability & boundary | Pola `complaint/domain` existing | — | Mode A OK | Draft |
| DTM-D-043 | Tiga implementasi port: enterprise / standalone / inmemory; prod fail-closed | DESIGN | EA-TARGET §6.4 | CI + Mode A hedge + Mode B | Customer provider pattern | H* related port | POST C-7 (enterprise) | Draft |
| DTM-D-044 | FE: shell/theme/auth UI milik HOST; business features milik modul; `platform/` ACL | DESIGN | EA-TARGET BAB 7 | Anti-corruption UI | `features/**` dipertahankan | F1–F4, H2, H5 | POST G-HOST ∩ C-7 | Draft |
| DTM-D-045 | DB: hanya tabel domain keluhan + ref cache read-only; hapus users/tokens/branches master di Mode B | DESIGN | EA-TARGET BAB 8 | Kepemilikan data | 33 tables as-is (fakta) | H7, C-B6-3 | POST C-7 | Draft |
| DTM-D-046 | Ref cache: opaque refs, no cross-ownership FK, stale → fail-closed | DESIGN | EA-TARGET §8.3 | Hindari SoR siluman | ADR-018 | H7, K4 | POST C-7 | Draft |
| DTM-D-047 | Event catalog existing = kontrak keluar modul; consumer idempotent | DESIGN | EA-TARGET BAB 10 · events.yaml | Jangan invent event di luar katalog | EVT-CAT-001 Approved | H4, K6 | Mode A OK (publish path lokal); bus = POST G-HOST | Draft |
| DTM-D-048 | Notification: modul punya *intent*; HOST punya delivery | DESIGN | EA-TARGET §2.3 · matrix #9–10 | Capability vs meaning | Notification LOC fakta | K8 | POST G-HOST ∩ C-7 | Draft |
| DTM-D-049 | Authorization dalam modul = Permission Matrix lokal; entitlement ke modul = HOST | DESIGN | EA-TARGET matrix #2–3 · ADR-008/014/017 | AuthN ≠ AuthZ | PermissionResolver; RoleMapper | H6, K3 | POST C-7 (entitlement); matrix Mode A OK | Draft |
| DTM-D-050 | Queue/Appointment ownership pending Q1/Q3 | DESIGN | EA-TARGET §3.4 | Hindari salah tempat 5k+ LOC | BUTUH INFO | H1 (case/ticket generik) | Board-only sampai Closed | Draft / Open |
| DTM-D-051 | Target roadmap Sprint 1–6 = usulan; bukan backlog sampai G-HOST∧G-ORG∧G-OWN∧G-C7 | GATE | EA-TARGET BAB 18 (amended) · BOARD-008 | Anti-skip | Board pack §4 | All H*/K*/F* | Blocked | Draft binding rec. |
| DTM-D-052 | Hapus ~platform modules (auth/users/iam/…) hanya setelah Mode B cutover | DESIGN | EA-TARGET §3.3 · Sprint 4 | Mode A hedge masih butuh | LOC table | G-C7 + G-HOST | POST C-7 | Draft |

---

## 5. Matrix — HOST open items (operasional)

Salinan ringkas register BOARD-008 §4. Update status di sini saat EP menjawab.

| Code | Topic | Status | Closed evidence | Blocks DTM-ID (contoh) |
|---|---|---|---|---|
| H1 | Model ekstensi EP existing? | Open | | D-024, D-026, D-050 |
| H2 / K5 / F2 | Framework host | Open | | D-044, D-008 |
| H3 | Module Registry roadmap | Open | | D-022 |
| H4 / K6 | Event bus + DLQ | Open | | D-012, D-047 |
| H5 / F1 | Embed UI method | Open | | D-044 |
| H6 / K3 | Entitlement mechanism | Open | | D-006, D-049 |
| H7 / K4 | Org model + API | Open | | D-007, D-045, D-046 |
| H8 / K9 | Observability sink | Open | | — |
| H9 / K1–K2 | Token sample + OIDC params | Open | | D-004, D-005 |
| H10 | Second module validator | Open | | D-025 |
| K7 | File service API | Open | | D-048-like storage |
| K8 | Notification contract | Open | | D-048 |
| K10 / F4 | Manifest format | Open | | D-044 |
| K11 | Deployment shape | Open | | D-040 |
| F3 | Design system contract | Open | | D-044 |
| C-B6-3 | Org-gap evidence | Open / in plan | Org-gap delivery plan Draft | D-002, D-007 |

---

## 6. Coverage map (dokumen → DTM)

| Document | DTM rows (primary) |
|---|---|
| ADR-014…018, ADR-002, ADR-009, ADR-013 | D-001…D-012 |
| BOARD-004 / 006 / 008 | D-002, D-003, D-051 |
| DEC-020 | D-009, D-010 |
| EA-PLATFORM-001 | D-020…D-026; H* |
| EA-TARGET-CM-001 | D-020, D-040…D-052; K*/F* |

---

## 7. Change control

| Event | Action |
|---|---|
| Board Accept/Amend ADR | Tambah/ubah baris Class=ADR; link resolution |
| EP menutup H*/K*/F* | Update §5 Status + Evidence; set Impl. posture terkait dari Blocked → POST C-7 jika C-7 juga terbuka |
| Mode B unlock Resolution | Update D-002; jangan menghapus sejarah |
| Design change di EA draft | Baris DESIGN baru atau amend; bump EA version |
| Implementation selesai | Tambah Evidence (PR/test ID); jangan ubah Statement tanpa Board |

---

## 8. Explicit non-goals of DTM-001

- Bukan backlog sprint
- Bukan pengganti OpenAPI / Event Catalog / RTM
- Bukan Mode B authorization
- Tidak menginvent Acceptance Board untuk ADR

---

## 9. Revision

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Initial matrix for BOARD-008 pack; HOST register all Open |
