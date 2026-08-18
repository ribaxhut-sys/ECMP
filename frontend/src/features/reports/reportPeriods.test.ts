import { describe, expect, it } from "vitest";
import {
  DEFAULT_REPORT_PERIOD,
  REPORT_PERIOD_KEYS,
  REPORT_PERIOD_LABEL_KEY,
  reportPeriodRange,
} from "./reportPeriods";

/** 17:30 WIB on 18 Aug 2026 — same calendar day as the UTC clock. */
const NOW = new Date("2026-08-18T10:30:00.000Z");

describe("reportPeriodRange", () => {
  it("sends no window for the all-time default", () => {
    expect(DEFAULT_REPORT_PERIOD).toBe("all");
    expect(reportPeriodRange("all", NOW)).toEqual({});
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
