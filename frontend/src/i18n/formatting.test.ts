import { describe, expect, it } from "vitest";
import { formatDate } from "./formatting";

describe("formatDate", () => {
  it("renders DD-MM-YYYY for the id locale by default", () => {
    expect(formatDate("2026-08-14T03:51:00.000Z", "id")).toBe("14-08-2026");
  });

  it("renders the same DD-MM-YYYY order for the en locale — never MM-DD-YYYY", () => {
    expect(formatDate("2026-08-14T03:51:00.000Z", "en")).toBe("14-08-2026");
  });

  it("still honors explicit narrative options, per locale", () => {
    const options: Intl.DateTimeFormatOptions = {
      day: "numeric",
      month: "long",
      year: "numeric",
    };
    expect(formatDate("2026-08-14T03:51:00.000Z", "id", options)).toBe(
      "14 Agustus 2026",
    );
    expect(formatDate("2026-08-14T03:51:00.000Z", "en", options)).toBe(
      "August 14, 2026",
    );
  });

  it("returns empty string for missing or unparseable values", () => {
    expect(formatDate(null, "id")).toBe("");
    expect(formatDate(undefined, "id")).toBe("");
    expect(formatDate("", "id")).toBe("");
    expect(formatDate("not a date", "id")).toBe("");
  });
});
