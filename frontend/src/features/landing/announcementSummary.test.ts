import { describe, expect, it } from "vitest";
import { summarize } from "./announcementSummary";

describe("summarize", () => {
  it("returns the body unchanged when already short", () => {
    expect(summarize("Sistem akan pemeliharaan.")).toBe(
      "Sistem akan pemeliharaan.",
    );
  });

  it("collapses internal whitespace", () => {
    expect(summarize("Baris satu\n\nBaris   dua")).toBe(
      "Baris satu Baris dua",
    );
  });

  it("truncates at a word boundary and adds an ellipsis", () => {
    const body = "kata ".repeat(50).trim();
    const result = summarize(body, 20);
    expect(result.endsWith("…")).toBe(true);
    expect(result.length).toBeLessThanOrEqual(21);
    expect(result.startsWith("kata kata")).toBe(true);
  });

  it("hard-truncates when there is no earlier space", () => {
    const body = "a".repeat(50);
    const result = summarize(body, 10);
    expect(result).toBe("aaaaaaaaaa…");
  });
});
