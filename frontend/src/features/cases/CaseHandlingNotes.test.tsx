import { cleanup, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { CaseHandlingNotes } from "./CaseHandlingNotes";
import type { CaseHandlingNote } from "./caseHandlingNotes";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/complaints/cm/cases/case-1",
  useSearchParams: () => new URLSearchParams(),
}));

function note(
  overrides: Partial<CaseHandlingNote> & Pick<CaseHandlingNote, "key" | "labelKey" | "text">,
): CaseHandlingNote {
  return {
    source: "history",
    occurredAt: "2026-08-24T15:57:00Z",
    actorName: "Dewi Hidayat",
    ...overrides,
  };
}

describe("CaseHandlingNotes", () => {
  afterEach(() => {
    cleanup();
  });

  it("nests HQ accept under case created", () => {
    renderWithProviders(
      <CaseHandlingNotes
        notes={[
          note({
            key: "1",
            labelKey: "eventCaseCreated",
            eventCode: "CASE_CREATED",
            text: "tes eska 1",
          }),
          note({
            key: "2",
            labelKey: "eventHqAccepted",
            eventCode: "HQ_ACCEPTED",
            actorName: "Teguh Prasetyo",
            text: "Pengaduan diterima di pusat",
          }),
        ]}
      />,
    );
    const panel = screen.getByTestId("case-handling-notes");
    expect(panel).toHaveTextContent("Case created");
    expect(panel).toHaveTextContent("HQ accepted");
    expect(panel).toHaveTextContent("tes eska 1");
    expect(panel).toHaveTextContent("Pengaduan diterima di pusat");
    const nested = screen.getByTestId("case-handling-note-children");
    expect(nested).toHaveTextContent("HQ accepted");
    expect(nested).not.toHaveTextContent("Case created");
  });

  it("labels a later arrival slot as rescheduled under the first schedule", () => {
    renderWithProviders(
      <CaseHandlingNotes
        notes={[
          note({
            key: "3",
            labelKey: "eventHqScheduled",
            eventCode: "HQ_ARRIVAL_SCHEDULED",
            text: "Slot pertama",
          }),
          note({
            key: "4",
            labelKey: "eventHqScheduled",
            eventCode: "HQ_ARRIVAL_SCHEDULED",
            text: "Slot kedua",
          }),
        ]}
      />,
    );
    expect(screen.getByText("Taxpayer arrival scheduled")).toBeInTheDocument();
    expect(screen.getByText("Arrival rescheduled")).toBeInTheDocument();
    expect(screen.getByTestId("case-handling-note-children")).toHaveTextContent(
      "Slot kedua",
    );
  });

  it("renders parent titles larger than note bodies", () => {
    renderWithProviders(
      <CaseHandlingNotes
        notes={[
          note({
            key: "1",
            labelKey: "eventCaseCreated",
            eventCode: "CASE_CREATED",
            text: "tes eska 1",
          }),
        ]}
      />,
    );
    const title = screen.getByText("Case created");
    const body = screen.getByText("tes eska 1").closest("[data-note-role='body']");
    expect(title).toHaveAttribute("data-note-role", "title");
    expect(title.className).toContain("--ecmp-font-body-small-size");
    expect(body?.className).toContain("--ecmp-font-helper-size");
  });
});
