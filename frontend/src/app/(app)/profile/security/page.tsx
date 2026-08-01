"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth";
import {
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  PageContainer,
  PageHeader,
} from "@/shared/ui";

export default function ProfileSecurityPage() {
  const t = useTranslations("profile");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("securityTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/profile" },
          { label: t("securityTitle") },
        ]}
        description={t("securityPageDescription")}
      />

      <Card>
        <CardHeader>
          <CardTitle>{t("passwordSection")}</CardTitle>
          <CardDescription>{t("passwordSectionDescription")}</CardDescription>
        </CardHeader>
        <CardBody>
          <Link
            href={PASSWORD_CHANGE_ROUTE}
            className="text-ecmp-primary underline-offset-2 hover:underline"
          >
            {t("changePassword")}
          </Link>
        </CardBody>
      </Card>
    </PageContainer>
  );
}
