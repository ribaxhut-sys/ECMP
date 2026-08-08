"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { DashboardSlaSummary, StatusCount } from "@/lib/api/types";
import { IconChevronRight, IconCheck } from "@/shared/icons";
import { Skeleton } from "@/shared/ui";
import {
  countByStatus,
  DASHBOARD_CAPTION,
  DASHBOARD_COMMAND_LABEL,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_TILE,
  OPS_TONE_RAIL,
  OPS_TONE_TEXT,
  type OpsTone,
} from "./dashboardUtils";

type AlertRow = {
  id: string;
  tone: OpsTone;
  title: string;
  href: string;
};

export function CriticalAlerts({
  sla,
  byStatus,
  complaintKpiSource,
  loading,
}: {
  sla: DashboardSlaSummary | null;
  byStatus?: StatusCount[] | null;
  complaintKpiSource?: "aggregate" | "foundation" | null;
  loading: boolean;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  // /resolutions reads the foundation Complaint aggregate only —
  // Aggregate-sourced (cm_batch1) counts have nowhere to land there (Batch-1
  // assignment workflow is DEFERRED, GOV-MODEA-NEXT-001 M4). SLA breach
  // alerts stay foundation-linked below since sla.* is always
  // foundation-sourced regardless of complaintKpiSource.
  const isAggregate = complaintKpiSource === "aggregate";
  const escalationHref = isAggregate ? "/complaints/cm/supervisor" : "/resolutions";

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

  const breached = sla?.overall.breached ?? 0;
  const assignmentBreached = sla?.assignment.breached ?? 0;
  const resolutionBreached = sla?.resolution.breached ?? 0;
  const escalated = countByStatus(byStatus, "ESCALATED") ?? 0;

  const alerts: AlertRow[] = [];

  if (breached > 0) {
    alerts.push({
      id: "sla-overall",
      tone: "critical",
      title: t("alertSlaTitle", { count: breached }),
      href: "/queue",
    });
  }
  if (assignmentBreached > 0) {
    alerts.push({
      id: "sla-assignment",
      tone: "critical",
      title: t("alertAssignmentSlaTitle", { count: assignmentBreached }),
      href: "/assignments",
    });
  }
  if (resolutionBreached > 0 && resolutionBreached !== breached) {
    alerts.push({
      id: "sla-resolution",
      tone: "attention",
      title: t("alertResolutionSlaTitle", { count: resolutionBreached }),
      href: "#sla-overview",
    });
  }
  if (escalated > 0) {
    alerts.push({
      id: "escalation",
      tone: "attention",
      title: t("alertEscalationTitle", { count: escalated }),
      href: escalationHref,
    });
  }
  // Waiting-for-assignment is routine intake state, not an anomaly — it's
  // already surfaced by the hero card's own signal text (SummaryCards) and
  // the queue breakdown below. Repeating it here as a "critical alert"
  // both duplicated that number and made this panel cry wolf.

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
        <ul className="mt-3 flex-1 space-y-1">
          {alerts.map((alert) => (
            <li key={alert.id}>
              <button
                type="button"
                onClick={() => activate(alert.href)}
                className={`${DASHBOARD_HOVER_ROW} flex w-full items-center gap-3 rounded-[var(--ecmp-radius-md)] px-2 py-2.5 text-left`}
              >
                <span
                  className={`h-8 w-0.5 shrink-0 rounded-full ${OPS_TONE_RAIL[alert.tone]}`}
                  aria-hidden
                />
                <span className="min-w-0 flex-1">
                  <span className="block text-[13px] font-medium text-ecmp-text-primary">
                    {alert.title}
                  </span>
                  <span className={`block ${DASHBOARD_CAPTION} ${OPS_TONE_TEXT[alert.tone]}`}>
                    {alert.tone === "critical" ? t("kpiCritical") : t("kpiAttention")}
                  </span>
                </span>
                <IconChevronRight
                  className="size-4 shrink-0 text-ecmp-text-secondary"
                  aria-hidden
                />
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
