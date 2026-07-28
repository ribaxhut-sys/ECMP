import { apiRequest, setAuthToken } from "./client";
import type {
  AuthMe,
  DataResponse,
  ForgotPasswordResponse,
  ResetPasswordResponse,
  TokenResponse,
} from "./types";

export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const body = await apiRequest<DataResponse<TokenResponse>>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
    skipAuth: true,
    skipRefresh: true,
    skipGlobalError: true,
  });
  setAuthToken(body.data.accessToken);
  return body.data;
}

/** API-410 — always returns a generic message (no account enumeration). */
export async function forgotPassword(
  email: string,
): Promise<ForgotPasswordResponse> {
  const body = await apiRequest<DataResponse<ForgotPasswordResponse>>(
    "/api/v1/auth/forgot-password",
    {
      method: "POST",
      body: JSON.stringify({ email }),
      skipAuth: true,
      skipRefresh: true,
      skipGlobalError: true,
    },
  );
  return body.data;
}

/** API-411 — reset with single-use token from email link. */
export async function resetPassword(payload: {
  token: string;
  password: string;
  confirmPassword: string;
}): Promise<ResetPasswordResponse> {
  const body = await apiRequest<DataResponse<ResetPasswordResponse>>(
    "/api/v1/auth/reset-password",
    {
      method: "POST",
      body: JSON.stringify(payload),
      skipAuth: true,
      skipRefresh: true,
      skipGlobalError: true,
    },
  );
  return body.data;
}

export async function refreshAccessToken(): Promise<TokenResponse | null> {
  try {
    const body = await apiRequest<DataResponse<TokenResponse>>(
      "/api/v1/auth/refresh",
      {
        method: "POST",
        skipAuth: true,
        skipRefresh: true,
        skipGlobalError: true,
        skipLoading: true,
      },
    );
    setAuthToken(body.data.accessToken);
    return body.data;
  } catch {
    setAuthToken(null);
    return null;
  }
}

export async function logout(): Promise<void> {
  try {
    await apiRequest<void>("/api/v1/auth/logout", {
      method: "POST",
      skipAuth: true,
      skipRefresh: true,
      skipGlobalError: true,
    });
  } finally {
    setAuthToken(null);
  }
}

export async function fetchCurrentUser(): Promise<AuthMe> {
  const body = await apiRequest<DataResponse<AuthMe>>("/api/v1/auth/me", {
    skipRefresh: false,
    skipGlobalError: true,
  });
  return body.data;
}
