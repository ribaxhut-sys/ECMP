"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type {
  DashboardHeader,
  DashboardSlaSummary,
  StatusCount,
} from "@/lib/api/types";
import { Skeleton } from "@/shared/ui";
import {
  countByStatus,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_STRIP,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  type OpsTone,
} from "./dashboardUtils";

type Chip = {
  id: string;
  label: string;
  tone: OpsTone;
};

export function OperationBriefing({
  header,
  sla,
  byStatus,
  loading,
  refreshing = false,
  onRefresh,
}: {
  header: DashboardHeader | null;
  sla: DashboardSlaSummary | null;
  byStatus: StatusCount[] | null;
  loading: boolean;
  refreshing?: boolean;
  onRefresh: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");

  const breached = sla?.overall.breached ?? 0;
  const waitingAssignment = countByStatus(byStatus, "NEW") ?? 0;
  const escalated = countByStatus(byStatus, "ESCALATED") ?? 0;
  void header;

  const chips: Chip[] = [];
  if (breached > 0) {
    chips.push({
      id: "critical",
      label: t("briefingChipCritical", { count: breached }),
      tone: "critical",
    });
  }
  if (waitingAssignment > 0) {
    chips.push({
      id: "waiting",
      label: t("briefingChipWaiting", { count: waitingAssignment }),
      tone: "attention",
    });
  }
  if (escalated > 0) {
    chips.push({
      id: "escalations",
      label: t("briefingChipEscalations", { count: escalated }),
      tone: "attention",
    });
  }

  const directive =
    chips.length > 0 ? t("briefingDirectiveShort") : t("heroAllClear");

  return (
    <section
      data-testid="dashboard-operation-briefing"
      aria-label={t("operationalBriefing")}
      className={`${DASHBOARD_STRIP} py-2.5`}
    >
      {loading ? (
        <div aria-busy="true">
          <Skeleton rows={1} />
        </div>
      ) : (
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1.5">
            <span className="text-[12px] font-medium text-ecmp-text-secondary">
              {t("operationalBriefing")}
            </span>
            {chips.length === 0 ? (
              <span className="inline-flex items-center gap-1.5 text-[13px] text-ecmp-text-primary">
                <span
                  className={`size-1.5 rounded-full ${OPS_TONE_DOT.healthy}`}
                  aria-hidden
                />
                {directive}
              </span>
            ) : (
              <>
                {chips.map((chip) => (
                  <span
                    key={chip.id}
                    className={`inline-flex items-center gap-1.5 text-[13px] tabular-nums ${OPS_TONE_TEXT[chip.tone]}`}
                  >
                    <span
                      className={`size-1.5 rounded-full ${OPS_TONE_DOT[chip.tone]}`}
                      aria-hidden
                    />
                    {chip.label}
                  </span>
                ))}
                <span className="text-[13px] font-medium text-ecmp-text-primary">
                  {directive}
                </span>
              </>
            )}
          </div>

          <div className="flex shrink-0 flex-wrap items-center gap-1">
            <button
              type="button"
              onClick={() => router.push("/queue")}
              className={`${DASHBOARD_HOVER_ROW} rounded px-2 py-1 text-[12px] font-medium text-ecmp-primary`}
            >
              {t("reviewQueue")}
            </button>
            <button
              type="button"
              onClick={() => router.push("/assignments")}
              className={`${DASHBOARD_HOVER_ROW} rounded px-2 py-1 text-[12px] font-medium text-ecmp-text-secondary`}
            >
              {t("assignComplaints")}
            </button>
            <button
              type="button"
              onClick={() => router.push("/reports")}
              className={`${DASHBOARD_HOVER_ROW} rounded px-2 py-1 text-[12px] font-medium text-ecmp-text-secondary`}
            >
              {t("viewReports")}
            </button>
            <button
              type="button"
              onClick={onRefresh}
              disabled={loading || refreshing}
              className={`${DASHBOARD_HOVER_ROW} rounded px-2 py-1 text-[12px] text-ecmp-text-secondary disabled:opacity-50`}
              aria-label={t("refreshDashboard")}
            >
              {refreshing ? "…" : t("refreshDashboard")}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
