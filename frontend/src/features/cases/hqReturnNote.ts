import type { CmBatch1HqReturnReasonCode } from "@/lib/api";

export const HQ_RETURN_REASON_CODES: readonly CmBatch1HqReturnReasonCode[] = [
  "MISSING_ATTACHMENT",
  "INCOMPLETE_CHRONOLOGY",
  "UNCLEAR_CUSTOMER_DATA",
  "WRONG_CATEGORY_OR_ROUTING",
  "ADDITIONAL_EVIDENCE_REQUIRED",
  "OTHER",
];

const PREFIX = /^\[([A-Z][A-Z0-9_]*)\]\s*([\s\S]*)$/;

const KNOWN = new Set<string>(HQ_RETURN_REASON_CODES);

export function splitHqReturnNote(text: string): {
  code: CmBatch1HqReturnReasonCode | null;
  body: string;
} {
  const trimmed = text.trim();
  const match = trimmed.match(PREFIX);
  if (!match) return { code: null, body: trimmed };
  const code = match[1];
  if (!code || !KNOWN.has(code)) return { code: null, body: trimmed };
  return {
    code: code as CmBatch1HqReturnReasonCode,
    body: (match[2] || "").trim(),
  };
}

/** Replace `[INCOMPLETE_CHRONOLOGY] …` with a human label. */
export function formatHqReturnNoteDisplay(
  text: string,
  labelFor: (code: CmBatch1HqReturnReasonCode) => string | undefined,
): string {
  const { code, body } = splitHqReturnNote(text);
  if (!code) return text;
  const label = labelFor(code)?.trim();
  if (!label) return text;
  return body ? `${label} — ${body}` : label;
}
