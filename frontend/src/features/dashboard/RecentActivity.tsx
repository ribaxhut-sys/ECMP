"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  fetchBranches,
  fetchDashboardRecentActivity,
  type Branch,
} from "@/lib/api";
import type { DashboardRecentActivityItem } from "@/lib/api/types";
import { IconEmpty } from "@/shared/icons";
import { Empty, Select, Skeleton, Timeline } from "@/shared/ui";
import { resolveActivityMeta } from "./activityLabels";
import {
  actorInitials,
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  formatRelativeTime,
} from "./dashboardUtils";

const RECENT_ACTIVITY_LIMIT = 10;

export function RecentActivity() {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const { user } = useAuth();

  // UM-BUG-009 — only a Head Office principal (no own branch) can pick which
  // branch's activity to view; the backend locks anyone else to their own
  // branch regardless, so the picker would be misleading for them.
  const isHeadOffice = !user?.branchId;

  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchId, setBranchId] = useState("");
  const [rows, setRows] = useState<DashboardRecentActivityItem[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isHeadOffice) return;
    fetchBranches(100)
      .then((res) => setBranches(res.data))
      .catch(() => setBranches([]));
  }, [isHeadOffice]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchDashboardRecentActivity({
      branchId: isHeadOffice && branchId ? branchId : undefined,
      limit: RECENT_ACTIVITY_LIMIT,
    })
      .then((res) => {
        if (!cancelled) setRows(res.data);
      })
      .catch(() => {
        if (!cancelled) setRows(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isHeadOffice, branchId]);

  const branchOptions = [
    { value: "", label: t("recentActivityAllBranches") },
    ...branches.map((branch) => ({
      value: branch.id,
      label: `${branch.code} — ${branch.name}`,
    })),
  ];

  return (
    <section
      data-testid="dashboard-recent-activity"
      id="recent-activity"
      aria-label={t("recentActivity")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className={DASHBOARD_SECTION_TITLE}>{t("recentActivity")}</h2>
          <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>{t("latestComplaints")}</p>
        </div>
        {isHeadOffice ? (
          <Select
            name="recentActivityBranch"
            aria-label={t("recentActivityBranchFilter")}
            options={branchOptions}
            value={branchId}
            onChange={(e) => setBranchId(e.target.value)}
            className="min-w-[12rem]"
          />
        ) : null}
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={4} />
        </div>
      ) : !rows || rows.length === 0 ? (
        <div className="mt-3 flex-1">
          <Empty
            className="py-8"
            icon={<IconEmpty className="size-8 text-ecmp-muted" aria-hidden />}
            title={t("noActivity")}
            description={t("noActivityDescription")}
            primaryAction={{
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
