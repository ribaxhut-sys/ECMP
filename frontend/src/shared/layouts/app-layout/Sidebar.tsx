"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  IconAssignments,
  IconComplaints,
  IconDashboard,
  IconPaperclip,
  IconQueue,
  IconReports,
  IconSettings,
  IconUsers,
} from "@/shared/icons";
import { useSidebar } from "@/shared/hooks";
import { cn } from "@/shared/utils";
import { APP_NAV_ITEMS, type NavItem } from "./nav";

const iconMap = {
  dashboard: IconDashboard,
  complaints: IconComplaints,
  queue: IconQueue,
  assignments: IconAssignments,
  reports: IconReports,
  users: IconUsers,
  settings: IconSettings,
  attachments: IconPaperclip,
} as const;

function NavLink({
  item,
  onNavigate,
}: {
  item: NavItem;
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
        "ecmp-touch flex items-center gap-3 rounded-[var(--ecmp-radius-md)] px-3 text-[length:var(--ecmp-font-body-size)] font-medium transition-colors",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus",
        active
          ? "bg-ecmp-primary-muted text-ecmp-primary"
          : "text-ecmp-text-secondary hover:bg-ecmp-secondary-muted hover:text-ecmp-text-primary",
      )}
    >
      <Icon className="size-5" />
      <span>{item.label}</span>
    </Link>
  );
}

export function Sidebar() {
  const { open, setOpen, isDesktop } = useSidebar();
  const closeDrawer = () => setOpen(false);

  const nav = (
    <nav aria-label="Primary" className="flex flex-1 flex-col gap-1 p-3">
      {APP_NAV_ITEMS.map((item) => (
        <NavLink
          key={item.id}
          item={item}
          onNavigate={isDesktop ? undefined : closeDrawer}
        />
      ))}
    </nav>
  );

  return (
    <>
      {/* Desktop persistent sidebar */}
      <aside
        className="hidden w-[var(--ecmp-sidebar-width)] shrink-0 border-r border-ecmp-border bg-ecmp-surface lg:flex lg:flex-col"
        aria-label="Application sidebar"
      >
        <div className="flex h-[var(--ecmp-header-height)] items-center border-b border-ecmp-border px-4">
          <Link
            href="/dashboard"
            className="text-[length:var(--ecmp-font-title-size)] font-bold tracking-tight text-ecmp-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
          >
            ECMP
          </Link>
        </div>
        {nav}
      </aside>

      {/* Mobile / tablet drawer */}
      <div
        className={cn(
          "fixed inset-0 z-40 lg:hidden",
          open ? "pointer-events-auto" : "pointer-events-none",
        )}
        aria-hidden={!open}
      >
        <button
          type="button"
          aria-label="Close navigation"
          className={cn(
            "absolute inset-0 bg-ecmp-overlay transition-opacity",
            open ? "opacity-100" : "opacity-0",
          )}
          onClick={closeDrawer}
          tabIndex={open ? 0 : -1}
        />
        <aside
          id="mobile-sidebar"
          className={cn(
            "absolute inset-y-0 left-0 flex w-[min(100%,var(--ecmp-sidebar-width))] flex-col bg-ecmp-surface shadow-ecmp-lg transition-transform duration-200",
            open ? "translate-x-0" : "-translate-x-full",
          )}
          aria-label="Mobile navigation"
        >
          <div className="flex h-[var(--ecmp-header-height)] items-center border-b border-ecmp-border px-4">
            <span className="text-[length:var(--ecmp-font-title-size)] font-bold text-ecmp-primary">
              ECMP
            </span>
          </div>
          {nav}
        </aside>
      </div>
    </>
  );
}
