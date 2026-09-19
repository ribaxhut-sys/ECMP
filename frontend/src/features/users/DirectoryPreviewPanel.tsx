"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import {
  fetchCmBatch1UserWorkStats,
  type CmBatch1UserWorkStats,
  type UserRef,
} from "@/lib/api";
import { Badge, Button, Card, CardBody, Empty, PanelHeader } from "@/shared/ui";
import { DirectoryAvatar } from "./DirectoryAvatar";
import { DirectoryRoleBadge } from "./DirectoryRoleBadge";
import { formatWhen } from "./directoryHelpers";

function WorkStatRow({
  label,
  value,
  loading,
  onClick,
}: {
  label: string;
  value: number | null;
  loading: boolean;
  onClick: () => void;
}) {
  const clickable = !loading && !!value;
  return (
    <li>
      <button
        type="button"
        onClick={onClick}
        disabled={!clickable}
        title={clickable ? label : undefined}
        className="group flex w-full items-center justify-between gap-2 rounded-[var(--ecmp-radius-sm)] px-2 py-1.5 text-left transition-colors duration-[var(--ecmp-duration-fast)] enabled:cursor-pointer enabled:hover:bg-ecmp-surface-hover disabled:cursor-default"
      >
        <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {label}
        </span>
        <span className="flex items-center gap-1">
          <span
            className={
              value
                ? "text-[length:var(--ecmp-font-body-size)] font-[number:var(--ecmp-font-emphasis-weight)] text-ecmp-primary underline-offset-2 group-hover:underline"
                : "text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary"
            }
          >
            {loading ? "…" : (value ?? 0)}
          </span>
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={
              clickable
                ? "size-3.5 shrink-0 text-ecmp-primary opacity-0 transition-[opacity,transform] duration-[var(--ecmp-duration-fast)] group-hover:translate-x-0.5 group-hover:opacity-100"
                : "size-3.5 shrink-0 opacity-0"
            }
          >
            <path d="M9 6l6 6-6 6" />
          </svg>
        </span>
      </button>
    </li>
  );
}

