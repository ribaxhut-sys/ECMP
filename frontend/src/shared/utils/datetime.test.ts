import { describe, expect, it } from "vitest";
import {
  formatDateTime24,
  formatHqArrivalSlot,
  parseHqArrivalScheduleBlob,
  resolveHqArrivalDisplay,
  toLocalDateKey,
} from "./datetime";

describe("formatDateTime24", () => {
  it("formats in Indonesian long month and Jakarta time", () => {
    expect(formatDateTime24("2026-08-14T03:51:00.000Z", "id")).toBe(
      "14 Agustus 2026, 10.51",
    );
  });

  it("follows the selected locale instead of the browser", () => {
    expect(formatDateTime24("2026-08-14T03:51:00.000Z", "en")).toBe(
      "August 14, 2026, 10:51",
    );
  });

  it("falls back to the default locale for unknown codes", () => {
    expect(formatDateTime24("2026-08-14T03:51:00.000Z", "fr")).toBe(
      "14 Agustus 2026, 10.51",
    );
  });

  it("returns the empty placeholder for blank values", () => {
    expect(formatDateTime24(null, "id", "—")).toBe("—");
    expect(formatDateTime24("", "id", "—")).toBe("—");
  });
});

describe("toLocalDateKey", () => {
  it("uses Asia/Jakarta, not UTC", () => {
    // 17:00 UTC 16 Aug = 00:00 WIB 17 Aug
    expect(toLocalDateKey(new Date("2026-08-16T17:00:00.000Z"))).toBe("2026-08-17");
    // 16:59 UTC 16 Aug = 23:59 WIB 16 Aug
    expect(toLocalDateKey(new Date("2026-08-16T16:59:59.000Z"))).toBe("2026-08-16");
  });
});

describe("formatHqArrivalSlot", () => {
  it("formats weekday, calendar date, and Jakarta time", () => {
    expect(formatHqArrivalSlot("2026-08-20", "09:30", "id")).toEqual({
      weekday: "Kamis",
      date: "20 Agustus 2026",
      time: "09.30",
    });
    expect(formatHqArrivalSlot("2026-08-20", "09:30", "en")).toEqual({
      weekday: "Thursday",
      date: "August 20, 2026",
      time: "09:30",
    });
  });

  it("rejects malformed calendar values", () => {
    expect(formatHqArrivalSlot("20-08-2026", "09:30", "id")).toBeNull();
    expect(formatHqArrivalSlot("2026-08-20", "9:30", "id")).toBeNull();
  });
});

describe("parseHqArrivalScheduleBlob", () => {
  it("reads the ISO first line and keeps the WP note", () => {
    expect(
      parseHqArrivalScheduleBlob("2026-08-20 09:30\nBawa dokumen asli"),
    ).toEqual({
      date: "2026-08-20",
      time: "09:30",
      wpNote: "Bawa dokumen asli",
    });
  });

  it("accepts the operator copy form with pukul", () => {
    expect(parseHqArrivalScheduleBlob("2026-08-20 pukul 09.30")).toEqual({
      date: "2026-08-20",
      time: "09:30",
      wpNote: "",
    });
  });

  it("returns null for a plain operator note", () => {
    expect(parseHqArrivalScheduleBlob("Bawa dokumen asli")).toBeNull();
  });
});

describe("resolveHqArrivalDisplay", () => {
  it("prefers structured fields and does not treat a later slot as this event", () => {
    expect(
      resolveHqArrivalDisplay({
        arrivalDate: "2026-08-20",
        arrivalTime: "09:30",
        note: "Bawa dokumen asli",
      }),
    ).toEqual({
      date: "2026-08-20",
      time: "09:30",
      wpNote: "Bawa dokumen asli",
    });
  });

  it("strips a legacy blob prefix when structured fields exist", () => {
    expect(
      resolveHqArrivalDisplay({
        arrivalDate: "2026-08-20",
        arrivalTime: "09:30",
        note: "2026-08-20 09:30\nLoket 2",
      }),
    ).toEqual({
      date: "2026-08-20",
      time: "09:30",
      wpNote: "Loket 2",
    });
  });

  it("falls back to the blob when structured fields are missing", () => {
    expect(
      resolveHqArrivalDisplay({
        note: "2026-08-20 09:30\nBawa dokumen asli",
      }),
    ).toEqual({
      date: "2026-08-20",
      time: "09:30",
      wpNote: "Bawa dokumen asli",
    });
  });
});
