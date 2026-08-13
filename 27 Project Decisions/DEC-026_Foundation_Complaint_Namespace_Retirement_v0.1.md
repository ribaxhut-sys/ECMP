# Decision Record — Retirement Namespace Foundation `/api/v1/complaints` (Mode A)

| Field | Value |
|---|---|
| ID | DEC-026 |
| Version | 1.0 |
| Owner | Business Owner / Solution Architect |
| Reviewer | Architecture Board / Domain PO ECMF |
| Approver | Architecture Board + Business Owner |
| Status | 🟢 **Accepted with Conditions** (Mode A — BO/Board session 2026-08-13) |
| Date | 2026-08-13 |
| Last Review | 2026-08-13 |
| Next Review | 2027-02-13 |
| Related | DEC-020 (Accepted; coexistence Foundation **dijadwalkan** berakhir setelah M-026); DEC-025 (Accepted; H1); PROGRAM-IMPLEMENTATION-001; FRD-CM-001; CAP-008 CLOSED |
| Type | Project Decision (non-ADR) — **Retirement / Cutover DEC** yang disyaratkan DEC-020 |

- Decision Status: **Accepted with Conditions**
- Kondisi: konsumen Mode A Foundation masih hidup → **M-026-1 sebelum** unmount API (AC §6.7)
- DEC-020 tubuh **tidak** di-rewrite; coexistence Foundation tidak lagi tujuan — berakhir setelah eksekusi M-026
- **Tidak** unmount router, **tidak** drop tabel, **tidak** hapus rute FE pada hari Accept
- **Tidak** unlock Mode B, CAP-006, DEC-F4, atau reopen CAP-008
- Eksekusi cutover = **M-026-1…3** terpisah, bukan bagian Accept ini

---

## 1. Context

DEC-020 (Accepted) mengunci Dual-SoT sampai ada **Retirement DEC** terpisah.

DEC-025 (Accepted 2026-08-13) mengunci **target** Single SoT = CM Aggregate `/api/v1/cm` + Case. Foundation diperlakukan legacy. Niat data historis = **H1**: yang sesuai sudah ada di CM; `CMP-…` **bukan** versi lama yang harus di-merge.

M-025-1…6 sudah dijalankan (kontrak/sync, pintu UI CM, overlay FRD, inventaris konsumen, opsi data). Runtime **masih** memasang `/api/v1/complaints`.

DEC-020 Acceptance Criteria §4 mensyaratkan Retirement DEC ini sebelum collapse namespace.

**Bukan** wholesale remapping pada tanggal tetap (Alternatif A DEC-020 — ditolak). Ini cutover **setelah** Accept + milestone eksekusi.

---

## 2. Options

| Opsi | Isi | Disposisi |
|---|---|---|
| A | Pertahankan Dual-SoT tanpa horizon | Ditolak BO (DEC-025) — membingungkan |
| B | Retirement: Foundation `/api/v1/complaints` + tabel `complaints*` di-retire **setelah** Accept + M-026; data per **H1**; CA BC **bukan** objek retire ini | **Selected — Accepted with Conditions 2026-08-13** |
| C | Accept + eksekusi drop hari ini | Ditolak — konsumen Foundation masih hidup (§8.4 DEC-025); meloncat |
| D | Merge / mapping `CMP-` → CM (H3/H4) | Ditolak — DEC-025 H1; model tidak 1:1 |

---

## 3. Decision (Accepted with Conditions 2026-08-13 — kebijakan mengikat; eksekusi ≠ Accept)

### 3.1 Apa yang di-retire (setelah Accept + eksekusi)

| Objek | Tindakan saat eksekusi (bukan saat Accept) |
|---|---|
| HTTP `/api/v1/complaints` (legacy ECMF: CRUD, search API-388, assign, escalate, resolve, close, SLA-on-legacy, timeline) | Unmount / berhenti dilayani sebagai API produk Mode A |
| FE Mode A: `/queue` (non-shell `QueueDashboardView`), `/assignments`, `/resolutions`, `/complaints/[id]`, `/complaints/[id]/edit` | Dihapus atau redirect ke CM / Case; bukan dual-read lagi |
| Client FE `createComplaint` / `searchComplaints` / lifecycle Foundation | Dihapus dari jalur produk |
| Tabel `complaints` + related (`complaint_assignments`, `complaint_escalations`, `complaint_resolutions`, `complaint_timelines`, `sla_records` yang hanya Foundation) | **H1:** tidak di-merge ke `cm_batch1_*`. Drop atau biarkan unused — dipilih di M-026, bukan hari Accept |
| Nomor `CMP-…` | Tidak dilestarikan sebagai SoT; tidak di-map ke `UNIT-YYMM-NNNN` |

### 3.2 Apa yang **tetap** (bukan objek DEC ini)

