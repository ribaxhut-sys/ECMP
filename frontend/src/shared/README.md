# ECMP Frontend Foundation

**Design System v1.0** (UI-02 / Phase 0) — visual foundation tokens.

This document explains the shared frontend architecture under `frontend/src/shared/`. Future modules must build on this foundation instead of inventing local UI primitives.

## Folder structure

```
frontend/src/
  app/                      # Next.js App Router
    globals.css             # Design token source of truth
    (app)/                  # Authenticated routes → AppLayout
  auth/                     # AuthProvider (session / permissions)
  features/                 # Feature modules
  lib/api/                  # Axios client + domain API modules
  shared/
    providers/              # AppProviders, ToastProvider
    theme/                  # TS mirrors of CSS tokens
    ui/                     # Design-system components
    layouts/                # AppLayout, AuthLayout
    icons/                  # Shared SVG icons
    hooks/                  # useMediaQuery, useSidebar
    utils/                  # cn(), helpers
```

Imports:

```ts
import { Button, Card, PageHeader, PageContainer } from "@/shared/ui";
import { AppLayout, AuthLayout } from "@/shared/layouts";
import { colors, spacing, layout, motion, zIndex } from "@/shared/theme";
```

## Design principles

1. **Tokens first** — Colors, spacing, radius, shadows, typography, layout, motion, z-index live in CSS variables (`app/globals.css`) with TypeScript mirrors (`shared/theme`). No hardcoded hex / one-off spacing in feature UI.
2. **Compose, don’t copy** — Prefer shared `ui/*` over feature-local buttons, badges, tables, alerts.
3. **One shell** — Authenticated pages use `AppLayout`. Auth screens use `AuthLayout`.
4. **Accessible by default** — One focus ring, ARIA roles, 44×44px touch targets, 16px minimum body text, WCAG AA contrast on token pairs.
5. **Responsive, not separate apps** — Same components adapt across breakpoints.
6. **Professional over decorative** — Enterprise SaaS (Linear / Stripe / GitHub), not marketing or glassmorphism.

---

## Design System v1.0

**Source of truth:** `frontend/src/app/globals.css`  
**TS mirrors:** `frontend/src/shared/theme/`  
**Prefix:** `--ecmp-*` — existing keys are never renamed; new keys extend only.

### Color tokens

| Group | Tokens |
|---|---|
| Brand | `primary`, `primary-foreground`, `primary-muted`, `secondary` (+ foreground/muted) |
| Semantic actions | `success`, `warning`, `danger`, `info` (+ foreground/muted) |
| Surfaces | `background`, `surface`, `surface-raised`, `surface-sunken`, `surface-floating`, `surface-overlay` |
| Interaction | `hover`, `selected`, `pressed`, `disabled`, `muted` |
| Semantic states | `{success\|warning\|danger\|info}-{bg\|border\|text\|subtle}` |
| Text / chrome | `text-primary`, `text-secondary`, `border`, `focus` |

Tailwind: `bg-ecmp-surface-raised`, `text-ecmp-success-text`, `bg-ecmp-hover`, `text-ecmp-muted`, …

**Usage**
- Page canvas → `background`
- Cards / panels → `surface` + `shadow-raised`
- Nested wells → `surface-sunken`
- Dropdowns / popovers → `surface-floating` + `shadow-floating`
- Modal scrim → `surface-overlay` (alias: `overlay`)

### Typography

