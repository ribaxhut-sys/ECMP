import { afterEach, describe, expect, it } from "vitest";
import {
  clearKnownCaseIds,
  listKnownCaseIds,
  rememberCaseId,
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
});
