import { describe, expect, it } from "vitest";
import {
  COMPLAINT_SUMMARY_MAX_CHARS,
  summarizeComplaintNarrative,
} from "./complaintSummary";

describe("summarizeComplaintNarrative", () => {
  it("returns short text unchanged", () => {
    expect(summarizeComplaintNarrative("Singkat")).toEqual({
      text: "Singkat",
      truncated: false,
    });
  });

  it("truncates long text near a word boundary", () => {
    const words = Array.from({ length: 80 }, (_, i) => `kata${i}`).join(" ");
    const result = summarizeComplaintNarrative(words, 40);
    expect(result.truncated).toBe(true);
    expect(result.text.endsWith("…")).toBe(true);
    expect(result.text.length).toBeLessThanOrEqual(42);
  });

  it("uses the default max length", () => {
    const long = "a".repeat(COMPLAINT_SUMMARY_MAX_CHARS + 10);
    const result = summarizeComplaintNarrative(long);
    expect(result.truncated).toBe(true);
    expect(result.text.length).toBeLessThanOrEqual(
      COMPLAINT_SUMMARY_MAX_CHARS + 1,
    );
  });
});
