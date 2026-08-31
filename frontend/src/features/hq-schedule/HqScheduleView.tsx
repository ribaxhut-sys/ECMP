"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type Ref } from "react";
import Link from "next/link";
import { useTranslations, useLocale } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { isPusatWorkAudience } from "@/features/complaints/cmBatch1ComplaintListIdentity";
import {
  canCmBatch1HqReview,
  isHqScheduleDestinationUnitCode,
} from "@/features/complaints/cmBatch1HqActions";
import { fetchBranches, ackCmHqScheduleSeen } from "@/lib/api";
import {
  createHqScheduleHoliday,
  deleteHqScheduleHoliday,
  fetchHqScheduleAvailability,
  fetchHqScheduleAvailabilityDetail,
  fetchHqScheduleHolidayCatalog,
  fetchHqScheduleHolidays,
  importHqScheduleHolidays,
  type HqScheduleAvailabilityResponse,
  type HqScheduleDayAvailability,
  type HqScheduleHoliday,
  type HqScheduleHolidayCatalog,
  type HqScheduleHolidayKind,
  type HqScheduleProposalSummary,
  type HqScheduleSlotAvailability,
} from "@/lib/api/hqSchedule";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Checkbox,
  Empty,
  ErrorState,
  Input,
  Loading,
  PageContainer,
  PageHeader,
  Select,
  StatCard,
} from "@/shared/ui";
import { IconAlert, IconCheck, IconChevronRight } from "@/shared/icons";
import { useToast } from "@/shared/providers";
import { formatShortDate, toLocalDateKey } from "@/shared/utils/datetime";
import { cn, pusatUnitShortCode } from "@/shared/utils";
import { refreshWorkBadges } from "@/features/cases/workBadgesSignal";

const RANGE_DAYS = 6; // one week, inclusive

function importYearOptions(centerYear: number): { value: string; label: string }[] {
  return [centerYear - 1, centerYear, centerYear + 1, centerYear + 2].map((year) => ({
    value: String(year),
    label: String(year),
  }));
}

function holidayChipDate(iso: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    timeZone: "Asia/Jakarta",
  }).format(new Date(`${iso}T00:00:00+07:00`));
}

function holidayKindLabel(
  kind: HqScheduleHolidayKind | null | undefined,
  t: (key: string) => string,
): string | null {
  if (kind === "CUTI_BERSAMA") return t("holidayKindCollective");
  if (kind === "LIBUR_NASIONAL") return t("holidayKindNational");
  return null;
}

