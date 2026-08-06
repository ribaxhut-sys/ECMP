"use client";

import { useTranslations } from "next-intl";
import type { UserRef } from "@/lib/api";
import { Badge, Button, Card, CardBody, Empty, PanelHeader } from "@/shared/ui";
import { DirectoryAvatar } from "./DirectoryAvatar";
import { DirectoryRoleBadge } from "./DirectoryRoleBadge";
import { formatWhen } from "./directoryHelpers";

export function DirectoryPreviewPanel({
  user,
  unitLabel,
  canUpdateStatus,
  updatingStatus,
  onRequestStatusChange,
  canUpdateRole,
  onRequestRoleChange,
  onClose,
}: {
  user: UserRef | null;
  unitLabel: string | null;
  canUpdateStatus: boolean;
  updatingStatus: boolean;
  onRequestStatusChange: (user: UserRef) => void;
  canUpdateRole: boolean;
  onRequestRoleChange: (user: UserRef) => void;
  onClose: () => void;
}) {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");

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

  const lastLogin = formatWhen(user.lastLoginAt);
  const updated = formatWhen(user.updatedAt);
  const created = formatWhen(user.createdAt);

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