| Role | Size | Weight | Line height | Token |
|---|---|---|---|---|
| Display | 2.25rem | 700 | 1.2 | `--ecmp-font-display-*` |
| Page Title | 1.875rem | 700 | 1.25 | `--ecmp-font-page-title-*` (aliases `heading`) |
| Section Title | 1.25rem | 600 | 1.35 | `--ecmp-font-section-title-*` (aliases `title`) |
| Card Title | 1.125rem | 600 | 1.4 | `--ecmp-font-card-title-*` |
| Body | 1rem (16px min) | 400 | 1.5 | `--ecmp-font-body-*` |
| Body Small | 0.875rem | 400 | 1.45 | `--ecmp-font-body-small-*` |
| Label | 0.875rem | 600 | 1.4 | `--ecmp-font-label-*` |
| Helper | 0.8125rem | 400 | 1.4 | `--ecmp-font-helper-*` |
| Caption | 0.875rem | 400 | 1.4 | `--ecmp-font-caption-*` |
| Overline | 0.75rem | 600 | 1.35 | `--ecmp-font-overline-*` (+ tracking 0.06em) |

Family: Source Sans 3 / system sans (`--ecmp-font-family`).

### Spacing scale

Keep: **4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64** px.

| Use | Prefer |
|---|---|
| Tight control padding | 4–8 |
| Field / list gaps | 12–16 |
| Section rhythm | 24–32 |
| Page blocks | 40–64 |

Do not invent values outside the scale.

### Layout tokens

| Token | Default | Purpose |
|---|---|---|
| `--ecmp-page-gutter` | 16px | Horizontal page padding |
| `--ecmp-section-gap` | 24px | Between major sections |
| `--ecmp-panel-gap` | 16px | Inside split panels |
| `--ecmp-card-gap` | 16px | Between cards |
| `--ecmp-dashboard-gap` | 24px | Dashboard grid rhythm |
| `--ecmp-form-gap` | 16px | Form field stack |
| `--ecmp-content-max-width` | 80rem | Constrained content |
| `--ecmp-form-max-width` | 42rem | Narrow forms |
| `--ecmp-sidebar-width` | 16rem | App sidebar |
| `--ecmp-header-height` | 4rem | Sticky header |
| `--ecmp-touch-min` | 44px | Min touch target |

Phase 0 defines tokens only — page components migrate in later phases.

### Radius system

Scale: **sm 4 · md 8 · lg 12 · xl 16 · full**.

| Role | Token | Value |
|---|---|---|
| Button / Input / Select / Textarea / Dropdown | `--ecmp-radius-{role}` | 8 (md) |
| Badge | `--ecmp-radius-badge` | 4 (sm) |
| Card / Table / Surface | `--ecmp-radius-card` etc. | 12 (lg) |
| Modal / Dialog | `--ecmp-radius-modal` | 16 (xl) |

### Elevation

| Level | Token | Intended use |
|---|---|---|
| Surface | `--ecmp-shadow-surface` | Flat on background (`none`) |
| Raised | `--ecmp-shadow-raised` | Cards, table shells |
| Floating | `--ecmp-shadow-floating` | Dropdowns, popovers |
| Overlay | `--ecmp-shadow-overlay` | Modals |
| Hover | `--ecmp-shadow-hover` | Interactive lift |

Legacy `sm` / `md` / `lg` remain for existing classNames. Soft shadows only.

### Z-index

| Layer | Token | Value |
|---|---|---|
| Sticky header | `--ecmp-z-sticky-header` | 30 |
| Dropdown | `--ecmp-z-dropdown` | 40 |
| Sidebar (drawer) | `--ecmp-z-sidebar` | 50 |
| Scrim | `--ecmp-z-overlay` | 55 |
| Modal | `--ecmp-z-modal` | 60 |
| Toast | `--ecmp-z-toast` | 65 |
| Loading bar | `--ecmp-z-loading` | 70 |

No magic numbers in new UI work.

### Motion

| Token | Value |
|---|---|
| `--ecmp-duration-fast` | 120ms |
| `--ecmp-duration-normal` | 200ms |
| `--ecmp-duration-slow` | 300ms |
| `--ecmp-ease-standard` | cubic-bezier(0.2, 0, 0, 1) |
| `--ecmp-ease-enter` | cubic-bezier(0, 0, 0.2, 1) |
| `--ecmp-ease-exit` | cubic-bezier(0.4, 0, 1, 1) |
| `--ecmp-ease-hover` | cubic-bezier(0.2, 0, 0, 1) |

