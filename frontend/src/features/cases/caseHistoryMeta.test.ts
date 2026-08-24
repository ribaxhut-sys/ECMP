import { describe, expect, it } from "vitest";
import {
  filterWpCaseHistoryEntries,
  isWpCaseHistoryHidden,
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
