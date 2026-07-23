import { apiRequest } from "./client";
import type {
  DataResponse,
  Escalation,
  EscalationRequestCreate,
  EscalationRequestResult,
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
