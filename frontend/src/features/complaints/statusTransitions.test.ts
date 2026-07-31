import { describe, expect, it } from "vitest";
import { statusActionsFor, STATUS_TRANSITIONS } from "./statusTransitions";

describe("STATUS_TRANSITIONS", () => {
  it("allows IN_PROGRESS from ASSIGNED only", () => {
    expect(STATUS_TRANSITIONS.ASSIGNED).toEqual(["IN_PROGRESS"]);
  });

  it("keeps NEW and CLOSED terminal for PATCH status", () => {
    expect(STATUS_TRANSITIONS.NEW).toEqual([]);
    expect(STATUS_TRANSITIONS.CLOSED).toEqual([]);
  });
});

describe("statusActionsFor", () => {
  it("returns start progress for ASSIGNED", () => {
    expect(statusActionsFor("ASSIGNED")).toEqual([
      { labelKey: "startProgress", target: "IN_PROGRESS" },
    ]);
  });

  it("returns close and reopen for RESOLVED", () => {
    expect(statusActionsFor("RESOLVED")).toEqual([
      { labelKey: "closeComplaint", target: "CLOSED" },
      { labelKey: "reopen", target: "IN_PROGRESS" },
    ]);
  });

  it("returns no actions for NEW", () => {
    expect(statusActionsFor("NEW")).toEqual([]);
  });
});
