import { describe, expect, it } from "vitest";
import {
  DEFAULT_REPORT_PERIOD,
  REPORT_PERIOD_KEYS,
  REPORT_PERIOD_LABEL_KEY,
  reportPeriodRange,
} from "./reportPeriods";

const NOW = new Date("2026-08-18T10:30:00.000Z");

describe("reportPeriodRange", () => {
  it("sends no window for the all-time default", () => {
    expect(DEFAULT_REPORT_PERIOD).toBe("all");
    expect(reportPeriodRange("all", NOW)).toEqual({});
  });

  it("spans the current month up to the end of today", () => {
    expect(reportPeriodRange("thisMonth", NOW)).toEqual({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-18T23:59:59.999Z",
    });
  });

  it("closes the previous month on its last instant", () => {
    expect(reportPeriodRange("lastMonth", NOW)).toEqual({
      dateFrom: "2026-07-01T00:00:00.000Z",
      dateTo: "2026-07-31T23:59:59.999Z",
    });
  });

  it("rolls the previous month across a year boundary", () => {
    const range = reportPeriodRange("lastMonth", new Date("2026-01-09T00:00:00.000Z"));
    expect(range.dateFrom).toBe("2025-12-01T00:00:00.000Z");
    expect(range.dateTo).toBe("2025-12-31T23:59:59.999Z");
  });

  it("counts 90 days inclusive of today", () => {
    expect(reportPeriodRange("last90", NOW)).toEqual({
      dateFrom: "2026-05-21T00:00:00.000Z",
      dateTo: "2026-08-18T23:59:59.999Z",
    });
  });

  it("starts the year on 1 January", () => {
    expect(reportPeriodRange("thisYear", NOW).dateFrom).toBe(
      "2026-01-01T00:00:00.000Z",
    );
  });

  it("labels every preset", () => {
    for (const key of REPORT_PERIOD_KEYS) {
      expect(REPORT_PERIOD_LABEL_KEY[key]).toBeTruthy();
    }
  });
});
