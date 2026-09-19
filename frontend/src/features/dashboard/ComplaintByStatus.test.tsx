import { cleanup, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { ComplaintByStatus } from "./ComplaintByStatus";
import { buildAggregateKpis } from "./loadDashboardData";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: () => true,
  }),
}));

afterEach(cleanup);

describe("ComplaintByStatus", () => {
  it("renders HQ-scheduled origin rows on the cabang donut", () => {
    const kpis = buildAggregateKpis({
      total: 30,
      open: 19,
      closed: 11,
      escalatePending: 0,
      waitingAssignment: 0,
      escalateApproved: 0,
      escalateScheduled: 12,
      hqAcceptedOpen: 12,
      inProgress: 7,
    });
    renderWithProviders(
      <ComplaintByStatus rows={kpis.byStatus} loading={false} />,
    );
    expect(screen.getByText("Scheduled at HQ")).toBeTruthy();
    expect(screen.getByText("12")).toBeTruthy();
    expect(screen.getByText("30")).toBeTruthy();
  });
});
