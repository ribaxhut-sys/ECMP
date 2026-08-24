import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { CmCaseHistoryEntry } from "@/lib/api";
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

  it("lists this Case's events with operational detail blocks", async () => {
    renderWithProviders(
      <CaseHistoryPanel
        loading={false}
        error={null}
        entries={[
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
            actorUnitId: "PUSAT-CRO",
            caseStatus: "IN_PROGRESS",
            caseNumber: "CASE-2026-0001",
          }),
        ]}
      />,
    );
    await waitFor(() =>
      expect(screen.getByTestId("case-history")).toBeInTheDocument(),
    );
    expect(screen.getByText("Case history")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Full event history for this Case, including status, unit, and operational notes.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Case created")).toBeInTheDocument();
    expect(screen.getByText("Work started")).toBeInTheDocument();
    expect(screen.getByText("Handling unit accepted")).toBeInTheDocument();
    expect(screen.getByText("OK unit")).toBeInTheDocument();
    expect(screen.getByText("PUSAT-CRO")).toBeInTheDocument();
    expect(screen.getByText("IN_PROGRESS")).toBeInTheDocument();
    expect(screen.getByText("CASE-2026-0001")).toBeInTheDocument();
  });

  it("shows HQ scheduled slot and preserves the visit note", async () => {
    renderWithProviders(
      <CaseHistoryPanel
        loading={false}
        error={null}
        entries={[
          entry({
            entryId: "h1",
            eventCode: "HQ_ARRIVAL_SCHEDULED",
            actorName: "Pusat",
            arrivalDate: "2026-08-20",
            arrivalTime: "09:30",
            note: "Bring original documents",
          }),
        ]}
      />,
    );
    await waitFor(() =>
      expect(screen.getByText("Taxpayer arrival scheduled")).toBeInTheDocument(),
    );
    expect(
      screen.getByText("Thursday, August 20, 2026 at 09:30"),
    ).toBeInTheDocument();
    expect(screen.getByText("Bring original documents")).toBeInTheDocument();
  });

  it("labels Case escalation to HQ instead of Other", async () => {
    renderWithProviders(
      <CaseHistoryPanel
        loading={false}
        error={null}
        entries={[
          entry({
            entryId: "e1",
            eventCode: "CASE_ESCALATED_TO_PUSAT",
            actorName: "Dewi",
            note: "Case cabang tidak bisa diselesaikan di unit ini.",
          }),
        ]}
      />,
    );
    await waitFor(() =>
      expect(screen.getByText("Sent to HQ")).toBeInTheDocument(),
    );
    expect(
      screen.getByText("Case cabang tidak bisa diselesaikan di unit ini."),
    ).toBeInTheDocument();
  });

  it("shows empty copy inside the card", async () => {
    renderWithProviders(
      <CaseHistoryPanel loading={false} error={null} entries={[]} />,
    );
    await waitFor(() =>
      expect(
        screen.getByText("No events recorded for this Case yet."),
      ).toBeInTheDocument(),
    );
  });
});