function isPastHolidayDate(iso: string, todayIso: string): boolean {
  return iso < todayIso;
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

export type SlotOccupancy = "empty" | "partial" | "full";

/** Occupancy from booked count — not leftover capacity — so capacity > 2 stays correct. */
export function slotOccupancy(
  scheduledCount: number,
  capacity: number,
): SlotOccupancy {
  if (scheduledCount <= 0) return "empty";
  if (scheduledCount >= capacity) return "full";
  return "partial";
}

export interface HqWeekSummary {
  /** Total occupants for the visible week (live + completed). */
  scheduled: number;
  /** Total occupants today (live + completed). */
  today: number;
  /** Subset of `today` whose HQ visit is already closed. */
  todayCompleted: number;
  /** Slots still open to book — future, not on break, capacity left. */
  bookable: number;
  /** Total completed visits across the visible week. */
  weekCompleted: number;
}

export const UNASSIGNED_UNIT_FILTER = "__unassigned__";

export function matchingScheduledCases(
  cases: HqScheduleProposalSummary[],
  unitFilter: string | null,
): HqScheduleProposalSummary[] {
  if (!unitFilter) return cases;
  if (unitFilter === UNASSIGNED_UNIT_FILTER) {
    return cases.filter((c) => !c.destinationUnitCode?.trim());
  }
  const needle = unitFilter.trim().toUpperCase();
  return cases.filter(
    (c) => (c.destinationUnitCode ?? "").trim().toUpperCase() === needle,
  );
}

export function slotCountsForFilter(
  slot: HqScheduleSlotAvailability,
  unitFilter: string | null,
): { scheduled: number; capacity: number; completed: number } {
  if (!unitFilter) {
    return {
      scheduled: slot.scheduledCount,
      capacity: slot.capacity,
      completed: slot.completedCount,
    };
  }
  if (unitFilter === UNASSIGNED_UNIT_FILTER) {
    const cases = matchingScheduledCases(slot.scheduledCases, unitFilter);
    return {
      scheduled: cases.length,
      capacity: slot.capacity,
      completed: cases.filter((c) => Boolean(c.completed)).length,
    };
  }
  const unit = (slot.units ?? []).find(
    (row) => row.unitCode.trim().toUpperCase() === unitFilter.trim().toUpperCase(),
  );
  if (unit) {
    return {
      scheduled: unit.scheduledCount,
      capacity: unit.capacity,
      completed: unit.completedCount,
    };
  }
  const cases = matchingScheduledCases(slot.scheduledCases, unitFilter);
  return {
    scheduled: cases.length,
    capacity: slot.capacity,
    completed: cases.filter((c) => Boolean(c.completed)).length,
  };
}

export function dayOccupancyTotals(
  day: HqScheduleDayAvailability,
  unitFilter: string | null,
): { scheduled: number; completed: number } {
  let scheduled = 0;
  let completed = 0;
  for (const slot of day.slots) {
    if (slot.isBreak) continue;
    const counts = slotCountsForFilter(slot, unitFilter);
    scheduled += counts.scheduled;
    completed += counts.completed;
  }
  return { scheduled, completed };
}

/** Per-destination counts for a day's past summary (null code = unit belum ditetapkan). */
export function dayUnitBreakdown(
  day: HqScheduleDayAvailability,
): { code: string | null; count: number }[] {
  const byUnit = new Map<string, number>();
  let unassigned = 0;
  for (const slot of day.slots) {
    if (slot.isBreak) continue;
    for (const visit of slot.scheduledCases ?? []) {
      const code = visit.destinationUnitCode?.trim();
      if (!code) {
        unassigned += 1;
        continue;
      }
      const key = code.toUpperCase();
      byUnit.set(key, (byUnit.get(key) ?? 0) + 1);
    }
  }
  const rows: { code: string | null; count: number }[] = [...byUnit.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([code, count]) => ({ code, count }));
  if (unassigned > 0) rows.push({ code: null, count: unassigned });
  return rows;
}

export function summarizeHqWeek(
  days: HqScheduleDayAvailability[],
  todayIso: string,
  unitFilter: string | null = null,
): HqWeekSummary {
  let scheduled = 0;
  let today = 0;
  let todayCompleted = 0;
  let bookable = 0;
  let weekCompleted = 0;
  for (const day of days) {
    if (day.closed) continue;
    for (const slot of day.slots) {
      if (slot.isBreak) continue;
      const counts = slotCountsForFilter(slot, unitFilter);
      scheduled += counts.scheduled;
      weekCompleted += counts.completed;
      if (!unitFilter || unitFilter === UNASSIGNED_UNIT_FILTER) {
        bookable += slot.bookableCount;
      } else {
        const unit = (slot.units ?? []).find(
          (row) =>
            row.unitCode.trim().toUpperCase() === unitFilter.trim().toUpperCase(),
        );
        bookable += unit && unit.bookable ? unit.availableCount : 0;
      }
      if (day.date === todayIso) {
        today += counts.scheduled;
        todayCompleted += counts.completed;
      }
    }
  }
  return { scheduled, today, todayCompleted, bookable, weekCompleted };
}

/** Where the taxpayer reports — the trailing half of a visit line. */
function destinationLabel(
  proposal: HqScheduleProposalSummary,
  unsetLabel: string,
): string {
  return proposal.destinationUnitCode?.trim()
    ? pusatUnitShortCode(proposal.destinationUnitCode)
    : unsetLabel;
}

/**
 * The board lists Case numbers, so each one opens its own Case — not the
 * parent complaint. A row without a Case (legacy arrival booked before the
 * escalation Case existed) falls back to the complaint number and page,
 * which is then the only record there is to open.
 */
function caseHref(caseId: string): string {
  return `/complaints/cm/cases/${encodeURIComponent(caseId)}`;
}

/**
 * Purely visual hint, derived from the clock — not a stored fact. A slot
 * whose end time has already passed while the case is still HQ_SCHEDULED
 * (not completed) reads as "past its slot, not yet closed by Pusat". This
 * never changes case state and carries no record of who/when.
 */
export function isArrivalOverdue(date: string, endTime: string, nowMs: number): boolean {
  const slotEnd = new Date(`${date}T${endTime}:00`).getTime();
  return Number.isFinite(slotEnd) && slotEnd < nowMs;
}

/**
 * A slot whose entire window has elapsed — same boundary as `isArrivalOverdue`
 * (end time), but for the slot itself rather than one occupant. Drives the
 * neutral "this is history now" styling and the outcome-instead-of-ratio
 * label, regardless of whether anyone was ever booked into the slot. A slot
 * still in progress (start passed, end not yet) reads as current, not past.
 */
export function isSlotPast(date: string, endTime: string, nowMs: number): boolean {
  const slotEnd = new Date(`${date}T${endTime}:00`).getTime();
  return Number.isFinite(slotEnd) && slotEnd < nowMs;
}

/** "2/6 slot" while still current; an outcome ("1/2 selesai" / past-empty) once the slot has ended. */
function slotRatioText(
  date: string,
  slot: HqScheduleSlotAvailability,
  nowMs: number,
  t: ReturnType<typeof useTranslations>,
  unitFilter: string | null = null,
): string {
  const counts = slotCountsForFilter(slot, unitFilter);
  if (isSlotPast(date, slot.endTime, nowMs)) {
    if (counts.scheduled === 0) return t("slotPastEmpty");
    return t("slotOutcomeLabel", {
      completed: counts.completed,
      scheduled: counts.scheduled,
    });
  }
  return t("slotRatio", { scheduled: counts.scheduled, capacity: counts.capacity });
}

/** "healthy" once every occupant today is closed out; "critical" once one is overdue and still open. */
function todayAccent(
  days: HqScheduleDayAvailability[],
  todayIso: string,
  nowMs: number,
): "normal" | "attention" | "critical" | "healthy" {
  let scheduled = 0;
  let completed = 0;
  let overdue = false;
  for (const day of days) {
    if (day.date !== todayIso || day.closed) continue;
    for (const slot of day.slots) {
      if (slot.isBreak) continue;
      scheduled += slot.scheduledCount;
      completed += slot.completedCount;
      if (
        slot.completedCount < slot.scheduledCount &&
        isArrivalOverdue(day.date, slot.endTime, nowMs)
      ) {
        overdue = true;
      }
    }
  }
  if (scheduled === 0) return "normal";
  if (overdue) return "critical";
  if (completed < scheduled) return "attention";
  return "healthy";
}

function CaseLine({
  proposal,
  canOpen,
  overdue,
}: {
  proposal: HqScheduleProposalSummary;
  canOpen: boolean;
  overdue: boolean;
}) {
  const t = useTranslations("hqSchedule");
  const showOverdue = overdue && !proposal.completed;
  // One link per Case — the number shown is a Case number, so it must open
  // that Case. Only a legacy arrival with no Case falls back to the complaint.
  const refs =
    proposal.cases.length > 0
      ? proposal.cases.map((c) => ({ label: c.caseNumber, href: caseHref(c.caseId) }))
      : [
          {
            label: proposal.complaintNumber,
            href: `/complaints/cm/${encodeURIComponent(proposal.complaintId)}`,
          },
        ];
  const linkClass = cn(
    "font-medium hover:underline",
    showOverdue ? "text-ecmp-danger-text" : "text-ecmp-primary",
  );
  const plainClass = showOverdue
    ? "font-medium text-ecmp-danger-text"
    : "text-ecmp-text-secondary";
  const customerName =
    canOpen && proposal.customerDisplayName?.trim()
      ? proposal.customerDisplayName.trim()
      : null;
  return (
    <div
      data-completed={proposal.completed ? "true" : "false"}
      data-overdue={showOverdue ? "true" : "false"}
      className="flex min-w-0 items-start gap-1.5 py-1.5 first:pt-0 last:pb-0 text-left text-[length:var(--ecmp-font-helper-size)] leading-tight"
    >
      <span className={cn("min-w-0", !canOpen && plainClass)}>
        <span className="block min-w-0 truncate">
          {refs.map((ref, index) => (
            <span key={ref.href}>
              {index > 0 ? ", " : null}
              {canOpen ? (
                <Link href={ref.href} className={linkClass}>
                  {ref.label}
                </Link>
              ) : (
                ref.label
              )}
            </span>
          ))}
          <span className={showOverdue ? "text-ecmp-danger-text" : "text-ecmp-text-secondary"}>
            {` · ${destinationLabel(proposal, t("destinationUnassigned"))}`}
          </span>
        </span>
        {customerName ? (
          <span
            className="mt-0.5 block min-w-0 truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary"
            title={customerName}
            data-testid="hq-schedule-wp-name"
          >
            {customerName}
          </span>
        ) : null}
      </span>
      {proposal.completed ? (
        <Badge
          tone="success"
          variant="outline"
          className="shrink-0 px-1 py-0"
          title={t("visitCompleted")}
          aria-label={t("visitCompleted")}
        >
          <IconCheck className="size-3" aria-hidden />
        </Badge>
      ) : null}
      {showOverdue ? (
        <Badge
          tone="warning"
          variant="outline"
          className="shrink-0 px-1 py-0"
          title={t("visitOverdue")}
          aria-label={t("visitOverdue")}
        >
          <IconAlert className="size-3" aria-hidden />
        </Badge>
      ) : null}
    </div>
  );
}

function SlotCaseList({
  cases,
  date,
  canOpenCase,
  nowMs,
  slotEndTime,
}: {
  cases: HqScheduleProposalSummary[];
  date: string;
  canOpenCase: (owningUnitId: string | null | undefined) => boolean;
  nowMs: number;
  slotEndTime: string;
}) {
  if (cases.length === 0) return null;
  return (
    <div
      className="mt-1.5 divide-y divide-ecmp-border/60"
      data-testid="hq-schedule-slot-cases"
    >
      {cases.map((proposal) => (
        <CaseLine
          key={proposal.complaintId}
          proposal={proposal}
          canOpen={canOpenCase(proposal.owningUnitId)}
          overdue={isArrivalOverdue(date, slotEndTime, nowMs)}
        />
      ))}
    </div>
  );
}

function SlotCard({
  slot,
  date,
  canOpenCase,
  slotRatioLabel,
  breakLabel,
  nowMs,
  unitFilter,
}: {
  slot: HqScheduleSlotAvailability;
  date: string;
  canOpenCase: (owningUnitId: string | null | undefined) => boolean;
  slotRatioLabel: string;
  breakLabel: string;
  nowMs: number;
  unitFilter: string | null;
}) {
  const visibleCases = matchingScheduledCases(slot.scheduledCases, unitFilter);
  if (slot.isBreak) {
    // Arrivals booked before the break window changed (Jumat 11:30–13:30) are
    // bucketed here — still listed, so nobody disappears from the board.
    return (
      <div
        data-testid={`hq-schedule-slot-${date}-${slot.startTime}`}
        className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken px-2.5 py-3 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary"
      >
        <p className="text-center font-bold italic text-ecmp-text-primary">
          {slot.startTime}–{slot.endTime} · {breakLabel}
        </p>
        <SlotCaseList
          cases={visibleCases}
          date={date}
          canOpenCase={canOpenCase}
          nowMs={nowMs}
          slotEndTime={slot.endTime}
        />
      </div>
    );
  }

  const counts = slotCountsForFilter(slot, unitFilter);
  const occupancy = slotOccupancy(counts.scheduled, counts.capacity);
  const isPast = isSlotPast(date, slot.endTime, nowMs);
  return (
    <article
      data-testid={`hq-schedule-slot-${date}-${slot.startTime}`}
      data-occupancy={occupancy}
      data-past={isPast ? "true" : undefined}
      className={cn(
        "rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 px-2.5 py-3 min-h-16",
        "border-l-4",
        isPast
          ? "border-l-ecmp-border bg-ecmp-surface-sunken/60"
          : cn(
              occupancy === "empty" && "border-l-ecmp-success bg-ecmp-success-subtle/40",
              occupancy === "partial" && "border-l-ecmp-warning bg-ecmp-warning-subtle/40",
              occupancy === "full" && "border-l-ecmp-danger bg-ecmp-danger-subtle/40",
            ),
      )}
    >
      <div className="flex items-baseline justify-between gap-2">
        <p className="text-[length:var(--ecmp-font-helper-size)] font-semibold text-ecmp-text-primary">
          {/* A shortened slot must show where it ends — "11:00" alone would
              read as a full hour that runs into the break. */}
          {slot.partial ? `${slot.startTime}–${slot.endTime}` : slot.startTime}
        </p>
        <p className="text-[length:var(--ecmp-font-helper-size)] tabular-nums text-ecmp-text-secondary">
          {slotRatioLabel}
        </p>
      </div>
      <SlotCaseList
        cases={visibleCases}
        date={date}
        canOpenCase={canOpenCase}
        nowMs={nowMs}
        slotEndTime={slot.endTime}
      />
    </article>
  );
}

function DayColumn({
  day,
  isToday,
  isPast,
  summaryLabel,
  weekdayLabel,
  todayLabel,
  canOpenCase,
  slotRatio,
  breakLabel,
  holidayLabel,
  weekendLabel,
  columnRef,
  nowMs,
  unitFilter,
}: {
  day: HqScheduleDayAvailability;
  isToday: boolean;
  isPast: boolean;
  summaryLabel: string | null;
  weekdayLabel: string;
  todayLabel: string;
  canOpenCase: (owningUnitId: string | null | undefined) => boolean;
  slotRatio: (slot: HqScheduleSlotAvailability) => string;
  breakLabel: string;
  holidayLabel: string;
  weekendLabel: string;
  columnRef?: Ref<HTMLElement>;
  nowMs: number;
  unitFilter: string | null;
}) {
  const closedCopy =
    day.closedReason === "HOLIDAY" ? day.holidayLabel || holidayLabel : weekendLabel;
  return (
    <section
      ref={columnRef}
      data-testid={`hq-schedule-day-${day.date}`}
      data-today={isToday ? "true" : undefined}
      data-past={isPast ? "true" : undefined}
      className={cn(
        "flex min-w-[11.5rem] shrink-0 snap-start flex-1 flex-col gap-2 rounded-[var(--ecmp-radius-card)] border p-3",
        isToday
          ? "border-ecmp-primary bg-ecmp-primary-muted/40"
          : "border-ecmp-border/70 bg-ecmp-surface",
        isPast && "opacity-70",
      )}
    >
      <header className="flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
        <h2 className="text-[length:var(--ecmp-font-helper-size)] font-semibold capitalize text-ecmp-text-primary">
          {weekdayLabel}
        </h2>
        <p
          className={cn(
            "text-[length:var(--ecmp-font-helper-size)]",
            isToday ? "text-ecmp-primary" : "text-ecmp-text-secondary",
          )}
        >
          {formatShortDate(day.date)}
        </p>
        {isToday ? (
          <Badge tone="info" variant="solid">
            {todayLabel}
          </Badge>
        ) : null}
        {summaryLabel ? (
          <span className="w-full text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {summaryLabel}
          </span>
        ) : null}
      </header>
      {day.closed ? (
        <p className="rounded-[var(--ecmp-radius-md)] bg-ecmp-danger-subtle px-2.5 py-3 text-center text-[length:var(--ecmp-font-helper-size)] text-ecmp-danger-text">
          {closedCopy}
        </p>
      ) : (
        day.slots.map((slot) => (
          <SlotCard
            key={`${day.date}-${slot.startTime}`}
            slot={slot}
            date={day.date}
            canOpenCase={canOpenCase}
            slotRatioLabel={slotRatio(slot)}
            breakLabel={breakLabel}
            nowMs={nowMs}
            unitFilter={unitFilter}
          />
        ))
      )}
    </section>
  );
}

export function HqScheduleView() {
  const t = useTranslations("hqSchedule");
  const tCommon = useTranslations("common");
  const locale = useLocale();
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
  const [holidays, setHolidays] = useState<HqScheduleHoliday[]>([]);
  const [holidayDate, setHolidayDate] = useState("");
  const [holidayLabel, setHolidayLabel] = useState("");
  const [holidaySaving, setHolidaySaving] = useState(false);
  const [holidayDeletingDate, setHolidayDeletingDate] = useState<string | null>(
    null,
  );
  const [importYear, setImportYear] = useState(() => String(new Date().getFullYear()));
  const [importing, setImporting] = useState(false);
  const [catalogPreview, setCatalogPreview] = useState<HqScheduleHolidayCatalog | null>(
    null,
  );
  const [selectedImportDates, setSelectedImportDates] = useState<Set<string>>(
    () => new Set(),
  );
  const [showPastHolidays, setShowPastHolidays] = useState(false);
  const todayColumnRef = useRef<HTMLElement>(null);
  // Drives the "overdue" tag only — ticks slowly since it's a visual hint, not a stored fact.
  const [nowMs, setNowMs] = useState(() => Date.now());
  const [unitFilter, setUnitFilter] = useState<string | null>(null);
  const [pusatUnits, setPusatUnits] = useState<{ code: string; name: string }[]>(
    [],
  );

  const rangeFrom = useMemo(() => toLocalDateKey(weekStart), [weekStart]);
  const rangeTo = useMemo(
    () => toLocalDateKey(addDays(weekStart, RANGE_DAYS)),
    [weekStart],
  );

  useEffect(() => {
    if (status !== "authenticated" || !canRead || !orgReady) return;
    if (isPusatWorkAudience(unitCode) !== false) return;
    let cancelled = false;
    void ackCmHqScheduleSeen()
      .then(() => {
        if (!cancelled) refreshWorkBadges();
      })
      .catch(() => {
        /* Fail-open: calendar still loads. */
      });
    return () => {
      cancelled = true;
    };
  }, [canRead, orgReady, status, unitCode]);

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
    if (!canSeeDetail) return;
    let cancelled = false;
    fetchBranches()
      .then((res) => {
        if (cancelled) return;
        const units = (res.data ?? [])
          .filter((branch) => isHqScheduleDestinationUnitCode(branch.code))
          .map((branch) => ({ code: branch.code, name: branch.name }));
        setPusatUnits(units);
      })
      .catch(() => {
        if (!cancelled) setPusatUnits([]);
      });
    return () => {
      cancelled = true;
    };
  }, [canSeeDetail]);

  const canOpenCase = useCallback(
    (owningUnitId: string | null | undefined): boolean => {
      if (canSeeDetail) return true;
      return unitCode != null && owningUnitId != null && unitCode === owningUnitId;
    },
    [canSeeDetail, unitCode],
  );

  const holidayRangeFrom = `${importYear}-01-01`;
  const holidayRangeTo = `${importYear}-12-31`;

  const reloadHolidays = useCallback(() => {
    if (!showHolidayPanel) {
      setHolidays([]);
      return;
    }
    fetchHqScheduleHolidays(holidayRangeFrom, holidayRangeTo)
      .then((res) => setHolidays(res.data ?? []))
      .catch(() => setHolidays([]));
  }, [holidayRangeFrom, holidayRangeTo, showHolidayPanel]);

  useEffect(() => {
    reloadHolidays();
  }, [reloadHolidays]);

  useEffect(() => {
    todayColumnRef.current?.scrollIntoView({
      inline: "start",
      block: "nearest",
    });
  }, [data, rangeFrom]);

  useEffect(() => {
    const id = setInterval(() => setNowMs(Date.now()), 60_000);
    return () => clearInterval(id);
  }, []);

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

  async function openImportPreview(): Promise<void> {
    const year = Number(importYear);
    if (!Number.isInteger(year)) return;
    setImporting(true);
    try {
      const res = await fetchHqScheduleHolidayCatalog(year);
      const catalog = res.data;
      setCatalogPreview(catalog);
      setSelectedImportDates(
        new Set(
          catalog.entries
            .filter(
              (entry) =>
                entry.defaultSelected &&
                !isPastHolidayDate(entry.holidayDate, toLocalDateKey(new Date())),
            )
            .map((entry) => entry.holidayDate),
        ),
      );
    } catch (err) {
      setCatalogPreview(null);
      setSelectedImportDates(new Set());
      pushError(err, t("holidayImportUnavailable", { year: importYear }));
    } finally {
      setImporting(false);
    }
  }

  function toggleImportDate(holidayDate: string, checked: boolean): void {
    setSelectedImportDates((prev) => {
      const next = new Set(prev);
      if (checked) next.add(holidayDate);
      else next.delete(holidayDate);
      return next;
    });
  }

  async function submitImportHolidays(): Promise<void> {
    const year = Number(importYear);
    if (!Number.isInteger(year) || selectedImportDates.size === 0) return;
    setImporting(true);
    try {
      const res = await importHqScheduleHolidays({
        year,
        dates: [...selectedImportDates].sort(),
      });
      pushSuccess(
        t("holidayImportedToast", {
          count: res.data.importedCount,
          year,
        }),
      );
      setCatalogPreview(null);
      setSelectedImportDates(new Set());
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

  const visibleDays: HqScheduleDayAvailability[] = useMemo(
    () => data?.days.filter((day) => day.closedReason !== "WEEKEND") ?? [],
    [data],
  );
  const todayIso = toLocalDateKey(new Date());
  const upcomingHolidays = useMemo(
    () => holidays.filter((holiday) => !isPastHolidayDate(holiday.holidayDate, todayIso)),
    [holidays, todayIso],
  );
  const pastHolidays = useMemo(
    () => holidays.filter((holiday) => isPastHolidayDate(holiday.holidayDate, todayIso)),
    [holidays, todayIso],
  );
  const visibleHolidays = showPastHolidays ? holidays : upcomingHolidays;
  const weekStats = summarizeHqWeek(visibleDays, todayIso, unitFilter);
  const destinationCodesThisWeek = useMemo(() => {
    const codes = new Set<string>();
    let hasUnassigned = false;
    for (const day of visibleDays) {
      for (const slot of day.slots) {
        for (const visit of slot.scheduledCases ?? []) {
          const code = visit.destinationUnitCode?.trim();
          if (code) codes.add(code);
          else hasUnassigned = true;
        }
      }
    }
    return { codes, hasUnassigned };
  }, [visibleDays]);
  const unitFilterChips = useMemo(() => {
    const chips = pusatUnits.filter((unit) =>
      destinationCodesThisWeek.codes.has(unit.code),
    );
    return { chips, hasUnassigned: destinationCodesThisWeek.hasUnassigned };
  }, [destinationCodesThisWeek, pusatUnits]);
  const showUnitFilters = canSeeDetail && unitFilterChips.chips.length > 0;

  useEffect(() => {
    if (!unitFilter) return;
    const stillVisible =
      unitFilter === UNASSIGNED_UNIT_FILTER
        ? unitFilterChips.hasUnassigned
        : unitFilterChips.chips.some((unit) => unit.code === unitFilter);
    if (!stillVisible) setUnitFilter(null);
  }, [unitFilter, unitFilterChips]);

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
  const hasOpenSlots = visibleDays.some(
    (day) => !day.closed && day.slots.length > 0,
  );
  const viewingThisWeek =
    toLocalDateKey(weekStart) === toLocalDateKey(startOfWeek(new Date()));
  const isPastWeek = toLocalDateKey(addDays(weekStart, RANGE_DAYS)) < todayIso;
  const todayPending = weekStats.today - weekStats.todayCompleted;
  const todayBreakdown =
    weekStats.today > 0
      ? t("todayBreakdownLabel", {
          completed: weekStats.todayCompleted,
          pending: todayPending,
        })
      : null;
  const weekNavButtonClass =
    "!rounded-none !border-0 !shadow-none min-w-[var(--ecmp-touch-min)] sm:min-w-0";

  return (
    <PageContainer>
      <PageHeader
        title={t("title")}
        description={t("description")}
        actions={
          <div
            role="group"
            aria-label={t("weekNavigationLabel")}
            className="inline-flex divide-x divide-ecmp-border overflow-hidden rounded-[var(--ecmp-radius-button)] border border-ecmp-border bg-ecmp-surface shadow-ecmp-surface"
          >
            <Button
              variant="ghost"
              size="sm"
              className={weekNavButtonClass}
              aria-label={t("previousWeek")}
              leftIcon={<IconChevronRight className="size-4 rotate-180" aria-hidden />}
              onClick={() => setWeekStart((prev) => addDays(prev, -7))}
            >
              <span className="hidden sm:inline">{t("previousWeek")}</span>
            </Button>
            <Button
              variant={viewingThisWeek ? "ghost" : "primary"}
              size="sm"
              className={weekNavButtonClass}
              disabled={viewingThisWeek}
              onClick={() => setWeekStart(startOfWeek(new Date()))}
            >
              {t("thisWeek")}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className={weekNavButtonClass}
              aria-label={t("nextWeek")}
              rightIcon={<IconChevronRight className="size-4" aria-hidden />}
              onClick={() => setWeekStart((prev) => addDays(prev, 7))}
            >
              <span className="hidden sm:inline">{t("nextWeek")}</span>
            </Button>
          </div>
        }
      />

      {showLoading && <Loading label={t("loading")} />}
      {!showLoading && error && <ErrorState message={t("loadError")} />}

      {!showLoading && !error && data && (
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <StatCard
              hierarchy="supporting"
              accent="normal"
              title={t("weekArrivalsLabel")}
              value={<span className="tabular-nums">{weekStats.scheduled}</span>}
              className="flex flex-row items-center justify-between gap-2 !p-3 md:!p-3.5 [&>p]:!mt-0 [&>div>p]:!text-[length:var(--ecmp-font-helper-size)] [&>p]:!text-[length:var(--ecmp-font-card-title-size)]"
            />
            <StatCard
              hierarchy="supporting"
              accent={todayAccent(visibleDays, todayIso, nowMs)}
              title={t("todayArrivalsLabel")}
              value={
                <span className="flex flex-col items-end gap-0.5">
                  <span className="tabular-nums">{weekStats.today}</span>
                  {todayBreakdown ? (
                    <span className="text-[length:var(--ecmp-font-caption-size)] font-normal text-ecmp-text-secondary">
                      {todayBreakdown}
                    </span>
                  ) : null}
                </span>
              }
              className="flex flex-row items-center justify-between gap-2 !p-3 md:!p-3.5 [&>p]:!mt-0 [&>div>p]:!text-[length:var(--ecmp-font-helper-size)] [&>p]:!text-[length:var(--ecmp-font-card-title-size)]"
            />
            <StatCard
              hierarchy="supporting"
              accent="healthy"
              title={isPastWeek ? t("weekCompletedLabel") : t("emptySlotsLabel")}
              value={
                <span className="tabular-nums">
                  {isPastWeek ? weekStats.weekCompleted : weekStats.bookable}
                </span>
              }
              className="flex flex-row items-center justify-between gap-2 !p-3 md:!p-3.5 [&>p]:!mt-0 [&>div>p]:!text-[length:var(--ecmp-font-helper-size)] [&>p]:!text-[length:var(--ecmp-font-card-title-size)]"
            />
          </div>

          {!hasOpenSlots ? (
            <p className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-surface p-3 text-center text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("weekClosed")}
            </p>
          ) : (
            <div className="space-y-2">
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary lg:hidden">
                {t("boardSwipeHint")}
              </p>
              {showUnitFilters ? (
                <div
                  role="group"
                  aria-label={t("unitFilterLabel")}
                  className="flex flex-wrap gap-1.5"
                  data-testid="hq-schedule-unit-filter"
                >
                  {unitFilterChips.chips.map((unit) => (
                    <Button
                      key={unit.code}
                      type="button"
                      size="sm"
                      variant={unitFilter === unit.code ? "primary" : "secondary"}
                      onClick={() => setUnitFilter(unit.code)}
                    >
                      {unit.name}
                    </Button>
                  ))}
                </div>
              ) : null}
              <div
                data-testid="hq-schedule-board"
                role="region"
                aria-label={t("boardRegionLabel")}
                className="flex snap-x snap-mandatory gap-2 overflow-x-auto overscroll-x-contain pb-1"
              >
                {visibleDays.map((day) => {
                  const isPastDay = day.date < todayIso;
                  let summaryLabel: string | null = null;
                  if (isPastDay && !day.closed) {
                    const totals = dayOccupancyTotals(day, unitFilter);
                    if (totals.scheduled > 0) {
                      const base = t("daySummaryLabel", {
                        scheduled: totals.scheduled,
                        pending: totals.scheduled - totals.completed,
                      });
                      if (unitFilter === null) {
                        const parts = dayUnitBreakdown(day).map((row) =>
                          row.code
                            ? t("dayUnitCount", {
                                unit: pusatUnitShortCode(row.code),
                                count: row.count,
                              })
                            : t("dayUnassignedCount", { count: row.count }),
                        );
                        summaryLabel =
                          parts.length > 0
                            ? `${base} · ${parts.join(" · ")}`
                            : base;
                      } else {
                        summaryLabel = base;
                      }
                    }
                  }
                  return (
                    <DayColumn
                      key={day.date}
                      day={day}
                      isToday={day.date === todayIso}
                      isPast={isPastDay}
                      summaryLabel={summaryLabel}
                      unitFilter={unitFilter}
                      weekdayLabel={weekdayFormatterLong.format(
                        new Date(`${day.date}T00:00:00`),
                      )}
                      todayLabel={t("todayLabel")}
                      canOpenCase={canOpenCase}
                      slotRatio={(slot) =>
                        slotRatioText(day.date, slot, nowMs, t, unitFilter)
                      }
                      breakLabel={t("breakLabel")}
                      holidayLabel={t("holiday")}
                      weekendLabel={t("weekend")}
                      columnRef={day.date === todayIso ? todayColumnRef : undefined}
                      nowMs={nowMs}
                    />
                  );
                })}
              </div>
            </div>
          )}

          {showHolidayPanel ? (
            <details
              data-testid="hq-schedule-holiday-panel"
              className="rounded-[var(--ecmp-radius-card)] border border-ecmp-border/80 bg-ecmp-surface shadow-ecmp-raised"
            >
              <summary className="flex cursor-pointer items-center justify-between gap-3 px-[var(--ecmp-card-padding)] py-3 text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
                <span className="flex min-w-0 flex-wrap items-center gap-2">
                  {t("holidayManageTitle")}
                  <Badge tone="info">
                    {t("holidayCountBadge", {
                      count: upcomingHolidays.length,
                      year: importYear,
                    })}
                  </Badge>
                </span>
              </summary>
              <Card className="rounded-none border-0 shadow-none" padding={false}>
                <CardBody className="space-y-4 border-t border-ecmp-border px-[var(--ecmp-card-padding)] py-[var(--ecmp-panel-gap)]">
                  <div className="flex flex-wrap items-end justify-between gap-3">
                    <div className="w-[9.5rem] shrink-0">
                      <Select
                        label={t("holidayImportYearLabel")}
                        value={importYear}
                        onChange={(e) => {
                          setImportYear(e.target.value);
                          setCatalogPreview(null);
                          setSelectedImportDates(new Set());
                          setShowPastHolidays(false);
                        }}
                        options={importYearOptions(new Date().getFullYear())}
                        disabled={importing}
                      />
                    </div>
                    {pastHolidays.length > 0 ? (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="px-3"
                        onClick={() => setShowPastHolidays((prev) => !prev)}
                      >
                        {showPastHolidays
                          ? t("holidayHidePast")
                          : t("holidayShowPast", { count: pastHolidays.length })}
                      </Button>
                    ) : null}
                  </div>

                  {holidays.length === 0 ? (
                    <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                      {t("holidayEmpty", { year: importYear })}
                    </p>
                  ) : visibleHolidays.length === 0 ? (
                    <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                      {t("holidayEmptyUpcoming", { year: importYear })}
                    </p>
                  ) : (
                    <ul className="overflow-hidden rounded-[var(--ecmp-radius-md)] border border-ecmp-border/80">
                      {visibleHolidays.map((holiday) => {
                        const kindLabel = holidayKindLabel(holiday.kind, t);
                        const past = isPastHolidayDate(holiday.holidayDate, todayIso);
                        return (
                          <li
                            key={holiday.holidayDate}
                            className={cn(
                              "flex flex-wrap items-center gap-3 border-b border-ecmp-border/60 px-3.5 py-2.5 last:border-b-0",
                              past && "opacity-60",
                            )}
                          >
                            <span className="inline-flex min-w-[3.25rem] justify-center rounded-[var(--ecmp-radius-sm)] bg-ecmp-primary-muted px-2 py-1 text-[length:var(--ecmp-font-caption-size)] font-semibold tabular-nums text-ecmp-primary">
                              {holidayChipDate(holiday.holidayDate, locale)}
                            </span>
                            <span className="min-w-0 flex-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                              <span className="capitalize text-ecmp-text-secondary">
                                {weekdayFormatterLong.format(
                                  new Date(`${holiday.holidayDate}T00:00:00`),
                                )}
                              </span>
                              {" · "}
                              {holiday.label}
                              {kindLabel ? (
                                <Badge
                                  tone={
                                    holiday.kind === "CUTI_BERSAMA"
                                      ? "warning"
                                      : "info"
                                  }
                                  className="ml-2 align-middle"
                                >
                                  {kindLabel}
                                </Badge>
                              ) : null}
                            </span>
                            {canManageHolidays ? (
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                className="px-3"
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
                        );
                      })}
                    </ul>
                  )}

                  {canManageHolidays ? (
                    <div className="space-y-3 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-[color-mix(in_srgb,var(--ecmp-color-text-primary)_3%,var(--ecmp-color-surface))] p-4">
                      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                        {t("holidayImportHint")}
                      </p>
                      <p className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border/60 bg-ecmp-surface px-3 py-2 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                        {t("holidayImportNote")}
                      </p>
                      {catalogPreview == null ? (
                        <Button
                          type="button"
                          variant="secondary"
                          className="px-5"
                          loading={importing}
                          onClick={() => void openImportPreview()}
                        >
                          {t("holidayImportButton", { year: importYear })}
                        </Button>
                      ) : (
                        <div
                          className="space-y-3"
                          data-testid="hq-schedule-holiday-import-preview"
                        >
                          <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-primary">
                            {t("holidayImportPreviewTitle")}
                            {catalogPreview.sourceName
                              ? ` · ${catalogPreview.sourceName}`
                              : ""}
                          </p>
                          <div className="flex flex-wrap gap-2">
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="px-3"
                              onClick={() =>
                                setSelectedImportDates(
                                  new Set(
                                    catalogPreview.entries
                                      .filter(
                                        (entry) =>
                                          !isPastHolidayDate(
                                            entry.holidayDate,
                                            todayIso,
                                          ),
                                      )
                                      .map((entry) => entry.holidayDate),
                                  ),
                                )
                              }
                            >
                              {t("holidaySelectAll")}
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="px-3"
                              onClick={() => setSelectedImportDates(new Set())}
                            >
                              {t("holidaySelectNone")}
                            </Button>
                          </div>
                          <ul className="max-h-80 space-y-1 overflow-y-auto">
                            {catalogPreview.entries
                              .filter(
                                (entry) =>
                                  showPastHolidays ||
                                  !isPastHolidayDate(entry.holidayDate, todayIso),
                              )
                              .map((entry) => (
                              <li key={entry.holidayDate}>
                                <Checkbox
                                  id={`import-${entry.holidayDate}`}
                                  checked={selectedImportDates.has(entry.holidayDate)}
                                  onChange={(event) =>
                                    toggleImportDate(
                                      entry.holidayDate,
                                      event.target.checked,
                                    )
                                  }
                                  labelContent={
                                    <span>
                                      {holidayChipDate(entry.holidayDate, locale)}{" "}
                                      {entry.label}
                                      {entry.alreadyExists ? (
                                        <span className="ml-2 text-ecmp-text-secondary">
                                          ({t("holidayAlreadyExists")})
                                        </span>
                                      ) : null}
                                    </span>
                                  }
                                />
                              </li>
                            ))}
                          </ul>
                          <div className="flex flex-wrap gap-2">
                            <Button
                              type="button"
                              className="px-5"
                              loading={importing}
                              disabled={selectedImportDates.size === 0}
                              onClick={() => void submitImportHolidays()}
                            >
                              {t("holidayImportConfirm", {
                                count: selectedImportDates.size,
                              })}
                            </Button>
                            <Button
                              type="button"
                              variant="outline"
                              className="px-4"
                              disabled={importing}
                              onClick={() => {
                                setCatalogPreview(null);
                                setSelectedImportDates(new Set());
                              }}
                            >
                              {t("holidayImportCancel")}
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : null}

                  {canManageHolidays ? (
                    <div className="grid grid-cols-1 items-end gap-3 rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-border px-4 py-3 sm:grid-cols-[minmax(0,11rem)_minmax(0,1fr)_auto]">
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
                        className="px-5"
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
            </details>
          ) : null}
        </div>
      )}
    </PageContainer>
  );
}
