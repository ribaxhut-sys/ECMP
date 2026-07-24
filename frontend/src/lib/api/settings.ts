import { apiRequest } from "./client";
import type { DataResponse, Setting, SettingUpdateRequest } from "./types";

/** API-320 — GET /api/v1/settings/public (no auth) */
export function fetchPublicSettings(): Promise<DataResponse<Setting[]>> {
  return apiRequest<DataResponse<Setting[]>>("/api/v1/settings/public", {
    skipAuth: true,
  });
}

/** API-321 — GET /api/v1/settings */
export function fetchSettings(): Promise<DataResponse<Setting[]>> {
  return apiRequest<DataResponse<Setting[]>>("/api/v1/settings");
}

/** API-322 — PUT /api/v1/settings/{key} */
export function updateSetting(
  key: string,
  body: SettingUpdateRequest,
): Promise<DataResponse<Setting>> {
  return apiRequest<DataResponse<Setting>>(
    `/api/v1/settings/${encodeURIComponent(key)}`,
    {
      method: "PUT",
      body: JSON.stringify(body),
    },
  );
}