**Rules:** hover / card / modal / dropdown / toast / loading only. Never animate whole pages. `prefers-reduced-motion: reduce` is applied globally in `globals.css`.

### Focus

One ring for the app:

- Width `--ecmp-focus-ring-width` (2px)
- Offset `--ecmp-focus-ring-offset` (2px)
- Color `--ecmp-focus-ring-color` (= focus / primary)

`:focus { outline: none }` · `:focus-visible` uses the ring. Do not invent alternate focus styles.

### Density

| Mode | Row | Gap | Cell Y |
|---|---|---|---|
| Comfortable | 48px | 16px | 12px |
| Compact | 36px | 8px | 8px |

Tokens only — no density switch UI in Phase 0.

### Dark-ready

`.dark { … }` mirrors all color and shadow tokens.  
**Not enabled:** Header theme toggle stays disabled; do not wire a theme provider in Phase 0.

### Icon rules

| Size | CSS var | Tailwind | Use |
|---|---|---|---|
| 16 | `--ecmp-icon-size-16` | `size-4` | Dense chrome, breadcrumbs |
| 20 | `--ecmp-icon-size-20` | `size-5` | Default UI / nav (IconBase default) |
| 24 | `--ecmp-icon-size-24` | `size-6` | Emphasis, empty-state icons |

Stroke width: **1.75** (`--ecmp-icon-stroke`). ViewBox 24×24. Phase 0 does not rewrite icon components.

### Interaction language (guidance)

| State | Guidance |
|---|---|
| Loading | Skeleton / spinner using motion tokens; top `GlobalLoadingBar` for Axios |
| Empty | `Empty` — dashed surface, calm copy, optional single action |
| Success | `success-*` semantic tokens; Toast or Alert |
| Warning | `warning-*` tokens; never rely on color alone |
| Error | `danger-*` + `ErrorState` for page/list failures; `Alert` for inline |
| Info | `info-*` for neutral operational notices |

Page migration of these patterns continues in Phase 2–3 (adopt shared primitives; remove local duplicates).

---

## Component Library v1 (Phase 1)

Barrel: `@/shared/ui`. All primitives consume Design System tokens (color, radius, elevation, motion, layout, focus). No new hardcoded colors or spacing systems.

### Catalog

| Component | Purpose |
|---|---|
| `FormField` | Unified label / description / helper / error chrome |
| `Input` / `Textarea` / `Select` | Text controls via `FormField` |
| `Checkbox` / `Radio` / `RadioGroup` | Choice controls |
| `Button` | `primary` `secondary` `outline` `ghost` `danger` `success` · `sm` `md` `lg` |
| `Card` (+ Header/Title/Description/Body/Footer) | Surfaces; `interactive` hover elevation |
| `Badge` | `soft` `solid` `outline` × semantic tones |
| `Alert` | Compact inline banner (info/success/warning/danger + dismiss/actions); not a card |
| `Modal` | Dialogs (Escape + overlay close) |
| `Table` | Sticky header, row hover, density, loading/empty, selection highlight (presentation) |
| `Loading` / `Spinner` / `Skeleton` / `GlobalLoadingBar` | Async feedback |
| `Empty` / `ErrorState` | Empty & error UX (+ secondary action) |
| `Breadcrumb` / `PageHeader` / `PageContainer` | Page chrome (layout tokens) |
| `SectionHeader` / `PanelHeader` | In-page section / panel titles |
| `StatCard` / `MetricCard` | KPI tiles (trend/delta/status slots) |
| `FilterBar` | Search / filters / actions / export / reset slots |
| `Timeline` | Activity list (presentation only) |
| `Pagination` | Prev/next/pages/summary/page-size slots (no fetch logic) |
| `Toast` | Transient notifications |

