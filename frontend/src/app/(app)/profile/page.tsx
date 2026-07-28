"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
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
import { LanguageSwitcher } from "@/shared/i18n";

export default function ProfilePage() {
  const { user } = useAuth();
  const t = useTranslations("profile");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("description")}
      />

      <Card>
        <CardHeader>
          <CardTitle>{t("account")}</CardTitle>
          <CardDescription>{t("accountDescription")}</CardDescription>
        </CardHeader>
        <CardBody className="space-y-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
          <p>
            <span className="text-ecmp-text-secondary">{t("name")} </span>
            {user?.fullName ?? tCommon("emDash")}
          </p>
          <p>
            <span className="text-ecmp-text-secondary">{t("username")} </span>
            {user?.username ?? tCommon("emDash")}
          </p>
          <p>
            <span className="text-ecmp-text-secondary">{t("email")} </span>
            {user?.email ?? tCommon("emDash")}
          </p>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("security")}</CardTitle>
          <CardDescription>{t("securityDescription")}</CardDescription>
        </CardHeader>
        <CardBody>
          <Link
            href="/profile/security"
            className="text-ecmp-primary underline-offset-2 hover:underline"
          >
            {t("openSecurity")}
          </Link>
          <span className="mx-2 text-ecmp-text-secondary">·</span>
          <Link
            href={PASSWORD_CHANGE_ROUTE}
            className="text-ecmp-primary underline-offset-2 hover:underline"
          >
            {t("changePassword")}
          </Link>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("languageTitle")}</CardTitle>
          <CardDescription>{t("languageDescription")}</CardDescription>
        </CardHeader>
        <CardBody>
          <LanguageSwitcher variant="full" />
        </CardBody>
      </Card>
    </PageContainer>
  );
}
