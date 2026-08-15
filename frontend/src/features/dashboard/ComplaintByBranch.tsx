"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import type { BranchCount } from "@/lib/api/types";
import { IconEmpty } from "@/shared/icons";
import { Empty, Skeleton } from "@/shared/ui";
import {
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  sortBranchesByHealth,
} from "./dashboardUtils";

function casePctLabel(
  closed: number,
  total: number,
  locale: string,
  empty: string,
): string {
  if (total <= 0) return empty;
  const pct = (closed / total) * 100;
  const formatted = new Intl.NumberFormat(locale, {
    maximumFractionDigits: 1,
    minimumFractionDigits: pct % 1 === 0 ? 0 : 1,
  }).format(pct);
  return `${formatted}%`;
}

export function ComplaintByBranch({
  rows,
  loading,
}: {
  rows: BranchCount[] | null;
  loading: boolean;
}) {
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");

  const ranked = useMemo(() => {
    if (!rows || rows.length === 0) return [];
    return sortBranchesByHealth(rows);
  }, [rows]);

  const emptyPct = t("branchHealthPctNone");

  return (
    <section
      data-testid="dashboard-branch-performance"
      id="branch-health"
      aria-label={t("branchHealth")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className={DASHBOARD_SECTION_TITLE}>{t("branchHealth")}</h2>
          <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>{t("byBranch")}</p>
        </div>
        {ranked.length > 0 ? (
          <p className={`shrink-0 ${DASHBOARD_CAPTION}`}>
            {t("branchHealthListCount", { count: ranked.length })}
          </p>
        ) : null}
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={4} />
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
        <div className="mt-3 max-h-[20rem] overflow-y-auto pr-1">
          <div
            className={`${DASHBOARD_CAPTION} mb-1 grid grid-cols-[minmax(0,1fr)_7.5rem_minmax(11rem,auto)] gap-3 px-1`}
          >
            <span />
            <span className="text-right">{t("branchHealthComplaints")}</span>
            <span className="text-right">{t("branchHealthCases")}</span>
          </div>
          <ol>
            {ranked.map((row, index) => {
              const label = row.branchName ?? t("unknownBranch");
              const pct = casePctLabel(
                row.caseClosed,
                row.caseTotal,
                locale,
                emptyPct,
              );
              return (
                <li
                  key={row.branchId ?? `unassigned-${index}`}
                  className="grid grid-cols-[minmax(0,1fr)_7.5rem_minmax(11rem,auto)] items-baseline gap-3 border-b border-ecmp-border/30 px-1 py-1.5 last:border-0"
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <span className="w-6 shrink-0 tabular-nums text-[11px] text-ecmp-text-secondary">
                      {index + 1}
                    </span>
                    <span className="truncate text-[13px] text-ecmp-text-primary">
                      {label}
                    </span>
                  </span>
                  <span className="text-right tabular-nums text-[13px] text-ecmp-text-primary">
                    {t("branchHealthComplaintVolume", {
                      count: row.total,
                      cases: row.caseTotal,
                    })}
                  </span>
                  <span className={`text-right tabular-nums ${DASHBOARD_CAPTION}`}>
                    {t("branchHealthCaseDetail", {
                      closed: row.caseClosed,
                      open: row.caseOpen,
                      pct,
                    })}
                  </span>
                </li>
              );
            })}
          </ol>
        </div>
      )}
    </section>
  );
}
