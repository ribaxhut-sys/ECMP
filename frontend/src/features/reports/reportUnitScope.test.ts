import { describe, expect, it } from "vitest";
import { canPickReportUnit } from "./reportUnitScope";

describe("canPickReportUnit", () => {
  it("lets Head Office (no home branch) pick a unit", () => {
    expect(canPickReportUnit(null, undefined)).toBe(true);
    expect(canPickReportUnit("", undefined)).toBe(true);
  });

  it("lets a Pusat home unit pick every unit", () => {
    expect(canPickReportUnit("uuid-pusat", "PUSAT")).toBe(true);
    expect(canPickReportUnit("uuid-cro", "PUSAT-CRO")).toBe(true);
  });

  it("locks a cabang user to their home unit", () => {
    expect(canPickReportUnit("uuid-tab", "UPPPD-TANAH-ABANG")).toBe(false);
    expect(canPickReportUnit("uuid-tab", undefined)).toBe(false);
  });
});
