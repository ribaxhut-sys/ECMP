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

  it("lists events as a compact log without note bodies (no case/status/unit blocks)", async () => {
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
            eventCode: "CASE_RESOLVED",
            actorName: "Budi",
            note: "OK unit",
            actorUnitId: "PUSAT-CRO",
            caseStatus: "RESOLVED",
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
        "Event log for this Case. Note text is shown under Handling notes.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Case created")).toBeInTheDocument();
    expect(screen.getByText("Work started")).toBeInTheDocument();
    expect(screen.getByText("Case resolved")).toBeInTheDocument();
    expect(screen.queryByText("OK unit")).not.toBeInTheDocument();
    expect(screen.queryByText("PUSAT-CRO")).not.toBeInTheDocument();
    expect(screen.queryByText("RESOLVED")).not.toBeInTheDocument();
    expect(screen.queryByText("CASE-2026-0001")).not.toBeInTheDocument();
  });

  it("hides Internal dual-acceptance events on taxpayer Case history", async () => {
    renderWithProviders(
      <CaseHistoryPanel
        loading={false}
        error={null}
        entries={[
          entry({ entryId: "1", eventCode: "CASE_RESOLVED", actorName: "Ayu" }),
          entry({
            entryId: "2",
            eventCode: "CASE_OWNER_ACCEPTED",
            actorName: "Admin Utama",
          }),
          entry({
            entryId: "3",
            eventCode: "CASE_HANDLING_UNIT_ACCEPTED",
            actorName: "Budi",
          }),
          entry({ entryId: "4", eventCode: "CASE_CLOSED", actorName: "Ayu" }),
        ]}
      />,
    );
    await waitFor(() =>
      expect(screen.getByText("Case resolved")).toBeInTheDocument(),
    );
    expect(screen.getByText("Case closed")).toBeInTheDocument();
    expect(screen.queryByText("Owner accepted")).not.toBeInTheDocument();
    expect(
      screen.queryByText("Handling unit accepted"),
    ).not.toBeInTheDocument();
  });

  it("shows HQ scheduled slot without the visit note body", async () => {
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
    expect(
      screen.queryByText("Bring original documents"),
    ).not.toBeInTheDocument();
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
      screen.queryByText("Case cabang tidak bisa diselesaikan di unit ini."),
    ).not.toBeInTheDocument();
  });

  it("labels a later send after HQ return as re-escalation", async () => {
    renderWithProviders(
      <CaseHistoryPanel
        loading={false}
        error={null}
        entries={[
          entry({
            entryId: "e1",
            eventCode: "CASE_ESCALATED_TO_PUSAT",
            actorName: "Dewi",
          }),
          entry({
            entryId: "r1",
            eventCode: "CASE_ESCALATION_RETURNED",
            actorName: "Daffa",
          }),
          entry({
            entryId: "e2",
            eventCode: "CASE_ESCALATED_TO_PUSAT",
            actorName: "Dewi",
            note: "Dokumen sudah dilengkapi.",
          }),
        ]}
      />,
    );
    await waitFor(() =>
      expect(screen.getByText("Sent back to HQ")).toBeInTheDocument(),
    );
    expect(screen.getByText("Sent to HQ")).toBeInTheDocument();
    expect(screen.getByText("Returned by HQ")).toBeInTheDocument();
    expect(
      screen.queryByText("Dokumen sudah dilengkapi."),
    ).not.toBeInTheDocument();
  });

  it("shows a priority tag once, then again only after it changes", async () => {
    renderWithProviders(
      <CaseHistoryPanel
        loading={false}
        error={null}
        entries={[
          entry({
            entryId: "1",
            eventCode: "CASE_CREATED",
            priority: "HIGH",
          }),
          entry({
            entryId: "2",
            eventCode: "CASE_WORK_STARTED",
            priority: "HIGH",
          }),
          entry({
            entryId: "3",
            eventCode: "CASE_ESCALATED_TO_PUSAT",
            priority: "HIGH",
          }),
          entry({
            entryId: "4",
            eventCode: "CASE_RESOLVED",
            actorName: "Budi",
            priority: "MEDIUM",
          }),
        ]}
      />,
    );
    await waitFor(() =>
      expect(screen.getByText("Case created")).toBeInTheDocument(),
    );
    expect(screen.getAllByText("High")).toHaveLength(1);
    expect(screen.getAllByText("Medium")).toHaveLength(1);
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
