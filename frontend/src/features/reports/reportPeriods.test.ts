import { describe, expect, it } from "vitest";
import {
  DEFAULT_REPORT_PERIOD,
  REPORT_PERIOD_KEYS,
  REPORT_PERIOD_LABEL_KEY,
  previousReportPeriodRange,
  reportPeriodRange,
} from "./reportPeriods";

/** 17:30 WIB on 18 Aug 2026 — same calendar day as the UTC clock. */
const NOW = new Date("2026-08-18T10:30:00.000Z");

describe("reportPeriodRange", () => {
  it("sends no window for the all-time default", () => {
    expect(DEFAULT_REPORT_PERIOD).toBe("all");
    expect(reportPeriodRange("all", NOW)).toEqual({});
  });

  it("spans the current Jakarta week (Monday start) up to the end of today WIB", () => {
    // 18 Aug 2026 WIB is a Tuesday — the week started Monday 17 Aug.
    expect(reportPeriodRange("thisWeek", NOW)).toEqual({
      dateFrom: "2026-08-16T17:00:00.000Z",
      dateTo: "2026-08-18T16:59:59.999Z",
    });
  });

  it("rolls the week start across a month boundary", () => {
    // 1 Sep 2026 WIB is a Tuesday — the week started Monday 31 Aug.
    const range = reportPeriodRange(
      "thisWeek",
      new Date("2026-08-31T19:00:00.000Z"),
    );
    expect(range.dateFrom).toBe("2026-08-30T17:00:00.000Z");
    expect(range.dateTo).toBe("2026-09-01T16:59:59.999Z");
  });

  it("spans the current Jakarta month up to the end of today WIB", () => {
    expect(reportPeriodRange("thisMonth", NOW)).toEqual({
      dateFrom: "2026-07-31T17:00:00.000Z",
      dateTo: "2026-08-18T16:59:59.999Z",
    });
  });

  it("closes the previous Jakarta month on its last instant", () => {
    expect(reportPeriodRange("lastMonth", NOW)).toEqual({
      dateFrom: "2026-06-30T17:00:00.000Z",
      dateTo: "2026-07-31T16:59:59.999Z",
    });
  });

  it("rolls the previous month across a year boundary", () => {
    const range = reportPeriodRange(
      "lastMonth",
      new Date("2026-01-09T00:00:00.000Z"),
    );
    expect(range.dateFrom).toBe("2025-11-30T17:00:00.000Z");
    expect(range.dateTo).toBe("2025-12-31T16:59:59.999Z");
  });

  it("does not put 1 Sep 02:00 WIB into last-month of August", () => {
    const firstOfSeptemberWib = new Date("2026-08-31T19:00:00.000Z");
    const range = reportPeriodRange("thisMonth", firstOfSeptemberWib);
    expect(range.dateFrom).toBe("2026-08-31T17:00:00.000Z");
  });

  it("counts 90 Jakarta days inclusive of today", () => {
    expect(reportPeriodRange("last90", NOW)).toEqual({
      dateFrom: "2026-05-20T17:00:00.000Z",
      dateTo: "2026-08-18T16:59:59.999Z",
    });
  });

  it("starts the year on 1 January Jakarta time", () => {
    expect(reportPeriodRange("thisYear", NOW).dateFrom).toBe(
      "2025-12-31T17:00:00.000Z",
    );
  });

  it("labels every preset", () => {
    for (const key of REPORT_PERIOD_KEYS) {
      expect(REPORT_PERIOD_LABEL_KEY[key]).toBeTruthy();
    }
  });
});

describe("previousReportPeriodRange", () => {
  it("has no predecessor for all-time", () => {
    expect(previousReportPeriodRange("all", NOW)).toBeNull();
  });

  it("shifts this week back seven Jakarta days", () => {
    expect(previousReportPeriodRange("thisWeek", NOW)).toEqual({
      dateFrom: "2026-08-09T17:00:00.000Z",
      dateTo: "2026-08-11T16:59:59.999Z",
    });
  });

  it("compares this month to the same days last month", () => {
    expect(previousReportPeriodRange("thisMonth", NOW)).toEqual({
      dateFrom: "2026-06-30T17:00:00.000Z",
      dateTo: "2026-07-18T16:59:59.999Z",
    });
  });

  it("compares last month to the full month before it", () => {
    expect(previousReportPeriodRange("lastMonth", NOW)).toEqual({
      dateFrom: "2026-05-31T17:00:00.000Z",
      dateTo: "2026-06-30T16:59:59.999Z",
    });
  });

  it("places the prior 90 days immediately before the current 90", () => {
    expect(previousReportPeriodRange("last90", NOW)).toEqual({
      dateFrom: "2026-02-19T17:00:00.000Z",
      dateTo: "2026-05-20T16:59:59.999Z",
    });
  });

  it("compares this year to the same calendar date last year", () => {
    expect(previousReportPeriodRange("thisYear", NOW)).toEqual({
      dateFrom: "2024-12-31T17:00:00.000Z",
      dateTo: "2025-08-18T16:59:59.999Z",
    });
  });
});
