import { apiRequest } from "./client";
import type { DataResponse, ListResponse } from "./types";

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

/** API-213 create payload. */
export interface UserCreateRequest {
  username: string;
  email: string;
  fullName: string;
  password: string;
  roleId: string;
  branchId?: string | null;
  isActive?: boolean;
}

/** API-214 — GET /api/v1/users */
export function fetchUsers(options?: {
  page?: number;
  pageSize?: number;
  isActive?: boolean;
}): Promise<ListResponse<UserRef>> {
  const params = new URLSearchParams({
    page: String(options?.page ?? 1),
    pageSize: String(options?.pageSize ?? 100),
  });
  if (options?.isActive !== undefined) {
    params.set("isActive", String(options.isActive));
  }
  return apiRequest<ListResponse<UserRef>>(
    `/api/v1/users?${params.toString()}`,
  );
}

/** API-213 — POST /api/v1/users */
export function createUser(
  payload: UserCreateRequest,
): Promise<DataResponse<UserRef>> {
  return apiRequest<DataResponse<UserRef>>("/api/v1/users", {
    method: "POST",
    body: JSON.stringify({
      username: payload.username,
      email: payload.email,
      fullName: payload.fullName,
      password: payload.password,
      roleId: payload.roleId,
      ...(payload.branchId ? { branchId: payload.branchId } : {}),
      isActive: payload.isActive ?? true,
    }),
  });
}
