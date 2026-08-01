/**
 * CM Batch 1 Aggregate API client — DEC-020 `/api/v1/cm` namespace.
 *
 * Dual SoT: this module is **not** interchangeable with `complaints.ts`
 * (foundation `/api/v1/complaints`). Create UI Mode A posts here
 * (`CreateComplaintView`); confirmation reads via `fetchCmBatch1Complaint`.
 * Do not merge SoTs or retire foundation without a Retirement DEC.
 * Mode B / Batch-2 remain CLOSED.
 */
import { apiRequest } from "./client";
import {
  buildCmBatch1CreateHeaders,
  cmBatch1Paths,
  type CmBatch1CreateComplaintOptions,
} from "./cmBatch1Contract";
import type { DataResponse, ListResponse } from "./types";

export {
  CM_BATCH1_BASE,
  buildCmBatch1CreateHeaders,
  cmBatch1Paths,
  type CmBatch1CreateComplaintOptions,
} from "./cmBatch1Contract";

export type CmBatch1VerificationStatus =
  | "verified"
  | "not_found"
  | "ambiguous"
  | "degraded"
  | "blocked";

export type CmBatch1DuplicateDecision =
  | "link_existing"
  | "override"
  | "recommend_only"
  | "blocked";

export interface CmBatch1CustomerSearchRequest {
  customerNumber?: string;
  identityNumber?: string;
  referenceNumber?: string;
}

export interface CmBatch1CustomerCandidate {
  customerId: string;
  displayName: string;
  maskedIdentity?: string | null;
}

export interface CmBatch1CustomerSearchResponse {
  verificationStatus: CmBatch1VerificationStatus;
  customerId?: string | null;
  asOf: string;
  candidates: CmBatch1CustomerCandidate[];
  enumerationOutcome: "allowed" | "delayed" | "blocked" | "alerted";
  briefProfile?: Record<string, unknown> | null;
}

export interface CmBatch1ConfirmCustomerRequest {
  customerId: string;
}

export interface CmBatch1ConfirmCustomerResponse {
  customerId: string;
  locked: boolean;
  asOf: string;
}

export interface CmBatch1Customer360Response {
  customerId: string;
  profile: Record<string, unknown>;
  activeComplaints: Record<string, unknown>[];
  complaintCount: number;
  asOf: string;
}

export interface CmBatch1CreateComplaintRequest {
  customerId: string;
  category: string;
  channel: string;
  subject: string;
  description: string;
  priority?: string | null;
  recordingUnitId?: string | null;
  duplicateOverrideJustification?: string | null;
  stagingToken?: string | null;
}

export interface CmBatch1ComplaintResponse {
  complaintId: string;
  complaintNumber: string;
  status: "REGISTERED";
  customerId: string;
  caseCreated: false;
  replayed: boolean;
  category?: string | null;
  channel?: string | null;
  subject?: string | null;
  priority?: string | null;
  createdAt?: string | null;
  duplicateCheckResult?: string | null;
}

export interface CmBatch1DuplicateCheckRequest {
  customerId: string;
  category?: string | null;
  subject?: string | null;
  channel?: string | null;
}

export interface CmBatch1DuplicateCheckResponse {
  warning: boolean;
  candidates: Record<string, unknown>[];
  degraded: boolean;
  laterReviewWorkItemId?: string | null;
}

export interface CmBatch1DuplicateDecisionRequest {
  decision: CmBatch1DuplicateDecision;
  survivingComplaintId?: string | null;
  justification?: string | null;
  stagingToken?: string | null;
  customerId?: string | null;
}

export interface CmBatch1DuplicateDecisionResponse {
  decisionId: string;
  decision: string;
  customerId: string;
  survivingComplaintId?: string | null;
  warning: boolean;
  hardBlock: boolean;
  caseCreated: false;
  policyVersion: string;
  createdAt: string;
}

export interface CmBatch1TransferAttachmentsRequest {
  stagingToken: string;
  survivingComplaintId: string;
}

export interface CmBatch1TransferAttachmentsResponse {
  stagingToken: string;
  survivingComplaintId: string;
  transferredCount: number;
  attachments: CmBatch1AttachmentResponse[];
  discarded: false;
}

export type CmBatch1AttachmentStatus =
  | "STAGED"
  | "ACTIVE"
  | "TRANSFERRED"
  | "VOID"
  | "SUPERSEDED";

export type CmBatch1AttachmentClassification =
  | "customer_evidence"
  | "internal_evidence"
  | "official_letter";

export interface CmBatch1AttachmentResponse {
  attachmentId: string;
  platformAttachmentId: string;
  status: CmBatch1AttachmentStatus;
  classification: string;
  stagingToken?: string | null;
  complaintId?: string | null;
  originalName: string;
  mimeType: string;
  sizeBytes: number;
  checksumSha256: string;
  supersedesId?: string | null;
  voidReason?: string | null;
  createdAt: string;
}

export interface UploadCmBatch1AttachmentInput {
  file: File;
  classification: CmBatch1AttachmentClassification | string;
  stagingToken?: string | null;
  complaintId?: string | null;
  caseId?: string | null;
  supersedesAttachmentId?: string | null;
}

export interface CmBatch1LaterReviewWorkItem {
  workItemId: string;
  customerId: string;
  complaintId?: string | null;
  reason: string;
  status: string;
  createdAt: string;
  ageHours: number;
}

export interface CmBatch1AgingComplaintItem {
  complaintId: string;
  complaintNumber: string;
  customerId: string;
  status: string;
  subject?: string | null;
  priority?: string | null;
  createdAt: string;
  ageHours: number;
  caseCreated: false;
}

