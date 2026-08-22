import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { CmBatch1ComplaintResponse, CmCase } from "@/lib/api";
import { renderWithProviders } from "@/test/harness";

const fetchCmCase = vi.fn();
const fetchCmBatch1Complaint = vi.fn();
const fetchCmBatch1Customer360 = vi.fn();
const fetchUsers = vi.fn();
const decideCmBatch1IntakeEscalation = vi.fn();
const hasPermission = vi.fn((code: string) =>
  code === "complaints:read" ||
  code === "complaints:update" ||
  code === "complaints:create",
);
const authState = {
  userId: "officer-dewi",
  roles: [] as string[],
};

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/complaints/cm/cases/case-1",
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    user: { id: authState.userId },
    roles: authState.roles,
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmCase: (...args: unknown[]) => fetchCmCase(...args),
    fetchCmBatch1Complaint: (...args: unknown[]) =>
      fetchCmBatch1Complaint(...args),
    fetchCmBatch1Customer360: (...args: unknown[]) =>
      fetchCmBatch1Customer360(...args),
    fetchUsers: (...args: unknown[]) => fetchUsers(...args),
    decideCmBatch1IntakeEscalation: (...args: unknown[]) =>
      decideCmBatch1IntakeEscalation(...args),
  };
});

vi.mock("./CaseHistoryPanel", () => ({
  CaseHistoryPanel: () => <div>HistoryPanel</div>,
}));

vi.mock("@/features/complaints/CmBatch1BoundAttachmentsCard", () => ({
  CmBatch1BoundAttachmentsCard: () => <div>AttachmentsCard</div>,
}));

import { CaseDetailView } from "./CaseDetailView";

const CASE_ID = "c02969f2-3c3b-47cd-808c-c7d0d4527940";
const COMPLAINT_ID = "11111111-1111-1111-1111-111111111111";

function baseCase(overrides: Partial<CmCase> = {}): CmCase {
  return {
    caseId: CASE_ID,
    caseNumber: "CASE-2026-000001",
    complaintId: COMPLAINT_ID,
    customerId: "cust-1",
    status: "IN_PROGRESS",
    caseType: "SERVICE",
    subject: "Late counter",
    description: "Queue too long",
    priority: "MEDIUM",
    owningUnitId: "JKT-SELATAN",
    slaCountdownActive: false,
    createdAt: "2026-08-01T00:00:00Z",
    createdBy: "officer-dewi",
    handlingClaimedBy: "officer-dewi",
    handlingClaimedByName: "Dewi Hidayat",
    ...overrides,
  };
}

function baseComplaint(
  overrides: Partial<CmBatch1ComplaintResponse> = {},
): CmBatch1ComplaintResponse {
  return {
    complaintId: COMPLAINT_ID,
    complaintNumber: "CMP-0001",
    status: "IN_PROGRESS",
    customerId: "cust-1",
    customerDisplayName: "Budi",
    caseCreated: true,
    replayed: false,
    ...overrides,
  };
}

describe("CaseDetailView HQ path", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchCmCase.mockReset();
    fetchCmBatch1Complaint.mockReset();
    fetchCmBatch1Customer360.mockReset();
    fetchUsers.mockReset();
    decideCmBatch1IntakeEscalation.mockReset();
    hasPermission.mockImplementation(
      (code: string) =>
        code === "complaints:read" ||
        code === "complaints:update" ||
        code === "complaints:create",
    );
    authState.userId = "officer-dewi";
    authState.roles = ["SUPERVISOR"];
    fetchCmCase.mockResolvedValue({ data: baseCase() });
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    fetchCmBatch1Customer360.mockResolvedValue({ data: { profile: {} } });
    fetchUsers.mockResolvedValue({ data: [] });
  });

  it("keeps resolve and handler title while the parent is still at the branch", async () => {
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", {
          name: "Handling in progress (Dewi Hidayat)",
        }),
      ).toBeInTheDocument();
    });
    expect(screen.getByRole("button", { name: "Resolve" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Reassign handling" }),
    ).toBeInTheDocument();
    expect(screen.queryByTestId("case-hq-schedule-card")).not.toBeInTheDocument();
  });

  it("hides resolve and uses HQ schedule copy once the parent is HQ_SCHEDULED", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        intakeDisposition: "HQ_SCHEDULED",
        hqAcceptedAt: "2026-08-17T10:00:00Z",
        hqArrivalDate: "2026-08-20",
        hqArrivalTime: "09:30",
        hqArrivalNote: "2026-08-20 09:30\nBring original documents",
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getAllByRole("heading", {
          name: "Taxpayer arrival schedule",
        }).length,
      ).toBeGreaterThanOrEqual(1);
    });
    expect(
      screen.queryByRole("heading", {
        name: "Handling in progress (Dewi Hidayat)",
      }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Resolve" })).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Reassign handling" }),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId("case-hq-schedule-card")).toHaveAttribute(
      "data-tone",
      "info",
    );
    expect(screen.getByText("Arrival scheduled")).toBeInTheDocument();
    expect(
      screen.getAllByText("Thursday, August 20, 2026 at 09:30").length,
    ).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Bring original documents")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Continue to parent complaint" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Cancel escalation" }),
    ).not.toBeInTheDocument();
  });

  it("shows parent-level Cancel escalation while HQ has not accepted", async () => {
    hasPermission.mockImplementation(
      (code: string) =>
        code === "complaints:read" ||
        code === "complaints:update" ||
        code === "complaints:create" ||
        code === "complaints:escalate",
    );
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({ intakeDisposition: "ESCALATE_APPROVED" }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Cancel escalation" }),
      ).toBeInTheDocument();
    });
    expect(screen.queryByRole("button", { name: "Resolve" })).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Cancel escalation" }));
    expect(
      screen.getByText(
        /cancels HQ escalation for parent complaint CMP-0001, including every Case under it/i,
      ),
    ).toBeInTheDocument();

    decideCmBatch1IntakeEscalation.mockResolvedValue({
      data: baseComplaint({
        intakeDisposition: "ESCALATE_CANCELLED",
        cancellationNote: "Wajib Pajak setuju ditangani di cabang.",
      }),
    });
    await userEvent.type(
      screen.getByLabelText(/cancellation reason/i),
      "Wajib Pajak setuju ditangani di cabang.",
    );
    await userEvent.click(
      screen.getAllByRole("button", { name: "Cancel escalation" })[1],
    );
    await waitFor(() => {
      expect(decideCmBatch1IntakeEscalation).toHaveBeenCalledWith(COMPLAINT_ID, {
        decision: "CANCEL",
        note: "Wajib Pajak setuju ditangani di cabang.",
      });
    });
    expect(
      screen.getByText(
        /applies to every Case under the parent, not this Case alone/i,
      ),
    ).toBeInTheDocument();
  });

  it("hides Cancel escalation for officers without complaints:escalate", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({ intakeDisposition: "ESCALATE_APPROVED" }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Continue to parent complaint" }),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByRole("button", { name: "Cancel escalation" }),
    ).not.toBeInTheDocument();
  });
});
