import { describe, expect, it } from "vitest";
import {
  caseHistoryDisplayLabelKey,
  filterWpCaseHistoryEntries,
  isWpCaseHistoryHidden,
  shouldShowCaseHistoryPriority,
} from "./caseHistoryMeta";

describe("filterWpCaseHistoryEntries", () => {
  it("hides Internal dual-acceptance codes from taxpayer Case logs", () => {
    expect(isWpCaseHistoryHidden("CASE_OWNER_ACCEPTED")).toBe(true);
    expect(isWpCaseHistoryHidden("case_owner_rejected")).toBe(true);
    expect(isWpCaseHistoryHidden("CASE_HANDLING_UNIT_ACCEPTED")).toBe(true);
    expect(isWpCaseHistoryHidden("CASE_CLOSED")).toBe(false);

    const visible = filterWpCaseHistoryEntries([
      { eventCode: "CASE_RESOLVED" },
      { eventCode: "CASE_OWNER_ACCEPTED" },
      { eventCode: "CASE_HANDLING_UNIT_ACCEPTED" },
      { eventCode: "CASE_CLOSED" },
    ]);
    expect(visible.map((row) => row.eventCode)).toEqual([
      "CASE_RESOLVED",
      "CASE_CLOSED",
    ]);
  });
});

describe("caseHistoryDisplayLabelKey", () => {
  it("keeps the first send-to-HQ label", () => {
    expect(caseHistoryDisplayLabelKey("CASE_ESCALATED_TO_PUSAT", [])).toBe(
      "eventCaseEscalatedToPusat",
    );
  });

  it("labels a later send after HQ return as re-escalation", () => {
    expect(
      caseHistoryDisplayLabelKey("CASE_ESCALATED_TO_PUSAT", [
        "CASE_ESCALATED_TO_PUSAT",
        "CASE_ESCALATION_RETURNED",
      ]),
    ).toBe("eventCaseReEscalatedToPusat");
  });
});

describe("shouldShowCaseHistoryPriority", () => {
  const rows = [
    { priority: "HIGH" },
    { priority: "HIGH" },
    { priority: null },
    { priority: "HIGH" },
    { priority: "MEDIUM" },
    { priority: "medium" },
    { priority: "HIGH" },
  ];

  it("shows the first tag, then only when the value changes", () => {
    expect(shouldShowCaseHistoryPriority(rows, 0)).toBe(true);
    expect(shouldShowCaseHistoryPriority(rows, 1)).toBe(false);
    expect(shouldShowCaseHistoryPriority(rows, 2)).toBe(false);
    expect(shouldShowCaseHistoryPriority(rows, 3)).toBe(false);
    expect(shouldShowCaseHistoryPriority(rows, 4)).toBe(true);
    expect(shouldShowCaseHistoryPriority(rows, 5)).toBe(false);
    expect(shouldShowCaseHistoryPriority(rows, 6)).toBe(true);
  });

  it("shows the first non-empty priority when earlier rows omit it", () => {
    expect(
      shouldShowCaseHistoryPriority([{ priority: null }, { priority: "LOW" }], 1),
    ).toBe(true);
  });
});
