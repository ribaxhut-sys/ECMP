import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { KnowledgeHistoryEntry } from "@/lib/api/types";

const fetchKnowledgeHistory = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchKnowledgeHistory: (...args: unknown[]) => fetchKnowledgeHistory(...args),
  };
});

import { KnowledgeHistorySection } from "./KnowledgeHistorySection";

function entry(overrides: Partial<KnowledgeHistoryEntry> = {}): KnowledgeHistoryEntry {
  return {
    id: "a1111111-1111-1111-1111-111111111111",
    eventType: "KnowledgeCreated",
    action: "CREATE",
    actorId: "b2222222-2222-2222-2222-222222222222",
    actorName: "Admin Pusat",
    oldValues: null,
    newValues: { title: "SOP Baru" },
    metadata: null,
    createdAt: "2026-08-01T00:00:00Z",
    ...overrides,
  };
}

describe("KnowledgeHistorySection", () => {
  beforeEach(() => {
    fetchKnowledgeHistory.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("shows the actor and event label for each history entry", async () => {
    fetchKnowledgeHistory.mockResolvedValue({
      data: [entry({ eventType: "KnowledgeCreated", actorName: "Admin Pusat" })],
    });

    renderWithProviders(<KnowledgeHistorySection knowledgeId="k-1" />);

    await waitFor(() => {
      expect(screen.getByText("Created")).toBeInTheDocument();
    });
    expect(screen.getByText(/Admin Pusat/)).toBeInTheDocument();
    expect(fetchKnowledgeHistory).toHaveBeenCalledWith("k-1");
  });

  it("shows a field-level diff for a KnowledgeUpdated entry", async () => {
    fetchKnowledgeHistory.mockResolvedValue({
      data: [
        entry({
          id: "a2",
          eventType: "KnowledgeUpdated",
          oldValues: { summary: "Ringkasan lama" },
          newValues: { summary: "Ringkasan baru" },
        }),
      ],
    });

    renderWithProviders(<KnowledgeHistorySection knowledgeId="k-1" />);

    await waitFor(() => {
      expect(screen.getByText("Updated")).toBeInTheDocument();
    });
    expect(screen.getByText(/Ringkasan lama/)).toBeInTheDocument();
    expect(screen.getByText(/Ringkasan baru/)).toBeInTheDocument();
  });

  it("shows old → new file name for a KnowledgeFileReplaced entry", async () => {
    fetchKnowledgeHistory.mockResolvedValue({
      data: [
        entry({
          id: "a3",
          eventType: "KnowledgeFileReplaced",
          oldValues: { fileName: "sop_v1.pdf", role: "PRIMARY" },
          newValues: { fileName: "sop_v2.pdf", role: "PRIMARY" },
        }),
      ],
    });

    renderWithProviders(<KnowledgeHistorySection knowledgeId="k-1" />);

    expect(await screen.findByText("sop_v1.pdf → sop_v2.pdf")).toBeInTheDocument();
  });

  it("marks a post-publish change (DEC-030) with a badge", async () => {
    fetchKnowledgeHistory.mockResolvedValue({
      data: [
        entry({
          id: "a4",
          eventType: "KnowledgeUpdated",
          oldValues: { summary: "Lama" },
          newValues: { summary: "Baru" },
          metadata: { postPublish: true, statusAtChange: "ACTIVE" },
        }),
      ],
    });

    renderWithProviders(<KnowledgeHistorySection knowledgeId="k-1" />);

    expect(await screen.findByText("After publish")).toBeInTheDocument();
  });

  it("shows the empty state when there is no history yet", async () => {
    fetchKnowledgeHistory.mockResolvedValue({ data: [] });

    renderWithProviders(<KnowledgeHistorySection knowledgeId="k-1" />);

    await waitFor(() => {
      expect(screen.getByText("No history yet")).toBeInTheDocument();
    });
  });

  it("shows an error state and retries on failure", async () => {
    fetchKnowledgeHistory.mockRejectedValue(new Error("network down"));

    renderWithProviders(<KnowledgeHistorySection knowledgeId="k-1" />);

    await waitFor(() => {
      expect(screen.getByText("Unable to load history.")).toBeInTheDocument();
    });
  });
});
