import { apiRequest } from "./client";
import type {
  DataResponse,
  SlaPolicy,
  SlaPolicyCreateRequest,
} from "./types";

/** API-315 — GET /api/v1/sla/policies */
export function fetchSlaPolicies(): Promise<DataResponse<SlaPolicy[]>> {
  return apiRequest<DataResponse<SlaPolicy[]>>("/api/v1/sla/policies");
}

/** API-316 — POST /api/v1/sla/policies */
export function createSlaPolicy(
  body: SlaPolicyCreateRequest,
): Promise<DataResponse<SlaPolicy>> {
  return apiRequest<DataResponse<SlaPolicy>>("/api/v1/sla/policies", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** API-317 — PUT /api/v1/sla/policies/{id}/activate */
export function activateSlaPolicy(
  id: string,
): Promise<DataResponse<SlaPolicy>> {
  return apiRequest<DataResponse<SlaPolicy>>(
    `/api/v1/sla/policies/${encodeURIComponent(id)}/activate`,
    { method: "PUT" },
  );
}
