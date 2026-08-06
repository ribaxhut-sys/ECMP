"use client";

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
  DASHBOARD_CAPTION,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_MAIN,
  OPS_TONE_BAR,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  proportionalPct,
  type OpsTone,
} from "./dashboardUtils";

type QueueRow = {
  id: string;
  label: string;
  count: number;
  tone: OpsTone;
  href: string;
};

function QueueBar({
  label,
  count,
  max,
  tone,
  onActivate,
}: {
  label: string;
  count: number;
  max: number;
  tone: OpsTone;
  onActivate: () => void;
}) {
  const pct = proportionalPct(count, max);

  return (
    <li>
      <button
        type="button"
        onClick={onActivate}
        className={`${DASHBOARD_HOVER_ROW} group flex w-full items-center gap-4 rounded-[var(--ecmp-radius-md)] px-2 py-2.5 text-left`}
      >
        <span className="flex w-40 shrink-0 items-center gap-2 sm:w-48">
          <span
            className={`size-1.5 shrink-0 rounded-full ${OPS_TONE_DOT[tone]}`}
            aria-hidden
          />
          <span className="truncate text-[13px] text-ecmp-text-primary">
            {label}
          </span>
        </span>
        <span
          className="h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-ecmp-secondary-muted/50"
          role="meter"
          aria-valuenow={count}
          aria-valuemin={0}
          aria-valuemax={max}
          aria-label={label}
        >
          <span
            className={`block h-full rounded-full motion-safe:transition-[width] motion-safe:duration-500 ${OPS_TONE_BAR[tone]}`}
            style={{ width: `${pct}%` }}
          />
        </span>
        <span
          className={`w-12 shrink-0 text-right text-[16px] font-medium tabular-nums ${OPS_TONE_TEXT[tone]}`}
        >
          <AnimatedCount value={count} />
        </span>
      </button>
    </li>
  );
}

export function QueueHealth({
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
        data-testid="dashboard-queue-health"
        aria-label={t("queueHealth")}
        className={`${DASHBOARD_SURFACE_MAIN} flex h-full min-h-[320px] flex-col p-5`}
      >
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("queueHealth")}</h2>
        <div className="mt-5" aria-busy="true">
          <Skeleton rows={5} />
        </div>
      </section>
    );
  }

  const waitingAssignment = countByStatus(byStatus, "NEW") ?? 0;
  const waitingReview = countByStatus(byStatus, "PENDING") ?? 0;
  const inProgress = countByStatus(byStatus, "IN_PROGRESS") ?? 0;
  const overSla = sla?.overall.breached ?? 0;
  const escalated = countByStatus(byStatus, "ESCALATED") ?? 0;

  const rows: QueueRow[] = [
    {
      id: "waiting-assignment",
      label: t("waitingAssignment"),
      count: waitingAssignment,
      tone: waitingAssignment > 0 ? "attention" : "healthy",
      href: "/assignments",
    },
    {
      id: "waiting-review",
      label: t("waitingReview"),
      count: waitingReview,
      tone: waitingReview > 0 ? "attention" : "healthy",
      href: "/queue",
    },
    {
      id: "in-progress",
      label: t("queueInProgress"),
      count: inProgress,
      tone: "neutral",
      href: "/queue",
    },
    {
      id: "over-sla",
      label: t("overSla"),
      count: overSla,
      tone: overSla > 0 ? "critical" : "healthy",
      href: "/queue",
    },
    {
      id: "escalated",
      label: t("escalationsPending"),
      count: escalated,
      tone: escalated > 0 ? "critical" : "healthy",
      href: "/resolutions",
    },
  ];

  const max = Math.max(...rows.map((row) => row.count), 1);
  const emptyPortfolio = !header || header.totalComplaints === 0;

  return (
    <section
      data-testid="dashboard-queue-health"
      aria-label={t("queueHealth")}
      className={`${DASHBOARD_SURFACE_MAIN} flex h-full min-h-[320px] flex-col p-5`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("queueHealth")}</h2>
        <p className={`mt-1 ${DASHBOARD_CAPTION}`}>
          {t("queueHealthOpsDescription")}
        </p>
      </div>

      {emptyPortfolio ? (
        <div className="mt-5 flex-1">
          <Empty
            title={t("noSummaryYet")}
            description={t("noSummaryDescription")}
            primaryAction={{
              label: t("refreshDashboard"),
              onClick: onRefresh,
            }}
            secondaryAction={{
              label: tCommon("goToQueue"),
              onClick: () => router.push("/queue"),
            }}
          />
        </div>
      ) : (
        <ul className="mt-5 flex-1 space-y-1">
          {rows.map((row) => (
            <QueueBar
              key={row.id}
              label={row.label}
              count={row.count}
              max={max}
              tone={row.tone}
              onActivate={() => router.push(row.href)}
            />
          ))}
        </ul>
      )}
    </section>
  );
}
