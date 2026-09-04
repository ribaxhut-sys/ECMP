import { ApiError } from "@/lib/api/client";

type TranslateFn = (
  key: string,
  values?: Record<string, string | number | Date>,
) => string;

/** Map API error codes → next-intl `errors.*` keys (prefer code over server text). */
const ERROR_CODE_TO_KEY: Record<string, string> = {
  NETWORK_ERROR: "network", // resolved via common
  UNAUTHENTICATED: "unauthenticated",
  FORBIDDEN: "forbidden",
  DATA_SCOPE_DENIED: "dataScopeDenied",
  ORG_SCOPE_DENIED: "orgScopeDenied",
  NOT_FOUND: "notFound",
  VALIDATION_ERROR: "validationError",
  INVALID_STATE: "invalidState",
  CONFLICT: "conflict",
  RATE_LIMITED: "rateLimited",
  INTERNAL_ERROR: "internalError",
  METHOD_NOT_ALLOWED: "methodNotAllowed",
  PASSWORD_CHANGE_REQUIRED: "passwordChangeRequired",
};

/**
 * Map API / network failures to locale strings.
 * Prefer error codes over English (or raw) server messages.
 */
export function resolveApiErrorMessage(
  err: unknown,
  tErrors: TranslateFn,
  tCommon: TranslateFn,
  fallbackKey = "unexpectedError",
): string {
  if (err instanceof ApiError) {
    if (err.code === "NETWORK_ERROR") {
      return tCommon("networkErrorDescription");
    }
    if (err.code === "HTTP_ERROR") {
      return tCommon("requestFailed");
    }
    if (err.code === "UNKNOWN_ERROR") {
      return tErrors(fallbackKey);
    }
    if (err.code === "UNAUTHENTICATED" || err.status === 401) {
      return tErrors("unauthenticated");
    }
    if (err.code === "RATE_LIMITED" || err.status === 429) {
      return tErrors("rateLimited");
    }
    if (err.code === "FORBIDDEN" || err.status === 403) {
      // Prefer specific scope codes when present.
      const scoped = ERROR_CODE_TO_KEY[err.code];
      if (scoped && scoped !== "forbidden") {
        return tErrors(scoped);
      }
      return tErrors("forbidden");
    }
    const mapped = ERROR_CODE_TO_KEY[err.code];
    if (mapped) {
      // Prefer the server's localized validation text when present — codes
      // alone hide actionable messages (e.g. customer confirm lock required).
      if (
        err.code === "VALIDATION_ERROR" &&
        typeof err.message === "string" &&
        err.message.trim()
      ) {
        return err.message.trim();
      }
      return tErrors(mapped);
    }
    return tErrors(fallbackKey);
  }
  if (err instanceof Error && err.message === "PROFILE_LOAD_FAILED") {
    return tErrors("profileLoadFailed");
  }
  if (
    err instanceof Error &&
    /network|failed to fetch|load failed|timeout|timed out/i.test(err.message)
  ) {
    return tCommon("networkErrorDescription");
  }
  return tCommon(fallbackKey);
}

/** Translate `validation.*` keys returned by form validators. */
export function translateValidationErrors(
  keys: Record<string, string | undefined>,
  tValidation: TranslateFn,
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [field, key] of Object.entries(keys)) {
    if (!key) continue;
    try {
      if (key === "subjectMax") {
        out[field] = tValidation(key, { max: 200 });
      } else if (key === "descriptionMax") {
        out[field] = tValidation(key, { max: 5000 });
      } else if (key === "channelMax") {
        out[field] = tValidation(key, { max: 32 });
      } else if (key === "categoryMax") {
        out[field] = tValidation(key, { max: 64 });
      } else if (key === "customerIdMax") {
        out[field] = tValidation(key, { max: 128 });
      } else {
        out[field] = tValidation(key);
      }
    } catch {
      out[field] = key;
    }
  }
  return out;
}
