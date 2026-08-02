"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth";
import { cn } from "@/shared/utils";
import {
  Card,
  CardBody,
  PageContainer,
  PageHeader,
  SectionHeader,
} from "@/shared/ui";

const linkButtonClass = cn(
  "inline-flex min-h-[var(--ecmp-touch-min)] items-center justify-center rounded-[var(--ecmp-radius-button)]",
  "border border-ecmp-border bg-ecmp-surface px-3 font-medium",
  "text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary shadow-ecmp-surface",
  "hover:border-ecmp-secondary hover:bg-ecmp-hover hover:shadow-ecmp-raised",
  "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]",
);

export default function ProfileSecurityPage() {
  const t = useTranslations("profile");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("securityTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/profile" },
          { label: t("securityTitle") },
        ]}
        description={t("securityPageDescription")}
      />

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("passwordSection")}
          description={t("passwordSectionDescription")}
        />
        <Card>
          <CardBody>
            <Link href={PASSWORD_CHANGE_ROUTE} className={linkButtonClass}>
              {t("changePassword")}
            </Link>
          </CardBody>
        </Card>
      </section>
    </PageContainer>
  );
}
