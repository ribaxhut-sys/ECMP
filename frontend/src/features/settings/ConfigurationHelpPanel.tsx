"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, PanelHeader } from "@/shared/ui";
import type { ConfigurationSection } from "./configurationSections";

export function ConfigurationHelpPanel({
  section,
}: {
  section: ConfigurationSection;
}) {
  const t = useTranslations("settings");

  const copy: Record<
    ConfigurationSection,
    {
      description: string;
      status: string;
      statusTone: "success" | "warning" | "neutral" | "info";
      impact: string;
      bestPractice: string;
    }
  > = {
    general: {
      description: t("helpGeneralDescription"),
      status: t("helpStatusReady"),
      statusTone: "success",
      impact: t("helpGeneralImpact"),
      bestPractice: t("helpGeneralBestPractice"),
    },
    preferences: {
      description: t("helpPreferencesDescription"),
      status: t("helpStatusPersonal"),
      statusTone: "info",
      impact: t("helpPreferencesImpact"),
      bestPractice: t("helpPreferencesBestPractice"),
    },
    sla: {
      description: t("helpSlaDescription"),
      status: t("helpStatusActivePolicies"),
      statusTone: "info",
      impact: t("helpSlaImpact"),
      bestPractice: t("helpSlaBestPractice"),
    },
    notifications: {
      description: t("helpNotificationsDescription"),
      status: t("statusDisabled"),
      statusTone: "neutral",
      impact: t("helpNotificationsImpact"),
      bestPractice: t("helpNotificationsBestPractice"),
    },
    security: {
      description: t("helpSecurityDescription"),
      status: t("helpStatusProfileLinked"),
      statusTone: "warning",
      impact: t("helpSecurityImpact"),
      bestPractice: t("helpSecurityBestPractice"),
    },
    workflow: {
      description: t("helpWorkflowDescription"),
      status: t("statusDisabled"),
      statusTone: "neutral",
      impact: t("helpWorkflowImpact"),
      bestPractice: t("helpWorkflowBestPractice"),
    },
    advanced: {
      description: t("helpAdvancedDescription"),
      status: t("helpStatusOperational"),
      statusTone: "info",
      impact: t("helpAdvancedImpact"),
      bestPractice: t("helpAdvancedBestPractice"),
    },
  };

  const active = copy[section];

  return (
    <aside aria-label={t("helpPanelTitle")}>
      <Card className="sticky top-4">
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          <PanelHeader
            title={t("helpPanelTitle")}
            description={t("helpPanelSubtitle")}
            className="mb-0"
          />

          <div className="space-y-[var(--ecmp-space-8)]">
            <p className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("helpDescription")}
            </p>
            <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
              {active.description}
            </p>
          </div>

          <div className="space-y-[var(--ecmp-space-8)]">
            <p className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("helpCurrentStatus")}
            </p>
            <Badge tone={active.statusTone}>{active.status}</Badge>
          </div>

          <div className="space-y-[var(--ecmp-space-8)]">
            <p className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("helpImpact")}
            </p>
            <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              {active.impact}
            </p>
          </div>

          <div className="space-y-[var(--ecmp-space-8)] rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-[var(--ecmp-panel-gap)]">
            <p className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("helpBestPractice")}
            </p>
            <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              {active.bestPractice}
            </p>
          </div>
        </CardBody>
      </Card>
    </aside>
  );
}
