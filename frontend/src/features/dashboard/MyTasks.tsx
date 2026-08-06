"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { Empty } from "@/shared/ui";
import {
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE,
} from "./dashboardUtils";

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

export function MyTasks() {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const { hasPermission } = useAuth();
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const tasks = TODAY_TASKS.filter(
    (task) => hasPermission(task.permission) || hasPermission("*"),
  );

  return (
    <section
      data-testid="dashboard-my-tasks"
      aria-label={t("todayTasks")}
      className={`${DASHBOARD_SURFACE} flex h-full flex-col p-4`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("todayTasks")}</h2>
        <p className={`mt-1 ${DASHBOARD_CAPTION}`}>{t("todayTasksDescription")}</p>
      </div>

      {tasks.length === 0 ? (
        <div className="mt-3 flex-1">
          <Empty
            title={t("noActions")}
            description={t("noActionsDescription")}
          />
        </div>
      ) : (
        <ul className="mt-3 space-y-1" role="list">
          {tasks.map((task) => {
            const isChecked = Boolean(checked[task.id]);
            return (
              <li key={task.id}>
                <div className="flex items-center gap-2 rounded-[var(--ecmp-radius-md)] px-1 py-1.5 hover:bg-ecmp-hover/50">
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
                    className={`min-w-0 flex-1 text-left text-[13px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus ${
                      isChecked
                        ? "text-ecmp-text-secondary line-through"
                        : "font-medium text-ecmp-text-primary"
                    }`}
                  >
                    {t(task.titleKey)}
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
