import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { CmBatch1ComplaintResponse, CmCase } from "@/lib/api";
import { renderWithProviders } from "@/test/harness";

const fetchCmCase = vi.fn();
const fetchCmBatch1Complaint = vi.fn();
const fetchCmBatch1Customer360 = vi.fn();
const fetchUsers = vi.fn();
const fetchBranches = vi.fn();
const fetchCmCaseHistory = vi.fn();
const decideCmBatch1IntakeEscalation = vi.fn();
const escalateCmCaseToPusat = vi.fn();
const cancelCmCaseEscalationToPusat = vi.fn();
const acceptAndScheduleCmBatch1HqEscalation = vi.fn();
const returnCmBatch1HqEscalation = vi.fn();
const scheduleCmBatch1HqArrival = vi.fn();
const completeCmBatch1HqVisit = vi.fn();
const hasPermission = vi.fn((code: string) =>
  code === "complaints:read" ||
  code === "complaints:update" ||
  code === "complaints:create",
);
const authState = {
  userId: "officer-dewi",
  roles: [] as string[],
};
let orgUnitCode: string | null | undefined = "JKT-SELATAN";

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

vi.mock("@/features/announcements/useOrgUnitCode", () => ({
  useOrgUnitCode: () => orgUnitCode,
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
    fetchBranches: (...args: unknown[]) => fetchBranches(...args),
    fetchCmCaseHistory: (...args: unknown[]) => fetchCmCaseHistory(...args),
    decideCmBatch1IntakeEscalation: (...args: unknown[]) =>
      decideCmBatch1IntakeEscalation(...args),
    escalateCmCaseToPusat: (...args: unknown[]) =>
      escalateCmCaseToPusat(...args),
    cancelCmCaseEscalationToPusat: (...args: unknown[]) =>
      cancelCmCaseEscalationToPusat(...args),
    acceptAndScheduleCmBatch1HqEscalation: (...args: unknown[]) =>
      acceptAndScheduleCmBatch1HqEscalation(...args),
    returnCmBatch1HqEscalation: (...args: unknown[]) =>
      returnCmBatch1HqEscalation(...args),
    scheduleCmBatch1HqArrival: (...args: unknown[]) =>
      scheduleCmBatch1HqArrival(...args),
    completeCmBatch1HqVisit: (...args: unknown[]) =>
      completeCmBatch1HqVisit(...args),
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
    fetchBranches.mockReset();
    fetchCmCaseHistory.mockReset();
    decideCmBatch1IntakeEscalation.mockReset();
    escalateCmCaseToPusat.mockReset();
    cancelCmCaseEscalationToPusat.mockReset();
    acceptAndScheduleCmBatch1HqEscalation.mockReset();
    returnCmBatch1HqEscalation.mockReset();
    scheduleCmBatch1HqArrival.mockReset();
    completeCmBatch1HqVisit.mockReset();
    orgUnitCode = "JKT-SELATAN";
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
    fetchBranches.mockResolvedValue({
      data: [{ id: "branch-pusat-cro", code: "PUSAT-CRO", name: "CRO Pusat" }],
    });
    fetchCmCaseHistory.mockResolvedValue({ data: [] });
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
      screen.getByRole("button", { name: "Request escalation to HQ" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Reassign" }),
    ).toBeInTheDocument();
    expect(screen.queryByTestId("case-hq-schedule-card")).not.toBeInTheDocument();
  });

  it("links the parent complaint number to the parent complaint", async () => {
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    const link = await screen.findByTestId("case-parent-complaint-link");
    expect(link).toHaveTextContent("CMP-0001");
    expect(link).toHaveAttribute(
      "href",
      `/complaints/cm/${COMPLAINT_ID}?focus=penanganan`,
    );
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
      screen.queryByRole("button", { name: "Reassign" }),
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

  it("uses cancelled copy, not the closed copy, for a CANCELLED Case", async () => {
    fetchCmCase.mockResolvedValue({
      data: baseCase({ status: "CANCELLED" }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Case cancelled" }),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByRole("heading", { name: "Case has been closed" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText(
        "This case was cancelled and will not continue. See history for the cancellation reason.",
      ),
    ).toBeInTheDocument();
  });

  it("shows the resolved title and description, not the HQ slot label, once a scheduled-path Case is RESOLVED", async () => {
    fetchCmCase.mockResolvedValue({
      data: baseCase({ status: "RESOLVED" }),
    });
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        intakeDisposition: "HQ_SCHEDULED",
        hqAcceptedAt: "2026-08-17T10:00:00Z",
        hqArrivalDate: "2026-08-20",
        hqArrivalTime: "09:30",
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    const heading = await waitFor(() =>
      screen.getByRole("heading", { name: "Case has been resolved" }),
    );
    // The HQ arrival slot may still appear in the schedule card body — only
    // the page header description must not regress to the bare slot label.
    const header = heading.closest("header");
    expect(header).not.toBeNull();
    expect(header).not.toHaveTextContent("Thursday, August 20, 2026 at 09:30");
  });

  it("tells the branch who at Pusat is handling once Pusat claims an escalated Case", async () => {
    fetchCmCase.mockResolvedValue({
      data: baseCase({
        escalatedToPusat: true,
        owningUnit: "PUSAT",
        handlingClaimedBy: "officer-pusat-1",
        handlingClaimedByName: "Rahma Sari",
      }),
    });
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({ intakeDisposition: "ESCALATE_APPROVED" }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", {
          name: "Being handled by Pusat (Rahma Sari)",
        }),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByRole("heading", { name: "Case sent to Pusat" }),
    ).not.toBeInTheDocument();
  });

  it("hides Cancel escalation and uses schedule title after HQ accepted a Case still flagged to Pusat", async () => {
    fetchCmCase.mockResolvedValue({
      data: baseCase({
        escalatedToPusat: true,
        owningUnit: "PUSAT",
        handlingClaimedBy: null,
        handlingClaimedByName: null,
      }),
    });
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        intakeDisposition: "HQ_SCHEDULED",
        hqAcceptedAt: "2026-08-17T10:00:00Z",
        hqArrivalDate: "2026-08-20",
        hqArrivalTime: "09:30",
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
      screen.queryByRole("heading", { name: "Case sent to Pusat" }),
    ).not.toBeInTheDocument();
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

  it("renders HQ accept and return actions on the Case page for Pusat reviewers", async () => {
    orgUnitCode = "PUSAT";
    authState.userId = "pusat-reviewer";
    authState.roles = ["SCHEDULER"];
    hasPermission.mockImplementation(
      (code: string) =>
        code === "complaints:read" ||
        code === "complaints:update" ||
        code === "complaints:create" ||
        code === "escalations:review",
    );
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        status: "IN_PROGRESS",
        intakeDisposition: "ESCALATE_APPROVED",
        hqAcceptedAt: null,
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Accept & schedule" }),
      ).toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", { name: /return/i }),
    ).toBeInTheDocument();
  });

  it("prefills branch proposed arrival when opening Accept & schedule", async () => {
    orgUnitCode = "PUSAT";
    authState.userId = "pusat-reviewer";
    authState.roles = ["SCHEDULER"];
    hasPermission.mockImplementation(
      (code: string) =>
        code === "complaints:read" ||
        code === "complaints:update" ||
        code === "complaints:create" ||
        code === "escalations:review",
    );
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        status: "IN_PROGRESS",
        intakeDisposition: "ESCALATE_APPROVED",
        hqAcceptedAt: null,
        proposedArrivalDate: "2099-08-20",
        proposedArrivalTime: "09:30",
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Accept & schedule" }),
      ).toBeInTheDocument();
    });
    await userEvent.click(
      screen.getByRole("button", { name: "Accept & schedule" }),
    );
    await waitFor(() => {
      expect(
        screen.getByText(/Branch proposed 2099-08-20 at 09:30/i),
      ).toBeInTheDocument();
    });
    expect(screen.getByText("20/08/2099")).toBeInTheDocument();
    expect(
      screen.getByText(/Destination unit: PUSAT-CRO/i),
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

  it("submits Case-level escalate to HQ without using parent complaint", async () => {
    escalateCmCaseToPusat.mockResolvedValue({
      data: baseCase({
        escalatedToPusat: true,
        owningUnit: "PUSAT",
        escalationReason: "Case cabang tidak bisa diselesaikan di unit ini.",
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Request escalation to HQ" }),
      ).toBeInTheDocument();
    });
    await userEvent.click(
      screen.getByRole("button", { name: "Request escalation to HQ" }),
    );
    await userEvent.type(
      screen.getByLabelText(/escalation reason/i),
      "Case cabang tidak bisa diselesaikan di unit ini.",
    );
    await userEvent.click(screen.getByRole("button", { name: "Send to HQ" }));
    await waitFor(() => {
      expect(escalateCmCaseToPusat).toHaveBeenCalledWith(CASE_ID, {
        reason: "Case cabang tidak bisa diselesaikan di unit ini.",
      });
    });
  });

  it("shows Cancel escalation for the branch before Pusat claims the Case", async () => {
    fetchCmCase.mockResolvedValue({
      data: baseCase({
        escalatedToPusat: true,
        owningUnit: "PUSAT",
        handlingClaimedBy: null,
        handlingClaimedByName: null,
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Cancel escalation" }),
      ).toBeInTheDocument();
    });
    expect(screen.queryByRole("button", { name: "Resolve" })).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Request escalation to HQ" }),
    ).not.toBeInTheDocument();
  });

  it("lets a Pusat officer claim an escalated Case instead of cancel", async () => {
    orgUnitCode = "PUSAT";
    authState.userId = "pusat-1";
    authState.roles = ["AGENT"];
    fetchCmCase.mockResolvedValue({
      data: baseCase({
        escalatedToPusat: true,
        owningUnit: "PUSAT",
        handlingClaimedBy: null,
        handlingClaimedByName: null,
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(screen.getByTestId("case-with-pusat-note")).toHaveTextContent(
        /claim handling/i,
      );
    });
    expect(
      screen.queryByRole("button", { name: "Cancel escalation" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /return to branch|kembalikan/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Request escalation to HQ" }),
    ).not.toBeInTheDocument();
    await waitFor(() => {
      expect(
        screen.getByText(/Take this Case for HQ handling\?|Ambil Case ini untuk ditangani Pusat\?/i),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByText(/Registered by|Didaftarkan/i),
    ).not.toBeInTheDocument();
  });

  it("shows one return button when parent HQ path and Case DEC-029 return overlap", async () => {
    orgUnitCode = "PUSAT";
    authState.userId = "pusat-1";
    authState.roles = ["AGENT"];
    fetchCmCase.mockResolvedValue({
      data: baseCase({
        escalatedToPusat: true,
        owningUnit: "PUSAT",
        handlingClaimedBy: "pusat-1",
        handlingClaimedByName: "Teguh Prasetyo",
      }),
    });
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        intakeDisposition: "ESCALATE_APPROVED",
      }),
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(screen.getByTestId("case-return-escalation")).toBeInTheDocument();
    });
    expect(screen.getAllByRole("button", { name: /return to branch|kembalikan/i }))
      .toHaveLength(1);
    await userEvent.click(screen.getByTestId("case-return-escalation"));
    await waitFor(() => {
      expect(screen.getByLabelText(/return reason|alasan pengembalian/i)).toBeInTheDocument();
    });
  });
});

describe("CaseDetailView handling notes", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchCmCase.mockReset();
    fetchCmBatch1Complaint.mockReset();
    fetchCmBatch1Customer360.mockReset();
    fetchUsers.mockReset();
    fetchCmCaseHistory.mockReset();
    hasPermission.mockImplementation(
      (code: string) =>
        code === "complaints:read" ||
        code === "complaints:update" ||
        code === "complaints:create",
    );
    authState.userId = "officer-dewi";
    authState.roles = [];
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    fetchCmBatch1Customer360.mockResolvedValue({ data: { profile: {} } });
    fetchUsers.mockResolvedValue({ data: [] });
  });

  it("shows catatan under description; note bodies stay in handling notes, not the history log", async () => {
    fetchCmCase.mockResolvedValue({
      data: baseCase({
        description: "Queue too long\n\n---\nCatatan:\nSudah dijelaskan",
      }),
    });
    fetchCmCaseHistory.mockResolvedValue({
      data: [
        {
          entryId: "3",
          eventCode: "HQ_ACCEPTED",
          eventType: "HqAccepted",
          occurredAt: "2026-08-18T03:00:00Z",
          actorName: "Budi",
          note: "OK unit",
        },
      ],
    });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(screen.getByTestId("case-handling-notes")).toHaveTextContent(
        "OK unit",
      );
    });
    expect(screen.getByText("Queue too long")).toBeInTheDocument();
    expect(screen.queryByText(/---/)).not.toBeInTheDocument();
    const notes = screen.getByTestId("case-handling-notes");
    expect(notes).toHaveTextContent("Sudah dijelaskan");
    expect(notes).toHaveTextContent("OK unit");
    expect(notes).toHaveTextContent("HQ accepted");
  });

  it("shows parent intake Catatan when the Case description has none", async () => {
    fetchCmCase.mockResolvedValue({ data: baseCase() });
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        branchResolution: "Sudah diinfokan ke wajib pajak",
      }),
    });
    fetchCmCaseHistory.mockResolvedValue({ data: [] });
    renderWithProviders(<CaseDetailView caseId={CASE_ID} />);
    await waitFor(() => {
      expect(screen.getByTestId("case-handling-notes")).toHaveTextContent(
        "Sudah diinfokan ke wajib pajak",
      );
    });
  });
});
