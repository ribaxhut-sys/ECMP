"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { CM_BATCH1_ESCALATION_PENDING_HREF } from "@/features/complaints/cmBatch1ListFilters";
import type { StatusCount } from "@/lib/api/types";
import { IconChevronRight, IconCheck } from "@/shared/icons";
import { Skeleton } from "@/shared/ui";
import {
  buildCriticalAlerts,
  countByStatus,
  CRITICAL_ALERT_VISIBLE_LIMIT,
  DASHBOARD_CAPTION,
  DASHBOARD_COMMAND_LABEL,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_TILE,
  OPS_TONE_RAIL,
  OPS_TONE_TEXT,
  visibleAlertSlice,
} from "./dashboardUtils";

export function CriticalAlerts({
  byStatus,
  loading,
}: {
  byStatus?: StatusCount[] | null;
  loading: boolean;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const [expanded, setExpanded] = useState(false);
  const { hasPermission } = useAuth();
  const canOpenComplaintList =
    hasPermission("complaints:read") || hasPermission("*");
  const escalationHref = canOpenComplaintList
    ? CM_BATCH1_ESCALATION_PENDING_HREF
    : null;

  if (loading) {
    return (
      <section
        data-testid="dashboard-critical-alerts"
        aria-label={t("criticalAlerts")}
        className={`${DASHBOARD_TILE} flex h-full flex-col p-5`}
      >
        <h2 className="sr-only">{t("criticalAlerts")}</h2>
        <div aria-busy="true">
          <Skeleton rows={3} />
        </div>
      </section>
    );
  }

  const alerts = buildCriticalAlerts({
    breached: 0,
    assignmentBreached: 0,
    resolutionBreached: 0,
    escalated: countByStatus(byStatus, "escalatePending") ?? 0,
    escalationHref,
  });
  const visible = visibleAlertSlice(alerts, expanded);
  const overflow = alerts.length > CRITICAL_ALERT_VISIBLE_LIMIT;

  const activate = (href: string) => {
    if (href.startsWith("#")) {
      document.getElementById(href.slice(1))?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    router.push(href);
  };

  return (
    <section
      data-testid="dashboard-critical-alerts"
      aria-label={t("criticalAlerts")}
      className={`${DASHBOARD_TILE} flex h-full flex-col p-5`}
    >
      <h2 className="sr-only">{t("criticalAlerts")}</h2>
      <p className={DASHBOARD_COMMAND_LABEL}>{t("criticalAlerts")}</p>

      {alerts.length === 0 ? (
        <div className="mt-3 flex flex-1 items-center gap-2.5">
          <IconCheck className="size-4 shrink-0 text-ecmp-success-text" aria-hidden />
          <p className="text-[13px] text-ecmp-text-primary">
            {t("noOperationalAlertsToday")}
          </p>
        </div>
      ) : (
        <>
        <ul className="mt-3 max-h-[18rem] flex-1 space-y-1 overflow-y-auto">
          {visible.map((alert) => {
            const title = t(alert.titleKey, { count: alert.count });
            return (
              <li key={alert.id}>
                {alert.href ? (
                  <button
                    type="button"
                    onClick={() => activate(alert.href!)}
                    className={`${DASHBOARD_HOVER_ROW} flex w-full items-center gap-3 rounded-[var(--ecmp-radius-md)] px-2 py-2.5 text-left`}
                  >
                    <span
                      className={`h-8 w-0.5 shrink-0 rounded-full ${OPS_TONE_RAIL[alert.tone]}`}
                      aria-hidden
                    />
                    <span className="min-w-0 flex-1">
                      <span className="block text-[13px] font-medium text-ecmp-text-primary">
                        {title}
                      </span>
                      <span
                        className={`block ${DASHBOARD_CAPTION} ${OPS_TONE_TEXT[alert.tone]}`}
                      >
                        {alert.tone === "critical"
                          ? t("kpiCritical")
                          : t("kpiAttention")}
                      </span>
                    </span>
                    <IconChevronRight
                      className="size-4 shrink-0 text-ecmp-text-secondary"
                      aria-hidden
                    />
                  </button>
                ) : (
                  <div className="flex w-full items-center gap-3 rounded-[var(--ecmp-radius-md)] px-2 py-2.5">
                    <span
                      className={`h-8 w-0.5 shrink-0 rounded-full ${OPS_TONE_RAIL[alert.tone]}`}
                      aria-hidden
                    />
                    <span className="min-w-0 flex-1">
                      <span className="block text-[13px] font-medium text-ecmp-text-primary">
                        {title}
                      </span>
                      <span
                        className={`block ${DASHBOARD_CAPTION} ${OPS_TONE_TEXT[alert.tone]}`}
                      >
                        {alert.tone === "critical"
                          ? t("kpiCritical")
                          : t("kpiAttention")}
                      </span>
                    </span>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
        {overflow ? (
          <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            className={`${DASHBOARD_HOVER_ROW} mt-1 w-full rounded-[var(--ecmp-radius-md)] px-2 py-1.5 text-left text-[12px] font-medium text-ecmp-primary`}
          >
            {expanded
              ? t("criticalAlertsShowLess")
              : t("criticalAlertsShowAll", { count: alerts.length })}
          </button>
        ) : null}
        </>
      )}
    </section>
  );
}
