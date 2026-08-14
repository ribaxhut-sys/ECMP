/**
 * Human-readable labels for Batch-1 confirmation “Rincian pendaftaran”.
 * Intake UI does not collect category (API default GENERAL) — hide that noise.
 */

const CHANNEL_LABEL_KEYS = {
  CALL: "channelCall",
  EMAIL: "channelEmail",
  BRANCH: "channelBranch",
  WEB: "channelWeb",
  OTHER: "channelOther",
} as const;

export type CmBatch1ChannelLabelKey =
  (typeof CHANNEL_LABEL_KEYS)[keyof typeof CHANNEL_LABEL_KEYS];

/** next-intl `complaints.*` key for a channel code, or null → show raw value. */
export function cmBatch1ChannelLabelKey(
  channel: string | null | undefined,
): CmBatch1ChannelLabelKey | null {
  const raw = (channel ?? "").trim().toUpperCase();
  if (!raw) return null;
  return CHANNEL_LABEL_KEYS[raw as keyof typeof CHANNEL_LABEL_KEYS] ?? null;
}

/**
 * Category is system-defaulted to GENERAL on intake and not shown on the create
 * form — omit it from registration details unless a real value was set later.
 */
export function shouldShowCmBatch1Category(
  category: string | null | undefined,
): boolean {
  const raw = (category ?? "").trim().toUpperCase();
  return Boolean(raw) && raw !== "GENERAL";
}

/** Wajib Pajak: "Nama (nomor)" — names alone are not unique. */
export function formatCmBatch1CustomerLabel(
  displayName: string | null | undefined,
  customerNumber: string | null | undefined,
  fallbackId?: string | null,
): string | null {
  const name = (displayName ?? "").trim();
  const number = (customerNumber ?? "").trim() || (fallbackId ?? "").trim();
  if (name && number) return `${name} (${number})`;
  if (name) return name;
  if (number) return number;
  return null;
}

export type CmBatch1UnitRef = {
  id: string;
  code: string;
  name: string;
};

/** Prefer unit name; fall back to code / raw owningUnitId. */
export function resolveCmBatch1RegistrationUnitLabel(
  owningUnitId: string | null | undefined,
  units: readonly CmBatch1UnitRef[],
): string | null {
  const key = (owningUnitId ?? "").trim();
  if (!key) return null;
  const match = units.find(
    (u) => u.id === key || u.code.toUpperCase() === key.toUpperCase(),
  );
  if (match) {
    const name = match.name.trim();
    if (name) return name;
    const code = match.code.trim();
    if (code) return code;
  }
  return key;
}
