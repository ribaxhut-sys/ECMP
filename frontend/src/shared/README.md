# ECMP Frontend Foundation

**EPIC-01 / Sprint-01 — Design System & Responsive Layout**

This document explains the shared frontend architecture under `frontend/src/shared/`. Future modules must build on this foundation instead of inventing local UI primitives.

## Folder structure

```
frontend/src/
  app/                      # Next.js App Router
    (app)/                  # Authenticated routes → AppLayout
      dashboard/
      complaints/
      attachments/          # Attachment Viewer (TASK-032)
      reports/
      users/
      settings/
    login/                  # AuthLayout
  auth/                     # AuthProvider (session / permissions)
  features/                 # Feature modules (dashboard, attachments, …)
  lib/api/                  # Axios client + domain API modules
  shared/
    providers/              # AppProviders, ToastProvider (global errors)
    theme/                  # Design tokens (TS mirrors of CSS vars)
    ui/                     # Design-system components + GlobalLoadingBar
    layouts/                # AppLayout, AuthLayout
    icons/                  # Shared SVG icons
    hooks/                  # useMediaQuery, useSidebar
    utils/                  # cn(), helpers
```

Imports:

```ts
import { Button, Card, PageHeader, PageContainer } from "@/shared/ui";
import { AppLayout, AuthLayout } from "@/shared/layouts";
import { colors, spacing } from "@/shared/theme";
```

## Design principles

1. **Tokens first** — Colors, spacing, radius, shadows, and typography live in CSS variables (`globals.css`) and TypeScript mirrors (`shared/theme`). Components must not hardcode hex colors or one-off spacing.
2. **Compose, don’t copy** — Prefer shared `ui/*` over feature-local buttons, badges, tables, alerts, etc.
3. **One shell** — Authenticated pages use `AppLayout` (via `app/(app)/layout.tsx`). Auth screens use `AuthLayout`.
4. **Accessible by default** — Labels, focus rings, ARIA roles, keyboard-dismissible modal, 44×44px touch targets, 16px minimum body text.
5. **Responsive, not separate apps** — Same components adapt across `sm` / `md` / `lg` / `xl` / `2xl`.

## Design tokens

| Category | Tokens |
|---|---|
| Colors | primary, secondary, success, warning, danger, info, surface, background, border, text-primary, text-secondary |
| Spacing | 4, 8, 12, 16, 24, 32, 40, 48, 64 (px) |
| Radius | sm, md, lg, xl |
| Shadow | sm, md, lg |
| Typography | display, heading, title, subtitle, body (16px+), caption |

Tailwind theme keys use the `ecmp-` prefix, e.g. `bg-ecmp-primary`, `text-ecmp-text-secondary`, `border-ecmp-border`, `shadow-ecmp-md`, `rounded-[var(--ecmp-radius-md)]`.

## Shared UI catalog

| Component | Purpose |
|---|---|
| `Button` | Primary actions (min 44×44 touch) |
| `Input` / `Textarea` / `Select` | Labeled form controls |
| `Card` (+ Header/Title/Body) | Section containers |
| `Badge` | Status / priority chips |
| `Alert` | Inline notices |
| `Modal` | Dialogs (Escape + overlay close) |
| `Table` | Desktop table → mobile stacked cards |
| `Loading` / `Skeleton` | Async placeholders |
| `GlobalLoadingBar` | Top bar while Axios requests are in flight |
| `Empty` / `ErrorState` | Empty & error UX |
| `Breadcrumb` / `PageHeader` / `PageContainer` | Page chrome |
| `Toast` | Transient success / status notifications |

Barrel: `@/shared/ui`.

## Application layout

```
┌─────────────────────────────────────┐
│ Header (logo / search / user / …)   │
├──────────┬──────────────────────────┤
│ Sidebar  │ Content                  │
│          │  Breadcrumb              │
│          │  Page Header             │
│          │  Main                    │
└──────────┴──────────────────────────┘
```

- **Desktop (`lg+`)**: persistent sidebar
- **Mobile / tablet**: drawer navigation (menu button in header)
- Header includes: logo area, complaint search (API-388 via `/complaints?keyword=`), notifications placeholder, current user, theme switch placeholder, logout

## Responsive strategy

| Concern | Mobile | Tablet | Desktop |
|---|---|---|---|
| Sidebar | Drawer | Drawer | Persistent |
| Summary cards | 1 / row | 2 / row (`sm`) | 4 / row (`lg`) |
| Tables | Stacked cards | Table (`md+`) | Table |
| Forms | 1 column | 2 columns when appropriate (`md:grid-cols-2`) | 2 columns |
| Buttons | ≥ 44×44 | ≥ 44×44 | ≥ 44×44 |
| Body text | ≥ 16px | ≥ 16px | ≥ 16px |

Avoid horizontal overflow: `overflow-x-hidden` on shells; tables switch to cards below `md`.

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
4. Import only from `@/shared/ui`, `@/shared/layouts`, `@/shared/theme`, `@/shared/icons`, `@/shared/hooks`.
5. Do **not** reintroduce feature-local Panel/Badge/Button CSS.
6. Do **not** change backend APIs, auth flow, or invent business features in foundation work.
7. Prefer lazy-loaded heavy feature trees via `next/dynamic` when a module grows.

### Example page skeleton

```tsx
import { PageContainer, PageHeader, Card, CardBody, Empty } from "@/shared/ui";

export default function ExamplePage() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Example"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Example" },
        ]}
        description="Short page purpose."
      />
      <Card>
        <CardBody>
          <Empty title="Ready" description="Implement module content here." />
        </CardBody>
      </Card>
    </PageContainer>
  );
}
```

## Out of scope (foundation sprint)

- Backend / OpenAPI / database changes
- Auth flow changes
- Notifications / theme persistence
- Dedicated global search API (header search uses complaint search via `/complaints?keyword=`)
