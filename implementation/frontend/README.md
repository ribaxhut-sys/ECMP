# ECMP Frontend (Sprint-04)

Case Detail Workspace (`UX-SCR-001`) — React 18 + TypeScript SPA per `ADR-013`.

## Run locally

```bash
cd implementation/frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173/cases/<caseId>` (queue screen is out of scope; there is no list at `/`).

Backend must be running on `http://localhost:8000`. The Vite dev server proxies `/v1` to it (see `vite.config.ts`) so CORS is not required on the backend.

## Environment variables

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | API origin. Leave empty in local dev to use the Vite proxy. |
| `VITE_DEV_TOKEN` | Bearer token for `AuthContext` (dev-mode stub). Must match a backend static fixture. |

### Dev tokens (mirror `implementation/backend/app/auth.py`)

| Token | userId | Permissions |
|---|---|---|
| `dev-token` | `cs.agent.1` | `cases:create`, `cases:read` |
| `dev-readonly-token` | `viewer.1` | `cases:read` |
| `dev-supervisor-token` | `supervisor.1` | `cases:assign`, `cases:read`, `cases:create`, `dashboard:read` (+ supervised `UNIT-01`) |
| `dev-handler-token` | `USR-2001` | `cases:status`, `cases:read` |
| `dev-noperm-token` | `noperm.1` | (none) |
| `dev-foreign-supervisor-token` | `supervisor.other` | `cases:assign`, `cases:read`, `dashboard:read` (+ supervised `UNIT-99`) |

## Known limitations (not bugs)

- **Auth stub** — token acquisition is unresolved (`ADR-013` item 7). `AuthContext` reads `VITE_DEV_TOKEN`; there is no login screen.
- **Queue + CAP-007 dashboard** — Case queue at `/` uses API-005; Operational queues panel uses API-040 when `dashboard:read` is present (B2-14). Not API-390 / API-513.
- **No live updates** — case state updates only on load or after a successful/409 action (Screen Spec §8).
- **Activity timeline** — placeholder only; no audit-log read API.
- **Customer panel** — degraded to `customerId` + `customerVerified` (API-010 deferred).

## Scripts

- `npm run dev` — Vite dev server
- `npm run build` — typecheck + production build
- `npm run typecheck` — `tsc --noEmit`
- `npm run lint` — ESLint

## Sources of truth

- Stack: `05 Architecture Decision Records/ECMP_ADR_013_Frontend_Technology_Stack_v1.0.md`
- Screen: `12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` (`UX-SCR-001`)
- Contract: `07 API Catalog/openapi/case-service.v1.yaml` v1.5.0 (unchanged)
- Plan: `implementation/frontend/IMPLEMENTATION_PLAN.md`
