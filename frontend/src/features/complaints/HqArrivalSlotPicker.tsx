"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  fetchHqScheduleAvailability,
  type HqScheduleDayAvailability,
} from "@/lib/api/hqSchedule";
import { Alert, Select } from "@/shared/ui";

const weekdayFormatter = new Intl.DateTimeFormat("id-ID", { weekday: "long" });

/** "2026-08-18" -> "18-08-2026 (Selasa)" for display; API params stay ISO. */
function formatDateOption(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  if (!year || !month || !day) return isoDate;
  const weekday = weekdayFormatter.format(new Date(`${isoDate}T00:00:00`));
  return `${day}-${month}-${year} (${weekday})`;
}

export interface HqArrivalSlotValue {
  date: string;
  time: string;
}

export interface HqArrivalSlotPickerProps {
  value: HqArrivalSlotValue | null;
  onChange: (value: HqArrivalSlotValue | null) => void;
  disabled?: boolean;
}

/**
 * Branch-facing slot picker shown inline on escalation — advisory proposal
 * only, Pusat still decides the final HQ arrival date/time.
 */
export function HqArrivalSlotPicker({
  value,
  onChange,
  disabled,
}: HqArrivalSlotPickerProps) {
  const t = useTranslations("hqSchedule");
  const [days, setDays] = useState<HqScheduleDayAvailability[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchHqScheduleAvailability()
      .then((res) => {
        if (!cancelled) setDays(res.data.days);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        {t("proposeLoading")}
      </p>
    );
  }

  if (failed) {
    return (
      <Alert
        tone="warning"
        title={t("loadError")}
        description={t("proposeUnavailableHint")}
      />
    );
  }

  const openDays = days.filter((day) => !day.closed && day.slots.length > 0);
  if (openDays.length === 0) {
    return (
      <Alert
        tone="info"
        title={t("proposeNoSlotsTitle")}
        description={t("proposeNoSlotsHint")}
      />
    );
  }

  const dateOptions = openDays.map((day) => ({
    value: day.date,
    label: formatDateOption(day.date),
  }));
  const selectedDay = openDays.find((day) => day.date === value?.date) ?? null;
  const slotOptions = (selectedDay?.slots ?? [])
    .filter((slot) => !slot.isBreak)
    .map((slot) => ({
      value: slot.startTime,
      label: `${slot.startTime}–${slot.endTime} (${t("availableCount", {
        count: slot.availableCount,
      })})`,
      disabled: slot.availableCount <= 0,
    }));

  return (
    <div className="grid gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
      <Select
        name="proposedArrivalDate"
        id="proposedArrivalDate"
        label={t("proposeDateLabel")}
        placeholder={t("proposeDatePlaceholder")}
        options={dateOptions}
        value={value?.date ?? ""}
        disabled={disabled}
        onChange={(e) => {
          const date = e.target.value;
          if (!date) {
            onChange(null);
            return;
          }
          onChange({ date, time: "" });
        }}
      />
      <Select
        name="proposedArrivalTime"
        id="proposedArrivalTime"
        label={t("proposeTimeLabel")}
        placeholder={t("proposeTimePlaceholder")}
        options={slotOptions}
        value={value?.time ?? ""}
        disabled={disabled || !value?.date}
        onChange={(e) => {
          if (!value?.date) return;
          onChange({ date: value.date, time: e.target.value });
        }}
      />
    </div>
  );
}
