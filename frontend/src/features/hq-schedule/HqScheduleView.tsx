"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  createHqScheduleHoliday,
  deleteHqScheduleHoliday,
  fetchHqScheduleAvailabilityDetail,
  fetchHqScheduleHolidays,
  type HqScheduleAvailabilityResponse,
  type HqScheduleDayAvailability,
  type HqScheduleHoliday,
} from "@/lib/api/hqSchedule";
import {
  Badge,
  Button,
  Card,
  CardBody,
  ErrorState,
  Input,
  Loading,
  PageContainer,
  PageHeader,
  SectionHeader,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";
import { toLocalDateKey } from "@/shared/utils/datetime";
import { cn } from "@/shared/utils";

const RANGE_DAYS = 6; // one week, inclusive

function startOfWeek(date: Date): Date {
  const copy = new Date(date);
  const iso = copy.getDay() === 0 ? 7 : copy.getDay(); // 1=Mon..7=Sun
  copy.setDate(copy.getDate() - (iso - 1));
  copy.setHours(0, 0, 0, 0);
  return copy;
}

function addDays(date: Date, days: number): Date {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
}

function DayColumnHeader({
  day,
  weekdayLabel,
  holidayLabel,
  weekendLabel,
}: {
  day: HqScheduleDayAvailability;
  weekdayLabel: string;
  holidayLabel: string;
  weekendLabel: string;
}) {
  const closed = day.closed;
  return (
    <div
      className={cn(
        "flex flex-col items-center gap-1 rounded-[var(--ecmp-radius-md)] px-2 py-2 text-center",
        closed
          ? "border border-ecmp-danger-border bg-ecmp-danger-bg text-ecmp-danger-text"
          : "border border-ecmp-border/70 bg-ecmp-surface-sunken text-ecmp-text-primary",
      )}
    >
      <span className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-wide">
        {weekdayLabel}
      </span>
      <span className="text-[length:var(--ecmp-font-body-size)] font-semibold">
        {day.date}
      </span>
      {closed && (
        <span className="text-[length:var(--ecmp-font-caption-size)] font-medium">
          {day.closedReason === "HOLIDAY"
            ? day.holidayLabel || holidayLabel
            : weekendLabel}
        </span>
      )}
    </div>
  );
}

export function HqScheduleView() {
  const t = useTranslations("hqSchedule");
  const { hasPermission } = useAuth();
  const canReadHolidays = hasPermission("settings:read");
  const canManageHolidays = hasPermission("settings:update");
  const showHolidayPanel = canReadHolidays || canManageHolidays;
  const { pushSuccess, pushError } = useToast();
  const [weekStart, setWeekStart] = useState<Date>(() => startOfWeek(new Date()));
  const [data, setData] = useState<HqScheduleAvailabilityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [holidays, setHolidays] = useState<HqScheduleHoliday[]>([]);
  const [holidayDate, setHolidayDate] = useState("");
  const [holidayLabel, setHolidayLabel] = useState("");
  const [holidaySaving, setHolidaySaving] = useState(false);
  const [holidayDeletingDate, setHolidayDeletingDate] = useState<string | null>(
    null,
  );

  const rangeFrom = useMemo(() => toLocalDateKey(weekStart), [weekStart]);
  const rangeTo = useMemo(
    () => toLocalDateKey(addDays(weekStart, RANGE_DAYS)),
    [weekStart],
  );

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    fetchHqScheduleAvailabilityDetail(rangeFrom, rangeTo)
      .then((res) => {
        if (!cancelled) setData(res.data);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [rangeFrom, rangeTo]);

  const reloadHolidays = useCallback(() => {
    if (!showHolidayPanel) {
      setHolidays([]);
      return;
    }
    fetchHqScheduleHolidays(rangeFrom, rangeTo)
      .then((res) => setHolidays(res.data ?? []))
      .catch(() => setHolidays([]));
  }, [rangeFrom, rangeTo, showHolidayPanel]);

  useEffect(() => {
    reloadHolidays();
  }, [reloadHolidays]);

  async function submitCreateHoliday(): Promise<void> {
    const date = holidayDate.trim();
    const label = holidayLabel.trim();
    if (!date || !label) return;
    setHolidaySaving(true);
    try {
      await createHqScheduleHoliday({ holidayDate: date, label });
      setHolidayDate("");
      setHolidayLabel("");
      pushSuccess(t("holidayCreatedToast"));
      reloadHolidays();
    } catch (err) {
      pushError(err, t("holidayCreateFailed"));
    } finally {
      setHolidaySaving(false);
    }
  }

  async function submitDeleteHoliday(date: string): Promise<void> {
    setHolidayDeletingDate(date);
    try {
      await deleteHqScheduleHoliday(date);
      pushSuccess(t("holidayDeletedToast"));
      reloadHolidays();
    } catch (err) {
      pushError(err, t("holidayDeleteFailed"));
    } finally {
      setHolidayDeletingDate(null);
    }
  }

  const weekdayFormatter = useMemo(
    () => new Intl.DateTimeFormat("id-ID", { weekday: "short" }),
    [],
  );

  return (
    <PageContainer>
      <PageHeader
        title={t("title")}
        description={t("description")}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setWeekStart((prev) => addDays(prev, -7))}
            >
              {t("previousWeek")}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setWeekStart(startOfWeek(new Date()))}
            >
              {t("thisWeek")}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setWeekStart((prev) => addDays(prev, 7))}
            >
              {t("nextWeek")}
            </Button>
          </div>
        }
      />

      {loading && <Loading label={t("loading")} />}
      {!loading && error && <ErrorState message={t("loadError")} />}

      {!loading && !error && data && (
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <div
            className="grid gap-2"
            style={{ gridTemplateColumns: `repeat(${data.days.length}, minmax(0, 1fr))` }}
          >
            {data.days.map((day) => (
              <DayColumnHeader
                key={day.date}
                day={day}
                weekdayLabel={weekdayFormatter.format(new Date(`${day.date}T00:00:00`))}
                holidayLabel={t("holiday")}
                weekendLabel={t("weekend")}
              />
            ))}
          </div>

          <div className="overflow-x-auto">
            <div
              className="grid min-w-[720px] gap-2"
              style={{ gridTemplateColumns: `repeat(${data.days.length}, minmax(0, 1fr))` }}
            >
              {data.days.map((day) => (
                <div key={day.date} className="flex flex-col gap-2">
                  {day.closed ? (
                    <div className="rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-danger-border bg-ecmp-danger-subtle px-3 py-4 text-center text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger-text">
                      {day.closedReason === "HOLIDAY"
                        ? day.holidayLabel || t("holiday")
                        : t("weekend")}
                    </div>
                  ) : (
                    day.slots.map((slot) => {
                      const full = slot.availableCount <= 0;
                      return (
                        <Card
                          key={`${day.date}-${slot.startTime}`}
                          padding={false}
                          className={cn(
                            "p-3",
                            full && "border-ecmp-warning-border bg-ecmp-warning-subtle",
                          )}
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-[length:var(--ecmp-font-body-size)] font-medium">
                              {slot.startTime}–{slot.endTime}
                            </span>
                            <Badge tone={full ? "warning" : "success"} variant="soft">
                              {t("availableCount", { count: slot.availableCount })}
                            </Badge>
                          </div>
                          <p className="mt-1 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                            {t("scheduledOfCapacity", {
                              scheduled: slot.scheduledCount,
                              capacity: slot.capacity,
                            })}
                          </p>
                          {slot.proposedCount > 0 && (
                            <div className="mt-2 space-y-1 border-t border-ecmp-border/60 pt-2">
                              <p className="text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-primary">
                                {t("pendingProposalsCount", { count: slot.proposedCount })}
                              </p>
                              <ul className="space-y-1">
                                {slot.pendingProposals.map((proposal) => (
                                  <li
                                    key={proposal.complaintId}
                                    className="flex items-center justify-between gap-2 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary"
                                  >
                                    <span>{proposal.complaintNumber}</span>
                                    <span>{proposal.owningUnitId ?? "—"}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </Card>
                      );
                    })
                  )}
                </div>
              ))}
            </div>
          </div>

          {showHolidayPanel ? (
          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader title={t("holidayManageTitle")} />
            <Card>
              <CardBody className="space-y-[var(--ecmp-panel-gap)]">
                {holidays.length === 0 ? (
                  <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                    {t("holidayEmpty")}
                  </p>
                ) : (
                  <ul className="space-y-2">
                    {holidays.map((holiday) => (
                      <li
                        key={holiday.holidayDate}
                        className="flex items-center justify-between gap-3 rounded-[var(--ecmp-radius-md)] border border-ecmp-border px-3 py-2"
                      >
                        <span className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                          {holiday.holidayDate} — {holiday.label}
                        </span>
                        {canManageHolidays ? (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            loading={holidayDeletingDate === holiday.holidayDate}
                            disabled={holidayDeletingDate !== null}
                            onClick={() =>
                              void submitDeleteHoliday(holiday.holidayDate)
                            }
                          >
                            {t("holidayDeleteButton")}
                          </Button>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}

                {canManageHolidays ? (
                  <div className="flex flex-wrap items-end gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                    <Input
                      type="date"
                      label={t("holidayDateLabel")}
                      value={holidayDate}
                      onChange={(e) => setHolidayDate(e.target.value)}
                      disabled={holidaySaving}
                    />
                    <Input
                      label={t("holidayLabelLabel")}
                      placeholder={t("holidayLabelPlaceholder")}
                      value={holidayLabel}
                      onChange={(e) => setHolidayLabel(e.target.value)}
                      disabled={holidaySaving}
                      maxLength={200}
                    />
                    <Button
                      type="button"
                      loading={holidaySaving}
                      disabled={!holidayDate.trim() || !holidayLabel.trim()}
                      onClick={() => void submitCreateHoliday()}
                    >
                      {t("holidayAddButton")}
                    </Button>
                  </div>
                ) : null}
              </CardBody>
            </Card>
          </section>
          ) : null}
        </div>
      )}
    </PageContainer>
  );
}
