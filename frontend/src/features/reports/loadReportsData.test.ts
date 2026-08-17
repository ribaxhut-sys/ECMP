import { beforeEach, describe, expect, it, vi } from "vitest";
import { loadReportsData } from "./loadReportsData";

vi.mock("@/lib/api", () => ({
  fetchDashboardAggregateKpis: vi.fn(),
  fetchReportByBranch: vi.fn(),
}));

import { fetchDashboardAggregateKpis, fetchReportByBranch } from "@/lib/api";

const aggregateMock = vi.mocked(fetchDashboardAggregateKpis);
const byBranchMock = vi.mocked(fetchReportByBranch);

describe("loadReportsData", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    byBranchMock.mockResolvedValue({ data: [] } as never);
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
  });

  it("throws when Aggregate KPI fails (no foundation fallback)", async () => {
    const boom = new Error("aggregate down");
    aggregateMock.mockRejectedValue(boom);
    byBranchMock.mockResolvedValue({ data: [] } as never);
    await expect(loadReportsData()).rejects.toThrow("aggregate down");
  });

  it("returns null branch rows when there are none (API-212 side panel)", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 0, open: 0, closed: 0, escalatePending: 0 },
    } as never);
    byBranchMock.mockResolvedValue({ data: [] } as never);

    const data = await loadReportsData();
    expect(data.byBranch).toBeNull();
  });

  it("passes through branch rows when API-212 returns data", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 1, open: 1, closed: 0, escalatePending: 0 },
    } as never);
    byBranchMock.mockResolvedValue({
      data: [
        {
          branchId: "b1",
          branchCode: "JKT",
          branchName: "Jakarta",
          total: 1,
          open: 1,
          closed: 0,
          caseTotal: 0,
          caseOpen: 0,
          caseClosed: 0,
        },
      ],
    } as never);

    const data = await loadReportsData();
    expect(data.byBranch).toHaveLength(1);
    expect(data.byBranch?.[0]?.branchName).toBe("Jakarta");
  });

  it("keeps idle branch rows so Kesehatan Cabang can show the full unit set", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 12, open: 7, closed: 5, escalatePending: 2 },
    } as never);
    byBranchMock.mockResolvedValue({
      data: [
        {
          branchId: "idle",
          branchCode: "UPPPD-GAMBIR",
          branchName: "UPPPD Gambir",
          unitCode: "GAM",
          total: 0,
          open: 0,
          closed: 0,
          escalated: 0,
          caseTotal: 0,
          caseOpen: 0,
          caseClosed: 0,
        },
        {
          branchId: "tab",
          branchCode: "UPPPD-TANAH-ABANG",
          branchName: "UPPPD Tanah Abang",
          unitCode: "TAB",
          total: 12,
          open: 7,
          closed: 5,
          escalated: 2,
          caseTotal: 15,
          caseOpen: 10,
          caseClosed: 5,
        },
      ],
    } as never);

    const data = await loadReportsData();
    expect(data.byBranch).toHaveLength(2);
    expect(data.byBranch?.map((row) => row.unitCode)).toEqual(["GAM", "TAB"]);
  });

  it("degrades to null branch rows without failing the page when API-212 errors", async () => {
    aggregateMock.mockResolvedValue({
      data: { total: 1, open: 1, closed: 0, escalatePending: 0 },
    } as never);
    byBranchMock.mockRejectedValue(new Error("by-branch down"));

    const data = await loadReportsData();
    expect(data.summary?.total).toBe(1);
    expect(data.byBranch).toBeNull();
  });
});
