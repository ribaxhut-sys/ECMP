import { afterEach, describe, expect, it } from "vitest";
import {
  clearKnownCaseIds,
  getCaseHandleDecision,
  listKnownCaseIds,
  markCaseHandleClaimed,
  markCaseHandleViewed,
  rememberCaseId,
  shouldAskHandleClaim,
} from "./caseSessionRegistry";

describe("caseSessionRegistry", () => {
  afterEach(() => {
    sessionStorage.clear();
  });

  it("remembers unique case ids per complaint", () => {
    rememberCaseId("c1", "a");
    rememberCaseId("c1", "a");
    rememberCaseId("c1", "b");
    rememberCaseId("c2", "x");
    expect(listKnownCaseIds("c1")).toEqual(["a", "b"]);
    expect(listKnownCaseIds("c2")).toEqual(["x"]);
    clearKnownCaseIds("c1");
    expect(listKnownCaseIds("c1")).toEqual([]);
  });

  it("records handle claim vs view-only for this session", () => {
    expect(getCaseHandleDecision("case-1")).toBeNull();
    markCaseHandleClaimed("case-1");
    expect(getCaseHandleDecision("case-1")).toBe("claimed");
    markCaseHandleViewed("case-2");
    expect(getCaseHandleDecision("case-2")).toBe("viewed");
  });

  it("asks to handle only for open cases without a session decision", () => {
    expect(
      shouldAskHandleClaim({
        status: "IN_PROGRESS",
        canAct: true,
        decision: null,
      }),
    ).toBe(true);
    expect(
      shouldAskHandleClaim({
        status: "CLOSED",
        canAct: true,
        decision: null,
      }),
    ).toBe(false);
    expect(
      shouldAskHandleClaim({
        status: "ASSIGNED",
        canAct: true,
        decision: "viewed",
      }),
    ).toBe(false);
    expect(
      shouldAskHandleClaim({
        status: "IN_PROGRESS",
        canAct: true,
        decision: null,
        handlingClaimedBy: "other",
        userId: "me",
      }),
    ).toBe(false);
    expect(
      shouldAskHandleClaim({
        status: "CREATED",
        canAct: false,
        decision: null,
      }),
    ).toBe(false);
    expect(
      shouldAskHandleClaim({
        status: "IN_PROGRESS",
        canAct: true,
        decision: null,
        handlingClaimedBy: "me",
        userId: "me",
      }),
    ).toBe(false);
  });
});
