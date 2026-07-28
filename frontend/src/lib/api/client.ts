import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth/routes";
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

type LoadingListener = (pending: number) => void;
type ApiErrorListener = (error: ApiError) => void;

let authToken: string | null = null;
let refreshInFlight: Promise<boolean> | null = null;
let pendingRequests = 0;
const loadingListeners = new Set<LoadingListener>();
const errorListeners = new Set<ApiErrorListener>();

export function setAuthToken(token: string | null): void {
  authToken = token?.trim() || null;
}

export function getAuthToken(): string | null {
  return authToken;
}

export function subscribeLoading(listener: LoadingListener): () => void {
  loadingListeners.add(listener);
  listener(pendingRequests);
  return () => {
    loadingListeners.delete(listener);
  };
}

export function subscribeApiErrors(listener: ApiErrorListener): () => void {
  errorListeners.add(listener);
  return () => {
    errorListeners.delete(listener);
  };
}

function notifyLoading(): void {
  for (const listener of loadingListeners) {
    listener(pendingRequests);
  }
}

function bumpLoading(): void {
  pendingRequests += 1;
  notifyLoading();
}

function dropLoading(): void {
  pendingRequests = Math.max(0, pendingRequests - 1);
  notifyLoading();
}

function notifyGlobalError(error: ApiError): void {
  for (const listener of errorListeners) {
    listener(error);
  }
}

function baseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (raw) {
    return raw.replace(/\/$/, "");
  }
  // R2-04: localhost fallback only for local `next dev` — never silent in builds.
  if (process.env.NODE_ENV === "development") {
    return "http://localhost:8000";
  }
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL must be set for non-development builds",
  );
}

/** Custom flags carried on Axios configs through interceptors. */
export interface EcmpAxiosConfig {
  skipAuth?: boolean;
  skipRefresh?: boolean;
  skipLoading?: boolean;
  skipGlobalError?: boolean;
  /** Internal: request already retried after refresh. */
  _retry?: boolean;
}

export type ApiRequestInit = {
  method?: string;
  headers?: HeadersInit;
  body?: BodyInit | null;
  signal?: AbortSignal;
} & EcmpAxiosConfig;

type InternalConfig = InternalAxiosRequestConfig & EcmpAxiosConfig;

function isAuthPath(url: string | undefined): boolean {
  if (!url) return false;
  return url.includes("/api/v1/auth/");
}

function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;

  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorBody>;
    if (!axiosError.response) {
      return new ApiError(0, "NETWORK_ERROR", "Network request failed");
    }

    const status = axiosError.response.status;
    const body = axiosError.response.data;
    const code =
      body && typeof body === "object" && "code" in body && body.code
        ? String(body.code)
        : status === 500
          ? "INTERNAL_ERROR"
          : "HTTP_ERROR";
    const message =
      body && typeof body === "object" && "message" in body && body.message
        ? String(body.message)
        : axiosError.message || "Request failed";
    const details =
      body && typeof body === "object" && "details" in body
        ? ((body.details as Record<string, unknown> | null) ?? null)
        : null;

    return new ApiError(status, code, message, details);
  }

  return new ApiError(
    0,
    "UNKNOWN_ERROR",
    error instanceof Error ? error.message : "Request failed",
  );
}

