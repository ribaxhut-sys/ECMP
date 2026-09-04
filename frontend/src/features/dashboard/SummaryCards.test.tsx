import { cleanup, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { DashboardHeader, DashboardResolutionSla } from "@/lib/api/types";
import { renderWithProviders } from "@/test/harness";
import { SummaryCards } from "./SummaryCards";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: () => true,
  }),
}));

beforeEach(() => {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      addListener: () => undefined,
      removeListener: () => undefined,
      dispatchEvent: () => false,
    }),
  });
});

afterEach(cleanup);

const header: DashboardHeader = {
  totalComplaints: 10,
  openComplaints: 4,
  closedComplaints: 6,
};

const sla: DashboardResolutionSla = {
  targetDays: 30,
  onTrack: 3,
  warning: 0,
  overdue: 1,
  met: 5,
  missed: 1,
  unknown: 0,
  compliancePercentage: 83.33,
};

describe("SummaryCards SLA tile", () => {
  it("no longer claims Batch-1 SLA is inactive once the rollup is present", () => {
    renderWithProviders(
      <SummaryCards
        header={header}
        byStatus={[]}
        sla={sla}
        loading={false}
      />,
    );
    expect(screen.queryByText("Not activated on Batch-1")).toBeNull();
    expect(screen.getByText("1 overdue")).toBeTruthy();
  });

  it("keeps the deferred caption only when measurement is off", () => {
    renderWithProviders(
      <SummaryCards
        header={header}
        byStatus={[]}
        sla={null}
        loading={false}
      />,
    );
    expect(screen.getByText("Not activated on Batch-1")).toBeTruthy();
  });

  it("shows Pusat work doors instead of cabang assignment KPIs", () => {
    renderWithProviders(
      <SummaryCards
        header={header}
        byStatus={[{ status: "escalateScheduled", count: 12 }]}
        sla={null}
        loading={false}
        pusatWork={{ queue: 1, followUp: 0, hqScheduleToday: 10 }}
      />,
    );
    expect(screen.getByText("HQ intake")).toBeTruthy();
    expect(screen.getByText("Follow-up")).toBeTruthy();
    expect(screen.getByText("Today's schedule")).toBeTruthy();
    expect(screen.queryByText("Open Complaints")).toBeNull();
    expect(screen.queryByText("Closure rate")).toBeNull();
  });
});
