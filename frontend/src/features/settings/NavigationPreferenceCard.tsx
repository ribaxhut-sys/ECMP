"use client";

import { useTranslations } from "next-intl";
import {
  NAV_PREFERENCE_MODES,
  normalizeNavPreferenceMode,
  useNavPreference,
  type NavPreferenceMode,
} from "@/shared/navigation";
import { RadioGroup, type RadioOption } from "@/shared/ui";

const MODE_COPY: Record<
  NavPreferenceMode,
  { labelKey: string; descriptionKey: string }
> = {
  auto: {
    labelKey: "navModeAuto",
    descriptionKey: "navModeAutoDescription",
  },
  remember: {
    labelKey: "navModeRemember",
    descriptionKey: "navModeRememberDescription",
  },
  expandAll: {
    labelKey: "navModeExpandAll",
    descriptionKey: "navModeExpandAllDescription",
  },
};

/**
 * Pengaturan → Preferensi → Navigasi.
 * Personal to the signed-in user; presentation only — it never changes which
 * menus the permission filter allows.
 */
export function NavigationPreferenceCard() {
  const t = useTranslations("settings");
  const { mode, setMode } = useNavPreference();

  const options: readonly RadioOption[] = NAV_PREFERENCE_MODES.map((value) => ({
    value,
    label: (
      <span className="flex flex-col gap-0.5">
        <span className="font-medium text-ecmp-text-primary">
          {t(MODE_COPY[value].labelKey)}
        </span>
        <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {t(MODE_COPY[value].descriptionKey)}
        </span>
      </span>
    ),
  }));

  return (
    <RadioGroup
      name="navSidebarComplaints"
      label={t("navSidebarComplaintsLabel")}
      helper={t("navSidebarComplaintsHelper")}
      value={mode}
      options={options}
      onChange={(next) => setMode(normalizeNavPreferenceMode(next))}
    />
  );
}
