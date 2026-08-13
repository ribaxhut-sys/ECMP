import { apiRequest } from "./client";
import type {
  DataResponse,
  ListResponse,
} from "./types";

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

/** Page through API-214 (max pageSize 100) so the directory is complete. */
export async function fetchAllUsers(options?: {
  isActive?: boolean;
}): Promise<UserRef[]> {
  const rows: UserRef[] = [];
  let page = 1;
  for (;;) {
    const res = await fetchUsers({
      page,
      pageSize: 100,
      isActive: options?.isActive,
    });
    rows.push(...res.data);
    const total = res.meta?.totalItems ?? rows.length;
    if (rows.length >= total || res.data.length === 0) break;
    page += 1;
    if (page > 50) break;
  }
  return rows;
}

/** API-217 — soft activate/deactivate (requires users:update). */
export async function updateUserStatus(
  userId: string,
  isActive: boolean,
): Promise<UserRef> {
  const body = await apiRequest<DataResponse<UserRef>>(
    `/api/v1/users/${encodeURIComponent(userId)}/status`,
    {
      method: "PATCH",
      body: JSON.stringify({ isActive }),
      skipGlobalError: true,
    },
  );
  return body.data;
}

/**
 * API-216 — change a user's primary role (requires users:update; backend also
 * applies the UAT-020 escalation guard). `branchId` is sent so the backend's
 * role↔unit rule (service.py `_ensure_branch_for_role`) stays satisfied: a
 * head-office role must carry no unit, a branch role keeps the existing one.
 */
export async function updateUserRole(
  userId: string,
  roleId: string,
  branchId: string | null,
): Promise<UserRef> {
  const body = await apiRequest<DataResponse<UserRef>>(
    `/api/v1/users/${encodeURIComponent(userId)}`,
    {
      method: "PUT",
      body: JSON.stringify({ roleId, branchId }),
      skipGlobalError: true,
    },
  );
  return body.data;
}

export interface CreateUserPayload {
  username: string;
  email: string;
  fullName: string;
  password: string;
  roleId: string;
  branchId?: string | null;
  isActive?: boolean;
}

/** API-213 — POST /api/v1/users (requires users:create). */
export async function createUser(payload: CreateUserPayload): Promise<UserRef> {
  const body = await apiRequest<DataResponse<UserRef>>("/api/v1/users", {
    method: "POST",
    body: JSON.stringify({
      username: payload.username,
      email: payload.email,
      fullName: payload.fullName,
      password: payload.password,
      roleId: payload.roleId,
      branchId: payload.branchId ?? null,
      isActive: payload.isActive ?? true,
    }),
    skipGlobalError: true,
  });
  return body.data;
}

export interface PreferredLanguageUpdateRequest {
  preferredLanguage: string;
}

/** PATCH /api/v1/users/me/preferred-language — persist UI locale preference. */
export function updatePreferredLanguage(
  preferredLanguage: string,
): Promise<DataResponse<{ preferredLanguage: string }>> {
  return apiRequest<DataResponse<{ preferredLanguage: string }>>(
    "/api/v1/users/me/preferred-language",
    {
      method: "PATCH",
      body: JSON.stringify({
        preferredLanguage,
      } satisfies PreferredLanguageUpdateRequest),
      skipGlobalError: true,
    },
  );
}
