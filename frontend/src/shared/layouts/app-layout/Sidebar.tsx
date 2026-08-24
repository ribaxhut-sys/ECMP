"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import type { Branch } from "@/lib/api/branches";
import { mayManageAnnouncements } from "@/features/announcements/announcementManageGate";
import { prefersComplaintNumberIdentity } from "@/features/complaints/cmBatch1ComplaintListIdentity";
import { useOrgUnitBranch } from "@/features/announcements/useOrgUnitCode";
import { useUnreadAnnouncementCount } from "@/features/announcements/useUnreadAnnouncementCount";
import { useHqScheduleTodayCount } from "@/features/hq-schedule/useHqScheduleTodayCount";
import { usePendingTransferRequestCount } from "@/features/internal-complaints/usePendingTransferRequestCount";
import { usePendingWithdrawRequestCount } from "@/features/internal-complaints/usePendingWithdrawRequestCount";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";
import { isShellUiBatch } from "@/shared/config/uiBatch";
import {
  IconAdjustments,
  IconAssignments,
  IconBell,
  IconChevronDown,
  IconComplaints,
  IconDashboard,
  IconFile,
  IconMegaphone,
  IconPaperclip,
  IconQueue,
  IconReports,
  IconResolutions,
  IconSettings,
  IconUsers,
} from "@/shared/icons";
import { useSidebar } from "@/shared/hooks";
import {
  resolveExpandedSubgroups,
  useNavPreference,
} from "@/shared/navigation";
import { cn } from "@/shared/utils";
import {
  APP_NAV_GROUPS,
  APP_NAV_ITEMS,
  INTERNAL_COMPLAINTS_SUBGROUP_ID,
  isInternalNavItemId,
  isNavItemActive,
  isNavItemVisible,
  resolveActiveSubgroupId,
  type NavGroup,
  type NavItem,
  type NavSubgroup,
} from "./nav";
import { B0_NAV_GROUPS, B0_NAV_ITEMS } from "./b0Nav";

function isAppNavItemVisible(
  item: NavItem,
  hasPermission: (permission: string) => boolean,
): boolean {
  if (isInternalNavItemId(item.id) && !isInternalComplaintsUiEnabled()) {
    return false;
  }
  return isNavItemVisible(item, hasPermission);
}

/**
 * Resolve the unit label under the PELAYANAN brand.
 * - Cabang: branch name from catalog (matched by user.branchId).
 * - Pusat / head-office (EBS-001): branchId is null — show "Pusat", not blank.
 *
 * Derives from the branch already resolved by `useOrgUnitBranch` in the
 * caller — no fetch of its own, so the sidebar issues one branch-catalog
 * request instead of two for the same `user.branchId`.
 */
function useBrandUnitLabel(orgUnitBranch: Branch | null | undefined): string | null {
  const { user, hasPermission } = useAuth();
  const tCommon = useTranslations("common");
  const branchId = user?.branchId ?? null;
  const canReadBranches = hasPermission("complaints:read");

  if (!user) return null;
  if (!branchId) return tCommon("headOfficeUnit");
  if (!canReadBranches) return null;
  return orgUnitBranch?.name ?? null;
}

const iconMap = {
  dashboard: IconDashboard,
  complaints: IconComplaints,
  queue: IconQueue,
  assignments: IconAssignments,
  resolutions: IconResolutions,
  reports: IconReports,
  users: IconUsers,
  settings: IconSettings,
  adjustments: IconAdjustments,
  attachments: IconPaperclip,
  announcements: IconBell,
  megaphone: IconMegaphone,
  knowledge: IconFile,
} as const;

function NavBadge({
  value,
  tone = "default",
}: {
  value: number | string;
  tone?: "default" | "unread";
}) {
  const label = typeof value === "number" && value > 99 ? "99+" : String(value);
  return (
    <span
      className={cn(
        "ml-auto inline-flex min-w-5 shrink-0 items-center justify-center rounded-full px-1.5",
        "text-[length:var(--ecmp-font-overline-size)] font-semibold leading-5",
        tone === "unread"
          ? "bg-ecmp-danger text-ecmp-danger-foreground"
          : "bg-ecmp-primary-muted text-ecmp-primary",
      )}
    >
      {label}
    </span>
  );
}

