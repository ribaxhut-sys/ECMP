# DRR-000 — Decision Readiness Review

| Field | Value |
|---|---|
| Document ID | DRR-000 |
| Title | Decision Readiness Review & Resolution (atas DL-000) |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | Draft — hasil review; **addendum G0.2D** mencatat disposisi Business Owner P1 (2026-08-05) |
| Milestone | Governance Phase 0 — G0.2B / G0.2D |
| Input | `docs/governance/DL-000-Decision-Log.md` (DL-001 … DL-065) |
| Subordination | Board Resolution → ADR → EA Documents → ECMP-CONSTITUTION-001 → DL-000 → **DRR-000** |
| Does not | Mengubah keputusan asli · memodifikasi DL-000 · membuat BC-000 · menyelesaikan konflik secara otomatis |

---

## 1. Metodologi

DRR-000 hanya menilai **kesiapan** setiap keputusan untuk diangkat ke BC-000. Isi keputusan tidak diubah, tidak ditafsir ulang, dan tidak digabung.

### 1.1 Definisi klasifikasi (setiap keputusan mendapat tepat satu)

| Status | Arti operasional dalam review ini |
|---|---|
| **APPROVED** | Berkas sumber menyatakan persetujuan penuh (`Approved` · `Accepted` · `LOCKED` · `CLOSED — approved option` · `PROGRAM CLOSED`), tanpa kondisi terbuka dan tanpa kontradiksi terdaftar |
| **APPROVED WITH CONDITIONS** | Sumber menyatakan `Accepted with Conditions` / `BASELINE + Accepted with Conditions`; kondisi (C-1, C-3, C-7, C-B6-1…7) **belum ditutup** |
| **PENDING** | Keputusan sudah ditulis tetapi jalur persetujuannya belum selesai (menunggu countersign / Accept) |
| **CONFLICT** | Bertentangan dengan keputusan lain, dengan kenyataan repositori, atau memuat inkonsistensi internal yang terdaftar |
| **SUPERSEDED** | Seluruh isinya digantikan keputusan lain |
| **DEPRECATED** | Efek normatifnya sudah habis (trigger terpenuhi / tidak lagi mengikat), berkas dipertahankan sebagai sejarah |

### 1.2 Aturan kelayakan BC-000

Diterapkan **dua saringan berurutan**:

1. **Saringan status** — hanya berstatus **APPROVED**. Ini pembacaan ketat dari Success Criteria G0.2B (*"generate BC-000 using ONLY the APPROVED decisions"*). Konsekuensinya: `APPROVED WITH CONDITIONS` **tidak** masuk BC-000 hari ini, termasuk seluruh rantai enterprise ADR-014…018.
2. **Saringan sifat** — keputusan harus menyatakan sesuatu yang **permanen tentang bisnis komplain**: lingkup, aktor, lifecycle, aturan, kepemilikan, atau kewajiban. Keputusan yang bersifat implementasi, sprint, gate, atau kesepakatan operasional sementara dikeluarkan meski berstatus APPROVED.

> **Catatan penting atas saringan 1.** Mengeluarkan ADR-014/015 dari BC-000 **tidak** menghilangkan batas "ECMP adalah modul, bukan aplikasi standalone" dari konstitusi — batas itu sudah dinyatakan **DL-046 (ECMP-CONSTITUTION-001, LOCKED, APPROVED)** §3 Target Architecture. BC-000 dapat mengambil batas tersebut dari DL-046 tanpa bergantung pada ADR yang kondisinya belum tertutup.

---

## 2. Deliverable 1 — Decision Readiness Report

### 2.1 Rekapitulasi status

| Status | Jumlah | Persentase | Decision ID |
|---|---|---|---|
| **APPROVED** | 51 | 78,5 % | DL-001…011, 015…036, 043, 044, 046…052, 056, 058…065 |
| **APPROVED WITH CONDITIONS** | 8 | 12,3 % | DL-013, 014, 039, 040, 041, 042, 045, 057 |
| **PENDING** | 1 | 1,5 % | DL-012 |
| **CONFLICT** | 4 | 6,2 % | DL-038, 053, 054, 055 |
| **SUPERSEDED** | 0 | 0 % | — |
| **DEPRECATED** | 1 | 1,5 % | DL-037 |
| **Total** | **65** | 100 % | |

### 2.2 Kelayakan BC-000

| Kategori | Jumlah |
|---|---|
| **BC-000 Eligible — YES** | **19** |
| BC-000 Eligible — NO | 46 |

Dari 51 keputusan berstatus APPROVED, **32 dikeluarkan oleh saringan sifat** (implementasi, sprint/gate, atau sementara), menyisakan 19 kandidat.

### 2.3 Temuan utama

1. **Basis konstitusi bisnis sudah cukup.** 19 kandidat mencakup lingkup bisnis (DL-002), aturan bisnis & baselinenya (DL-003…006, DL-019, DL-024), lifecycle (DL-023), kepemilikan (DL-025, DL-031, DL-056), persona & pengalaman (DL-001, DL-027), klasifikasi rule (DL-026), kewajiban audit (DL-063…065), dan konstitusi payung + kendali perubahan (DL-046, DL-047). Tidak ada kategori bisnis yang kosong.
2. **Seluruh rantai identitas enterprise tertahan di gerbang kondisi.** Delapan keputusan `APPROVED WITH CONDITIONS` semuanya terikat C-7 / C-B6-1 (Mode B CLOSED). Ini bukan cacat — ini status yang memang dikehendaki Board.
3. **Empat konflik struktural memerlukan disposisi**, dua di antaranya menyentuh isi bisnis (lingkup eskalasi dan audiens dashboard vs persona Manager), bukan sekadar kebersihan dokumen.
4. **Nol keputusan SUPERSEDED penuh** — yang ada adalah rantai supersession **parsial** (DL-002 → DL-007…011). Ini adalah jebakan terbesar bagi BC-000: mengutip DL-002 tanpa carve-out akan memasukkan pernyataan lingkup yang sudah tidak benar ke dalam konstitusi.
5. **Substansi UX belum matang secara governance.** Hanya DL-001 dan DL-027 yang layak; seluruh turunan (PDS-001 → WF-001-01) masih Draft, dan dokumen payungnya memuat status yang saling bertentangan (Konflik C-07).

### 2.4 Verifikasi yang dilakukan

Tiga dugaan konflik diverifikasi langsung ke repositori sebelum dicatat:

| Dugaan | Metode | Hasil |
|---|---|---|
| Status paket UX Foundation tidak konsisten | Baca `UX-FOUNDATION-000` baris 42, 52 vs 112–113 | **Terkonfirmasi** — §2 mencantumkan PWDM-001/IA-001 `READY FOR APPROVAL`, §6 menyatakan paket `DRAFT` dan status READY dicabut |
| Tidak ada DEC yang mengotorisasi Head Office escalation | `grep -l -i escalat "27 Project Decisions"/DEC-*.md` lalu baca bagian Decision tiap hasil | **Terkonfirmasi** — eskalasi hanya muncul sebagai *prasyarat* (mis. "against an `APPROVED` escalation"), tidak pernah sebagai lingkup yang diotorisasi |
| Register tabrakan ID DEC tidak konsisten secara internal | Baca `DEC_ID_Collision_Register_20260801.md` | **Terkonfirmasi** — `Action taken: documented only, no renumber` vs tabel opsi yang mendefinisikan Option A sebagai *renumber* |

---

## 3. Deliverable 2 — Decision Readiness Matrix

