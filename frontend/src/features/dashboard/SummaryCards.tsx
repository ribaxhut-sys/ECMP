"use client";

import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type {
  DashboardHeader,
  DashboardSlaSummary,
  StatusCount,
} from "@/lib/api/types";
import { Empty, Skeleton } from "@/shared/ui";
import { AnimatedCount } from "./AnimatedCount";
import {
  countByStatus,
  DASHBOARD_CARD_TITLE,
  DASHBOARD_CAPTION,
  DASHBOARD_METRIC,
  DASHBOARD_METRIC_LG,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  openBacklogAccent,
  resolutionRatePct,
  type OpsTone,
} from "./dashboardUtils";

function KpiBlock({
  title,
  value,
  signal,
  tone,
  emphasize = false,
  className = "",
}: {
  title: string;
  value: ReactNode;
  signal: string;
  tone: OpsTone;
  emphasize?: boolean;
  className?: string;
}) {
  return (
    <article className={`flex flex-col gap-1 px-1 py-1 ${className}`}>
      <p className={DASHBOARD_CARD_TITLE}>{title}</p>
      <p className={emphasize ? DASHBOARD_METRIC_LG : DASHBOARD_METRIC}>{value}</p>
      <p
        className={`mt-0.5 inline-flex items-center gap-1.5 ${DASHBOARD_CAPTION} ${OPS_TONE_TEXT[tone]}`}
      >
        <span
          className={`size-1.5 shrink-0 rounded-full ${OPS_TONE_DOT[tone]}`}
          aria-hidden
        />
        <span className="line-clamp-1">{signal}</span>
      </p>
    </article>
  );
}

export function SummaryCards({
  header,
  sla,
  byStatus,
  loading,
  onRefresh,
}: {
  header: DashboardHeader | null;
  sla: DashboardSlaSummary | null;
  byStatus: StatusCount[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");

  if (loading) {
    return (
      <section
        data-testid="dashboard-header-cards"
        aria-label={t("priorityKpi")}
        className="grid grid-cols-12 gap-2"
      >
        {Array.from({ length: 5 }).map((_, index) => (
          <div
            key={index}
            className="col-span-6 py-1 xl:col-span-2"
            aria-busy="true"
          >
            <Skeleton rows={2} />
          </div>
        ))}
      </section>
    );
  }

  if (!header) {
    return (
      <div className="py-2" data-testid="dashboard-header-cards">
        <Empty
          title={t("noSummaryYet")}
          description={t("noSummaryDescription")}
          primaryAction={{
            label: t("refreshDashboard"),
            onClick: onRefresh,
          }}
          secondaryAction={{
            label: tCommon("goToComplaints"),
            onClick: () => router.push("/complaints"),
          }}
        />
      </div>
    );
  }

  const waitingAssignment = countByStatus(byStatus, "NEW") ?? 0;
  const escalated = countByStatus(byStatus, "ESCALATED") ?? 0;
  const breached = sla?.overall.breached ?? 0;
  const rate = resolutionRatePct(header);
  const openAccent = openBacklogAccent(
    header.openComplaints,
    header.totalComplaints,
  );

  const openTone: OpsTone =
    waitingAssignment > 0
      ? "attention"
      : openAccent === "attention"
        ? "attention"
        : openAccent === "healthy"
          ? "healthy"
          : "neutral";

  return (
    <section
      data-testid="dashboard-header-cards"
      aria-label={t("priorityKpi")}
      className="grid grid-cols-12 gap-x-3 gap-y-2 border-b border-ecmp-border/30 pb-2.5"
    >
      <KpiBlock
        className="col-span-12 sm:col-span-6 xl:col-span-4"
        title={t("openComplaints")}
        value={<AnimatedCount value={header.openComplaints} />}
        signal={t("kpiWaitingDetail", { count: waitingAssignment })}
        tone={openTone}
        emphasize
      />
      <KpiBlock
        className="col-span-6 sm:col-span-3 xl:col-span-2"
        title={t("slaBreached")}
        value={<AnimatedCount value={breached} />}
        signal={breached > 0 ? t("kpiCritical") : t("kpiHealthy")}
        tone={breached > 0 ? "critical" : "healthy"}
      />
      <KpiBlock
        className="col-span-6 sm:col-span-3 xl:col-span-2"
        title={t("escalationsPending")}
        value={<AnimatedCount value={escalated} />}
        signal={
          escalated > 0 ? t("kpiEscalationStory") : t("kpiHealthy")
        }
        tone={escalated > 0 ? "attention" : "healthy"}
      />
      <KpiBlock
        className="col-span-6 sm:col-span-3 xl:col-span-2"
        title={t("closedComplaints")}
        value={<AnimatedCount value={header.closedComplaints} />}
        signal={t("kpiHealthy")}
        tone="healthy"
      />
      <KpiBlock
        className="col-span-6 sm:col-span-3 xl:col-span-2"
        title={t("resolutionRate")}
        value={
          rate === null ? (
            "—"
          ) : (
            <>
              <AnimatedCount value={rate} />
              <span className="text-[16px]">%</span>
            </>
          )
        }
        signal={
          rate === null
            ? "—"
            : rate >= 80
              ? t("kpiGood")
              : rate >= 60
                ? t("kpiAttention")
                : t("kpiCritical")
        }
        tone={
          rate === null
            ? "neutral"
            : rate >= 80
              ? "healthy"
              : rate >= 60
                ? "attention"
                : "critical"
        }
      />
    </section>
  );
}
