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
  const description = input.description?.trim();
  if (description && description.length <= 80) return description;
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
  const raw = input.description?.trim();
  return raw || fallback;
}
