"use client";

import { useMemo, type ComponentProps } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  Skeleton,
  StatCard,
  type StatAccent,
} from "@/shared/ui";
import { IconAssignments, IconCheck, IconComplaints, IconQueue } from "@/shared/icons";
import { useInternalComplaints } from "./mock/useInternalComplaints";
import { sortForDashboardAction } from "./internalComplaintsFilters";
import { usePendingTransferRequestCount } from "./usePendingTransferRequestCount";
import { usePendingWithdrawRequestCount } from "./usePendingWithdrawRequestCount";
import {
  InternalPriorityBadge,
  InternalStatusBadge,
  InternalTransferRequestBadge,
  InternalWithdrawRequestBadge,
} from "./components/InternalBadges";
import { displayInternalUnitCode } from "./transferDirection";

function ClickableStat({
  href,
  ...statProps
}: { href: string } & Omit<ComponentProps<typeof StatCard>, "className">) {
  const router = useRouter();
  return (
    <button
      type="button"
      className="block w-full rounded-[var(--ecmp-radius-card)] text-left transition-transform hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-primary"
      onClick={() => router.push(href)}
    >
      <StatCard {...statProps} className="hover:shadow-ecmp-hover" />
    </button>
  );
}

export function InternalDashboardView() {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const { rows, total, truncated, loading, error, reload } = useInternalComplaints();
  const pendingTransfer = usePendingTransferRequestCount();
  const pendingWithdraw = usePendingWithdrawRequestCount();

  const actionable = useMemo(
    () => sortForDashboardAction(rows).slice(0, 6),
    [rows],
  );

  const openCount = rows.filter((r) => r.status !== "CLOSED").length;
  const resolvedCount = rows.filter((r) => r.status === "RESOLVED").length;
  const closedCount = rows.filter((r) => r.status === "CLOSED").length;
  const pendingRequests = pendingTransfer + pendingWithdraw;

  const resolvedAccent: StatAccent = resolvedCount > 0 ? "attention" : "healthy";
  const pendingAccent: StatAccent = pendingRequests > 0 ? "attention" : "healthy";

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        description={t("dashboardDescription")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        actions={
          <Button type="button" onClick={() => router.push("/internal/complaints/new")}>
            {t("create")}
          </Button>
        }
      />
      {error ? (
        <ErrorState message={error} onRetry={reload} />
      ) : truncated ? (
        <Alert
          tone="warning"
          title={t("partialDataWarning", { loaded: rows.length, total })}
        />
      ) : null}

      <div className="grid gap-[var(--ecmp-card-gap)] sm:grid-cols-2 xl:grid-cols-4">
        <ClickableStat
          href="/internal/complaints"
          accent="normal"
          icon={<IconQueue className="size-4" aria-hidden />}
          title={t("kpiOpen")}
          value={<span className="tabular-nums">{openCount}</span>}
          subtitle={t("kpiOpenHint")}
          loading={loading}
        />
        <ClickableStat
          href="/internal/verification"
          accent={resolvedAccent}
          icon={<IconCheck className="size-4" aria-hidden />}
          title={t("kpiResolved")}
          value={<span className="tabular-nums">{resolvedCount}</span>}
          subtitle={t("kpiResolvedHint")}
          loading={loading}
        />
        <ClickableStat
          href="/internal/complaints"
          accent={pendingAccent}
          icon={<IconAssignments className="size-4" aria-hidden />}
          title={t("kpiPendingRequests")}
          value={<span className="tabular-nums">{pendingRequests}</span>}
          subtitle={t("kpiPendingRequestsHint")}
        />
        <ClickableStat
          href="/internal/complaints"
          accent="archived"
          icon={<IconComplaints className="size-4" aria-hidden />}
          title={t("kpiClosed")}
          value={<span className="tabular-nums">{closedCount}</span>}
          subtitle={t("kpiClosedHint")}
          loading={loading}
        />
      </div>

      <Card padding={false}>
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-ecmp-border p-[var(--ecmp-card-padding)]">
          <div>
            <h2 className="text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
              {t("actionNeededTitle")}
            </h2>
            <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              {t("actionNeededDescription")}
            </p>
          </div>
          <button
            type="button"
            className="text-[length:var(--ecmp-font-helper-size)] font-semibold text-ecmp-primary hover:underline"
            onClick={() => router.push("/internal/complaints")}
          >
            {t("seeAllComplaints")}
          </button>
        </div>
        {loading ? (
          <CardBody className="p-[var(--ecmp-card-padding)]">
            <Skeleton rows={4} />
          </CardBody>
        ) : actionable.length === 0 ? (
          <CardBody className="p-[var(--ecmp-card-padding)]">
            <Empty title={t("listEmpty")} description={t("listEmptyDescription")} />
          </CardBody>
        ) : (
          <ul>
            {actionable.map((row) => (
              <li
                key={row.id}
                className="border-b border-ecmp-border last:border-b-0"
              >
                <button
                  type="button"
                  className="flex w-full flex-wrap items-center gap-3 px-[var(--ecmp-card-padding)] py-3 text-left hover:bg-ecmp-secondary-muted/60"
                  onClick={() =>
                    router.push(`/internal/complaints/${encodeURIComponent(row.id)}`)
                  }
                >
                  <div className="min-w-[220px] flex-1">
                    <div className="text-[length:var(--ecmp-font-caption-size)] font-semibold tabular-nums text-ecmp-text-secondary">
                      {row.number}
                    </div>
                    <div className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                      {row.title}
                    </div>
                    <div className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                      {displayInternalUnitCode(row.handlingUnitId)}
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5">
                    <InternalStatusBadge status={row.status} />
                    <InternalPriorityBadge priority={row.priority} />
                    <InternalTransferRequestBadge status={row.transferRequestStatus} />
                    <InternalWithdrawRequestBadge status={row.withdrawRequestStatus} />
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </PageContainer>
  );
}
