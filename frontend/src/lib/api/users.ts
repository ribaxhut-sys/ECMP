import { apiRequest } from "./client";
import type {
  AdminResetPasswordResponse,
  ChangePasswordResponse,
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

/** API-412 — self-service change password (also clears forcePasswordChange). */
export async function changePassword(payload: {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}): Promise<ChangePasswordResponse> {
  const body = await apiRequest<DataResponse<ChangePasswordResponse>>(
    "/api/v1/users/me/change-password",
    {
      method: "POST",
      body: JSON.stringify(payload),
      skipGlobalError: true,
    },
  );
  return body.data;
}

/** API-413 — admin/supervisor reset; temporary password returned once. */
export async function adminResetPassword(
  userId: string,
): Promise<AdminResetPasswordResponse> {
  const body = await apiRequest<DataResponse<AdminResetPasswordResponse>>(
    `/api/v1/users/${userId}/reset-password`,
    {
      method: "POST",
      skipGlobalError: true,
    },
  );
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