| Decision | Status | Reason | Action Required | BC-000 Eligible |
|---|---|---|---|---|
| DL-001 Merge persona | APPROVED | Keputusan UX Review eksplisit; merge sendiri tidak diperdebatkan | Setujui formal paket UX Foundation (PDS-001 dst.) agar turunannya ikut mengikat | **YES** |
| DL-002 Business Baseline SoT | APPROVED | DEC-001 Approved oleh ARB; masih menjadi baseline aktif | **Wajib dikutip bersama carve-out DL-007…011**; konsolidasikan pernyataan lingkup kumulatif | **YES** |
| DL-003 Skema ID `BR-0xx` | APPROVED | SoT ID aturan bisnis; tidak ada penentang | Pastikan BC-000 hanya mengutip `BR-0xx` | **YES** |
| DL-004 BR Baseline Defaults | APPROVED | Ditutup ARB dengan nilai baseline reversibel | Kutip sebagai **rujukan**, jangan inline angka (revisi BO via DEC) | **YES** |
| DL-005 Target SLA & NFR | APPROVED | Ditutup ARB, reversibel via DEC | Idem DL-004; perhatikan Konflik C-12 (SLA tidak berjalan di Mode A) | **YES** |
| DL-006 Multi-source/target complaint | APPROVED | DEC-018 Approved; model domain aktif | — | **YES** |
| DL-007 Appointment booking | APPROVED | DEC-007 Approved | Klausul "check-in out of scope" **sudah tidak berlaku** (DL-008) | NO — task-specific |
| DL-008 Appointment check-in | APPROVED | DEC-008 Approved | Klausul "completion out of scope" **sudah tidak berlaku** (DL-009) | NO — task-specific |
| DL-009 Appointment completion | APPROVED | DEC-009 Approved | Klausul "no-show out of scope" **sudah tidak berlaku** (DL-010) | NO — task-specific |
| DL-010 Customer no-show | APPROVED | DEC-010 Approved | — | NO — task-specific |
| DL-011 Final Resolution | APPROVED | DEC-011 Approved | Aturan bisnisnya (1 resolusi/complaint, tidak menutup case) sebaiknya diangkat ke katalog BR | NO — task-specific |
| DL-012 Escalation visibility (DEC-F4) | **PENDING** | Bisnis Locked oleh BO, tetapi berkas 🟡 Proposed & countersign Board belum tercatat | Countersign Architecture Board; naikkan status DEC-F4 | NO — unresolved |
| DL-013 Kepemilikan org | APPROVED WITH CONDITIONS | ADR-014 BR-009; C-1/C-3/C-7 terbuka | Tutup C-1; unlock Mode B terpisah | NO — kondisi terbuka |
| DL-014 Organization Sync | APPROVED WITH CONDITIONS | ADR-018 BR-013; C-B6-1…7 terbuka, gap org = prasyarat unlock | Tutup gap model organisasi (C-B6-3); Accept DEC-021/022 | NO — kondisi terbuka |
| DL-015 EBS-001 org-location | APPROVED | Keputusan tertulis & terimplementasi (Commit 1–7) | **Ratifikasi otoritas keputusan** — tidak ada baris tanda tangan BO/Board; PR belum dibuka | NO — Mode A implementation |
| DL-016 SLA deadline calculator | APPROVED | DEC-012 Approved | — | NO — implementation |
| DL-017 SLA breach detection | APPROVED | DEC-013 Approved | Lihat Konflik C-05 / C-12 | NO — implementation |
| DL-018 SLA → timeline | APPROVED | DEC-014 Approved | — | NO — implementation |
| DL-019 Penutupan bisnis CAP-006 | APPROVED | Business Decision Closure, FRD-005 LOCKED | 3 butir DEFERRED perlu DEC BO bila diaktifkan | **YES** |
| DL-020 CAP-006 Hybrid | APPROVED | ADR-CAP006-001 Accepted (B2-20) | — | NO — architecture mechanism |
| DL-021 CAP-006 runtime konseptual | APPROVED | ARC-CAP006-002 Accepted (B2-21) | Runtime konkret tetap Deferred (B2-22/24) | NO — architecture |
| DL-022 G1 Contract Freeze | APPROVED | DEC-006 Accepted (freeze) | — | NO — API contract |
| DL-023 Case State Machine O3 | APPROVED | DEC-BQ001 APPROVED oleh BO/Board | **Wajib dikutip beserta kualifikasi dual SoT** (Definition A vs B) | **YES** |
| DL-024 Mode A Case baseline | APPROVED | BQ-002…014 ALL LOCKED, residual ZERO | Tandai butir yang eksplisit "outside Mode A" (BQ-003/006) | **YES** |
| DL-025 Workflow Config SoT | APPROVED | ADR-008 §2 Accepted | — | **YES** |
| DL-026 Configuration-First | APPROVED | ADR-003 Accepted | — | **YES** |
| DL-027 CWX-000 | APPROVED | 🔒 LOCKED | — | **YES** |
| DL-028 Penutupan EPIC-CW-001 | APPROVED | Laporan penutupan diterima | — | NO — epic-specific |
| DL-029 WCAG 2.2 AA | APPROVED | OD-FE-009 CLOSED (working target) | Jangan naikkan menjadi klaim konformansi tanpa audit | NO — working target |
| DL-030 Event-driven integration | APPROVED | ADR-001 Accepted | — | NO — architecture |
| DL-031 ECMP bukan SoR pelanggan | APPROVED | ADR-002 Accepted | — | **YES** |
| DL-032 Stack backend | APPROVED | ADR-004 Accepted | — | NO — implementation |
| DL-033 Backend layering | APPROVED | ADR-005 Accepted | — | NO — implementation |
| DL-034 API versioning | APPROVED | ADR-006 Accepted | — | NO — implementation |
| DL-035 Broker deferral + outbox | APPROVED | ADR-009 + Addendum Accepted | Re-evaluasi saat trigger tersentuh | NO — implementation |
| DL-036 Baseline deployment | APPROVED | ADR-010 Accepted | PROD masih ditunda | NO — implementation |
| DL-037 Deferral frontend | **DEPRECATED** | Trigger ADR-011 sudah terpenuhi (G1 lulus, ADR-013 dibuat, screen spec ditulis); larangan "tidak ada frontend produk" tidak lagi mengikat | **Board mencatat status ADR-011 sebagai fulfilled/spent** — saat ini repositori masih menampilkannya sebagai Approved aktif | NO — deprecated |
| DL-038 Frontend stack ADR-013 | **CONFLICT** | ADR-013 (Vite/React Router) aktif, produksi berjalan Next.js 15 + React 19 (OD-FE-001 OPEN) | ADR stack terpisah oleh Architecture Board (BR-007 melarang supersession lewat dokumen FE) | NO — conflict |
| DL-039 ECMP Enterprise Business Module | APPROVED WITH CONDITIONS | ADR-014 BR-009; C-1/C-3/C-7 | Tutup kondisi; batas modul sementara diambil dari DL-046 | NO — kondisi terbuka |
| DL-040 Enterprise Identity Contract | APPROVED WITH CONDITIONS | ADR-015 BR-010; dinyatakan Bilateral Contract (C-3) tetapi counterparty belum terverifikasi | Peroleh kontrak nyata dari pemilik Enterprise Platform (Konflik C-10) | NO — kondisi terbuka |
| DL-041 Protocol & Binding | APPROVED WITH CONDITIONS | ADR-016 BR-011; C-B6-1…7 | — | NO — kondisi terbuka |
| DL-042 Entitlement Architecture | APPROVED WITH CONDITIONS | ADR-017 BR-012; representasi entitlement masih deferred | — | NO — kondisi terbuka |
| DL-043 Canonical trees | APPROVED | DEC-019 Approved | Counterparty Konflik C-01 | NO — CI/implementation |
| DL-044 Dual SoT & remapping | APPROVED | DEC-020 Approved oleh Board | **Retirement DEC belum ada** — dual SoT tanpa batas waktu | NO — implementation SoT |
| DL-045 Baseline FE + CI policy | APPROVED WITH CONDITIONS | FE-CI-POL-001 Accepted with Conditions | Tidak boleh dipakai sebagai bukti Mode B Accepted | NO — kondisi terbuka |
| DL-046 ECMP-CONSTITUTION-001 | APPROVED | 🔒 LOCKED, subordinat pada Board/ADR | **Jadikan tulang punggung BC-000** | **YES** |
| DL-047 GOV-001 kategori delivery | APPROVED | 🔒 LOCKED | Masukkan sebagai **klausul kendali perubahan**, bukan pasal bisnis | **YES** |
| DL-048 Board-004 | APPROVED | Resolution sah | Dikutip sebagai **rantai otoritas**, bukan isi | NO — authority reference |
| DL-049 Board-006 | APPROVED | Resolution sah | Idem | NO — authority reference |
| DL-050 Otorisasi build G0 | APPROVED | DEC-002 Approved | — | NO — sprint-specific |
| DL-051 G2 Mini-Gate | APPROVED | Exited untuk Mode A lab | — | NO — gate-specific |
| DL-052 CAP-008 PROGRAM CLOSED | APPROVED | ARB PROGRAM CLOSED | — | NO — program-specific |
| DL-053 DEC ID collision | **CONFLICT** | Register menyatakan `CLOSED — Board Option A` + "documented only, no renumber", sementara Option A pada berkas yang sama berarti *renumber* | Klarifikasi Board: opsi mana yang sesungguhnya diambil | NO — conflict |
| DL-054 AuthN slice (ADR-007) | **CONFLICT** | Relasi ADR-007 ↔ ADR-012 dinyatakan **Pending** oleh Board (C-B6-6); dua model AuthN hidup berdampingan tanpa disposisi | Board memutuskan relasi (supersede / koeksistensi berfase) | NO — conflict |
| DL-055 Target AuthN (ADR-012) | **CONFLICT** | Idem — pasangan dari C-B6-6 | Idem | NO — conflict |
| DL-056 Role-Permission SoT | APPROVED | ADR-008 §1 Accepted | — | **YES** |
| DL-057 Larangan local auth Mode B | APPROVED WITH CONDITIONS | Bagian ADR-014 (BR-009) | Berlaku hanya saat Mode B aktif | NO — kondisi terbuka |
| DL-058 Lab auth local JWT | APPROVED | Ops working agreement Accepted | Bersifat sementara sampai runbook migrasi SSO | NO — temporary/ops |
| DL-059 Pintu auth Mode A→B | APPROVED | Ops working agreement Accepted | Prinsipnya sudah tercakup DL-046 | NO — temporary/ops |
| DL-060 KPI Foundation | APPROVED | DEC-015 Approved | Prinsip "KPI bukan SoT kedua" sebaiknya diangkat sebagai pasal via DL-031/DL-026 | NO — implementation |
| DL-061 Dashboard API | APPROVED | DEC-016 Approved | — | NO — implementation |
| DL-062 Penutupan bisnis CAP-007 | APPROVED | Business closure, FRD dikunci | Audiens v0.1 Supervisor-only → lihat Konflik C-09 | NO — v0.1 sementara |
| DL-063 Write-audit wajib | APPROVED | OQ-007 Resolved oleh BO | Catat bahwa read-audit masih ditunda | **YES** |
| DL-064 Audit immutable + override | APPROVED | ADR-003 + DEC-004 | — | **YES** |
| DL-065 Audit role/workflow config | APPROVED | ADR-008 §3 Accepted | — | **YES** |

