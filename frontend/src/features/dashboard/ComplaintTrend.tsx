"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { StatusCount } from "@/lib/api/types";
import { Empty, Skeleton } from "@/shared/ui";
import {
  DASHBOARD_BODY,
  DASHBOARD_CAPTION,
  DASHBOARD_CARD_TITLE,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE,
} from "./dashboardUtils";
import { STATUS_CHART_COLORS, STATUS_CHART_FALLBACK } from "./statusPalette";

/**
 * Live volume composition from by-status report (real snapshot).
 * Daily historical trend remains unavailable until analytics history ships —
 * never invent time-series points.
 */
export function ComplaintTrend({
  rows,
  loading,
  onRefresh,
}: {
  rows?: StatusCount[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const tStatus = useTranslations("status");

  const bars = useMemo(() => {
    const visible = (rows ?? []).filter((row) => row.count > 0);
    const max = Math.max(...visible.map((row) => row.count), 0);
    return { visible, max: max || 1 };
  }, [rows]);

  const total = bars.visible.reduce((sum, row) => sum + row.count, 0);

  return (
    <section
      data-testid="dashboard-complaint-trend"
      className={`${DASHBOARD_SURFACE} relative flex h-full min-h-[360px] flex-col overflow-hidden p-5 md:p-6`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className={DASHBOARD_SECTION_TITLE}>{t("liveVolumeTitle")}</h2>
          <p className={`mt-1 ${DASHBOARD_CARD_TITLE}`}>
            {t("liveVolumeDescription")}
          </p>
        </div>
        <span className="inline-flex items-center rounded-full border border-ecmp-border/70 bg-ecmp-surface-sunken px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-ecmp-text-secondary">
          {t("liveSnapshotBadge")}
        </span>
      </div>

      {loading ? (
        <div className="mt-6 flex-1" aria-busy="true">
          <Skeleton rows={7} />
        </div>
      ) : bars.visible.length === 0 ? (
        <div className="mt-6 flex-1">
          <Empty
            title={t("noStatusData")}
            description={t("noStatusDataDescription")}
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
      ) : (
        <div className="mt-5 flex flex-1 flex-col">
          <div className="mb-4 flex items-end justify-between gap-3">
            <div>
              <p className="text-[32px] font-semibold leading-none tabular-nums text-ecmp-text-primary">
                {total}
              </p>
              <p className={`mt-1 ${DASHBOARD_CAPTION}`}>{t("liveVolumeTotal")}</p>
            </div>
            <p className={`max-w-[220px] text-right ${DASHBOARD_CAPTION}`}>
              {t("historyDeferredNote")}
            </p>
          </div>

          {/* Chart frame */}
          <div className="relative flex min-h-[200px] flex-1 items-end gap-2 rounded-[var(--ecmp-radius-xl)] border border-ecmp-border/50 bg-[linear-gradient(180deg,color-mix(in_srgb,var(--ecmp-color-primary)_4%,transparent)_0%,transparent_42%)] px-3 pb-3 pt-8 sm:gap-3 sm:px-4">
            {/* Horizontal guides */}
            <div aria-hidden className="pointer-events-none absolute inset-x-3 top-8 bottom-3 sm:inset-x-4">
              <div className="absolute inset-x-0 top-0 border-t border-dashed border-ecmp-border/60" />
              <div className="absolute inset-x-0 top-1/3 border-t border-dashed border-ecmp-border/40" />
              <div className="absolute inset-x-0 top-2/3 border-t border-dashed border-ecmp-border/40" />
              <div className="absolute inset-x-0 bottom-0 border-t border-ecmp-border/50" />
            </div>

            {bars.visible.map((row) => {
              const heightPct = Math.max(8, Math.round((row.count / bars.max) * 100));
              const color = STATUS_CHART_COLORS[row.status] ?? STATUS_CHART_FALLBACK;
              return (
                <div
                  key={row.status}
                  className="relative z-[1] flex min-w-0 flex-1 flex-col items-center justify-end gap-2"
                >
                  <span className="text-[12px] font-semibold tabular-nums text-ecmp-text-primary">
                    {row.count}
                  </span>
                  <div
                    className="w-full max-w-[48px] rounded-t-[10px] motion-safe:transition-[height] motion-safe:duration-500"
                    style={{
                      height: `${heightPct}%`,
                      background: `linear-gradient(180deg, ${color} 0%, color-mix(in srgb, ${color} 55%, white) 100%)`,
                      minHeight: "28px",
                    }}
                    title={`${tStatus(row.status)}: ${row.count}`}
                    role="img"
                    aria-label={`${tStatus(row.status)}: ${row.count}`}
                  />
                  <span className="w-full truncate text-center text-[11px] font-medium text-ecmp-text-secondary">
                    {tStatus(row.status)}
                  </span>
                </div>
              );
            })}
          </div>

          <p className={`mt-3 ${DASHBOARD_BODY}`}>{t("liveVolumeFootnote")}</p>
        </div>
      )}
    </section>
  );
}
