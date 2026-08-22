# DEC-021 — Mode A Case branch close: Comment (+ optional attachment); resolutionCode/summary optional

**Status:** ACCEPTED WITH CONDITIONS (product authorization 2026-08-12)  
**Basis:** `18 Architecture Governance/board-drafts/BOARD-DRAFT_ModeA_Case_Close_Comment_Optional_Attachment_v0.1.md` option **ACCEPT WITH CONDITIONS (sentinel)**  
**Scope:** CAP-008 Aggregate Case Mode A (`API-534` resolve ACCEPT)  
**Does not unlock:** Mode B · DEC-F4 Escalation Engine on Case · Complaint Aggregate auto-close (BQ-007)

---

## Decision

1. **BQ-010 remains LOCKED:** Comment **required**; Attachment **optional** (may reuse Complaint attachments).
2. For Mode A **`action=ACCEPT`**: `resolutionCode` and `summary` are **optional** on the request. When omitted, persistence uses sentinel:
   - `resolutionCode` = `BRANCH_DONE`
   - `summary` = Comment text (trimmed)
3. **`action=PROPOSE`:** same optionality (sentinel) for contract symmetry; primary cabang UX uses ACCEPT path labeled **Tutup**.
4. **`action=REJECT`:** unchanged — `rejectionReason` (or comment-as-reason) required.
5. **Eskalasi Pusat** is **not** a Case resolve action. **Amended DEC-029 (2026-08-22):** ajuan dari halaman Case (`API-520` lab); bukan `ACCEPT`/`PROPOSE`, bukan navigasi ke pengaduan induk.
6. Close Case still obeys checklist / F4 dual acceptance where enforced; UX **Tutup** may orchestrate ACCEPT → Owner ACCEPT (when required) → CLOSED without inventing acceptances when already satisfied.

## Conditions

- Dual-SoT DEC-020 unchanged.
- Do not map HQ escalate onto `PROPOSE`.
- Formal resolution catalogue remains available when clients send explicit `resolutionCode`/`summary`.

## Follow-up artifacts

- OpenAPI `cm-case-management.v1.yaml` API-534  
- Domain `CaseAggregate.resolve`  
- FRD-CM-B2-001 AC-12 note (Mode A branch)  
- FE Resolve dialog (Tutup / Tolak). CTA eskalasi: halaman Case (DEC-029).