---

## 4. Deliverable 3 — Conflict Register

Dua belas konflik terdaftar. **Tidak satu pun diselesaikan di dokumen ini.** Kolom "Disposisi diminta" adalah usulan jalur, bukan keputusan.

---

### C-01 — ADR stack frontend vs tree produksi *(obsolete ADR)*

| Field | Isi |
|---|---|
| **Jenis** | ADR usang vs kenyataan repositori |
| **Pihak** | DL-038 (ADR-013: React 18 + Vite + React Router → `implementation/frontend`) ⟷ DL-043 (DEC-019: `frontend/` kanonik) |
| **Bukti** | Produksi berjalan **Next.js 15 + React 19 + Tailwind + Axios** dari `frontend/`; `docs/frontend/OPEN_DECISIONS.md` OD-FE-001 **OPEN** |
| **Penjelasan** | Dua keputusan sama-sama Approved dan sama-sama berlaku, tetapi menyebut stack yang berbeda untuk hal yang sama. Board (BR-007) menyatakan ADR-013 **tetap aktif** dan **melarang** supersession lewat dokumentasi frontend — sehingga konflik ini tidak dapat ditutup oleh FE-ARCH/FE-STD. Akibatnya `21 Technical Standards` tidak dapat menyatakan satu "standar stack frontend". |
| **Dampak BC-000** | Rendah — stack bukan materi konstitusi bisnis. Tinggi untuk CI, rilis, dan standar teknis. |
| **Disposisi diminta** | Architecture Board — ADR stack terpisah (Opsi A pada OD-FE-001) |

---

### C-02 — Dua model autentikasi tanpa relasi formal *(conflicting ownership)*

| Field | Isi |
|---|---|
| **Jenis** | Duplikasi/tumpang tindih kepemilikan keputusan |
| **Pihak** | DL-054 (ADR-007 dev token) ⟷ DL-055 (ADR-012 OIDC target) — dan keduanya terhadap DL-039 (ADR-014 AuthN enterprise) |
| **Bukti** | Board-006 **C-B6-6**: relasi ADR-007 / ADR-012 **tetap Pending**; brief disposisi `ECMP_PROGRAM_BOARD_007_ADR007_012_Relationship_Disposition_Brief_v0.1.md` masih v0.1 |
| **Penjelasan** | Tiga lapis autentikasi hidup bersamaan tanpa pernyataan mana yang menggantikan mana dan kapan. ADR-012 mempertahankan dev-token untuk DEV/CI, tetapi tidak dinyatakan apakah ADR-007 tersupersede, terbatas, atau berlapis. Kekosongan ini yang membuat DL-054/DL-055 tidak dapat diklasifikasi APPROVED bersih. |
| **Dampak BC-000** | Rendah langsung — mekanisme auth bukan materi bisnis. Tinggi untuk kesiapan Mode B. |
| **Disposisi diminta** | Architecture Board — naikkan BOARD-007 dari v0.1 ke resolusi |

---

### C-03 — Tabrakan ID DEC dan inkonsistensi registernya *(duplicate rules)*

| Field | Isi |
|---|---|
| **Jenis** | Duplikasi identitas dokumen + inkonsistensi internal register |
| **Pihak** | DL-053; menyentuh keterbacaan DL-044, DL-051, DL-058 |
| **Bukti** | `DEC-020` dipakai dua berkas Accepted (SoT remapping · lab auth); `DEC-021` dipakai dua berkas berbeda status (O-06 **Proposed** · G2 mini-gate **Accepted**). Register: `Status: CLOSED — Board Option A`, `Action taken: Documented only — no renumber`, sementara tabel opsi mendefinisikan **Option A = renumber G2 → ID bebas berikutnya**. |
| **Penjelasan** | Dua pernyataan dalam satu berkas saling meniadakan: bila Option A benar-benar dipilih maka renumber seharusnya terjadi; bila tindakan yang diambil adalah "dokumentasi saja" maka yang dipilih sebenarnya bukan Option A. Selama ini tidak diklarifikasi, kutipan "DEC-021" tanpa kualifikasi tidak dapat dipercaya. |
| **Dampak BC-000** | Sedang — BC-000 harus mengutip DEC dengan path + judul, bukan ID saja |
| **Disposisi diminta** | Architecture Board — klarifikasi opsi yang berlaku, lalu eksekusi konsisten |

