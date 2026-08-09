import { describe, expect, it } from "vitest";
import {
  INTERNAL_COMPLAINTS_BASE,
  internalComplaintPaths,
} from "./internalComplaintsContract";
import { FOUNDATION_COMPLAINTS_BASE } from "./dualSotNamespaces";
import { CM_CASE_BASE } from "./cmCaseContract";

describe("internalComplaintPaths", () => {
  it("stays under /api/v1/internal/complaints (not F4 / foundation)", () => {
    const paths = internalComplaintPaths();
    expect(paths.list).toBe("/api/v1/internal/complaints");
    expect(paths.detail("a/b")).toBe("/api/v1/internal/complaints/a%2Fb");
    expect(paths.transfer("id")).toBe("/api/v1/internal/complaints/id/transfer");
    expect(paths.receive("id")).toBe("/api/v1/internal/complaints/id/receive");
    expect(paths.resolve("id")).toBe("/api/v1/internal/complaints/id/resolve");
    expect(paths.acceptance("id")).toBe(
      "/api/v1/internal/complaints/id/acceptance",
    );
    expect(paths.close("id")).toBe("/api/v1/internal/complaints/id/close");
    expect(INTERNAL_COMPLAINTS_BASE.startsWith(FOUNDATION_COMPLAINTS_BASE)).toBe(
      false,
    );
    expect(INTERNAL_COMPLAINTS_BASE.startsWith(CM_CASE_BASE)).toBe(false);
  });
});
