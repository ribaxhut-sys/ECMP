import { beforeEach, describe, expect, it, vi } from "vitest";
import { loadReportsData } from "./loadReportsData";

vi.mock("@/lib/api", () => ({
  fetchDashboardAggregateKpis: vi.fn(),
  fetchReportCycleTime: vi.fn(),
  fetchReportByUser: vi.fn(),
}));

import {
  fetchDashboardAggregateKpis,
  fetchReportByUser,
  fetchReportCycleTime,
} from "@/lib/api";

const aggregateMock = vi.mocked(fetchDashboardAggregateKpis);
const cycleTimeMock = vi.mocked(fetchReportCycleTime);
const byUserMock = vi.mocked(fetchReportByUser);

describe("loadReportsData", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    cycleTimeMock.mockResolvedValue({
      data: { closedCases: 0, buckets: [] },
    } as never);
    byUserMock.mockResolvedValue({ data: [] } as never);
  });

  it("maps Batch-1 Aggregate KPI into report summary (same SoT as dashboard)", async () => {
    aggregateMock.mockResolvedValue({
      data: {
        total: 16,
        open: 8,
        closed: 6,
        escalatePending: 4,
        waitingAssignment: 3,
        escalateApproved: 1,
        escalateScheduled: 0,
        inProgress: 2,
      },
    } as never);

    const data = await loadReportsData();
    expect(data.summary?.total).toBe(16);
    expect(data.previous).toBeNull();
    expect(data.summary?.byStatus).toEqual(data.byStatus);
    expect(
      data.byStatus?.find((row) => row.labelKey === "waitingEscalationApproval")
        ?.count,
    ).toBe(4);
    expect(
      data.byStatus?.find((row) => row.labelKey === "queueInProgress")?.count,
    ).toBe(2);
    expect(data.byStatus?.reduce((sum, row) => sum + row.count, 0)).toBe(16);
  });

  it("forwards the selected period window to the Aggregate KPI", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 0, open: 0, closed: 0, escalatePending: 0 },
    } as never);

    await loadReportsData({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-31T23:59:59.999Z",
    });

    expect(aggregateMock).toHaveBeenCalledWith({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-31T23:59:59.999Z",
    });
    expect(cycleTimeMock).toHaveBeenCalledWith({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-31T23:59:59.999Z",
    });
    expect(byUserMock).toHaveBeenCalledWith({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-31T23:59:59.999Z",
    });
  });

  it("forwards the selected unit to Aggregate KPI and cycle time", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 0, open: 0, closed: 0, escalatePending: 0 },
    } as never);

    await loadReportsData(
      {
        dateFrom: "2026-08-01T00:00:00.000Z",
        dateTo: "2026-08-31T23:59:59.999Z",
      },
      "branch-tab",
    );

    expect(aggregateMock).toHaveBeenCalledWith({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-31T23:59:59.999Z",
      branchId: "branch-tab",
    });
    expect(cycleTimeMock).toHaveBeenCalledWith({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-31T23:59:59.999Z",
      branchId: "branch-tab",
    });
    expect(byUserMock).toHaveBeenCalledWith({
      dateFrom: "2026-08-01T00:00:00.000Z",
      dateTo: "2026-08-31T23:59:59.999Z",
      branchId: "branch-tab",
    });
  });

  it("degrades to no cycle time instead of failing the page", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 1, open: 1, closed: 0, escalatePending: 0 },
    } as never);
    cycleTimeMock.mockRejectedValue(new Error("cycle-time down"));

    const data = await loadReportsData();
    expect(data.summary?.total).toBe(1);
    expect(data.cycleTime).toBeNull();
  });

  it("degrades to no user activity instead of failing the page", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 1, open: 1, closed: 0, escalatePending: 0 },
    } as never);
    byUserMock.mockRejectedValue(new Error("by-user down"));

    const data = await loadReportsData();
    expect(data.summary?.total).toBe(1);
    expect(data.byUser).toBeNull();
  });

  it("throws when Aggregate KPI fails (no foundation fallback)", async () => {
    aggregateMock.mockRejectedValue(new Error("aggregate down"));
    await expect(loadReportsData()).rejects.toThrow("aggregate down");
  });

  it("loads the previous window when asked, without failing the page if it errors", async () => {
    aggregateMock
      .mockResolvedValueOnce({
        data: { total: 10, open: 4, closed: 6, escalatePending: 0 },
      } as never)
      .mockRejectedValueOnce(new Error("previous down"));

    const data = await loadReportsData(
      { dateFrom: "2026-08-01T00:00:00.000Z" },
      undefined,
      { dateFrom: "2026-07-01T00:00:00.000Z" },
    );

    expect(data.summary?.total).toBe(10);
    expect(data.previous).toBeNull();
    expect(aggregateMock).toHaveBeenCalledTimes(2);
  });

  it("forwards the previous window to Aggregate KPI", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 1, open: 0, closed: 1, escalatePending: 0 },
    } as never);

    const data = await loadReportsData(
      {
        dateFrom: "2026-08-01T00:00:00.000Z",
        dateTo: "2026-08-18T16:59:59.999Z",
      },
      "branch-tab",
      {
        dateFrom: "2026-07-01T00:00:00.000Z",
        dateTo: "2026-07-18T16:59:59.999Z",
      },
    );

    expect(data.previous?.summary?.total).toBe(1);
    expect(aggregateMock).toHaveBeenNthCalledWith(2, {
      dateFrom: "2026-07-01T00:00:00.000Z",
      dateTo: "2026-07-18T16:59:59.999Z",
      branchId: "branch-tab",
    });
  });
});
