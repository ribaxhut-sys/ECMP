/**
 * ResolutionCard — Knowledge Reference (@) wiring on Penyelesaian.
 * Read mode renders `[title]` references as clickable; edit mode uses the
 * `@` mention textarea and round-trips the marker on submit.
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchComplaintResolution = vi.fn();
const resolveComplaint = vi.fn();
const searchKnowledge = vi.fn();
const hasPermission = vi.fn<(permission: string) => boolean>(() => true);
const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({ hasPermission, userId: "u-1" }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchComplaintResolution: (...args: unknown[]) => fetchComplaintResolution(...args),
    resolveComplaint: (...args: unknown[]) => resolveComplaint(...args),
    searchKnowledge: (...args: unknown[]) => searchKnowledge(...args),
  };
});

import { ApiError } from "@/lib/api";
import { ResolutionCard } from "./ResolutionCard";

const KNOWLEDGE_ID = "e5555555-5555-5555-5555-555555555555";

function resolution(overrides: Record<string, unknown> = {}) {
  return {
    id: "r-1",
    complaintId: "c-1",
    resolutionCategory: "SOLVED",
    rootCause: "Kesalahan input",
    resolutionNotes: `Penyelesaian sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:${KNOWLEDGE_ID}).`,
    resolvedBy: "u-1",
    resolvedByName: "Agent Satu",
    resolvedAt: "2026-08-01T00:00:00Z",
    isCurrent: true,
    ...overrides,
  };
}

describe("ResolutionCard — Knowledge Reference", () => {
  beforeEach(() => {
    fetchComplaintResolution.mockReset();
    resolveComplaint.mockReset();
    searchKnowledge.mockReset();
    hasPermission.mockReset().mockReturnValue(true);
    push.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders an existing reference in read mode as a clickable element", async () => {
    fetchComplaintResolution.mockResolvedValue({ data: resolution() });

    renderWithProviders(
      <ResolutionCard complaintId="c-1" status="RESOLVED" />,
    );

    const ref = await screen.findByRole("button", {
      name: /SOP Penanganan Pengaduan v2\.1/i,
    });
    await userEvent.click(ref);
    expect(push).toHaveBeenCalledWith(`/knowledge/${KNOWLEDGE_ID}`);
  });

  it("lets the user insert a Knowledge reference via @ and submits it unchanged", async () => {
    const user = userEvent.setup();
    fetchComplaintResolution.mockRejectedValue(new ApiError(404, "NOT_FOUND", "not found"));
    searchKnowledge.mockResolvedValue({
      data: [
        {
          id: KNOWLEDGE_ID,
          title: "SOP Penanganan Pengaduan",
          knowledgeType: "SOP",
          status: "ACTIVE",
          documentNumber: "SOP-001",
          summary: null,
          versionLabel: "2.1",
          effectiveFrom: null,
          effectiveTo: null,
          ownerOrgUnitId: "PUSAT",
          publishedAt: "2026-08-01T00:00:00Z",
          publishedBy: null,
          supersedesKnowledgeId: null,
          supersedesTitle: null,
          createdBy: null,
          createdAt: "2026-07-30T00:00:00Z",
          updatedBy: null,
          updatedAt: "2026-07-30T00:00:00Z",
          files: [],
        },
      ],
    });
    resolveComplaint.mockResolvedValue({
      data: { resolution: resolution(), complaintId: "c-1", status: "RESOLVED" },
    });

    renderWithProviders(<ResolutionCard complaintId="c-1" status="IN_PROGRESS" />);

    await waitFor(() => {
      expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    });
    await user.selectOptions(screen.getByLabelText(/category/i), "SOLVED");
    await user.type(screen.getByLabelText(/root cause/i), "Kesalahan input");
    await user.type(
      screen.getByLabelText(/resolution notes/i),
      "Sesuai @pengaduan",
    );

    const option = await screen.findByRole("option", {
      name: /SOP Penanganan Pengaduan/i,
    });
    await user.click(option);

    await user.click(screen.getByRole("button", { name: /record resolution/i }));

    await waitFor(() => {
      expect(resolveComplaint).toHaveBeenCalled();
    });
    const [, payload] = resolveComplaint.mock.calls[0] as [string, { resolutionNotes: string }];
    expect(payload.resolutionNotes).toContain(`knowledge:${KNOWLEDGE_ID}`);
    expect(payload.resolutionNotes).toContain("SOP Penanganan Pengaduan v2.1");
  });
});
