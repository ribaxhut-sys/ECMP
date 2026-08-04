# ECMP UI Baseline — Official UI Freeze

| Field | Value |
|---|---|
| ID | ECMP-UI-BASELINE-001 |
| Alias | ECMP-UI-FREEZE-01 |
| Program | PROGRAM-FRONTEND-001 |
| Status | 🔒 **LOCKED** (product UI baseline) |
| Effective | 2026-08-02 |
| Owner | Frontend Lead / UX Lead |
| Reviewer | Solution Architect |
| Approver | Product Owner / Architecture Board (as applicable) |
| Canonical tree | `frontend/` (DEC-019) |
| Design System SoT | `frontend/src/app/globals.css` (Design System v1.0) |
| Architecture SoT | FE-ARCH-001 v1.2 (**BASELINE**) |
| Standards SoT | FE-STD-001 v1.0 (**BASELINE**) |
| Related | ECMP-UX-2.1 Product Cohesion Polish; `frontend/src/shared/README.md` |

---

## 1. Purpose

Dokumen ini menetapkan **baseline resmi Complaint Module UI**.

Mulai tanggal efektif di atas:

1. Product UI dianggap **LOCKED**.
2. Redesign terbuka **tidak** dilanjutkan.
3. Perubahan visual hanya mengikuti **Change Policy** (§10).

Ini adalah **UI product freeze**, bukan Board unlock Mode B, bukan supersede ADR-013, dan bukan klaim WCAG conformance penuh.

---

## 2. Freeze scope (LOCKED surfaces)

| Surface | Status | Canonical location | Notes |
|---|---|---|---|
| **Design System** | 🔒 LOCKED | `frontend/src/app/globals.css` + `frontend/src/shared/theme/` | Prefix `--ecmp-*`; extend keys only; do not rename |
| **Shared UI** | 🔒 LOCKED | `frontend/src/shared/ui/` | Compose; do not fork primitives in features |
| **Shell** | 🔒 LOCKED | `frontend/src/shared/layouts/app-layout/` | Header + Sidebar + content; nav groups presentation-only |
| **Dashboard** | 🔒 LOCKED | `frontend/src/features/dashboard/` | Layout grid, CompactHeader, surface tokens, card hierarchy |
| **Workspace** | 🔒 LOCKED | List/detail chrome via `PageContainer` + `PageHeader` + `WorkspaceToolbar` + `FilterBar` / `Table` | Complaints, queue, assignments, resolutions, attachments, reports, users, settings |
| **Auth chrome (Mode A)** | 🔒 LOCKED (Mode A hedge) | `AuthLayout` + credential routes | Mode B AuthN UI remains **CLOSED** (C-7 / C-B6-1) |

**Out of freeze (not redesign targets):**

- Backend / OpenAPI / hooks / permissions / business logic / routing contracts
- Mode B SSO / Identity Adapter / enterprise `securitySchemes` (Board-gated)
- Formal UX inventory under `12 UI UX Spec/` (OD-FE-005 — documentation debt, not UI redesign)

---

## 3. Design principles

1. **Tokens first** — No hardcoded hex, arbitrary radius (`rounded-[Npx]`), or one-off spacing in feature UI. Consume `--ecmp-*` / Tailwind `ecmp-*` theme keys.
2. **Compose, don’t copy** — Prefer `@/shared/ui` over local buttons, badges, tables, alerts, empty/error states.
3. **One shell** — Authenticated pages use `AppLayout`. Auth screens use `AuthLayout`.
4. **One product feel** — Dashboard, workspaces, directory, settings, and profile share the same visual language (ECMP-UX-2.1 cohesion baseline).
5. **Honest affordances** — No fake chevrons, fake keyboard badges, or hover-lift on static cards.
6. **Interactive hover only** — Elevation / translate on hover is reserved for clickable/navigable elements (`Card interactive`, row click, buttons).
7. **Accessible by default** — Single focus ring, 44×44 touch targets, 16px minimum body, skip link, semantic landmarks.
8. **Professional over decorative** — Enterprise SaaS density; no marketing glassmorphism or decorative redesign.
9. **Module, not platform** — ECMP is an Enterprise Business Module (ADR-014). Do not invent portal chrome, enterprise SSO UI, or Role-Permission SoT admin as product redesign.
10. **Stability** — Do not redesign accepted/green UI without Change Policy gate (§10).

---

## 4. Token utama (Design System v1.0)

**SoT:** `frontend/src/app/globals.css`  
**TS mirrors:** `frontend/src/shared/theme/`  
**Prefix:** `--ecmp-*` — existing keys never renamed; new keys extend only.

### 4.1 Color (semantic)

