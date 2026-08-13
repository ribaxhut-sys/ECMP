"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  CM_BATCH1_ESCALATION_PENDING_HREF,
  CM_BATCH1_WAITING_ASSIGNMENT_HREF,
} from "@/features/complaints/cmBatch1ListFilters";
import type { DashboardHeader, StatusCount } from "@/lib/api/types";
import { IconEmpty } from "@/shared/icons";
import { Empty, Skeleton } from "@/shared/ui";
import { AnimatedCount } from "./AnimatedCount";
import {
  buildQueueHealthRows,
  dashboardEmptyWorkCta,
  DASHBOARD_CAPTION,
  DASHBOARD_COMMAND_LABEL,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_TILE,
  OPS_TONE_BAR,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  proportionalPct,
  type OpsTone,
} from "./dashboardUtils";

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
  onActivate?: () => void;
}) {
  const pct = proportionalPct(count, max);

  const meter = (
    <>
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
        className={`w-12 shrink-0 text-right font-mono text-[16px] font-medium tabular-nums ${OPS_TONE_TEXT[tone]}`}
      >
        <AnimatedCount value={count} />
      </span>
    </>
  );

  if (!onActivate) {
    return (
      <li>
        <div className="flex w-full items-center gap-4 px-2 py-2.5">{meter}</div>
      </li>
    );
  }

  return (
    <li>
      <button
        type="button"
        onClick={onActivate}
        className={`${DASHBOARD_HOVER_ROW} group flex w-full items-center gap-4 rounded-[var(--ecmp-radius-md)] px-2 py-2.5 text-left`}
      >
        {meter}
      </button>
    </li>
  );
}

export function QueueHealth({
  header,
  byStatus,
  complaintKpiSource,
  loading,
}: {
  header: DashboardHeader | null;
  byStatus: StatusCount[] | null;
  complaintKpiSource?: "aggregate" | "foundation" | null;
  loading: boolean;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const { hasPermission } = useAuth();
  const canOpenComplaintList =
    hasPermission("complaints:read") || hasPermission("*");

  if (loading) {
    return (
      <section
        data-testid="dashboard-queue-health"
        aria-label={t("queueHealth")}
        className={`${DASHBOARD_TILE} flex h-full min-h-[320px] flex-col p-5`}
      >
        <h2 className={DASHBOARD_COMMAND_LABEL}>{t("queueHealth")}</h2>
        <div className="mt-5" aria-busy="true">
          <Skeleton rows={5} />
        </div>
      </section>
    );
  }

  // /assignments reads the foundation Complaint aggregate only — an
  // Aggregate-sourced (cm_batch1) count has nowhere to land there
  // (assignment workflow for Batch-1 intake is DEFERRED,
  // GOV-MODEA-NEXT-001 M4). Route to the Aggregate list only when the
  // principal can open it (complaints:read); MANAGER KPI is dashboard:read.
  const isAggregate = complaintKpiSource === "aggregate";
  const waitingAssignmentHref = isAggregate
    ? canOpenComplaintList
      ? CM_BATCH1_WAITING_ASSIGNMENT_HREF
      : null
    : "/assignments";
  const escalationHref = isAggregate
    ? canOpenComplaintList
      ? CM_BATCH1_ESCALATION_PENDING_HREF
      : null
    : "/resolutions";

  const rows = buildQueueHealthRows({
    byStatus,
    complaintKpiSource,
    waitingAssignmentHref,
    escalationHref,
  });

  const max = Math.max(...rows.map((row) => row.count), 1);
  const emptyPortfolio = !header || header.totalComplaints === 0;
  const emptyWorkCta = dashboardEmptyWorkCta(complaintKpiSource ?? null);

  return (
    <section
      data-testid="dashboard-queue-health"
      aria-label={t("queueHealth")}
      className={`${DASHBOARD_TILE} flex h-full min-h-[320px] flex-col p-5`}
    >
      <div>
        <h2 className={DASHBOARD_COMMAND_LABEL}>{t("queueHealth")}</h2>
        <p className={`mt-1 ${DASHBOARD_CAPTION}`}>
          {t("queueHealthOpsDescription")}
        </p>
      </div>

      {emptyPortfolio ? (
        <div className="mt-5 flex-1">
          <Empty
            className="py-8"
            icon={<IconEmpty className="size-8 text-ecmp-muted" aria-hidden />}
            title={t("noSummaryYet")}
            description={t("noSummaryDescription")}
            primaryAction={
              complaintKpiSource === "aggregate" && !canOpenComplaintList
                ? undefined
                : {
                    label: tCommon(emptyWorkCta.labelKey),
                    onClick: () => router.push(emptyWorkCta.href),
                  }
            }
          />
        </div>
      ) : (
        <ul className="mt-5 flex-1 space-y-1">
          {rows.map((row) => (
            <QueueBar
              key={row.id}
              label={t(row.labelKey)}
              count={row.count}
              max={max}
              tone={row.tone}
              onActivate={row.href ? () => router.push(row.href!) : undefined}
            />
          ))}
        </ul>
      )}
    </section>
  );
}
