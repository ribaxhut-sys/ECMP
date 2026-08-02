"use client";

import { useTranslations } from "next-intl";
import { SystemSettingsManagement } from "@/features/settings";
import { SlaPolicyManagement } from "@/features/sla";
import { LanguageSwitcher } from "@/shared/i18n/LanguageSwitcher";
import {
  Card,
  CardBody,
  PageContainer,
  PageHeader,
  SectionHeader,
} from "@/shared/ui";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("pageDescription")}
      />

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("language")}
          description={t("languageDescription")}
        />
        <Card>
          <CardBody>
            <LanguageSwitcher variant="full" id="settings-language-switcher" />
          </CardBody>
        </Card>
      </section>

      <SystemSettingsManagement />
      <SlaPolicyManagement />
    </PageContainer>
  );
}
