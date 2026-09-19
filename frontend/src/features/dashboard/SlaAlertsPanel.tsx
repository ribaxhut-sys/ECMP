"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { fetchDashboardSlaAlerts } from "@/lib/api";
import type { ComplaintSlaAlerts } from "@/lib/api/types";
import { Badge } from "@/shared/ui";
import { DASHBOARD_CAPTION } from "./dashboardUtils";

const ALERT_LIMIT = 8;

/**
 * DEC-031 in-app SLA alerts — the substitute for the proactive notification
 * CAP-005/CAP-006 would send.
 *
 * Renders nothing when nothing is pressing. An alert band that is always on
 * screen stops being an alert; this one appears only when a complaint is
 * approaching or past the 30-day target, so its presence is itself the signal.
 *
 * Honest limit, stated in the panel: this reaches an officer when they open
 * the app, not at the instant a threshold is crossed. Closing that gap needs
 * a scheduler and a transport, both still frozen (DEC-031 §3 Fase 2).
 */
export function SlaAlertsPanel({ reloadKey }: { reloadKey?: number }) {
  const t = useTranslations("dashboard");
  const [alerts, setAlerts] = useState<ComplaintSlaAlerts | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await fetchDashboardSlaAlerts({ limit: ALERT_LIMIT });
      setAlerts(res.data);
    } catch {
      // Silent: the SLA band is an aid, not the reason the page exists. A
      // failure here must not push an error state over the whole dashboard.
      setAlerts(null);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, reloadKey]);

  const total = (alerts?.overdueCount ?? 0) + (alerts?.warningCount ?? 0);
  if (!alerts || total === 0) return null;

  return (
    <section
      data-testid="dashboard-sla-alerts"
      aria-label={t("slaAlertsTitle")}
      className="rounded-[var(--ecmp-radius-lg)] border border-ecmp-warning-border bg-ecmp-warning-subtle p-3.5"
    >
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <h2 className="text-[13px] font-semibold text-ecmp-text-primary">
          {t("slaAlertsTitle")}
        </h2>
        {alerts.overdueCount > 0 ? (
          <Badge tone="danger" variant="solid">
            {t("slaAlertsOverdueCount", { count: alerts.overdueCount })}
          </Badge>
        ) : null}
        {alerts.warningCount > 0 ? (
          <Badge tone="warning">
            {t("slaAlertsWarningCount", { count: alerts.warningCount })}
          </Badge>
        ) : null}
        <span className={`ml-auto ${DASHBOARD_CAPTION}`}>
          {t("slaTargetTitle", { days: alerts.targetDays })}
        </span>
      </div>

      <ul className="mt-2.5 space-y-1">
        {alerts.items.map((item) => (
          <li
            key={item.complaintId}
            className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5"
          >
            <Link
              href={`/complaints?keyword=${encodeURIComponent(item.complaintNumber)}`}
              className="shrink-0 font-mono text-[12px] text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
            >
              {item.complaintNumber}
            </Link>
            <span
              className={`shrink-0 text-[12px] font-medium ${
                item.isOverdue ? "text-ecmp-danger-text" : "text-ecmp-warning-text"
              }`}
            >
              {item.isOverdue
                ? t("slaAlertsOverdueDays", { days: item.overdueDays ?? 0 })
                : t("slaAlertsRemainingDays", { days: item.remainingDays ?? 0 })}
            </span>
            {item.subject ? (
              <span className="min-w-0 truncate text-[12px] text-ecmp-text-secondary">
                {item.subject}
              </span>
            ) : null}
          </li>
        ))}
      </ul>

      {total > alerts.items.length ? (
        <p className={`mt-1.5 ${DASHBOARD_CAPTION}`}>
          {t("slaAlertsMore", { count: total - alerts.items.length })}
        </p>
      ) : null}

      <p className={`mt-2 ${DASHBOARD_CAPTION}`}>{t("slaAlertsInAppNote")}</p>
    </section>
  );
}
