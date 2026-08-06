"use client";

import { useTranslations } from "next-intl";
import {
  Badge,
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
} from "@/shared/ui";

export function UnavailableSettingCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  const t = useTranslations("settings");

  return (
    <Card className="h-full opacity-95">
      <CardHeader action={<Badge tone="neutral">{t("statusDisabled")}</Badge>}>
        <PanelHeader
          title={title}
          description={description}
          className="mb-0 border-0 pb-0"
        />
      </CardHeader>
      <CardBody>
        <Empty
          className="border-0 bg-transparent px-2 py-6"
          title={t("unavailableTitle")}
          description={t("unavailableDescription")}
        />
      </CardBody>
    </Card>
  );
}
