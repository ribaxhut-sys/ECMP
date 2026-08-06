"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { SlaPolicyManagement } from "@/features/sla";
import { LanguageSwitcher } from "@/shared/i18n/LanguageSwitcher";
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  Empty,
  Input,
  PageContainer,
  PageHeader,
  PanelHeader,
  SectionHeader,
} from "@/shared/ui";
import { ConfigurationHelpPanel } from "./ConfigurationHelpPanel";
import { ConfigurationNav } from "./ConfigurationNav";
import { SystemSettingsManagement } from "./SystemSettingsManagement";
import { UnavailableSettingCard } from "./UnavailableSettingCard";
import {
  CONFIGURATION_SECTIONS,
  matchesSearch,
  type ConfigurationSection,
} from "./configurationSections";

type UnavailableItem = {
  id: string;
  section: ConfigurationSection;
  titleKey:
    | "groupLocalization"
    | "groupRegional"
    | "groupDateTime"
    | "groupThresholds"
    | "groupEscalation"
    | "groupEmail"
    | "groupWebhook"
    | "groupAlerts"
    | "groupPassword"
    | "groupSession"
    | "groupAccess"
    | "groupAssignment"
    | "groupResolution"
    | "groupWorkflowEscalation"
    | "groupDeveloper"
    | "groupExperimental";
  descriptionKey:
    | "groupLocalizationDescription"
    | "groupRegionalDescription"
    | "groupDateTimeDescription"
    | "groupThresholdsDescription"
    | "groupEscalationDescription"
    | "groupEmailDescription"
    | "groupWebhookDescription"
    | "groupAlertsDescription"
    | "groupPasswordDescription"
    | "groupSessionDescription"
    | "groupAccessDescription"
    | "groupAssignmentDescription"
    | "groupResolutionDescription"
    | "groupWorkflowEscalationDescription"
    | "groupDeveloperDescription"
    | "groupExperimentalDescription";
};

const UNAVAILABLE_ITEMS: readonly UnavailableItem[] = [
  {
    id: "regional",
    section: "general",
    titleKey: "groupRegional",
    descriptionKey: "groupRegionalDescription",
  },
  {
    id: "datetime",
    section: "general",
    titleKey: "groupDateTime",
    descriptionKey: "groupDateTimeDescription",
  },
  {
    id: "thresholds",
    section: "sla",
    titleKey: "groupThresholds",
    descriptionKey: "groupThresholdsDescription",
  },
  {
    id: "sla-escalation",
    section: "sla",
    titleKey: "groupEscalation",
    descriptionKey: "groupEscalationDescription",
  },
  {
    id: "email",
    section: "notifications",
    titleKey: "groupEmail",
    descriptionKey: "groupEmailDescription",
  },
  {
    id: "webhook",
    section: "notifications",
    titleKey: "groupWebhook",
    descriptionKey: "groupWebhookDescription",
  },
  {
    id: "alerts",
    section: "notifications",
    titleKey: "groupAlerts",
    descriptionKey: "groupAlertsDescription",
  },
  {
    id: "session",
    section: "security",
    titleKey: "groupSession",
    descriptionKey: "groupSessionDescription",
  },
  {
    id: "access",
    section: "security",
    titleKey: "groupAccess",
    descriptionKey: "groupAccessDescription",
  },
  {
    id: "assignment",
    section: "workflow",
    titleKey: "groupAssignment",
    descriptionKey: "groupAssignmentDescription",
  },
  {
    id: "resolution",
    section: "workflow",
    titleKey: "groupResolution",
    descriptionKey: "groupResolutionDescription",
  },
  {
    id: "workflow-escalation",
    section: "workflow",
    titleKey: "groupWorkflowEscalation",
    descriptionKey: "groupWorkflowEscalationDescription",
  },
];

