"use client";

import { useTranslations } from "next-intl";
import type { UserRef } from "@/lib/api";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  PanelHeader,
} from "@/shared/ui";
import { DirectoryAvatar } from "./DirectoryAvatar";
import { DirectoryLocationBadge } from "./DirectoryLocationBadge";
import { DirectoryRoleBadge } from "./DirectoryRoleBadge";
import { formatBranch, formatWhen } from "./directoryHelpers";

export function DirectoryPreviewPanel({
  user,
  canReset,
  currentUserId,
  onResetPassword,
  onClose,
}: {
  user: UserRef | null;
  canReset: boolean;
  currentUserId: string | null | undefined;
  onResetPassword: (user: UserRef) => void;
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
  const isSelf = user.id === currentUserId;

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
            <p className="mt-1 truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {user.email}
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
              {t("branch")}
            </dt>
            <dd className="mt-1 flex flex-wrap items-center gap-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              <DirectoryLocationBadge user={user} />
              <span>{formatBranch(user.branchId, t("noDepartment"))}</span>
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

        <section aria-label={t("quickActions")} className="space-y-[var(--ecmp-space-8)]">
          <h4 className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
            {t("quickActions")}
          </h4>
          <div className="flex flex-col gap-[var(--ecmp-space-8)]">
            {canReset ? (
              <Button
                variant="outline"
                className="min-h-[var(--ecmp-touch-min)] justify-start"
                disabled={!user.isActive || isSelf}
                title={
                  isSelf
                    ? t("resetOwnPasswordHint")
                    : user.isActive
                      ? t("resetPasswordHint")
                      : t("inactiveResetHint")
                }
                onClick={() => onResetPassword(user)}
              >
                {t("resetPassword")}
              </Button>
            ) : (
              <Empty
                className="border-0 bg-transparent px-2 py-4"
                title={t("noQuickActions")}
                description={t("noQuickActionsDescription")}
              />
            )}
          </div>
        </section>
      </CardBody>
    </Card>
  );
}