### New components (Phase 1)

`FormField`, `Checkbox`, `Radio`/`RadioGroup`, `CardFooter`, `Spinner`, `SectionHeader`, `PanelHeader`, `StatCard`/`MetricCard`, `FilterBar`, `Timeline`, `Pagination`.

### Usage rules

1. Prefer shared primitives over feature-local buttons, badges, filter bars, pagination, and stat tiles.
2. Forms: use `Input`/`Select`/`Textarea`/`Checkbox`/`RadioGroup` (they wrap `FormField`). Do not re-implement label/error rows.
3. Tables: pass `loading` / `emptyMessage` / `density`; keep sort/filter/page fetch in the feature.
4. `FilterBar` / `Pagination` / `Timeline` / `StatCard` are **slots + chrome only** — parents own state and API calls.
5. Buttons: use color + elevation hover (not opacity-only). Use `success` for positive confirms when needed.
6. Badges: prefer `soft` for status chips; `solid` for emphasis; `outline` for secondary tags.

### Composition rules

```tsx
<PageContainer>
  <PageHeader title="…" breadcrumbs={…} actions={…} />
  <FilterBar search={…} filters={…} actions={…} />
  <Table columns={…} rows={…} getRowKey={…} loading={…} />
  <Pagination summary={…} onPrevious={…} onNext={…} />
</PageContainer>
```

```tsx
<Card>
  <CardHeader action={…}>
    <CardTitle>…</CardTitle>
    <CardDescription>…</CardDescription>
  </CardHeader>
  <CardBody>…</CardBody>
  <CardFooter>…</CardFooter>
</Card>
```

### Accessibility notes

- One global `:focus-visible` ring (Design System). Do not invent per-control rings that diverge.
- Touch targets ≥ `--ecmp-touch-min` (44px) on interactive controls.
- `Button` exposes `aria-busy` when `loading`; form controls set `aria-invalid` / `aria-describedby`.
- `Table` empty state uses `Empty`; loading uses `Skeleton`.
- `RadioGroup` uses `role="radiogroup"` with labelled options.
- Motion respects `prefers-reduced-motion` (global CSS).

## Application Shell v1 (Phase 2)

```
┌─────────────────────────────────────┐
│ Header (sticky · search · user)     │
├──────────┬──────────────────────────┤
│ Sidebar  │ main#main-content        │
│ groups   │  PageContainer           │
│ active   │    Breadcrumb            │
│ indicator│    PageHeader            │
│          │    Section / Panel       │
└──────────┴──────────────────────────┘
```

### Layout rules

- Canvas: `bg-ecmp-background`; chrome surfaces: `bg-ecmp-surface`
- Content width: `PageContainer` → `--ecmp-content-max-width` + `--ecmp-page-gutter`
- Section rhythm: `--ecmp-section-gap` / `--ecmp-panel-gap` via `PageHeader` / `SectionHeader` / `PanelHeader`
- Z-index: sticky header / sidebar / dropdown / loading from Design System tokens only
- Skip link to `#main-content` in `AppLayout`

### Sidebar rules

- Same routes and menu membership as before (no route/menu product changes)
- Visual groups only: Operations · Workspace · Administration (`APP_NAV_GROUPS`)
- Active: `bg-ecmp-selected` + left indicator bar + primary icon/text
- Hover: `bg-ecmp-hover`; motion via `--ecmp-duration-fast`
- Desktop (`lg+`): persistent; below `lg`: drawer + overlay (`--ecmp-z-sidebar`)
- Brand links to `/dashboard` (desktop + mobile)

### Header rules

- Sticky + `shadow-ecmp-raised` + translucent surface
- Search uses sunken field surface; mobile search expands as floating panel
- Notifications + theme controls remain **disabled** placeholders
- User chip is a single focusable control to `/profile`
- Dark toggle not wired

### Auth layout rules

