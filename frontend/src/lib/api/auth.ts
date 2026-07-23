import { apiRequest, setAuthToken } from "./client";
import type { AuthMe, DataResponse, TokenResponse } from "./types";

export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const body = await apiRequest<DataResponse<TokenResponse>>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
    skipAuth: true,
    skipRefresh: true,
  });
  setAuthToken(body.data.accessToken);
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
    });
  } finally {
    setAuthToken(null);
  }
}

export async function fetchCurrentUser(): Promise<AuthMe> {
  const body = await apiRequest<DataResponse<AuthMe>>("/api/v1/auth/me", {
    skipRefresh: false,
  });
  return body.data;
}
