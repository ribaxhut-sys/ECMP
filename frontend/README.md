# ECMP Frontend

Next.js 15 + React 19 + Tailwind CSS 4 application for the Enterprise Complaint Management Platform.

## Quick start

```bash
npm install
npm run dev
```

## Architecture

v1.1 frontend foundation lives in `src/shared/`:

- Design tokens → `src/shared/theme`
- Design system components → `src/shared/ui`
- App / Auth layouts → `src/shared/layouts`

See **[src/shared/README.md](./src/shared/README.md)** for folder structure, design principles, responsive rules, and how future modules must consume the shared layer.

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Local development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | Next.js lint |
