"use client";

import { useTranslations } from "next-intl";
import type {
  DashboardHeader,
  DashboardSlaSummary,
  StatusCount,
} from "@/lib/api/types";
import { IconAlert, IconCheck, IconQueue } from "@/shared/icons";
import { Skeleton } from "@/shared/ui";
import {
  buildTodaysInsights,
  DASHBOARD_BODY,
  DASHBOARD_CARD_TITLE,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_FLAT,
  type InsightKind,
} from "./dashboardUtils";

const INSIGHT_ICON: Record<InsightKind, typeof IconCheck> = {
  slaBreached: IconAlert,
  escalationReview: IconAlert,
  backlog: IconQueue,
  normal: IconCheck,
};

const INSIGHT_SHELL: Record<InsightKind, string> = {
  slaBreached: "from-ecmp-danger-subtle/50 to-ecmp-surface",
  escalationReview: "from-ecmp-warning-subtle/50 to-ecmp-surface",
  backlog: "from-ecmp-primary-muted/40 to-ecmp-surface",
  normal: "from-ecmp-success-subtle/45 to-ecmp-surface",
};

const INSIGHT_ICON_TONE: Record<InsightKind, string> = {
  slaBreached: "bg-ecmp-danger-subtle text-ecmp-danger-text",
  escalationReview: "bg-ecmp-warning-subtle text-ecmp-warning-text",
  backlog: "bg-ecmp-surface-sunken text-ecmp-primary",
  normal: "bg-ecmp-success-subtle text-ecmp-success-text",
};

export function TodaysInsight({
  header,
  sla,
  byStatus,
  loading,
}: {
  header: DashboardHeader | null;
  sla: DashboardSlaSummary | null;
  byStatus: StatusCount[] | null;
  loading: boolean;
}) {
  const t = useTranslations("dashboard");
  const insights = buildTodaysInsights({ header, sla, byStatus });
  const primary = insights[0] ?? "normal";
  const Icon = INSIGHT_ICON[primary];

  return (
    <section
      data-testid="dashboard-todays-insight"
      className={`${DASHBOARD_SURFACE_FLAT} flex h-full min-h-[300px] flex-col overflow-hidden bg-gradient-to-br p-5 ${INSIGHT_SHELL[primary]}`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("todaysInsight")}</h2>
        <p className={`mt-1 ${DASHBOARD_CARD_TITLE}`}>
          {t("todaysInsightDescription")}
        </p>
      </div>

      {loading ? (
        <div className="mt-6" aria-busy="true">
          <Skeleton rows={3} />
        </div>
      ) : (
        <div className="mt-6 flex flex-1 flex-col justify-center gap-4">
          <span
            className={`flex size-12 items-center justify-center rounded-[var(--ecmp-radius-xl)] shadow-ecmp-raised ${INSIGHT_ICON_TONE[primary]}`}
          >
            <Icon className="size-5" aria-hidden />
          </span>
          <p className={`text-[18px] font-medium leading-snug text-ecmp-text-primary`}>
            {primary === "slaBreached"
              ? t("insightSlaBreached")
              : primary === "escalationReview"
                ? t("insightEscalationReview")
                : primary === "backlog"
                  ? t("insightBacklog")
                  : t("insightNormal")}
          </p>
          <p className={DASHBOARD_BODY}>{t("insightRuleBasedNote")}</p>
        </div>
      )}
    </section>
  );
}
