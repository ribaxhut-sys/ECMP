/**
 * CM Batch 1 Aggregate API client — DEC-026 Single SoT `/api/v1/cm`.
 *
 * Foundation `/api/v1/complaints` lifecycle is retired (M-026-2).
 * Create UI Mode A posts here (`CreateComplaintView`).
 * Mode B / CAP-006 remain CLOSED. CA BC is a separate surface.
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
  customerNumber?: string | null;
  maskedIdentity?: string | null;
  phone?: string | null;
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

export interface CmBatch1ComplaintBrief {
  complaintId?: string;
  complaintNumber?: string;
  status?: string;
  subject?: string | null;
  category?: string | null;
  channel?: string | null;
  createdAt?: string | null;
}

export interface CmBatch1Customer360Response {
  customerId: string;
  profile: Record<string, unknown>;
  activeComplaints: CmBatch1ComplaintBrief[];
  /** Recent history (open + closed); may be capped by API. */
  complaintHistory?: CmBatch1ComplaintBrief[];
  /** Total Aggregate complaints including CLOSED. */
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
  /** BRANCH_CLOSED = handled at branch. ESCALATE_PENDING_APPROVAL = await supervisor. */
  intakeDisposition?: "BRANCH_CLOSED" | "ESCALATE_PENDING_APPROVAL" | null;
}

export interface CmBatch1ComplaintResponse {
  complaintId: string;
  complaintNumber: string;
  status: "REGISTERED" | "IN_PROGRESS" | "CLOSED";
  customerId: string;
  /** Operator-facing name from customer provider (not SoR). */
  customerDisplayName?: string | null;
  /** External/business customer id (not internal UUID). */
  customerNumber?: string | null;
  /** Actor id of the intake officer (PIC). */
  createdBy?: string | null;
  /** Operator-facing name of the intake officer, resolved via directory. */
  createdByName?: string | null;
  /** Intake path label; Aggregate status is REGISTERED | IN_PROGRESS | CLOSED. */
  intakeDisposition?:
    | "BRANCH_CLOSED"
    | "ESCALATE_PENDING_APPROVAL"
    | "ESCALATE_APPROVED"
    | "ESCALATE_REJECTED"
    | "ESCALATE_CANCELLED"
    | string
    | null;
  caseCreated: boolean;
  replayed: boolean;
  category?: string | null;
  channel?: string | null;
  subject?: string | null;
  /** Full intake narrative blob (Supervisor / HQ history). */
  description?: string | null;
  /** Taxpayer complaint body parsed from description. */
  intakeNarrative?: string | null;
  /** Branch close note (Penyelesaian). */
  branchResolution?: string | null;
  /** Why escalate to HQ (Alasan eskalasi) — HQ history. */
  escalationReason?: string | null;
  /** Supervisor/Manager note for HQ — required on APPROVE. */
  supervisorNote?: string | null;
  /** Reject reason history (Penolakan Eskalasi). */
  rejectionNote?: string | null;
  /** Batalkan Eskalasi reason history. */
  cancellationNote?: string | null;
  /** When set, Pusat accepted — Batalkan Eskalasi blocked. */
  hqAcceptedAt?: string | null;
  /** Scheduled arrival date YYYY-MM-DD. */
  hqArrivalDate?: string | null;
  /** Scheduled arrival time HH:MM. */
  hqArrivalTime?: string | null;
  hqAcceptanceNote?: string | null;
  hqArrivalNote?: string | null;
  hqReturnNote?: string | null;
  owningUnitId?: string | null;
  priority?: string | null;
  createdAt?: string | null;
  duplicateCheckResult?: string | null;
}

/** Stable event codes from API-517 — labels live in the UI, not the API. */
export type CmBatch1HistoryEventCode =
  | "REGISTERED"
  | "ESCALATION_REQUESTED"
  | "BRANCH_CLOSED"
  | "ESCALATION_APPROVED"
  | "ESCALATION_REJECTED"
  | "ESCALATION_CANCELLED"
  | "ESCALATION_RE_REQUESTED"
  | "HQ_ACCEPTED"
  | "HQ_RETURNED"
  | "HQ_ARRIVAL_SCHEDULED"
  | (string & {});

export interface CmBatch1IntakeHistoryEntry {
  entryId: string;
  eventCode: CmBatch1HistoryEventCode;
  eventType: string;
  occurredAt: string;
  actorId?: string | null;
  actorName?: string | null;
  priority?: string | null;
  /** Operator note captured with this event; null for rows logged before API-517. */
  note?: string | null;
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
  | "official_letter"
  | "other";

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
  customerId?: string | null;
  caseId?: string | null;
  supersedesAttachmentId?: string | null;
}

export interface CmBatch1IntakeEscalationDecisionRequest {
  decision: "APPROVE" | "REJECT" | "CANCEL";
  note?: string | null;
  /** Required on APPROVE — Supervisor/Manager HQ triage priority. */
  priority?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | null;
}

