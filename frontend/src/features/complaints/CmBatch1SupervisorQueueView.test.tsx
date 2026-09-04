/**
 * Smoke — supervisor queue view (API-513 Mode A visibility harden).
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
  useLocale: () => "id",
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
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
    hasPermission: (p: string) => p === "complaints:read",
  }),
}));

const fetchCmBatch1SupervisorQueue = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmBatch1SupervisorQueue: (...args: unknown[]) =>
      fetchCmBatch1SupervisorQueue(...args),
  };
});

import { CmBatch1SupervisorQueueView } from "./CmBatch1SupervisorQueueView";

describe("CmBatch1SupervisorQueueView", () => {
  afterEach(() => {
    cleanup();
    fetchCmBatch1SupervisorQueue.mockReset();
  });

  it("renders empty queues safely", async () => {
    fetchCmBatch1SupervisorQueue.mockResolvedValue({
      data: {
        laterReviewItems: [],
        agingComplaints: [],
        agingThresholdHours: 24,
        asOf: "2026-07-31T00:00:00Z",
      },
    });
    render(<CmBatch1SupervisorQueueView />);
    expect(await screen.findByText("noOpenLaterReview")).toBeInTheDocument();
    expect(screen.getByText("noAgingComplaints")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "goToComplaints" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "goToQueue" }),
    ).not.toBeInTheDocument();
  });

  it("renders API-513 fields including unknown reason without rewrite", async () => {
    fetchCmBatch1SupervisorQueue.mockResolvedValue({
      data: {
        laterReviewItems: [
          {
            workItemId: "LR-TEST0001",
            customerId: "CUST-1",
            complaintId: "cmp-bind-1",
            reason: "future_enrichment_v2",
            status: "OPEN",
            createdAt: "2026-07-30T00:00:00Z",
            ageHours: 36,
          },
        ],
        agingComplaints: [
          {
            complaintId: "cmp-1",
            complaintNumber: "CM-0001",
            customerId: "CUST-1",
            status: "REGISTERED",
            subject: "Aged subject",
            priority: "MEDIUM",
            createdAt: "2026-07-29T00:00:00Z",
            ageHours: 48,
            caseCreated: false,
          },
        ],
        agingThresholdHours: 24,
        asOf: "2026-07-31T00:00:00Z",
      },
    });
    render(<CmBatch1SupervisorQueueView />);
    expect(await screen.findAllByText("openComplaint")).not.toHaveLength(0);
    expect(screen.getAllByText("future_enrichment_v2").length).toBeGreaterThan(
      0,
    );
    expect(screen.getAllByText("unknownType").length).toBeGreaterThan(0);
    expect(screen.getAllByText("statusOpen").length).toBeGreaterThan(0);
    expect(screen.getAllByText("CM-0001").length).toBeGreaterThan(0);
    expect(screen.getAllByText("registered").length).toBeGreaterThan(0);
    // caseCreated=false renders via common.no (identity mock -> key name).
    expect(screen.getAllByText("no").length).toBeGreaterThan(0);
  });
});
