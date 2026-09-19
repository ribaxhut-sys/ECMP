export type ConfigurationSection =
  | "general"
  | "preferences"
  | "sla"
  | "workflow"
  | "advanced";

export const CONFIGURATION_SECTIONS: readonly ConfigurationSection[] = [
  "general",
  "preferences",
  "sla",
  "workflow",
  "advanced",
] as const;

export type SettingStatusTone = "success" | "warning" | "neutral" | "info";

export type SettingStatusKey =
  | "configured"
  | "needsReview"
  | "disabled"
  | "default";

export function humanizeSettingKey(key: string): string {
  const segment = key.split(/[./]/).filter(Boolean).at(-1) ?? key;
  return segment
    .replace(/[_-]+/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function settingDisplayTitle(input: {
  key: string;
  description: string | null;
}): string {
  return humanizeSettingKey(input.key);
}

export function settingStatus(input: {
  value: string;
  visibility: string;
}): { key: SettingStatusKey; tone: SettingStatusTone } {
  if (input.value.trim() === "") {
    return { key: "default", tone: "neutral" };
  }
  if (input.visibility === "PROTECTED") {
    return { key: "needsReview", tone: "warning" };
  }
  return { key: "configured", tone: "success" };
}

export function matchesSearch(
  query: string,
  ...haystacks: Array<string | null | undefined>
): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return haystacks.some((value) => (value ?? "").toLowerCase().includes(q));
}

/** Dot-keys cannot be next-intl nested paths, so `hq.schedule.start` → `hq_schedule_start`. */
export function settingI18nId(key: string): string {
  return key.replaceAll(".", "_");
}

type SettingsCopy = {
  (key: string): string;
  has: (key: string) => boolean;
};

export function localizedSettingTitle(
  input: { key: string; description: string | null },
  t: SettingsCopy,
): string {
  const labelKey = `settingKey.${settingI18nId(input.key)}.label`;
  return t.has(labelKey) ? t(labelKey) : settingDisplayTitle(input);
}

export function localizedSettingDescription(
  input: { key: string; description: string | null },
  t: SettingsCopy,
  fallback: string,
): string {
  const descKey = `settingKey.${settingI18nId(input.key)}.description`;
  if (t.has(descKey)) return t(descKey);
  return fallback;
}

export function parseStringArraySetting(value: string): string[] | null {
  try {
    const parsed: unknown = JSON.parse(value);
    if (!Array.isArray(parsed) || parsed.length === 0) return null;
    if (!parsed.every((item) => typeof item === "string" && item.trim() !== "")) {
      return null;
    }
    return parsed.map((item) => item.trim());
  } catch {
    return null;
  }
}

const MIME_CHIP_LABEL: Record<string, string> = {
  "application/pdf": "PDF",
  "image/jpeg": "JPEG",
  "image/png": "PNG",
  "image/gif": "GIF",
  "image/webp": "WEBP",
  "text/plain": "TXT",
  "application/msword": "DOC",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    "DOCX",
  "application/vnd.ms-excel": "XLS",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
  "application/zip": "ZIP",
};

export function mimeChipLabel(mime: string): string {
  const key = mime.trim().toLowerCase();
  if (MIME_CHIP_LABEL[key]) return MIME_CHIP_LABEL[key];
  if (!key.includes("/")) return mime.trim();
  const subtype = key.split("/")[1] ?? key;
  const last = subtype.split(".").at(-1) ?? subtype;
  const compact = last.replace(/[^a-z0-9]+/gi, "").toUpperCase();
  return compact || mime;
}

export function formatSettingDraft(value: string): string {
  const items = parseStringArraySetting(value);
  return items ? JSON.stringify(items, null, 2) : value;
}

export function compactSettingValue(value: string): string {
  const items = parseStringArraySetting(value);
  return items ? JSON.stringify(items) : value;
}

export function settingValuesEquivalent(left: string, right: string): boolean {
  if (left === right) return true;
  const a = parseStringArraySetting(left);
  const b = parseStringArraySetting(right);
  if (a && b) return JSON.stringify(a) === JSON.stringify(b);
  return left.trim() === right.trim();
}

export function usesMultilineSettingEditor(value: string, valueType?: string): boolean {
  if ((valueType ?? "").toUpperCase() === "JSON") return true;
  if (parseStringArraySetting(value)) return true;
  return value.length > 80;
}
