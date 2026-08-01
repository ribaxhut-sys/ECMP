import { beforeEach, describe, expect, it, vi } from "vitest";
import { loadReportsData } from "./loadReportsData";

vi.mock("@/lib/api", () => ({
  fetchReportSummary: vi.fn(),
  fetchReportByStatus: vi.fn(),
  fetchReportByBranch: vi.fn(),
}));

import {
  fetchReportByBranch,
  fetchReportByStatus,
  fetchReportSummary,
} from "@/lib/api";

const summaryMock = vi.mocked(fetchReportSummary);
const byStatusMock = vi.mocked(fetchReportByStatus);
const byBranchMock = vi.mocked(fetchReportByBranch);

describe("loadReportsData", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns fulfilled slices and nulls for rejected ones", async () => {
    summaryMock.mockResolvedValue({
      data: { total: 1, byStatus: [{ status: "NEW", count: 1 }] },
    } as never);
    byStatusMock.mockRejectedValue(new Error("status down"));
    byBranchMock.mockResolvedValue({
      data: [
        {
          branchId: "b1",
          branchCode: "JKT",
          branchName: "Jakarta",
          total: 1,
        },
      ],
    } as never);

    const data = await loadReportsData();
    expect(data.summary?.total).toBe(1);
    expect(data.byStatus).toBeNull();
    expect(data.byBranch?.[0]?.branchCode).toBe("JKT");
  });

  it("throws when every report API fails", async () => {
    const boom = new Error("all down");
    summaryMock.mockRejectedValue(boom);
    byStatusMock.mockRejectedValue(new Error("status down"));
    byBranchMock.mockRejectedValue(new Error("branch down"));

    await expect(loadReportsData()).rejects.toThrow("all down");
  });
});