---

### C-04 — Dua definisi Case State Machine *(conflicting terminology)*

| Field | Isi |
|---|---|
| **Jenis** | Terminologi & model domain ganda (disengaja, tetapi belum punya rencana konvergensi) |
| **Pihak** | DL-023 — Definition A (`DOM-ECMF-003`: REGISTERED → ASSIGNED → IN_PROGRESS → PENDING_REVIEW → CLOSED → REOPENED) ⟷ Definition B (`BR-CM-CAT-001`: CREATED → ASSIGNED → IN_PROGRESS → PENDING/ESCALATED → RESOLVED → CLOSED + CANCELLED) |
| **Bukti** | DEC-BQ001 Option O3 (APPROVED) memilih **dual SoT eksplisit**; DL-044 melarang forced merge |
| **Penjelasan** | Ini konflik yang **sudah diputuskan untuk dibiarkan**, bukan kelalaian. Masalahnya bagi BC-000: kata "Case" berarti dua hal berbeda (intake case pada Definition A; child dari Complaint aggregate pada Definition B), sehingga konstitusi tidak dapat menulis satu kalimat lifecycle tanpa kualifikasi. Rencana konvergensi belum ada (tidak ada Retirement DEC — lihat C-06). |
| **Dampak BC-000** | **Tinggi** — BC-000 wajib menuliskan kedua definisi beserta ruang berlakunya |
| **Disposisi diminta** | Business Owner + Architecture Board — konfirmasi bahwa dualitas ini memang dikehendaki dalam konstitusi bisnis |

---

### C-05 — Dua jalur SLA berjalan paralel *(duplicate rules)*

| Field | Isi |
|---|---|
| **Jenis** | Duplikasi kapabilitas |
| **Pihak** | DL-016 / DL-017 / DL-018 (DEC-012/013/014 — kalkulator deadline, deteksi breach, event timeline, sudah berjalan) ⟷ DL-019 / DL-020 / DL-021 (CAP-006, FRD-005 LOCKED, runtime **Deferred**) |
| **Bukti** | BQ-CAP006-15: "Separate track ≠ CAP-006 fulfillment" |
| **Penjelasan** | Repositori memiliki dua mekanisme SLA: satu yang sudah dieksekusi di jalur lab, satu yang sudah dikunci secara bisnis tetapi runtime-nya belum diotorisasi. Keduanya dinyatakan **bukan** pemenuhan satu sama lain. Belum ada keputusan tentang apa yang terjadi pada jalur DEC-012/013 ketika runtime CAP-006 diaktifkan. |
| **Dampak BC-000** | Sedang — pernyataan SLA di BC-000 harus netral terhadap mekanisme |
| **Disposisi diminta** | Architecture Board — rencana konvergensi saat M-18 (runtime konkret) diputuskan |

---

### C-06 — Dual SoT tanpa Retirement DEC *(unresolved)*

| Field | Isi |
|---|---|
| **Jenis** | Keputusan yang mensyaratkan keputusan lanjutan yang belum ada |
| **Pihak** | DL-044, DL-023, DL-051, DL-052 |
| **Bukti** | DL-044: "cutover hanya lewat Decision"; DL-052 non-decision: "Retire dual SoT — No, needs Retirement DEC"; DL-046 Forbidden Behavior: "Force-merge / retire dual-SoT tanpa Retirement DEC" |
| **Penjelasan** | Tiga keputusan berbeda mensyaratkan Retirement DEC, dan Retirement DEC itu belum pernah dibuat. Akibatnya `/api/v1/complaints`, `/api/v1/cm`, dan Complaint CA BC hidup berdampingan tanpa horizon waktu. Ini bukan pelanggaran — tetapi merupakan kewajiban terbuka yang menggantung. |
| **Dampak BC-000** | Sedang — konstitusi akan mewarisi dualitas ini secara permanen bila tidak diberi batas |
| **Disposisi diminta** | Architecture Board — terbitkan Retirement DEC atau nyatakan dualitas permanen |

---

### C-07 — Status paket UX Foundation saling bertentangan *(repository inconsistency)*

| Field | Isi |
|---|---|
| **Jenis** | Inkonsistensi internal dokumen |
| **Pihak** | DL-001 dan seluruh turunan UX |
| **Bukti** | `docs/ux/UX-FOUNDATION-000-…md` baris 42 dan 52 mencantumkan PWDM-001 dan IA-001 berstatus **`READY FOR APPROVAL`**, sementara baris 112–113 menyatakan paket **`DRAFT — BUKAN READY FOR APPROVAL`** dan bahwa status READY sebelumnya **dicabut**. Berkas PWDM-001 dan IA-001 sendiri berstatus **Draft**. |
| **Penjelasan** | Satu dokumen payung menyatakan dua status berbeda untuk dua dokumen yang sama. Pembaca yang hanya membaca §2 akan menyimpulkan paket siap disetujui; yang membaca §6 menyimpulkan sebaliknya. Selama ini belum diperbaiki, tidak ada satu pun turunan UX (closed set persona, closed set destinasi/zona, backlog 21 wireframe) yang dapat diklaim mengikat. |
| **Dampak BC-000** | **Tinggi** — memblokir pengangkatan substansi UX apa pun selain DL-001 dan DL-027 |
| **Disposisi diminta** | UX Lead + Business Owner — sinkronkan §2 dengan §6, lalu jalankan Review paket |

---

### C-08 — Status "Head Office escalation" tidak pernah dicabut *(scope inconsistency)*

| Field | Isi |
|---|---|
| **Jenis** | Kekosongan otorisasi lingkup |
| **Pihak** | DL-002 (DEC-001) ⟷ DL-007…DL-011, DL-012, DL-017, DL-024 |
| **Bukti** | DEC-001 menempatkan **"Branch Officer / Head Office escalation / Schedule Slot / Appointment / Work Order"** di luar lingkup sampai revisi Blueprint. Penelusuran seluruh `27 Project Decisions/DEC-*.md` menemukan otorisasi eksplisit hanya untuk **Appointment** (DEC-007…010) dan **Final Resolution** (DEC-011). Tidak ada DEC yang mengotorisasi **eskalasi** itu sendiri — eskalasi hanya muncul sebagai *prasyarat* ("against an `APPROVED` escalation"). Sementara itu DEC-F4 mendefinisikan model eskalasi Cabang → Pusat, DEC-013 memakai tahap SLA `escalation`, dan Escalation Detail UI sudah ada. |
| **Penjelasan** | Kapabilitas eskalasi diperlakukan sebagai ada oleh banyak artefak, padahal pernyataan out-of-scope DEC-001 atasnya tidak pernah dicabut lewat DEC mana pun — berbeda dengan Appointment yang setiap langkahnya disupersede secara eksplisit. Ini kemungkinan besar celah pencatatan, bukan pelanggaran sengaja; tetapi konsekuensinya nyata: **BC-000 tidak dapat menyatakan lingkup bisnis eskalasi tanpa dasar keputusan.** |
| **Dampak BC-000** | **Tinggi** — menyentuh pernyataan lingkup inti (DL-002) |
| **Disposisi diminta** | **Business Owner** — terbitkan DEC yang mencabut/mengonfirmasi status eskalasi, atau tunjukkan otorisasi yang belum teridentifikasi review ini |

---

### C-09 — Persona Manager vs audiens dashboard *(conflicting ownership)*

