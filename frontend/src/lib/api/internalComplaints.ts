/**
 * Pengaduan Internal API client — domain terpisah dari F4 / Batch-1.
 */
import { apiRequest } from "./client";
import { internalComplaintPaths } from "./internalComplaintsContract";
import type { DataResponse, ListResponse } from "./types";

export {
  INTERNAL_COMPLAINTS_BASE,
  internalComplaintPaths,
} from "./internalComplaintsContract";

export type InternalComplaintStatus =
  | "CREATED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "RESOLVED"
  | "CLOSED";

export type InternalResolveAction = "PROPOSE" | "ACCEPT" | "REJECT";
export type InternalAcceptanceParty = "OWNER" | "HANDLING_UNIT";
export type InternalAcceptanceDecision = "ACCEPT" | "REJECT";
export type InternalTransferRequestStatus = "PENDING" | "APPROVED" | "REJECTED";
export type InternalTransferRequestDecision = "APPROVE" | "REJECT";

export interface InternalResolution {
  resolutionId: string;
  resolutionCode: string;
  summary: string;
  status: string;
  comment: string;
  detail?: string | null;
  proposedBy?: string | null;
  proposedAt?: string | null;
  decidedBy?: string | null;
  decidedAt?: string | null;
  rejectionReason?: string | null;
}

export interface InternalAcceptance {
  acceptanceId: string;
  party: InternalAcceptanceParty | string;
  decision: InternalAcceptanceDecision | string;
  actorId: string;
  actorUnitId?: string | null;
  decidedAt: string;
  note?: string | null;
}

export interface InternalHistoryEvent {
  eventId: string;
  eventType: string;
  actorId: string;
  actorName?: string | null;
  actorUnitId?: string | null;
  occurredAt: string;
  note?: string | null;
  sourceUnitId?: string | null;
  targetUnitId?: string | null;
}

export interface InternalComplaintSummary {
  complaintId: string;
  complaintNumber: string;
  status: InternalComplaintStatus | string;
  subject: string;
  category?: string | null;
  priority?: string | null;
  ownerUnitId: string;
  handlingUnitId: string;
  createdAt: string;
  createdBy: string;
  createdByName?: string | null;
  relatedComplaintId?: string | null;
  relatedComplaintNumber?: string | null;
  transferRequestStatus?: InternalTransferRequestStatus | string | null;
}

export interface InternalComplaint {
  complaintId: string;
  complaintNumber: string;
  status: InternalComplaintStatus | string;
  subject: string;
  description: string;
  category: string;
  subcategory?: string | null;
  priority: string;
  chronology?: string | null;
  impact?: string | null;
  relatedComplaintId?: string | null;
  relatedComplaintNumber?: string | null;
  ownerUnitId: string;
  handlingUnitId: string;
  resolution?: InternalResolution | null;
  resolutionHistory?: InternalResolution[];
  handlingUnitAcceptance?: InternalAcceptance | null;
  ownerAcceptance?: InternalAcceptance | null;
  acceptanceHistory?: InternalAcceptance[];
  history: InternalHistoryEvent[];
  closedBy?: string | null;
  closedByName?: string | null;
  closedAt?: string | null;
  createdAt: string;
  createdBy: string;
  createdByName?: string | null;
  updatedAt?: string | null;
  transferRequestStatus?: InternalTransferRequestStatus | string | null;
  transferRequestDestinationUnitId?: string | null;
  transferRequestReason?: string | null;
  transferRequestedBy?: string | null;
  transferRequestedByName?: string | null;
  transferRequestedAt?: string | null;
  transferDecidedBy?: string | null;
  transferDecidedByName?: string | null;
  transferDecidedAt?: string | null;
  transferDecisionReason?: string | null;
}

export interface CreateInternalComplaintRequest {
  subject: string;
  description: string;
  category: string;
  priority?: string;
  subcategory?: string | null;
  chronology?: string | null;
  impact?: string | null;
  relatedComplaintId?: string | null;
  /**
   * Optional Handling Unit (Cabang ↔ Pusat). Meaning depends on the actor:
   * Supervisor/Manager (complaints:assign) → direct initial transfer.
   * Agent-family (no complaints:assign) → becomes a pending transfer
   * request; requestReason is then required.
   */
  handlingUnitId?: string | null;
  /** Required when the actor is Agent-family and handlingUnitId is set. */
  requestReason?: string | null;
}

export interface TransferInternalComplaintRequest {
  destinationUnitId: string;
  reason?: string | null;
}

export interface RequestInternalTransferRequest {
  destinationUnitId: string;
  reason: string;
}

export interface DecideInternalTransferRequest {
  decision: InternalTransferRequestDecision | string;
  reason?: string | null;
}

export interface ResolveInternalComplaintRequest {
  action: InternalResolveAction | string;
  comment: string;
  resolutionCode?: string | null;
  summary?: string | null;
  detail?: string | null;
  rejectionReason?: string | null;
}

export interface RecordInternalAcceptanceRequest {
  party: InternalAcceptanceParty | string;
  decision: InternalAcceptanceDecision | string;
  note?: string | null;
}

export function createInternalComplaint(
  body: CreateInternalComplaintRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().list,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function fetchInternalComplaints(options?: {
  page?: number;
  pageSize?: number;
  status?: string;
  pendingTransferRequest?: boolean;
}): Promise<ListResponse<InternalComplaintSummary>> {
  const params = new URLSearchParams({
    page: String(options?.page ?? 1),
    pageSize: String(options?.pageSize ?? 50),
  });
  if (options?.status?.trim()) params.set("status", options.status.trim());
  if (options?.pendingTransferRequest !== undefined) {
    params.set("pendingTransferRequest", String(options.pendingTransferRequest));
  }
  return apiRequest<ListResponse<InternalComplaintSummary>>(
    `${internalComplaintPaths().list}?${params.toString()}`,
  );
}

/** Sidebar badge — count of pending Agent transfer requests visible to the caller. */
export function fetchPendingTransferRequestCount(): Promise<DataResponse<number>> {
  return apiRequest<DataResponse<number>>(
    internalComplaintPaths().pendingTransferRequestCount,
  );
}

export function fetchInternalComplaint(
  id: string,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().detail(id),
  );
}

export function transferInternalComplaint(
  id: string,
  body: TransferInternalComplaintRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().transfer(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function receiveInternalComplaint(
  id: string,
  body?: { note?: string | null },
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().receive(id),
    { method: "POST", body: JSON.stringify(body ?? {}) },
  );
}

export function resolveInternalComplaint(
  id: string,
  body: ResolveInternalComplaintRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().resolve(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function recordInternalAcceptance(
  id: string,
  body: RecordInternalAcceptanceRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().acceptance(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function closeInternalComplaint(
  id: string,
  body?: { note?: string | null },
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().close(id),
    { method: "POST", body: JSON.stringify(body ?? {}) },
  );
}

/** Agent (re-)submits a transfer request — first submit or after REJECTED. */
export function requestInternalTransfer(
  id: string,
  body: RequestInternalTransferRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().transferRequest(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

/** Supervisor/Manager/Admin decides a pending Agent transfer request. */
export function decideInternalTransferRequest(
  id: string,
  body: DecideInternalTransferRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().transferRequestDecision(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}
