import {
  closeComplaint,
  fetchComplaintAssignments,
  fetchComplaintResolution,
  fetchFinalResolution,
  resolveComplaint,
  searchComplaints,
  submitFinalResolution,
} from "./complaints";
import {
  closeEscalation,
  fetchComplaintEscalations,
  requestEscalation,
} from "./escalations";
import type {
  Assignment,
  CloseComplaintRequest,
  CloseComplaintResult,
  CloseEscalationRequest,
  CloseEscalationResult,
  ComplaintSearchParams,
  ComplaintSearchResponse,
  DataResponse,
  Escalation,
  EscalationRequestCreate,
  EscalationRequestResult,
  FinalResolutionDetail,
  FinalResolutionRequest,
  FinalResolutionResult,
  Resolution,
  ResolveComplaintRequest,
  ResolveComplaintResult,
} from "./types";

/** API-388 — GET /api/v1/complaints/search (resolution list base). */
export function fetchResolutionsList(
  filters: ComplaintSearchParams = {},
): Promise<ComplaintSearchResponse> {
  return searchComplaints(filters);
}

/** API-206 — assignment enrichment for list rows. */
export function fetchResolutionAssignee(
  complaintId: string,
): Promise<DataResponse<Assignment[]>> {
  return fetchComplaintAssignments(complaintId);
}

/** API-226 — GET /api/v1/complaints/{id}/resolution */
export function fetchResolution(
  complaintId: string,
): Promise<DataResponse<Resolution>> {
  return fetchComplaintResolution(complaintId);
}

/** API-225 — POST /api/v1/complaints/{id}/resolution */
export function submitResolution(
  complaintId: string,
  body: ResolveComplaintRequest,
): Promise<DataResponse<ResolveComplaintResult>> {
  return resolveComplaint(complaintId, body);
}

/** API-311 — GET /api/v1/complaints/{id}/final-resolution */
export function fetchFinalResolutionDetail(
  complaintId: string,
): Promise<DataResponse<FinalResolutionDetail>> {
  return fetchFinalResolution(complaintId);
}

/** API-310 — POST /api/v1/complaints/{id}/final-resolution */
export function submitFinalResolutionForComplaint(
  complaintId: string,
  body: FinalResolutionRequest,
): Promise<DataResponse<FinalResolutionResult>> {
  return submitFinalResolution(complaintId, body);
}

/** API-208 — GET /api/v1/complaints/{id}/escalations */
export function fetchResolutionEscalations(
  complaintId: string,
): Promise<DataResponse<Escalation[]>> {
  return fetchComplaintEscalations(complaintId);
}

/** API-301 — POST /api/v1/complaints/{id}/escalations */
export function requestEscalationForComplaint(
  complaintId: string,
  body: EscalationRequestCreate,
): Promise<DataResponse<EscalationRequestResult>> {
  return requestEscalation(complaintId, body);
}

/** API-313 — POST /api/v1/escalations/{id}/close */
export function closeEscalationForComplaint(
  escalationId: string,
  body: CloseEscalationRequest,
): Promise<DataResponse<CloseEscalationResult>> {
  return closeEscalation(escalationId, body);
}

/** API-312 — POST /api/v1/complaints/{id}/close */
export function closeComplaintFromResolution(
  complaintId: string,
  body: CloseComplaintRequest,
): Promise<DataResponse<CloseComplaintResult>> {
  return closeComplaint(complaintId, body);
}
