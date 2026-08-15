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
  const display = officerDisplayName(name);
  if (!display) return null;
  const parts = display.split(/\s+/).filter(Boolean);
  if (parts.length >= 3) {
    const code = `${parts[0][0] ?? ""}${parts[1][0] ?? ""}${parts[2][0] ?? ""}`;
    return code.toUpperCase() || null;
  }
  if (parts.length === 2) {
    const first = parts[0] ?? "";
    const last = parts[1] ?? "";
    if (last.length >= 2) {
      return `${first[0] ?? ""}${last.slice(0, 2)}`.toUpperCase();
    }
    return `${first.slice(0, 2)}${last[0] ?? ""}`.toUpperCase().slice(0, 3);
  }
  const letters = [...(parts[0] ?? "")].filter((ch) => /\p{L}/u.test(ch)).join("");
  const slice = letters.slice(0, 3).toUpperCase();
  return slice || null;
}
