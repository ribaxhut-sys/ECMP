/**
 * Per-user sidebar presentation preference (Pengaturan → Preferensi → Navigasi).
 *
 * Presentation only: it decides how the complaint subgroups are *displayed*,
 * never which menus a user may see. Permission filtering stays in
 * `isNavItemVisible` / AuthProvider and runs before any of this.
 *
 * Storage follows the existing persisted-client-preference pattern
 * (`LOCALE_STORAGE_KEY` in `@/i18n/config`): localStorage, best-effort, keyed
 * per user id so a shared browser does not leak one user's layout to another.
 * No backend table or API is introduced for it.
 */

export const NAV_PREFERENCE_MODES = ["auto", "remember", "expandAll"] as const;

export type NavPreferenceMode = (typeof NAV_PREFERENCE_MODES)[number];

export const DEFAULT_NAV_PREFERENCE_MODE: NavPreferenceMode = "auto";

export function isNavPreferenceMode(value: unknown): value is NavPreferenceMode {
  return (
    typeof value === "string" &&
    (NAV_PREFERENCE_MODES as readonly string[]).includes(value)
  );
}

/** Unknown / corrupt / missing values always land on "auto" (§10 fallback). */
export function normalizeNavPreferenceMode(value: unknown): NavPreferenceMode {
  return isNavPreferenceMode(value) ? value : DEFAULT_NAV_PREFERENCE_MODE;
}

export interface NavPreferenceState {
  mode: NavPreferenceMode;
  /** Subgroup id → expanded. Only consulted in "remember" mode. */
  expanded: Readonly<Record<string, boolean>>;
}

export const DEFAULT_NAV_PREFERENCE_STATE: NavPreferenceState = {
  mode: DEFAULT_NAV_PREFERENCE_MODE,
  expanded: {},
};

const STORAGE_KEY_PREFIX = "ecmp.nav.complaintsSidebar";

export function navPreferenceStorageKey(userId?: string | null): string {
  return userId ? `${STORAGE_KEY_PREFIX}:${userId}` : STORAGE_KEY_PREFIX;
}

function sanitizeExpanded(value: unknown): Record<string, boolean> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  const out: Record<string, boolean> = {};
  for (const [key, entry] of Object.entries(value as Record<string, unknown>)) {
    if (typeof entry === "boolean") out[key] = entry;
  }
  return out;
}

/** Never throws — a malformed payload degrades to the default state. */
export function parseNavPreference(
  raw: string | null | undefined,
): NavPreferenceState {
  if (!raw) return DEFAULT_NAV_PREFERENCE_STATE;
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return DEFAULT_NAV_PREFERENCE_STATE;
    }
    const record = parsed as Record<string, unknown>;
    return {
      mode: normalizeNavPreferenceMode(record.mode),
      expanded: sanitizeExpanded(record.expanded),
    };
  } catch {
    return DEFAULT_NAV_PREFERENCE_STATE;
  }
}

export function serializeNavPreference(state: NavPreferenceState): string {
  return JSON.stringify({
    mode: normalizeNavPreferenceMode(state.mode),
    expanded: sanitizeExpanded(state.expanded),
  });
}

export interface ResolveExpandedInput {
  mode: NavPreferenceMode;
  /** Subgroups actually rendered (already permission-filtered). */
  subgroupIds: readonly string[];
  /** Subgroup owning the active route, if any. */
  activeSubgroupId?: string | null;
  /** Persisted expand/collapse choices ("remember" mode). */
  remembered?: Readonly<Record<string, boolean>>;
  /** Manual toggles made during this visit ("auto" mode only). */
  overrides?: Readonly<Record<string, boolean>>;
}

/**
 * Expanded state per subgroup.
 *
 * - expandAll → every rendered subgroup open.
 * - remember  → last stored choice; falls back to the active-route subgroup
 *               (and, with nothing active, the first subgroup) so a first-time
 *               user never faces an all-collapsed sidebar.
 * - auto      → only the active-route subgroup, with in-visit manual toggles
 *               layered on top.
 */
export function resolveExpandedSubgroups(
  input: ResolveExpandedInput,
): Record<string, boolean> {
  const {
    mode,
    subgroupIds,
    activeSubgroupId = null,
    remembered = {},
    overrides = {},
  } = input;

  const fallbackId = activeSubgroupId ?? subgroupIds[0] ?? null;
  const result: Record<string, boolean> = {};

  for (const id of subgroupIds) {
    if (mode === "expandAll") {
      result[id] = true;
      continue;
    }
    const base = id === fallbackId;
    if (mode === "remember") {
      result[id] = remembered[id] ?? base;
      continue;
    }
    result[id] = overrides[id] ?? base;
  }

  return result;
}
