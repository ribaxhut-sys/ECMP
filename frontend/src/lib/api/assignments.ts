import { apiRequest } from "./client";
import {
  assignComplaint,
  fetchComplaintAssignments,
  searchComplaints,
} from "./complaints";
import type {
  AssignComplaintRequest,
  AssignComplaintResult,
  Assignment,
  ComplaintSearchParams,
  ComplaintSearchResponse,
  DataResponse,
  UnassignComplaintRequest,
} from "./types";

/** API-388 — GET /api/v1/complaints/search (assignment list base). */
export function fetchAssignmentsList(
  filters: ComplaintSearchParams = {},
): Promise<ComplaintSearchResponse> {
  return searchComplaints(filters);
}

/** API-206 — GET /api/v1/complaints/{id}/assignments. */
export function fetchAssignmentHistory(
  complaintId: string,
): Promise<DataResponse<Assignment[]>> {
  return fetchComplaintAssignments(complaintId);
}

/** API-205 — POST /api/v1/complaints/{id}/assign (initial assign). */
export function assignComplaintHandler(
  complaintId: string,
  body: AssignComplaintRequest,
): Promise<DataResponse<AssignComplaintResult>> {
  return assignComplaint(complaintId, body);
}

/**
 * API-205 — POST /api/v1/complaints/{id}/assign (reassign).
 * OpenAPI: `reason` is mandatory when an assignment already exists.
 */
export function reassignComplaintHandler(
  complaintId: string,
  body: AssignComplaintRequest,
): Promise<DataResponse<AssignComplaintResult>> {
  return assignComplaint(complaintId, body);
}

/** API-403 — POST /api/v1/complaints/{id}/unassign (cancel / release). */
export function cancelAssignment(
  complaintId: string,
  body: UnassignComplaintRequest,
): Promise<DataResponse<Assignment>> {
  return apiRequest<DataResponse<Assignment>>(
    `/api/v1/complaints/${encodeURIComponent(complaintId)}/unassign`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}
