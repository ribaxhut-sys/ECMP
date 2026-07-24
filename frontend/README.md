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

## Features

### Attachment Viewer (TASK-032)

Platform attachment UI under `src/features/attachments/`:

| Component | Role |
|---|---|
| `AttachmentList` | Loads metadata by ID list (or accepts preloaded rows) |
| `AttachmentCard` | Filename, size, MIME, upload date, Preview / Download / New tab |
| `AttachmentViewer` | Lazy modal preview (image zoom, PDF browser iframe) |

Route: `/attachments?ids=<uuid>[,<uuid>…]`

#### API usage (existing only — no new endpoints)

| Action | API |
|---|---|
| Metadata | `GET /api/v1/attachments/{id}` (API-324) |
| Preview / Download / New tab | `GET /api/v1/attachments/{id}/download` (API-325) |

Bytes are fetched **only** when the user opens Preview, Download, or Open in new tab.

Previewable: `jpg`, `jpeg`, `png`, `gif`, `webp`, `pdf`.  
Unsupported (icon + download): `doc`, `docx`, `xls`, `xlsx`, `zip`, `rar`, `ppt`, `pptx`, others.

Permission: `attachment:read`.

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Local development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | Next.js lint |
