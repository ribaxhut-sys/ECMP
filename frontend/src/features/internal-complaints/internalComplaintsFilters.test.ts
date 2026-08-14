import { describe, expect, it } from "vitest";
import {
  defaultInternalListFilters,
  filterInternalComplaints,
  hasActiveInternalFilters,
  sortByMostRecent,
} from "./internalComplaintsFilters";
import type { InternalComplaint } from "./types";

function row(
  partial: Partial<InternalComplaint> & Pick<InternalComplaint, "id" | "number">,
): InternalComplaint {
  return {
    title: "t",
    category: "OPERATIONAL",
    subcategory: "",
    relatedComplaintId: null,
    relatedComplaintNumber: null,
    priority: "MEDIUM",
    status: "CREATED",
    description: "",
    chronology: "",
    impact: "",
    ownerUnitId: "UPPPD-GAMBIR",
    handlingUnitId: "UPPPD-GAMBIR",
    createdBy: "u1",
    createdByName: null,
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: null,
    closedBy: null,
    closedByName: null,
    closedAt: null,
    resolutionSummary: null,
    handlingUnitAcceptance: null,
    ownerAcceptance: null,
    history: [],
    transferRequestStatus: null,
    transferRequestDestinationUnitId: null,
    transferRequestReason: null,
    transferRequestedBy: null,
    transferRequestedByName: null,
    transferRequestedAt: null,
    transferDecidedBy: null,
    transferDecidedByName: null,
    transferDecidedAt: null,
    transferDecisionReason: null,
    ...partial,
  };
}

describe("internalComplaintsFilters", () => {
  it("detects active filters", () => {
    expect(hasActiveInternalFilters(defaultInternalListFilters())).toBe(false);
    expect(
      hasActiveInternalFilters({ ...defaultInternalListFilters(), status: "CLOSED" }),
    ).toBe(true);
  });

  it("filters by status and owner", () => {
    const rows = [
      row({ id: "1", number: "PI-1", status: "CREATED" }),
      row({
        id: "2",
        number: "PI-2",
        status: "CLOSED",
        ownerUnitId: "PUSAT",
        handlingUnitId: "PUSAT",
      }),
    ];
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        status: "CLOSED",
      }),
    ).toHaveLength(1);
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        ownerUnitId: "PUSAT",
      })[0].id,
    ).toBe("2");
  });

  it("sorts newest first", () => {
    const rows = [
      row({ id: "1", number: "a", createdAt: "2026-01-01T00:00:00Z" }),
      row({ id: "2", number: "b", createdAt: "2026-02-01T00:00:00Z" }),
    ];
    expect(sortByMostRecent(rows).map((r) => r.id)).toEqual(["2", "1"]);
  });
});