| Field | Isi |
|---|---|
| **Jenis** | Konflik antara keputusan UX dan keputusan bisnis kapabilitas |
| **Pihak** | DL-001 / turunannya (Manager = satu-satunya persona level agregat; entry point **Dashboard**) ⟷ DL-062 (BQ-CAP007-04: **Approve Supervisor-only v0.1; Defer Manager/Executive**) |
| **Bukti** | `NAV-001` §1 Manager: `Login → Dashboard`; `IA-001` §4: "Zona primer Manager: Reference"; BQ-CAP007-04 menunda Manager/Executive |
| **Penjelasan** | Model persona menempatkan Dashboard sebagai satu-satunya rumah kerja Manager, sementara keputusan bisnis CAP-007 menetapkan dashboard v0.1 hanya untuk Supervisor dan menunda Manager. Dalam keadaan sekarang, persona Manager tidak memiliki permukaan kerja yang diotorisasi. Diperkuat oleh catatan PDS-001 bahwa **Manager belum punya padanan peran teknis** di Authorization. |
| **Dampak BC-000** | **Tinggi** — BC-000 tidak dapat menetapkan tiga persona sebagai closed set bila satu persona tidak punya kapabilitas maupun role |
| **Disposisi diminta** | **Business Owner** — tetapkan apakah Manager tetap dalam closed set persona meski kapabilitasnya ditunda |

---

### C-10 — Kontrak bilateral tanpa counterparty terverifikasi *(unresolved)*

| Field | Isi |
|---|---|
| **Jenis** | Kontrak sepihak yang dideklarasikan bilateral |
| **Pihak** | DL-040 (ADR-015 di bawah C-3 = **Bilateral Contract**) |
| **Bukti** | Repositori tidak memuat artefak dari aplikasi enterprise nyata: tidak ada issuer produksi, tidak ada spesifikasi entitlement/user directory/organisasi, tidak ada metode integrasi portal; seluruh referensi IdP menunjuk realm yang di-provision ECMP sendiri |
| **Penjelasan** | Sebuah kontrak dinyatakan bilateral oleh satu pihak saja. Selama pihak kedua belum mengonfirmasi, seluruh daftar claim wajib, semantik claim, dan aturan fail-closed adalah asumsi ECMP — akurat secara internal, belum tentu benar secara eksternal. |
| **Dampak BC-000** | Rendah hari ini (di luar BC-000 karena kondisi terbuka); **kritis** saat Mode B unlock dipertimbangkan |
| **Disposisi diminta** | Architecture Board + Business Owner — peroleh konfirmasi tertulis pemilik Enterprise Platform sebelum pekerjaan identitas dinilai atau dijadwalkan |

---

### C-11 — Status ADR-011 tidak mencerminkan kenyataan *(obsolete ADR)*

| Field | Isi |
|---|---|
| **Jenis** | ADR yang efeknya sudah habis tetapi masih tampil aktif |
| **Pihak** | DL-037 (ADR-011: "tidak ada frontend produk sampai trigger tersentuh") |
| **Bukti** | Trigger ADR-011 telah terpenuhi: G1 lulus, ADR stack frontend dibuat (ADR-013), screen spec `UX-SCR-001` ditulis, dan frontend produksi berjalan. Berkas ADR-011 tetap berstatus 🟢 Approved tanpa penanda fulfilled. |
| **Penjelasan** | Pembaca baru dapat menyimpulkan bahwa ECMP masih API-first dan frontend dilarang. Ini jenis kesalahan yang murah diperbaiki tetapi mahal bila dibiarkan masuk ke konstitusi. |
| **Dampak BC-000** | Rendah — sudah dikeluarkan dari kandidat |
| **Disposisi diminta** | Architecture Board — catat ADR-011 sebagai *fulfilled / spent* |

---

### C-12 — SLA berjalan vs "SLA tidak berjalan di Mode A" *(conflicting rules)*

| Field | Isi |
|---|---|
| **Jenis** | Aturan bisnis yang saling bertentangan antar jalur |
| **Pihak** | DL-024 (BQ-005: Case **SHALL** mengikat SLA Policy Version; **countdown SLA TIDAK diaktifkan** di Mode A — *bind-without-clock*) ⟷ DL-016 / DL-017 (deadline dihitung saat create, status dievaluasi menjadi `BREACHED` saat event terjadi) ⟷ DL-005 (target numerik SLA berlaku) |
| **Bukti** | BQ-005 LOCKED 2026-08-01; DEC-012/013 Approved 2026-07-23 dan berjalan di jalur lab |
| **Penjelasan** | Satu keputusan menyatakan jam SLA tidak berjalan di Mode A, keputusan lain sudah menghitung deadline dan menandai breach. Keduanya dapat dijelaskan sebagai berlaku pada **jalur implementasi yang berbeda** (Aggregate CAP-008 vs Foundation/lab) — dan penjelasan itu konsisten dengan dual SoT C-04/C-05 — tetapi **tidak ada keputusan yang menyatakan pemisahan itu secara eksplisit untuk SLA**. Bagi pembaca konstitusi, ini tampak sebagai dua aturan bisnis yang bertentangan tentang hal yang sama. |
| **Dampak BC-000** | **Tinggi** — SLA adalah materi bisnis inti yang pasti masuk konstitusi |
| **Disposisi diminta** | **Business Owner** — nyatakan secara eksplisit ruang berlaku masing-masing (per jalur SoT), atau selaraskan |

---

## 5. Deliverable 4 — Business Owner Review List

Keputusan/butir yang memerlukan persetujuan atau penegasan **eksplisit Business Owner**. Prioritas: **P1** = memblokir BC-000 · **P2** = memblokir kelengkapan konstitusi tetapi BC-000 tetap dapat disusun dengan kualifikasi · **P3** = dapat menyusul.

| # | Butir | Terkait | Kenapa BO | Prioritas |
|---|---|---|---|---|
| BO-01 | **Status lingkup eskalasi** — cabut atau konfirmasi status out-of-scope "Head Office escalation" pada DEC-001 | C-08, DL-002, DL-012 | Pernyataan lingkup produk adalah kewenangan BO (DEC-001 Approver: Business Owner) | **P1** |
| BO-02 | **Ruang berlaku aturan SLA** — apakah "SLA tidak berjalan di Mode A" (BQ-005) dan penghitungan deadline/breach (DEC-012/013) berlaku pada jalur berbeda | C-12, DL-005, DL-016, DL-017, DL-024 | Aturan SLA adalah aturan bisnis; revisi baseline SLA adalah kewenangan BO via DEC | **P1** |
| BO-03 | **Nasib persona Manager** — tetap dalam closed set tiga persona meski dashboard v0.1 Supervisor-only dan padanan role teknisnya belum ada | C-09, DL-001, DL-062 | Menentukan aktor bisnis modul | **P1** |
| BO-04 | **Persetujuan formal paket UX Foundation** (PDS-001 · PWDM-001 · IA-001 + turunan) setelah §2/§6 disinkronkan | C-07, DL-001 | Approver UX-001 adalah Business Owner | **P1** |
| BO-05 | **Konsolidasi lingkup kumulatif appointment** — pernyataan tunggal yang menggantikan pembacaan berantai DEC-001 → DEC-007…011 | DL-002, DL-007…011 | Menghindari pernyataan lingkup yang salah masuk BC-000 | **P1** |
| BO-06 | **DEC-F4** — selesaikan persetujuan formal DEC (berkas masih 🟡 Proposed) bersamaan countersign Board | DL-012, M-12 | Keputusan bisnis F4…F4.5 sudah di-lock BO di workshop; formalitasnya belum tertutup | **P2** |
| BO-07 | **Penegasan nilai baseline reversibel** (BR defaults DL-004 dan target SLA/NFR DL-005) untuk dikutip BC-000 sebagai rujukan | DL-004, DL-005 | Kewenangan revisi berada di BO via DEC baru | **P2** |
| BO-08 | **Butir DEFERRED CAP-006** — aktivasi kalender kerja, pause/resume, diferensiasi target per case type | DL-019, M-15…M-17 | Ketiganya eksplisit menunggu DEC Business Owner | **P2** |
| BO-09 | **Konfirmasi dualitas Case State Machine** sebagai keadaan yang dikehendaki dalam konstitusi bisnis | C-04, DL-023 | Menentukan bagaimana BC-000 menulis lifecycle | **P2** |
| BO-10 | **Read-audit** — pertahankan penundaan atau aktifkan | DL-063, M-22 | Kewajiban audit adalah materi kepatuhan bisnis | **P2** |
| BO-11 | **Dashboard Manager/Executive** dan kolom FR-030 | DL-062, M-26, M-27 | Ditunda oleh keputusan bisnis CAP-007 | **P3** |
| BO-12 | **OQ-001 Channel app** — fase 1 atau sekadar integration boundary | M-03 | Open sejak 2026-07-21, Owner: Business Owner, target TBD | **P3** |
| BO-13 | **Kebijakan di luar Mode A** — override maksimum 5 Case per Complaint (BQ-003) dan Assigned User (BQ-006) | DL-024, M-24, M-25 | Eksplisit dinyatakan "outside Mode A" | **P3** |
| BO-14 | **DEC-021 (O-06) dan DEC-022 (O-07)** — Accept atau revisi opsi | M-01, M-02 | Approver tercatat: Architecture Board **/ Business Owner** | **P3** (bersama Board) |

