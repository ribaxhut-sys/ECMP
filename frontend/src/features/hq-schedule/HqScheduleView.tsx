"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { canCmBatch1HqReview } from "@/features/complaints/cmBatch1HqActions";
import { fetchBranches, type Branch } from "@/lib/api";
import {
  createHqScheduleHoliday,
  deleteHqScheduleHoliday,
  fetchHqScheduleAvailability,
  fetchHqScheduleAvailabilityDetail,
  fetchHqScheduleHolidays,
  type HqScheduleAvailabilityResponse,
  type HqScheduleDayAvailability,
  type HqScheduleHoliday,
  type HqScheduleProposalSummary,
  type HqScheduleSlotAvailability,
} from "@/lib/api/hqSchedule";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Input,
  Loading,
  PageContainer,
  PageHeader,
  SectionHeader,
  Select,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";
import { toLocalDateKey } from "@/shared/utils/datetime";
import { cn } from "@/shared/utils";

const RANGE_DAYS = 6; // one week, inclusive

/**
 * Fixed-date national holidays only (same calendar date every year, set by
 * law) — Idul Fitri, Nyepi, Waisak, and cuti bersama move every year and
 * are only confirmed once the government publishes that year's SKB 3
 * Menteri, so they must still be added manually.
 */
const FIXED_NATIONAL_HOLIDAYS: readonly { month: number; day: number; labelKey: string }[] = [
  { month: 1, day: 1, labelKey: "holidayFixedNewYear" },
  { month: 5, day: 1, labelKey: "holidayFixedLabourDay" },
  { month: 6, day: 1, labelKey: "holidayFixedPancasilaDay" },
  { month: 8, day: 17, labelKey: "holidayFixedIndependenceDay" },
  { month: 12, day: 25, labelKey: "holidayFixedChristmas" },
];

function importYearOptions(centerYear: number): { value: string; label: string }[] {
  return [centerYear - 1, centerYear, centerYear + 1, centerYear + 2].map((year) => ({
    value: String(year),
    label: String(year),
  }));
}

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

/** "2026-08-20" -> "20-08-2026" for display; API params/inputs stay ISO. */
function formatDateDMY(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  return year && month && day ? `${day}-${month}-${year}` : isoDate;
}

function slotTone(availableCount: number): "success" | "warning" | "danger" {
  if (availableCount <= 0) return "danger";
  if (availableCount === 1) return "warning";
  return "success";
}

type BreakRowSegment =
  | { closed: true; day: HqScheduleDayAvailability }
  | { closed: false; span: number };

/** Groups a break-time row into per-holiday cells plus one merged "break" cell per run of open days. */
function breakRowSegments(days: HqScheduleDayAvailability[]): BreakRowSegment[] {
  const segments: BreakRowSegment[] = [];
  let openRun = 0;
  for (const day of days) {
    if (day.closed) {
      if (openRun > 0) {
        segments.push({ closed: false, span: openRun });
        openRun = 0;
      }
      segments.push({ closed: true, day });
    } else {
      openRun += 1;
    }
  }
  if (openRun > 0) segments.push({ closed: false, span: openRun });
  return segments;
}

function CaseTag({
  proposal,
  branchNameByCode,
}: {
  proposal: HqScheduleProposalSummary;
  branchNameByCode: Map<string, string>;
}) {
  const title = branchNameByCode.get(proposal.owningUnitId ?? "") || proposal.unitCode;
  return (
    <span
      title={title}
      className="cursor-help border-b border-dotted border-ecmp-text-secondary/60 text-ecmp-text-secondary"
    >
      {" "}
      ({proposal.unitCode})
    </span>
  );
}

function CaseLine({
  proposal,
  canOpen,
  branchNameByCode,
}: {
  proposal: HqScheduleProposalSummary;
  canOpen: boolean;
  branchNameByCode: Map<string, string>;
}) {
  return (
    <div className="text-[length:var(--ecmp-font-caption-size)]">
      {canOpen ? (
        <Link
          href={`/complaints/cm/${encodeURIComponent(proposal.complaintId)}`}
          className="font-medium text-ecmp-primary hover:underline"
        >
          {proposal.complaintNumber}
        </Link>
      ) : (
        <span className="text-ecmp-text-secondary">{proposal.complaintNumber}</span>
      )}
      <CaseTag proposal={proposal} branchNameByCode={branchNameByCode} />
    </div>
  );
}

function ScheduleSlotCell({
  slot,
  canOpenCase,
  branchNameByCode,
  slotRatioLabel,
}: {
  slot: HqScheduleSlotAvailability;
  canOpenCase: (owningUnitId: string | null | undefined) => boolean;
  branchNameByCode: Map<string, string>;
  slotRatioLabel: string;
}) {
  const tone = slotTone(slot.availableCount);
  return (
    <td
      className={cn(
        "border-b border-ecmp-border/70 p-2 align-top",
        tone === "danger" && "bg-ecmp-danger-subtle",
        tone === "warning" && "bg-ecmp-warning-subtle",
      )}
    >
      <div className="flex flex-col gap-1">
        {slot.scheduledCases.map((proposal) => (
          <CaseLine
            key={proposal.complaintId}
            proposal={proposal}
            canOpen={canOpenCase(proposal.owningUnitId)}
            branchNameByCode={branchNameByCode}
          />
        ))}
        <Badge tone={tone} variant="solid" className="self-start">
          {slotRatioLabel}
        </Badge>
      </div>
    </td>
  );
}

