"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  IconComplaints,
  IconQueue,
  IconReports,
  IconUsers,
} from "@/shared/icons";
import { Empty, Skeleton } from "@/shared/ui";
import {
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_FLAT,
} from "./dashboardUtils";

type Shortcut = {
  id: string;
  href: string;
  permission: string;
  labelKey: "createComplaint" | "openQueue" | "viewReports" | "manageUsers";
  icon: typeof IconComplaints;
};

const SHORTCUTS: readonly Shortcut[] = [
  {
    id: "create",
    href: "/complaints/new",
    permission: "complaints:create",
    labelKey: "createComplaint",
    icon: IconComplaints,
  },
  {
    id: "queue",
    href: "/queue",
    permission: "complaints:read",
    labelKey: "openQueue",
    icon: IconQueue,
  },
  {
    id: "reports",
    href: "/reports",
    permission: "reports:read",
    labelKey: "viewReports",
    icon: IconReports,
  },
  {
    id: "users",
    href: "/users",
    permission: "users:read",
    labelKey: "manageUsers",
    icon: IconUsers,
  },
] as const;

export function QuickActions({ onRefresh }: { onRefresh: () => void }) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const { hasPermission } = useAuth();
  const actions = SHORTCUTS.filter(
    (action) => hasPermission(action.permission) || hasPermission("*"),
  );

  return (
    <section
      data-testid="dashboard-quick-actions"
      id="quick-actions"
      aria-label={t("quickActions")}
      className={`${DASHBOARD_SURFACE_FLAT} p-4`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("quickActions")}</h2>
        <p className={`mt-1 ${DASHBOARD_CAPTION}`}>{t("quickActionsHint")}</p>
      </div>

      {actions.length === 0 ? (
        <div className="mt-3">
          <Empty
            title={t("noActions")}
            description={t("noActionsDescription")}
            primaryAction={{
              label: t("refreshDashboard"),
              onClick: onRefresh,
            }}
          />
        </div>
      ) : (
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {actions.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.id}
                type="button"
                onClick={() => router.push(action.href)}
                className="group flex items-center gap-2.5 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/60 bg-ecmp-surface-sunken/30 px-3 py-2.5 text-left transition-[border-color,background-color] hover:border-ecmp-border hover:bg-ecmp-hover/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus"
              >
                <span className="flex size-7 shrink-0 items-center justify-center rounded-[var(--ecmp-radius-sm)] bg-ecmp-surface text-ecmp-text-secondary transition-colors group-hover:text-ecmp-primary">
                  <Icon className="size-4" aria-hidden />
                </span>
                <span className="truncate text-[12px] font-semibold text-ecmp-text-primary">
                  {t(action.labelKey)}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}

export function QuickActionsSkeleton() {
  return (
    <div className={`${DASHBOARD_SURFACE_FLAT} p-4`} aria-busy="true">
      <Skeleton rows={2} />
    </div>
  );
}
