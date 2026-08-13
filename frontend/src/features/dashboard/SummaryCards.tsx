"use client";

import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { CM_BATCH1_OPEN_HREF } from "@/features/complaints/cmBatch1ListFilters";
import type {
  DashboardHeader,
  DashboardSlaSummary,
  DashboardTrendItem,
  StatusCount,
} from "@/lib/api/types";
import { IconEmpty } from "@/shared/icons";
import { Empty, Skeleton } from "@/shared/ui";
import { AnimatedCount } from "./AnimatedCount";
import {
  countByStatus,
  DASHBOARD_COMMAND_LABEL,
  DASHBOARD_CAPTION,
  DASHBOARD_METRIC,
  DASHBOARD_METRIC_HERO,
  DASHBOARD_TILE,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  openBacklogAccent,
  resolutionRatePct,
  type OpsTone,
} from "./dashboardUtils";
import { TrendSparkline } from "./TrendSparkline";

function KpiBlock({
  title,
  value,
  signal,
  tone,
  hero = false,
  trailing,
  className = "",
  onActivate,
}: {
  title: string;
  value: ReactNode;
  signal: string;
  tone: OpsTone;
  hero?: boolean;
  trailing?: ReactNode;
  className?: string;
  onActivate?: () => void;
}) {
  const body = (
    <>
      <p className={DASHBOARD_COMMAND_LABEL}>{title}</p>
      <div className="flex items-end justify-between gap-3">
        <p className={hero ? DASHBOARD_METRIC_HERO : DASHBOARD_METRIC}>{value}</p>
        {trailing}
      </div>
      {/* Neutral state is silent — color is reserved for what needs attention. */}
      {tone === "healthy" || tone === "neutral" ? (
        <p className={`mt-0.5 ${DASHBOARD_CAPTION} text-ecmp-text-secondary`}>
          {signal}
        </p>
      ) : (
        <p
          className={`mt-0.5 flex items-start gap-1.5 ${DASHBOARD_CAPTION} ${OPS_TONE_TEXT[tone]}`}
        >
          <span
            className={`mt-[0.35rem] size-1.5 shrink-0 rounded-full ${OPS_TONE_DOT[tone]}`}
            aria-hidden
          />
          <span className="min-w-0 leading-snug">{signal}</span>
        </p>
      )}
    </>
  );

  if (onActivate) {
    return (
      <button
        type="button"
        onClick={onActivate}
        className={`flex w-full flex-col gap-1 rounded-[var(--ecmp-radius-md)] px-1 py-1 text-left transition-colors duration-150 hover:bg-ecmp-hover/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus ${className}`}
      >
        {body}
      </button>
    );
  }

  return <article className={`flex w-full flex-col gap-1 px-1 py-1 ${className}`}>{body}</article>;
}

export function SummaryCards({
  header,
  sla,
  byStatus,
  trend,
  complaintKpiSource,
  loading,
}: {
  header: DashboardHeader | null;
  sla: DashboardSlaSummary | null;
  byStatus: StatusCount[] | null;
  trend?: DashboardTrendItem[] | null;
  complaintKpiSource?: "aggregate" | "foundation" | null;
  loading: boolean;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const { hasPermission } = useAuth();
  // Aggregate list (/complaints/cm) requires complaints:read. MANAGER KPI
  // cards use dashboard:read only — do not deep-link into a 403 list.
  const canOpenComplaintList =
    hasPermission("complaints:read") || hasPermission("*");

  if (loading) {
    return (
      <section
        data-testid="dashboard-header-cards"
        aria-label={t("priorityKpi")}
        className={`${DASHBOARD_TILE} flex h-full flex-col p-5`}
      >
        <Skeleton rows={2} className="mb-4" />
        <div className="grid grid-cols-4 gap-3 border-t border-ecmp-border/30 pt-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} aria-busy="true">
              <Skeleton rows={2} />
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (!header) {
    return (
      <div
        className={`${DASHBOARD_TILE} p-5`}
        data-testid="dashboard-header-cards"
      >
        <Empty
          icon={<IconEmpty className="size-8 text-ecmp-muted" aria-hidden />}
          title={t("noSummaryYet")}
          description={t("noSummaryDescription")}
          primaryAction={{
            label: tCommon("goToComplaints"),
            onClick: () => router.push("/complaints"),
          }}
        />
      </div>
    );
  }

  const waitingAssignment = countByStatus(byStatus, "NEW") ?? 0;
  const escalated = countByStatus(byStatus, "ESCALATED") ?? 0;
  const slaDeferred = complaintKpiSource === "aggregate";
  const breached = slaDeferred ? null : (sla?.overall.breached ?? 0);
  const slaSignal = slaDeferred
    ? t("slaDeferredBatch1")
    : (breached ?? 0) > 0
      ? t("kpiCritical")
      : t("kpiHealthy");
  const slaTone: OpsTone = slaDeferred
    ? "neutral"
    : (breached ?? 0) > 0
      ? "critical"
      : "healthy";
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
      className={`${DASHBOARD_TILE} flex h-full flex-col p-5`}
    >
      <h2 className="sr-only">{t("priorityKpi")}</h2>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-stretch">
        <div className="sm:w-[260px] sm:shrink-0">
          <KpiBlock
            title={t("openComplaints")}
            value={<AnimatedCount value={header.openComplaints} />}
            signal={t("kpiWaitingDetail", { count: waitingAssignment })}
            tone={openTone}
            hero
            // /queue reads /api/v1/complaints/search — foundation-only. When
            // the hero number is Aggregate-sourced (DEC-020), send people to
            // where those complaints actually live instead of an empty
            // foundation list — only if they hold complaints:read.
            onActivate={
              complaintKpiSource === "aggregate" && !canOpenComplaintList
                ? undefined
                : () =>
                    router.push(
                      complaintKpiSource === "aggregate"
                        ? CM_BATCH1_OPEN_HREF
                        : "/queue",
                    )
            }
            trailing={
              trend && trend.length > 1 ? (
                <TrendSparkline
                  items={trend}
                  label={t("trendOpen30d")}
                  hint={t("trendFoundationOnlyHint")}
                />
              ) : undefined
            }
          />
        </div>

        <div className="grid grid-cols-2 gap-x-3 gap-y-3 border-t border-ecmp-border/30 pt-4 sm:grid-cols-4 sm:border-l sm:border-t-0 sm:pl-6 sm:pt-0">
          <KpiBlock
            title={t("slaBreached")}
            value={
              breached === null ? (
                tCommon("emDash")
              ) : (
                <AnimatedCount value={breached} />
              )
            }
            signal={slaSignal}
            tone={slaTone}
          />
          <KpiBlock
            title={t("escalationsPending")}
            value={<AnimatedCount value={escalated} />}
            signal={
              escalated > 0 ? t("kpiEscalationStory") : t("kpiHealthy")
            }
            tone={escalated > 0 ? "attention" : "healthy"}
          />
          <KpiBlock
            title={t("closedComplaints")}
            value={<AnimatedCount value={header.closedComplaints} />}
            signal={t("kpiHealthy")}
            tone="healthy"
          />
          <KpiBlock
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
        </div>
      </div>
    </section>
  );
}
