export interface NavItem {
  id: string;
  /** Key within the "nav" message namespace, e.g. "dashboard" -> t("dashboard") */
  labelKey: string;
  href: string;
  icon:
    | "dashboard"
    | "complaints"
    | "queue"
    | "assignments"
    | "resolutions"
    | "reports"
    | "users"
    | "settings"
    | "adjustments"
    | "attachments"
    | "announcements"
    | "megaphone"
    | "knowledge";
  /** Optional notification badge (presentation only). */
  badge?: number | string;
  /**
   * Canonical permission strings (existing catalog, see backend/app/core/rbac.py)
   * gating this item's visibility. Item is visible if the user holds at least
   * one. Omit for items with no permission gate.
   */
  requiredPermissions?: readonly string[];
}

/** Visible iff the item has no gate, or the caller holds at least one of its
 * requiredPermissions. hasPermission is caller-supplied so this stays a pure
 * function — AuthProvider.hasPermission already owns wildcard ("*") handling. */
export function isNavItemVisible(
  item: Pick<NavItem, "requiredPermissions">,
  hasPermission: (permission: string) => boolean,
): boolean {
  if (!item.requiredPermissions || item.requiredPermissions.length === 0) {
    return true;
  }
  return item.requiredPermissions.some((permission) => hasPermission(permission));
}

function navPath(raw: string): string {
  const withoutQuery = (raw.split("?")[0] || "").replace(/\/+$/, "") || "/";
  return withoutQuery;
}

/**
 * Longest-prefix match so a parent like `/internal` is not active under
 * `/internal/follow-up` when a more specific nav href also matches.
 * Query strings on hrefs (e.g. Pusat `?needsPusatHandling=1`) are ignored.
 */
export function resolveActiveNavHref(
  pathname: string,
  hrefs: readonly string[],
): string | null {
  const path = navPath(pathname);
  let best: string | null = null;
  for (const raw of hrefs) {
    const href = navPath(raw);
    if (path === href || path.startsWith(`${href}/`)) {
      if (best === null || href.length > best.length) {
        best = href;
      }
    }
  }
  return best;
}

export function isNavItemActive(
  pathname: string,
  href: string,
  allHrefs: readonly string[],
): boolean {
  return resolveActiveNavHref(pathname, allHrefs) === navPath(href);
}

/**
 * Collapsible subgroup inside a NavGroup — presentation only.
 * Membership mirrors the parent group; it never widens access.
 */
export interface NavSubgroup {
  id: string;
  /** Key within the "nav" namespace */
  labelKey: string;
  itemIds: readonly string[];
}

/**
 * Visual nav groups for Sidebar hierarchy only.
 * Does not change routes, menu membership, or item order within each group.
 */
export interface NavGroup {
  id: string;
  /** Key within the "nav" namespace. Omit for an unlabelled lead-in group. */
  labelKey?: string;
  itemIds: readonly string[];
  /**
   * Collapsible subgroups. When present, `itemIds` stays the flattened union
   * so permission filtering and href collection keep working unchanged.
   */
  subgroups?: readonly NavSubgroup[];
}

/**
 * Which subgroup owns the currently active route.
 * Pure — the caller supplies only the hrefs it already decided are visible,
 * so permission filtering stays upstream and is never re-implemented here.
 */
export function resolveActiveSubgroupId(
  pathname: string,
  subgroups: readonly { id: string; hrefs: readonly string[] }[],
  allHrefs: readonly string[],
): string | null {
  const active = resolveActiveNavHref(pathname, allHrefs);
  if (!active) return null;
  for (const subgroup of subgroups) {
    const owns = subgroup.hrefs.some((href) => navPath(href) === active);
    if (owns) return subgroup.id;
  }
  return null;
}