---

## 6. Deliverable 5 — Architecture Board Review List

| # | Butir | Terkait | Kenapa Board | Prioritas |
|---|---|---|---|---|
| AB-01 | **ADR stack frontend terpisah** — menutup OD-FE-001 tanpa men-supersede ADR-013 lewat dokumen FE | C-01, DL-038, DL-043 | BR-007 secara eksplisit menyerahkan ini ke Board | **P1** |
| AB-02 | **Relasi ADR-007 ↔ ADR-012** — naikkan BOARD-007 dari brief v0.1 menjadi resolusi | C-02, DL-054, DL-055 | Ditahan oleh kondisi Board sendiri (C-B6-6) | **P1** |
| AB-03 | **Klarifikasi register tabrakan ID DEC** — opsi mana yang sesungguhnya berlaku | C-03, DL-053 | Register menyatakan keputusan Board Option A yang bertentangan dengan tindakan yang dicatat | **P1** |
| AB-04 | **Retirement DEC untuk dual SoT** — atau pernyataan bahwa dualitas bersifat permanen | C-06, DL-044, DL-052 | Disyaratkan tiga keputusan sekaligus dan oleh Forbidden Behavior konstitusi | **P2** |
| AB-05 | **Penutupan kondisi C-1** (higiene canonical ADR Index) dan **C-B6-7** | DL-048, DL-049 | Kondisi wajib yang belum dinyatakan tertutup | **P2** |
| AB-06 | **Status ADR-011** — catat sebagai *fulfilled / spent* | C-11, DL-037 | Perubahan status ADR adalah kewenangan Board | **P2** |
| AB-07 | **Verifikasi bilateral ADR-015** — peroleh konfirmasi pemilik Enterprise Platform sebelum pekerjaan identitas dijadwalkan | C-10, DL-040 | C-3 menetapkan sifat bilateral; counterparty belum ada | **P2** |
| AB-08 | **Gap model organisasi (C-B6-3)** — prasyarat unlock Mode B; termasuk Accept DEC-021 (O-06) dan DEC-022 (O-07) | DL-014, M-01, M-02, M-14 | Prasyarat unlock yang ditetapkan Board sendiri | **P2** |
| AB-09 | **Ratifikasi otoritas EBS-001** — tidak ada baris persetujuan BO/Board pada berkas keputusan | DL-015 | Keputusan sudah diimplementasikan tanpa jalur persetujuan yang tercatat | **P2** |
| AB-10 | **Rencana konvergensi dua jalur SLA** saat runtime konkret CAP-006 diputuskan | C-05, DL-016…021, M-18 | Menyentuh arsitektur runtime dan FRD-005 LOCKED | **P2** |
| AB-11 | **`DEC-017` hilang** — konfirmasi nomor sengaja dilewati atau berkasnya hilang | M-33 | Integritas seri keputusan | **P3** |
| AB-12 | **Disposisi OD-FE-004 / 006 / 007** (Technical Standards, library platform, ADR infrastruktur) | M-06, M-08, M-09 | Tiga open decision berdisposisi *Move to ADR* / menunggu | **P3** |
| AB-13 | **Butir Deferred jangka panjang**: pemilihan broker (M-19), platform PROD (M-20), reopen + EVT-007 (M-21), observability penuh (M-30), integrasi Customer Master nyata (M-23) | DL-035, DL-036, DL-051 | Semua menunggu trigger yang ditetapkan Board/ADR | **P3** |
| AB-14 | **Resolution unlock Mode B** — hanya setelah AB-07, AB-08, dan kesiapan operasional | M-14, DL-039…042 | Ditetapkan sebagai resolusi terpisah oleh Board-006 F-4 | **P3** |

---

## 7. Deliverable 6 — BC-000 Candidate List

**19 keputusan** yang aman dimasukkan ke BC-000 hari ini. Semua berstatus **APPROVED** dan lolos saringan sifat. Kolom "Kualifikasi wajib" adalah syarat penulisan — bukan syarat kelayakan.

| # | DL | Judul | Peran usulan dalam BC-000 | Kualifikasi wajib saat dikutip |
|---|---|---|---|---|
| 1 | **DL-046** | ECMP-CONSTITUTION-001 (North Star, batas, completion criteria) | **Tulang punggung** — Mukadimah, Misi, Batas Produk, Target Architecture, Decision Filter, Completion Criteria | Tetap subordinat pada Board → ADR → EA |
| 2 | **DL-047** | GOV-001 kategori delivery A/B/C | Klausul **kendali perubahan** konstitusi | Ditulis sebagai klausul proses, bukan pasal bisnis |
| 3 | **DL-002** | Business Baseline SoT | Pasal **Lingkup Bisnis** | **Wajib** disertai carve-out kumulatif DL-007…011 dan catatan C-08 (eskalasi) |
| 4 | **DL-003** | Skema ID `BR-0xx` | Pasal **Terminologi & rujukan aturan** | BC-000 hanya mengutip `BR-0xx` |
| 5 | **DL-004** | BR Baseline Defaults | Pasal **Aturan Bisnis Dasar** | Kutip sebagai rujukan; angka reversibel via DEC BO |
| 6 | **DL-005** | Target SLA & NFR | Pasal **Komitmen Layanan** | Idem; sertakan catatan C-12 |
| 7 | **DL-006** | Multi-source & multi-target complaint | Pasal **Model Komplain** | — |
| 8 | **DL-023** | Case State Machine (Option O3) | Pasal **Lifecycle** | **Wajib** menuliskan Definition A dan B beserta ruang berlakunya (C-04) |
| 9 | **DL-024** | Mode A Case Management baseline | Pasal **Aturan Case** (case per complaint, penomoran, close, cancel) | Tandai butir yang eksplisit "outside Mode A" |
| 10 | **DL-019** | Penutupan bisnis CAP-006 | Pasal **Waktu & SLA** (kalender 24x7, start/stop clock, warning) | Sertakan tiga butir DEFERRED |
| 11 | **DL-025** | Workflow Config SoT = Administration | Pasal **Kepemilikan Konfigurasi** | ECMF adalah enforcer, bukan pendefinisi |
| 12 | **DL-026** | Configuration-First Principle | Pasal **Klasifikasi Aturan** (Configuration vs Hardcoded) | — |
| 13 | **DL-031** | ECMP bukan SoR pelanggan | Pasal **Kepemilikan Data** | — |
| 14 | **DL-056** | Role-Permission SoT = Core Platform | Pasal **Kepemilikan Otorisasi** | Bedakan Core Platform (domain ECMP) dari Enterprise Platform |
| 15 | **DL-001** | Merge persona → Complaint Officer | Pasal **Aktor / Persona** | Closed set tiga persona; sertakan status C-09 (Manager) dan C-07 |
| 16 | **DL-027** | CWX-000 Golden Rules | Pasal **Prinsip Pengalaman Kerja** | Dual-SoT UX dipertahankan |
| 17 | **DL-063** | Write-audit wajib | Pasal **Kewajiban Audit** | Catat read-audit masih ditunda |
| 18 | **DL-064** | Audit immutable + override berjustifikasi | Pasal **Integritas Audit** | Sifat immutable berasal dari ADR-003, bukan baseline reversibel |
| 19 | **DL-065** | Audit perubahan role-permission & workflow config | Pasal **Audit Konfigurasi Kritikal** | — |

