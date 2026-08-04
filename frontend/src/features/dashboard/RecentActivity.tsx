"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import type { DashboardRecentActivityItem } from "@/lib/api/types";
import { Empty, Skeleton, Timeline } from "@/shared/ui";
import { resolveActivityMeta } from "./activityLabels";
import {
  actorInitials,
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  formatRelativeTime,
} from "./dashboardUtils";

export function RecentActivity({
  rows,
  loading,
  onRefresh,
}: {
  rows: DashboardRecentActivityItem[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const locale = useLocale();

  return (
    <section
      data-testid="dashboard-recent-activity"
      id="recent-activity"
      aria-label={t("recentActivity")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div>
        <h2 className={DASHBOARD_SECTION_TITLE}>{t("recentActivity")}</h2>
        <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>{t("latestComplaints")}</p>
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={4} />
        </div>
      ) : !rows || rows.length === 0 ? (
        <div className="mt-3 flex-1">
          <Empty
            title={t("noActivity")}
            description={t("noActivityDescription")}
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
        <div className="mt-2.5 max-h-[20rem] flex-1 overflow-y-auto pr-1">
          <Timeline
            aria-label={t("recentActivity")}
            items={rows.map((row, index) => {
              const meta = resolveActivityMeta(row.eventType);
              const initials = actorInitials(row.actor);
              return {
                id: `${row.complaintNumber}-${row.eventType}-${row.timestamp}-${index}`,
                title: t(meta.labelKey),
                time: formatRelativeTime(row.timestamp, locale),
                actor: row.actor || tCommon("emDash"),
                status: t(meta.badgeKey),
                statusTone: meta.statusTone,
                icon: (
                  <span
                    className="text-[10px] font-medium text-ecmp-primary"
                    aria-hidden
                  >
                    {initials}
                  </span>
                ),
                description: (
                  <Link
                    href={`/complaints?keyword=${encodeURIComponent(row.complaintNumber)}`}
                    className="font-mono text-[12px] text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
                  >
                    {row.complaintNumber}
                  </Link>
                ),
              };
            })}
          />
        </div>
      )}
    </section>
  );
}
