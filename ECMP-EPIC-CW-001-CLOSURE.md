# EPIC-CW-001 — Closure Report

| Field | Value |
|---|---|
| Document ID | ECMP-EPIC-CW-001-CLOSURE |
| Type | Delivery retrospective & future-EPIC reference |
| Project | ECMP |
| Module | Complaint Module |
| Epic | EPIC-CW-001 — Case Workspace Experience (CWX) |
| Date | 2026-08-03 |
| Classification | **Not** a constitution · **Not** an ADR · **Not** Board Resolution |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → GOV-001 → CWX chain |

---

## 1. Executive Summary

EPIC-CW-001 mendefinisikan dan mengirimkan **Case Workspace Experience** untuk Complaint Module Mode A: bagaimana petugas memahami konteks Case, mengambil aksi legal, dan membaca riwayat operasional — tanpa mengubah domain bisnis, Dual-SoT, atau membuka Mode B.

Rantai pengalaman **CWX-000 → M1 → M2 → M3 → M4 → CWX-R** telah dijalankan. Capability berstatus **READY** di-compose di atas Foundation (`/api/v1/complaints`) dan Aggregate (`/api/v1/cm`). Capability **BLOCKED** (Conversation, Notes, Decision Notes, Aggregate Activity Feed, Audit Summary) **tidak** diimplementasikan — sesuai gate governance.

**Verdict penutupan:** EPIC-CW-001 **dapat ditutup** untuk ruang lingkup pengalaman Case Workspace Mode A yang READY, dengan residual hygiene (artefak living M4, merge/commit FE) tercatat di §10–§11 — bukan sebagai utang domain.

---

## 2. Business Objective

Memungkinkan petugas menyelesaikan kerja Case lebih cepat dan lebih yakin dengan menjawab, berurutan:

1. **Apa kasus ini?** (identitas & konteks ringkas)
2. **Apa yang sedang terjadi?** (status operasional / kerja saat ini)
3. **Apa yang boleh saya kerjakan sekarang?** (aksi legal)
4. **Apa yang sudah terjadi?** (riwayat operasional)

Tanpa meninggalkan Workspace, tanpa admin-form sprawl, dan tanpa mengubah aturan bisnis Complaint.

---

## 3. Architecture Objective

Menjaga North Star ECMP:

> Selesaikan Complaint Management Module dengan arsitektur yang benar, sehingga ketika pintu Enterprise terbuka yang berubah hanya mekanisme integrasi — bukan domain bisnis.

Implikasi arsitektur yang ditegakkan di EPIC ini:

- CWX = **experience layer** (presentasi & komposisi), bukan SoR baru
- **Compose, never fork** native capability (attachment, timeline, resolution, dialogs)
- **Parent owns SoT**; shell anak tidak fetch / mutate / branch SoT
- **DEC-020 Dual-SoT** utuh (Foundation ≠ Aggregate; no silent merge)
- Mode B / SSO / Identity Adapter tetap **CLOSED**

---

## 4. Completed Milestones

| Milestone | Judul | Peran | Status penutupan |
|---|---|---|---|
| **CWX-000** | Case Workspace Experience Constitution | Batas produk, Golden Rules, Dual-SoT, living artifacts | 🔒 LOCKED · living di `docs/governance/ECMP-CWX-000.md` |
| **CWX-M1** | Experience Foundation | Context Header, Decision Bar, Context-Aware Layout, progressive levels | Spek LOCKED · FE shells + wiring Mode A |
| **CWX-M2** | Operational Context | Current Work, Case/Customer summary, badges, derive helpers | Spek LOCKED · FE derive + panels |
| **CWX-M3** | Working Surface | Evidence Surface, Working Actions Area; BLOCKED Conversation/Notes/Decision Notes | Spek LOCKED · FE compose Evidence + Working Actions |
| **CWX-M4** | Operational History | History Shell, Navigation, Activity Feed (Foundation), Decision History; Audit gate | Delivery READY slices selesai · Audit **BLOCKED** · living `docs/governance/ECMP-CWX-M4.md` 🔒 LOCKED |
| **CWX-R** | Review Checklist | Functional · Cognitive · Consistency gate sebelum surface DONE | 🔒 LOCKED · `docs/governance/ECMP-CWX-R.md` |

