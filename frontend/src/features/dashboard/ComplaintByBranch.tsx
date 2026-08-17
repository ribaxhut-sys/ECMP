"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import {
  BRANCH_HEALTH_BAR_COLOR_CLASS,
  BRANCH_HEALTH_BAR_LABEL_KEY,
} from "./branchHealthPalette";
import {
  BRANCH_HEALTH_BAR_KEYS,
  branchHealthMonthOptions,
  branchHealthScale,
  branchHealthShortLabel,
  branchHealthYearOptions,
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  proportionalPct,
  sortBranchesByHealth,
} from "./dashboardUtils";
import { useBranchHealthData } from "./useBranchHealthData";
import { IconEmpty } from "@/shared/icons";
import { Empty, ErrorState, Select, Skeleton } from "@/shared/ui";
import { cn } from "@/shared/utils";

export function ComplaintByBranch() {
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const { month, setMonth, year, setYear, state, retry } =
    useBranchHealthData();

  const monthOptions = useMemo(
    () => branchHealthMonthOptions(locale),
    [locale],
  );
  const yearOptions = useMemo(
    () => branchHealthYearOptions(new Date().getFullYear()),
    [],
  );

  const rows = state.status === "success" ? state.data : null;
  const loading = state.status === "loading";

  const ranked = useMemo(() => {
    if (!rows || rows.length === 0) return [];
    return sortBranchesByHealth(rows);
  }, [rows]);

  const scale = useMemo(() => branchHealthScale(ranked), [ranked]);

  return (
    <section
      data-testid="dashboard-branch-performance"
      id="branch-health"
      aria-label={t("branchHealth")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className={DASHBOARD_SECTION_TITLE}>{t("branchHealth")}</h2>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <div className="w-[8rem]">
            <Select
              name="branchHealthMonth"
              aria-label={t("branchHealthFilterMonth")}
              value={String(month)}
              onChange={(e) => setMonth(Number(e.target.value))}
              options={monthOptions.map((o) => ({
                value: String(o.value),
                label: o.label,
              }))}
            />
          </div>
          <div className="w-[6rem]">
            <Select
              name="branchHealthYear"
              aria-label={t("branchHealthFilterYear")}
              value={String(year)}
              onChange={(e) => setYear(Number(e.target.value))}
              options={yearOptions.map((y) => ({
                value: String(y),
                label: String(y),
              }))}
            />
          </div>
        </div>
      </div>

      {ranked.length > 0 ? (
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 px-1">
          {BRANCH_HEALTH_BAR_KEYS.map((key) => (
            <span
              key={key}
              className="flex items-center gap-1.5 text-[11px] text-ecmp-text-secondary"
            >
              <span
                className={cn(
                  "size-2 shrink-0 rounded-full",
                  BRANCH_HEALTH_BAR_COLOR_CLASS[key],
                )}
                aria-hidden
              />
              {t(BRANCH_HEALTH_BAR_LABEL_KEY[key])}
            </span>
          ))}
          <span className={`ml-auto shrink-0 ${DASHBOARD_CAPTION}`}>
            {t("branchHealthListCount", { count: ranked.length })}
          </span>
        </div>
      ) : null}

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={4} />
        </div>
      ) : state.status === "error" ? (
        <div className="mt-3 flex-1">
          <ErrorState
            title={t("unableToLoad")}
            message={t("noBranchDataDescription")}
            onRetry={retry}
          />
        </div>
      ) : ranked.length === 0 ? (
        <div className="mt-3 flex-1">
          <Empty
            className="py-8"
            icon={<IconEmpty className="size-8 text-ecmp-muted" aria-hidden />}
            title={t("noBranchData")}
            description={t("noBranchDataDescription")}
            primaryAction={{
              label: tCommon("goToReports"),
              onClick: () => router.push("/reports"),
            }}
          />
        </div>
      ) : (
        <ol className="mt-2 max-h-[20rem] overflow-y-auto pr-1">
          {ranked.map((row, index) => {
            const label =
              row.unitCode ??
              (row.branchName
                ? branchHealthShortLabel(row.branchName)
                : t("unknownBranch"));
            const values: Record<(typeof BRANCH_HEALTH_BAR_KEYS)[number], number> = {
              caseTotal: row.caseTotal,
              caseClosed: row.caseClosed,
              escalated: row.escalated,
            };

            return (
              <li
                key={row.branchId ?? `unassigned-${index}`}
                className={cn(
                  "flex items-center gap-2.5 px-1 py-1.5",
                  index > 0 ? "border-t border-ecmp-border/30" : "",
                )}
              >
                <span className="w-8 shrink-0 truncate text-[13px] font-medium text-ecmp-text-primary">
                  {label}
                </span>
                <div className="flex min-w-0 flex-1 flex-col gap-px">
                  {BRANCH_HEALTH_BAR_KEYS.map((key) => {
                    const value = values[key];
                    const pct = proportionalPct(value, scale);
                    const barLabel = t(BRANCH_HEALTH_BAR_LABEL_KEY[key]);
                    return (
                      <div
                        key={key}
                        className="flex h-2 items-center gap-1.5"
                        title={t("branchHealthSegmentTooltip", {
                          label: barLabel,
                          count: value,
                        })}
                      >
                        <div className="h-full min-w-0 flex-1 overflow-hidden rounded-[2px] bg-ecmp-surface-sunken">
                          <div
                            className={cn(
                              "h-full rounded-[2px]",
                              BRANCH_HEALTH_BAR_COLOR_CLASS[key],
                            )}
                            style={{ width: `${Math.max(pct, value > 0 ? 3 : 0)}%` }}
                          />
                        </div>
                        <span className="shrink-0 tabular-nums text-[10px] text-ecmp-text-secondary">
                          {value}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
}
