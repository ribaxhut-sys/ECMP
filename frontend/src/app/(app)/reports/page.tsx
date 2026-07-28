"use client";

import { useTranslations } from "next-intl";
import {
  Empty,
  PageContainer,
  PageHeader,
} from "@/shared/ui";

export default function ReportsPage() {
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");

  return (
    <PageContainer>
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("description")}
      />
      <Empty
        title={t("moduleTitle")}
        description={t("placeholder")}
      />
    </PageContainer>
  );
}
