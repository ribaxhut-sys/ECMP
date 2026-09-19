/**
 * Navigation catalog for the application shell.
 * Source of truth remains layouts/app-layout/nav — re-exported for shell consumers.
 */
export {
  APP_NAV_ITEMS,
  APP_NAV_GROUPS,
} from "@/shared/layouts/app-layout/nav";
export type {
  NavItem,
  NavGroup,
  NavSubgroup,
} from "@/shared/layouts/app-layout/nav";

export {
  NAV_PREFERENCE_MODES,
  DEFAULT_NAV_PREFERENCE_MODE,
  DEFAULT_NAV_PREFERENCE_STATE,
  isNavPreferenceMode,
  navPreferenceStorageKey,
  normalizeNavPreferenceMode,
  parseNavPreference,
  resolveExpandedSubgroups,
  serializeNavPreference,
} from "./navPreference";
export type {
  NavPreferenceMode,
  NavPreferenceState,
  ResolveExpandedInput,
} from "./navPreference";

export { NavPreferenceProvider, useNavPreference } from "./NavPreferenceProvider";