### Ringkas hasil per milestone (delivery)

| Milestone | Delivered (READY) | Explicitly not delivered |
|---|---|---|
| M1 | Header · Decision Bar · Layout · dual-SoT wire | Customer History content · Mode B chrome |
| M2 | Operational Context Block · badges · next-action labels | Conversation · Notes · Timeline redesign |
| M3 | Evidence compose · Working Actions compose | Conversation · Internal Notes · Decision Notes |
| M4 | History Shell · Nav · Foundation Activity (`TimelineCard`) · Decision History (Foundation resolution · Aggregate `resolutionHistory`) | Aggregate Activity Feed · Audit Summary · CAP-010 merge · Timeline redesign |
| R | Checklist evaluasi surface READY | Bukan fitur runtime |

---

## 5. Major Decisions

| Decision | Meaning in this EPIC |
|---|---|
| **Case is the Product** | Workspace Case adalah unit kerja; Queue hanya entry |
| **Queue is Entry** | Kembali ke Queue tanpa kehilangan identitas Case |
| **Compose Never Fork** | Bungkus capability native; jangan parallel tree / port `implementation/` |
| **Parent Owns SoT** | Detail view memilih Foundation vs Aggregate; shell tidak branch |
| **Child Owns Lifecycle** | Kartu/dialog native tetap pemilik fetch/submit/lifecycle masing-masing |
| **Zero Duplicate Context** | Jangan ulangi fakta Header/M2 di History/Evidence sebagai “source kedua” |
| **Reference Don't Redefine** | BR/API/ADR dirujuk; CWX tidak menulis ulang domain |
| **Dual-SoT preserved** | Asimetri Foundation/Aggregate dihormati (termasuk Feed Aggregate BLOCKED) |
| **READY only / BLOCKED stay dark** | Matriks capability lebih kuat daripada “parity vanity” |
| **Presentation shells** | Surface = landmark + framing + children; no business rules in shell |

---

## 6. Architecture Decisions That Proved Correct

1. **Shell presentasi + children** (M3 Evidence / Working Actions → M4 History/Feed/Decisions) mencegah rewrite TimelineCard dan attachment cards.
2. **Controlled History Navigation** (`value` / `onChange`, no URL) menjaga History sebagai state UI lokal, bukan routing product baru.
3. **Menyembunyikan tab Audit** saat sumber tidak READY menghindari fake compliance UI.
4. **Aggregate Activity Feed jujur BLOCKED** mencegah pelanggaran Dual-SoT (tidak memanggil API-209 dari Case Aggregate).
5. **Decision History dari data existing saja** (resolution / `resolutionHistory`) mencegah Decision Notes / synthetic events.
6. **Pemisahan Decision Bar (aksi) vs Decision History (baca)** menjaga M1 entry tetap kanonis.
7. **Gate Commit 4 Audit** (“tanpa API call baru / data sudah di parent”) menghentikan creep client audit spekulatif.

---

## 7. Decisions Intentionally Deferred

Bukan kegagalan delivery — **keputusan sadar** menunggu Board / ADR / kontrak sumber:

| Item | Alasan defer |
|---|---|
| **Audit Summary** | FE Mode A tidak punya client/payload audit existing; API-336/337 ada di katalog tetapi Commit 4 gate = no new API calls → **BLOCKED** (2026-08-03) |
| **Conversation** | Tidak ada kontrak Dual-SoT Mode A untuk thread komunikasi |
| **Internal Notes** | Notes FR-007 / UI hanya di case-service `implementation/`; bukan Mode A CWX |
| **Decision Notes** | Tidak ada FR/BR/ADR entitas Decision Notes |
| **Aggregate Activity Feed** | Tidak ada timeline API Mode A pada `/api/v1/cm` |
| **CAP-010 timeline merge** | Canonical Feed Foundation = API-209; merge butuh AD terpisah |
| **Customer History slot content** | Slot M1 tetap placeholder; Customer Master / BR-010 OOS |
| **Mode B / SSO / Identity Adapter** | Board C-7 / C-B6-1 CLOSED |
| **Timeline redesign / storage** | M4 = compose presentation only |
| **Living CWX-M4.md LOCK write-back** | **Resolved 2026-08-03** — `docs/governance/ECMP-CWX-M4.md` + mirror `18 Architecture Governance/ECMP_CWX_M4_Operational_History_v1.0.md` |

