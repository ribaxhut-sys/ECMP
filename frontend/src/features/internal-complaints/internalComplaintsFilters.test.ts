import { describe, expect, it } from "vitest";
import {
  defaultInternalListFilters,
  filterInternalComplaints,
  hasActiveInternalFilters,
  needsAttention,
  sortByMostRecent,
  sortForDashboardAction,
} from "./internalComplaintsFilters";
import { isInternalTerminalStatus, type InternalComplaint } from "./types";

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
    resolutionStatus: null,
    resolutionComment: null,
    resolutionProposedBy: null,
    resolutionProposedByName: null,
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
    withdrawRequestStatus: null,
    withdrawRequestReason: null,
    withdrawRequestedBy: null,
    withdrawRequestedByName: null,
    withdrawRequestedAt: null,
    withdrawDecidedBy: null,
    withdrawDecidedByName: null,
    withdrawDecidedAt: null,
    withdrawDecisionReason: null,
    withdrawnBy: null,
    withdrawnByName: null,
    withdrawnAt: null,
    withdrawReason: null,
    completionRequestStatus: null,
    completionReturnReason: null,
    completionReturnedBy: null,
    completionReturnedByName: null,
    completionReturnedAt: null,
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

  it("filters by search across number, subject, description, and reporter", () => {
    const rows = [
      row({
        id: "1",
        number: "PI-TAB-2608-001",
        title: "Antrian panjang",
        description: "Loket penuh",
        createdByName: "Ani",
      }),
      row({ id: "2", number: "PI-TAB-2608-002", title: "Lain" }),
    ];
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        q: "pelapor-tidak-ada",
      }),
    ).toHaveLength(0);
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        q: "Ani",
      })[0].id,
    ).toBe("1");
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        q: "Loket",
      })[0].id,
    ).toBe("1");
  });

  it("filters by an inclusive createdAt period", () => {
    const rows = [
      row({ id: "1", number: "a", createdAt: "2026-01-31T17:00:00Z" }),
      row({ id: "2", number: "b", createdAt: "2026-02-15T03:00:00Z" }),
      row({ id: "3", number: "c", createdAt: "2026-03-01T00:00:00Z" }),
    ];
    // 2026-01-31T17:00Z is already 2026-02-01 in Asia/Jakarta.
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        dateFrom: "2026-02-01",
        dateTo: "2026-02-15",
      }).map((r) => r.id),
    ).toEqual(["1", "2"]);
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        dateFrom: "2026-02-15",
      }).map((r) => r.id),
    ).toEqual(["2", "3"]);
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        dateTo: "2026-02-01",
      }).map((r) => r.id),
    ).toEqual(["1"]);
  });

  it("drops rows with an unreadable createdAt only while a period is set", () => {
    const rows = [row({ id: "1", number: "a", createdAt: "not-a-date" })];
    expect(
      filterInternalComplaints(rows, defaultInternalListFilters()),
    ).toHaveLength(1);
    expect(
      filterInternalComplaints(rows, {
        ...defaultInternalListFilters(),
        dateFrom: "2026-01-01",
      }),
    ).toHaveLength(0);
  });

  it("counts a period as an active filter", () => {
    expect(
      hasActiveInternalFilters({
        ...defaultInternalListFilters(),
        dateFrom: "2026-01-01",
      }),
    ).toBe(true);
    expect(
      hasActiveInternalFilters({
        ...defaultInternalListFilters(),
        dateTo: "2026-01-31",
      }),
    ).toBe(true);
  });

  it("sorts newest first", () => {
    const rows = [
      row({ id: "1", number: "a", createdAt: "2026-01-01T00:00:00Z" }),
      row({ id: "2", number: "b", createdAt: "2026-02-01T00:00:00Z" }),
    ];
    expect(sortByMostRecent(rows).map((r) => r.id)).toEqual(["2", "1"]);
  });

  it("flags RESOLVED and pending-request rows as needing attention", () => {
    expect(needsAttention(row({ id: "1", number: "a", status: "RESOLVED" }))).toBe(
      true,
    );
    expect(
      needsAttention(
        row({ id: "2", number: "b", transferRequestStatus: "PENDING" }),
      ),
    ).toBe(true);
    expect(
      needsAttention(
        row({ id: "3", number: "c", withdrawRequestStatus: "PENDING" }),
      ),
    ).toBe(true);
    expect(needsAttention(row({ id: "4", number: "d", status: "CREATED" }))).toBe(
      false,
    );
  });

  it("filters the incoming receive queue by actor unit", () => {
    const rows = [
      row({
        id: "1",
        number: "PI-1",
        status: "ASSIGNED",
        handlingUnitId: "PUSAT",
      }),
      row({
        id: "2",
        number: "PI-2",
        status: "ASSIGNED",
        handlingUnitId: "UPPPD-GAMBIR",
      }),
      row({
        id: "3",
        number: "PI-3",
        status: "IN_PROGRESS",
        handlingUnitId: "PUSAT",
      }),
    ];
    expect(
      filterInternalComplaints(
        rows,
        { ...defaultInternalListFilters(), needsReceive: true },
        "PUSAT",
      ).map((r) => r.id),
    ).toEqual(["1"]);
    expect(
      filterInternalComplaints(
        rows,
        { ...defaultInternalListFilters(), needsReceive: true },
        "UPPPD-GAMBIR",
      ).map((r) => r.id),
    ).toEqual(["2"]);
    expect(
      hasActiveInternalFilters({
        ...defaultInternalListFilters(),
        needsReceive: true,
      }),
    ).toBe(true);
  });

  it("keeps owner usulan in the needsAction queue for Cabang, not Pusat", () => {
    const rows = [
      row({
        id: "proposal",
        number: "PI-U",
        status: "IN_PROGRESS",
        ownerUnitId: "UPPPD-JOHAR-BARU",
        handlingUnitId: "PUSAT",
        resolutionStatus: "PENDING_APPROVAL",
      }),
    ];
    expect(
      filterInternalComplaints(
        rows,
        { ...defaultInternalListFilters(), needsAction: true },
        "UPPPD-JOHAR-BARU",
      ).map((r) => r.id),
    ).toEqual(["proposal"]);
    expect(
      filterInternalComplaints(
        rows,
        { ...defaultInternalListFilters(), needsAction: true },
        "PUSAT",
      ),
    ).toEqual([]);
  });

  it("drops IN_PROGRESS ACCEPTED from Cabang needsAction, keeps it for Pusat rebound", () => {
    const rows = [
      row({
        id: "stale",
        number: "PI-STALE",
        status: "IN_PROGRESS",
        ownerUnitId: "UPPPD-JOHAR-BARU",
        handlingUnitId: "PUSAT",
        resolutionStatus: "ACCEPTED",
      }),
    ];
    expect(
      filterInternalComplaints(
        rows,
        { ...defaultInternalListFilters(), needsAction: true },
        "UPPPD-JOHAR-BARU",
      ),
    ).toEqual([]);
    expect(
      filterInternalComplaints(
        rows,
        { ...defaultInternalListFilters(), needsAction: true },
        "PUSAT",
      ).map((r) => r.id),
    ).toEqual(["stale"]);
  });

  it("sorts rows needing attention before the rest, newest first within each group", () => {
    const rows = [
      row({
        id: "old-normal",
        number: "a",
        status: "CREATED",
        createdAt: "2026-01-01T00:00:00Z",
      }),
      row({
        id: "new-urgent",
        number: "b",
        status: "RESOLVED",
        createdAt: "2026-03-01T00:00:00Z",
      }),
      row({
        id: "new-normal",
        number: "c",
        status: "CREATED",
        createdAt: "2026-02-01T00:00:00Z",
      }),
      row({
        id: "old-urgent",
        number: "d",
        withdrawRequestStatus: "PENDING",
        createdAt: "2026-01-15T00:00:00Z",
      }),
    ];
    expect(sortForDashboardAction(rows).map((r) => r.id)).toEqual([
      "new-urgent",
      "old-urgent",
      "new-normal",
      "old-normal",
    ]);
  });
});

describe("isInternalTerminalStatus", () => {
  it("treats CLOSED and WITHDRAWN as finished", () => {
    expect(isInternalTerminalStatus("CLOSED")).toBe(true);
    expect(isInternalTerminalStatus("WITHDRAWN")).toBe(true);
    expect(isInternalTerminalStatus("IN_PROGRESS")).toBe(false);
    expect(isInternalTerminalStatus("RESOLVED")).toBe(false);
  });
});
