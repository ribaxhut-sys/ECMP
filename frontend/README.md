# ECMP Frontend

Next.js 15 + React 19 + Tailwind CSS 4 application for the Enterprise Complaint Management Platform.

## Quick start

```bash
cp .env.example .env.local
npm install
npm run dev
```

Requires the backend at `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).

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
| Design system | `src/shared/ui`, `src/shared/theme` |

See **[src/shared/README.md](./src/shared/README.md)** for design tokens and layout rules.

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Local development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | Next.js lint |
