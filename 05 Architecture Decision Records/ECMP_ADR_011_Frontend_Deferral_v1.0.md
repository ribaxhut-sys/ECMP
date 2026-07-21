# ECMP_ADR_011_Frontend_Deferral_v1.0

| Field | Value |
|---|---|
| ID | ADR-011 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | UX Lead / Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

- ADR Status: Accepted (Architecture Board, 2026-07-21 — gap remediation)
- Date: 2026-07-21
- Decision Owners: Solution Architect, UX Lead
- Related Domains: All (product UI)

## Context
Penundaan frontend selama ini hanya tersirat: DEC-002 mencantumkan "frontend produk" sebagai non-goal Sprint-0/G0, ADR-004 menandai frontend "deferred (API-first)" dengan follow-up ADR terpisah, dan `21 Technical Standards` menahan TypeScript/React Standard. Tidak ada satu keputusan resmi yang menyatakan kapan dan dengan syarat apa frontend dimulai — celah untuk membangun UI prematur atau berdebat ulang tanpa acuan.

## Decision
1. **ECMP adalah API-first** — tidak ada frontend produk yang dibangun sampai trigger di butir 2 tersentuh. Interaksi Sprint-01 memakai API langsung (journey API-first di UX-001).
2. **Trigger memulai frontend** (semua terpenuhi):
   (a) slice create/get stabil dan gate **G1** (lifecycle contract — assign/status) lulus;
   (b) kebutuhan UI **divalidasi Business Owner** (bukan asumsi tim teknis);
   (c) kebutuhan per persona **P-01..P-05** di UX-001 (`../12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md`) dijadikan dasar scope layar.
3. **Saat trigger tersentuh:** buat **ADR stack frontend baru** (memenuhi follow-up ADR-004) dan tulis **screen spec** di `../12 UI UX Spec` sebelum kode UI pertama.
4. **Kandidat dicatat, tidak diputuskan sekarang:** SPA (React + TypeScript — default candidate ADR-004 — atau Vue) vs server-rendered (mis. template FastAPI/Jinja atau meta-framework SSR). Evaluasi dilakukan di ADR stack frontend dengan data kebutuhan persona nyata.
5. **Pengecualian yang bukan frontend produk:** developer portal internal (`implementation/portal`, IMP-PORTAL-001) dan dokumentasi — bukan UI produk, tidak tunduk pada deferral ini.

## Consequences
- Non-goal "frontend produk" DEC-002 kini punya dasar ADR eksplisit dengan kondisi keluar yang terukur, bukan sekadar larangan sprint.
- TypeScript/React Standard di `21 Technical Standards` tetap Planned sampai ADR stack frontend ada.
- UI test di Test Strategy (TST-001 §6) tetap backlog dengan trigger yang sama.
- Tidak ada komponen frontend, build pipeline JS, atau design system yang boleh dibangun spekulatif sebelum trigger.

## Compliance / Follow-up
- [ ] ADR stack frontend — saat trigger butir 2 tersentuh
- [ ] Screen spec per persona di `../12 UI UX Spec` — sebelum kode UI pertama
- [ ] Aktifkan TypeScript/React Standard di `21 Technical Standards` — setelah ADR stack frontend
