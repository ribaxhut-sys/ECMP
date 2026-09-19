import { describe, expect, it } from "vitest";
import {
  INTAKE_DUPLICATE_HISTORY_LABEL_KEYS,
  INTAKE_RECORDED_HISTORY_LABEL_KEY,
  isCaseSummaryEvent,
  isCaseWorkDetailEvent,
  latestCaseHistoryEvent,
} from "./complaintHistoryScope";

describe("isCaseWorkDetailEvent", () => {
  it("hides handling and status-change rows from the complaint log", () => {
    expect(isCaseWorkDetailEvent("CASE_STATUS_CHANGED")).toBe(true);
    expect(isCaseWorkDetailEvent("handling_taken_over")).toBe(true);
    expect(isCaseWorkDetailEvent("RESOLUTION_UPDATED")).toBe(true);
  });

  it("keeps complaint-level and Case milestone rows", () => {
    expect(isCaseWorkDetailEvent("REGISTERED")).toBe(false);
    expect(isCaseWorkDetailEvent("ESCALATION_APPROVED")).toBe(false);
    expect(isCaseWorkDetailEvent("HQ_ARRIVAL_SCHEDULED")).toBe(false);
    expect(isCaseWorkDetailEvent("CASE_CREATED")).toBe(false);
    expect(isCaseWorkDetailEvent("CASE_CLOSED")).toBe(false);
    expect(isCaseWorkDetailEvent("CASE_CANCELLED")).toBe(false);
  });
});

describe("isCaseSummaryEvent", () => {
  it("marks Case milestone rows whose note body belongs on the Case page", () => {
    expect(isCaseSummaryEvent("CASE_CREATED")).toBe(true);
    expect(isCaseSummaryEvent("CASE_CLOSED")).toBe(true);
    expect(isCaseSummaryEvent("case_resolved")).toBe(true);
    expect(isCaseSummaryEvent("REGISTERED")).toBe(false);
  });
});

describe("latestCaseHistoryEvent", () => {
  it("returns the newest row for that Case number", () => {
    const latest = latestCaseHistoryEvent(
      [
        {
          eventCode: "CASE_CREATED",
          caseNumber: "TAB-2608-0001",
          occurredAt: "2026-08-20T01:00:00Z",
        },
        {
          eventCode: "CASE_STATUS_CHANGED",
          caseNumber: "TAB-2608-0001",
          occurredAt: "2026-08-21T04:00:00Z",
        },
        {
          eventCode: "CASE_CREATED",
          caseNumber: "TAB-2608-0002",
          occurredAt: "2026-08-22T00:00:00Z",
        },
      ],
      "TAB-2608-0001",
    );
    expect(latest?.eventCode).toBe("CASE_STATUS_CHANGED");
  });

  it("returns null when the Case has no tagged events", () => {
    expect(
      latestCaseHistoryEvent(
        [{ eventCode: "REGISTERED", occurredAt: "2026-08-20T01:00:00Z" }],
        "TAB-2608-0001",
      ),
    ).toBeNull();
  });
});

describe("INTAKE_DUPLICATE_HISTORY_LABEL_KEYS", () => {
  it("maps every backend Duplicate* history code to a complaints i18n key", () => {
    expect(INTAKE_DUPLICATE_HISTORY_LABEL_KEYS).toEqual({
      DUPLICATE_FOUND: "tagDuplicateFound",
      DUPLICATE_OVERRIDDEN: "tagDuplicateOverridden",
      DUPLICATE_LINKED: "tagDuplicateLinked",
      DUPLICATE_REDIRECTED: "tagDuplicateRedirected",
      DUPLICATE_RECOMMENDED: "tagDuplicateRecommended",
      DUPLICATE_BLOCKED: "tagDuplicateBlocked",
    });
    expect(INTAKE_RECORDED_HISTORY_LABEL_KEY).toBe("tagIntakeRecorded");
  });
});