---

## 8. Lessons Learned

### Technical

- Wrapper presentasi + parent ownership menskala lebih aman daripada “feature panel” yang fetch sendiri.
- Asimetri Dual-SoT harus dirancang di UX (hide / empty jujur), bukan diseragamkan palsu.
- Retensi payload dari fetch yang sudah ada (mis. resolution) cukup untuk History tanpa API baru — jika fetch belum ada, jangan pura-pura READY.

### UX

- Progressive disclosure (level layout M1 + tabs History M4) menjaga kasus sederhana tetap sederhana.
- Empty state jujur lebih baik daripada placeholder keputusan/audit.
- CWX-R #9 (Activity Feed) hanya dapat dievaluasi penuh di Foundation; Aggregate harus dikecualikan secara eksplisit.

### Governance

- Matriks READY/BLOCKED di spek M3/M4 efektif mencegah scope creep.
- Anti-skip (Mode B, invent API) harus diingat di setiap commit prompt.
- Living artifact LOCK di `docs/governance/` harus mengikuti PASS review — jangan hanya mengklaim LOCKED di prompt.

### Delivery

- Commit slicing (shell → feed → decisions → audit conditional) memudahkan stop-on-BLOCKED tanpa merusak slice sebelumnya.
- “Do not commit until Architecture Review” menjaga review gate, tetapi menghasilkan utang merge/process (lihat §10) — proses release perlu explicit land-to-main setelah PASS.

---

## 9. Reusable Patterns

Untuk EPIC pengalaman berikutnya (bukan domain baru):

| Pattern | Deskripsi singkat | Contoh CWX |
|---|---|---|
| **Presentation Shell** | `<section>` + title/aria + optional heading + children | Evidence, Working Actions, History, Feed, Decisions |
| **Controlled Navigation** | Parent state; no route/query persistence | `CwxHistoryNavigation` |
| **Progressive Disclosure** | Complexity by level / tab / disclosure | Context-Aware Layout levels; History tabs |
| **Operational Context** | Derive display fields from existing case/complaint props | `deriveOperationalContext` |
| **Working Surface** | Aksi legal di area kerja; Decision Bar = entry | M3 Working Actions |
| **Operational History** | Shell + nav + surfaces baca saja | M4 |
| **READY/BLOCKED matrix** | Capability table sebelum coding | M3/M4 specs |
| **Compose never fork** | Reuse native card/dialog/timeline | `TimelineCard`, attachments, resolve dialogs |
| **Honest empty / hide** | No fake parity across Dual-SoT | Aggregate Feed · Audit tab |

---

## 10. Technical Debt

**Hanya utang teknis/proses nyata.** Deferred scope (§7) **bukan** technical debt.

| ID | Debt | Severity | Notes |
|---|---|---|---|
| TD-1 | Sebagian besar artefak FE CWX (M1–M4) masih **uncommitted / belum land** ke baseline git bersama (hanya sebagian shell M3 tercatat di history) | Medium | Process debt — butuh PR land setelah Architecture Review PASS |
| TD-2 | ~~Living `ECMP-CWX-M4.md` missing~~ | — | **Resolved 2026-08-03** (backfill LOCKED) |
| TD-3 | ~~Metadata M3 “NOT STARTED”~~ | — | **Resolved 2026-08-03** (Implementation: DELIVERED READY) |
| TD-5 | Aggregate History Navigation masih menampilkan tab **Activity** meski Feed BLOCKED (konten kosong jika dipilih); Audit sudah di-hide | Low | Hygiene UX — sarankan hide Activity tab Aggregate (parity dengan Audit), tanpa invent feed |
| TD-4 | Foundation Decision History saat ini menampilkan **resolution existing** saja (assignment/escalation history tidak digabung sebagai list keputusan terpisah) | Low | Bukan invent — perlu AD jika ingin memperluas sumber keputusan tanpa API baru |

