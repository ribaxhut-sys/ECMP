"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { BranchCount } from "@/lib/api/types";
import { Empty, Skeleton } from "@/shared/ui";
import {
  branchBadgeKind,
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  OPS_TONE_DOT,
  OPS_TONE_TEXT,
  type BranchBadgeKind,
  type OpsTone,
} from "./dashboardUtils";

function kindTone(kind: BranchBadgeKind): OpsTone {
  if (kind === "top") return "healthy";
  if (kind === "attention") return "attention";
  return "neutral";
}

export function ComplaintByBranch({
  rows,
  loading,
  onRefresh,
}: {
  rows: BranchCount[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");

  const ranked = useMemo(() => {
    if (!rows || rows.length === 0) return [];
    return [...rows].sort((a, b) => b.total - a.total);
  }, [rows]);

  const grandTotal = ranked.reduce((sum, row) => sum + row.total, 0) || 1;

  return (
    <section
      data-testid="dashboard-branch-performance"
      id="branch-health"
      aria-label={t("branchHealth")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("branchHealth")}</h2>
        <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>{t("byBranch")}</p>
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={4} />
        </div>
      ) : ranked.length === 0 ? (
        <div className="mt-3 flex-1">
          <Empty
            title={t("noBranchData")}
            description={t("noBranchDataDescription")}
            primaryAction={{
              label: t("refreshDashboard"),
              onClick: onRefresh,
            }}
            secondaryAction={{
              label: tCommon("goToReports"),
              onClick: () => router.push("/reports"),
            }}
          />
        </div>
      ) : (
        <ol className="mt-3 space-y-1.5">
          {ranked.map((row, index) => {
            const label = row.branchName ?? t("unknownBranch");
            const pct = Math.round((row.total / grandTotal) * 100);
            const kind = branchBadgeKind(index, pct, ranked.length);
            const tone = kindTone(kind);
            const statusLabel =
              kind === "top"
                ? t("topPerformer")
                : kind === "attention"
                  ? t("needsAttention")
                  : null;
            return (
              <li
                key={row.branchId ?? `unassigned-${index}`}
                className="flex items-center justify-between gap-2 px-1 py-1"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span className="w-4 shrink-0 tabular-nums text-[11px] text-ecmp-text-secondary">
                    {index + 1}
                  </span>
                  <span className="truncate text-[13px] text-ecmp-text-primary">
                    {label}
                  </span>
                  {statusLabel ? (
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] ${OPS_TONE_TEXT[tone]}`}
                    >
                      <span
                        className={`size-1.5 rounded-full ${OPS_TONE_DOT[tone]}`}
                        aria-hidden
                      />
                      {statusLabel}
                    </span>
                  ) : null}
                </span>
                <span className="shrink-0 tabular-nums text-[13px] text-ecmp-text-primary">
                  {row.total}
                  <span className={`ml-1.5 ${DASHBOARD_CAPTION}`}>{pct}%</span>
                </span>
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
}
