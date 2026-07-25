# Sprint F1 — Frontend Foundation

**Status:** Complete  
**Scope:** Authentication shell, routing, Axios API client, dashboard layout.  
**Out of scope:** Complaint CRUD screens (do not start in F1).

## Deliverables

### 1. Folder structure

```
frontend/src/
  app/
    (app)/                 # Protected routes (RequireAuth + AppLayout)
      layout.tsx
      dashboard/           # Post-login home
      …                    # Later modules mount here
    login/                 # Public login route
    layout.tsx             # AppProviders (auth + toast + loading)
  auth/
    AuthProvider.tsx       # Session state (login / logout / me / refresh)
  lib/api/
    client.ts              # Axios instance + interceptors
    auth.ts                # /api/v1/auth/* wrappers
    types.ts
  shared/
    layouts/
      app-layout/          # Sidebar, Header, RequireAuth, shell
      auth-layout/         # Centered login shell
    providers/             # AppProviders, ToastProvider
    ui/                    # Design-system primitives + GlobalLoadingBar
  features/
    dashboard/             # Dashboard view (live API)
```

### 2. Routing

| Route | Access | Shell |
|---|---|---|
| `/` | redirect → `/dashboard` | — |
| `/login` | Public | `AuthLayout` |
| `/dashboard` | Protected | `AppLayout` (Sidebar + Header) |
| `/complaints/*`, `/reports`, … | Protected (shell only; feature work is later sprints) | `AppLayout` |

Protection: `app/(app)/layout.tsx` → `AuthenticatedShell` → `RequireAuth` → `AppLayout`.

### 3. Authentication flow

1. Bootstrap: `AuthProvider` calls `POST /api/v1/auth/refresh` (HttpOnly cookie) → `GET /api/v1/auth/me`.
2. Login: form → `POST /api/v1/auth/login` → store access token in memory → load `/me` → `/dashboard`.
3. Logout: `POST /api/v1/auth/logout` → clear token → `/login`.
4. Protected routes: unauthenticated users redirected to `/login`.

Backend contracts used (unchanged): login, refresh, logout, me.

### 4. API client

- **Axios** instance (`axiosClient`) with `withCredentials: true` for refresh cookie.
- **Request interceptor:** attach `Authorization: Bearer <accessToken>`; track pending count.
- **Response interceptor:** on `401`, single-flight refresh + retry; map failures to `ApiError`; emit global toast for network/5xx.
- Module helpers keep the existing `apiRequest` / `apiRequestBlob` surface.

### 5. State management

| Concern | Mechanism |
|---|---|
| Auth session / user / permissions | React Context (`AuthProvider`) |
| Access token | In-memory module store (not localStorage) |
| Refresh token | HttpOnly cookie (backend-owned) |
| Global loading | Axios pending counter → `GlobalLoadingBar` |
| Global errors | Axios error subscribers → `ToastProvider` |
| Screen data | Feature hooks / local state (TanStack not required for F1) |

### 6. Visual verification (desktop-first)

**Login (`/login`)**  
Centered ECMP card: brand label, “Sign in” heading, username/email + password fields, full-width primary CTA. Soft slate background; no sidebar.

**Authenticated shell (`/dashboard`)**  
Persistent left sidebar (ECMP brand + nav) on `lg+`; sticky header with search placeholder, user chip, Logout. Main content: Dashboard page header + live summary cards / SLA / recent activity. Top teal progress bar appears while Axios requests are in flight. Network/5xx failures surface as a danger toast (top-right).

**Mobile / tablet**  
Sidebar collapses to a drawer opened from the header menu button.

### 7. Commit

See git commit hash produced for this sprint.
