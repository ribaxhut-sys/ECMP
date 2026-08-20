/**
 * HQ arrival schedule API client — branch-facing aggregate slot availability
 * (escalation slot picker) and Pusat detail view (pending proposals).
 */
import { apiRequest } from "./client";
import type { DataResponse } from "./types";

export type HqScheduleClosedReason = "WEEKEND" | "HOLIDAY";

export interface HqScheduleProposalSummary {
  complaintId: string;
  complaintNumber: string;
  owningUnitId?: string | null;
  unitCode: string;
  /** Case(s) tracking this complaint's escalation — empty for pending proposals. */
  caseNumbers: string[];
  proposedBy?: string | null;
  proposedAt?: string | null;
  /** HQ visit completed (HQ_CLOSED) — still listed that day; does not consume capacity. */
  completed?: boolean;
}

export interface HqScheduleSlotAvailability {
  startTime: string;
  endTime: string;
  capacity: number;
  isBreak: boolean;
  scheduledCount: number;
  proposedCount: number;
  availableCount: number;
  /** Pusat detail view only — empty on the branch-facing aggregate view. */
  pendingProposals: HqScheduleProposalSummary[];
  /** Pusat detail view only — empty on the branch-facing aggregate view. */
  scheduledCases: HqScheduleProposalSummary[];
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
