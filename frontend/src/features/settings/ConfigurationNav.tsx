"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";
import {
  IconAssignments,
  IconCheck,
  IconSettings,
  IconUser,
  IconUsers,
} from "@/shared/icons";
import { cn } from "@/shared/utils";
import {
  CONFIGURATION_SECTIONS,
  type ConfigurationSection,
} from "./configurationSections";

const sectionIcon: Record<ConfigurationSection, ReactNode> = {
  general: <IconSettings className="size-4" aria-hidden />,
  preferences: <IconUser className="size-4" aria-hidden />,
  sla: <IconCheck className="size-4" aria-hidden />,
  workflow: <IconAssignments className="size-4" aria-hidden />,
  advanced: <IconUsers className="size-4" aria-hidden />,
};

export function ConfigurationNav({
  activeSection,
  onSelect,
  visibleSections,
}: {
  activeSection: ConfigurationSection;
  onSelect: (section: ConfigurationSection) => void;
  visibleSections?: readonly ConfigurationSection[];
}) {
  const t = useTranslations("settings");
  const sections = visibleSections ?? CONFIGURATION_SECTIONS;

  const labels: Record<ConfigurationSection, string> = {
    general: t("navGeneral"),
    preferences: t("navPreferences"),
    sla: t("navSlaPolicies"),
    workflow: t("navWorkflow"),
    advanced: t("navAdvanced"),
  };

  return (
    <nav
      aria-label={t("navigationLabel")}
      className="rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface p-2 shadow-ecmp-surface"
    >
      <p className="px-2 pb-2 pt-1 text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {t("navigationLabel")}
      </p>
      <ul role="tablist" aria-orientation="vertical" className="flex flex-col gap-1">
        {sections.map((section) => {
          const active = activeSection === section;
          return (
            <li key={section} role="presentation">
              <button
                type="button"
                role="tab"
                id={`settings-tab-${section}`}
                aria-selected={active}
                aria-controls={`settings-panel-${section}`}
                onClick={() => onSelect(section)}
                className={cn(
                  "relative flex w-full min-h-[var(--ecmp-touch-min)] items-center gap-2.5 rounded-[var(--ecmp-radius-button)] px-3 py-2 text-left",
                  "text-[length:var(--ecmp-font-body-small-size)] font-medium",
                  "transition-[background-color,color,box-shadow] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
                  "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]",
                  active
                    ? "bg-ecmp-primary-muted text-ecmp-primary shadow-ecmp-surface"
                    : "text-ecmp-text-secondary hover:bg-ecmp-hover hover:text-ecmp-text-primary",
                )}
              >
                {active ? (
                  <span
                    className="absolute inset-y-1.5 left-0 w-1 rounded-r-[var(--ecmp-radius-sm)] bg-ecmp-primary"
                    aria-hidden
                  />
                ) : null}
                <span
                  className={cn(
                    "flex size-8 items-center justify-center rounded-[var(--ecmp-radius-md)]",
                    active
                      ? "bg-ecmp-surface text-ecmp-primary"
                      : "bg-ecmp-surface-sunken text-ecmp-text-secondary",
                  )}
                >
                  {sectionIcon[section]}
                </span>
                <span>{labels[section]}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
