# ECMP Frontend

Next.js 15 + React 19 + Tailwind CSS 4 application for the Enterprise Complaint Management Platform.

## Quick start

```bash
cp .env.example .env.local
npm install
npm run dev
```

Requires the backend at `NEXT_PUBLIC_API_BASE_URL`.
For local `next dev`, if unset, the client falls back to `http://localhost:8000`.
Production / Docker builds **require** an explicit `NEXT_PUBLIC_API_BASE_URL` (no silent default).

## Sprint F1 — Foundation

See **[SPRINT_F1.md](./SPRINT_F1.md)** for auth, routing, Axios client, and shell deliverables.

## Sprint F2 — Complaints

See **[SPRINT_F2.md](./SPRINT_F2.md)** for list / detail / create / edit against frozen complaint APIs.

## Sprint F3 — Queue

See **[SPRINT_F3.md](./SPRINT_F3.md)** for the complaint work-queue dashboard against frozen APIs.

## Sprint F4 — Assignments

See **[SPRINT_F4.md](./SPRINT_F4.md)** for assignment list + assign/reassign/cancel against frozen APIs.

## Sprint F5 — Resolutions

See **[SPRINT_F5.md](./SPRINT_F5.md)** for resolution workflow list + supported close/escalate actions.

| Area | Location |
|---|---|
| Auth session | `src/auth/AuthProvider.tsx` |
| Axios + interceptors | `src/lib/api/client.ts` |
| Protected shell | `src/shared/layouts/app-layout/` |
| Login shell | `src/shared/layouts/auth-layout/` + `src/app/login/` |
| Global loading / errors | `src/shared/providers/` + `GlobalLoadingBar` |
| Complaints module | `src/features/complaints/`, `src/app/(app)/complaints/` |
| Queue module | `src/features/queue/`, `src/app/(app)/queue/` |
| Assignments module | `src/features/assignments/`, `src/app/(app)/assignments/` |
| Resolutions module | `src/features/resolutions/`, `src/app/(app)/resolutions/` |
| Reports module | `src/features/reports/`, `src/app/(app)/reports/` (API-210…212) |
| CM Batch 1 Aggregate client | `src/lib/api/cmBatch1.ts` (`/api/v1/cm` — DEC-020; **not** a replace for `complaints.ts`) |
| Design system | `src/shared/ui`, `src/shared/theme` |

See **[src/shared/README.md](./src/shared/README.md)** for design tokens and layout rules.

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Local development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | ESLint (max-warnings 0) |
| `npm run typecheck` | TypeScript `--noEmit` |
| `npm run test` | Vitest unit tests |
| `npm run test:coverage` | Vitest + Phase C coverage hard-fail thresholds |
| `npm run test:a11y` | axe-core smoke on shared UI (warn-mode in CI) |
