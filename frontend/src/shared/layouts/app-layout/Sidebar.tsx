"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
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

const itemsById = Object.fromEntries(
  APP_NAV_ITEMS.map((item) => [item.id, item]),
) as Record<string, NavItem>;

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
  onNavigate,
}: {
  asLink: boolean;
  onNavigate?: () => void;
}) {
  const tCommon = useTranslations("common");
  const className =
    "text-[length:var(--ecmp-font-card-title-size)] font-semibold tracking-tight text-ecmp-text-primary";

  if (asLink) {
    return (
      <Link href="/dashboard" onClick={onNavigate} className={className}>
        {tCommon("appName")}
      </Link>
    );
  }

  return <span className={className}>{tCommon("appName")}</span>;
}

function NavSections({ onNavigate }: { onNavigate?: () => void }) {
  const t = useTranslations("nav");
  const tCommon = useTranslations("common");
  const { hasPermission } = useAuth();

  return (
    <nav
      aria-label={tCommon("primaryNav")}
      className="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-4"
    >
      {APP_NAV_GROUPS.map((group) => {
        const items = group.itemIds
          .map((id) => itemsById[id])
          .filter(Boolean)
          .filter((item) => isNavItemVisible(item, hasPermission));
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

  return (
    <>
      {/* Desktop persistent sidebar */}
      <aside
        className="hidden w-[var(--ecmp-sidebar-width)] shrink-0 border-r border-ecmp-border/80 bg-ecmp-surface lg:flex lg:flex-col"
        aria-label={tCommon("appSidebar")}
      >
        <div className="flex h-[var(--ecmp-header-height)] shrink-0 items-center px-5">
          <Brand asLink />
        </div>
        <NavSections />
      </aside>

      {/* Mobile / tablet drawer */}
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
            <Brand asLink onNavigate={isDesktop ? undefined : closeDrawer} />
          </div>
          <NavSections onNavigate={isDesktop ? undefined : closeDrawer} />
        </aside>
      </div>
    </>
  );
}
