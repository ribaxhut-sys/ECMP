import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { createEmptyComplaintForm } from "./createComplaintForm";
import {
  clearEscalateIntakeDraft,
  peekEscalateIntakeDraft,
  stashEscalateIntakeDraft,
} from "./escalateIntakeDraft";

const push = vi.fn();
const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: (p: string) => p === "complaints:create",
    user: { id: "officer-1", branchId: null },
    roles: [],
  }),
}));

const fetchBranches = vi.fn();
const fetchPublicSettings = vi.fn();
const confirmCmBatch1Customer = vi.fn();
vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchBranches: (...args: unknown[]) => fetchBranches(...args),
    fetchPublicSettings: (...args: unknown[]) => fetchPublicSettings(...args),
    confirmCmBatch1Customer: (...args: unknown[]) =>
      confirmCmBatch1Customer(...args),
  };
});

vi.mock("./CustomerSearchPanel", () => ({
  CustomerSearchPanel: () => null,
}));
vi.mock("./ActiveComplaintsBanner", () => ({
  ActiveComplaintsBanner: () => null,
}));
vi.mock("./StagingAttachmentsPanel", () => ({
  StagingAttachmentsPanel: () => null,
}));
vi.mock("./DuplicateWarningPanel", () => ({
  DuplicateWarningPanel: () => null,
}));

vi.mock("@/lib/api/hqSchedule", () => ({
  fetchHqScheduleAvailability: vi.fn().mockResolvedValue({
    data: { days: [] },
  }),
  fetchHqScheduleAvailabilityDetail: vi.fn().mockResolvedValue({
    data: { days: [] },
  }),
  fetchHqScheduleHolidays: vi.fn().mockResolvedValue({
    data: [],
  }),
}));

import { CreateComplaintView } from "./CreateComplaintView";

afterEach(() => {
  cleanup();
  clearEscalateIntakeDraft();
});

beforeEach(() => {
  push.mockReset();
  replace.mockReset();
  fetchBranches.mockReset();
  fetchPublicSettings.mockReset();
  confirmCmBatch1Customer.mockReset();
  fetchBranches.mockResolvedValue({ data: [] });
  fetchPublicSettings.mockResolvedValue({ data: [] });
  confirmCmBatch1Customer.mockResolvedValue({
    data: { customerId: "cust-1", locked: true },
  });
});

