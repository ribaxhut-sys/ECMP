"use client";

import { useTranslations } from "next-intl";
import { Select, type SelectOption } from "@/shared/ui";
import { MOCK_UNITS } from "../mock/assignmentRepository";

export interface UnitSelectorProps {
  value: string;
  onChange: (unitId: string) => void;
  disabled?: boolean;
  error?: string;
}

/** Destination unit selector for SCR-WS-09 (B1 mock). */
export function UnitSelector({
  value,
  onChange,
  disabled,
  error,
}: UnitSelectorProps) {
  const t = useTranslations("supervisorAssign");

  const options: SelectOption[] = MOCK_UNITS.map((unit) => ({
    value: unit.id,
    label: t("unitOption", {
      name: unit.name,
      workload: unit.openWorkload,
    }),
  }));

  return (
    <Select
      id="b1-unit-selector"
      name="unitId"
      label={t("unitLabel")}
      description={t("unitDescription")}
      placeholder={t("unitPlaceholder")}
      options={options}
      value={value}
      disabled={disabled}
      error={error}
      required
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