- Layered sunken/surface background; no illustrations; no heavy gradients
- Content capped at `--ecmp-form-max-width`
- Pages supply their own `Card` content (shell does not double-wrap)

### Responsive rules

| Breakpoint | Sidebar | Header | Content |
|---|---|---|---|
| Mobile | Drawer | Compact actions + search toggle | Full width + page gutter |
| Tablet | Drawer | Search from `md` | Constrained when using `PageContainer` |
| Desktop `lg+` | Persistent | Full search + user chip | `max-w` content |

No horizontal overflow: shell uses `overflow-x-hidden` / `min-w-0`.

## Responsive strategy

| Concern | Mobile | Tablet | Desktop |
|---|---|---|---|
| Sidebar | Drawer | Drawer | Persistent |
| Summary cards | 1 / row | 2 / row (`sm`) | 4 / row (`lg`) |
| Tables | Stacked cards | Table (`md+`) | Table |
| Forms | 1 column | 2 columns when appropriate | 2 columns |
| Buttons | ≥ 44×44 | ≥ 44×44 | ≥ 44×44 |
| Body text | ≥ 16px | ≥ 16px | ≥ 16px |

### Form layout pattern

```tsx
<div className="grid grid-cols-1 gap-4 md:grid-cols-2">
  <Input label="Branch" name="branch" />
  <Select label="Priority" name="priority" options={…} />
  <Textarea className="md:col-span-2" label="Description" name="description" />
</div>
```

## How future modules must use this

1. Place feature code under `features/<module>/`.
2. Add routes under `app/(app)/<module>/` so they inherit `AppLayout` + auth gate.
3. Build screens with `PageContainer` → `PageHeader` → shared `Card` / `Table` / form controls.
4. Import from `@/shared/ui`, `@/shared/layouts`, `@/shared/theme`, `@/shared/icons`, `@/shared/hooks`.
5. Do **not** reintroduce feature-local Panel/Badge/Button CSS or hardcoded colors.
6. Do **not** change backend APIs, auth flow, or invent business features in foundation work.
7. Consume z-index / motion / radius role tokens instead of magic numbers.

## Phase notes

### Phase -1 — Visual Inventory (approved)

Identified incomplete tokens, missing elevation/motion/dark/layout/density/z-index, duplicated list chrome, native form controls.

### Phase 0 — Design System v1.0 (approved)

- Extended tokens in `globals.css` + `shared/theme/*`
- Dark-ready `.dark` mirror (toggle not wired)
- Global focus ring + `prefers-reduced-motion`

### Phase 1 — Component Library v1 (approved)

- Elevated shared UI to consume Design System tokens
- Unified form chrome via `FormField`
- Added StatCard, FilterBar, Timeline, Pagination, SectionHeader, PanelHeader, Checkbox, Radio

### Phase 2 — Application Shell v1 (approved)

- Modernized `AppLayout`, `Sidebar`, `Header`, `AuthLayout`
- Visual nav groups (same routes); skip link; sticky elevated header
- Page chrome spacing aligned to layout tokens

### Phase 3 Wave A — operational pages (approved)

Pages migrated (presentation only):

| Page | Shared adoption |
|---|---|
| Dashboard | `StatCard`, `SectionHeader`, layout hierarchy (KPI → widgets → activity) |
| Complaint List | `FilterBar`, `Pagination`, `Table`, `Empty`, `Skeleton` |
| Complaint Detail | `SectionHeader`, section grouping, `Timeline` (via TimelineCard), badges |
| Queue Dashboard | `StatCard`, `FilterBar`, `Pagination`, `Checkbox`, `Alert` |
| Create Complaint | `SectionHeader`, form spacing tokens, `Alert` / `Card` |

### Phase 3 Wave B — operational pages (approved)

Pages migrated (presentation only):

