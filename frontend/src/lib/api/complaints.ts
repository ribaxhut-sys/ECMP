import { apiRequest } from "./client";
import type {
  AssignComplaintRequest,
  AssignComplaintResult,
  Assignment,
  CloseComplaintRequest,
  CloseComplaintResult,
  Complaint,
  ComplaintCreateRequest,
  ComplaintStatus,
  DataResponse,
  FinalResolutionDetail,
  FinalResolutionRequest,
  FinalResolutionResult,
  ListResponse,
  Resolution,
  ResolveComplaintRequest,
  ResolveComplaintResult,
  TimelineEntry,
} from "./types";

export function fetchLatestComplaints(
  pageSize = 10,
): Promise<ListResponse<Complaint>> {
  const params = new URLSearchParams({
    page: "1",
    pageSize: String(pageSize),
  });
  return apiRequest<ListResponse<Complaint>>(
    `/api/v1/complaints?${params.toString()}`,
  );
}

/** API-203 — GET /api/v1/complaints/{id} */
export function fetchComplaint(
  id: string,
): Promise<DataResponse<Complaint>> {
  return apiRequest<DataResponse<Complaint>>(
    `/api/v1/complaints/${encodeURIComponent(id)}`,
  );
}

/** API-201 — POST /api/v1/complaints */
export function createComplaint(
  body: ComplaintCreateRequest,
): Promise<DataResponse<Complaint>> {
  return apiRequest<DataResponse<Complaint>>("/api/v1/complaints", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-205 — POST /api/v1/complaints/{id}/assign */
export function assignComplaint(
  id: string,
  body: AssignComplaintRequest,
): Promise<DataResponse<AssignComplaintResult>> {
  return apiRequest<DataResponse<AssignComplaintResult>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/assign`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-206 — GET /api/v1/complaints/{id}/assignments */
export function fetchComplaintAssignments(
  id: string,
): Promise<DataResponse<Assignment[]>> {
  return apiRequest<DataResponse<Assignment[]>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/assignments`,
  );
}

/** API-209 — GET /api/v1/complaints/{id}/timeline (read-only) */
export function fetchComplaintTimeline(
  id: string,
): Promise<DataResponse<TimelineEntry[]>> {
  return apiRequest<DataResponse<TimelineEntry[]>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/timeline`,
  );
}

/** API-224 — PATCH /api/v1/complaints/{id}/status */
export function changeComplaintStatus(
  id: string,
  body: { status: ComplaintStatus; reason?: string | null },
): Promise<DataResponse<Complaint>> {
  return apiRequest<DataResponse<Complaint>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/status`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}

/** API-225 — POST /api/v1/complaints/{id}/resolution */
export function resolveComplaint(
  id: string,
  body: ResolveComplaintRequest,
): Promise<DataResponse<ResolveComplaintResult>> {
  return apiRequest<DataResponse<ResolveComplaintResult>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/resolution`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-226 — GET /api/v1/complaints/{id}/resolution */
export function fetchComplaintResolution(
  id: string,
): Promise<DataResponse<Resolution>> {
  return apiRequest<DataResponse<Resolution>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/resolution`,
  );
}

/** API-310 — POST /api/v1/complaints/{id}/final-resolution */
export function submitFinalResolution(
  id: string,
  body: FinalResolutionRequest,
): Promise<DataResponse<FinalResolutionResult>> {
  return apiRequest<DataResponse<FinalResolutionResult>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/final-resolution`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-311 — GET /api/v1/complaints/{id}/final-resolution */
export function fetchFinalResolution(
  id: string,
): Promise<DataResponse<FinalResolutionDetail>> {
  return apiRequest<DataResponse<FinalResolutionDetail>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/final-resolution`,
  );
}

/** API-312 — POST /api/v1/complaints/{id}/close */
export function closeComplaint(
  id: string,
  body: CloseComplaintRequest,
): Promise<DataResponse<CloseComplaintResult>> {
  return apiRequest<DataResponse<CloseComplaintResult>>(
    `/api/v1/complaints/${encodeURIComponent(id)}/close`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}
