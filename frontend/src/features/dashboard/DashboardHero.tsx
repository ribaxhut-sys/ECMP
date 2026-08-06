"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import type { DashboardHeader, DashboardSlaSummary, StatusCount } from "@/lib/api/types";
import { Button, Skeleton } from "@/shared/ui";
import {
  countByStatus,
  DASHBOARD_RIPPLE,
  DASHBOARD_SURFACE,
} from "./dashboardUtils";

function greetingKey(hour: number): "greetingMorning" | "greetingAfternoon" | "greetingEvening" {
  if (hour < 12) return "greetingMorning";
  if (hour < 18) return "greetingAfternoon";
  return "greetingEvening";
}

export function DashboardHero({
  displayName,
  header,
  sla,
  byStatus,
  loading,
  refreshing = false,
  onRefresh,
}: {
  displayName: string;
  header: DashboardHeader | null;
  sla: DashboardSlaSummary | null;
  byStatus: StatusCount[] | null;
  loading: boolean;
  refreshing?: boolean;
  updatedAt: Date | null;
  onRefresh: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const hour = new Date().getHours();
  const greeting = t(greetingKey(hour));
  const name = displayName || "—";

  const breached = sla?.overall.breached ?? null;
  const waitingAssignment = countByStatus(byStatus, "NEW");
  const escalationsPending = countByStatus(byStatus, "ESCALATED");
  const open = header?.openComplaints ?? null;

  const briefingItems = [
    breached !== null && breached > 0
      ? {
          id: "sla",
          label: t("attentionSlaBreached", { count: breached }),
        }
      : null,
    waitingAssignment !== null && waitingAssignment > 0
      ? {
          id: "assign",
          label: t("attentionWaitingAssignment", { count: waitingAssignment }),
        }
      : null,
    escalationsPending !== null && escalationsPending > 0
      ? {
          id: "esc",
          label: t("attentionEscalations", { count: escalationsPending }),
        }
      : null,
    open !== null &&
    open > 0 &&
    breached === 0 &&
    (waitingAssignment ?? 0) === 0 &&
    (escalationsPending ?? 0) === 0
      ? {
          id: "open",
          label: t("attentionOpenComplaints", { count: open }),
        }
      : null,
  ].filter(Boolean) as { id: string; label: string }[];

  return (
    <section
      data-testid="dashboard-hero"
      aria-label={t("operationalBriefing")}
      className={`${DASHBOARD_SURFACE} relative min-h-[160px] overflow-hidden border border-ecmp-border bg-gradient-to-br from-ecmp-primary-muted/45 via-ecmp-surface to-ecmp-surface px-5 py-6 md:px-6 md:py-7`}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-y-0 right-0 w-1/3 bg-[radial-gradient(circle_at_top_right,color-mix(in_srgb,var(--ecmp-color-primary)_18%,transparent),transparent_70%)]"
      />
      <div className="relative flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1 space-y-4">
          {loading ? (
            <div className="space-y-3" aria-busy="true">
              <Skeleton rows={2} />
              <Skeleton rows={1} />
            </div>
          ) : (
            <>
              <div>
                <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("overline")}
                </p>
                <h1 className="mt-1 text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] leading-tight text-ecmp-text-primary">
                  <span className="block text-[length:var(--ecmp-font-section-title-size)] font-medium text-ecmp-text-secondary">
                    {greeting}
                  </span>
                  <span className="mt-0.5 block">{name}</span>
                </h1>
                <p className="mt-3 max-w-2xl text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  {briefingItems.length > 0
                    ? t("heroAttentionRequired")
                    : t("heroAllClear")}
                </p>
              </div>

              {briefingItems.length > 0 ? (
                <ul
                  className="space-y-2"
                  aria-label={t("heroAttentionRequired")}
                >
                  {briefingItems.map((item) => (
                    <li
                      key={item.id}
                      className="flex items-start gap-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary"
                    >
                      <span
                        className="mt-2 size-1.5 shrink-0 rounded-full bg-ecmp-primary"
                        aria-hidden
                      />
                      <span>{item.label}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-success-text">
                  {t("noCriticalAlertsToday")}
                </p>
              )}

              <div className="flex flex-wrap gap-2 pt-1">
                <Button
                  type="button"
                  className={DASHBOARD_RIPPLE}
                  onClick={() => router.push("/queue")}
                >
                  {t("reviewQueue")}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className={DASHBOARD_RIPPLE}
                  onClick={() => router.push("/reports")}
                >
                  {t("viewReports")}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className={DASHBOARD_RIPPLE}
                  onClick={onRefresh}
                  disabled={loading || refreshing}
                  aria-label={
                    loading || refreshing
                      ? tCommon("refreshing")
                      : tCommon("refresh")
                  }
                >
                  {loading || refreshing
                    ? tCommon("refreshing")
                    : tCommon("refresh")}
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
