"use client";

import { useTranslations } from "next-intl";
import { SystemSettingsManagement } from "@/features/settings";
import { SlaPolicyManagement } from "@/features/sla";
import { LanguageSwitcher } from "@/shared/i18n/LanguageSwitcher";
import {
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  PageContainer,
  PageHeader,
} from "@/shared/ui";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");

  return (
    <PageContainer>
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("pageDescription")}
      />
      <div style={{ display: "grid", gap: "1.5rem" }}>
        <Card>
          <CardHeader>
            <CardTitle>{t("language")}</CardTitle>
            <CardDescription>{t("languageDescription")}</CardDescription>
          </CardHeader>
          <CardBody>
            <LanguageSwitcher variant="full" id="settings-language-switcher" />
          </CardBody>
        </Card>
        <SystemSettingsManagement />
        <SlaPolicyManagement />
      </div>
    </PageContainer>
  );
}