function NavLink({
  item,
  label,
  allHrefs,
  onNavigate,
}: {
  item: NavItem;
  label: string;
  allHrefs: readonly string[];
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const tAnnouncements = useTranslations("announcements");
  const active = isNavItemActive(pathname, item.href, allHrefs);
  const Icon = iconMap[item.icon];
  const unreadCount =
    item.id === "announcements" && typeof item.badge === "number"
      ? item.badge
      : 0;
  const accessibleName =
    unreadCount > 0
      ? `${label}, ${tAnnouncements("sidebarUnreadCount", { count: unreadCount })}`
      : label;

  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      aria-label={accessibleName}
      className={cn(
        "ecmp-touch group relative flex items-center gap-3 rounded-[var(--ecmp-radius-md)] px-3",
        "text-[length:var(--ecmp-font-body-small-size)] font-normal tracking-[-0.01em]",
        "transition-[background-color,color,transform] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
        active
          ? "bg-ecmp-selected/70 font-medium text-ecmp-text-primary"
          : "text-ecmp-text-secondary hover:bg-ecmp-hover hover:text-ecmp-text-primary",
      )}
    >
      <Icon
        className={cn(
          "size-5 shrink-0",
          active
            ? "text-ecmp-primary"
            : "text-ecmp-muted group-hover:text-ecmp-text-primary",
        )}
      />
      <span className="min-w-0 flex-1 truncate">{label}</span>
      {item.badge !== undefined && item.badge !== null && item.badge !== "" ? (
        <NavBadge
          value={item.badge}
          tone={item.id === "announcements" ? "unread" : "default"}
        />
      ) : null}
    </Link>
  );
}

function Brand({
  asLink,
  href,
  onNavigate,
  branchName,
}: {
  asLink: boolean;
  href: string;
  onNavigate?: () => void;
  branchName: string | null;
}) {
  const tCommon = useTranslations("common");
  const content = (
    <span className="flex min-w-0 flex-col gap-0.5 leading-tight">
      <span className="truncate text-[1.25rem] font-semibold tracking-tight text-ecmp-primary">
        {tCommon("appName")}
      </span>
      {branchName ? (
        <span className="truncate text-[14px] font-semibold text-ecmp-text-primary">
          {branchName}
        </span>
      ) : null}
    </span>
  );

  if (asLink) {
    return (
      <Link href={href} onClick={onNavigate} className="min-w-0">
        {content}
      </Link>
    );
  }

  return content;
}

/**
 * `orgUnitBranch` is resolved once by the caller (`Sidebar`) and passed in —
 * this used to call `useOrgUnitCode()` itself, and since both `Sidebar` and
 * `NavSections` called this hook, the branch catalog was fetched twice per
 * page load for the identical `user.branchId` lookup.
 */
