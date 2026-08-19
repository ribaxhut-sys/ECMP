/**
 * Pengaduan Internal — UI domain types aligned to backend persistence.
 *
 * Domain terpisah dari F4 / Batch-1. Owner immutable; Handling Unit berubah
 * saat transfer; CLOSED hanya setelah dual acceptance.
 */

import type { BadgeTone } from "@/shared/ui";
import type {
  InternalComplaint as ApiInternalComplaint,
  InternalComplaintSummary,
  InternalHistoryEvent,
} from "@/lib/api/internalComplaints";

export type InternalStatus =
  | "CREATED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "RESOLVED"
  | "CLOSED"
  | "WITHDRAWN";

export type InternalCategory =
  | "PERFORMANCE"
  | "PROCESS_SOP"
  | "COORDINATION"
  | "COMPLIANCE"
  | "SYSTEM"
  | "OPERATIONAL"
  | "OTHER";

export type InternalPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type InternalAcceptanceParty = "OWNER" | "HANDLING_UNIT";

export type InternalTransferRequestStatus = "PENDING" | "APPROVED" | "REJECTED";

export type InternalWithdrawRequestStatus = "PENDING" | "APPROVED" | "REJECTED";

/** UI list/detail row derived from API. */
export interface InternalComplaint {
  id: string;
  number: string;
  title: string;
  category: string;
  subcategory: string;
  relatedComplaintId: string | null;
  relatedComplaintNumber: string | null;
  priority: InternalPriority | string;
  status: InternalStatus | string;
  description: string;
  chronology: string;
  impact: string;
  ownerUnitId: string;
  handlingUnitId: string;
  createdBy: string;
  createdByName: string | null;
  createdAt: string;
  updatedAt: string | null;
  closedBy: string | null;
  closedByName: string | null;
  closedAt: string | null;
  resolutionSummary: string | null;
  handlingUnitAcceptance: string | null;
  ownerAcceptance: string | null;
  history: InternalHistoryEvent[];
  transferRequestStatus: InternalTransferRequestStatus | string | null;
  transferRequestDestinationUnitId: string | null;
  transferRequestReason: string | null;
  transferRequestedBy: string | null;
  transferRequestedByName: string | null;
  transferRequestedAt: string | null;
  transferDecidedBy: string | null;
  transferDecidedByName: string | null;
  transferDecidedAt: string | null;
  transferDecisionReason: string | null;
  withdrawRequestStatus: InternalWithdrawRequestStatus | string | null;
  withdrawRequestReason: string | null;
  withdrawRequestedBy: string | null;
  withdrawRequestedByName: string | null;
  withdrawRequestedAt: string | null;
  withdrawDecidedBy: string | null;
  withdrawDecidedByName: string | null;
  withdrawDecidedAt: string | null;
  withdrawDecisionReason: string | null;
  withdrawnBy: string | null;
  withdrawnByName: string | null;
  withdrawnAt: string | null;
  withdrawReason: string | null;
  completionRequestStatus: string | null;
  completionReturnReason: string | null;
  completionReturnedBy: string | null;
  completionReturnedByName: string | null;
  completionReturnedAt: string | null;
}

/** Matches backend case_acceptance._AGENT_ROLES for related Aggregate filter. */
const AGENT_FAMILY_ROLES = new Set([
  "AGENT",
  "CS_AGENT",
  "HANDLER",
  "BRANCH_OFFICER",
]);

export function isInternalAgentFamily(roles: readonly string[]): boolean {
  return roles.some((r) => AGENT_FAMILY_ROLES.has(r.toUpperCase()));
}

export const INTERNAL_STATUSES: readonly InternalStatus[] = [
  "CREATED",
  "ASSIGNED",
  "IN_PROGRESS",
  "RESOLVED",
  "CLOSED",
  "WITHDRAWN",
] as const;

export const INTERNAL_CATEGORIES: readonly InternalCategory[] = [
  "PERFORMANCE",
  "PROCESS_SOP",
  "COORDINATION",
  "COMPLIANCE",
  "SYSTEM",
  "OPERATIONAL",
  "OTHER",
] as const;

export const INTERNAL_PRIORITIES: readonly InternalPriority[] = [
  "LOW",
  "MEDIUM",
  "HIGH",
  "CRITICAL",
] as const;

