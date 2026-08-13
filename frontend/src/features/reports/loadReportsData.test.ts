import { beforeEach, describe, expect, it, vi } from "vitest";
import { loadReportsData } from "./loadReportsData";

vi.mock("@/lib/api", () => ({
  fetchDashboardAggregateKpis: vi.fn(),
}));

import { fetchDashboardAggregateKpis } from "@/lib/api";

const aggregateMock = vi.mocked(fetchDashboardAggregateKpis);

describe("loadReportsData", () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
        inProgress: 2,
      },
    } as never);

    const data = await loadReportsData();
    expect(data.summary?.total).toBe(16);
    expect(data.summary?.byStatus).toEqual(data.byStatus);
    expect(
      data.byStatus?.find((row) => row.labelKey === "waitingEscalationApproval")
        ?.count,
    ).toBe(4);
    expect(
      data.byStatus?.find((row) => row.labelKey === "queueInProgress")?.count,
    ).toBe(2);
    expect(data.byStatus?.reduce((sum, row) => sum + row.count, 0)).toBe(16);
    expect(data.byBranch).toBeNull();
  });

  it("throws when Aggregate KPI fails (no foundation fallback)", async () => {
    const boom = new Error("aggregate down");
    aggregateMock.mockRejectedValue(boom);
    await expect(loadReportsData()).rejects.toThrow("aggregate down");
  });
});