| Objek | Aturan |
|---|---|
| `/api/v1/cm` + `cm_batch1_*` + `cm_cases` | Target Single SoT (DEC-025) |
| Shared `/api/v1/attachments*` | Tetap (DEC-020) |
| CA BC ticket-nested `complaint_api_router` | **Tetap mounted** |
| CA BC `complaint_foundation_router` | **Tetap unmounted** |
| Tabel `complaint_cases*` | **Tidak** di-drop oleh DEC-026 |
| Shell B0 `/queue/*` + `/workspace` (mock WF-001) | **Di luar** Dual-SoT WP — jangan dicampur eksekusi |
| `/internal/*` | Prototype terpisah — di luar DEC ini |
| Mode B / SSO / Identity Adapter | CLOSED |

### 3.3 CA BC — keputusan eksplisit (syarat DEC-020 AC §4)

DEC-026 **memutus** (jika Accept):

> CA BC **bukan** di-retire dan **bukan** di-mount penuh oleh retirement Foundation.  
> Produksi tetap: ticket-nested only. Full `complaint_foundation_router` tetap unmounted.  
> Bukan CM Case. Bukan evolusi `cm_batch1`.

DEC terpisah masih boleh kelak jika Board ingin retire/mount CA BC. **Tidak** digabung diam-diam ke M-026.

### 3.4 Data (H1 — dari DEC-025)

- Yang sesuai = versi CM. Tidak ada merge, tidak ada mapping table.
- Saat eksekusi: data `CMP-…` ignore/drop, bukan migrasi ke Aggregate.
- Accept **tidak** menjalankan DROP.

### 3.5 Hubungan ke DEC-020 / DEC-025

| Saat | DEC-020 | DEC-025 | DEC-026 |
|---|---|---|---|
| Sekarang (Accept, pra-M-026) | Tubuh tidak diubah; coexistence Foundation **dijadwalkan** berakhir | Accepted (target + H1) | Kebijakan retire mengikat; runtime **belum** berubah |
| Setelah M-026 eksekusi | Foundation path tidak dilayani | CM = SoT runtime | Cutover selesai untuk objek §3.1 |

DEC-020 **tidak** di-rewrite. Indeks: superseded **for Foundation namespace coexistence only** setelah M-026-2 — bukan hari Accept.

---

## 4. Explicit non-goals (binding)

Accept DEC-026 **tidak** mengotorisasi:

- Eksekusi unmount/drop sebagai bagian dari vote Accept itu sendiri
- Merge `complaints` + `cm_batch1_*` + `cm_cases` (H4)
- Mapping `CMP-` ↔ nomor CM (H3)
- Hapus CA BC / mount `complaint_foundation_router`
- Retarget atau hapus Shell B0 `/queue/*` sebagai syarat cutover CM
- Mode B / enterprise `securitySchemes` / Identity Adapter
- Reopen CAP-008, CAP-006, DEC-F4
- Silent foundation UI cutover **sebelum** Accept

---

## 5. Prasyarat vs status Observed (jujur)

Sumber: DEC-025 §8 / §17 + inventaris M-025-6.

| Prasyarat DEC-020 / DEC-025 | Status 2026-08-13 | Cukup untuk draf? | Cukup untuk Accept 2026-08-13? |
|---|---|---|---|
| Dedicated Retirement DEC | Dokumen ini | Ya | Ya (dokumen ada) |
| Kontrak + sync Aggregate §3.4 | Ada (M-025-1) | Ya | Ya |
| Overlay AC-16 / BR-009 | Ada (M-025-4) | Ya | Ya |
| H1 data historis | Niat BO terkunci | Ya | Ya |
| CA BC decided explicitly | §3.3 | Ya | **Ya** — vote mencakup §3.3 |
| Consumer migration complete | **Belum** — `/queue`, assign, resolve, detail Foundation masih hidup | Ya (draf) | **Accept-with-conditions:** konsumen Mode A dihapus di **M-026-1 sebelum** unmount API |
| OpenAPI + RTM | Belum diubah (benar: jangan sekarang) | Ya | Setelah Accept: M-026-2 catalog |
| Mode B tidak diandalkan | Ya | Ya | Ya |

**Vote 2026-08-13:** **Accept-with-conditions** — bukan opsi C (drop hari ini). Kondisi: M-026-1 sebelum unmount.

---

## 6. Acceptance Criteria (vote Board)

Board **Accept** DEC-026 hanya jika mengonfirmasi **semua**:

1. Objek retire = §3.1 saja; §3.2 tetap.
2. CA BC = §3.3 (ticket-nested; full unmounted; bukan objek drop).
3. Data = H1 (DEC-025); bukan H2/H3/H4.
4. DEC-020 tetap tidak di-rewrite; coexistence Foundation berakhir **hanya setelah** Accept + eksekusi.
5. Accept **bukan** M-026; tidak ada DROP/unmount di hari vote.
6. Mode B / CAP-008 / CAP-006 / DEC-F4 / B0 shell **tidak** di-unlock atau di-retire oleh vote ini.
7. Kondisi konsumen: M-026-1 mengangkat FE Mode A Foundation **sebelum** API di-unmount (tidak ada jendela petugas ke API mati).

