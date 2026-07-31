import { apiRequest } from "./client";
import type { DataResponse } from "./types";

/** API-338 role row. */
export interface RoleRef {
  id: string;
  code: string;
  name: string;
  description: string | null;
  isSystem: boolean;
  isActive: boolean;
}

/** GET /api/v1/roles — requires role:read (SUPER_ADMIN/ADMIN typically). */
export function fetchRoles(options?: {
  activeOnly?: boolean;
}): Promise<DataResponse<RoleRef[]>> {
  const params = new URLSearchParams();
  if (options?.activeOnly !== undefined) {
    params.set("activeOnly", String(options.activeOnly));
  }
  const query = params.toString();
  return apiRequest<DataResponse<RoleRef[]>>(
    `/api/v1/roles${query ? `?${query}` : ""}`,
  );
}
