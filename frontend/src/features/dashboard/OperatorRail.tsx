"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  IconAssignments,
  IconComplaints,
  IconQueue,
  IconReports,
} from "@/shared/icons";
import { Empty } from "@/shared/ui";
import {
  DASHBOARD_CAPTION,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
} from "./dashboardUtils";

type Shortcut = {
  id: string;
  href: string;
  permission: string;
  labelKey: "assignments" | "openQueue" | "viewReports" | "createComplaint";
  icon: typeof IconComplaints;
};

type TodayTask = {
  id: string;
  href: string;
  permission: string;
  titleKey:
    | "taskAssignComplaints"
    | "taskReviewEscalation"
    | "taskCloseResolved"
    | "taskVerifyAttachments";
};

const SHORTCUTS: readonly Shortcut[] = [
  {
    id: "assignments",
    href: "/assignments",
    permission: "complaints:assign",
    labelKey: "assignments",
    icon: IconAssignments,
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
    id: "create",
    href: "/complaints/new",
    permission: "complaints:create",
    labelKey: "createComplaint",
    icon: IconComplaints,
  },
] as const;

const TODAY_TASKS: readonly TodayTask[] = [
  {
    id: "assign",
    href: "/assignments",
    permission: "complaints:assign",
    titleKey: "taskAssignComplaints",
  },
  {
    id: "escalation",
    href: "/resolutions",
    permission: "complaints:read",
    titleKey: "taskReviewEscalation",
  },
  {
    id: "close",
    href: "/queue",
    permission: "complaints:read",
    titleKey: "taskCloseResolved",
  },
  {
    id: "attachments",
    href: "/complaints",
    permission: "complaints:read",
    titleKey: "taskVerifyAttachments",
  },
] as const;

/** Combined Today Tasks + Quick Actions — single operator surface. */
export function OperatorRail({ onRefresh }: { onRefresh?: () => void }) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const { hasPermission } = useAuth();
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const actions = SHORTCUTS.filter(
    (action) => hasPermission(action.permission) || hasPermission("*"),
  );
  const tasks = TODAY_TASKS.filter(
    (task) => hasPermission(task.permission) || hasPermission("*"),
  );

  const empty = actions.length === 0 && tasks.length === 0;

  return (
    <section
      data-testid="dashboard-operator-rail"
      id="quick-actions"
      aria-label={t("operatorRail")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("operatorRail")}</h2>
        <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>{t("operatorRailHint")}</p>
      </div>

      {empty ? (
        <div className="mt-3 flex-1">
          <Empty
            title={t("noActions")}
            description={t("noActionsDescription")}
            primaryAction={
              onRefresh
                ? {
                    label: t("refreshDashboard"),
                    onClick: onRefresh,
                  }
                : undefined
            }
          />
        </div>
      ) : (
        <div className="mt-3 flex flex-1 flex-col gap-3">
          {actions.length > 0 ? (
            <div className="grid grid-cols-2 gap-1">
              {actions.map((action) => {
                const Icon = action.icon;
                return (
                  <button
                    key={action.id}
                    type="button"
                    onClick={() => router.push(action.href)}
                    className={`${DASHBOARD_HOVER_ROW} flex items-center gap-2 rounded px-2 py-1.5 text-left`}
                  >
                    <Icon
                      className="size-3.5 shrink-0 text-ecmp-text-secondary"
                      aria-hidden
                    />
                    <span className="truncate text-[12px] text-ecmp-text-primary">
                      {t(action.labelKey)}
                    </span>
                  </button>
                );
              })}
            </div>
          ) : null}

          {tasks.length > 0 ? (
            <ul className="space-y-0.5 border-t border-ecmp-border/30 pt-2.5" role="list">
              {tasks.map((task) => {
                const isChecked = Boolean(checked[task.id]);
                return (
                  <li key={task.id}>
                    <div className="flex items-center gap-2 rounded px-1 py-1">
                      <input
                        id={`today-task-${task.id}`}
                        type="checkbox"
                        checked={isChecked}
                        onChange={() =>
                          setChecked((prev) => ({
                            ...prev,
                            [task.id]: !prev[task.id],
                          }))
                        }
                        className="size-3.5 shrink-0 rounded border-ecmp-border text-ecmp-primary focus:ring-ecmp-focus"
                        aria-label={t(task.titleKey)}
                      />
                      <button
                        type="button"
                        onClick={() => router.push(task.href)}
                        className={`min-w-0 flex-1 text-left text-[12px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus ${
                          isChecked
                            ? "text-ecmp-text-secondary line-through"
                            : "text-ecmp-text-primary"
                        }`}
                      >
                        {t(task.titleKey)}
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : null}
        </div>
      )}
    </section>
  );
}
