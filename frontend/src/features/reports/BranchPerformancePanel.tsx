"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import type { BranchCount } from "@/lib/api/types";
import { cn } from "@/shared/utils";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { branchPerformanceRows } from "./reportSummaryStats";

const rankBarClass = {
  top: "bg-ecmp-success",
  middle: "bg-ecmp-info",
  lowest: "bg-ecmp-warning",
} as const;

export function BranchPerformancePanel({
  rows,
  loading,
}: {
  rows: BranchCount[] | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");
  const ranked = useMemo(() => branchPerformanceRows(rows), [rows]);

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("branchPerformance")}
    >
      <SectionHeader
        title={t("branchPerformance")}
        description={t("branchPerformanceDescription")}
      />
      <Card>
        <CardHeader>
          <PanelHeader
            title={t("branchVolume")}
            description={t("branchVolumeDescription")}
            className="mb-0 border-0 pb-0"
          />
        </CardHeader>
        <CardBody>
          {loading ? (
            <Skeleton rows={5} />
          ) : !ranked ? (
            <Empty
              title={t("noBranchData")}
              description={t("noBranchDataDescription")}
            />
          ) : (
            <ul className="space-y-[var(--ecmp-card-gap)]" role="list">
              {ranked.map((row) => (
                <li key={row.key} className="space-y-2">
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-[length:var(--ecmp-font-body-size)] font-[number:var(--ecmp-font-card-title-weight)] text-ecmp-text-primary">
                        {row.name === "—" ? t("unknownBranch") : row.name}
                      </p>
                      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                        {row.rank === "top"
                          ? t("rankTop")
                          : row.rank === "lowest"
                            ? t("rankLowest")
                            : t("rankMiddle")}
                      </p>
                    </div>
                    <span className="shrink-0 tabular-nums text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {row.total}
                    </span>
                  </div>
                  <div
                    className="h-3 overflow-hidden rounded-[var(--ecmp-radius-full)] bg-ecmp-secondary-muted"
                    role="meter"
                    aria-valuenow={row.total}
                    aria-valuemin={0}
                    aria-valuemax={ranked[0]?.total ?? row.total}
                    aria-label={t("branchBarLabel", {
                      branch: row.name === "—" ? t("unknownBranch") : row.name,
                      count: row.total,
                    })}
                  >
                    <div
                      className={cn(
                        "h-full rounded-[var(--ecmp-radius-full)] transition-[width] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
                        rankBarClass[row.rank],
                      )}
                      style={{ width: `${row.share}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </section>
  );
}
