/**
 * HQ arrival schedule API client — branch-facing aggregate slot availability
 * (escalation slot picker) and Pusat detail view (pending proposals).
 */
import { apiRequest } from "./client";
import type { DataResponse } from "./types";

export type HqScheduleClosedReason = "WEEKEND" | "HOLIDAY";

export interface HqScheduleCaseRef {
  caseId: string;
  caseNumber: string;
}

export interface HqScheduleProposalSummary {
  complaintId: string;
  complaintNumber: string;
  owningUnitId?: string | null;
  unitCode: string;
  /** Case(s) tracking this complaint's escalation — empty for pending proposals. */
  cases: HqScheduleCaseRef[];
  proposedBy?: string | null;
  proposedAt?: string | null;
  /** HQ visit completed (HQ_CLOSED) — still listed that day and counted in the slot ratio. */
  completed?: boolean;
  /** Pusat unit the taxpayer reports to. Empty on pending proposals and legacy rows. */
  destinationUnitCode?: string | null;
  /**
   * Taxpayer display name (Master Customer, read-only). Pusat detail: all
   * occupants. Branch aggregate: caller's own unit only — other units omit it.
   */
  customerDisplayName?: string | null;
}

export interface HqScheduleSlotAvailability {
  startTime: string;
  endTime: string;
  capacity: number;
  isBreak: boolean;
  /**
   * Slot shortened by a break that does not fall on a grid boundary (Jumat
   * 11:00–11:30 / 13:30–14:00) — `capacity` is pro-rated, not the nominal
   * `capacityPerSlot`.
   */
  partial?: boolean;
  /** Total occupants (live + completed) — the slot's booked ratio. */
  scheduledCount: number;
  /** Subset of scheduledCount whose HQ visit is already closed. */
  completedCount: number;
  proposedCount: number;
  /** Raw capacity left (capacity - scheduledCount); not time-aware. */
  availableCount: number;
  /** Open day, not a break, slot start still in the future, capacity left. */
  bookable: boolean;
  /** availableCount when bookable, else 0 — what a picker should offer. */
  bookableCount: number;
  /** Pusat detail view only — empty on the branch-facing aggregate view. */
  pendingProposals: HqScheduleProposalSummary[];
  /** Pusat detail view only — empty on the branch-facing aggregate view. */
  scheduledCases: HqScheduleProposalSummary[];
  /** Per-destination occupancy. Pusat detail only — empty on the branch aggregate. */
  units?: HqScheduleUnitAvailability[];
}

export interface HqScheduleUnitAvailability {
  unitCode: string;
  unitName: string;
  capacity: number;
  scheduledCount: number;
  completedCount: number;
  availableCount: number;
  bookable: boolean;
}

export interface HqScheduleDayAvailability {
  date: string;
  weekday: number;
  closed: boolean;
  closedReason?: HqScheduleClosedReason | null;
  holidayLabel?: string | null;
  slots: HqScheduleSlotAvailability[];
}

export interface HqScheduleAvailabilityResponse {
  startTime: string;
  endTime: string;
  slotMinutes: number;
  /** Nominal capacity of a full-length slot — read slot.capacity for ratios. */
  capacityPerSlot: number;
  days: HqScheduleDayAvailability[];
}

export interface HqScheduleHoliday {
  holidayDate: string;
  label: string;
  createdBy?: string | null;
  createdAt: string;
}

function rangeQuery(dateFrom?: string, dateTo?: string): string {
  const params = new URLSearchParams();
  if (dateFrom) params.set("from", dateFrom);
  if (dateTo) params.set("to", dateTo);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

/** Branch-facing aggregate view — used inline in the escalation slot picker. */
export function fetchHqScheduleAvailability(
  dateFrom?: string,
  dateTo?: string,
): Promise<DataResponse<HqScheduleAvailabilityResponse>> {
  return apiRequest<DataResponse<HqScheduleAvailabilityResponse>>(
    `/api/v1/hq-schedule/availability${rangeQuery(dateFrom, dateTo)}`,
  );
}

/** Pusat-only detail view — same grid, plus per-slot pending proposals. */
export function fetchHqScheduleAvailabilityDetail(
  dateFrom?: string,
  dateTo?: string,
): Promise<DataResponse<HqScheduleAvailabilityResponse>> {
  return apiRequest<DataResponse<HqScheduleAvailabilityResponse>>(
    `/api/v1/hq-schedule/availability/detail${rangeQuery(dateFrom, dateTo)}`,
  );
}

export function fetchHqScheduleHolidays(
  dateFrom?: string,
  dateTo?: string,
): Promise<DataResponse<HqScheduleHoliday[]>> {
  return apiRequest<DataResponse<HqScheduleHoliday[]>>(
    `/api/v1/hq-schedule/holidays${rangeQuery(dateFrom, dateTo)}`,
  );
}

export function createHqScheduleHoliday(body: {
  holidayDate: string;
  label: string;
}): Promise<DataResponse<HqScheduleHoliday>> {
  return apiRequest<DataResponse<HqScheduleHoliday>>("/api/v1/hq-schedule/holidays", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function deleteHqScheduleHoliday(holidayDate: string): Promise<void> {
  return apiRequest<void>(
    `/api/v1/hq-schedule/holidays/${encodeURIComponent(holidayDate)}`,
    { method: "DELETE" },
  );
}