| Group | Examples |
|---|---|
| Brand | `primary`, `primary-foreground`, `primary-muted`, `secondary` (+ fg/muted) |
| Feedback | `success`, `warning`, `danger`, `info` (+ fg/muted) |
| Surfaces | `background`, `surface`, `surface-raised`, `surface-sunken`, `surface-floating`, `surface-overlay` |
| Text / chrome | `text-primary`, `text-secondary`, `border`, `focus`, `muted` |
| Interaction | `hover`, `selected`, `pressed`, `disabled` |
| State surfaces | `{success\|warning\|danger\|info}-{bg\|border\|text\|subtle}` |

**Rule:** Do not use raw Tailwind `slate-*` / `teal-*` / `gray-*` in product UI. Use semantic `ecmp-*` tokens.

Dark-ready mirrors exist under `.dark` but **toggle is not wired** — do not ship dark mode UI without Change Policy + product decision.

### 4.2 Spacing scale

`4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64` px → `--ecmp-space-*`

### 4.3 Layout tokens

| Token | Role |
|---|---|
| `--ecmp-page-gutter` | Page horizontal padding |
| `--ecmp-section-gap` | Between major page sections |
| `--ecmp-panel-gap` | Inside panels / toolbars |
| `--ecmp-card-gap` | Between cards / grid cells |
| `--ecmp-dashboard-gap` | Dashboard vertical rhythm |
| `--ecmp-form-gap` | Form field stacks |
| `--ecmp-content-max-width` | `PageContainer` max width (80rem) |
| `--ecmp-sidebar-width` | 248px |
| `--ecmp-header-height` | 64px |
| `--ecmp-touch-min` / `--ecmp-button-height` | 44px |
| `--ecmp-card-padding` | 24px |

### 4.4 Radius

| Scale | Value |
|---|---|
| sm / md / lg / xl / full | 4 / 8 / 12 / 18 / 9999 |
| Roles | button/input/select/textarea → md; badge → sm; card/table/modal/dialog/surface → 18; search → 14 |

### 4.5 Elevation

`shadow-sm` · `md` · `lg` · `surface` · `raised` · `floating` · `overlay` · `hover` · `search`

### 4.6 Motion

Fast / normal / slow: **180 / 200 / 220 ms** with `--ecmp-ease-*`. Respect `motion-reduce`.

### 4.7 Z-index

dropdown 40 · sticky-header 30 · sidebar 50 · overlay 55 · modal 60 · toast 65 · loading 70

---

## 5. Typography

| Role | Size | Weight | Token family |
|---|---|---|---|
| Display | 2.25rem | 700 | `--ecmp-font-display-*` |
| Page title | 1.875rem | 700 | `--ecmp-font-page-title-*` |
| Section title | 1.25rem | 600 | `--ecmp-font-section-title-*` |
| Card title | 1.125rem | 600 | `--ecmp-font-card-title-*` |
| Body | 1rem (16px min) | 400 | `--ecmp-font-body-*` |
| Body small | 0.875rem | 400 | `--ecmp-font-body-small-*` |
| Label | 0.875rem | 600 | `--ecmp-font-label-*` |
| Helper | 0.8125rem | 400 | `--ecmp-font-helper-*` |
| Caption | 0.875rem | 400 | `--ecmp-font-caption-*` |
| Overline | 0.75rem | 600 | `--ecmp-font-overline-*` |

**Font family:** Source Sans 3 (+ system fallbacks) via `--ecmp-font-family`.

**Dashboard exception (locked):** Dashboard uses a deliberate display scale in `dashboardUtils.ts` (`DASHBOARD_TITLE`, `DASHBOARD_METRIC`, etc.). Do **not** “normalize” these to page-title tokens as a redesign; treat as part of the locked dashboard language.

---

## 6. Shell (LOCKED)

**Files:** `AppLayout.tsx`, `Header.tsx`, `Sidebar.tsx`, `nav.ts`

| Element | Baseline |
|---|---|
| Structure | Persistent sidebar (desktop) + drawer (mobile); sticky header; `#main-content` landmark |
| Skip link | Present (`common.skipToContent`) |
| Header | Global search (permission-gated), language switcher, ProfileChip → `/profile`, logout |
| Search honesty | Ctrl/Meta+K focuses global search; badge only when shortcut is live |
| ProfileChip | Avatar + name/role; **no** fake dropdown chevron; navigates to profile |
| Nav | `APP_NAV_ITEMS` + presentation groups (`operations` / `knowledge` / `administration`) — order/membership not reinvented here |
| Dimensions | Sidebar 248px; header 64px; page gutter tokens |

**Do not:** redesign chrome density, invent enterprise portal switcher, or Mode B SSO browser UI.

---

## 7. Dashboard layout (LOCKED)

**Entry:** `DashboardView` + `DASHBOARD_SHELL` / surface helpers in `dashboardUtils.ts`

