/**
 * KnowledgeMentionTextarea — `@` autocomplete (Option A: inline chips).
 */
import { useState } from "react";
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Knowledge } from "@/lib/api/types";

const searchKnowledge = vi.fn();
const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    searchKnowledge: (...args: unknown[]) => searchKnowledge(...args),
  };
});

import { KnowledgeMentionTextarea } from "./KnowledgeMentionTextarea";

function knowledge(overrides: Partial<Knowledge> = {}): Knowledge {
  return {
    id: "e5555555-5555-5555-5555-555555555555",
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
    ...overrides,
  };
}

function Harness({ onValue }: { onValue?: (value: string) => void }) {
  const [value, setValue] = useState("");
  return (
    <KnowledgeMentionTextarea
      label="Catatan Penyelesaian"
      value={value}
      onChange={(next) => {
        setValue(next);
        onValue?.(next);
      }}
    />
  );
}

describe("KnowledgeMentionTextarea", () => {
  beforeEach(() => {
    searchKnowledge.mockReset();
    push.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("opens the dropdown and searches Knowledge (ACTIVE, referenceOnly) when @ is typed", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @");

    await waitFor(() => {
      expect(screen.getByText("Search Knowledge")).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(searchKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({
          q: "",
          status: "ACTIVE",
          referenceOnly: true,
          limit: 10,
        }),
      );
    });
  });

  it("filters the search by the typed query", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@pengaduan");

    await waitFor(() => {
      expect(searchKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({
          q: "pengaduan",
          status: "ACTIVE",
          referenceOnly: true,
          limit: 10,
        }),
      );
    });
  });

  it("shows the empty state when no Knowledge matches", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@xyz");

    await waitFor(() => {
      expect(screen.getByText("No Knowledge found.")).toBeInTheDocument();
    });
  });

  it("shows an error state when the search fails", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockRejectedValue(new Error("network down"));
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@x");

    await waitFor(() => {
      expect(screen.getByText("Unable to load Knowledge.")).toBeInTheDocument();
    });
  });

  it("selecting a result inserts an inline chip (no raw marker, no below preview)", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    const onValue = vi.fn();
    renderWithProviders(<Harness onValue={onValue} />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @pengaduan");

    const option = await screen.findByRole("option", {
      name: /SOP Penanganan Pengaduan/i,
    });
    await user.click(option);

    await waitFor(() => {
      expect(onValue).toHaveBeenCalledWith(
        expect.stringContaining(
          "@[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555)",
        ),
      );
    });

    // Visible UI shows the title chip, not the raw marker / below preview.
    expect(editor.textContent).toContain("SOP Penanganan Pengaduan v2.1");
    expect(editor.textContent).not.toContain("knowledge:");
    expect(
      screen.queryByText(/Selected references|Rujukan terpilih/i),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Search Knowledge")).not.toBeInTheDocument();
  });

  it("selects the highlighted result with Enter", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    const onValue = vi.fn();
    renderWithProviders(<Harness onValue={onValue} />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@sop");
    await screen.findByRole("option", { name: /SOP Penanganan Pengaduan/i });
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(onValue).toHaveBeenCalledWith(
        expect.stringContaining("knowledge:e5555555-5555-5555-5555-555555555555"),
      );
    });
  });

  it("caps client search requests at limit 10", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({
      data: Array.from({ length: 15 }, (_, i) =>
        knowledge({
          id: `e5555555-5555-5555-5555-5555555555${i.toString().padStart(2, "0")}`,
          title: `SOP ${i}`,
        }),
      ),
    });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@sop");

    await waitFor(() => {
      expect(screen.getAllByRole("option")).toHaveLength(10);
    });
  });

  it("closes the dropdown on Escape without keeping a selection", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @pengaduan");
    await waitFor(() => {
      expect(screen.getByText("Search Knowledge")).toBeInTheDocument();
    });

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByText("Search Knowledge")).not.toBeInTheDocument();
    });
    expect(editor.textContent).toContain("@pengaduan");
  });

  it("shows type/version/status subtitle for each result", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({
      data: [knowledge({ documentNumber: null, versionLabel: "1.0" })],
    });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@sop");

    await waitFor(() => {
      expect(screen.getByText("SOP · v1.0 · Active")).toBeInTheDocument();
    });
  });
});
