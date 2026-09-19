/**
 * Ditutup archive fetches CLOSED + COMPLETED (cabang) or HQ_CLOSED (Pusat).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchCmBatch1Complaints = vi.fn();
const hasPermission = vi.fn((code: string) => code === "complaints:read");
let orgUnitCode: string | null | undefined = "UPPPD-A";
let search = "";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/ditutup",
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

import { ClosedArchiveListView } from "./ClosedArchiveListView";

describe("ClosedArchiveListView", () => {
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
    search = "";
  });

  it("loads cabang archive as CLOSED + COMPLETED", async () => {
    renderWithProviders(<ClosedArchiveListView />);
    await waitFor(() => {
      expect(fetchCmBatch1Complaints).toHaveBeenCalled();
    });
    expect(fetchCmBatch1Complaints).toHaveBeenCalledWith(
      expect.objectContaining({
        status: "CLOSED",
        intakeDisposition: "COMPLETED",
      }),
    );
    expect(
      screen.getByRole("heading", { name: "Closed" }),
    ).toBeInTheDocument();
  });

  it("loads Pusat archive as CLOSED + HQ_CLOSED", async () => {
    orgUnitCode = "PUSAT";
    renderWithProviders(<ClosedArchiveListView />);
    await waitFor(() => {
      expect(fetchCmBatch1Complaints).toHaveBeenCalledWith(
        expect.objectContaining({
          status: "CLOSED",
          intakeDisposition: "HQ_CLOSED",
        }),
      );
    });
  });

  it("shows Case number above complaint number for cabang", async () => {
    fetchCmBatch1Complaints.mockResolvedValue({
      data: [
        {
          complaintId: "cmp-1",
          complaintNumber: "CMTAB-2608-0028",
          status: "CLOSED",
          intakeDisposition: "BRANCH_CLOSED",
          customerId: "cust-1",
          caseCreated: true,
          replayed: false,
          cases: [
            {
              caseId: "case-1",
              caseNumber: "TAB-2608-0028",
              complaintId: "cmp-1",
              status: "CLOSED",
            },
          ],
        },
      ],
      meta: { totalItems: 1 },
    });
    renderWithProviders(<ClosedArchiveListView />);
    const caseLink = (await screen.findAllByRole("link", { name: "TAB-2608-0028" }))[0];
    const complaintLink = screen.getAllByRole("link", { name: "CMTAB-2608-0028" })[0];
    expect(caseLink).toBeDefined();
    expect(complaintLink).toBeDefined();
    expect(caseLink!.compareDocumentPosition(complaintLink!)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
    expect(
      screen.getAllByRole("columnheader", { name: "Case" }).length,
    ).toBeGreaterThan(0);
  });
});
