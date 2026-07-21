# Repository Standards

| Field | Value |
|---|---|
| ID | EAR-STD-006 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | PMO / Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## 1. Folder Naming
- Format: `NN Name` (contoh: `04 Solution Architecture`)
- Nomor 2 digit, urutan stabil
- Jangan rename nomor folder tanpa approval Architecture Board

## 2. File Naming
```text
ECMP_<Area>_<DocumentName>_v<Major.Minor>.<ext>
```
Contoh:
- `ECMP_Business_Blueprint_v2.1.docx`
- `ECMP_ADR_001_Event_Driven_Integration_v1.0.md`
- `ECMP_API_Case_Service_v1.0.yaml`

## 3. Versioning
- `Major`: perubahan scope/breaking/baseline baru
- `Minor`: penyempurnaan non-breaking
- ID enterprise (`SA-001`) tetap meski versi naik
- Deprecated version tetap diarsipkan

## 4. Archive
- Jangan hapus artefak approved tanpa jejak
- Pindahkan versi lama ke subfolder `archive/` bila mengganggu navigasi
- Tandai `🔴 Deprecated` + link ke pengganti

## 5. Review
- Ikuti `REVIEW_SCHEDULE.md`
- Metadata `Last Review` / `Next Review` wajib diupdate

## 6. Approval
Default path:
`Author → Reviewer → Owner → Approver (Architecture/Business Gate)`

Baseline (`🟢 Approved`) hanya setelah Approver sign-off.

## 7. Format Policy
- Markdown/YAML/OpenAPI untuk living docs
- Diagram source di `23 Assets`
- Word hanya distribusi formal stakeholder non-teknis

## 8. Traceability
Perubahan approved pada BR/FR/API/Event wajib update `26 Traceability`.

## Related
- `DOCUMENT_METADATA_STANDARD.md`
- `ENTERPRISE_NUMBERING.md`
- `STATUS_BADGES.md`
- `OWNERSHIP_MATRIX.md`