export function ConfigurationCenter() {
  const router = useRouter();
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const [activeSection, setActiveSection] =
    useState<ConfigurationSection>("general");
  const [searchQuery, setSearchQuery] = useState("");

  const sectionMeta: Record<
    ConfigurationSection,
    { title: string; description: string; keywords: string }
  > = {
    general: {
      title: t("sectionGeneralTitle"),
      description: t("sectionGeneralDescription"),
      keywords: t("sectionGeneralKeywords"),
    },
    sla: {
      title: t("sectionSlaTitle"),
      description: t("sectionSlaDescription"),
      keywords: t("sectionSlaKeywords"),
    },
    notifications: {
      title: t("sectionNotificationsTitle"),
      description: t("sectionNotificationsDescription"),
      keywords: t("sectionNotificationsKeywords"),
    },
    security: {
      title: t("sectionSecurityTitle"),
      description: t("sectionSecurityDescription"),
      keywords: t("sectionSecurityKeywords"),
    },
    workflow: {
      title: t("sectionWorkflowTitle"),
      description: t("sectionWorkflowDescription"),
      keywords: t("sectionWorkflowKeywords"),
    },
    advanced: {
      title: t("sectionAdvancedTitle"),
      description: t("sectionAdvancedDescription"),
      keywords: t("sectionAdvancedKeywords"),
    },
  };

  const visibleSections = useMemo(() => {
    if (!searchQuery.trim()) return CONFIGURATION_SECTIONS;

    const metaBySection: Record<
      ConfigurationSection,
      { title: string; description: string; keywords: string }
    > = {
      general: {
        title: t("sectionGeneralTitle"),
        description: t("sectionGeneralDescription"),
        keywords: t("sectionGeneralKeywords"),
      },
      sla: {
        title: t("sectionSlaTitle"),
        description: t("sectionSlaDescription"),
        keywords: t("sectionSlaKeywords"),
      },
      notifications: {
        title: t("sectionNotificationsTitle"),
        description: t("sectionNotificationsDescription"),
        keywords: t("sectionNotificationsKeywords"),
      },
      security: {
        title: t("sectionSecurityTitle"),
        description: t("sectionSecurityDescription"),
        keywords: t("sectionSecurityKeywords"),
      },
      workflow: {
        title: t("sectionWorkflowTitle"),
        description: t("sectionWorkflowDescription"),
        keywords: t("sectionWorkflowKeywords"),
      },
      advanced: {
        title: t("sectionAdvancedTitle"),
        description: t("sectionAdvancedDescription"),
        keywords: t("sectionAdvancedKeywords"),
      },
    };

    return CONFIGURATION_SECTIONS.filter((section) => {
      const meta = metaBySection[section];
      const unavailableMatch = UNAVAILABLE_ITEMS.some(
        (item) =>
          item.section === section &&
          matchesSearch(searchQuery, t(item.titleKey), t(item.descriptionKey)),
      );
      return (
        matchesSearch(
          searchQuery,
          meta.title,
          meta.description,
          meta.keywords,
        ) || unavailableMatch
      );
    });
  }, [searchQuery, t]);

  useEffect(() => {
    if (!visibleSections.includes(activeSection) && visibleSections[0]) {
      setActiveSection(visibleSections[0]);
    }
  }, [activeSection, visibleSections]);

  const unavailableForSection = UNAVAILABLE_ITEMS.filter((item) => {
    if (item.section !== activeSection) return false;
    return matchesSearch(
      searchQuery,
      t(item.titleKey),
      t(item.descriptionKey),
    );
  });

  const meta = sectionMeta[activeSection];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("pageDescription")}
      />

      <div className="max-w-xl">
        <Input
          name="configurationSearch"
          label={t("searchLabel")}
          placeholder={t("searchPlaceholder")}
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
          helper={t("searchHelper")}
        />
      </div>

      {visibleSections.length === 0 ? (
        <Empty
          title={t("searchEmptyTitle")}
          description={t("searchEmptyDescription")}
          primaryAction={{
            label: t("clearSearch"),
            onClick: () => setSearchQuery(""),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 gap-[var(--ecmp-section-gap)] xl:grid-cols-12">
          <div className="xl:col-span-3">
            <ConfigurationNav
              activeSection={activeSection}
              onSelect={setActiveSection}
              visibleSections={visibleSections}
            />
          </div>

          <div className="min-w-0 space-y-[var(--ecmp-section-gap)] xl:col-span-6">
            <section
              role="tabpanel"
              id={`settings-panel-${activeSection}`}
              aria-labelledby={`settings-tab-${activeSection}`}
              className="space-y-[var(--ecmp-panel-gap)]"
            >
              <SectionHeader
                title={meta.title}
                description={meta.description}
              />

              {activeSection === "general" ? (
                <div className="space-y-[var(--ecmp-card-gap)]">
                  <Card>
                    <CardHeader
                      action={<Badge tone="success">{t("statusConfigured")}</Badge>}
                    >
                      <PanelHeader
                        title={t("groupLocalization")}
                        description={t("groupLocalizationDescription")}
                        className="mb-0 border-0 pb-0"
                      />
                    </CardHeader>
                    <CardBody>
                      <LanguageSwitcher
                        variant="full"
                        id="settings-language-switcher"
                      />
                    </CardBody>
                  </Card>
                  <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2">
                    {unavailableForSection.map((item) => (
                      <UnavailableSettingCard
                        key={item.id}
                        title={t(item.titleKey)}
                        description={t(item.descriptionKey)}
                      />
                    ))}
                  </div>
                </div>
              ) : null}

              {activeSection === "sla" ? (
                <div className="space-y-[var(--ecmp-card-gap)]">
                  <SlaPolicyManagement searchQuery={searchQuery} />
                  {unavailableForSection.length > 0 ? (
                    <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2">
                      {unavailableForSection.map((item) => (
                        <UnavailableSettingCard
                          key={item.id}
                          title={t(item.titleKey)}
                          description={t(item.descriptionKey)}
                        />
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : null}

              {activeSection === "notifications" ? (
                <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2">
                  {unavailableForSection.length > 0 ? (
                    unavailableForSection.map((item) => (
                      <UnavailableSettingCard
                        key={item.id}
                        title={t(item.titleKey)}
                        description={t(item.descriptionKey)}
                      />
                    ))
                  ) : (
                    <Empty
                      title={t("searchEmptyTitle")}
                      description={t("searchEmptyDescription")}
                      primaryAction={{
                        label: t("clearSearch"),
                        onClick: () => setSearchQuery(""),
                      }}
                    />
                  )}
                </div>
              ) : null}

              {activeSection === "security" ? (
                <div className="space-y-[var(--ecmp-card-gap)]">
                  <Card>
                    <CardHeader
                      action={
                        <Badge tone="warning">{t("statusNeedsReview")}</Badge>
                      }
                    >
                      <PanelHeader
                        title={t("groupPassword")}
                        description={t("groupPasswordDescription")}
                        className="mb-0 border-0 pb-0"
                      />
                    </CardHeader>
                    <CardBody className="space-y-[var(--ecmp-panel-gap)]">
                      <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                        {t("securityPasswordGuidance")}
                      </p>
                      <Button
                        type="button"
                        variant="outline"
                        className="min-h-[var(--ecmp-touch-min)]"
                        onClick={() => router.push("/profile/security")}
                      >
                        {t("openProfileSecurity")}
                      </Button>
                    </CardBody>
                  </Card>
                  <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2">
                    {unavailableForSection.map((item) => (
                      <UnavailableSettingCard
                        key={item.id}
                        title={t(item.titleKey)}
                        description={t(item.descriptionKey)}
                      />
                    ))}
                  </div>
                </div>
              ) : null}

              {activeSection === "workflow" ? (
                <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2">
                  {unavailableForSection.length > 0 ? (
                    unavailableForSection.map((item) => (
                      <UnavailableSettingCard
                        key={item.id}
                        title={t(item.titleKey)}
                        description={t(item.descriptionKey)}
                      />
                    ))
                  ) : (
                    <Empty
                      title={t("searchEmptyTitle")}
                      description={t("searchEmptyDescription")}
                      primaryAction={{
                        label: t("clearSearch"),
                        onClick: () => setSearchQuery(""),
                      }}
                    />
                  )}
                </div>
              ) : null}

              {activeSection === "advanced" ? (
                <div className="space-y-[var(--ecmp-card-gap)]">
                  <SystemSettingsManagement
                    searchQuery={searchQuery}
                    onClearSearch={() => setSearchQuery("")}
                  />
                  {unavailableForSection.length > 0 ? (
                    <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2">
                      {unavailableForSection.map((item) => (
                        <UnavailableSettingCard
                          key={item.id}
                          title={t(item.titleKey)}
                          description={t(item.descriptionKey)}
                        />
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : null}
            </section>
          </div>

          <div className="xl:col-span-3">
            <ConfigurationHelpPanel section={activeSection} />
          </div>
        </div>
      )}
    </PageContainer>
  );
}
