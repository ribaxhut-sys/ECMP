/**
 * Pengaduan Internal API client — domain terpisah dari F4 / Batch-1.
 */
import { apiRequest, apiRequestBlob } from "./client";
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
  | "CLOSED"
  | "WITHDRAWN";

export type InternalResolveAction = "PROPOSE" | "ACCEPT" | "REJECT";
export type InternalAcceptanceParty = "OWNER" | "HANDLING_UNIT";
export type InternalAcceptanceDecision = "ACCEPT" | "REJECT";
export type InternalTransferRequestStatus = "PENDING" | "APPROVED" | "REJECTED";
export type InternalTransferRequestDecision = "APPROVE" | "REJECT";
export type InternalWithdrawRequestStatus = "PENDING" | "APPROVED" | "REJECTED";
export type InternalCompletionRequestStatus = "PENDING";
export type InternalWithdrawRequestDecision = "APPROVE" | "REJECT";

export interface InternalResolution {
  resolutionId: string;
  resolutionCode: string;
  summary: string;
  status: string;
  comment: string;
  detail?: string | null;
  proposedBy?: string | null;
  proposedByName?: string | null;
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
  withdrawRequestStatus?: InternalWithdrawRequestStatus | string | null;
  completionRequestStatus?: InternalCompletionRequestStatus | string | null;
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
  withdrawRequestStatus?: InternalWithdrawRequestStatus | string | null;
  withdrawRequestReason?: string | null;
  withdrawRequestedBy?: string | null;
  withdrawRequestedByName?: string | null;
  withdrawRequestedAt?: string | null;
  withdrawDecidedBy?: string | null;
  withdrawDecidedByName?: string | null;
  withdrawDecidedAt?: string | null;
  withdrawDecisionReason?: string | null;
  withdrawnBy?: string | null;
  withdrawnByName?: string | null;
  withdrawnAt?: string | null;
  withdrawReason?: string | null;
  completionRequestStatus?: InternalCompletionRequestStatus | string | null;
  completionReturnReason?: string | null;
  completionReturnedBy?: string | null;
  completionReturnedByName?: string | null;
  completionReturnedAt?: string | null;
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
   * Optional Handling Unit (Cabang ↔ Pusat).
   * Cabang create always goes to Pusat (ASSIGNED) — no requestReason.
   * Pusat Agent-family + dest cabang → pending transfer request; requestReason required.
   * Pusat Supervisor/Manager → direct initial transfer.
   */
  handlingUnitId?: string | null;
  /** Required when a Pusat Agent-family actor sets handlingUnitId. */
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

export interface WithdrawInternalComplaintRequest {
  reason: string;
}

export interface ReturnForCompletionRequest {
  reason: string;
}

export interface ResendToPusatRequest {
  note: string;
}

export interface DecideInternalWithdrawRequest {
  decision: InternalWithdrawRequestDecision | string;
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
  pendingWithdrawRequest?: boolean;
  needsReceive?: boolean;
}): Promise<ListResponse<InternalComplaintSummary>> {
  const params = new URLSearchParams({
    page: String(options?.page ?? 1),
    pageSize: String(options?.pageSize ?? 50),
  });
  if (options?.status?.trim()) params.set("status", options.status.trim());
  if (options?.pendingTransferRequest !== undefined) {
    params.set("pendingTransferRequest", String(options.pendingTransferRequest));
  }
  if (options?.pendingWithdrawRequest !== undefined) {
    params.set("pendingWithdrawRequest", String(options.pendingWithdrawRequest));
  }
  if (options?.needsReceive !== undefined) {
    params.set("needsReceive", String(options.needsReceive));
  }
  return apiRequest<ListResponse<InternalComplaintSummary>>(
    `${internalComplaintPaths().list}?${params.toString()}`,
  );
}

/** Sidebar badge — incoming tickets awaiting receive at the caller's unit. */
export function fetchPendingInboxCount(): Promise<DataResponse<number>> {
  return apiRequest<DataResponse<number>>(
    internalComplaintPaths().pendingInboxCount,
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

/** Lab/API only — Mode A Internal UI does not call this. */
export function receiveInternalComplaint(
  id: string,
  body?: { note?: string | null },
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().receive(id),
    { method: "POST", body: JSON.stringify(body ?? {}) },
  );
}

export function returnInternalComplaintForCompletion(
  id: string,
  body: ReturnForCompletionRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().returnForCompletion(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function resendInternalComplaintToPusat(
  id: string,
  body: ResendToPusatRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().resendToPusat(id),
    { method: "POST", body: JSON.stringify(body) },
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

/** Sidebar badge — pending branch withdraw requests visible to the caller. */
export function fetchPendingWithdrawRequestCount(): Promise<DataResponse<number>> {
  return apiRequest<DataResponse<number>>(
    internalComplaintPaths().pendingWithdrawRequestCount,
  );
}

/** Branch cancels before Pusat receives — no Pusat notification. */
export function withdrawInternalComplaint(
  id: string,
  body: WithdrawInternalComplaintRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().withdraw(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

/** After Pusat received: branch asks Pusat to withdraw. */
export function requestInternalWithdraw(
  id: string,
  body: WithdrawInternalComplaintRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().withdrawRequest(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

/** Pusat Supervisor/Manager/Admin decides a pending withdraw request. */
export function decideInternalWithdrawRequest(
  id: string,
  body: DecideInternalWithdrawRequest,
): Promise<DataResponse<InternalComplaint>> {
  return apiRequest<DataResponse<InternalComplaint>>(
    internalComplaintPaths().withdrawRequestDecision(id),
    { method: "POST", body: JSON.stringify(body) },
  );
}

function filenameFromDisposition(header: string | null): string | null {
  if (!header) return null;
  const utfMatch = /filename\*=UTF-8''([^;]+)/i.exec(header);
  const plainMatch = /filename="([^"]+)"/i.exec(header);
  const raw = utfMatch?.[1] ?? plainMatch?.[1];
  if (!raw) return null;
  try {
    return decodeURIComponent(raw);
  } catch {
    return raw;
  }
}

function saveBlob(blob: Blob, filename: string): void {
  if (typeof document === "undefined") return;
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/** API-550 — GET /api/v1/internal/complaints/{id}/export (operator snapshot PDF). */
export async function downloadInternalComplaintPdf(
  id: string,
): Promise<{ filename: string }> {
  const result = await apiRequestBlob(internalComplaintPaths().exportPdf(id));
  const filename =
    filenameFromDisposition(result.contentDisposition) ??
    "pengaduan-internal.pdf";
  saveBlob(result.blob, filename);
  return { filename };
}
