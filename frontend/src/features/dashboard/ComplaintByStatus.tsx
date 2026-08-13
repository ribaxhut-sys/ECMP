"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import type { ComplaintStatus, StatusCount } from "@/lib/api/types";
import { IconEmpty } from "@/shared/icons";
import { Empty, Skeleton } from "@/shared/ui";
import {
  DASHBOARD_CAPTION,
  DASHBOARD_COMMAND_LABEL,
  DASHBOARD_HOVER_ROW,
  DASHBOARD_TILE,
} from "./dashboardUtils";
import { STATUS_CHART_COLORS, STATUS_CHART_FALLBACK } from "./statusPalette";

function buildConicGradient(
  slices: { status: ComplaintStatus; count: number; pct: number }[],
  highlight: ComplaintStatus | null,
): string {
  if (slices.length === 0) return STATUS_CHART_FALLBACK;
  let cursor = 0;
  const parts: string[] = [];
  for (const slice of slices) {
    const start = cursor;
    const end = cursor + slice.pct;
    const base = STATUS_CHART_COLORS[slice.status] ?? STATUS_CHART_FALLBACK;
    const dimmed = highlight !== null && highlight !== slice.status;
    // Token is --ecmp-color-surface (the bare --ecmp-surface name only
    // exists as the Tailwind utility bg-ecmp-surface). An undefined var
    // here makes color-mix invalid, which invalidates the whole
    // conic-gradient — the donut vanished entirely on legend hover.
    const color = dimmed
      ? `color-mix(in srgb, ${base} 28%, var(--ecmp-color-surface))`
      : base;
    parts.push(`${color} ${start}% ${end}%`);
    cursor = end;
  }
  return `conic-gradient(${parts.join(", ")})`;
}

export function ComplaintByStatus({
  rows,
  complaintKpiSource,
  loading,
}: {
  rows: StatusCount[] | null;
  complaintKpiSource?: "aggregate" | "foundation" | null;
  loading: boolean;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const { hasPermission } = useAuth();
  const canOpenComplaintList =
    hasPermission("complaints:read") || hasPermission("*");
  const tCommon = useTranslations("common");
  const tStatus = useTranslations("status");
  const [highlight, setHighlight] = useState<ComplaintStatus | null>(null);

  const slices = useMemo(() => {
    const visible = (rows ?? []).filter((row) => row.count > 0);
    const total = visible.reduce((sum, row) => sum + row.count, 0);
    if (total === 0) return [];
    return visible.map((row) => ({
      status: row.status,
      count: row.count,
      pct: (row.count / total) * 100,
      labelKey: row.labelKey,
    }));
  }, [rows]);

  const total = slices.reduce((sum, slice) => sum + slice.count, 0);
  const gradient = buildConicGradient(slices, highlight);

  return (
    <section
      data-testid="dashboard-status-distribution"
      aria-label={t("byStatus")}
      className={`${DASHBOARD_TILE} flex h-full flex-col p-5`}
    >
      <div>
        <h2 className={DASHBOARD_COMMAND_LABEL}>{t("byStatus")}</h2>
        <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>
          {complaintKpiSource === "aggregate"
            ? t("statusDistributionAggregateHint")
            : t("statusDistributionDescription")}
        </p>
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={4} />
        </div>
      ) : slices.length === 0 ? (
        <div className="mt-3 flex-1">
          <Empty
            className="py-8"
            icon={<IconEmpty className="size-8 text-ecmp-muted" aria-hidden />}
            title={t("noStatusData")}
            description={t("noStatusDataDescription")}
            primaryAction={
              canOpenComplaintList
                ? {
                    label: tCommon("goToComplaints"),
                    onClick: () => router.push("/complaints"),
                  }
                : undefined
            }
          />
        </div>
      ) : (
        <div className="mt-3 flex flex-1 flex-col items-center gap-4 sm:flex-row sm:items-start">
          <div
            className="relative size-36 shrink-0 rounded-full"
            style={{ background: gradient }}
            role="img"
            aria-label={t("byStatus")}
          >
            <div className="absolute inset-[24%] flex flex-col items-center justify-center rounded-full bg-ecmp-surface">
              <span className="font-mono text-[24px] font-medium tabular-nums text-ecmp-text-primary">
                {total}
              </span>
              <span className={DASHBOARD_CAPTION}>{t("total")}</span>
            </div>
          </div>
          <ul className="w-full min-w-0 flex-1 space-y-0.5" aria-label={t("byStatus")}>
            {slices.map((slice) => {
              const active = highlight === slice.status;
              const label = slice.labelKey
                ? t(slice.labelKey)
                : tStatus(slice.status);
              return (
                <li key={slice.status}>
                  <button
                    type="button"
                    onMouseEnter={() => setHighlight(slice.status)}
                    onMouseLeave={() => setHighlight(null)}
                    onFocus={() => setHighlight(slice.status)}
                    onBlur={() => setHighlight(null)}
                    className={`${DASHBOARD_HOVER_ROW} flex w-full items-center justify-between gap-2 rounded px-1.5 py-1 text-left ${
                      active ? "bg-ecmp-hover/50" : ""
                    }`}
                    aria-label={`${label}: ${slice.count} (${Math.round(slice.pct)}%)`}
                  >
                    <span className="flex min-w-0 items-center gap-2">
                      <span
                        className="size-2 shrink-0 rounded-full"
                        style={{
                          backgroundColor:
                            STATUS_CHART_COLORS[slice.status] ??
                            STATUS_CHART_FALLBACK,
                        }}
                        aria-hidden
                      />
                      <span className="truncate text-[12px] text-ecmp-text-primary">
                        {label}
                      </span>
                    </span>
                    <span className="flex shrink-0 items-baseline gap-1.5 font-mono tabular-nums">
                      <span className="text-[12px] font-medium text-ecmp-text-primary">
                        {slice.count}
                      </span>
                      <span className={DASHBOARD_CAPTION}>
                        {Math.round(slice.pct)}%
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </section>
  );
}
