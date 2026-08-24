/**
 * CAP-008 Mode A — path/header contract (no network).
 */
import { describe, expect, it } from "vitest";
import {
  CM_CASE_BASE,
  buildCmCaseMutateHeaders,
  cmCasePaths,
} from "./cmCaseContract";
import { FOUNDATION_COMPLAINTS_BASE } from "./dualSotNamespaces";

describe("cmCasePaths", () => {
  it("anchors Case ops under /api/v1/cm", () => {
    const paths = cmCasePaths();
    expect(CM_CASE_BASE).toBe("/api/v1/cm");
    expect(paths.cases).toBe("/api/v1/cm/cases");
    expect(paths.case("c/1")).toBe("/api/v1/cm/cases/c%2F1");
    expect(paths.addCase("p/1")).toBe("/api/v1/cm/complaints/p%2F1/cases");
    expect(paths.status("id")).toBe("/api/v1/cm/cases/id/status");
    expect(paths.resolve("id")).toBe("/api/v1/cm/cases/id/resolve");
    expect(paths.acceptance("id")).toBe("/api/v1/cm/cases/id/acceptance");
    expect(paths.close("id")).toBe("/api/v1/cm/cases/id/close");
    expect(paths.escalateToPusat("id")).toBe(
      "/api/v1/cm/cases/id/escalate-to-pusat",
    );
    expect(paths.cancelEscalationToPusat("id")).toBe(
      "/api/v1/cm/cases/id/cancel-escalation-to-pusat",
    );
    expect(paths.returnEscalation("id")).toBe(
      "/api/v1/cm/cases/id/return-escalation",
    );
    expect(paths.history("c/1")).toBe("/api/v1/cm/cases/c%2F1/history");
    expect(paths.workBadges).toBe("/api/v1/cm/work-badges");
  });

  it("does not use foundation complaints base for create case", () => {
    expect(cmCasePaths().cases.startsWith(FOUNDATION_COMPLAINTS_BASE)).toBe(
      false,
    );
  });
});

describe("buildCmCaseMutateHeaders", () => {
  it("omits empty idempotency key", () => {
    expect(buildCmCaseMutateHeaders()).toEqual({});
    expect(buildCmCaseMutateHeaders({ idempotencyKey: "  " })).toEqual({});
  });

  it("sets Idempotency-Key when provided", () => {
    expect(
      buildCmCaseMutateHeaders({ idempotencyKey: " key-1 " }),
    ).toEqual({ "Idempotency-Key": "key-1" });
  });
});
