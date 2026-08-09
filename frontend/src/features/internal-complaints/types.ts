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
  | "CLOSED";

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
  closedAt: string | null;
  resolutionSummary: string | null;
  handlingUnitAcceptance: string | null;
  ownerAcceptance: string | null;
  history: InternalHistoryEvent[];
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
  TRANSFER: "activityASSIGNED",
  RECEIVED: "activityRECEIVED",
  REVIEW: "activityREVIEW_STARTED",
  RESOLUTION: "activityFOLLOW_UP_RECORDED",
  HANDLING_UNIT_ACCEPT: "activityVERIFICATION_REQUESTED",
  HANDLING_UNIT_REJECT: "activityVERIFICATION_RETURNED",
  OWNER_ACCEPT: "activityCOMPLETED",
  OWNER_REJECT: "activityVERIFICATION_RETURNED",
  CLOSED: "activityCOMPLETED",
};

export const STATUS_TONE: Record<InternalStatus, BadgeTone> = {
  CREATED: "info",
  ASSIGNED: "primary",
  IN_PROGRESS: "primary",
  RESOLVED: "warning",
  CLOSED: "success",
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
    closedAt: null,
    resolutionSummary: null,
    handlingUnitAcceptance: null,
    ownerAcceptance: null,
    history: [],
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
    closedAt: dto.closedAt ?? null,
    resolutionSummary: dto.resolution?.summary ?? null,
    handlingUnitAcceptance: dto.handlingUnitAcceptance?.decision ?? null,
    ownerAcceptance: dto.ownerAcceptance?.decision ?? null,
    history: dto.history ?? [],
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