function useShellNav(orgUnitBranch: Branch | null | undefined): {
  groups: typeof APP_NAV_GROUPS;
  itemsById: Record<string, NavItem>;
  homeHref: string;
  isItemVisible: (item: NavItem) => boolean;
} {
  const {
    hasPermission,
    roles,
    isMockSession,
    mockPersona,
    officerWorkMode,
  } = useAuth();
  const orgUnitCode =
    orgUnitBranch === undefined ? undefined : orgUnitBranch?.code ?? null;
  const batchB0 = isShellUiBatch() || isMockSession;

  if (!batchB0) {
    const itemsById = Object.fromEntries(
      APP_NAV_ITEMS.map((item) => [item.id, item]),
    ) as Record<string, NavItem>;
    return {
      groups: APP_NAV_GROUPS,
      itemsById,
      // Brand → Dashboard, the app's default home (LOCKED). "/" is the
      // post-login entry-point gate, not a content route — see
      // (app)/page.tsx; it must not be reused for in-app navigation to
      // avoid re-triggering the unread-announcement redirect.
      homeHref: "/dashboard",
      isItemVisible: (item) => {
        if (!isAppNavItemVisible(item, hasPermission)) return false;
        if (item.id === "announcementsManage") {
          // Hide while org unit resolves — avoids flashing manage to Cabang.
          if (orgUnitCode === undefined) return false;
          return mayManageAnnouncements({
            roles,
            hasPermission,
            orgUnitCode,
          });
        }
        // Case inbox = Cabang work door (DEC-025 route stays deep-linkable).
        // Pusat / Admin tanpa branch / loading → hide sidebar entry.
        if (item.id === "cases") {
          return prefersComplaintNumberIdentity(orgUnitCode);
        }
        return true;
      },
    };
  }

  const itemsById = Object.fromEntries(
    B0_NAV_ITEMS.map((item) => [item.id, item]),
  ) as Record<string, NavItem>;

  return {
    groups: B0_NAV_GROUPS,
    itemsById,
    homeHref:
      mockPersona === "supervisor"
        ? "/queue"
        : mockPersona === "administrator"
          ? "/settings"
          : "/workspace",
    isItemVisible: (item) => {
      if (mockPersona === "complaint_officer") {
        if (item.id === "workspace") return officerWorkMode === "intake";
        if (item.id === "queue") return officerWorkMode === "handling";
        return false;
      }
      return isNavItemVisible(item, hasPermission);
    },
  };
}

const GROUP_HEADING_CLASS =
  "px-3 pb-2 text-[11px] font-semibold uppercase tracking-[0.08em] text-ecmp-muted";

/**
 * Soft domain panel chrome — distinguishes Wajib Pajak vs Internal without
 * heavy cards. Collapse/expand behaviour is unchanged.
 */
function resolveDomainChrome(subgroupId: string): {
  panel: string;
  label: string;
  hoverLabel: string;
  divider: string;
} {
  if (subgroupId === INTERNAL_COMPLAINTS_SUBGROUP_ID) {
    return {
      panel:
        "rounded-[var(--ecmp-radius-md)] border border-ecmp-info/20 bg-ecmp-info-muted/45 pl-0.5 border-l-[3px] border-l-ecmp-info",
      label: "text-ecmp-info",
      hoverLabel: "hover:text-ecmp-info",
      divider: "border-ecmp-info/20",
    };
  }
  // Default: Wajib Pajak (and any non-internal subgroup)
  return {
    panel:
      "rounded-[var(--ecmp-radius-md)] border border-ecmp-primary/15 bg-ecmp-primary-muted/40 pl-0.5 border-l-[3px] border-l-ecmp-primary",
    label: "text-ecmp-primary",
    hoverLabel: "hover:text-ecmp-primary",
    divider: "border-ecmp-primary/15",
  };
}

/**
 * Domain subgroup heading — uppercase + weight 600 (match PELAYANAN).
 * `!font-[600]` beats the global `button { font: inherit }` reset that
 * otherwise wipes Tailwind weight utilities on disclosure buttons.
 */
const SUBGROUP_HEADING_BASE_CLASS =
  "px-3 pt-1 pb-1 text-[17px] !font-[600] uppercase tracking-tight";

/**
 * Expand/collapse state for the complaint subgroups.
 *
 * Presentation only — `subgroups` arrives already permission-filtered, so a
 * preference can never surface a menu the user may not see.
 */
