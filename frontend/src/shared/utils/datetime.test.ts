import { describe, expect, it } from "vitest";
import { formatDateTime24, toLocalDateKey } from "./datetime";

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
