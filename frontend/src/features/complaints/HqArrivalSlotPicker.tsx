"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  fetchHqScheduleAvailability,
  type HqScheduleDayAvailability,
} from "@/lib/api/hqSchedule";
import { Alert, Input, Select } from "@/shared/ui";
import { toLocalDateKey } from "@/shared/utils/datetime";

const MAX_LEAD_DAYS = 60;

const weekdayFormatter = new Intl.DateTimeFormat("id-ID", { weekday: "long" });

/** "2026-08-18" -> "Selasa, 18-08-2026" for display; API params stay ISO. */
function formatDateLabel(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  if (!year || !month || !day) return isoDate;
  const weekday = weekdayFormatter.format(new Date(`${isoDate}T00:00:00`));
  return `${weekday}, ${day}-${month}-${year}`;
}

function addDays(date: Date, days: number): Date {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
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
 * only, Pusat still decides the final HQ arrival date/time. The date input
 * is free-pick (not limited to "this week") so a taxpayer asking for a slot
 * weeks out can still be proposed one; only that single day is fetched.
 */
export function HqArrivalSlotPicker({
  value,
  onChange,
  disabled,
}: HqArrivalSlotPickerProps) {
  const t = useTranslations("hqSchedule");
  const [day, setDay] = useState<HqScheduleDayAvailability | null>(null);
  const [dayLoading, setDayLoading] = useState(false);
  const [dayFailed, setDayFailed] = useState(false);

  const minDate = useMemo(() => toLocalDateKey(addDays(new Date(), 1)), []);
  const maxDate = useMemo(
    () => toLocalDateKey(addDays(new Date(), MAX_LEAD_DAYS)),
    [],
  );

  const selectedDate = value?.date ?? "";

  useEffect(() => {
    if (!selectedDate) {
      setDay(null);
      setDayFailed(false);
      return;
    }
    let cancelled = false;
    setDayLoading(true);
    setDayFailed(false);
    fetchHqScheduleAvailability(selectedDate, selectedDate)
      .then((res) => {
        if (!cancelled) setDay(res.data.days[0] ?? null);
      })
      .catch(() => {
        if (!cancelled) setDayFailed(true);
      })
      .finally(() => {
        if (!cancelled) setDayLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedDate]);

  const slotOptions = (day?.slots ?? [])
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
      <div>
        <Input
          type="date"
          name="proposedArrivalDate"
          id="proposedArrivalDate"
          label={t("proposeDateLabel")}
          min={minDate}
          max={maxDate}
          value={selectedDate}
          disabled={disabled}
          onChange={(e) => {
            const date = e.target.value;
            onChange(date ? { date, time: "" } : null);
          }}
        />
        {selectedDate && (
          <p className="mt-1 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {formatDateLabel(selectedDate)}
          </p>
        )}
      </div>

      {!selectedDate ? null : dayLoading ? (
        <p className="self-end text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("proposeLoading")}
        </p>
      ) : dayFailed ? (
        <Alert
          tone="warning"
          title={t("loadError")}
          description={t("proposeUnavailableHint")}
        />
      ) : !day || day.closed || slotOptions.length === 0 ? (
        <Alert
          tone="info"
          title={t("proposeNoSlotsTitle")}
          description={t("proposeNoSlotsHint")}
        />
      ) : (
        <Select
          name="proposedArrivalTime"
          id="proposedArrivalTime"
          label={t("proposeTimeLabel")}
          placeholder={t("proposeTimePlaceholder")}
          options={slotOptions}
          value={value?.time ?? ""}
          disabled={disabled}
          onChange={(e) => {
            if (!selectedDate) return;
            onChange({ date: selectedDate, time: e.target.value });
          }}
        />
      )}
    </div>
  );
}
