import { describe, expect, it } from "vitest";
import {
  CM_BATCH1_AGGREGATE_BASE,
  FOUNDATION_COMPLAINTS_BASE,
  dualSotNamespaceOf,
  isCmBatch1AggregatePath,
  isFoundationComplaintsPath,
} from "./dualSotNamespaces";

describe("dualSotNamespaces (DEC-020)", () => {
  it("keeps Aggregate and foundation bases distinct", () => {
    expect(FOUNDATION_COMPLAINTS_BASE).toBe("/api/v1/complaints");
    expect(CM_BATCH1_AGGREGATE_BASE).toBe("/api/v1/cm");
    expect(FOUNDATION_COMPLAINTS_BASE).not.toBe(CM_BATCH1_AGGREGATE_BASE);
  });

  it("classifies foundation lifecycle paths", () => {
    expect(isFoundationComplaintsPath("/api/v1/complaints")).toBe(true);
    expect(isFoundationComplaintsPath("/api/v1/complaints/search")).toBe(true);
    expect(isFoundationComplaintsPath("/api/v1/complaints?page=1")).toBe(true);
    expect(isFoundationComplaintsPath("/api/v1/cm/complaints")).toBe(false);
  });

  it("classifies Aggregate Batch 1 paths", () => {
    expect(isCmBatch1AggregatePath("/api/v1/cm")).toBe(true);
    expect(isCmBatch1AggregatePath("/api/v1/cm/complaints")).toBe(true);
    expect(isCmBatch1AggregatePath("/api/v1/cm/duplicates/check")).toBe(true);
    expect(isCmBatch1AggregatePath("/api/v1/complaints")).toBe(false);
  });

  it("maps dualSotNamespaceOf without treating namespaces as interchangeable", () => {
    expect(dualSotNamespaceOf("/api/v1/complaints")).toBe("foundation");
    expect(dualSotNamespaceOf("/api/v1/cm/complaints")).toBe("aggregate");
    expect(dualSotNamespaceOf("/api/v1/customers")).toBe("unknown");
  });
});