| Region | Baseline |
|---|---|
| Shell | Max width 1440px; dashboard gap token; soft primary atmosphere gradient (tokenized surfaces) |
| Header | `CompactHeader` — greeting, title, period chip (Today active; 7d/30d disabled), refresh |
| Row 1 | `SummaryCards` KPI strip |
| Row 2 | Trend (8) + By Status (4) |
| Row 3 | By Branch (4) + SLA (4) + Today’s Insight (4) |
| Row 4 | Recent Activity (8) + Quick Actions (4) |
| Surfaces | `DASHBOARD_SURFACE` / `DASHBOARD_SURFACE_FLAT` — raised/flat cards **without** hover-lift |
| Empty / error | Shared `Empty` / `ErrorState` |

**Do not:** rearrange grid, invent new dashboard information architecture, or reintroduce hover-lift on static analytics cards.

---

## 8. Workspace pattern (LOCKED)

Standard authenticated workspace composition:

```
PageContainer
  └─ PageHeader (overline, title, description, breadcrumbs, actions, meta)
  └─ WorkspaceToolbar / FilterBar / QuickFilters (as applicable)
  └─ Table | Cards | Detail panels
  └─ Empty | ErrorState | Loading/Skeleton
```

| Workspace family | Examples |
|---|---|
| Operations lists | Complaints, Queue, Assignments, Resolutions |
| Knowledge | Attachments, Reports |
| Administration | Users (directory), Settings (Configuration Center) |
| Account | Profile / security (Mode A) |

**Rules:**

- Use `PageHeader` + layout tokens for section rhythm.
- `WorkspaceToolbar` uses search radius role; sticky under header when enabled.
- Table mobile cards: hover-lift **only** when row is clickable.
- Users: people-directory feel (avatar, role chip, status) — not a greenfield admin CRUD redesign.
- Settings: Configuration Center grouping — not a registry redesign.

---

## 9. Interaction & accessibility

### 9.1 Interaction

| Rule | Baseline |
|---|---|
| Hover elevation | Interactive elements only |
| Card | Default static; `interactive` enables lift + pointer |
| Buttons | Variant hierarchy via shared `Button` |
| Focus | Single ring: `--ecmp-focus-ring-*` |
| Motion | 180–220 ms; honor `prefers-reduced-motion` |
| Density | Comfortable/compact tokens exist; density toggle is shared — do not invent parallel density systems |

### 9.2 Accessibility (working target)

| Item | Baseline |
|---|---|
| Target | WCAG 2.2 AA **working target** (OD-FE-009 CLOSED as target; **no** formal conformance claim without UX audit) |
| Focus | Visible `:focus-visible` ring application-wide |
| Touch | Min 44×44 (`--ecmp-touch-min`) |
| Body text | ≥ 16px |
| Landmarks | Skip link, `main#main-content`, labeled listboxes/panels where implemented |
| Live regions | Dashboard sync / polite updates where present |

---

## 10. Shared UI inventory (LOCKED primitives)

Export surface: `frontend/src/shared/ui/index.ts`

| Category | Components |
|---|---|
| Actions | `Button` |
| Forms | `FormField`, `Input`, `Textarea`, `Select`, `Checkbox`, `Radio` / `RadioGroup` |
| Structure | `Card` (+ Header/Title/Description/Body/Footer), `PageContainer`, `PageHeader`, `SectionHeader`, `PanelHeader`, `Breadcrumb` |
| Feedback | `Alert`, `Badge`, `Toast`, `Empty`, `ErrorState`, `Loading` / `Skeleton` / `Spinner` / skeletons, `PageFallback` |
| Data | `Table`, `Pagination`, `StatCard` / `MetricCard`, `ProgressMeter`, `Timeline` |
| Workspace chrome | `WorkspaceToolbar`, `FilterBar`, `QuickFilters`, `DensityToggle` |
| Overlay | `Modal` / `ModalSection` |

**Rule:** New visual needs must prefer extending these primitives (token-compatible) over one-off feature chrome — and only when Change Policy allows.

---

## 11. Change Policy (binding)

Mulai freeze ini, perubahan UI **hanya** boleh jika salah satu terpenuhi:

| # | Gate | Examples |
|---|---|---|
| 1 | **Bug visual** | Broken layout, overflow, clipped text, wrong contrast from regression |
| 2 | **Accessibility issue** | Missing label, focus trap, keyboard dead-end, contrast failure |
| 3 | **Business requirement baru** | FR/BR approved that requires UI surface |
| 4 | **API baru membutuhkan visualisasi baru** | Catalogued OpenAPI field/endpoint with agreed UX |
| 5 | **UAT menunjukkan masalah nyata** | Recorded UAT finding with reproduction |

