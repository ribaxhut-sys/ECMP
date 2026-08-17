import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { createEmptyComplaintForm } from "./createComplaintForm";
import {
  clearEscalateIntakeDraft,
  stashEscalateIntakeDraft,
} from "./escalateIntakeDraft";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: (p: string) => p === "complaints:create",
    user: { id: "officer-1", branchId: null },
    roles: [],
  }),
}));

const fetchAnnouncement = vi.fn();
const fetchCmBatch1Customer360 = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchAnnouncement: (...args: unknown[]) => fetchAnnouncement(...args),
    fetchCmBatch1Customer360: (...args: unknown[]) =>
      fetchCmBatch1Customer360(...args),
  };
});

vi.mock("./ActiveComplaintsBanner", () => ({
  ActiveComplaintsBanner: () => null,
}));

vi.mock("./DuplicateWarningPanel", () => ({
  DuplicateWarningPanel: () => null,
}));

import { EscalateIntakeView } from "./EscalateIntakeView";

const AID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc";

afterEach(() => {
  cleanup();
  clearEscalateIntakeDraft();
});

beforeEach(() => {
  fetchAnnouncement.mockReset();
  fetchCmBatch1Customer360.mockReset();
  fetchCmBatch1Customer360.mockResolvedValue({ data: { activeComplaints: [] } });
  fetchAnnouncement.mockResolvedValue({
    data: {
      id: AID,
      title: "Libur Nasional",
      effectiveStatus: "PUBLISHED",
    },
  });
});

describe("EscalateIntakeView — Catatan mention chips", () => {
  it("renders intake-note @ mentions as chips, not raw marker text", async () => {
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: `Detail kasus @[Libur Nasional](announcement:${AID})`,
        resolution: `Sudah diinfokan. @[Libur Nasional](announcement:${AID})`,
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
    });

    renderWithProviders(<EscalateIntakeView />);

    await waitFor(() => {
      expect(
        screen.getAllByRole("button", { name: /Libur Nasional/i }),
      ).toHaveLength(2);
    });
    expect(screen.getByRole("heading", { name: /case 1/i })).toBeInTheDocument();
    expect(
      screen.getByRole("radio", { name: /register this case/i }),
    ).toBeChecked();
  });
});
