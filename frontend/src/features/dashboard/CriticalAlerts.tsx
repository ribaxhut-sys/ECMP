"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { DashboardSlaSummary, StatusCount } from "@/lib/api/types";
import { IconAlert, IconCheck } from "@/shared/icons";
import { Skeleton } from "@/shared/ui";
import {
  countByStatus,
  DASHBOARD_CAPTION,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  OPS_TONE_RAIL,
  OPS_TONE_TEXT,
  type OpsTone,
} from "./dashboardUtils";

type AlertRow = {
  id: string;
  tone: OpsTone;
  title: string;
  ctaLabel: string;
  href: string;
};

export function CriticalAlerts({
  sla,
  byStatus,
  loading,
}: {
  sla: DashboardSlaSummary | null;
  byStatus?: StatusCount[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");

  if (loading) {
    return (
      <section
        data-testid="dashboard-critical-alerts"
        aria-label={t("criticalAlerts")}
        className="py-1"
      >
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("criticalAlerts")}</h2>
        <div className="mt-2" aria-busy="true">
          <Skeleton rows={2} />
        </div>
      </section>
    );
  }

  const breached = sla?.overall.breached ?? 0;
  const assignmentBreached = sla?.assignment.breached ?? 0;
  const resolutionBreached = sla?.resolution.breached ?? 0;
  const escalated = countByStatus(byStatus, "ESCALATED") ?? 0;
  const waiting = countByStatus(byStatus, "NEW") ?? 0;

  const alerts: AlertRow[] = [];

  if (breached > 0) {
    alerts.push({
      id: "sla-overall",
      tone: "critical",
      title: t("alertSlaTitle", { count: breached }),
      ctaLabel: t("reviewQueue"),
      href: "/queue",
    });
  }
  if (assignmentBreached > 0) {
    alerts.push({
      id: "sla-assignment",
      tone: "critical",
      title: t("alertAssignmentSlaTitle", { count: assignmentBreached }),
      ctaLabel: t("assignComplaints"),
      href: "/assignments",
    });
  }
  if (resolutionBreached > 0 && resolutionBreached !== breached) {
    alerts.push({
      id: "sla-resolution",
      tone: "attention",
      title: t("alertResolutionSlaTitle", { count: resolutionBreached }),
      ctaLabel: t("viewSlaDetails"),
      href: "#sla-overview",
    });
  }
  if (escalated > 0) {
    alerts.push({
      id: "escalation",
      tone: "attention",
      title: t("alertEscalationTitle", { count: escalated }),
      ctaLabel: t("taskActionReview"),
      href: "/resolutions",
    });
  }
  if (waiting > 0 && breached === 0) {
    alerts.push({
      id: "waiting",
      tone: "attention",
      title: t("alertWaitingTitle", { count: waiting }),
      ctaLabel: t("assignComplaints"),
      href: "/assignments",
    });
  }

  return (
    <section
      data-testid="dashboard-critical-alerts"
      aria-label={t("criticalAlerts")}
      className="py-1"
    >
      <h2 className={DASHBOARD_SECTION_TITLE}>{t("criticalAlerts")}</h2>

      {alerts.length === 0 ? (
        <div
          className={`${DASHBOARD_SURFACE_QUIET} mt-2 flex items-center gap-3 px-3 py-2.5`}
        >
          <span className={`w-0.5 self-stretch rounded-full ${OPS_TONE_RAIL.healthy}`} aria-hidden />
          <IconCheck className="size-4 shrink-0 text-ecmp-success-text" aria-hidden />
          <p className="min-w-0 flex-1 text-[13px] text-ecmp-text-primary">
            {t("noOperationalAlertsToday")}
          </p>
          <button
            type="button"
            onClick={() => router.push("/queue")}
            className={`${DASHBOARD_HOVER_ROW} shrink-0 rounded px-2 py-1 text-[12px] font-medium text-ecmp-primary`}
          >
            {t("reviewQueue")}
          </button>
        </div>
      ) : (
        <ul className="mt-2 space-y-1">
          {alerts.map((alert) => (
            <li key={alert.id}>
              <div
                className={`${DASHBOARD_SURFACE_QUIET} flex items-center gap-3 px-3 py-2`}
              >
                <span
                  className={`w-0.5 self-stretch rounded-full ${OPS_TONE_RAIL[alert.tone]}`}
                  aria-hidden
                />
                <IconAlert
                  className={`size-4 shrink-0 ${OPS_TONE_TEXT[alert.tone]}`}
                  aria-hidden
                />
                <p className="min-w-0 flex-1 truncate text-[13px] text-ecmp-text-primary">
                  {alert.title}
                </p>
                <span className={`hidden text-[11px] sm:inline ${DASHBOARD_CAPTION} ${OPS_TONE_TEXT[alert.tone]}`}>
                  {alert.tone === "critical" ? t("kpiCritical") : t("kpiAttention")}
                </span>
                <button
                  type="button"
                  onClick={() => {
                    if (alert.href.startsWith("#")) {
                      document
                        .getElementById(alert.href.slice(1))
                        ?.scrollIntoView({ behavior: "smooth" });
                      return;
                    }
                    router.push(alert.href);
                  }}
                  className={`${DASHBOARD_HOVER_ROW} shrink-0 rounded px-2 py-1 text-[12px] font-medium text-ecmp-primary`}
                >
                  {alert.ctaLabel}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