export const STATUS_LABEL_KEY: Record<InternalStatus, string> = {
  CREATED: "statusCREATED",
  ASSIGNED: "statusASSIGNED",
  IN_PROGRESS: "statusIN_PROGRESS",
  RESOLVED: "statusRESOLVED",
  CLOSED: "statusCLOSED",
  WITHDRAWN: "statusWITHDRAWN",
};

export const CATEGORY_LABEL_KEY: Record<InternalCategory, string> = {
  PERFORMANCE: "categoryPERFORMANCE",
  PROCESS_SOP: "categoryPROCESS_SOP",
  COORDINATION: "categoryCOORDINATION",
  COMPLIANCE: "categoryCOMPLIANCE",
  SYSTEM: "categorySYSTEM",
  OPERATIONAL: "categoryOPERATIONAL",
  OTHER: "categoryOTHER",
};

export const HISTORY_LABEL_KEY: Record<string, string> = {
  CREATED: "activityCREATED",
  TRANSFER: "activityTransferred",
  TRANSFER_REQUESTED: "activityTRANSFER_REQUESTED",
  TRANSFER_REQUEST_APPROVED: "activityTRANSFER_REQUEST_APPROVED",
  TRANSFER_REQUEST_REJECTED: "activityTRANSFER_REQUEST_REJECTED",
  RECEIVED: "activityRECEIVED",
  REVIEW: "activityREVIEW_STARTED",
  RESOLUTION: "activityResolutionRecorded",
  HANDLING_UNIT_ACCEPT: "activityHandlingAccepted",
  HANDLING_UNIT_REJECT: "activityReturnedToHandling",
  OWNER_ACCEPT: "activityOwnerAccepted",
  OWNER_REJECT: "activityReturnedToHandling",
  CLOSED: "activityClosed",
  WITHDRAWN: "activityWITHDRAWN",
  WITHDRAW_REQUESTED: "activityWITHDRAW_REQUESTED",
  WITHDRAW_REQUEST_APPROVED: "activityWITHDRAW_REQUEST_APPROVED",
  WITHDRAW_REQUEST_REJECTED: "activityWITHDRAW_REQUEST_REJECTED",
  RETURNED_FOR_COMPLETION: "activityRETURNED_FOR_COMPLETION",
  RESENT_TO_PUSAT: "activityRESENT_TO_PUSAT",
};

export const STATUS_TONE: Record<InternalStatus, BadgeTone> = {
  CREATED: "info",
  ASSIGNED: "primary",
  IN_PROGRESS: "primary",
  RESOLVED: "warning",
  CLOSED: "success",
  WITHDRAWN: "danger",
};

export const PRIORITY_TONE: Record<InternalPriority, BadgeTone> = {
  LOW: "neutral",
  MEDIUM: "info",
  HIGH: "warning",
  CRITICAL: "danger",
};

export function mapSummaryToRow(
  row: InternalComplaintSummary,
): InternalComplaint {
  return {
    id: row.complaintId,
    number: row.complaintNumber,
    title: row.subject,
    category: row.category ?? "OTHER",
    subcategory: "",
    relatedComplaintId: row.relatedComplaintId ?? null,
    relatedComplaintNumber: row.relatedComplaintNumber ?? null,
    priority: row.priority ?? "MEDIUM",
    status: row.status,
    description: "",
    chronology: "",
    impact: "",
    ownerUnitId: row.ownerUnitId,
    handlingUnitId: row.handlingUnitId,
    createdBy: row.createdBy,
    createdByName: row.createdByName ?? null,
    createdAt: row.createdAt,
    updatedAt: null,
    closedBy: null,
    closedByName: null,
    closedAt: null,
    resolutionSummary: null,
    handlingUnitAcceptance: null,
    ownerAcceptance: null,
    history: [],
    transferRequestStatus: row.transferRequestStatus ?? null,
    transferRequestDestinationUnitId: null,
    transferRequestReason: null,
    transferRequestedBy: null,
    transferRequestedByName: null,
    transferRequestedAt: null,
    transferDecidedBy: null,
    transferDecidedByName: null,
    transferDecidedAt: null,
    transferDecisionReason: null,
    withdrawRequestStatus: row.withdrawRequestStatus ?? null,
    withdrawRequestReason: null,
    withdrawRequestedBy: null,
    withdrawRequestedByName: null,
    withdrawRequestedAt: null,
    withdrawDecidedBy: null,
    withdrawDecidedByName: null,
    withdrawDecidedAt: null,
    withdrawDecisionReason: null,
    withdrawnBy: null,
    withdrawnByName: null,
    withdrawnAt: null,
    withdrawReason: null,
    completionRequestStatus: row.completionRequestStatus ?? null,
    completionReturnReason: null,
    completionReturnedBy: null,
    completionReturnedByName: null,
    completionReturnedAt: null,
  };
}

