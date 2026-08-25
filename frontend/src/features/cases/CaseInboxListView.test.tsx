import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchCmCases = vi.fn();
const fetchCustomers = vi.fn();
const fetchCmBatch1Customer360 = vi.fn();
const hasPermission = vi.fn((code: string) => code === "complaints:read");
let orgUnitCode: string | null | undefined = "JKT-SELATAN";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({ hasPermission }),
}));

vi.mock("@/features/announcements/useOrgUnitCode", () => ({
  useOrgUnitCode: () => orgUnitCode,
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmCases: (...args: unknown[]) => fetchCmCases(...args),
    fetchCustomers: (...args: unknown[]) => fetchCustomers(...args),
    fetchCmBatch1Customer360: (...args: unknown[]) =>
      fetchCmBatch1Customer360(...args),
  };
});

import { CaseInboxListView } from "./CaseInboxListView";

describe("CaseInboxListView title", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchCmCases.mockReset();
    fetchCustomers.mockReset();
    fetchCmBatch1Customer360.mockReset();
    hasPermission.mockImplementation((code: string) => code === "complaints:read");
    orgUnitCode = "JKT-SELATAN";
    fetchCmCases.mockResolvedValue({ data: [], meta: { totalItems: 0 } });
    fetchCustomers.mockResolvedValue({ data: [] });
  });

  it("uses the branch inbox title for a Cabang unit", async () => {
    renderWithProviders(<CaseInboxListView />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "All branch Cases" }),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByRole("heading", { name: "Cases you are handling" }),
    ).not.toBeInTheDocument();
  });

  it("uses the Pusat inbox title for a Pusat unit", async () => {
    orgUnitCode = "PUSAT-CRO";
    renderWithProviders(<CaseInboxListView />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Cases you are handling" }),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByRole("heading", { name: "All branch Cases" }),
    ).not.toBeInTheDocument();
  });

  it("keeps the branch title while org unit is still loading", async () => {
    orgUnitCode = undefined;
    renderWithProviders(<CaseInboxListView />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "All branch Cases" }),
      ).toBeInTheDocument();
    });
  });

  it("shows access-denied under the correct audience title without complaints:read", () => {
    hasPermission.mockImplementation(() => false);
    orgUnitCode = "PUSAT-CRO";
    renderWithProviders(<CaseInboxListView />);
    expect(
      screen.getByRole("heading", { name: "Cases you are handling" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Permission denied")).toBeInTheDocument();
  });
});
