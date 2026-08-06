"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  formatIdentityBranch,
  formatIdentityWhen,
  identityInitials,
  primaryRoleLabel,
} from "@/features/auth";
import { LanguageSwitcher } from "@/shared/i18n";
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  Empty,
  PageContainer,
  PageHeader,
  PanelHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";

export default function ProfilePage() {
  const router = useRouter();
  const { user, status } = useAuth();
  const t = useTranslations("profile");
  const tCommon = useTranslations("common");

  const initials = useMemo(
    () => identityInitials(user?.fullName ?? user?.username),
    [user?.fullName, user?.username],
  );
  const roleLabel = primaryRoleLabel(user, t("roleUnassigned"));
  const branchLabel = formatIdentityBranch(user?.branchId, t("branchUnassigned"));
  const lastLogin = formatIdentityWhen(user?.lastLoginAt);
  const updatedAt = formatIdentityWhen(user?.updatedAt);

  if (status === "loading") {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <Skeleton rows={5} />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("description")}
      />

      <Card className="shadow-ecmp-raised">
        <CardBody className="flex flex-col gap-[var(--ecmp-panel-gap)] lg:flex-row lg:items-center lg:justify-between">
          <div className="flex min-w-0 items-center gap-4">
            <div
              aria-hidden
              className="flex size-16 shrink-0 items-center justify-center rounded-full bg-ecmp-primary-muted text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-primary ring-1 ring-inset ring-ecmp-primary/15"
            >
              {initials}
            </div>
            <div className="min-w-0 space-y-1">
              <p className="truncate text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
                {user?.fullName ?? tCommon("emDash")}
              </p>
              <p className="truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                @{user?.username ?? tCommon("emDash")}
              </p>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <Badge tone="info">{roleLabel}</Badge>
                <Badge tone={user?.isActive ? "success" : "neutral"}>
                  {user?.isActive ? t("statusActive") : t("statusInactive")}
                </Badge>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              className="min-h-[var(--ecmp-touch-min)]"
              onClick={() => router.push("/profile/security")}
            >
              {t("openSecurity")}
            </Button>
          </div>
        </CardBody>
      </Card>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("personalInformation")}
          description={t("personalInformationDescription")}
        />
        <Card>
          <CardBody>
            <dl className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-2">
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("name")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                  {user?.fullName ?? tCommon("emDash")}
                </dd>
              </div>
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("username")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                  {user?.username ?? tCommon("emDash")}
                </dd>
              </div>
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("email")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                  {user?.email ?? tCommon("emDash")}
                </dd>
              </div>
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("role")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                  {roleLabel}
                </dd>
              </div>
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("branch")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                  {branchLabel}
                </dd>
              </div>
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("accountStatus")}
                </dt>
                <dd>
                  <Badge tone={user?.isActive ? "success" : "neutral"}>
                    {user?.isActive ? t("statusActive") : t("statusInactive")}
                  </Badge>
                </dd>
              </div>
            </dl>
          </CardBody>
        </Card>
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("security")}
          description={t("securityDescription")}
        />
        <Card>
          <CardHeader>
            <PanelHeader
              title={t("securitySummaryTitle")}
              description={t("securitySummaryDescription")}
              className="mb-0 border-0 pb-0"
            />
          </CardHeader>
          <CardBody className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              className="min-h-[var(--ecmp-touch-min)]"
              onClick={() => router.push("/profile/security")}
            >
              {t("openSecurity")}
            </Button>
          </CardBody>
        </Card>
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("recentActivity")}
          description={t("recentActivityDescription")}
        />
        <Card>
          <CardBody>
            {lastLogin || updatedAt ? (
              <ul className="space-y-3">
                <li className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  <span className="text-ecmp-text-primary">{t("lastLogin")}: </span>
                  {lastLogin ?? tCommon("emDash")}
                </li>
                <li className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  <span className="text-ecmp-text-primary">{t("lastUpdated")}: </span>
                  {updatedAt ?? tCommon("emDash")}
                </li>
              </ul>
            ) : (
              <Empty
                className="border-0 bg-transparent py-6"
                title={t("recentActivityEmptyTitle")}
                description={t("recentActivityEmptyDescription")}
                primaryAction={{
                  label: t("refreshProfile"),
                  onClick: () => router.refresh(),
                }}
                secondaryAction={{
                  label: t("openSecurity"),
                  onClick: () => router.push("/profile/security"),
                }}
              />
            )}
          </CardBody>
        </Card>
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("languageTitle")}
          description={t("languageDescription")}
        />
        <Card>
          <CardBody>
            <LanguageSwitcher variant="full" />
          </CardBody>
        </Card>
      </section>
    </PageContainer>
  );
}