### 7.1 Cakupan kandidat terhadap materi konstitusi bisnis

| Materi wajib sebuah Business Constitution | Tersedia? | Dari |
|---|---|---|
| Misi & batas produk | ✅ | DL-046 |
| Lingkup bisnis | ⚠️ tersedia dengan kualifikasi | DL-002 (+ C-08 terbuka) |
| Aktor / persona | ⚠️ tersedia dengan kualifikasi | DL-001 (+ C-09 terbuka) |
| Model & lifecycle komplain | ⚠️ tersedia dengan kualifikasi | DL-006, DL-023, DL-024 (+ C-04) |
| Aturan bisnis & baseline | ✅ | DL-003, DL-004, DL-026 |
| Komitmen layanan (SLA) | ⚠️ tersedia dengan kualifikasi | DL-005, DL-019 (+ C-12) |
| Kepemilikan (data, konfigurasi, otorisasi) | ✅ | DL-025, DL-031, DL-056 |
| Prinsip pengalaman kerja | ✅ | DL-027 |
| Kewajiban audit & kepatuhan | ✅ | DL-063, DL-064, DL-065 |
| Kendali perubahan konstitusi | ✅ | DL-047 (+ DL-046 §5) |
| Integrasi enterprise | ❌ **tidak tersedia** | Seluruhnya `APPROVED WITH CONDITIONS`; batas minimal diambil dari DL-046 §3 |

---

## 8. Deliverable 7 — Out-of-Scope Decision List

**46 keputusan** yang **tidak boleh** muncul sebagai pasal BC-000, dikelompokkan per alasan.

### 8.1 Implementation-specific (17)

Menyatakan modul kode, skema, endpoint, atau mekanisme — bukan aturan bisnis.

| DL | Judul | Catatan |
|---|---|---|
| DL-015 | EBS-001 org-location authorization | Enforcement Mode A |
| DL-016 | SLA deadline calculator | "perluas modul, tanpa migrasi" |
| DL-017 | SLA breach detection | Aturan evaluasinya bermateri bisnis → sudah terwakili DL-005/DL-019 |
| DL-018 | SLA → `complaint_timelines` | Keputusan reuse tabel |
| DL-020 | CAP-006 mechanism class Hybrid | Klasifikasi arsitektur |
| DL-021 | CAP-006 runtime di KPI & Performance | Penempatan runtime |
| DL-022 | G1 Contract Freeze | Semantik HTTP & payload event |
| DL-030 | Event-driven integration | Pola integrasi |
| DL-032 | Stack backend | — |
| DL-033 | Backend layering | — |
| DL-034 | API versioning `/v1` | — |
| DL-035 | Broker deferral + outbox | — |
| DL-036 | Baseline deployment | — |
| DL-043 | Canonical trees | CI ownership |
| DL-044 | Dual SoT & namespace remapping | Sequencing implementasi; tetap **wajib dirujuk** oleh kualifikasi DL-023 |
| DL-060 | KPI Foundation | Prinsip "KPI bukan SoT kedua" terwakili DL-031/DL-026 |
| DL-061 | Dashboard API | Orchestration layer |

### 8.2 Sprint / gate / program-specific (9)

| DL | Judul | Catatan |
|---|---|---|
| DL-007 | Appointment booking | Otorisasi TASK-014 |
| DL-008 | Appointment check-in | TASK-015 |
| DL-009 | Appointment completion | TASK-016 |
| DL-010 | Customer no-show | TASK-017 |
| DL-011 | Final Resolution | TASK-018 |
| DL-028 | Penutupan EPIC-CW-001 | Retrospektif epik |
| DL-050 | Otorisasi build G0 | Sprint-01 |
| DL-051 | G2 Mini-Gate | Gate lab |
| DL-052 | CAP-008 PROGRAM CLOSED | Penutupan program |

> **Peringatan:** DL-007…DL-011 dikeluarkan **sebagai record**, tetapi efek lingkup kumulatifnya **wajib** dibawa sebagai kualifikasi DL-002 (lihat BO-05). Mengabaikannya akan memasukkan pernyataan lingkup yang sudah tidak benar ke dalam konstitusi.

### 8.3 Sementara / bersyarat waktu (4)

| DL | Judul | Catatan |
|---|---|---|
| DL-029 | WCAG 2.2 AA | *Working target*, bukan klaim konformansi |
| DL-058 | Lab auth local JWT | Berlaku sampai runbook migrasi SSO diterima |
| DL-059 | Pintu auth Mode A → Mode B | Kesepakatan operasional; prinsipnya sudah di DL-046 |
| DL-062 | Penutupan bisnis CAP-007 | Audiens **v0.1** Supervisor-only, Manager ditunda |

### 8.4 Deprecated (1)

| DL | Judul | Catatan |
|---|---|---|
| DL-037 | Deferral frontend (ADR-011) | Trigger terpenuhi; efek normatif habis (C-11) |

### 8.5 Superseded (0)

Tidak ada keputusan yang **seluruhnya** digantikan. Yang ada adalah supersession **parsial berantai** pada DL-002 → DL-007 → DL-008 → DL-009 (dan DL-010 terhadap DL-007), dicatat pada kolom Reason matriks dan pada §8.2.

### 8.6 Belum selesai — kondisi terbuka (8)

Seluruhnya `APPROVED WITH CONDITIONS`, semuanya terikat C-7 / C-B6-1 (Mode B **CLOSED**).

| DL | Judul | Kondisi yang menahan |
|---|---|---|
| DL-013 | Kepemilikan organisasi | C-1, C-3, C-7 |
| DL-014 | Organization Synchronization | C-B6-1…7, gap org (C-B6-3) |
| DL-039 | ECMP Enterprise Business Module | C-1, C-3, C-7 |
| DL-040 | Enterprise Identity Contract | C-3 (bilateral belum terverifikasi), C-7 |
| DL-041 | Protocol & Binding | C-B6-1…7 |
| DL-042 | Entitlement Architecture | C-B6-1…7; representasi masih deferred |
| DL-045 | Baseline FE + CI policy | Accepted with Conditions |
| DL-057 | Larangan local auth Mode B | Bagian ADR-014; berlaku saat Mode B aktif |

### 8.7 Belum selesai — PENDING & CONFLICT (5)

| DL | Status | Alasan |
|---|---|---|
| DL-012 | PENDING | Countersign Board belum tercatat |
| DL-038 | CONFLICT | C-01 |
| DL-053 | CONFLICT | C-03 |
| DL-054 | CONFLICT | C-02 |
| DL-055 | CONFLICT | C-02 |

