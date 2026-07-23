import { apiRequest } from "./client";
import type {
  DataResponse,
  Escalation,
  EscalationRequestCreate,
  EscalationRequestResult,
  EscalationReviewRequest,
  EscalationReviewResult,
} from "./types";

/** API-301 — POST /api/v1/complaints/{id}/escalations */
export function requestEscalation(
  complaintId: string,
  body: EscalationRequestCreate,
): Promise<DataResponse<EscalationRequestResult>> {
  return apiRequest<DataResponse<EscalationRequestResult>>(
    `/api/v1/complaints/${encodeURIComponent(complaintId)}/escalations`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-208 — GET /api/v1/complaints/{id}/escalations */
export function fetchComplaintEscalations(
  complaintId: string,
): Promise<DataResponse<Escalation[]>> {
  return apiRequest<DataResponse<Escalation[]>>(
    `/api/v1/complaints/${encodeURIComponent(complaintId)}/escalations`,
  );
}

/** API-302 — GET /api/v1/escalations/{id} */
export function fetchEscalation(
  id: string,
): Promise<DataResponse<Escalation>> {
  return apiRequest<DataResponse<Escalation>>(
    `/api/v1/escalations/${encodeURIComponent(id)}`,
  );
}

/** API-303 — POST /api/v1/escalations/{id}/approve */
export function approveEscalation(
  id: string,
  body: EscalationReviewRequest,
): Promise<DataResponse<EscalationReviewResult>> {
  return apiRequest<DataResponse<EscalationReviewResult>>(
    `/api/v1/escalations/${encodeURIComponent(id)}/approve`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-304 — POST /api/v1/escalations/{id}/reject */
export function rejectEscalation(
  id: string,
  body: EscalationReviewRequest,
): Promise<DataResponse<EscalationReviewResult>> {
  return apiRequest<DataResponse<EscalationReviewResult>>(
    `/api/v1/escalations/${encodeURIComponent(id)}/reject`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}