| Page | Shared adoption |
|---|---|
| Assignments | `FilterBar`, `Pagination`, `Table`, `Empty`, `Skeleton`, `Badge` |
| Resolutions | `FilterBar`, `Pagination`, `Checkbox`, `Select`, `FormField` controls |
| Reports | `StatCard`, `SectionHeader`, layout spacing tokens (no new charts/metrics) |
| Attachments | `FilterBar`, `Card`, `Badge`, `Alert`, `Empty`, `Skeleton`, metadata hierarchy |
| Supervisor (CM Batch-1) | `FilterBar`, `Select`, `StatCard`, `SectionHeader`, `Table`, `Badge` |
| Confirmation (CM Batch-1) | `SectionHeader`, `Card`, `Badge`, `Alert`, `Empty` |
| Cases / Case Detail | `SectionHeader`, `Card`, status badge, spacing/token hierarchy |
| Bound attachments (CM) | `SectionHeader`, `Badge`, `Empty`, sunken void form |

### Phase 3 Wave C — administration & authentication (approved)

Pages migrated (presentation only):

| Page | Shared adoption |
|---|---|
| Users | `PageContainer`, `PageHeader`, `SectionHeader`, `Table`, `Badge`, `Modal`, `Alert` |
| System Settings | `SectionHeader`, `Card`, `Table`, `Badge`, `Input`, `Skeleton` |
| SLA Settings | `SectionHeader`, `Card`, `Table`, `Badge`, create form spacing / sunken well |
| Settings (language) | `SectionHeader`, `Card`, layout tokens |
| Profile | `SectionHeader`, account metadata hierarchy, security link buttons |
| Security / Change Password | `SectionHeader`, `FormField` inputs, form max-width |
| Login / Forgot / Reset Password | `AuthLayout`, typography tokens, form-gap, focusable links |
| 404 / App error | token spacing + primary CTA styling |
| Edit Complaint (remaining) | `SectionHeader`, form / section spacing tokens |

Not present in this repo (no page to migrate): Roles, Organization Settings, User Detail.

No API / hook / route / permission / business-logic / auth-logic changes. Phase 3 page redesign complete.

### Final Visual QA (UI-08) — completed

Quality pass (not a redesign). Remaining presentation drift aligned to Design System tokens and shared UI.

**Consistency checklist**

| Area | Result |
|---|---|
| Spacing | Feature/app surfaces use `--ecmp-section-gap` / `panel-gap` / `form-gap` / `card-gap` |
| Typography | Body/helper/overline/page-title tokens; overline tracking tokenized |
| Radius / surfaces | `rounded-[var(--ecmp-radius-md)]`, sunken wells for nested forms |
| Badges | Shared `Badge` on staging/list status metadata |
| Forms | Shared `Checkbox` / `RadioGroup` / `FormField` controls (no native leftovers in feature panels) |
| Empty / loading / error | Shared `Empty`, `Skeleton`, `Alert` / `ErrorState` |
| Cards / headers | `SectionHeader` for page sections; `PanelHeader` for dashboard card chrome |
| Motion | Token durations (`--ecmp-duration-fast`); no custom `duration-150` |
| Color | `bg-ecmp-surface` (no `bg-white`); text tokens (`text-primary` / `text-secondary`) |

**Polish hotspots addressed:** StagingAttachments, CustomerSearch, DuplicateWarning, FinalResolution, dashboard widgets, KPI card, Report summary shells, Create Complaint section grouping, AttachmentViewer.

**Acceptable exceptions:** print-window HTML in admin password reset; AuthLayout decorative layers; Header search chrome; shared primitive padding (`Card`/`Modal`).

### Later phases

- Phase 4 (optional): micro-interactions polish beyond token motion

## Out of scope (Phase 0–1 foundation)

- Backend / OpenAPI / database / events
- Auth flow / permissions / routes / hooks / stores
- Feature page composition changes
- Enabling dark mode toggle
- Porting from `implementation/frontend`
