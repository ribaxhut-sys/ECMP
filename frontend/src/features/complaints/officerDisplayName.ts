import { nameInitials } from "@/shared/utils/initials";

/** User directory ids must never be shown as a PIC / petugas label. */
const USER_ID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isUserDirectoryId(value: string | null | undefined): boolean {
  return USER_ID_RE.test((value ?? "").trim());
}

/** First candidate that looks like a human name, not a user UUID. */
export function officerDisplayName(
  ...candidates: Array<string | null | undefined>
): string | null {
  for (const raw of candidates) {
    const value = (raw ?? "").trim();
    if (value && !isUserDirectoryId(value)) return value;
  }
  return null;
}

/**
 * Three-letter PIC code (same rule as activity avatars):
 * Ahmad Santoso → ASA, Ahmad Santoso Adi → ASA, Ahmad → AHM.
 */
export function officerInitials(name: string | null | undefined): string | null {
  return nameInitials(officerDisplayName(name));
}
