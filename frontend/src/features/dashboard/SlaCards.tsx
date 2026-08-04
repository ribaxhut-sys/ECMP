"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { DashboardSlaSummary } from "@/lib/api/types";
import { Empty, Skeleton } from "@/shared/ui";
import {
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  slaCompletionRatio,
  slaHealthLevel,
  slaLevelToOpsTone,
} from "./dashboardUtils";

export function SlaCards({
  sla,
  loading,
  onRefresh,
}: {
  sla: DashboardSlaSummary | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");

  const stages = sla
    ? [
        { key: "assignment", label: t("stageAssignment"), ...sla.assignment },
        { key: "appointment", label: t("stageAppointment"), ...sla.appointment },
        { key: "resolution", label: t("stageResolution"), ...sla.resolution },
        { key: "escalation", label: t("stageEscalation"), ...sla.escalation },
        { key: "overall", label: t("stageOverall"), ...sla.overall },
      ]
    : [];

  return (
    <section
      data-testid="dashboard-sla-cards"
      id="sla-overview"
      aria-label={t("slaHealthSummary")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("slaHealthSummary")}</h2>
        <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>{t("slaStageHealthHint")}</p>
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={5} />
        </div>
      ) : !sla ? (
        <div className="mt-3 flex-1">
          <Empty
            title={t("noSlaData")}
            description={t("noSlaDataDescription")}
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
        <ul className="mt-3 space-y-1">
          {stages.map((stage) => {
            const level = slaHealthLevel(stage);
            const tone = slaLevelToOpsTone(level);
            const pct = Math.round(slaCompletionRatio(stage) * 100);
            const label =
              level === "warning"
                ? t("kpiAttention")
                : level === "critical"
                  ? t("kpiCritical")
                  : t("kpiHealthy");
            return (
              <li
                key={stage.key}
                className="flex items-center justify-between gap-2 px-1 py-1.5"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span
                    className={`size-1.5 shrink-0 rounded-full ${OPS_TONE_DOT[tone]}`}
                    aria-hidden
                  />
                  <span className="truncate text-[13px] text-ecmp-text-primary">
                    {stage.label}
                  </span>
                </span>
                <span className="flex shrink-0 items-center gap-2">
                  <span className="tabular-nums text-[12px] text-ecmp-text-secondary">
                    {pct}%
                  </span>
                  <span className={`text-[11px] ${OPS_TONE_TEXT[tone]}`}>
                    {label}
                  </span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