/** Primary app navigation — UI routes for modules. */
export const APP_NAV_ITEMS: readonly NavItem[] = [
  { id: "dashboard", labelKey: "dashboard", href: "/dashboard", icon: "dashboard" },
  {
    id: "complaints",
    labelKey: "complaints",
    // Mode A primary entry = Aggregate list at /complaints (detail stays /complaints/cm/[id]).
    href: "/complaints",
    icon: "complaints",
    requiredPermissions: [
      "complaints:read",
      "complaints:create",
      "complaints:update",
      "complaints:assign",
      "complaints:escalate",
      "complaints:close",
    ],
  },
  {
    id: "followUp",
    labelKey: "followUp",
    href: "/tindak-lanjut",
    icon: "assignments",
    requiredPermissions: ["complaints:read"],
  },
  {
    id: "cases",
    labelKey: "cases",
    // DEC-025 §3.6 — primary Case work door (Foundation /queue stays routable).
    href: "/complaints/cm/cases",
    icon: "queue",
    requiredPermissions: ["complaints:read"],
  },
  { id: "queue", labelKey: "queue", href: "/queue", icon: "queue" },
  {
    id: "hqSchedule",
    labelKey: "hqSchedule",
    href: "/complaints/cm/hq-schedule",
    icon: "queue",
    // Cabang + Pusat: anyone with complaints:read. Per-complaint pending
    // proposals stay on the Pusat detail API, not this menu gate.
    requiredPermissions: ["complaints:read"],
  },
  {
    id: "assignments",
    labelKey: "assignments",
    href: "/assignments",
    icon: "assignments",
  },
  {
    id: "resolutions",
    labelKey: "resolutions",
    href: "/resolutions",
    icon: "resolutions",
  },
  {
    id: "announcements",
    labelKey: "announcements",
    href: "/announcements",
    icon: "announcements",
    // Reader archive — every Pengaduan-module user (announcement:read).
    requiredPermissions: ["announcement:read"],
  },
  {
    id: "announcementsManage",
    labelKey: "announcementsManage",
    href: "/announcements/manage",
    icon: "megaphone",
    // Coarse permission gate; Sidebar also requires Pusat unit via
    // mayManageAnnouncements (role codes SUPERVISOR/MANAGER are shared with Cabang).
    requiredPermissions: ["announcement:manage"],
  },
  {
    id: "knowledge",
    labelKey: "knowledge",
    href: "/knowledge",
    icon: "knowledge",
    requiredPermissions: ["knowledge:read"],
  },
  {
    id: "attachments",
    labelKey: "attachments",
    href: "/attachments",
    icon: "attachments",
  },
  { id: "reports", labelKey: "reports", href: "/reports", icon: "reports" },
  { id: "users", labelKey: "users", href: "/users", icon: "users" },
  { id: "settings", labelKey: "settings", href: "/settings", icon: "adjustments" },
  /**
   * Pengaduan Internal — Mode A (Cabang ↔ Pusat).
   * Sidebar visibility and `/internal` layout gated by
   * `NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI` (default off).
   */
  {
    id: "internalDashboard",
    labelKey: "internalDashboard",
    href: "/internal",
    icon: "dashboard",
  },
  {
    id: "internalComplaints",
    labelKey: "internalComplaints",
    href: "/internal/complaints",
    icon: "complaints",
  },
  {
    id: "internalAssignments",
    labelKey: "internalAssignments",
    href: "/internal/assignments",
    icon: "assignments",
  },
  {
    id: "internalFollowUp",
    labelKey: "internalFollowUp",
    href: "/internal/follow-up",
    icon: "queue",
  },
  {
    id: "internalVerification",
    labelKey: "internalVerification",
    href: "/internal/verification",
    icon: "resolutions",
  },
  {
    id: "internalReports",
    labelKey: "internalReports",
    href: "/internal/reports",
    icon: "reports",
  },
] as const;

/** Nav item ids for the unauthorized Pengaduan Internal prototype. */
export const INTERNAL_NAV_ITEM_IDS = [
  "internalDashboard",
  "internalComplaints",
  "internalAssignments",
  "internalFollowUp",
  "internalVerification",
  "internalReports",
] as const;

export type InternalNavItemId = (typeof INTERNAL_NAV_ITEM_IDS)[number];

export function isInternalNavItemId(id: string): id is InternalNavItemId {
  return (INTERNAL_NAV_ITEM_IDS as readonly string[]).includes(id);
}

/** Subgroup ids under the "complaints" group — stable keys for the
 * per-user sidebar preference, so renaming a label never orphans stored state. */
export const TAXPAYER_COMPLAINTS_SUBGROUP_ID = "taxpayerComplaints";
export const INTERNAL_COMPLAINTS_SUBGROUP_ID = "internalComplaints";

/** Sidebar-visible items under PENGADUAN → Wajib Pajak. */
const TAXPAYER_COMPLAINTS_ITEM_IDS = [
  "dashboard",
  "complaints",
  "cases",
  "followUp",
  "hqSchedule",
  "reports",
] as const;

/** Sidebar-visible items under PENGADUAN → Internal (no Penugasan). */
const INTERNAL_COMPLAINTS_ITEM_IDS = [
  "internalDashboard",
  "internalComplaints",
  "internalFollowUp",
  "internalVerification",
  "internalReports",
] as const;

/**
 * Presentation-only sidebar hierarchy.
 * Items that remain in APP_NAV_ITEMS but are omitted here (queue, assignments,
 * resolutions, internalAssignments) keep their routes/pages; they are simply
 * not shown in the main ECMP sidebar (DEC-025 §3.6 — Foundation = legacy).
 */
export const APP_NAV_GROUPS: readonly NavGroup[] = [
  {
    id: "complaints",
    labelKey: "groupComplaints",
    itemIds: [...TAXPAYER_COMPLAINTS_ITEM_IDS, ...INTERNAL_COMPLAINTS_ITEM_IDS],
    subgroups: [
      {
        id: TAXPAYER_COMPLAINTS_SUBGROUP_ID,
        labelKey: "subgroupTaxpayerComplaints",
        itemIds: TAXPAYER_COMPLAINTS_ITEM_IDS,
      },
      {
        id: INTERNAL_COMPLAINTS_SUBGROUP_ID,
        labelKey: "subgroupInternalComplaints",
        itemIds: INTERNAL_COMPLAINTS_ITEM_IDS,
      },
    ],
  },
  {
    id: "information",
    labelKey: "groupInformation",
    // Informasi = Pengumuman + Pengetahuan (placeholder — separate milestone)
    // + Lampiran. Domain reports stay under their own subgroups: Wajib Pajak
    // → /reports, Internal → /internal/reports. Flat group (no subgroups) —
    // same shape as "administration", no chevron.
    itemIds: ["announcements", "announcementsManage", "knowledge", "attachments"],
  },
  {
    id: "administration",
    labelKey: "groupAdministration",
    itemIds: ["users", "settings"],
  },
] as const;
