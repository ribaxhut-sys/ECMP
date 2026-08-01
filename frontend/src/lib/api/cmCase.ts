/**
 * CAP-008 Case Management Mode A API client — FRD-CM-B2-001 / API-530…535.
 *
 * Dual SoT Aggregate `/api/v1/cm/cases`. Not interchangeable with foundation
 * complaints or Sprint case-service. No List/Timeline endpoints in Mode A.
 */
import { apiRequest } from "./client";
import {
  buildCmCaseMutateHeaders,
  cmCasePaths,
  type CmCaseMutateOptions,
} from "./cmCaseContract";
import type { DataResponse } from "./types";

export {
  CM_CASE_BASE,
  buildCmCaseMutateHeaders,
  cmCasePaths,
  type CmCaseMutateOptions,
} from "./cmCaseContract";

export type CmCaseStatus =
  | "CREATED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "RESOLVED"
  | "CLOSED"
  | "CANCELLED";

export type CmCaseCancelReason =
  | "DUPLICATE"
  | "WRONG_INPUT"
  | "CUSTOMER_CANCELLATION";

export type CmCaseResolveAction = "PROPOSE" | "ACCEPT" | "REJECT";

export interface CmCaseResolution {
  resolutionId: string;
  resolutionCode: string;
  summary: string;
  status: string;
  comment: string;
  detail?: string | null;
  customerImpact?: string | null;
  attachmentIds?: string[];
  proposedBy?: string | null;
  proposedAt?: string | null;
  decidedBy?: string | null;
  decidedAt?: string | null;
  rejectionReason?: string | null;
}

export interface CmCase {
  caseId: string;
  caseNumber: string;
  complaintId: string;
  customerId: string;
  status: CmCaseStatus;
  caseType: string;
  category?: string | null;
  subject: string;
  description: string;
  priority: string;
  owningUnitId?: string | null;
  assignedUserId?: string | null;
  slaPolicyVersionId?: string | null;
  slaCountdownActive: boolean;
  resolution?: CmCaseResolution | null;
  resolutionHistory?: CmCaseResolution[];
  cancelReason?: string | null;
  closedBy?: string | null;
  closedAt?: string | null;
  createdAt: string;
  createdBy: string;
  updatedAt?: string | null;
  complaintStatusAfterCreate?: string | null;
}

export interface CreateCmCaseRequest {
  complaintId: string;
  caseType: string;
  category?: string | null;
  subject: string;
  description: string;
  priority: string;
  destinationUnitId?: string | null;
  assignedUserId?: string | null;
  slaPolicyVersionId?: string | null;
}

export interface AddCmCaseRequest {
  caseType: string;
  category?: string | null;
  subject: string;
  description: string;
  priority: string;
  destinationUnitId?: string | null;
  assignedUserId?: string | null;
  slaPolicyVersionId?: string | null;
}

export interface UpdateCmCaseStatusRequest {
  toStatus: CmCaseStatus;
  destinationUnitId?: string | null;
  cancelReason?: CmCaseCancelReason | null;
  reason?: string | null;
  assignedUserId?: string | null;
}

export interface ResolveCmCaseRequest {
  action: CmCaseResolveAction;
  comment: string;
  resolutionCode?: string | null;
  summary?: string | null;
  detail?: string | null;
  customerImpact?: string | null;
  attachmentIds?: string[];
  rejectionReason?: string | null;
}

export interface CloseCmCaseRequest {
  note?: string | null;
}

async function unwrap(
  promise: Promise<DataResponse<CmCase>>,
): Promise<DataResponse<CmCase>> {
  return promise;
}

export function createCmCase(
  body: CreateCmCaseRequest,
  options?: CmCaseMutateOptions,
): Promise<DataResponse<CmCase>> {
  return unwrap(
    apiRequest<DataResponse<CmCase>>(cmCasePaths().cases, {
      method: "POST",
      body: JSON.stringify(body),
      headers: buildCmCaseMutateHeaders(options),
    }),
  );
}

export function addCmCase(
  complaintId: string,
  body: AddCmCaseRequest,
  options?: CmCaseMutateOptions,
): Promise<DataResponse<CmCase>> {
  return unwrap(
    apiRequest<DataResponse<CmCase>>(cmCasePaths().addCase(complaintId), {
      method: "POST",
      body: JSON.stringify(body),
      headers: buildCmCaseMutateHeaders(options),
    }),
  );
}

export function fetchCmCase(
  caseId: string,
  options?: { complaintId?: string },
): Promise<DataResponse<CmCase>> {
  const paths = cmCasePaths();
  const qs =
    options?.complaintId && options.complaintId.trim()
      ? `?complaintId=${encodeURIComponent(options.complaintId.trim())}`
      : "";
  return unwrap(
    apiRequest<DataResponse<CmCase>>(`${paths.case(caseId)}${qs}`, {
      method: "GET",
    }),
  );
}

export function updateCmCaseStatus(
  caseId: string,
  body: UpdateCmCaseStatusRequest,
  options?: CmCaseMutateOptions,
): Promise<DataResponse<CmCase>> {
  return unwrap(
    apiRequest<DataResponse<CmCase>>(cmCasePaths().status(caseId), {
      method: "PATCH",
      body: JSON.stringify(body),
      headers: buildCmCaseMutateHeaders(options),
    }),
  );
}

export function resolveCmCase(
  caseId: string,
  body: ResolveCmCaseRequest,
  options?: CmCaseMutateOptions,
): Promise<DataResponse<CmCase>> {
  return unwrap(
    apiRequest<DataResponse<CmCase>>(cmCasePaths().resolve(caseId), {
      method: "POST",
      body: JSON.stringify(body),
      headers: buildCmCaseMutateHeaders(options),
    }),
  );
}

export function closeCmCase(
  caseId: string,
  body?: CloseCmCaseRequest,
  options?: CmCaseMutateOptions,
): Promise<DataResponse<CmCase>> {
  return unwrap(
    apiRequest<DataResponse<CmCase>>(cmCasePaths().close(caseId), {
      method: "POST",
      body: JSON.stringify(body ?? {}),
      headers: buildCmCaseMutateHeaders(options),
    }),
  );
}