**Selain itu: JANGAN redesign.**

### Explicitly forbidden without a gate above

- “Polish pass” / “make it prettier” / alternate dashboard IA
- New shell chrome, command palette product, profile mega-menu (unless gated)
- Token renames or parallel design systems
- Mode B AuthN / SSO UI (also Board-gated — CLOSED)
- Silent replacement of foundation complaint UI (DEC-020 coexistence)

### Process expectation

1. Cite the gate (bug ID / a11y finding / FR / API / UAT).
2. Prefer minimal token/shared-component fix over page redesign.
3. Keep Dashboard / Shell / Workspace / Shared UI / Design System structure intact unless the gate proves structure is the defect.

---

## 12. Verification checklist (freeze audit)

| # | Check | Result |
|---|---|---|
| 1 | Design System tokens SoT present (`globals.css` + theme mirrors) | ✓ LOCKED |
| 2 | Shared UI primitives exported and consumed as product baseline | ✓ LOCKED |
| 3 | Shell = Header + Sidebar + main; nav groups presentation-only | ✓ LOCKED |
| 4 | Dashboard grid + CompactHeader + surface helpers stable | ✓ LOCKED |
| 5 | Workspace pattern PageContainer/PageHeader/Toolbar/Table stable | ✓ LOCKED |
| 6 | Product cohesion pass applied (ECMP-UX-2.1) — no open redesign track | ✓ |
| 7 | Mode B AuthN UI not in scope / remains CLOSED | ✓ |
| 8 | FE-ARCH / FE-STD remain architecture BASELINE (not contradicted by this freeze) | ✓ |
| 9 | Change Policy documented (§11 / §10) | ✓ |
| 10 | Open redesign workstreams for frozen surfaces | **None** |

---

## 13. Remaining UI debt (non-redesign)

| Item | Class | Notes |
|---|---|---|
| OD-FE-005 UX spec consolidation | Documentation | Formal screens under `12 UI UX Spec/` incomplete vs routes — **does not** authorize redesign |
| OD-FE-009 formal a11y audit | Process | Working target accepted; conformance claim still needs UX audit |
| Dashboard local type scale | Accepted exception | Locked dashboard language; do not “fix” via redesign |
| `.dark` tokens unwired | Limitation | Do not enable without product decision |
| Period 7d/30d disabled on dashboard | Product limitation | Requires data/API + BR before UI activation |
| Profile menu / command palette product | Out of scope | Not baseline; do not invent without gate |
| Legacy `implementation/frontend/` | Legacy (ADR-013) | Out of product UI freeze; DEC-019 canonical is `frontend/` |

---

## 14. Known limitations

1. **Mode A hedge UI** masih memuat credential/auth surfaces untuk lab — bukan AuthN enterprise Mode B.
2. **Tidak ada klaim WCAG certification** tanpa audit formal.
3. **UX specs formal** belum lengkap (OD-FE-005) — baseline as-built di kode + dokumen ini.
4. **Dual-SoT complaint** (DEC-020): Aggregate UI berdampingan foundation; freeze tidak berarti force-merge namespace.
5. **Dark mode** token-ready, UI toggle tidak diaktifkan.
6. **Stack governance** (OD-FE-001 / ADR-013 vs DEC-019) tetap open di Architecture — tidak membuka UI redesign.

---

## 15. Future change policy (summary)

> **Default = no UI change.**  
> Exception = bug visual · a11y · BR baru · API visualization · UAT nyata.  
> Prefer token / shared component / copy fix.  
> Never redesign locked Dashboard, Shell, Workspace, Shared UI, or Design System for taste.

---

## 16. Final recommendation

1. Treat this document as the **official UI freeze** for Complaint Module product UI in `frontend/`.
2. Route all UI work through the Change Policy gate; reject “drive-by redesign” prompts.
3. Continue **non-UI** delivery (domain completeness, tests, ops, Mode A lab hygiene) without reopening visual language.
4. Close documentation gaps (OD-FE-005 screen inventory; formal a11y audit) **without** changing locked visuals unless a gate fires.
5. Mode B chrome/AuthN remains **Board-gated CLOSED** — UI freeze does not unlock it.

---

## Traceability

| Artifact | Relationship |
|---|---|
| FE-ARCH-001 v1.2 | Architecture BASELINE — module posture; this freeze binds product visual baseline |
| FE-STD-001 v1.0 | Development standards BASELINE |
| DEC-019 | Canonical `frontend/` tree |
| ADR-014 / ADR-015 | Business module + identity ownership; Mode B CLOSED |
| `frontend/src/shared/README.md` | Design System v1.0 engineering notes |
| ECMP-UX-2.1 | Last cohesion polish before freeze |

---

*End of ECMP-UI-BASELINE-001 — Official UI Freeze.*
