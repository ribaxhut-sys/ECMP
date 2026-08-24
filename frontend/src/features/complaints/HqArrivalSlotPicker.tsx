"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  fetchHqScheduleAvailability,
  fetchHqScheduleAvailabilityDetail,
  fetchHqScheduleHolidays,
  type HqScheduleDayAvailability,
  type HqScheduleSlotAvailability,
} from "@/lib/api/hqSchedule";
import { Alert, DatePicker, Select } from "@/shared/ui";
import { toLocalDateKey } from "@/shared/utils/datetime";

const MAX_LEAD_DAYS = 60;

function addDays(date: Date, days: number): Date {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
}

function isSlotStartFuture(date: string, startTime: string, nowMs: number): boolean {
  const start = new Date(`${date}T${startTime}:00`).getTime();
  return Number.isFinite(start) && start > nowMs;
}

function unitRemaining(
  slot: HqScheduleSlotAvailability,
  destinationUnitCode: string,
): number | null {
  const needle = destinationUnitCode.trim().toUpperCase();
  const unit = (slot.units ?? []).find(
    (row) => row.unitCode.trim().toUpperCase() === needle,
  );
  return unit ? unit.availableCount : null;
}

export interface HqArrivalSlotValue {
  date: string;
  time: string;
}

export interface HqArrivalSlotPickerProps {
  value: HqArrivalSlotValue | null;
  onChange: (value: HqArrivalSlotValue | null) => void;
  disabled?: boolean;
  /**
   * When set, load the Pusat detail grid and label each slot with that
   * unit's remaining quota. Empty string waits for the caller to pick a unit.
   */
  destinationUnitCode?: string | null;
  /**
   * Pusat may schedule past a unit's quota (authority stays with Pusat).
   * Full slots stay selectable; a warning is shown instead of disabling.
   */
  allowOverCapacity?: boolean;
}

/**
 * Branch-facing slot picker shown inline on escalation — advisory proposal
 * only, Pusat still decides the final HQ arrival date/time. The date input
 * is free-pick (not limited to "this week") so a taxpayer asking for a slot
 * weeks out can still be proposed one; only that single day is fetched.
 *
 * With ``destinationUnitCode`` + ``allowOverCapacity``, the same control is
 * reused on the Pusat accept/schedule dialog so CRO sees per-unit remaining
 * before confirming.
 */
export function HqArrivalSlotPicker({
  value,
  onChange,
  disabled,
  destinationUnitCode,
  allowOverCapacity = false,
}: HqArrivalSlotPickerProps) {
  const t = useTranslations("hqSchedule");
  const [day, setDay] = useState<HqScheduleDayAvailability | null>(null);
  const [dayLoading, setDayLoading] = useState(false);
  const [dayFailed, setDayFailed] = useState(false);
  const [nowMs, setNowMs] = useState(() => Date.now());
  const [holidayDates, setHolidayDates] = useState<string[]>([]);

  const minDate = useMemo(() => toLocalDateKey(new Date()), []);
  const maxDate = useMemo(
    () => toLocalDateKey(addDays(new Date(), MAX_LEAD_DAYS)),
    [],
  );

  useEffect(() => {
    let cancelled = false;
    fetchHqScheduleHolidays(minDate, maxDate)
      .then((res) => {
        if (!cancelled) setHolidayDates(res.data.map((h) => h.holidayDate));
      })
      .catch(() => {
        // Holiday markers are advisory only — the backend still rejects a
        // closed day on submit, so a failed fetch just skips the hint.
      });
    return () => {
      cancelled = true;
    };
  }, [minDate, maxDate]);

  const selectedDate = value?.date ?? "";
  const pusatMode = destinationUnitCode !== undefined && destinationUnitCode !== null;
  const destinationReady = Boolean(destinationUnitCode?.trim());
  const needsDestinationFirst = pusatMode && !destinationReady;

  useEffect(() => {
    const id = setInterval(() => setNowMs(Date.now()), 60_000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!selectedDate || needsDestinationFirst) {
      setDay(null);
      setDayFailed(false);
      return;
    }
    let cancelled = false;
    setDayLoading(true);
    setDayFailed(false);
    const fetchDay = pusatMode
      ? fetchHqScheduleAvailabilityDetail
      : fetchHqScheduleAvailability;
    fetchDay(selectedDate, selectedDate)
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
  }, [selectedDate, pusatMode, needsDestinationFirst, destinationUnitCode]);

  const slotOptions = (day?.slots ?? [])
    .filter((slot) => !slot.isBreak)
    .map((slot) => {
      const remaining = destinationReady
        ? unitRemaining(slot, destinationUnitCode!)
        : null;
      const count =
        remaining !== null ? remaining : slot.bookableCount;
      const future = isSlotStartFuture(selectedDate, slot.startTime, nowMs);
      const overCapacity =
        allowOverCapacity && destinationReady && remaining !== null && remaining <= 0;
      const selectable = allowOverCapacity
        ? future
        : slot.bookable && (remaining === null || remaining > 0);
      return {
        value: slot.startTime,
        label: `${slot.startTime}–${slot.endTime} (${t("availableCount", {
          count,
        })})`,
        disabled: !selectable,
        overCapacity,
      };
    });

  const selectedOverCapacity = Boolean(
    value?.time &&
      slotOptions.find((opt) => opt.value === value.time)?.overCapacity,
  );

  return (
    <div className="flex flex-wrap gap-[var(--ecmp-form-gap)]">
      <div className="w-full sm:w-[180px]">
        <DatePicker
          name="proposedArrivalDate"
          id="proposedArrivalDate"
          label={t("proposeDateLabel")}
          helper={t("proposeDateHolidayHint")}
          min={minDate}
          max={maxDate}
          disabledWeekdays={[0, 6]}
          disabledDates={holidayDates}
          value={selectedDate}
          disabled={disabled || needsDestinationFirst}
          onChange={(date) => onChange(date ? { date, time: "" } : null)}
        />
      </div>

      {needsDestinationFirst ? (
        <p className="w-full text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("pickDestinationFirst")}
        </p>
      ) : !selectedDate ? null : (
        <div className="w-full min-w-0 sm:w-[18rem]">
          {dayLoading ? (
            <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
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
      )}

      {selectedOverCapacity ? (
        <div className="w-full">
          <Alert
            tone="warning"
            title={t("overCapacityWarningTitle")}
            description={t("overCapacityWarningBody")}
          />
        </div>
      ) : null}
    </div>
  );
}