function useSubgroupExpansion(
  subgroups: readonly { id: string; hrefs: readonly string[] }[],
  allHrefs: readonly string[],
) {
  const pathname = usePathname();
  const { mode, expanded: remembered, setSubgroupExpanded } = useNavPreference();
  const [overrides, setOverrides] = useState<Record<string, boolean>>({});

  const activeSubgroupId = resolveActiveSubgroupId(
    pathname,
    subgroups,
    allHrefs,
  );

  // Any navigation re-syncs "auto" to the route-owned subgroup.
  useEffect(() => {
    setOverrides({});
  }, [pathname]);

  const subgroupIds = subgroups.map((subgroup) => subgroup.id);

  const resolved = resolveExpandedSubgroups({
    mode,
    subgroupIds,
    activeSubgroupId,
    remembered,
    overrides,
  });

  return {
    activeSubgroupId,
    /** expandAll pins every subgroup open — nothing left to toggle. */
    collapsible: mode !== "expandAll",
    isExpanded: (id: string) => resolved[id] ?? false,
    toggle: (id: string) => {
      const next = !(resolved[id] ?? false);
      if (mode === "remember") {
        setSubgroupExpanded(id, next);
        return;
      }
      // auto: accordion — opening one domain closes the others.
      if (next) {
        const exclusive: Record<string, boolean> = {};
        for (const subgroupId of subgroupIds) {
          exclusive[subgroupId] = subgroupId === id;
        }
        setOverrides(exclusive);
        return;
      }
      setOverrides(() => {
        const closed: Record<string, boolean> = {};
        for (const subgroupId of subgroupIds) {
          closed[subgroupId] = false;
        }
        return closed;
      });
    },
  };
}

function NavSubgroupSection({
  subgroup,
  items,
  allHrefs,
  expanded,
  collapsible,
  containsActive,
  onToggle,
  onNavigate,
}: {
  subgroup: NavSubgroup;
  items: readonly NavItem[];
  allHrefs: readonly string[];
  expanded: boolean;
  collapsible: boolean;
  containsActive: boolean;
  onToggle: () => void;
  onNavigate?: () => void;
}) {
  const t = useTranslations("nav");
  const headingId = `nav-subgroup-${subgroup.id}`;
  const panelId = `nav-subgroup-panel-${subgroup.id}`;
  const label = t(subgroup.labelKey);
  const chrome = resolveDomainChrome(subgroup.id);

  return (
    <div
      className={cn("flex flex-col gap-0.5 py-1", chrome.panel)}
      data-domain-active={containsActive ? "true" : "false"}
    >
      {collapsible ? (
        <button
          type="button"
          id={headingId}
          aria-expanded={expanded}
          aria-controls={panelId}
          onClick={onToggle}
          className={cn(
            "ecmp-touch group flex w-full items-center gap-1.5 rounded-[var(--ecmp-radius-md)] px-3 py-1.5",
            SUBGROUP_HEADING_BASE_CLASS,
            chrome.label,
            "transition-colors duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
            "hover:bg-ecmp-hover/60",
            chrome.hoverLabel,
            "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus",
          )}
        >
          {/* Quiet disclosure: chevron reserved in layout, visible on hover/focus only. */}
          <IconChevronDown
            aria-hidden
            className={cn(
              "size-3 shrink-0 opacity-0",
              "transition-[opacity,transform] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)] motion-reduce:transition-none",
              "group-hover:opacity-70 group-focus-visible:opacity-70",
              expanded ? "rotate-0" : "-rotate-90 rtl:rotate-90",
            )}
          />
          <span className="min-w-0 truncate text-left !font-[600]">{label}</span>
        </button>
      ) : (
        <p
          id={headingId}
          className={cn(SUBGROUP_HEADING_BASE_CLASS, chrome.label)}
        >
          {label}
        </p>
      )}
      <div
        id={panelId}
        role="group"
        aria-labelledby={headingId}
        hidden={!expanded}
        className={cn(
          "flex flex-col gap-0.5 px-0.5 pb-0.5 pt-1",
          "mx-2 border-t",
          chrome.divider,
        )}
      >
        {items.map((item) => (
          <NavLink
            key={item.id}
            item={item}
            label={t(item.labelKey)}
            allHrefs={allHrefs}
            onNavigate={onNavigate}
          />
        ))}
      </div>
    </div>
  );
}

