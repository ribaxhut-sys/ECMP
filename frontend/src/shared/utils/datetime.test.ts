import { describe, expect, it } from "vitest";
import { formatDateTime24 } from "./datetime";

describe("formatDateTime24", () => {
  it("formats in Indonesian short month and Jakarta time", () => {
    expect(formatDateTime24("2026-08-14T03:51:00.000Z")).toBe(
      "14 Agu 2026, 10.51",
    );
  });

  it("returns the empty placeholder for blank values", () => {
    expect(formatDateTime24(null, "—")).toBe("—");
    expect(formatDateTime24("", "—")).toBe("—");
  });
});