### 8.8 Rujukan otoritas, bukan isi (2)

| DL | Judul | Catatan |
|---|---|---|
| DL-048 | Board-004 | Dikutip BC-000 sebagai rantai otoritas |
| DL-049 | Board-006 | Idem |

**Total out-of-scope: 17 + 9 + 4 + 1 + 0 + 8 + 5 + 2 = 46** ✓

---

## 9. Deliverable 8 — Overall Governance Verdict

### 9.1 Putusan

> **BC-000 DAPAT DISUSUN — DENGAN KUALIFIKASI.**
>
> Sembilan belas keputusan berstatus APPROVED tersedia dan cukup untuk menutup seluruh materi wajib sebuah Business Constitution, **kecuali** integrasi enterprise — yang memang sengaja ditahan Board (Mode B CLOSED) dan batas minimalnya sudah tersedia lewat DL-046.
>
> **Empat konflik (C-04, C-07, C-08, C-09, C-12) menyentuh isi kandidat BC-000** dan harus mendapat disposisi Business Owner sebelum pasal terkait ditulis sebagai kalimat final. BC-000 tetap dapat disusun lebih dulu dengan pasal-pasal tersebut ditulis **beserta kualifikasinya secara eksplisit**, bukan disembunyikan.

### 9.2 Tingkat kesiapan

| Aspek | Nilai | Dasar |
|---|---|---|
| Kelengkapan materi bisnis | **Tinggi** | 10 dari 11 materi wajib tersedia |
| Kebersihan status persetujuan | **Sedang–Tinggi** | 78,5 % APPROVED; hanya 1 PENDING |
| Konsistensi internal repositori | **Sedang** | 12 konflik terdaftar, 5 di antaranya menyentuh isi bisnis |
| Kesiapan integrasi enterprise | **Rendah (disengaja)** | Seluruh rantai tertahan C-7 / C-B6-1; kontrak bilateral belum terverifikasi |
| Risiko memasukkan pernyataan usang ke konstitusi | **Sedang** | Supersession parsial berantai (§8.2) dan C-11 |

### 9.3 Tiga risiko terbesar bagi BC-000

1. **Pernyataan lingkup yang sudah tidak benar** — mengutip DL-002 tanpa carve-out DL-007…011, ditambah status eskalasi yang tidak pernah dicabut (C-08). Ini risiko nomor satu karena menghasilkan konstitusi yang **salah**, bukan sekadar tidak lengkap.
2. **Persona tanpa kapabilitas** — menetapkan closed set tiga persona sementara Manager tidak memiliki dashboard yang diotorisasi maupun padanan role teknis (C-09).
3. **Dua aturan SLA yang tampak bertentangan** (C-12) pada materi yang pasti masuk konstitusi.

### 9.4 Urutan tindakan yang direkomendasikan

| Langkah | Isi | Pemilik | Memblokir? |
|---|---|---|---|
| 1 | Disposisi BO-01, BO-02, BO-03 (C-08, C-12, C-09) | Business Owner | **Ya** — memblokir pasal Lingkup, SLA, dan Persona |
| 2 | Sinkronkan §2/§6 UX-FOUNDATION-000, lalu Review paket (BO-04) | UX Lead + BO | **Ya** untuk substansi UX di luar DL-001/DL-027 |
| 3 | Konsolidasi lingkup kumulatif appointment (BO-05) | Business Owner | **Ya** untuk pasal Lingkup |
| 4 | Susun **BC-000** dari 19 kandidat, dengan kualifikasi tertulis | Governance | — |
| 5 | AB-01, AB-02, AB-03 (konflik struktural) | Architecture Board | Tidak memblokir BC-000 |
| 6 | AB-04…AB-14, BO-06…BO-14 | Board / BO | Tidak memblokir BC-000 |

> **Catatan urutan.** Langkah 4 dapat berjalan **paralel** dengan langkah 5–6. Yang tidak boleh: menyusun BC-000 sebelum langkah 1–3, karena ketiganya mengubah **isi kalimat** pasal, bukan sekadar catatan kaki.

### 9.5 Pemenuhan Success Criteria G0.2B

| Kriteria | Status |
|---|---|
| Setiap keputusan DL-001…DL-065 diklasifikasi tepat satu status | ✅ 65/65 |
| Decision Readiness Matrix tersedia | ✅ §3 |
| Conflict Register tersedia dan tidak diselesaikan otomatis | ✅ §4 — 12 konflik, semuanya berhenti pada "Disposisi diminta" |
| Business Owner Review List | ✅ §5 — 14 butir |
| Architecture Board Review List | ✅ §6 — 14 butir |
| BC-000 Candidate List berisi **hanya** keputusan APPROVED | ✅ §7 — 19 kandidat, seluruhnya APPROVED |
| Out-of-Scope List | ✅ §8 — 46 keputusan, total terverifikasi |
| Overall Governance Verdict | ✅ §9 |
| DL-000 tidak dimodifikasi | ✅ hanya dibaca |
| BC-000 tidak dibuat | ✅ |
| Tidak ada perubahan kode/frontend/backend/database | ✅ dokumentasi saja |
| **BC-000 dapat dihasilkan hanya dari keputusan APPROVED hasil review ini** | ✅ dengan kualifikasi §9.1 |

---

## Related

- `docs/governance/DL-000-Decision-Log.md` — input tunggal review ini
- `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_007_ADR007_012_Relationship_Disposition_Brief_v0.1.md`
- `docs/ux/UX-FOUNDATION-000-Complaint-Module-UX-Foundation.md`
- `docs/frontend/OPEN_DECISIONS.md`
- `deploy/evidence/DEC_ID_Collision_Register_20260801.md`
- `27 Project Decisions/OPEN_QUESTIONS.md`

## Future Work

BC-000 (Business Constitution) — disusun pada milestone berikutnya dari **19 kandidat §7** + **DL-066…069**, setelah P1 BO ditutup (GC-000). Di luar ruang lingkup dokumen review awal ini.

---

## Addendum G0.2D — Business Owner P1 Disposition (2026-08-05)

Addendum ini **tidak mengubah** klasifikasi historis §2–§9 di atas; ia mencatat disposisi yang terjadi setelah BO-WS-000.

| Conflict / BO item | Disposition | Status |
|---|---|---|
| C-08 / BO-001 | Option A — Escalation Branch↔HO in scope Mode A | **CLOSED** (DL-066) |
| BO-005 | Option A — Appointment in scope Mode A, same lifecycle | **CLOSED** (merged into DL-066) |
| Merge BO-001+005 | YES — Scope Consolidation | **CLOSED** |
| C-12 / BO-002 | Option A — satu SLA Constitution; timeline events wajib | **CLOSED** for BC business rule conflict (DL-067); C-05 mechanism convergence **STILL OPEN** (Board) |
| C-09 / BO-003 | Option A — Manager persona sah; workspace deferred | **CLOSED** (DL-068) |
| C-07 / BO-004 | Option A — sync status UX; administratif | **CLOSED** inconsistency (DL-069); paket **PARTIALLY CLOSED** sampai Review→Approval isi |
| C-01…C-03, C-05, C-06, C-10, C-11 | Di luar P1 BO | **STILL OPEN** (Architecture Board) |
| C-04 | Dual CSM disengaja | **PARTIALLY CLOSED** — tetap kualifikasi BC; Retirement DEC = Board |

**Updated verdict for starting BC-000:** lihat `docs/governance/GC-000-Governance-Closure-BC-Readiness.md` → **READY WITH CONDITIONS**.

---

*End of DRR-000.*
