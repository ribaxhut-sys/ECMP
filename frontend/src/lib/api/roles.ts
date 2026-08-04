import { apiRequest } from "./client";
import type { DataResponse } from "./types";

/** API-338 role master row. */
export interface RoleRef {
  id: string;
  code: string;
  name: string;
  description: string | null;
  isSystem: boolean;
  isActive: boolean;
}

/** API-338 — GET /api/v1/roles (requires role:read). */
export function fetchRoles(options?: {
  activeOnly?: boolean;
  includeSystem?: boolean;
}): Promise<RoleRef[]> {
  const params = new URLSearchParams();
  if (options?.activeOnly !== undefined) {
    params.set("activeOnly", String(options.activeOnly));
  }
  if (options?.includeSystem !== undefined) {
    params.set("includeSystem", String(options.includeSystem));
  }
  const qs = params.toString();
  return apiRequest<DataResponse<RoleRef[]>>(
    `/api/v1/roles${qs ? `?${qs}` : ""}`,
  ).then((body) => body.data);
}