export function DirectoryPreviewPanel({
  user,
  unitLabel,
  initials,
  canUpdateStatus,
  updatingStatus,
  onRequestStatusChange,
  canUpdateRole,
  onRequestRoleChange,
  onClose,
}: {
  user: UserRef | null;
  unitLabel: string | null;
  initials?: string | null;
  canUpdateStatus: boolean;
  updatingStatus: boolean;
  onRequestStatusChange: (user: UserRef) => void;
  canUpdateRole: boolean;
  onRequestRoleChange: (user: UserRef) => void;
  onClose: () => void;
}) {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();

  const userId = user?.id ?? null;
  const [stats, setStats] = useState<CmBatch1UserWorkStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  useEffect(() => {
    if (!userId) {
      setStats(null);
      return;
    }
    let cancelled = false;
    setStats(null);
    setStatsLoading(true);
    fetchCmBatch1UserWorkStats(userId)
      .then((res) => {
        if (!cancelled) setStats(res.data);
      })
      .catch(() => {
        if (!cancelled) setStats(null);
      })
      .finally(() => {
        if (!cancelled) setStatsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [userId]);

  if (!user) {
    return (
      <Card className="h-full" aria-label={t("previewTitle")}>
        <CardBody>
          <PanelHeader
            title={t("previewTitle")}
            description={t("previewEmptyDescription")}
            className="mb-[var(--ecmp-panel-gap)]"
          />
          <Empty
            className="border-0 bg-transparent py-8"
            title={t("previewEmptyTitle")}
            description={t("previewEmptyDescription")}
          />
        </CardBody>
      </Card>
    );
  }

  const lastLogin = formatWhen(user.lastLoginAt, locale);
  const updated = formatWhen(user.updatedAt, locale);
  const created = formatWhen(user.createdAt, locale);

  return (
    <Card
      className="h-full transition-[box-shadow] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]"
      aria-label={t("previewTitle")}
    >
      <CardBody className="space-y-[var(--ecmp-panel-gap)]">
        <PanelHeader
          title={t("previewTitle")}
          description={t("previewDescription")}
          actions={
            <Button variant="ghost" size="sm" onClick={onClose}>
              {tCommon("close")}
            </Button>
          }
          className="mb-0"
        />

        <div className="flex items-start gap-[var(--ecmp-panel-gap)]">
          <DirectoryAvatar
            fullName={user.fullName}
            username={user.username}
            initials={initials}
            size="lg"
          />
          <div className="min-w-0">
            <p className="truncate text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
              {user.fullName}
            </p>
            <p className="truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              @{user.username}
            </p>
          </div>
        </div>

        <dl className="space-y-[var(--ecmp-panel-gap)]">
          <div>
            <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("role")}
            </dt>
            <dd className="mt-1">
              <DirectoryRoleBadge user={user} />
            </dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("unit")}
            </dt>
            <dd className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              {unitLabel}
            </dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {tCommon("status")}
            </dt>
            <dd className="mt-1">
              <Badge tone={user.isActive ? "success" : "neutral"}>
                {user.isActive ? t("statusActive") : t("statusInactive")}
              </Badge>
            </dd>
          </div>
        </dl>

        <section aria-label={t("workStats")} className="space-y-[var(--ecmp-space-8)]">
          <h4 className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
            {t("workStats")}
          </h4>
          <ul className="space-y-1 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-[var(--ecmp-panel-gap)]">
            <WorkStatRow
              label={t("workStatsCreated")}
              value={stats?.createdCount ?? null}
              loading={statsLoading}
              onClick={() =>
                router.push(
                  `/complaints?createdBy=${encodeURIComponent(user.id)}`,
                )
              }
            />
            <WorkStatRow
              label={t("workStatsEscalationRequested")}
              value={stats?.escalationRequestedCount ?? null}
              loading={statsLoading}
              onClick={() =>
                router.push(
                  `/complaints?createdBy=${encodeURIComponent(user.id)}&intakeDisposition=ESCALATED`,
                )
              }
            />
            <WorkStatRow
              label={t("workStatsEscalationApproved")}
              value={stats?.escalationApprovedCount ?? null}
              loading={statsLoading}
              onClick={() =>
                router.push(
                  `/complaints?decidedBy=${encodeURIComponent(user.id)}&intakeDisposition=ESCALATE_APPROVED`,
                )
              }
            />
            <WorkStatRow
              label={t("workStatsEscalationRejected")}
              value={stats?.escalationRejectedCount ?? null}
              loading={statsLoading}
              onClick={() =>
                router.push(
                  `/complaints?decidedBy=${encodeURIComponent(user.id)}&intakeDisposition=ESCALATE_REJECTED`,
                )
              }
            />
          </ul>
        </section>

        {canUpdateStatus || canUpdateRole ? (
          <div className="flex flex-wrap gap-2">
            {canUpdateRole ? (
              <Button
                variant="outline"
                disabled={updatingStatus}
                onClick={() => onRequestRoleChange(user)}
              >
                {t("changeRole")}
              </Button>
            ) : null}
            {canUpdateStatus ? (
              <Button
                variant={user.isActive ? "outline" : "primary"}
                disabled={updatingStatus}
                onClick={() => onRequestStatusChange(user)}
              >
                {updatingStatus
                  ? t("updating")
                  : user.isActive
                    ? t("deactivate")
                    : t("activate")}
              </Button>
            ) : null}
          </div>
        ) : null}

        <section aria-label={t("recentActivity")} className="space-y-[var(--ecmp-space-8)]">
          <h4 className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
            {t("recentActivity")}
          </h4>
          <ul className="space-y-[var(--ecmp-space-8)] rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-[var(--ecmp-panel-gap)]">
            <li className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              <span className="text-ecmp-text-primary">{t("lastLogin")}: </span>
              {lastLogin ?? tCommon("emDash")}
            </li>
            <li className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              <span className="text-ecmp-text-primary">{t("lastUpdated")}: </span>
              {updated ?? tCommon("emDash")}
            </li>
            <li className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              <span className="text-ecmp-text-primary">{t("created")}: </span>
              {created ?? tCommon("emDash")}
            </li>
          </ul>
        </section>
      </CardBody>
    </Card>
  );
}
