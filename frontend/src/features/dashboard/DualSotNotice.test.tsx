import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: (permission: string) =>
      permission === "complaints:read" || permission === "*",
  }),
}));

import { DualSotNotice } from "./DualSotNotice";

describe("DualSotNotice", () => {
  it("opens the CM complaint list (DEC-025 one-door), not /complaints/cm", () => {
    renderWithProviders(<DualSotNotice complaintKpiSource="aggregate" />);

    expect(screen.getByTestId("dashboard-dual-sot-notice")).toBeInTheDocument();
    expect(screen.getByText(/target SoT/i)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /open complaint list/i }),
    ).toHaveAttribute("href", "/complaints");
  });

  it("labels Foundation KPI as legacy, not a competing SoT", () => {
    renderWithProviders(<DualSotNotice complaintKpiSource="foundation" />);

    expect(screen.getByText(/foundation \(legacy\)/i)).toBeInTheDocument();
    expect(screen.queryByText(/two data sources/i)).not.toBeInTheDocument();
  });
});