describe("CreateComplaintView — catatan dan putusan per Case", () => {
  it("keeps notes inside each Case card and places Add Case after the last note", async () => {
    renderWithProviders(<CreateComplaintView />);

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /^case 1$/i }),
      ).toBeInTheDocument();
    });
    const case1Note = document.getElementById("resolution");
    expect(document.getElementById("description")).toBeInTheDocument();
    expect(case1Note).toBeInTheDocument();
    expect(
      screen.getByRole("radio", { name: /register this case/i }),
    ).toBeChecked();
    expect(
      screen.getByRole("radio", { name: /request escalation to hq/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("radio", { name: /complete this case/i }),
    ).toBeInTheDocument();

    const addCase = screen.getByRole("button", { name: /add case/i });
    expect(
      addCase.compareDocumentPosition(case1Note!) &
        Node.DOCUMENT_POSITION_PRECEDING,
    ).toBe(Node.DOCUMENT_POSITION_PRECEDING);

    await userEvent.click(addCase);
    expect(screen.getByRole("heading", { name: /^case 2$/i })).toBeInTheDocument();
    const extraNotes = document.querySelectorAll(
      '[id^="extraCase-note-"][role="combobox"]',
    );
    expect(extraNotes).toHaveLength(1);
    expect(
      addCase.compareDocumentPosition(extraNotes[0]!) &
        Node.DOCUMENT_POSITION_PRECEDING,
    ).toBe(Node.DOCUMENT_POSITION_PRECEDING);
    expect(
      screen.getAllByRole("radio", { name: /register this case/i }),
    ).toHaveLength(2);
    // Blank Case 2 is dropped on Simpan — still one filled Case, so Simpan stays usable.
    expect(
      screen.getByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    ).toBeEnabled();
    expect(
      screen.queryByRole("button", { name: /lock decision for case/i }),
    ).not.toBeInTheDocument();
  });

  it("hides lock controls for a single Case and keeps Simpan enabled", async () => {
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: "Uraian case 1",
        resolution: "Catatan case 1",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
    });
    renderWithProviders(<CreateComplaintView />);
    await waitFor(() => {
      expect(document.getElementById("description")).toBeInTheDocument();
    });
    expect(
      screen.queryByRole("button", { name: /lock decision for case/i }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId("intake-case-lock-summary"),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    ).toBeEnabled();
  });

  it("requires a note on a filled extra Case before apply", async () => {
    const user = userEvent.setup();
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: "Uraian case 1",
        resolution: "Sudah diinfokan ke wajib pajak.",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
      extraCaseDrafts: [
        { id: "e2", subject: "Case 2", description: "Uraian case 2", note: "" },
      ],
    });

    renderWithProviders(<CreateComplaintView />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /^case 2$/i })).toBeInTheDocument();
    });
    await user.click(
      screen.getByRole("button", { name: /lock decision for case 2/i }),
    );
    expect(push).not.toHaveBeenCalled();
    expect(
      screen.getByText(/notes are required so the branch knows/i),
    ).toBeInTheDocument();
  });

  it("collapses a Case card and keeps the decision visible in the header", async () => {
    const user = userEvent.setup();
    renderWithProviders(<CreateComplaintView />);
    await waitFor(() => {
      expect(document.getElementById("description")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: /^collapse$/i }));
    expect(document.getElementById("description")).not.toBeInTheDocument();
    expect(screen.getByText(/register this case/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /^expand$/i }));
    expect(document.getElementById("description")).toBeInTheDocument();
  });

  it("does not navigate to the retired escalate step", async () => {
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: "Uraian case 1",
        resolution: "Catatan case 1",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
      extraCaseDrafts: [
        { id: "e2", subject: "Case 2", description: "Uraian case 2", note: "Catatan case 2" },
      ],
    });

    renderWithProviders(<CreateComplaintView />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Catatan case 2")).toBeInTheDocument();
    });
    expect(peekEscalateIntakeDraft()?.extraCaseDrafts?.[0]?.note).toBe(
      "Catatan case 2",
    );
    expect(
      screen.getByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /^continue$/i }),
    ).not.toBeInTheDocument();
  });

  it("locks Case 1 when multiple Cases exist, disables fields, and unlocks for edits", async () => {
    const user = userEvent.setup();
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: "Uraian case 1",
        resolution: "Catatan case 1",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
      extraCaseDrafts: [
        {
          id: "e2",
          subject: "Case 2",
          description: "Uraian case 2",
          note: "Catatan case 2",
          priority: "MEDIUM",
        },
      ],
    });
    renderWithProviders(<CreateComplaintView />);
    await waitFor(() => {
      expect(document.getElementById("description")).toBeInTheDocument();
    });
    await user.click(
      screen.getByRole("button", { name: /lock decision for case 1/i }),
    );
    // Lock must not auto-collapse — officer still sees the locked fields.
    expect(document.getElementById("description")).toBeInTheDocument();
    expect(document.getElementById("description")).toHaveAttribute(
      "aria-disabled",
      "true",
    );
    expect(
      screen.getByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    ).toBeDisabled();
    expect(document.getElementById("case-priority-primary")).toBeDisabled();
    await user.click(
      screen.getByRole("button", { name: /edit decision for case 1/i }),
    );
    expect(document.getElementById("description")).not.toHaveAttribute(
      "aria-disabled",
      "true",
    );
    expect(document.getElementById("case-priority-primary")).not.toBeDisabled();
    expect(
      screen.getByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    ).toBeDisabled();
  });

  it("opens confirm when a single Case is saved without locking", async () => {
    const user = userEvent.setup();
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: "Uraian case 1",
        resolution: "Catatan case 1",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
    });
    renderWithProviders(<CreateComplaintView />);
    expect(
      screen.queryByRole("button", { name: /lock decision for case/i }),
    ).not.toBeInTheDocument();
    const save = await screen.findByRole("button", {
      name: /save the complaint with each case decision/i,
    });
    expect(save).toBeEnabled();
    await user.click(save);
    expect(
      await screen.findByRole("heading", { name: /save complaint\?/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/taxpayer:\s*ada/i)).toBeInTheDocument();
    expect(screen.getByText(/subject:\s*[“"]mesin error[”"]/i)).toBeInTheDocument();
    expect(
      screen.getByText(/the complaint will be saved and remain open for handling/i),
    ).toBeInTheDocument();
  });

  it("shows close-complaint outcome when the only Case is completed", async () => {
    const user = userEvent.setup();
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ayu Santoso",
        subject: "Lorem Ipsum",
        description: "Uraian case 1",
        resolution: "Catatan penyelesaian case 1",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
      case1Action: "close",
    });
    renderWithProviders(<CreateComplaintView />);
    await user.click(
      await screen.findByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    );
    expect(
      await screen.findByRole("heading", { name: /close complaint\?/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/taxpayer:\s*ayu santoso/i)).toBeInTheDocument();
    expect(
      screen.getByText(/this complaint will be closed as completed/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /yes, close complaint/i }),
    ).toBeInTheDocument();
  });

  it("requires every Case locked before apply when there are two Cases", async () => {
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: "Uraian case 1",
        resolution: "Catatan case 1",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
      extraCaseDrafts: [
        {
          id: "e2",
          subject: "Case 2",
          description: "Uraian case 2",
          note: "Catatan case 2",
          priority: "MEDIUM",
        },
      ],
    });
    renderWithProviders(<CreateComplaintView />);
    await waitFor(() => {
      expect(screen.getByTestId("intake-case-lock-summary")).toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    ).toBeDisabled();
    expect(
      screen.getByText(/lock every case decision before saving/i),
    ).toBeInTheDocument();
  });

  it("shows the HQ arrival picker when a Case is set to escalate", async () => {
    const user = userEvent.setup();
    renderWithProviders(<CreateComplaintView />);
    await waitFor(() => {
      expect(
        screen.getByRole("radio", { name: /request escalation to hq/i }),
      ).toBeInTheDocument();
    });
    expect(screen.queryByLabelText(/arrival date/i)).not.toBeInTheDocument();
    await user.click(
      screen.getByRole("radio", { name: /request escalation to hq/i }),
    );
    expect(screen.getByLabelText(/arrival date/i)).toBeInTheDocument();
    expect(screen.getByText(/proposed hq arrival/i)).toBeInTheDocument();
  });

  it("blocks saving an escalated single Case until an arrival slot is chosen", async () => {
    const user = userEvent.setup();
    stashEscalateIntakeDraft({
      values: {
        ...createEmptyComplaintForm({ channel: "BRANCH" }),
        customerId: "cust-1",
        customerName: "Ada",
        subject: "Mesin error",
        description: "Uraian case 1",
        resolution: "Alasan eskalasi yang cukup panjang.",
        priority: "HIGH",
      },
      stagingToken: "",
      hasStagedAttachments: false,
      overrideJustification: null,
      recordingUnitCode: "JKT01",
    });
    renderWithProviders(<CreateComplaintView />);
    await waitFor(() => {
      expect(document.getElementById("description")).toBeInTheDocument();
    });
    await user.click(
      screen.getByRole("radio", { name: /request escalation to hq/i }),
    );
    expect(
      screen.queryByRole("button", { name: /lock decision for case/i }),
    ).not.toBeInTheDocument();
    await user.click(
      screen.getByRole("button", {
        name: /save the complaint with each case decision/i,
      }),
    );
    expect(
      screen.getByText(/choose a proposed hq arrival date and time/i),
    ).toBeInTheDocument();
    expect(document.getElementById("description")).toBeInTheDocument();
  });
});