**Bukan debt:** Audit Summary, Conversation, Notes, Mode B, Aggregate Feed — itu **deferred scope**.

---

## 11. Backlog (requires Board / ADR)

| Candidate | Prerequisite |
|---|---|
| Audit Summary Mode A (compose API-336/337) | AD: izinkan FE read client; bukti filter entity + `audit:read`; Audit ≠ Timeline |
| Conversation di Case Workspace | Kontrak Dual-SoT + API/entity komunikasi |
| Internal Notes Mode A | Keputusan SoT Notes (bukan port diam-diam dari case-service) |
| Decision Notes | FR/BR/ADR entitas baru — atau tolak permanen |
| Aggregate Activity Feed | Timeline/event kontrak `/api/v1/cm` atau AD eksplisit |
| CAP-010 ↔ API-209 strategy | Architecture Decision (jangan silent merge) |
| Customer History content | BR-010 / non–Customer-Master display rules |
| Mode B embed / SSO / Identity Adapter | Board unlock (C-7 / C-B6-*) + org-gap evidence |
| UI cutover Foundation→Aggregate | Retirement DEC (DEC-020) — bukan CWX experience EPIC |

---

## 12. Metrics

| Metric | Value |
|---|---|
| Milestones in chain | **6** (CWX-000, M1, M2, M3, M4, CWX-R) |
| Planned M4 delivery commits | **4** (Shell · Activity · Decisions · Audit) |
| M4 commits executed | **3 delivered + 1 BLOCKED (Audit)** |
| Git commits explicitly tagged CWX (recorded at closure) | **2** (`Evidence Surface`, `Working Actions Area` shells) — banyak FE CWX masih working tree |
| Capabilities **delivered** (READY, Mode A) | Context Header · Decision Bar · Layout · Operational Context · Evidence · Working Actions · History Shell · History Nav · Foundation Activity Feed · Decision History (Foundation + Aggregate) |
| Capabilities **deferred / BLOCKED** | Audit Summary · Aggregate Activity Feed · Conversation · Internal Notes · Decision Notes · Customer History content · Mode B · CAP-010 merge · Timeline redesign |
| Dual-SoT violations introduced | **0** (by design gates) |
| Backend / OpenAPI / DB changes in this EPIC | **0** (experience-only) |

---

## 13. Recommendation

### **YES — close EPIC-CW-001**

**Alasan:**

1. Tujuan bisnis & arsitektur Case Workspace Experience Mode A untuk capability **READY** telah tercapai tanpa merusak domain atau Dual-SoT.
2. Rantai milestone CWX-000 → R selesai sebagai kerangka; M4 READY slices (History, Foundation Feed, Decision History) terkirim; Audit dihentikan dengan benar saat gate FAIL.
3. Deferred items terdokumentasi sebagai backlog Board/ADR — bukan “setengah fitur” yang mengotori modul.
4. Menahan EPIC terbuka hanya untuk Audit/Conversation/Mode B akan mencampur pengalaman CWX dengan platform unlock — bertentangan dengan konstitusi modul.

**Kondisi penutupan (bukan blocker konsep, wajib follow-up proses):**

1. Land FE CWX + governance chain ke baseline setelah Architecture Review PASS (selesaikan TD-1) — **pisahkan** dari redesign dashboard/settings/reports non-CWX di working tree yang sama.
2. ~~Tulis/LOCK living `ECMP-CWX-M4.md`~~ — **done** (TD-2).
3. ~~Sync metadata M3~~ — **done** (TD-3).
4. Opsional hygiene: hide Aggregate Activity tab (TD-5).
5. Backlog §11 masuk antrean governance — **EPIC baru** bila dikerjakan (jangan diam-diam lanjut di bawah CW-001).

---

**EPIC-CW-001: CLOSED (READY scope) · Deferred scope tracked · No code in this document.**

**STOP.**
