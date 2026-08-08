"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { fetchBranches } from "@/lib/api/branches";
import { isShellUiBatch } from "@/shared/config/uiBatch";
import {
  IconAssignments,
  IconComplaints,
  IconDashboard,
  IconPaperclip,
  IconQueue,
  IconReports,
  IconResolutions,
  IconSettings,
  IconUsers,
} from "@/shared/icons";
import { useSidebar } from "@/shared/hooks";
import { cn } from "@/shared/utils";
import {
  APP_NAV_GROUPS,
  APP_NAV_ITEMS,
  isNavItemVisible,
  type NavItem,
} from "./nav";
import { B0_NAV_GROUPS, B0_NAV_ITEMS } from "./b0Nav";

/**
 * Resolve the logged-in user's branch name for the sidebar subtitle.
 * No GET /branches/{id} in the catalog — list once (same pattern as
 * AssignmentListView / ResolutionListView) and match branchId client-side.
 * null branchId is a valid state (head-office roles, EBS-001) — no fetch.
 */
function useLoggedInBranchName(): string | null {
  const { user, hasPermission } = useAuth();
  const branchId = user?.branchId ?? null;
  const canReadBranches = hasPermission("complaints:read");
  const [branchName, setBranchName] = useState<string | null>(null);

  useEffect(() => {
    if (!branchId || !canReadBranches) {
      setBranchName(null);
      return;
    }
    let cancelled = false;
    fetchBranches()
      .then((res) => {
        if (cancelled) return;
        const match = res.data.find((branch) => branch.id === branchId);
        setBranchName(match?.name ?? null);
      })
      .catch(() => {
        if (!cancelled) setBranchName(null);
      });
    return () => {
      cancelled = true;
    };
  }, [branchId, canReadBranches]);

  return branchName;
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
  attachments: IconPaperclip,
} as const;

function NavBadge({ value }: { value: number | string }) {
  const label = typeof value === "number" && value > 99 ? "99+" : String(value);
  return (
    <span
      className={cn(
        "ml-auto inline-flex min-w-5 shrink-0 items-center justify-center rounded-full px-1.5",
        "bg-ecmp-primary-muted text-[length:var(--ecmp-font-overline-size)] font-semibold leading-5 text-ecmp-primary",
      )}
    >
      {label}
    </span>
  );
}

function NavLink({
  item,
  label,
  onNavigate,
}: {
  item: NavItem;
  label: string;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const active =
    pathname === item.href || pathname.startsWith(`${item.href}/`);
  const Icon = iconMap[item.icon];

  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      className={cn(
        "ecmp-touch group relative flex items-center gap-3 rounded-[var(--ecmp-radius-md)] px-3",
        "text-[length:var(--ecmp-font-body-small-size)] font-normal tracking-[-0.01em]",
        "transition-[background-color,color,transform] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
        active
          ? "bg-ecmp-selected/70 font-medium text-ecmp-text-primary"
          : "text-ecmp-text-secondary hover:bg-ecmp-hover hover:text-ecmp-text-primary",
      )}
    >
      <span
        aria-hidden
        className={cn(
          "absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-full bg-ecmp-primary",
          "transition-opacity duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
          active ? "opacity-100" : "opacity-0 group-hover:opacity-35",
        )}
      />
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
        <NavBadge value={item.badge} />
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
    <span className="flex flex-col gap-0.5 leading-tight">
      <span className="text-[length:var(--ecmp-font-card-title-size)] font-semibold tracking-tight text-ecmp-text-primary">
        {tCommon("appName")}
      </span>
      {branchName ? (
        <span className="truncate text-[14px] font-medium text-ecmp-primary">
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

function useShellNav(): {
  groups: typeof APP_NAV_GROUPS;
  itemsById: Record<string, NavItem>;
  homeHref: string;
  isItemVisible: (item: NavItem) => boolean;
} {
  const {
    hasPermission,
    isMockSession,
    mockPersona,
    officerWorkMode,
  } = useAuth();
  const batchB0 = isShellUiBatch() || isMockSession;

  if (!batchB0) {
    const itemsById = Object.fromEntries(
      APP_NAV_ITEMS.map((item) => [item.id, item]),
    ) as Record<string, NavItem>;
    return {
      groups: APP_NAV_GROUPS,
      itemsById,
      homeHref: "/dashboard",
      isItemVisible: (item) => isNavItemVisible(item, hasPermission),
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

function NavSections({ onNavigate }: { onNavigate?: () => void }) {
  const t = useTranslations("nav");
  const tCommon = useTranslations("common");
  const { groups, itemsById, isItemVisible } = useShellNav();

  return (
    <nav
      aria-label={tCommon("primaryNav")}
      className="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-4"
    >
      {groups.map((group) => {
        const items = group.itemIds
          .map((id) => itemsById[id])
          .filter(Boolean)
          .filter((item) => isItemVisible(item));
        if (items.length === 0) return null;
        const headingId = `nav-group-${group.id}`;
        return (
          <div
            key={group.id}
            role="group"
            aria-labelledby={headingId}
            className="flex flex-col gap-0.5"
          >
            <p
              id={headingId}
              className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-[0.08em] text-ecmp-muted"
            >
              {t(group.labelKey)}
            </p>
            {items.map((item) => (
              <NavLink
                key={item.id}
                item={item}
                label={t(item.labelKey)}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        );
      })}
    </nav>
  );
}

export function Sidebar() {
  const { open, setOpen, isDesktop } = useSidebar();
  const closeDrawer = () => setOpen(false);
  const tCommon = useTranslations("common");
  const { homeHref } = useShellNav();
  const branchName = useLoggedInBranchName();

  return (
    <>
      <aside
        className="hidden w-[var(--ecmp-sidebar-width)] shrink-0 border-r border-ecmp-border/80 bg-ecmp-surface lg:flex lg:flex-col"
        aria-label={tCommon("appSidebar")}
      >
        <div className="flex h-[var(--ecmp-header-height)] shrink-0 items-center px-5">
          <Brand asLink href={homeHref} branchName={branchName} />
        </div>
        <NavSections />
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
              branchName={branchName}
            />
          </div>
          <NavSections onNavigate={isDesktop ? undefined : closeDrawer} />
        </aside>
      </div>
    </>
  );
}
