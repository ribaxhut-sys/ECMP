/**
 * Clipboard contract between ECMP intake (copy) and Sistem Antrian CRO (paste).
 *
 * Text/plain only — Windows desktop clipboard does not keep custom MIME types
 * from the browser. Labels are protocol tokens, not UI i18n.
 *
 * Salin profil:
 *   ECMP-WP-1
 *   Nama: …
 *   ID WP: …
 *   Telepon: …
 *   Email: …
 *
 * Salin ID WP: raw identifier (digits only when the value is numeric).
 * Alamat is not in Customer 360 — paste must leave it untouched.
 */

export const TAXPAYER_PROFILE_CLIPBOARD_MARKER = "ECMP-WP-1";

export interface TaxpayerProfileClipboardFields {
  nama: string;
  idWp: string;
  telepon: string;
  email: string;
}

export type ParsedTaxpayerProfileClipboard =
  | { kind: "profile"; fields: TaxpayerProfileClipboardFields }
  | { kind: "idWp"; idWp: string }
  | { kind: "invalid" };

const LABEL_NAMA = "Nama";
const LABEL_ID_WP = "ID WP";
const LABEL_TELEPON = "Telepon";
const LABEL_EMAIL = "Email";

export function taxpayerIdForClipboard(raw: string): string {
  const value = (raw || "").trim();
  if (!value) return "";
  const digits = value.replace(/\D+/g, "");
  const compact = value.replace(/[\s-]/g, "");
  if (digits.length >= 8 && digits.length === compact.length) {
    return digits;
  }
  return value.replace(/\s+/g, "");
}

export function formatTaxpayerProfileClipboard(
  fields: TaxpayerProfileClipboardFields,
): string {
  return [
    TAXPAYER_PROFILE_CLIPBOARD_MARKER,
    `${LABEL_NAMA}: ${fields.nama.trim()}`,
    `${LABEL_ID_WP}: ${taxpayerIdForClipboard(fields.idWp)}`,
    `${LABEL_TELEPON}: ${fields.telepon.trim()}`,
    `${LABEL_EMAIL}: ${fields.email.trim()}`,
  ].join("\n");
}

function parseLabeledLine(line: string): { label: string; value: string } | null {
  const idx = line.indexOf(":");
  if (idx <= 0) return null;
  return {
    label: line.slice(0, idx).trim(),
    value: line.slice(idx + 1).trim(),
  };
}

function isDigitsOnlyId(value: string): boolean {
  const digits = value.replace(/\D+/g, "");
  const compact = value.replace(/[\s-]/g, "");
  return digits.length >= 8 && digits.length === compact.length;
}

function isCompactCustomerNumber(value: string): boolean {
  const compact = value.replace(/\s+/g, "");
  if (compact.length < 8 || compact.length > 64) return false;
  if (/\s/.test(value.trim()) && !isDigitsOnlyId(value)) return false;
  return /[0-9]/.test(compact) && /^[A-Za-z0-9._/-]+$/.test(compact);
}

export function parseTaxpayerProfileClipboard(
  raw: string,
): ParsedTaxpayerProfileClipboard {
  const text = (raw || "").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").trim();
  if (!text) return { kind: "invalid" };

  const lines = text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  if (lines[0] === TAXPAYER_PROFILE_CLIPBOARD_MARKER) {
    const fields: TaxpayerProfileClipboardFields = {
      nama: "",
      idWp: "",
      telepon: "",
      email: "",
    };
    for (const line of lines.slice(1)) {
      const parsed = parseLabeledLine(line);
      if (!parsed) continue;
      const label = parsed.label.toLowerCase();
      if (label === LABEL_NAMA.toLowerCase()) fields.nama = parsed.value;
      else if (label === LABEL_ID_WP.toLowerCase()) {
        fields.idWp = taxpayerIdForClipboard(parsed.value);
      } else if (label === LABEL_TELEPON.toLowerCase()) {
        fields.telepon = parsed.value;
      } else if (label === LABEL_EMAIL.toLowerCase()) {
        fields.email = parsed.value;
      }
    }
    if (!fields.nama && !fields.idWp && !fields.telepon && !fields.email) {
      return { kind: "invalid" };
    }
    return { kind: "profile", fields };
  }

  if (isDigitsOnlyId(text) || isCompactCustomerNumber(text)) {
    return { kind: "idWp", idWp: taxpayerIdForClipboard(text) };
  }
  return { kind: "invalid" };
}

export async function writeClipboardText(text: string): Promise<void> {
  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  if (typeof document === "undefined") {
    throw new Error("clipboard unavailable");
  }
  const el = document.createElement("textarea");
  el.value = text;
  el.setAttribute("readonly", "");
  el.style.position = "fixed";
  el.style.left = "-9999px";
  document.body.appendChild(el);
  el.select();
  const ok = document.execCommand("copy");
  el.remove();
  if (!ok) throw new Error("clipboard unavailable");
}
