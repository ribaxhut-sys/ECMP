import { apiRequest } from "./client";
import type { ListResponse } from "./types";

/** API-214 user row (roleCode/roleName for picker display). */
export interface UserRef {
  id: string;
  username: string;
  email: string;
  fullName: string;
  roleId: string;
  roleCode: string | null;
  roleName: string | null;
  branchId: string | null;
  isActive: boolean;
  lastLoginAt: string | null;
  createdAt: string;
  updatedAt: string;
}

/** API-214 — GET /api/v1/users (user reference for assignee picker). */
export function fetchUsers(options?: {
  pageSize?: number;
  isActive?: boolean;
}): Promise<ListResponse<UserRef>> {
  const params = new URLSearchParams({
    page: "1",
    pageSize: String(options?.pageSize ?? 100),
  });
  if (options?.isActive !== undefined) {
    params.set("isActive", String(options.isActive));
  }
  return apiRequest<ListResponse<UserRef>>(
    `/api/v1/users?${params.toString()}`,
  );
}