export function mapDetailToRow(dto: ApiInternalComplaint): InternalComplaint {
  return {
    id: dto.complaintId,
    number: dto.complaintNumber,
    title: dto.subject,
    category: dto.category,
    subcategory: dto.subcategory ?? "",
    relatedComplaintId: dto.relatedComplaintId ?? null,
    relatedComplaintNumber: dto.relatedComplaintNumber ?? null,
    priority: dto.priority,
    status: dto.status,
    description: dto.description,
    chronology: dto.chronology ?? "",
    impact: dto.impact ?? "",
    ownerUnitId: dto.ownerUnitId,
    handlingUnitId: dto.handlingUnitId,
    createdBy: dto.createdBy,
    createdByName: dto.createdByName ?? null,
    createdAt: dto.createdAt,
    updatedAt: dto.updatedAt ?? null,
    closedBy: dto.closedBy ?? null,
    closedByName: dto.closedByName ?? null,
    closedAt: dto.closedAt ?? null,
    resolutionSummary: dto.resolution?.summary ?? null,
    handlingUnitAcceptance: dto.handlingUnitAcceptance?.decision ?? null,
    ownerAcceptance: dto.ownerAcceptance?.decision ?? null,
    history: dto.history ?? [],
    transferRequestStatus: dto.transferRequestStatus ?? null,
    transferRequestDestinationUnitId: dto.transferRequestDestinationUnitId ?? null,
    transferRequestReason: dto.transferRequestReason ?? null,
    transferRequestedBy: dto.transferRequestedBy ?? null,
    transferRequestedByName: dto.transferRequestedByName ?? null,
    transferRequestedAt: dto.transferRequestedAt ?? null,
    transferDecidedBy: dto.transferDecidedBy ?? null,
    transferDecidedByName: dto.transferDecidedByName ?? null,
    transferDecidedAt: dto.transferDecidedAt ?? null,
    transferDecisionReason: dto.transferDecisionReason ?? null,
    withdrawRequestStatus: dto.withdrawRequestStatus ?? null,
    withdrawRequestReason: dto.withdrawRequestReason ?? null,
    withdrawRequestedBy: dto.withdrawRequestedBy ?? null,
    withdrawRequestedByName: dto.withdrawRequestedByName ?? null,
    withdrawRequestedAt: dto.withdrawRequestedAt ?? null,
    withdrawDecidedBy: dto.withdrawDecidedBy ?? null,
    withdrawDecidedByName: dto.withdrawDecidedByName ?? null,
    withdrawDecidedAt: dto.withdrawDecidedAt ?? null,
    withdrawDecisionReason: dto.withdrawDecisionReason ?? null,
    withdrawnBy: dto.withdrawnBy ?? null,
    withdrawnByName: dto.withdrawnByName ?? null,
    withdrawnAt: dto.withdrawnAt ?? null,
    withdrawReason: dto.withdrawReason ?? null,
    completionRequestStatus: dto.completionRequestStatus ?? null,
    completionReturnReason: dto.completionReturnReason ?? null,
    completionReturnedBy: dto.completionReturnedBy ?? null,
    completionReturnedByName: dto.completionReturnedByName ?? null,
    completionReturnedAt: dto.completionReturnedAt ?? null,
  };
}

export function canReceive(status: string): boolean {
  return status === "CREATED" || status === "ASSIGNED";
}

export function canTransfer(status: string): boolean {
  return status === "CREATED" || status === "ASSIGNED" || status === "IN_PROGRESS";
}

export function canResolve(status: string): boolean {
  return status === "IN_PROGRESS";
}

export function canAccept(status: string): boolean {
  return status === "RESOLVED";
}

/** Agent-family gate: complaint still local (never transferred) and no request pending. */
export function canRequestTransfer(complaint: InternalComplaint): boolean {
  return (
    complaint.status === "CREATED" &&
    complaint.handlingUnitId === complaint.ownerUnitId &&
    complaint.transferRequestStatus !== "PENDING"
  );
}

export function hasPendingTransferRequest(complaint: InternalComplaint): boolean {
  return complaint.transferRequestStatus === "PENDING";
}

export function hasPendingWithdrawRequest(complaint: InternalComplaint): boolean {
  return complaint.withdrawRequestStatus === "PENDING";
}
