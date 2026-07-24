import type { ApiErrorBody } from "./types";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: Record<string, unknown> | null;

  constructor(
    status: number,
    code: string,
    message: string,
    details: Record<string, unknown> | null = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

let authToken: string | null = null;
let refreshInFlight: Promise<boolean> | null = null;

export function setAuthToken(token: string | null): void {
  authToken = token?.trim() || null;
}

export function getAuthToken(): string | null {
  return authToken;
}

function baseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  return raw.replace(/\/$/, "");
}

export type ApiRequestInit = RequestInit & {
  /** Skip Authorization header (login/refresh/logout). */
  skipAuth?: boolean;
  /** Skip one-shot refresh-on-401 retry. */
  skipRefresh?: boolean;
};

async function tryRefreshSession(): Promise<boolean> {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    try {
      const response = await fetch(`${baseUrl()}/api/v1/auth/refresh`, {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) {
        setAuthToken(null);
        return false;
      }
      const body = (await response.json()) as {
        data?: { accessToken?: string };
      };
      const token = body.data?.accessToken?.trim();
      if (!token) {
        setAuthToken(null);
        return false;
      }
      setAuthToken(token);
      return true;
    } catch {
      setAuthToken(null);
      return false;
    } finally {
      refreshInFlight = null;
    }
  })();
  return refreshInFlight;
}

export async function apiRequest<T>(
  path: string,
  init: ApiRequestInit = {},
): Promise<T> {
  const { skipAuth = false, skipRefresh = false, ...fetchInit } = init;
  const headers = new Headers(fetchInit.headers);
  if (!headers.has("Content-Type") && fetchInit.body) {
    headers.set("Content-Type", "application/json");
  }

  if (!skipAuth) {
    const token = getAuthToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  let response: Response;
  try {
    response = await fetch(`${baseUrl()}${path}`, {
      ...fetchInit,
      headers,
      credentials: "include",
    });
  } catch {
    throw new ApiError(0, "NETWORK_ERROR", "Network request failed");
  }

  if (
    response.status === 401 &&
    !skipRefresh &&
    !skipAuth &&
    !path.startsWith("/api/v1/auth/")
  ) {
    const refreshed = await tryRefreshSession();
    if (refreshed) {
      return apiRequest<T>(path, { ...init, skipRefresh: true });
    }
  }

  if (response.ok) {
    if (response.status === 204) {
      return undefined as T;
    }
    return (await response.json()) as T;
  }

  let body: ApiErrorBody | null = null;
  try {
    body = (await response.json()) as ApiErrorBody;
  } catch {
    body = null;
  }

  throw new ApiError(
    response.status,
    body?.code ?? (response.status === 500 ? "INTERNAL_ERROR" : "HTTP_ERROR"),
    body?.message || response.statusText || "Request failed",
    body?.details ?? null,
  );
}

export interface ApiBlobResult {
  blob: Blob;
  contentType: string | null;
  contentDisposition: string | null;
  checksumSha256: string | null;
}

/** Authenticated binary fetch (download/preview). Same auth/refresh as apiRequest. */
export async function apiRequestBlob(
  path: string,
  init: ApiRequestInit = {},
): Promise<ApiBlobResult> {
  const { skipAuth = false, skipRefresh = false, ...fetchInit } = init;
  const headers = new Headers(fetchInit.headers);

  if (!skipAuth) {
    const token = getAuthToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  let response: Response;
  try {
    response = await fetch(`${baseUrl()}${path}`, {
      ...fetchInit,
      headers,
      credentials: "include",
    });
  } catch {
    throw new ApiError(0, "NETWORK_ERROR", "Network request failed");
  }

  if (
    response.status === 401 &&
    !skipRefresh &&
    !skipAuth &&
    !path.startsWith("/api/v1/auth/")
  ) {
    const refreshed = await tryRefreshSession();
    if (refreshed) {
      return apiRequestBlob(path, { ...init, skipRefresh: true });
    }
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = null;
    }
    throw new ApiError(
      response.status,
      body?.code ?? (response.status === 500 ? "INTERNAL_ERROR" : "HTTP_ERROR"),
      body?.message || response.statusText || "Request failed",
      body?.details ?? null,
    );
  }

  const blob = await response.blob();
  return {
    blob,
    contentType: response.headers.get("Content-Type"),
    contentDisposition: response.headers.get("Content-Disposition"),
    checksumSha256: response.headers.get("X-Checksum-SHA256"),
  };
}
