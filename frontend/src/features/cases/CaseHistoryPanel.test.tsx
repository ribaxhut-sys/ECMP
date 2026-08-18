import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { CmCaseHistoryEntry } from "@/lib/api";

const fetchCmCaseHistory = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/complaints/cm/cases/case-1",
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmCaseHistory: (...args: unknown[]) => fetchCmCaseHistory(...args),
  };
});

import { CaseHistoryPanel } from "./CaseHistoryPanel";

function entry(
  overrides: Partial<CmCaseHistoryEntry> &
    Pick<CmCaseHistoryEntry, "entryId" | "eventCode">,
): CmCaseHistoryEntry {
  return {
    eventType: overrides.eventCode,
    occurredAt: "2026-08-18T03:00:00Z",
    actorName: "Ayu",
    ...overrides,
  };
}

describe("CaseHistoryPanel", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchCmCaseHistory.mockReset();
  });

  it("lists this Case's events with complaint-log chrome and hidden notes", async () => {
    fetchCmCaseHistory.mockResolvedValue({
      data: [
        entry({ entryId: "1", eventCode: "CASE_CREATED" }),
        entry({
          entryId: "2",
          eventCode: "CASE_WORK_STARTED",
          actorName: "Ayu",
        }),
        entry({
          entryId: "3",
          eventCode: "CASE_HANDLING_UNIT_ACCEPTED",
          actorName: "Budi",
          note: "OK unit",
        }),
      ],
    });
    renderWithProviders(<CaseHistoryPanel caseId="case-1" />);
    await waitFor(() =>
      expect(screen.getByTestId("case-history")).toBeInTheDocument(),
    );
    expect(screen.getByText("Case history")).toBeInTheDocument();
    expect(screen.getByText("Case created")).toBeInTheDocument();
    expect(screen.getByText("Work started")).toBeInTheDocument();
    expect(screen.getByText("Handling unit accepted")).toBeInTheDocument();
    expect(screen.queryByText("OK unit")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Show note/ })).toBeInTheDocument();
    expect(fetchCmCaseHistory).toHaveBeenCalledWith("case-1");
  });

  it("expands a note like the complaint event log", async () => {
    const user = userEvent.setup();
    fetchCmCaseHistory.mockResolvedValue({
      data: [
        entry({
          entryId: "3",
          eventCode: "CASE_HANDLING_UNIT_ACCEPTED",
          actorName: "Budi",
          note: "OK unit",
        }),
      ],
    });
    renderWithProviders(<CaseHistoryPanel caseId="case-1" />);
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /Show note/ })).toBeInTheDocument(),
    );
    await user.click(screen.getByRole("button", { name: /Show note/ }));
    expect(screen.getByText("OK unit")).toBeInTheDocument();
  });

  it("shows HQ scheduled slot on the history row, note collapsed", async () => {
    fetchCmCaseHistory.mockResolvedValue({
      data: [
        entry({
          entryId: "h1",
          eventCode: "HQ_ARRIVAL_SCHEDULED",
          actorName: "Pusat",
          arrivalDate: "2026-08-20",
          arrivalTime: "09:30",
          note: "Bring original documents",
        }),
      ],
    });
    renderWithProviders(<CaseHistoryPanel caseId="case-1" />);
    await waitFor(() =>
      expect(screen.getByText("Taxpayer arrival scheduled")).toBeInTheDocument(),
    );
    expect(
      screen.getByText("Thursday, August 20, 2026 at 09:30"),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Bring original documents"),
    ).not.toBeInTheDocument();
  });

  it("shows empty copy inside the card", async () => {
    fetchCmCaseHistory.mockResolvedValue({ data: [] });
    renderWithProviders(<CaseHistoryPanel caseId="case-1" />);
    await waitFor(() =>
      expect(
        screen.getByText("No events recorded for this Case yet."),
      ).toBeInTheDocument(),
    );
  });
});
