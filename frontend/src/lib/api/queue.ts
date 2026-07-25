import { apiRequest } from "./client";
import {
  assignComplaint,
  changeComplaintStatus,
  fetchComplaintAssignments,
  fetchComplaintSla,
  searchComplaints,
} from "./complaints";
import type {
  AssignComplaintRequest,
  AssignComplaintResult,
  Assignment,
  Complaint,
  ComplaintSearchParams,
  ComplaintSearchResponse,
  ComplaintStatus,
  DashboardComplaintSummary,
  DataResponse,
  SlaRecord,
  UnassignComplaintRequest,
} from "./types";

/** API-389 — GET /api/v1/dashboard/summary (complaint work-queue metrics). */
export function fetchQueueSummary(): Promise<
  DataResponse<DashboardComplaintSummary>
> {
  return apiRequest<DataResponse<DashboardComplaintSummary>>(
    "/api/v1/dashboard/summary",
  );
}

/** API-388 — GET /api/v1/complaints/search (queue list). */
export function fetchQueueList(
  filters: ComplaintSearchParams = {},
): Promise<ComplaintSearchResponse> {
  return searchComplaints(filters);
}

/** API-206 — current assignment for a queue row (assignee display). */
export function fetchQueueAssignments(
  complaintId: string,
): Promise<DataResponse<Assignment[]>> {
  return fetchComplaintAssignments(complaintId);
}

/** API-314 — SLA record for a queue row (indicator when available). */
export function fetchQueueSla(
  complaintId: string,
): Promise<DataResponse<SlaRecord>> {
  return fetchComplaintSla(complaintId);
}

/**
 * Take queue item — assign to the given handler (API-205).
 * Caller supplies assigneeId (typically the current user).
 */
export function takeQueue(
  complaintId: string,
  body: AssignComplaintRequest,
): Promise<DataResponse<AssignComplaintResult>> {
  return assignComplaint(complaintId, body);
}

/** API-403 — POST /api/v1/complaints/{id}/unassign (release). */
export function releaseQueue(
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

/** API-224 — PATCH /api/v1/complaints/{id}/status. */
export function updateQueueStatus(
  complaintId: string,
  body: { status: ComplaintStatus; reason?: string | null },
): Promise<DataResponse<Complaint>> {
  return changeComplaintStatus(complaintId, body);
}
