/**
 * Customer search key length rules (FR-002 anti-enumeration hygiene).
 * Keep in sync with backend `customer_search_key.py`.
 */

export type CustomerSearchKeyKind = "name" | "phone" | "id";

export const MIN_NAME_CHARS = 3;
export const MIN_ID_DIGITS = 8;
export const MIN_PHONE_DIGITS = 10;

export type CustomerSearchKeyErrorCode =
  | "empty"
  | "nameTooShort"
  | "phoneTooShort"
  | "idTooShort";

export interface CustomerSearchKeyValidation {
  ok: boolean;
  kind?: CustomerSearchKeyKind;
  digitCount: number;
  errorCode?: CustomerSearchKeyErrorCode;
}

export function digitsOnly(value: string): string {
  return (value || "").replace(/\D+/g, "");
}

export function classifyCustomerSearchKey(raw: string): CustomerSearchKeyKind {
  const q = (raw || "").trim();
  const digits = digitsOnly(q);
  const hasLetter = /[A-Za-zÀ-ÿ]/.test(q);
  const compact = q.replace(/\s+/g, "");

  if (
    digits &&
    (!hasLetter || digits.length >= Math.max(1, Math.floor(compact.length * 0.7)))
  ) {
    if (digits.startsWith("0") || digits.startsWith("62")) {
      return "phone";
    }
    return "id";
  }
  return "name";
}

export function validateCustomerSearchKey(
  raw: string,
): CustomerSearchKeyValidation {
  const q = (raw || "").trim();
  if (!q) {
    return { ok: false, digitCount: 0, errorCode: "empty" };
  }

  const kind = classifyCustomerSearchKey(q);
  const digitCount = digitsOnly(q).length;

  if (kind === "name") {
    if (q.length < MIN_NAME_CHARS) {
      return { ok: false, kind, digitCount, errorCode: "nameTooShort" };
    }
    return { ok: true, kind, digitCount };
  }

  if (kind === "phone") {
    if (digitCount < MIN_PHONE_DIGITS) {
      return { ok: false, kind, digitCount, errorCode: "phoneTooShort" };
    }
    return { ok: true, kind, digitCount };
  }

  if (digitCount < MIN_ID_DIGITS) {
    return { ok: false, kind, digitCount, errorCode: "idTooShort" };
  }
  return { ok: true, kind, digitCount };
}
