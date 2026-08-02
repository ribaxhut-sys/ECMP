"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth";
import { cn } from "@/shared/utils";
import {
  Card,
  CardBody,
  PageContainer,
  PageHeader,
  SectionHeader,
} from "@/shared/ui";
import { LanguageSwitcher } from "@/shared/i18n";

const linkButtonClass = cn(
  "inline-flex min-h-[var(--ecmp-touch-min)] items-center justify-center rounded-[var(--ecmp-radius-button)]",
  "border border-ecmp-border bg-ecmp-surface px-3 font-medium",
  "text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary shadow-ecmp-surface",
  "hover:border-ecmp-secondary hover:bg-ecmp-hover hover:shadow-ecmp-raised",
  "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]",
);

export default function ProfilePage() {
  const { user } = useAuth();
  const t = useTranslations("profile");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("description")}
      />

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("account")}
          description={t("accountDescription")}
        />
        <Card>
          <CardBody>
            <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("name")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {user?.fullName ?? tCommon("emDash")}
                </dd>
              </div>
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("username")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {user?.username ?? tCommon("emDash")}
                </dd>
              </div>
              <div className="space-y-1 sm:col-span-2">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("email")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {user?.email ?? tCommon("emDash")}
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
          <CardBody>
            <div className="flex flex-wrap gap-2">
              <Link href="/profile/security" className={linkButtonClass}>
                {t("openSecurity")}
              </Link>
              <Link href={PASSWORD_CHANGE_ROUTE} className={linkButtonClass}>
                {t("changePassword")}
              </Link>
            </div>
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
