import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchBranches = vi.fn();
const fetchDashboardRecentActivity = vi.fn();
const hasPermission = vi.fn((p: string) => p === "dashboard:read");

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    status: "authenticated",
    hasPermission,
    user: {
      id: "u-1",
      username: "ani",
      email: "ani@example.com",
      fullName: "Ani Petugas",
      roleId: "r1",
      branchId: "uuid-1",
      isActive: true,
      forcePasswordChange: false,
      lastLoginAt: "2026-08-16T01:00:00Z",
      createdAt: "2026-01-01T00:00:00Z",
      updatedAt: "2026-08-16T02:00:00Z",
      roles: ["AGENT"],
      permissions: ["dashboard:read"],
    },
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchBranches: (...args: unknown[]) => fetchBranches(...args),
    fetchDashboardRecentActivity: (...args: unknown[]) =>
      fetchDashboardRecentActivity(...args),
  };
});

import ProfilePage from "./page";

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  fetchBranches.mockReset();
  fetchDashboardRecentActivity.mockReset();
  hasPermission.mockReset();
  hasPermission.mockImplementation((p: string) => p === "dashboard:read");
  fetchBranches.mockResolvedValue({
    data: [{ id: "uuid-1", code: "JKT01", name: "Cabang Jakarta Selatan" }],
  });
  fetchDashboardRecentActivity.mockResolvedValue({
    data: [
      {
        eventType: "complaint.created",
        complaintNumber: "CMP-0001",
        timestamp: "2026-08-16T03:00:00Z",
        actor: "ani",
      },
      {
        eventType: "complaint.created",
        complaintNumber: "CMP-0002",
        timestamp: "2026-08-16T03:05:00Z",
        actor: "budi",
      },
    ],
  });
});

describe("ProfilePage", () => {
  it("shows name once in the identity card, not again under personal information", async () => {
    renderWithProviders(<ProfilePage />);
    expect(screen.getAllByText("Ani Petugas")).toHaveLength(1);
    expect(screen.getByText("@ani")).toBeInTheDocument();
    expect(screen.queryByText("Open security settings")).not.toBeInTheDocument();
    expect(screen.queryByText("Language")).not.toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Cabang Jakarta Selatan (JKT01)")).toBeInTheDocument();
    });
    expect(screen.queryByText(/uuid-1/)).not.toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("CMP-0001")).toBeInTheDocument();
    });
    expect(screen.queryByText("CMP-0002")).not.toBeInTheDocument();
    expect(screen.queryByText("Personal information")).not.toBeInTheDocument();
    expect(screen.getByText("Active since")).toBeInTheDocument();
    expect(screen.getByText("January 01, 2026, 07:00")).toBeInTheDocument();
  });
});