function NavGroupSection({
  group,
  itemsById,
  isItemVisible,
  allHrefs,
  onNavigate,
}: {
  group: NavGroup;
  itemsById: Record<string, NavItem>;
  isItemVisible: (item: NavItem) => boolean;
  allHrefs: readonly string[];
  onNavigate?: () => void;
}) {
  const t = useTranslations("nav");

  const resolveItems = (ids: readonly string[]) =>
    ids
      .map((id) => itemsById[id])
      .filter(Boolean)
      .filter((item) => isItemVisible(item));

  // Permission filter first — subgroups only ever narrow what is already visible.
  const visibleSubgroups = (group.subgroups ?? [])
    .map((subgroup) => ({ subgroup, items: resolveItems(subgroup.itemIds) }))
    .filter((entry) => entry.items.length > 0);

  const expansion = useSubgroupExpansion(
    visibleSubgroups.map((entry) => ({
      id: entry.subgroup.id,
      hrefs: entry.items.map((item) => item.href),
    })),
    allHrefs,
  );

  const items = resolveItems(group.itemIds);
  if (items.length === 0) return null;

  const headingId = `nav-group-${group.id}`;
  const heading = group.labelKey ? (
    <p id={headingId} className={GROUP_HEADING_CLASS}>
      {t(group.labelKey)}
    </p>
  ) : null;

  const body =
    visibleSubgroups.length > 0 ? (
      <div className="flex flex-col gap-2.5">
        {visibleSubgroups.map((entry, index) => (
          <div key={entry.subgroup.id} className="flex flex-col gap-2.5">
            <NavSubgroupSection
              subgroup={entry.subgroup}
              items={entry.items}
              allHrefs={allHrefs}
              expanded={expansion.isExpanded(entry.subgroup.id)}
              collapsible={expansion.collapsible}
              containsActive={expansion.activeSubgroupId === entry.subgroup.id}
              onToggle={() => expansion.toggle(entry.subgroup.id)}
              onNavigate={onNavigate}
            />
            {/* Domain separator — clarifies Wajib Pajak vs Internal without target/filter logic. */}
            {index < visibleSubgroups.length - 1 ? (
              <div
                role="separator"
                aria-hidden
                className="mx-3 border-t border-ecmp-border/80"
                data-testid="nav-domain-separator"
              />
            ) : null}
          </div>
        ))}
      </div>
    ) : (
      items.map((item) => (
        <NavLink
          key={item.id}
          item={item}
          label={t(item.labelKey)}
          allHrefs={allHrefs}
          onNavigate={onNavigate}
        />
      ))
    );

  return (
    <div
      role={heading ? "group" : undefined}
      aria-labelledby={heading ? headingId : undefined}
      className="flex flex-col gap-0.5"
    >
      {heading}
      {body}
    </div>
  );
}

