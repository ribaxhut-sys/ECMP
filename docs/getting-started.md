# Getting Started

| Field | Value |
|---|---|
| ID | EAR-PORTAL-002 |
| Version | 0.3 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Untuk anggota baru
1. Baca Glossary
2. Baca Business Blueprint
3. Buka Decision Tree
4. Lihat Dashboard + Health Report
5. Pelajari AI Rules (`ai-platform/policies/ai-rules.md`)

## Untuk engineer (Cursor)
1. Baca `ai-platform/policies/ai-rules.md`
2. Baca sprint aktif (`ai/sprint/Sprint-01.md`)
3. Baca domain terkait (atau `python tools/eos.py domain --name ECMF`)
4. Implement di `implementation/`
5. Sync OpenAPI/Event/Traceability bila kontrak berubah
6. Jalankan DX launcher:

```bash
python tools/eos.py
```

## Menjalankan portal
```bash
pip install -r requirements-docs.txt
python tools/eos.py --all
python -m mkdocs serve
```
