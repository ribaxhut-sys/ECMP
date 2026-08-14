"use client";

import { useEffect, useMemo, useState } from "react";
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
import { Badge, Empty, Select, Skeleton, Timeline } from "@/shared/ui";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { resolveActivityMeta } from "./activityLabels";
import {
  actorInitials,
  aggregateComplaintActivitySummaries,
  branchOptionLabel,
  DASHBOARD_CAPTION,
  DASHBOARD_SECTION_TITLE,
  DASHBOARD_SURFACE_QUIET,
  formatRelativeTime,
  sortBranchesHeadOfficeFirst,
} from "./dashboardUtils";

const RECENT_ACTIVITY_LIMIT = 10;

type MobilePane = "activity" | "summary";

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
  const [mobilePane, setMobilePane] = useState<MobilePane>("activity");
  const [selectedNumber, setSelectedNumber] = useState<string | null>(null);

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
        if (!cancelled) {
          setRows(res.data);
          setSelectedNumber(null);
        }
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

  const summaries = useMemo(
    () => (rows ? aggregateComplaintActivitySummaries(rows) : []),
    [rows],
  );

  const visibleRows = useMemo(() => {
    if (!rows) return [];
    if (!selectedNumber) return rows;
    return rows.filter((row) => row.complaintNumber === selectedNumber);
  }, [rows, selectedNumber]);

  const branchOptions = [
    { value: "", label: t("recentActivityAllBranches") },
    ...sortBranchesHeadOfficeFirst(branches).map((branch) => ({
      value: branch.id,
      label: branchOptionLabel(branch),
    })),
  ];

  const empty = !loading && (!rows || rows.length === 0);

  return (
    <section
      data-testid="dashboard-recent-activity"
      id="recent-activity"
      aria-label={t("recentActivity")}
      className={`${DASHBOARD_SURFACE_QUIET} flex h-full flex-col p-3.5`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className={DASHBOARD_SECTION_TITLE}>{t("recentActivity")}</h2>
          <p className={`mt-0.5 ${DASHBOARD_CAPTION}`}>{t("complaintSummaryHint")}</p>
        </div>
        {isHeadOffice ? (
          <div className="w-[11rem] shrink-0">
            <Select
              name="recentActivityBranch"
              aria-label={t("recentActivityBranchFilter")}
              options={branchOptions}
              value={branchId}
              onChange={(e) => setBranchId(e.target.value)}
            />
          </div>
        ) : null}
      </div>

      <div
        className="mt-3 flex gap-1 xl:hidden"
        role="tablist"
        aria-label={t("recentActivity")}
      >
        <PaneTab
          selected={mobilePane === "activity"}
          onSelect={() => setMobilePane("activity")}
          label={t("activityDetailTab")}
        />
        <PaneTab
          selected={mobilePane === "summary"}
          onSelect={() => setMobilePane("summary")}
          label={t("complaintSummaryTab")}
        />
      </div>

      {loading ? (
        <div className="mt-3" aria-busy="true">
          <Skeleton rows={4} />
        </div>
      ) : empty ? (
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
        <div className="mt-2.5 grid flex-1 grid-cols-1 gap-3 xl:grid-cols-12 xl:gap-4">
          <div
            className={`max-h-[20rem] overflow-y-auto pr-1 xl:col-span-7 xl:border-r xl:border-ecmp-border/60 xl:pr-4 ${
              mobilePane === "activity" ? "block" : "hidden xl:block"
            }`}
          >
            {selectedNumber ? (
              <div className="mb-2 flex items-center justify-between gap-2">
                <p className={DASHBOARD_CAPTION}>
                  {selectedNumber}
                </p>
                <button
                  type="button"
                  className="text-[12px] font-medium text-ecmp-primary hover:underline"
                  onClick={() => setSelectedNumber(null)}
                >
                  {t("showAllActivity")}
                </button>
              </div>
            ) : null}
            <Timeline
              aria-label={t("recentActivity")}
              items={visibleRows.map((row, index) => {
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
                      className="text-[9px] font-medium tracking-tight text-ecmp-primary"
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

          <div
            className={`max-h-[20rem] overflow-y-auto pr-1 xl:col-span-5 ${
              mobilePane === "summary" ? "block" : "hidden xl:block"
            }`}
          >
            <h3 className={DASHBOARD_SECTION_TITLE}>{t("complaintSummary")}</h3>
            <ul className="mt-2 space-y-1.5" aria-label={t("complaintSummary")}>
              {summaries.map((summary) => {
                const meta = resolveActivityMeta(summary.lastEventType);
                const selected = selectedNumber === summary.complaintNumber;
                const when = formatDateTime24(summary.lastTimestamp, tCommon("emDash"));
                const actor = summary.actor || tCommon("emDash");
                return (
                  <li
                    key={summary.complaintNumber}
                    className={`rounded-md px-2 py-1.5 ${
                      selected ? "bg-ecmp-surface ring-1 ring-ecmp-border" : ""
                    }`}
                  >
                    <div className="flex min-w-0 items-center gap-2">
                      <Link
                        href={`/complaints?keyword=${encodeURIComponent(summary.complaintNumber)}`}
                        className="shrink-0 font-mono text-[12px] text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
                      >
                        {summary.complaintNumber}
                      </Link>
                      <Badge tone={meta.statusTone} className="shrink-0">
                        {t(meta.badgeKey)}
                      </Badge>
                    </div>
                    <button
                      type="button"
                      aria-pressed={selected}
                      aria-label={t("filterActivityByComplaint")}
                      onClick={() =>
                        setSelectedNumber((current) =>
                          current === summary.complaintNumber
                            ? null
                            : summary.complaintNumber,
                        )
                      }
                      className={`mt-0.5 w-full truncate text-left hover:text-ecmp-text-primary ${DASHBOARD_CAPTION}`}
                    >
                      {when}
                      <span aria-hidden> · </span>
                      {actor}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}

function PaneTab({
  selected,
  onSelect,
  label,
}: {
  selected: boolean;
  onSelect: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={selected}
      onClick={onSelect}
      className={`rounded-md px-2.5 py-1 text-[12px] font-medium ${
        selected
          ? "bg-ecmp-surface text-ecmp-text-primary"
          : "text-ecmp-text-secondary hover:text-ecmp-text-primary"
      }`}
    >
      {label}
    </button>
  );
}
