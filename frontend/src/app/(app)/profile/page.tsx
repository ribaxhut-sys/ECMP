"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  isOwnModuleActivity,
  moduleRoleDisplayLabels,
  primaryRoleLabel,
  resolveIdentityUnitLabel,
} from "@/features/auth";
import { resolveActivityMeta } from "@/features/dashboard/activityLabels";
import {
  actorInitials,
  activitySubjectText,
  formatRelativeTime,
} from "@/features/dashboard/dashboardUtils";
import {
  fetchBranches,
  fetchDashboardRecentActivity,
  type Branch,
} from "@/lib/api";
import type { DashboardRecentActivityItem } from "@/lib/api/types";
import { formatDateTime24 } from "@/shared/utils/datetime";
import {
  Badge,
  Card,
  CardBody,
  Empty,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
  Timeline,
} from "@/shared/ui";

const WORK_HISTORY_FETCH_LIMIT = 50;
const WORK_HISTORY_SHOW_LIMIT = 8;

export default function ProfilePage() {
  const { user, status, hasPermission } = useAuth();
  const t = useTranslations("profile");
  const tUsers = useTranslations("users");
  const tCommon = useTranslations("common");
  const tDashboard = useTranslations("dashboard");
  const locale = useLocale();
  const canReadActivity = hasPermission("dashboard:read");

  const [units, setUnits] = useState<Branch[]>([]);
  const [activity, setActivity] = useState<DashboardRecentActivityItem[] | null>(
    null,
  );
  const [activityLoading, setActivityLoading] = useState(canReadActivity);

  const roleLabel = primaryRoleLabel(
    user,
    t("roleUnassigned"),
    moduleRoleDisplayLabels(tUsers),
  );
  const unitLabel = resolveIdentityUnitLabel(
    user?.branchId,
    units,
    t("branchUnassigned"),
  );

  useEffect(() => {
    let cancelled = false;
    void fetchBranches(100)
      .then((res) => {
        if (!cancelled) setUnits(res.data);
      })
      .catch(() => {
        if (!cancelled) setUnits([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const userId = user?.id;
  const userUsername = user?.username;
  const userEmail = user?.email;
  const userFullName = user?.fullName;

  useEffect(() => {
    if (!canReadActivity || !userId) {
      setActivityLoading(false);
      setActivity([]);
      return;
    }
    let cancelled = false;
    setActivityLoading(true);
    const identity = {
      id: userId,
      username: userUsername ?? "",
      email: userEmail ?? "",
      fullName: userFullName ?? "",
    };
    void fetchDashboardRecentActivity({ limit: WORK_HISTORY_FETCH_LIMIT })
      .then((res) => {
        if (cancelled) return;
        setActivity(
          res.data.filter((row) => isOwnModuleActivity(row.actor, identity)),
        );
      })
      .catch(() => {
        if (!cancelled) setActivity([]);
      })
      .finally(() => {
        if (!cancelled) setActivityLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [canReadActivity, userId, userUsername, userEmail, userFullName]);

  const facts = useMemo(
    () => [
      {
        label: t("email"),
        value: user?.email ?? tCommon("emDash"),
      },
      {
        label: t("branch"),
        value: unitLabel,
      },
      {
        label: t("firstActive"),
        value: formatDateTime24(user?.createdAt, locale, tCommon("emDash")),
      },
    ],
    [t, tCommon, locale, unitLabel, user?.createdAt, user?.email],
  );

  if (status === "loading") {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <Skeleton rows={5} />
      </PageContainer>
    );
  }

  const visibleActivity = (activity ?? []).slice(0, WORK_HISTORY_SHOW_LIMIT);

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("title")}
        title={user?.fullName ?? t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={
          user?.username ? (
            <span className="font-mono text-ecmp-text-secondary">
              @{user.username}
            </span>
          ) : null
        }
        meta={
          <>
            <Badge tone="info">{roleLabel}</Badge>
            <Badge tone={user?.isActive ? "success" : "neutral"}>
              {user?.isActive ? t("statusActive") : t("statusInactive")}
            </Badge>
          </>
        }
      />

      <Card>
        <CardBody>
          <dl className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-3">
            {facts.map((fact) => (
              <div key={fact.label} className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {fact.label.replace(/:$/, "")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {fact.value}
                </dd>
              </div>
            ))}
          </dl>
        </CardBody>
      </Card>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader title={t("recentActivity")} />
        <Card>
          <CardBody>
            {activityLoading ? (
              <Skeleton rows={4} />
            ) : visibleActivity.length > 0 ? (
              <Timeline
                aria-label={t("recentActivity")}
                items={visibleActivity.map((row, index) => {
                  const meta = resolveActivityMeta(row.eventType);
                  return {
                    id: `${row.complaintNumber}-${row.eventType}-${row.timestamp}-${index}`,
                    title: tDashboard(meta.labelKey),
                    time: formatRelativeTime(row.timestamp, locale),
                    status: tDashboard(meta.badgeKey),
                    statusTone: meta.statusTone,
                    icon: (
                      <span
                        className="text-[9px] font-medium tracking-tight text-ecmp-primary"
                        aria-hidden
                      >
                        {actorInitials(row.actor)}
                      </span>
                    ),
                    description: (
                      <Link
                        href={`/complaints?keyword=${encodeURIComponent(row.complaintNumber)}`}
                        className="font-mono text-ecmp-primary hover:underline"
                      >
                        {activitySubjectText(row)}
                      </Link>
                    ),
                  };
                })}
              />
            ) : (
              <Empty
                className="border-0 bg-transparent py-4"
                title={t("recentActivityEmptyTitle")}
                description={t("recentActivityEmptyDescription")}
              />
            )}
          </CardBody>
        </Card>
      </section>
    </PageContainer>
  );
}
