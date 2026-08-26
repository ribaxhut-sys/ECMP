/**
 * Pengaduan work list keeps the Status filter (Ditutup is `/ditutup`).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchCmBatch1Complaints = vi.fn();
const hasPermission = vi.fn((code: string) => code === "complaints:read");
let orgUnitCode: string | null | undefined = "UPPPD-A";
let search = "status=OPEN";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/complaints",
  useSearchParams: () => new URLSearchParams(search),
}));

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({ hasPermission, user: null }),
}));

vi.mock("@/features/announcements/useOrgUnitCode", () => ({
  useOrgUnitCode: () => orgUnitCode,
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmBatch1Complaints: (...args: unknown[]) =>
      fetchCmBatch1Complaints(...args),
  };
});

import { CmBatch1ComplaintListView } from "./CmBatch1ComplaintListView";

describe("CmBatch1ComplaintListView work-list filters", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchCmBatch1Complaints.mockReset();
    fetchCmBatch1Complaints.mockResolvedValue({
      data: [],
      meta: { totalItems: 0 },
    });
    hasPermission.mockImplementation((code: string) => code === "complaints:read");
    orgUnitCode = "UPPPD-A";
    search = "status=OPEN";
  });

  it("keeps the Status dropdown on the open work list", async () => {
    renderWithProviders(<CmBatch1ComplaintListView />);
    await waitFor(() => {
      expect(screen.getByTestId("cm-batch1-status-filter")).toBeInTheDocument();
    });
    expect(screen.getByRole("combobox", { name: "Status" })).toBeInTheDocument();
  });
});