export interface CmBatch1SupervisorQueueResponse {
  laterReviewItems: CmBatch1LaterReviewWorkItem[];
  agingComplaints: CmBatch1AgingComplaintItem[];
  agingThresholdHours: number;
  asOf: string;
}

export interface CmBatch1SupervisorQueueQuery {
  workItemStatus?: "OPEN" | "ALL" | "CLOSED";
  agingHours?: number;
  limit?: number;
}

/** API-502 — POST /api/v1/cm/customers/search */
export function searchCmBatch1Customer(
  body: CmBatch1CustomerSearchRequest,
): Promise<DataResponse<CmBatch1CustomerSearchResponse>> {
  return apiRequest(cmBatch1Paths().customerSearch, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-503 — POST /api/v1/cm/customers/confirm */
export function confirmCmBatch1Customer(
  body: CmBatch1ConfirmCustomerRequest,
): Promise<DataResponse<CmBatch1ConfirmCustomerResponse>> {
  return apiRequest(cmBatch1Paths().customerConfirm, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-504 — GET /api/v1/cm/customers/{customerId}/batch1-360 */
export function fetchCmBatch1Customer360(
  customerId: string,
): Promise<DataResponse<CmBatch1Customer360Response>> {
  return apiRequest(cmBatch1Paths().customer360(customerId));
}

/** API-500 — POST /api/v1/cm/complaints (Aggregate create; no Case). */
export function createCmBatch1Complaint(
  body: CmBatch1CreateComplaintRequest,
  options: CmBatch1CreateComplaintOptions = {},
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().complaints, {
    method: "POST",
    headers: buildCmBatch1CreateHeaders(options),
    body: JSON.stringify(body),
  });
}

/** API-501 — GET /api/v1/cm/complaints/{complaintId} */
export function fetchCmBatch1Complaint(
  complaintId: string,
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().complaint(complaintId));
}

/** API-505 — POST /api/v1/cm/duplicates/check */
export function checkCmBatch1Duplicates(
  body: CmBatch1DuplicateCheckRequest,
): Promise<DataResponse<CmBatch1DuplicateCheckResponse>> {
  return apiRequest(cmBatch1Paths().duplicatesCheck, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-506 — POST /api/v1/cm/duplicates/decisions */
export function recordCmBatch1DuplicateDecision(
  body: CmBatch1DuplicateDecisionRequest,
): Promise<DataResponse<CmBatch1DuplicateDecisionResponse>> {
  return apiRequest(cmBatch1Paths().duplicatesDecisions, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-508 — POST /api/v1/cm/attachments/transfer */
export function transferCmBatch1Attachments(
  body: CmBatch1TransferAttachmentsRequest,
): Promise<DataResponse<CmBatch1TransferAttachmentsResponse>> {
  return apiRequest(cmBatch1Paths().attachmentsTransfer, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-513 — GET /api/v1/cm/supervisor/queue (later-review + no-Case aging). */
export function fetchCmBatch1SupervisorQueue(
  query: CmBatch1SupervisorQueueQuery = {},
): Promise<DataResponse<CmBatch1SupervisorQueueResponse>> {
  const params = new URLSearchParams();
  if (query.workItemStatus) {
    params.set("workItemStatus", query.workItemStatus);
  }
  if (query.agingHours != null) {
    params.set("agingHours", String(query.agingHours));
  }
  if (query.limit != null) {
    params.set("limit", String(query.limit));
  }
  const qs = params.toString();
  const path = qs
    ? `${cmBatch1Paths().supervisorQueue}?${qs}`
    : cmBatch1Paths().supervisorQueue;
  return apiRequest(path);
}

/**
 * API-507 — POST /api/v1/attachments (Batch-1 orchestration fields).
 * Sends stagingToken / classification / complaintId so the backend routes
 * through CmBatch1AttachmentService (not CAP-011 platform-only upload).
 */
export function uploadCmBatch1Attachment(
  input: UploadCmBatch1AttachmentInput,
): Promise<DataResponse<CmBatch1AttachmentResponse>> {
  const form = new FormData();
  form.append("file", input.file);
  form.append("classification", input.classification);
  const stagingToken = input.stagingToken?.trim();
  if (stagingToken) {
    form.append("stagingToken", stagingToken);
  }
  const complaintId = input.complaintId?.trim();
  if (complaintId) {
    form.append("complaintId", complaintId);
  }
  const caseId = input.caseId?.trim();
  if (caseId) {
    form.append("caseId", caseId);
  }
  const supersedes = input.supersedesAttachmentId?.trim();
  if (supersedes) {
    form.append("supersedesAttachmentId", supersedes);
  }
  return apiRequest("/api/v1/attachments", {
    method: "POST",
    body: form,
  });
}

/** API-509 — GET /api/v1/complaints/{id}/attachments (Aggregate when id is Batch-1). */
export function fetchCmBatch1ComplaintAttachments(
  complaintId: string,
  pageSize = 100,
): Promise<ListResponse<CmBatch1AttachmentResponse>> {
  const params = new URLSearchParams({
    page: "1",
    pageSize: String(pageSize),
  });
  return apiRequest(
    `/api/v1/complaints/${encodeURIComponent(complaintId)}/attachments?${params.toString()}`,
  );
}

/**
 * API-512 — DELETE /api/v1/attachments/{id}?reason=…
 * Logical void (BR-012); Batch-1 returns metadata body when linked.
 */
export function voidCmBatch1Attachment(
  attachmentId: string,
  reason: string,
): Promise<DataResponse<CmBatch1AttachmentResponse>> {
  const params = new URLSearchParams({ reason: reason.trim() });
  return apiRequest(
    `/api/v1/attachments/${encodeURIComponent(attachmentId)}?${params.toString()}`,
    { method: "DELETE" },
  );
}