async function tryRefreshSession(): Promise<boolean> {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    try {
      const response = await axios.post(
        `${baseUrl()}/api/v1/auth/refresh`,
        null,
        {
          withCredentials: true,
          headers: { "Content-Type": "application/json" },
        },
      );
      const token = (
        response.data as { data?: { accessToken?: string } } | undefined
      )?.data?.accessToken?.trim();
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

export const axiosClient: AxiosInstance = axios.create({
  baseURL: baseUrl(),
  withCredentials: true,
});

axiosClient.interceptors.request.use((config: InternalConfig) => {
  if (!config.skipLoading) {
    bumpLoading();
  }

  if (!config.skipAuth) {
    const token = getAuthToken();
    if (token) {
      config.headers.set("Authorization", `Bearer ${token}`);
    }
  }

  return config;
});

axiosClient.interceptors.response.use(
  (response) => {
    const config = response.config as InternalConfig;
    if (!config.skipLoading) {
      dropLoading();
    }
    return response;
  },
  async (error: unknown) => {
    const axiosError = axios.isAxiosError(error) ? error : null;
    const config = (axiosError?.config ?? {}) as InternalConfig;

    if (!config.skipLoading) {
      dropLoading();
    }

    const status = axiosError?.response?.status;
    const url = config.url ?? "";

    if (
      status === 401 &&
      !config.skipRefresh &&
      !config.skipAuth &&
      !config._retry &&
      !isAuthPath(url)
    ) {
      const refreshed = await tryRefreshSession();
      if (refreshed) {
        const retryConfig: InternalConfig = {
          ...config,
          _retry: true,
          skipRefresh: true,
        };
        return axiosClient.request(retryConfig);
      }
    }

    const apiError = toApiError(error);

    // Safety net: force-password gate — avoid looping on the change-password call itself.
    if (
      typeof window !== "undefined" &&
      apiError.code === "PASSWORD_CHANGE_REQUIRED" &&
      !window.location.pathname.startsWith(PASSWORD_CHANGE_ROUTE)
    ) {
      window.location.replace(PASSWORD_CHANGE_ROUTE);
    }

    const shouldNotify =
      !config.skipGlobalError &&
      !isAuthPath(url) &&
      apiError.code !== "PASSWORD_CHANGE_REQUIRED" &&
      (apiError.status === 0 || apiError.status >= 500);

    if (shouldNotify) {
      notifyGlobalError(apiError);
    }

    return Promise.reject(apiError);
  },
);

function headersFromInit(headers?: HeadersInit): Record<string, string> {
  if (!headers) return {};
  const result: Record<string, string> = {};
  new Headers(headers).forEach((value, key) => {
    result[key] = value;
  });
  return result;
}

function toAxiosConfig(
  path: string,
  init: ApiRequestInit = {},
  extra: AxiosRequestConfig = {},
): AxiosRequestConfig & EcmpAxiosConfig {
  const {
    skipAuth = false,
    skipRefresh = false,
    skipLoading = false,
    skipGlobalError = false,
    method = "GET",
    headers,
    body,
    signal,
  } = init;

  const axiosHeaders = headersFromInit(headers);
  const isFormData =
    typeof FormData !== "undefined" && body instanceof FormData;
  if (
    body != null &&
    !isFormData &&
    !("Content-Type" in axiosHeaders) &&
    !("content-type" in axiosHeaders)
  ) {
    axiosHeaders["Content-Type"] = "application/json";
  }

  return {
    url: path,
    method,
    headers: axiosHeaders,
    data: body ?? undefined,
    signal,
    skipAuth,
    skipRefresh,
    skipLoading,
    skipGlobalError,
    ...extra,
  };
}

export async function apiRequest<T>(
  path: string,
  init: ApiRequestInit = {},
): Promise<T> {
  const response = await axiosClient.request<T>(toAxiosConfig(path, init));
  if (response.status === 204) {
    return undefined as T;
  }
  return response.data;
}

export interface ApiBlobResult {
  blob: Blob;
  contentType: string | null;
  contentDisposition: string | null;
  checksumSha256: string | null;
}

/** Authenticated binary download/preview — same auth/refresh interceptors. */
export async function apiRequestBlob(
  path: string,
  init: ApiRequestInit = {},
): Promise<ApiBlobResult> {
  const response = await axiosClient.request<Blob>(
    toAxiosConfig(path, init, { responseType: "blob" }),
  );

  const header = (name: string): string | null => {
    const value = response.headers[name];
    return typeof value === "string" ? value : null;
  };

  return {
    blob: response.data,
    contentType: header("content-type"),
    contentDisposition: header("content-disposition"),
    checksumSha256: header("x-checksum-sha256"),
  };
}
