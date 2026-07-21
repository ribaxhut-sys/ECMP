# Contribution Guide

| Field | Value |
|---|---|
| ID | EAR-STD-007 |
| Version | 1.1 |
| Owner | Enterprise Architecture / PMO |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## When to Add a Document
1. Belum ada artefak yang menutupi topik tersebut
2. Ada Owner yang jelas (lihat Ownership Matrix)
3. Status awal = `🟡 Draft`
4. ID enterprise sudah dialokasikan

## Before You Write
1. Cek [DECISION_TREE.md](./DECISION_TREE.md)
2. Ambil template dari `../24 Templates`
3. Pasang metadata header wajib
4. Alokasikan ID sesuai [ENTERPRISE_NUMBERING.md](./ENTERPRISE_NUMBERING.md)

## Choose the Right Folder
- Architecture pattern → `19`
- Per-domain diagram/design → `20`
- Stack standard → `21`
- Git/PR/review harian → `22`
- Diagram source/assets → `23`
- Reusable template → `24`
- Term definition → `25`
- Traceability mapping → `26`
- Non-ADR decision / open question → `27`
- Architecture review form → `18/reviews`

## How to Update
1. Update dokumen di folder yang benar
2. Pertahankan ID; naikkan Version
3. Update Status badge + teks
4. Update Last Review / Next Review
5. Update checklist folder README bila perlu
6. Update `26 Traceability` jika BR/FR/API/Event/Test berubah
7. Keputusan arsitektur → ADR (`05`); non-ADR → `27`
8. Simpan source diagram di `23 Assets`
9. Jalankan checker:

```bash
python tools/ear_repo_check.py
```

## Review Checklist
- [ ] Metadata lengkap
- [ ] Enterprise ID valid
- [ ] Status badge + teks benar
- [ ] Owner/Reviewer/Approver terisi
- [ ] Naming convention dipatuhi
- [ ] Tidak ada secret/credentials
- [ ] Link relatif valid
- [ ] Traceability updated (jika relevan)

## Approval Path
`Author → Reviewer → Owner → Approver (Architecture/Business Gate)`