**Reject** berarti: DEC-020 Dual-SoT tetap kebijakan penuh; DEC-025 target tetap; tidak ada jadwal retire.

### Sign-off record

| Role | Disposition | Date |
|---|---|---|
| Business Owner / Architecture Board (session) | **Accept with Conditions** — kriteria §6.1–6.7 | 2026-08-13 |
| Record | Working session ECMP — perintah `Board Accept` | 2026-08-13 |
| Condition | M-026-1 (FE Mode A Foundation) **sebelum** M-026-2 (unmount API) | 2026-08-13 |

Accept mengunci **kebijakan** §3. Tidak menjalankan M-026-1…3, tidak DROP/unmount, tidak mengubah OpenAPI/kode/test.

---

## 7. Follow-up setelah Accept (bukan sekarang)

| Milestone | Isi | Bukan |
|---|---|---|
| **M-026-1** | Hapus/redirect FE Mode A Foundation (§3.1); pastikan tidak ada caller API-388/201 di jalur produk | Jangan unmount API dulu |
| **M-026-2** | Unmount `/api/v1/complaints` legacy; OpenAPI + RTM + tes coexistence → retired/unmounted | Jangan drop CA BC |
| **M-026-3** | H1: drop atau unused-leave tabel `complaints*` (pilih satu di milestone; default lab = drop jika tidak ada kewajiban audit) | Jangan migrate ke CM |

Urutan mengikat: **1 → 2 → 3**. Accept tidak menjadwalkan tanggal dan **tidak** memulai M-026.

**M-026-1 execution (2026-08-13):** FE Mode A Foundation `/assignments` `/resolutions` `/complaints/[id]` `/complaints/[id]/edit` redirect ke CM/Case; `/queue` non-shell → Case inbox; B0/shell `/queue` tetap. CTA dasbor tidak lagi ke Foundation.

**M-026-2 execution (2026-08-13):** Unmount production `/api/v1/complaints` lifecycle + nested assign/search/escalate/resolve/SLA-instance/timeline + top-level `/api/v1/escalations` + `/api/v1/appointments`. CA BC ticket-nested + `/api/v1/cm` + SLA policies + generic timeline + attachments **tetap**. OpenAPI/OWNERSHIP/tes coexistence diselaraskan.

**M-026-3 execution (2026-08-13):** **DROP** tabel Foundation `appointments` → `sla_records` → `complaint_timelines` / `complaint_resolutions` / `complaint_assignments` / `complaint_escalations` → `complaints` (Alembic 0072). H1: tidak di-merge ke CM. CA BC `complaint_cases*` **tidak** disentuh. Prasyarat: reader dashboard/KPI/reports sudah Aggregate-only.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Vote Accept dianggap izin DROP | Status Accepted with Conditions; M-026 terpisah; non-goals §4 |
| Accept tanpa M-026-1 → petugas 404 di `/queue` | AC §6.7; urutan §7 |
| Tim meng-merge `CMP-` “supaya lengkap” | H1 + tolak H3/H4 |
| CA BC ikut terhapus | §3.3 eksplisit |
| B0 shell pecah | §3.2 out of scope |

---

## 9. Impact (hanya setelah Accept + M-026)

| Artefak | Dampak Accept (hari ini) | Dampak setelah eksekusi M-026 |
|---|---|---|
| DEC-020 | Tidak berubah | Coexistence Foundation superseded by DEC-026 |
| DEC-025 | Tetap Accepted | Target = runtime SoT |
| OpenAPI `complaint-service.v1.yaml` | Tidak diubah sekarang | Retired / unmounted (M-026-2) |
| OWNERSHIP_MATRIX | Dual-namespace tetap | Setelah M-026-2: `/api/v1/cm` kanonik |
| Tes coexistence mount | Tetap hijau | Diganti tes “Foundation unmounted” |

---

## Links

- DEC-020: `DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md`
- DEC-025: `DEC-025_CM_Target_Single_SoT_and_Mode_A_Complaint_Closure_v0.1.md` (§8, §14–17, H1)
- PROGRAM-IMPLEMENTATION-001: `18 Architecture Governance/ECMP_PROGRAM_IMPLEMENTATION_001_Implementation_Authorization_Posture_v1.0.md`
- Collision ID: `deploy/evidence/DEC_ID_Collision_Register_20260801.md` (DEC-026 **tidak** memakai ulang 020/021)

---

*End of DEC-026 v1.0 Accepted with Conditions.*
