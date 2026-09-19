/**
 * Pusat work-queue split (presentation only).
 *
 * Pengaduan = branch Cases escalated to Pusat that Pusat has never handled
 * (never accepted, never claimed). Tindak lanjut = already accepted or
 * claimed, still open. Cabang lists are unchanged.
 */
import type { CmBatch1ComplaintResponse } from "@/lib/api";
import type { CmCaseSummary } from "@/lib/api/cmCase";
import type { CmBatch1ComplaintListRow } from "./cmBatch1ComplaintListRows";

const CASE_TERMINAL_STATUSES = new Set(["CLOSED", "RESOLVED", "CANCELLED"]);

function isActiveCaseStatus(status: string | null | undefined): boolean {
  const s = (status || "").trim().toUpperCase();
  return s.length > 0 && !CASE_TERMINAL_STATUSES.has(s);
}

function norm(value: string | null | undefined): string {
  return (value || "").trim().toUpperCase();
}

function isClosedComplaint(parent: CmBatch1ComplaintResponse): boolean {
  return norm(parent.status) === "CLOSED";
}

function hasPusatAccepted(parent: CmBatch1ComplaintResponse): boolean {
  return Boolean(parent.hqAcceptedAt?.trim());
}

function hasClaim(caseItem: CmCaseSummary): boolean {
  return Boolean(caseItem.handlingClaimedBy?.trim());
}

function isAwaitingPusatAccept(parent: CmBatch1ComplaintResponse): boolean {
  return norm(parent.intakeDisposition) === "ESCALATE_APPROVED" && !hasPusatAccepted(parent);
}

/**
 * Case cabang yang sudah naik ke Pusat dan belum pernah ditangani Pusat.
 */
export function isPusatUnhandledCase(
  caseItem: CmCaseSummary,
  parent: CmBatch1ComplaintResponse,
): boolean {
  if (isClosedComplaint(parent)) return false;
  if (!isActiveCaseStatus(caseItem.status)) return false;
  const disposition = norm(parent.intakeDisposition);
  if (disposition === "HQ_SCHEDULED") {
    return false;
  }
  if (hasPusatAccepted(parent) || hasClaim(caseItem)) return false;
  return Boolean(caseItem.escalatedToPusat) || isAwaitingPusatAccept(parent);
}

/** Parent without a visible Case — still waiting for Pusat to accept. */
export function isPusatUnhandledComplaint(
  parent: CmBatch1ComplaintResponse,
): boolean {
  if (isClosedComplaint(parent)) return false;
  if (hasPusatAccepted(parent)) return false;
  const disposition = norm(parent.intakeDisposition);
  if (disposition === "HQ_SCHEDULED") {
    return false;
  }
  return isAwaitingPusatAccept(parent) || parent.needsPusatHandling === true;
}

export function keepPusatPengaduanListRow(row: CmBatch1ComplaintListRow): boolean {
  if (row.casesState === "loading" || row.casesState === "error") return true;
  if (row.caseItem) return isPusatUnhandledCase(row.caseItem, row.complaint);
  return isPusatUnhandledComplaint(row.complaint);
}

/**
 * Case Pusat sudah pegang (terima atau claim) dan masih terbuka.
 * Bukan antrian masuk, bukan yang dikembalikan ke cabang, bukan menunggu
 * persetujuan cabang.
 */
export function isPusatFollowUpCase(
  caseItem: CmCaseSummary,
  parent: CmBatch1ComplaintResponse | undefined,
): boolean {
  if (!parent) return false;
  if (!isActiveCaseStatus(caseItem.status)) return false;
  if (isPusatUnhandledCase(caseItem, parent)) return false;
  const disposition = norm(parent.intakeDisposition);
  if (disposition === "RETURNED_TO_BRANCH") return false;
  if (disposition === "ESCALATE_PENDING_APPROVAL") return false;
  const accepted = hasPusatAccepted(parent);
  const claimed = hasClaim(caseItem);
  const scheduled = disposition === "HQ_SCHEDULED";
  const escalated = Boolean(caseItem.escalatedToPusat);
  if (!accepted && !claimed && !scheduled) return false;
  return escalated || accepted || scheduled;
}

/** Unread typography: Pusat uses the parent receipt; Cabang uses Case inbox. */
export function complaintWorkListIsUnread(
  complaint: Pick<CmBatch1ComplaintResponse, "pusatUnread">,
  pusatAudience: boolean | null,
  caseItem?: Pick<CmCaseSummary, "isRead"> | null,
): boolean {
  if (pusatAudience === true) return complaint.pusatUnread === true;
  return caseItem?.isRead === false;
}
