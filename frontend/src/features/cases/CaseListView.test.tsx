/**
 * CaseListView — permission / empty UX smoke.
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchCmCases = vi.fn();
const hasPermission = vi.fn((code: string) => code === "complaints:read");

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/complaints/cm/complaint-1/cases",
  useSearchParams: () => new URLSearchParams(),
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
  useAuth: () => ({
    hasPermission,
    user: null,
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmCases: (...args: unknown[]) => fetchCmCases(...args),
  };
});

import { CaseListView } from "./CaseListView";
import { clearKnownCaseIds } from "./caseSessionRegistry";

const COMPLAINT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";

describe("CaseListView", () => {
  afterEach(() => {
    cleanup();
    clearKnownCaseIds(COMPLAINT_ID);
  });

  beforeEach(() => {
    fetchCmCases.mockReset();
    fetchCmCases.mockResolvedValue({ data: [] });
    hasPermission.mockImplementation((code: string) => code === "complaints:read");
    sessionStorage.clear();
  });

  it("shows permission denied without complaints:read", () => {
    hasPermission.mockReturnValue(false);
    renderWithProviders(<CaseListView complaintId={COMPLAINT_ID} />);
    expect(screen.getByText(/permission denied/i)).toBeInTheDocument();
  });

  it("shows empty state when no session cases", async () => {
    renderWithProviders(<CaseListView complaintId={COMPLAINT_ID} />);
    await waitFor(() => {
      expect(screen.getByText(/no branch work for this complaint yet/i)).toBeInTheDocument();
    });
    expect(fetchCmCases).toHaveBeenCalled();
  });
});
