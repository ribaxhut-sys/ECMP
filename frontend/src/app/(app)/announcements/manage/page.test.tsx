/**
 * /announcements/manage — Pusat manage only; Cabang redirected to history.
 */
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const hasPermission = vi.fn();
let mockRoles: string[] = ["SUPER_ADMIN"];
let mockUser: { id: string; branchId: string | null } | null = {
  id: "u1",
  branchId: null,
};
let mockStatus: "authenticated" | "loading" = "authenticated";
const replace = vi.fn();
const fetchBranches = vi.fn();

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    roles: mockRoles,
    user: mockUser,
    status: mockStatus,
  }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchBranches: (...args: unknown[]) => fetchBranches(...args),
  };
});

vi.mock("@/features/announcements", () => ({
  AnnouncementManagement: () => <div data-testid="management-view" />,
  AnnouncementHistoryView: () => <div data-testid="history-view" />,
}));

import AnnouncementsManagePage from "./page";

describe("AnnouncementsManagePage", () => {
  beforeEach(() => {
    hasPermission.mockReset();
    replace.mockReset();
    fetchBranches.mockReset();
    mockRoles = ["SUPER_ADMIN"];
    mockUser = { id: "u1", branchId: null };
    mockStatus = "authenticated";
    fetchBranches.mockResolvedValue({ data: [] });
    hasPermission.mockImplementation((code: string) => code === "announcement:manage");
  });

  afterEach(() => {
    cleanup();
  });

  it("renders management for unscoped Admin", async () => {
    render(<AnnouncementsManagePage />);
    await waitFor(() =>
      expect(screen.getByTestId("management-view")).toBeInTheDocument(),
    );
    expect(replace).not.toHaveBeenCalled();
  });

  it("redirects Manager Cabang to /announcements", async () => {
    mockRoles = ["MANAGER"];
    mockUser = { id: "u2", branchId: "branch-cabang" };
    fetchBranches.mockResolvedValue({
      data: [
        {
          id: "branch-cabang",
          code: "UPPPD-TANAH-ABANG",
          name: "UPPPD Tanah Abang",
        },
      ],
    });

    render(<AnnouncementsManagePage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/announcements"));
    expect(screen.queryByTestId("management-view")).not.toBeInTheDocument();
  });

  it("renders management for Supervisor Pusat", async () => {
    mockRoles = ["SUPERVISOR"];
    mockUser = { id: "u3", branchId: "branch-pusat" };
    fetchBranches.mockResolvedValue({
      data: [{ id: "branch-pusat", code: "PUSAT", name: "Pusat" }],
    });

    render(<AnnouncementsManagePage />);

    await waitFor(() =>
      expect(screen.getByTestId("management-view")).toBeInTheDocument(),
    );
  });
});