export function HqScheduleView() {
  const t = useTranslations("hqSchedule");
  const tCommon = useTranslations("common");
  const { hasPermission, roles, status } = useAuth();
  const unitCode = useOrgUnitCode();
  const canRead = hasPermission("complaints:read");
  const orgReady = unitCode !== undefined;
  const canSeeDetail = canCmBatch1HqReview({
    roles,
    hasPermission,
    unitCode,
  });
  const canReadHolidays = hasPermission("settings:read");
  const canManageHolidays = hasPermission("settings:update");
  const showHolidayPanel = canReadHolidays || canManageHolidays;
  const { pushSuccess, pushError } = useToast();
  const [weekStart, setWeekStart] = useState<Date>(() => startOfWeek(new Date()));
  const [data, setData] = useState<HqScheduleAvailabilityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [holidays, setHolidays] = useState<HqScheduleHoliday[]>([]);
  const [holidayDate, setHolidayDate] = useState("");
  const [holidayLabel, setHolidayLabel] = useState("");
  const [holidaySaving, setHolidaySaving] = useState(false);
  const [holidayDeletingDate, setHolidayDeletingDate] = useState<string | null>(
    null,
  );
  const [importYear, setImportYear] = useState(() => String(new Date().getFullYear()));
  const [importing, setImporting] = useState(false);

  const rangeFrom = useMemo(() => toLocalDateKey(weekStart), [weekStart]);
  const rangeTo = useMemo(
    () => toLocalDateKey(addDays(weekStart, RANGE_DAYS)),
    [weekStart],
  );

  useEffect(() => {
    if (status !== "authenticated" || !canRead || !orgReady) return;
    let cancelled = false;
    setLoading(true);
    setError(false);
    const fetchGrid = canSeeDetail
      ? fetchHqScheduleAvailabilityDetail
      : fetchHqScheduleAvailability;
    fetchGrid(rangeFrom, rangeTo)
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
  }, [canRead, canSeeDetail, orgReady, rangeFrom, rangeTo, status]);

  useEffect(() => {
    if (status !== "authenticated" || !canRead) return;
    let cancelled = false;
    fetchBranches(100)
      .then((res) => {
        if (!cancelled) setBranches(res.data ?? []);
      })
      .catch(() => {
        if (!cancelled) setBranches([]);
      });
    return () => {
      cancelled = true;
    };
  }, [canRead, status]);

  const branchNameByCode = useMemo(() => {
    const map = new Map<string, string>();
    for (const branch of branches) map.set(branch.code, branch.name);
    return map;
  }, [branches]);

  const canOpenCase = useCallback(
    (owningUnitId: string | null | undefined): boolean => {
      if (canSeeDetail) return true;
      return unitCode != null && owningUnitId != null && unitCode === owningUnitId;
    },
    [canSeeDetail, unitCode],
  );

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

  async function submitImportHolidays(): Promise<void> {
    const year = Number(importYear);
    if (!Number.isInteger(year)) return;
    setImporting(true);
    try {
      for (const holiday of FIXED_NATIONAL_HOLIDAYS) {
        const holidayDate = `${year}-${String(holiday.month).padStart(2, "0")}-${String(
          holiday.day,
        ).padStart(2, "0")}`;
        await createHqScheduleHoliday({ holidayDate, label: t(holiday.labelKey) });
      }
      pushSuccess(t("holidayImportedToast", { count: FIXED_NATIONAL_HOLIDAYS.length, year }));
      reloadHolidays();
    } catch (err) {
      pushError(err, t("holidayImportFailed"));
    } finally {
      setImporting(false);
    }
  }

  const weekdayFormatterLong = useMemo(
    () => new Intl.DateTimeFormat("id-ID", { weekday: "long" }),
    [],
  );
  const weekdayFormatterShort = useMemo(
    () => new Intl.DateTimeFormat("id-ID", { weekday: "short" }),
    [],
  );

  if (status === "authenticated" && !canRead) {
    return (
      <PageContainer>
        <Empty
          title={tCommon("accessRestricted")}
          description={t("accessRestrictedDescription")}
        />
      </PageContainer>
    );
  }

  const showLoading = status !== "authenticated" || !orgReady || loading;
  const visibleDays: HqScheduleDayAvailability[] =
    data?.days.filter((day) => day.closedReason !== "WEEKEND") ?? [];
  const templateSlots: HqScheduleDayAvailability["slots"] =
    visibleDays.find((day) => !day.closed)?.slots ?? [];
  const todayIso = toLocalDateKey(new Date());

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

      {showLoading && <Loading label={t("loading")} />}
      {!showLoading && error && <ErrorState message={t("loadError")} />}

      {!showLoading && !error && data && (
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <div className="overflow-x-auto rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70">
            <table className="w-full min-w-[640px] border-collapse">
              <thead>
                <tr>
                  <th className="sticky left-0 z-10 border-b border-r border-ecmp-border/70 bg-ecmp-surface-sunken p-2 text-center text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-secondary">
                    {t("timeColumnHeader")}
                  </th>
                  {visibleDays.map((day) => {
                    const isToday = day.date === todayIso;
                    return (
                      <th
                        key={day.date}
                        className={cn(
                          "border-b border-ecmp-border/70 p-2 text-center",
                          isToday ? "bg-ecmp-primary-muted" : "bg-ecmp-surface-sunken",
                        )}
                      >
                        <div
                          className={cn(
                            "text-[length:var(--ecmp-font-body-size)] font-semibold",
                            isToday ? "text-ecmp-primary" : "text-ecmp-text-primary",
                          )}
                        >
                          {formatDateDMY(day.date)}
                        </div>
                        <div
                          className={cn(
                            "text-[length:var(--ecmp-font-caption-size)] uppercase tracking-wide",
                            isToday ? "text-ecmp-primary" : "text-ecmp-text-secondary",
                          )}
                        >
                          <span className="hidden md:inline">
                            {weekdayFormatterLong.format(new Date(`${day.date}T00:00:00`))}
                          </span>
                          <span className="md:hidden">
                            {weekdayFormatterShort.format(new Date(`${day.date}T00:00:00`))}
                          </span>
                          {isToday ? ` · ${t("todayLabel")}` : ""}
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {templateSlots.length === 0 ? (
                  <tr>
                    <td
                      colSpan={visibleDays.length + 1}
                      className="p-4 text-center text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary"
                    >
                      {t("weekClosed")}
                    </td>
                  </tr>
                ) : (
                  templateSlots.map((templateSlot, index) => (
                    <tr key={templateSlot.startTime}>
                      <td className="sticky left-0 z-10 border-b border-r border-ecmp-border/70 bg-ecmp-surface p-2 text-center align-middle text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                        {templateSlot.startTime}
                      </td>
                      {templateSlot.isBreak
                        ? breakRowSegments(visibleDays).map((segment, segmentIndex) =>
                            segment.closed ? (
                              <td
                                key={segment.day.date}
                                className="border-b border-ecmp-border/70 bg-ecmp-danger-subtle p-2 text-center align-middle text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger-text"
                              >
                                {segment.day.closedReason === "HOLIDAY"
                                  ? segment.day.holidayLabel || t("holiday")
                                  : t("weekend")}
                              </td>
                            ) : (
                              <td
                                key={`break-${segmentIndex}`}
                                colSpan={segment.span}
                                className="border-b border-ecmp-border/70 p-2 text-center align-middle text-[length:var(--ecmp-font-body-size)] font-bold text-ecmp-text-secondary"
                              >
                                {t("breakLabel")}
                              </td>
                            ),
                          )
                        : visibleDays.map((day) => {
                            if (day.closed) {
                              return (
                                <td
                                  key={day.date}
                                  className="border-b border-ecmp-border/70 bg-ecmp-danger-subtle p-2 text-center align-middle text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger-text"
                                >
                                  {day.closedReason === "HOLIDAY"
                                    ? day.holidayLabel || t("holiday")
                                    : t("weekend")}
                                </td>
                              );
                            }
                            const slot = day.slots[index];
                            if (!slot) {
                              return (
                                <td key={day.date} className="border-b border-ecmp-border/70 p-2" />
                              );
                            }
                            return (
                              <ScheduleSlotCell
                                key={day.date}
                                slot={slot}
                                canOpenCase={canOpenCase}
                                branchNameByCode={branchNameByCode}
                                slotRatioLabel={t("slotRatio", {
                                  scheduled: slot.scheduledCount,
                                  capacity: slot.capacity,
                                })}
                              />
                            );
                          })}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
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
                          {formatDateDMY(holiday.holidayDate)} — {holiday.label}
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
                  <div className="space-y-2 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                    <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                      {t("holidayImportHint")}
                    </p>
                    <div className="flex flex-wrap items-end gap-[var(--ecmp-form-gap)]">
                      <Select
                        label={t("holidayImportYearLabel")}
                        value={importYear}
                        onChange={(e) => setImportYear(e.target.value)}
                        options={importYearOptions(new Date().getFullYear())}
                        disabled={importing}
                      />
                      <Button
                        type="button"
                        variant="secondary"
                        loading={importing}
                        onClick={() => void submitImportHolidays()}
                      >
                        {t("holidayImportButton")}
                      </Button>
                    </div>
                  </div>
                ) : null}

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