export interface CmBatch1IntakeEscalationRequestBody {
  /** Alasan ajuan ulang (≥20). Appended to history; cancel/reject notes kept. */
  reason: string;
  priority?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | null;
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
  caseCreated: boolean;
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

/** API-514 — GET /api/v1/cm/complaints (Aggregate list; coexistence read). */
export function fetchCmBatch1Complaints(
  pageOrFilters: number | {
    page?: number;
    pageSize?: number;
    keyword?: string;
    status?: string;
    intakeDisposition?: string;
    priority?: string;
    category?: string;
    createdBy?: string;
    decidedBy?: string;
  } = 1,
  pageSizeArg = 20,
): Promise<ListResponse<CmBatch1ComplaintResponse>> {
  const filters =
    typeof pageOrFilters === "number"
      ? { page: pageOrFilters, pageSize: pageSizeArg }
      : pageOrFilters;
  const params = new URLSearchParams({
    page: String(filters.page ?? 1),
    pageSize: String(filters.pageSize ?? 20),
  });
  const keyword = filters.keyword?.trim();
  if (keyword) params.set("keyword", keyword);
  const status = filters.status?.trim();
  if (status) params.set("status", status);
  const intakeDisposition = filters.intakeDisposition?.trim();
  if (intakeDisposition) params.set("intakeDisposition", intakeDisposition);
  const priority = filters.priority?.trim();
  if (priority) params.set("priority", priority);
  const category = filters.category?.trim();
  if (category) params.set("category", category);
  const createdBy = filters.createdBy?.trim();
  if (createdBy) params.set("createdBy", createdBy);
  const decidedBy = filters.decidedBy?.trim();
  if (decidedBy) params.set("decidedBy", decidedBy);
  return apiRequest(`${cmBatch1Paths().complaints}?${params.toString()}`);
}

export interface CmBatch1UserWorkStats {
  createdCount: number;
  escalationRequestedCount: number;
  escalationApprovedCount: number;
  escalationRejectedCount: number;
}

/** Per-user complaint work counters for the Users directory panel (UM-BUG-006). */
export function fetchCmBatch1UserWorkStats(
  userId: string,
): Promise<DataResponse<CmBatch1UserWorkStats>> {
  return apiRequest(cmBatch1Paths().userWorkStats(userId));
}

/** API-501 — GET /api/v1/cm/complaints/{complaintId} */
export function fetchCmBatch1Complaint(
  complaintId: string,
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().complaint(complaintId));
}

/** API-517 — GET chronological intake history (append-only timeline projection). */
export function fetchCmBatch1ComplaintHistory(
  complaintId: string,
): Promise<ListResponse<CmBatch1IntakeHistoryEntry>> {
  return apiRequest(cmBatch1Paths().complaintHistory(complaintId));
}

/** API-515 — POST intake escalation approve/reject/cancel (disposition only; no Case). */
export function decideCmBatch1IntakeEscalation(
  complaintId: string,
  body: CmBatch1IntakeEscalationDecisionRequest,
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().intakeEscalationDecision(complaintId), {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-518 lab — Re-ajukan eskalasi setelah CANCELLED/REJECTED (history append-only). */
export function requestCmBatch1IntakeEscalation(
  complaintId: string,
  body: CmBatch1IntakeEscalationRequestBody,
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().intakeEscalationRequest(complaintId), {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface CmBatch1HqAcceptRequest {
  note?: string | null;
}

export interface CmBatch1HqAcceptAndScheduleRequest {
  arrivalDate: string;
  arrivalTime: string;
  /** Mandatory info for branch to relay to the taxpayer (min 10). */
  note: string;
}

export interface CmBatch1HqScheduleArrivalRequest {
  arrivalDate: string;
  arrivalTime: string;
  note?: string | null;
}

export type CmBatch1HqReturnReasonCode =
  | "MISSING_ATTACHMENT"
  | "INCOMPLETE_CHRONOLOGY"
  | "UNCLEAR_CUSTOMER_DATA"
  | "WRONG_CATEGORY_OR_ROUTING"
  | "ADDITIONAL_EVIDENCE_REQUIRED"
  | "OTHER";

export interface CmBatch1HqReturnRequest {
  reasonCode: CmBatch1HqReturnReasonCode;
  note: string;
}

/** API-516 lab — Pusat menerima eskalasi yang sudah APPROVED. */
export function acceptCmBatch1HqEscalation(
  complaintId: string,
  body: CmBatch1HqAcceptRequest = {},
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().hqAccept(complaintId), {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Lab — Terima + jadwalkan sekaligus → HQ_SCHEDULED (cabang kabari wajib pajak). */
export function acceptAndScheduleCmBatch1HqEscalation(
  complaintId: string,
  body: CmBatch1HqAcceptAndScheduleRequest,
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().hqAcceptAndSchedule(complaintId), {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-519 lab — Pusat mengembalikan eskalasi ke cabang. */
export function returnCmBatch1HqEscalation(
  complaintId: string,
  body: CmBatch1HqReturnRequest,
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().hqReturn(complaintId), {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-517 lab — Jadwalkan kedatangan wajib pajak di Pusat. */
export function scheduleCmBatch1HqArrival(
  complaintId: string,
  body: CmBatch1HqScheduleArrivalRequest,
): Promise<DataResponse<CmBatch1ComplaintResponse>> {
  return apiRequest(cmBatch1Paths().hqScheduleArrival(complaintId), {
    method: "POST",
    body: JSON.stringify(body),
  });
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
  const customerId = input.customerId?.trim();
  if (customerId) {
    form.append("customerId", customerId);
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

/** API-509 — GET /api/v1/cm/complaints/{id}/attachments. */
export function fetchCmBatch1ComplaintAttachments(
  complaintId: string,
  pageSize = 100,
): Promise<ListResponse<CmBatch1AttachmentResponse>> {
  const params = new URLSearchParams({
    page: "1",
    pageSize: String(pageSize),
  });
  return apiRequest(
    `${cmBatch1Paths().complaintAttachments(complaintId)}?${params.toString()}`,
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
