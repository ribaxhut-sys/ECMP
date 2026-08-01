import { describe, expect, it } from "vitest";
import { QUICK_ACTIONS } from "./quickActionConfig";

describe("QUICK_ACTIONS", () => {
  it("has unique ids", () => {
    const ids = QUICK_ACTIONS.map((a) => a.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("requires a permission on every action", () => {
    for (const action of QUICK_ACTIONS) {
      expect(action.permission.length).toBeGreaterThan(0);
      expect(action.permission).toMatch(/:/);
    }
  });

  it("includes create complaint and refresh dashboard actions", () => {
    const ids = QUICK_ACTIONS.map((a) => a.id);
    expect(ids).toContain("create-complaint");
    expect(ids).toContain("refresh-reports");
  });
});
