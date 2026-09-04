"use client";

import { useTranslations } from "next-intl";
import type { DashboardResolutionSla } from "@/lib/api/types";
import { IconCheck, IconEmpty } from "@/shared/icons";
import { Empty, Skeleton } from "@/shared/ui";
import {
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  slaComplianceLevel,
  slaLevelToOpsTone,
} from "./dashboardUtils";

/**
 * DEC-031 resolution-SLA panel.
 *
 * Replaces the five-stage CAP-006 view this card used to render. Those stages
 * (assignment / appointment / resolution / escalation / overall) have no
 * clocks in Mode A and could only ever show zero, so the card was permanently
 * short-circuited to an "not activated yet" empty state. One target — 30
 * calendar days from registration to closure — is what the module actually
 * measures now.
 */
export function SlaCards({
  sla,
  loading,
}: {
  sla: DashboardResolutionSla | null;
  loading: boolean;
}) {
  const t = useTranslations("dashboard");

  const level = slaComplianceLevel(sla);
  const tone = slaLevelToOpsTone(level);

  // Live state first: what needs doing now, then how the settled ones went.
  const openRows = sla
    ? [
        { key: "overdue", label: t("slaCountOverdue"), value: sla.overdue, tone: "critical" as const },
        { key: "warning", label: t("slaCountWarning"), value: sla.warning, tone: "attention" as const },
        { key: "onTrack", label: t("slaCountOnTrack"), value: sla.onTrack, tone: "healthy" as const },
      ]
    : [];
  const settledRows = sla
    ? [
        { key: "met", label: t("slaCountMet"), value: sla.met, tone: "healthy" as const },
        { key: "missed", label: t("slaCountMissed"), value: sla.missed, tone: "critical" as const },
      ]
    : [];

  const nothingPressing =
    sla !== null && sla.overdue === 0 && sla.warning === 0;

  return (
    <section
      data-testid="dashboard-sla-cards"
      id="sla-overview"
      aria-label={t("slaResolutionSummary")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("slaResolutionSummary")}</h2>
        <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>
          {sla ? t("slaTargetTitle", { days: sla.targetDays }) : null}
        </p>
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={5} />
        </div>
      ) : !sla ? (
        <div className="mt-3 flex-1">
          <Empty
            className="py-8"
            icon={<IconEmpty className="size-8 text-ecmp-muted" aria-hidden />}
            title={t("slaDeferredTitle")}
            description={t("slaDeferredDescription")}
          />
        </div>
      ) : (
        <div className="mt-3 flex flex-1 flex-col gap-3">
          <div className="flex items-baseline gap-2">
            <span
              className={`size-1.5 shrink-0 rounded-full ${OPS_TONE_DOT[tone]}`}
              aria-hidden
            />
            <p className={`text-[13px] font-medium ${OPS_TONE_TEXT[tone]}`}>
              {sla.compliancePercentage === null
                ? t("slaComplianceNone")
                : t("slaCompliance", { pct: sla.compliancePercentage })}
            </p>
          </div>

          {nothingPressing ? (
            <div className="flex items-center gap-2.5">
              <IconCheck
                className="size-4 shrink-0 text-ecmp-success-text"
                aria-hidden
              />
              <p className="text-[13px] text-ecmp-text-primary">
                {t("slaAlertsEmptyDescription", { days: sla.targetDays })}
              </p>
            </div>
          ) : (
            <ul className="space-y-1">
              {openRows.map(({ key, ...row }) => (
                <SlaCountRow key={key} {...row} />
              ))}
            </ul>
          )}

          <ul className="space-y-1 border-t border-ecmp-border/40 pt-2">
            {settledRows.map(({ key, ...row }) => (
              <SlaCountRow key={key} {...row} />
            ))}
          </ul>

          {sla.unknown > 0 ? (
            <p className={DASHBOARD_CAPTION}>
              {t("slaUnknownHint", { count: sla.unknown })}
            </p>
          ) : null}

          <p className={`mt-auto ${DASHBOARD_CAPTION}`}>{t("slaResolutionHint")}</p>
        </div>
      )}
    </section>
  );
}

function SlaCountRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "healthy" | "attention" | "critical";
}) {
  // A zero count is dimmed rather than hidden: the set of rows must stay
  // stable so "0 lewat batas" is readable as good news, not as missing data.
  const muted = value === 0;
  return (
    <li className="flex items-center justify-between gap-2 px-1 py-1">
      <span className="flex min-w-0 items-center gap-2">
        <span
          className={`size-1.5 shrink-0 rounded-full ${
            muted ? "bg-ecmp-muted" : OPS_TONE_DOT[tone]
          }`}
          aria-hidden
        />
        <span
          className={`truncate text-[13px] ${
            muted ? "text-ecmp-text-secondary" : "text-ecmp-text-primary"
          }`}
        >
          {label}
        </span>
      </span>
      <span
        className={`shrink-0 tabular-nums text-[13px] ${
          muted ? "text-ecmp-text-secondary" : `font-medium ${OPS_TONE_TEXT[tone]}`
        }`}
      >
        {value}
      </span>
    </li>
  );
}