function NavSections({
  groups,
  itemsById,
  isItemVisible,
  onNavigate,
}: {
  groups: typeof APP_NAV_GROUPS;
  itemsById: Record<string, NavItem>;
  isItemVisible: (item: NavItem) => boolean;
  onNavigate?: () => void;
}) {
  const tCommon = useTranslations("common");
  const unreadCount = useUnreadAnnouncementCount();
  const hqScheduleTodayCount = useHqScheduleTodayCount();
  const pendingTransferRequestCount = usePendingTransferRequestCount();
  const pendingWithdrawRequestCount = usePendingWithdrawRequestCount();
  let itemsWithBadges = itemsById;
  if (unreadCount > 0 && itemsWithBadges.announcements) {
    itemsWithBadges = {
      ...itemsWithBadges,
      announcements: { ...itemsWithBadges.announcements, badge: unreadCount },
    };
  }
  if (hqScheduleTodayCount > 0 && itemsWithBadges.hqSchedule) {
    itemsWithBadges = {
      ...itemsWithBadges,
      hqSchedule: { ...itemsWithBadges.hqSchedule, badge: hqScheduleTodayCount },
    };
  }
  if (pendingTransferRequestCount > 0 && itemsWithBadges.internalAssignments) {
    itemsWithBadges = {
      ...itemsWithBadges,
      internalAssignments: {
        ...itemsWithBadges.internalAssignments,
        badge: pendingTransferRequestCount,
      },
    };
  }
  if (pendingWithdrawRequestCount > 0 && itemsWithBadges.internalFollowUp) {
    itemsWithBadges = {
      ...itemsWithBadges,
      internalFollowUp: {
        ...itemsWithBadges.internalFollowUp,
        badge: pendingWithdrawRequestCount,
      },
    };
  }

  const visibleItems = groups
    .flatMap((group) => group.itemIds.map((id) => itemsById[id]))
    .filter(Boolean)
    .filter((item) => isItemVisible(item));
  const allHrefs = visibleItems.map((item) => item.href);

  return (
    <nav
      aria-label={tCommon("primaryNav")}
      className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-3 py-4"
    >
      {groups.map((group) => (
        <NavGroupSection
          key={group.id}
          group={group}
          itemsById={itemsWithBadges}
          isItemVisible={isItemVisible}
          allHrefs={allHrefs}
          onNavigate={onNavigate}
        />
      ))}
    </nav>
  );
}

export function Sidebar() {
  const { open, setOpen, isDesktop } = useSidebar();
  const closeDrawer = () => setOpen(false);
  const tCommon = useTranslations("common");
  const orgUnitBranch = useOrgUnitBranch();
  const { groups, itemsById, homeHref, isItemVisible } =
    useShellNav(orgUnitBranch);
  const brandUnitLabel = useBrandUnitLabel(orgUnitBranch);

  return (
    <>
      <aside
        className={cn(
          "hidden h-full w-[var(--ecmp-sidebar-width)] shrink-0 border-r border-ecmp-border/80 bg-ecmp-surface",
          // Height comes from AppLayout's h-dvh shell — only <main> scrolls.
          "lg:flex lg:flex-col lg:overflow-hidden",
        )}
        aria-label={tCommon("appSidebar")}
      >
        <div className="flex h-[var(--ecmp-header-height)] shrink-0 items-center px-5">
          <Brand asLink href={homeHref} branchName={brandUnitLabel} />
        </div>
        <NavSections
          groups={groups}
          itemsById={itemsById}
          isItemVisible={isItemVisible}
        />
      </aside>

      <div
        className={cn(
          "fixed inset-0 z-[var(--ecmp-z-sidebar)] lg:hidden",
          open ? "pointer-events-auto" : "pointer-events-none",
        )}
        aria-hidden={!open}
      >
        <button
          type="button"
          aria-label={tCommon("closeNav")}
          className={cn(
            "absolute inset-0 bg-ecmp-surface-overlay backdrop-blur-[2px]",
            "transition-opacity duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-standard)]",
            open ? "opacity-100" : "opacity-0",
          )}
          onClick={closeDrawer}
          tabIndex={open ? 0 : -1}
        />
        <aside
          id="mobile-sidebar"
          className={cn(
            "absolute inset-y-0 left-0 flex w-[min(100%,var(--ecmp-sidebar-width))] flex-col bg-ecmp-surface-floating shadow-ecmp-overlay",
            "transition-transform duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-enter)]",
            open ? "translate-x-0" : "-translate-x-full",
          )}
          aria-label={tCommon("mobileNav")}
        >
          <div className="flex h-[var(--ecmp-header-height)] shrink-0 items-center px-5">
            <Brand
              asLink
              href={homeHref}
              onNavigate={isDesktop ? undefined : closeDrawer}
              branchName={brandUnitLabel}
            />
          </div>
          <NavSections
            groups={groups}
            itemsById={itemsById}
            isItemVisible={isItemVisible}
            onNavigate={isDesktop ? undefined : closeDrawer}
          />
        </aside>
      </div>
    </>
  );
}
