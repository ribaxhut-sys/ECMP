import { describe, expect, it } from "vitest";
import { CM_BATCH1_OPEN_HREF } from "@/features/complaints/cmBatch1ListFilters";
import {
  branchOptionLabel,
  dashboardEmptyWorkCta,
  sortBranchesHeadOfficeFirst,
} from "./dashboardUtils";

describe("branchOptionLabel", () => {
  it("drops the code when it is just the name reformatted", () => {
    expect(
      branchOptionLabel({ code: "UPPPD-PASAR-MINGGU", name: "UPPPD Pasar Minggu" }),
    ).toBe("UPPPD Pasar Minggu");
  });

  it("keeps both when the code carries distinct information", () => {
    expect(
      branchOptionLabel({ code: "JKT-01", name: "Cabang Jakarta Pusat" }),
    ).toBe("JKT-01 — Cabang Jakarta Pusat");
  });
});

describe("sortBranchesHeadOfficeFirst", () => {
  it("puts Pusat first, then the rest alphabetically by name", () => {
    const branches = [
      { code: "UPPPD-SENEN", name: "UPPPD Senen" },
      { code: "JKT-01", name: "Cabang Jakarta Pusat" },
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "UPPPD Gambir" },
    ];

    expect(sortBranchesHeadOfficeFirst(branches).map((b) => b.code)).toEqual([
      "PUSAT",
      "JKT-01",
      "UPPPD-GAMBIR",
      "UPPPD-SENEN",
    ]);
  });

  it("does not mutate the input array", () => {
    const branches = [
      { code: "B", name: "Beta" },
      { code: "A", name: "Alfa" },
    ];
    const sorted = sortBranchesHeadOfficeFirst(branches);
    expect(sorted).not.toBe(branches);
    expect(branches.map((b) => b.code)).toEqual(["B", "A"]);
  });
});

describe("dashboardEmptyWorkCta (DEC-025 §3.6)", () => {
  it("sends Aggregate KPI officers to the CM open list, not Foundation /queue", () => {
    expect(dashboardEmptyWorkCta("aggregate")).toEqual({
      href: CM_BATCH1_OPEN_HREF,
      labelKey: "goToComplaints",
    });
  });

  it("keeps Foundation fallback on the legacy queue", () => {
    expect(dashboardEmptyWorkCta("foundation")).toEqual({
      href: "/queue",
      labelKey: "goToQueue",
    });
    expect(dashboardEmptyWorkCta(null)).toEqual({
      href: "/queue",
      labelKey: "goToQueue",
    });
  });
});
